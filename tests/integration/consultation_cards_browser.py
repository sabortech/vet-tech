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
OUT = ROOT / 'openspec/changes/archive/2026-11-07-reformular-consultas-tutor/evidence'
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

            navigate('Consultas')
            expect(page.locator('.consultation-card')).to_have_count(5)
            cards = page.locator('.consultation-card')
            expect(cards.locator('.disease-status')).to_have_text(['Finalizada','Agendada','Registro anterior','Em atendimento','Cancelada'])
            assert cards.nth(0).get_by_role('button',name='Ver prontuário').count()==1
            assert cards.nth(1).get_by_role('button',name='Ver prontuário').count()==0
            assert cards.nth(3).get_by_role('button',name='Ver prontuário').count()==0
            chosen_backgrounds = None
            for width in (1440,390):
                page.set_viewport_size({'width':width,'height':1000})
                for theme in ('light','dark'):
                    page.evaluate('(t)=>{document.documentElement.dataset.vtTheme=t;document.documentElement.classList.toggle("dark",t==="dark")}',theme)
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                    cards.first.screenshot(path=str(OUT/f'list-{width}-{theme}.png'))
                    cards.first.get_by_role('button',name='Ver prontuário').click()
                    detail = page.locator('.consultation-detail')
                    expect(detail.get_by_text('Diagnóstico sintético',exact=True)).to_be_visible()
                    expect(page.locator('.consultations-header').get_by_role('button',name='Exportar PDF da consulta')).to_be_visible()
                    expect(detail.locator('.consultation-record')).to_have_count(0)
                    expect(detail.locator('.consultation-complements .vaccine-record-card')).to_have_count(7)
                    expect(detail.locator('.consultation-complements .vaccine-art-symbol')).to_have_count(7)
                    expect(detail.locator('.consultation-summary .consultation-narrative')).to_have_count(3)
                    expect(detail.locator('.consultation-summary-art .vaccine-art-symbol')).to_be_visible()
                    expect(detail.locator('.medication-card')).to_have_count(1)
                    expect(detail.locator('.disease-card:not(.exam-card)')).to_have_count(1)
                    expect(detail.locator('.disease-card:not(.exam-card)').get_by_text('Data do diagnóstico',exact=True)).to_be_visible()
                    assert detail.locator('.disease-card:not(.exam-card)').get_by_text('Última evolução',exact=True).count()==0
                    backgrounds = detail.locator('.exam-art').evaluate_all('(els)=>els.map(e=>getComputedStyle(e).getPropertyValue("--record-background"))')
                    assert len(set(backgrounds)) == 4, backgrounds
                    assert any('fundinho.webp' in value for value in backgrounds), backgrounds
                    assert all(value.split('/')[-1].split('.webp')[0] in background for value, background in zip(backgrounds, detail.locator('.exam-art').evaluate_all('(els)=>els.map(e=>getComputedStyle(e).backgroundImage)')))
                    if chosen_backgrounds is None:
                        chosen_backgrounds = backgrounds
                    else:
                        assert backgrounds == chosen_backgrounds
                    assert detail.get_by_role('button',name='Ver consulta de origem').count()==0
                    for text in ('Lote QA','10 mg','Uma vez por dia','Nota clínica sintética','Resultado sintético','Em tratamento','Realizado'):
                        expect(detail.get_by_text(text,exact=True).first).to_be_visible()
                    assert detail.locator('.consultation-narrative').first.inner_text()==DESCRIPTION
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                    page.locator('.consultations-header').screenshot(path=str(OUT/f'header-{width}-{theme}.png'))
                    detail.screenshot(path=str(OUT/f'detail-{width}-{theme}.png'))
                    page.get_by_role('button',name='Voltar à lista',exact=True).click()
                    expect(cards).to_have_count(5)
                    checks.append(f'{width}/{theme}: lista, documento completo, campos, retorno e PDF elegível')
            cards.nth(2).get_by_role('button',name='Ver prontuário').click()
            expect(page.locator('.consultation-section-empty').filter(has_text='Nenhum registro publicado nesta categoria.')).to_have_count(4)
            assert page.get_by_role('button',name='Exportar PDF da consulta').count()==0
            page.get_by_role('button',name='Voltar à lista',exact=True).click()
            page.get_by_role('button',name='Carregar permissões e histórico de acessos',exact=True).click()
            page.get_by_role('button',name='Permissões e histórico de acessos',exact=True).click()
            expect(page.get_by_role('button',name='Atualizar permissões e acessos',exact=True)).to_be_visible()
            expect(page.locator('.consultation-access-art .vaccine-art-symbol')).to_be_visible()
            for access_width in (1440,390):
                page.set_viewport_size({'width':access_width,'height':1000})
                for access_theme in ('light','dark'):
                    page.evaluate('(t)=>{document.documentElement.dataset.vtTheme=t;document.documentElement.classList.toggle("dark",t==="dark")}',access_theme)
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                    page.locator('.consultation-access-card').screenshot(path=str(OUT/f'access-{access_width}-{access_theme}.png'))
            MODE='error'
            page.get_by_role('button',name='Atualizar registros do pet',exact=True).click()
            expect(page.get_by_role('button',name='Tentar novamente',exact=True)).to_be_visible()
            MODE='empty'
            page.get_by_role('button',name='Tentar novamente',exact=True).click()
            expect(page.get_by_role('heading',name='Nenhuma consulta para este pet',exact=True)).to_be_visible()
            MODE='records'
            page.get_by_role('button',name='Atualizar registros do pet',exact=True).click()
            expect(cards).to_have_count(5)
            checks.append('legado sem PDF, categorias vazias, permissões, erro/retry, lista vazia e atualização')
            # Verify the frontend shown in the user screenshot shares the new modules.
            second = browser.new_page()
            second.route('**/env.json*',test_endpoints)
            second.route('https://fonts.googleapis.com/**',lambda r:r.abort())
            second.goto('http://localhost:3001/login',wait_until='domcontentloaded')
            second.wait_for_function('!!window.__reflex',timeout=60000)
            second.get_by_label('E-mail',exact=True).fill('tutor@example.invalid')
            second.get_by_label('Senha',exact=True).fill('synthetic-password')
            second.get_by_role('button',name='Login',exact=True).click()
            expect(second.locator('.pet-entry__action').first).to_be_visible()
            second.locator('.pet-entry__action').nth(1).click()
            expect(second).to_have_url('http://localhost:3001/dashboard')
            second.locator('#vet-tech-sidebar').get_by_label('Consultas',exact=True).click()
            expect(second.locator('.consultation-card')).to_have_count(5)
            assert any('/2/' in path for path in READS)
            checks.append('porta 3001 com segundo pet e navegação funcional')
            assert not errors,errors
            browser.close()
        (OUT/'results.json').write_text(json.dumps({'checks':checks,'errors':errors},ensure_ascii=False,indent=2))
        print('PASS:',len(checks),'grupos de verificações')
    finally:
        if env_file.read_bytes() != original:
            env_file.write_bytes(original)
        os.killpg(process.pid, signal.SIGINT)
        process.wait(timeout=20)
        api.shutdown()
        log.close()


if __name__ == '__main__':
    main()
