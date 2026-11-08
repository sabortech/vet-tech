"""Read-only browser checks with an isolated Reflex backend and synthetic API.

Uses the compiled frontend at localhost:3000; overrides endpoint configuration
only in the test browser so credentials never reach the active backend.
"""
import json
import os
import re
from pathlib import Path
import signal
import socket
import subprocess
import sys
import threading
import time
from http.server import ThreadingHTTPServer
from urllib.parse import urlsplit

import httpx
from playwright.sync_api import expect, sync_playwright
import dashboard_dates_browser as fixture

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'openspec/changes/archive/2026-11-07-padronizar-cartoes-doencas/evidence'
MODE = 'records'
READS = []
DESCRIPTION = 'Acompanhamento sintético.\nManter orientação registrada. ' + 'Descrição extensa para conferir leitura e quebra de linha. ' * 15


class API(fixture.SyntheticAPI):
    def handle_api(self):
        path = urlsplit(self.path).path.split('/', 2)[-1]
        if path.endswith('/historico'):
            READS.append(path)
            time.sleep(.3)
            states = ('em_tratamento', 'ativa', 'curada', 'controlada', '', 'estado_legado')
            rows = [dict(id=i+1, nome='Condição sintética ' + str(i+1), estado=state,
                         descricao=DESCRIPTION if i == 0 else '',
                         data_evolucao='2026-11-02' if i == 0 else '',
                         consulta_id=43 if i == 0 else None,
                         veterinario_nome='Profissional sintético' if i == 0 else '')
                    for i, state in enumerate(states)]
            status = 503 if MODE == 'error' else 200
            body = {'message': 'Falha sintética'} if status != 200 else {
                'doencas': rows if MODE == 'records' else [],
                'vacinas': [{'id': 1, 'vacina': 'Vacina sintética'}],
                'medicamentos': [{'id': 1, 'nome': 'Medicamento sintético'}],
                'consultas': [{'id': 43, 'status': 'finalizada', 'motivo': 'Consulta sintética', 'diagnostico': 'Diagnóstico sintético'}],
            }
        elif path.startswith('pets/'):
            body, status = {**fixture.PET, 'id': int(path.split('/')[-1])}, 200
        else:
            return super().handle_api()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())


def main():
    global MODE
    OUT.mkdir(parents=True, exist_ok=True)
    api = ThreadingHTTPServer(('127.0.0.1', 0), API)
    threading.Thread(target=api.serve_forever, daemon=True).start()
    with socket.socket() as available:
        available.bind(('127.0.0.1', 0))
        port = available.getsockname()[1]
    env_file = ROOT / '.web/env.json'
    original = env_file.read_bytes()
    log = (OUT / 'backend.log').open('w')
    process = subprocess.Popen([sys.executable, '-m', 'reflex', 'run', '--backend-only', '--env', 'prod', '--backend-port', str(port)],
        cwd=ROOT, env={**os.environ, 'XANO_API_BASE_URL': f'http://127.0.0.1:{api.server_port}', 'XANO_TENANT': ''},
        stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    checks, errors = [], []
    try:
        for _ in range(120):
            if process.poll() is not None:
                raise RuntimeError('Test backend stopped; inspect backend.log')
            try:
                if httpx.get(f'http://localhost:{port}/ping', timeout=.5).status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(.5)
        else:
            raise RuntimeError('Test backend did not start')
        if env_file.read_bytes() != original:
            env_file.write_bytes(original)
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path='/home/usuario/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome', args=['--no-sandbox'])
            page = browser.new_page(viewport={'width':1440, 'height':1000})
            def test_endpoints(route):
                response = route.fetch()
                body = re.sub(r'((?:https?|ws)://localhost):\d+', lambda m: m[1] + f':{port}', response.text())
                route.fulfill(response=response, body=body)
            page.route('**/env.json*', test_endpoints)
            connected = []
            page.on('websocket', lambda ws: connected.append(ws.url))
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.route('https://fonts.googleapis.com/**', lambda r:r.abort())
            page.goto('http://localhost:3000/login', wait_until='domcontentloaded')
            page.wait_for_function('!!window.__reflex', timeout=60000)
            page.wait_for_timeout(500)
            assert any(f':{port}/_event/' in url for url in connected), connected
            page.get_by_label('E-mail', exact=True).fill('tutor@example.invalid')
            page.get_by_label('Senha', exact=True).fill('synthetic-password')
            page.get_by_role('button', name='Login', exact=True).click()
            expect(page.locator('.pet-entry__action').first).to_be_visible()
            page.locator('.pet-entry__action').first.click()
            expect(page).to_have_url('http://localhost:3000/dashboard')

            def navigate(label):
                if page.viewport_size['width'] < 768:
                    page.locator('.sidebar-toggle--mobile').click()
                page.locator('#vet-tech-sidebar').get_by_label(label, exact=True).click()

            navigate('Doenças')
            expect(page.get_by_text('Carregando dados do pet…', exact=True)).to_be_visible()
            expect(page.locator('.disease-card')).to_have_count(6)
            for width in (1440, 390):
                page.set_viewport_size({'width':width, 'height':1000})
                for theme in ('light', 'dark'):
                    page.evaluate('(t)=>{document.documentElement.dataset.vtTheme=t;document.documentElement.classList.toggle("dark",t==="dark")}', theme)
                    expect(page.locator('.disease-status')).to_have_text(['Em tratamento', 'Ativa', 'Curada', 'Controlada', 'Não informado', 'estado_legado'])
                    expect(page.locator('.disease-card').first.locator('.disease-description')).to_have_text(DESCRIPTION)
                    assert page.locator('.disease-card').first.locator('button').count() == 1
                    assert page.locator('.disease-card').nth(1).locator('button').count() == 0
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                    page.locator('.disease-card').first.screenshot(path=str(OUT / f'card-{width}-{theme}.png'))
                    checks.append(f'{width}/{theme}: status, ausência, descrição, layout, LED e ação')
            page.emulate_media(reduced_motion='reduce')
            assert page.locator('.disease-card .vet-date-led-track').first.evaluate('(e)=>getComputedStyle(e).animationDuration') == '20s'
            page.locator('.disease-card').first.get_by_role('button', name='Ver consulta de origem').click()
            expect(page.get_by_text('Diagnóstico sintético', exact=True)).to_be_visible()
            assert page.locator('.disease-card').count() == 0
            checks.append('Consulta correta abre com complementos próprios do detalhe')
            navigate('Vacinas')
            expect(page.locator('.vaccine-record-art')).to_be_visible()
            navigate('Medicamentos')
            expect(page.locator('.medication-card')).to_be_visible()
            navigate('Doenças')
            MODE = 'error'
            page.get_by_role('button', name='Atualizar registros do pet', exact=True).click()
            expect(page.get_by_role('button', name='Tentar novamente', exact=True)).to_be_visible()
            MODE = 'empty'
            page.get_by_role('button', name='Tentar novamente', exact=True).click()
            expect(page.get_by_role('heading', name='Nenhuma doença registrada')).to_be_visible()
            MODE = 'records'
            page.get_by_role('button', name='Atualizar registros do pet', exact=True).click()
            expect(page.locator('.disease-card')).to_have_count(6)
            navigate('Meus Pets')
            page.locator('.pet-entry__action').nth(1).click()
            navigate('Doenças')
            expect(page.locator('.disease-card')).to_have_count(6)
            assert any('/2/' in path for path in READS)
            checks.append('Vacinas/Medicamentos, atualização, erro/retry, vazio e troca de pet')
            assert not errors, errors
            browser.close()
        (OUT / 'results.json').write_text(json.dumps({'checks':checks, 'errors':errors}, ensure_ascii=False, indent=2))
        print('PASS:', len(checks), 'grupos de verificações')
    finally:
        if env_file.read_bytes() != original:
            env_file.write_bytes(original)
        os.killpg(process.pid, signal.SIGINT)
        process.wait(timeout=20)
        api.shutdown()
        log.close()


if __name__ == '__main__':
    main()
