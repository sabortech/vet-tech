"""Consultation list/detail browser checks with an isolated synthetic backend.

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
FRONTEND_PORT=os.getenv('VET_TECH_TEST_FRONTEND_PORT','3000')
ORIGIN=f'http://localhost:{FRONTEND_PORT}'
OUT=ROOT/'openspec/changes/archive/2026-11-07-centralizar-selecao-pet/evidence/pet-page-backgrounds'/FRONTEND_PORT
MODE = 'records'
READS = []
DESCRIPTION = 'Acompanhamento sintético.\nOrientação registrada. ' + 'Texto longo para verificar leitura e quebra de linha. ' * 12
CONSULTATIONS = [
    {'id': 43, 'status': 'finalizada', 'data_atendimento': '2026-11-02', 'motivo': DESCRIPTION,
     'diagnostico': 'Diagnóstico sintético', 'obs': 'Observações sintéticas.\nSegunda linha.',
     'veterinario_nome': 'Profissional sintético', 'veterinario_id': 8,
     'iniciada_em': '2026-11-02T12:00:00Z', 'finalizada_em': '2026-11-02T13:00:00Z', 'retorno_previsto': '2026-12-02'},
    {'id': 44, 'status': 'agendada', 'data_atendimento': '2026-12-01'},
    {'id': 45, 'status': 'legado', 'data_atendimento': '2026-10-01'},
    {'id': 46, 'status': 'em_atendimento'}, {'id': 47, 'status': 'cancelada'},
]

class API(fixture.SyntheticAPI):
    def handle_api(self):
        path = urlsplit(self.path).path.split('/', 2)[-1]
        if path.endswith('/historico'):
            READS.append(path)
            time.sleep(.4)
            body = {'consultas': CONSULTATIONS,
                'vacinas': [{'id': 1, 'consulta_id': 43, 'vacina': 'Vacina sintética', 'data_aplicacao': '2026-11-02', 'lote': 'Lote QA', 'data_prox_dose': '2026-12-02'}],
                'medicamentos': [{'id': 2, 'consulta_id': 43, 'nome': 'Medicamento sintético', 'dose': 10, 'unidade': 'mg', 'frequencia': 'Uma vez por dia', 'via': 'oral', 'tipo': 'outro', 'data_inicio': '2026-11-02', 'data_fim': '2026-11-12'}],
                'diagnosticos': [{'id': 3, 'consulta_id': 43, 'nome': 'Condição sintética', 'estado': 'em_tratamento', 'data_diagnostico': '2026-11-02', 'observacoes': 'Nota clínica sintética'}],
                'exames': [{'id': 4+i, 'consulta_id': 43, 'tipo': 'Exame sintético '+str(i+1), 'status': 'realizado', 'data_solicitacao': '2026-11-02', 'data_realizacao': '2026-11-03', 'resultado': 'Resultado sintético'} for i in range(4)]}
            status = 503 if MODE == 'error' else 200
            if status != 200: body = {'message': 'Falha sintética'}
        elif path == 'tutor/account':
            body,status={'nome':'Tutor sintético','email':'tutor@example.invalid','telefone':'11999999999','endereco':'Endereço sintético','cpf_mascarado':'***'},200
        elif path == 'tutor/consultas':
            body, status = ([] if MODE == 'empty' else CONSULTATIONS), 200
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
            page.goto(ORIGIN+'/login', wait_until='domcontentloaded')
            page.wait_for_function('!!window.__reflex', timeout=60000)
            page.wait_for_timeout(500)
            assert any(f':{port}/_event/' in url for url in connected), connected
            page.get_by_label('E-mail', exact=True).fill('tutor@example.invalid')
            page.get_by_label('Senha', exact=True).fill('synthetic-password')
            page.get_by_role('button', name='Login', exact=True).click()
            expect(page.locator('.pet-entry__action').first).to_be_visible()
            sidebar=page.locator('#vet-tech-sidebar')
            for label in ('Meus Pets','Mudar pet','Configurações','Prontuário'):
                sidebar.get_by_label(label,exact=True).click()
                for width in (1440,390):
                    page.set_viewport_size({'width':width,'height':1000})
                    for theme,color,image in [('light','rgb(247, 243, 231)','fundpet-pattern-light.svg'),('dark','rgb(18, 34, 27)','fundpet-pattern.svg')]:
                        page.evaluate('(t)=>{document.documentElement.dataset.vtTheme=t;document.documentElement.classList.toggle("dark",t==="dark")}',theme)
                        expect(page.locator('.app-content')).to_have_css('background-color',color)
                        expect(page.locator('.app-content')).to_have_css('background-image',re.compile(image))
                        expect(page.locator('.app-layout')).to_have_css('background-color',color)
                        expect(page.locator('.app-layout')).to_have_css('background-image',re.compile(image))
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                        page.screenshot(path=str(OUT/f'{label}-{width}-{theme}.png'))
                        checks.append(f'{label}/{width}/{theme}: mesma estampa e sem overflow')
                page.set_viewport_size({'width':1440,'height':1000})
            assert not errors,errors
            browser.close()
        (OUT/'results.json').write_text(json.dumps({'checks':checks,'errors':errors},ensure_ascii=False,indent=2))
        print('PASS: fundo de conteúdo e atrás da sidebar igual nas quatro telas, dois temas e tamanhos')
    finally:
        if env_file.read_bytes() != original:
            env_file.write_bytes(original)
        os.killpg(process.pid, signal.SIGINT)
        process.wait(timeout=20)
        api.shutdown()
        log.close()


if __name__ == '__main__':
    main()
