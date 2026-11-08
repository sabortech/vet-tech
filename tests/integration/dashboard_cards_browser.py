"""Dashboard real com API sintética local; screenshots e geometria responsiva.

PYTHONPATH=/tmp/vet-tech-browser-tools .venv/bin/python tests/integration/dashboard_cards_browser.py
"""
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import threading
import time
from datetime import timedelta
from http.server import ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import httpx
from playwright.sync_api import expect, sync_playwright
import dashboard_dates_browser as fixture

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'openspec/changes/archive/2026-11-07-remodelar-cards-pets-dashboard/evidence'
PETS = [
    {**fixture.PET, 'nome': 'Jessy', 'peso_atual': 10, 'foto': '/mascote/clinicturtle.jpeg'},
    {**fixture.PET2, 'nome': 'Morph', 'foto': '/foto-inexistente.jpeg'},
    {**fixture.PET, 'id': 3, 'nome': 'Shangrilia com nome longo para verificar a quebra do conteúdo'},
]
EMPTY = False
REMOTE_RELEASE = threading.Event()
REMOTE_RELEASE.set()
SLOW_PET_RELEASE = threading.Event()
SLOW_PET_RELEASE.set()
DASHBOARD_READS = []

class API(fixture.SyntheticAPI):
    def handle_api(self):
        path = urlsplit(self.path).path.split('/', 2)[-1]
        if path == 'pets' and self.command == 'GET':
            body, status = ([] if EMPTY else PETS), 200
        elif path == 'tutor/dashboard':
            REMOTE_RELEASE.wait(timeout=15)
            pet_id = int(parse_qs(urlsplit(self.path).query)['pet_id'][0])
            DASHBOARD_READS.append(pet_id)
            if pet_id == 3:
                SLOW_PET_RELEASE.wait(timeout=15)
            if pet_id not in (1, 2, 3):
                body, status = {'message': 'Pet não disponível'}, 404
            elif fixture.ERROR_MODE:
                body, status = {'message': 'Erro sintético'}, 503
            else:
                body = {**PETS[pet_id-1], 'especie_nome': 'Cachorro', 'raca_nome': 'SRD',
                    'vacinas': [] if pet_id == 2 else [{'vacina': 'Raiva', 'data_prox_dose': (fixture.TODAY+timedelta(days=10 if pet_id == 1 else -10)).isoformat()}],
                    'consultas': [{'status': 'finalizada', 'data_atendimento': (fixture.TODAY-timedelta(days=5)).isoformat()}], 'exames': []}
                status = 200
        else:
            return super().handle_api()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())


def run():
    global EMPTY
    OUT.mkdir(parents=True, exist_ok=True)
    frontend_env = ROOT / '.web/env.json'
    original_frontend_env = frontend_env.read_bytes() if frontend_env.exists() else None
    api = ThreadingHTTPServer(('127.0.0.1', 0), API)
    threading.Thread(target=api.serve_forever, daemon=True).start()
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    origin = f'http://localhost:{port}'
    PETS[0]['foto'] = origin + '/mascote/clinicturtle.jpeg'
    PETS[1]['foto'] = origin + '/foto-inexistente.jpeg'
    env = {**os.environ, 'XANO_API_BASE_URL': f'http://127.0.0.1:{api.server_port}', 'XANO_TENANT': ''}
    errors, checks, geometry = [], [], []
    log = (OUT / 'reflex.log').open('w')
    process = subprocess.Popen([sys.executable, '-m', 'reflex', 'run', '--env', 'prod', '--single-port', '--backend-port', str(port)], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    try:
        for _ in range(240):
            if process.poll() is not None:
                raise RuntimeError('Servidor encerrou; veja evidence/reflex.log')
            try:
                if httpx.get(origin, timeout=1).status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(.5)
        else:
            raise RuntimeError('Servidor não iniciou')
        # The production bundle already embeds its test endpoint. Restore the
        # development frontend immediately instead of waiting for all checks.
        if original_frontend_env is not None:
            frontend_env.write_bytes(original_frontend_env)
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path='/home/usuario/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome', headless=True, args=['--no-sandbox'])
            context = browser.new_context(viewport={'width': 1440, 'height': 1000}, locale='pt-BR')
            page = context.new_page()
            page.set_default_timeout(15000)
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(origin + '/login')
            page.get_by_label('E-mail', exact=True).fill('tutor@example.invalid')
            page.get_by_label('Senha', exact=True).fill('synthetic-password')
            page.get_by_role('button', name='Login', exact=True).click()
            expect(page.get_by_role('heading', name='Perfil do tutor', exact=True)).to_be_visible()
            def dashboard():
                page.goto(origin + '/dashboard')
                expect(page.get_by_role('heading', name='Seus pets em foco')).to_be_visible()
                page.locator('.dashboard-page').get_by_role('combobox').click()
                page.get_by_role('option', name='Todos os pets', exact=True).click()
                expect(page.locator('.dashboard-pet-card')).to_have_count(3)
            REMOTE_RELEASE.clear()
            SLOW_PET_RELEASE.clear()
            page.goto(origin + '/dashboard')
            expect(page.get_by_text('Carregando dados do Dashboard...', exact=True)).to_be_visible()
            toggle = page.locator('.sidebar-toggle--desktop')
            previous_label = toggle.get_attribute('aria-label')
            clicked_at = time.perf_counter()
            toggle.click()
            expected_label = 'Abrir menu' if previous_label == 'Recolher menu' else 'Recolher menu'
            expect(toggle).to_have_attribute('aria-label', expected_label, timeout=2000)
            navigation_ms = round((time.perf_counter()-clicked_at)*1000, 1)
            assert not REMOTE_RELEASE.is_set()
            first_card_at = time.perf_counter()
            REMOTE_RELEASE.set()
            expect(page.locator('.dashboard-pet-card')).to_have_count(2)
            expect(page.get_by_text('Carregando dados do Dashboard...', exact=True)).to_be_visible()
            assert not SLOW_PET_RELEASE.is_set()
            first_card_ms = round((time.perf_counter()-first_card_at)*1000, 1)
            page.screenshot(path=str(OUT / 'carregamento-parcial.png'))
            SLOW_PET_RELEASE.set()
            expect(page.locator('.dashboard-pet-card')).to_have_count(3)
            expect(page.get_by_role('button', name='Atualizar', exact=True)).to_be_enabled()
            checks.append(f'cards rápidos visíveis em {first_card_ms} ms com terceiro pet bloqueado')
            request_count = len(DASHBOARD_READS)
            dashboard()
            assert len(DASHBOARD_READS) == request_count
            checks.append('retorno imediato reaproveitou dados sem novas leituras')
            REMOTE_RELEASE.clear()
            page.get_by_role('button', name='Atualizar', exact=True).click()
            expect(page.get_by_role('button', name='Atualizar', exact=True)).to_be_disabled()
            REMOTE_RELEASE.set()
            expect(page.get_by_role('button', name='Atualizar', exact=True)).to_be_enabled()
            assert len(DASHBOARD_READS) == request_count + 3, (request_count, DASHBOARD_READS)
            checks.append('Atualizar executou novas leituras dos três pets')
            checks.append(f'menu respondeu em {navigation_ms} ms enquanto API estava bloqueada')
            dashboard()
            expect(page.locator('.dashboard-pet-followup__title')).to_have_count(3)
            expect(page.locator('.dashboard-pet-photo').nth(1).get_by_text('🐾')).to_be_visible()
            assert page.locator('[role="progressbar"]').count() == 0
            assert httpx.get(origin + '/fundopets.jpeg').status_code == 200
            expect(page.locator('.dashboard-pet-vaccines--futura')).to_have_count(1)
            expect(page.locator('.dashboard-pet-vaccines--sem-data')).to_have_count(1)
            expect(page.locator('.dashboard-pet-vaccines--ultrapassada')).to_have_count(1)
            expect(page.get_by_text('Próxima dose em 10 dias', exact=True)).to_be_visible()
            expect(page.get_by_text('Data prevista há 10 dias — confira os registros', exact=True)).to_be_visible()
            assert page.locator('.dashboard-pet-vaccines').first.evaluate('(el) => getComputedStyle(el.querySelector(".dashboard-pet-track")).animationName') == 'none'
            checks.append('3 cards completos, fallback de foto, fundo e LEDs futura/sem-data/ultrapassada sem animação')
            expect(page.locator('.dashboard-card-led')).to_have_count(3)
            expect(page.locator('.dashboard-pet-card--sem-data .dashboard-card-led')).not_to_be_visible()
            orbit = page.locator('.dashboard-pet-card--futura .dashboard-card-led .vet-date-led-track').last
            before = orbit.evaluate('(el) => parseFloat(getComputedStyle(el).strokeDashoffset)')
            page.wait_for_timeout(180)
            after = orbit.evaluate('(el) => parseFloat(getComputedStyle(el).strokeDashoffset)')
            assert after < before, (before, after)
            assert orbit.evaluate('(el) => getComputedStyle(el).stroke') == page.locator('.dashboard-pet-card--futura .dashboard-vaccine-led').evaluate('(el) => getComputedStyle(el).backgroundColor')
            assert orbit.evaluate('(el) => getComputedStyle(el.closest("svg")).pointerEvents') == 'none'
            page.emulate_media(reduced_motion='reduce')
            assert orbit.evaluate('(el) => getComputedStyle(el).animationName') == 'vet-date-border-orbit'
            assert orbit.evaluate('(el) => getComputedStyle(el).animationDuration') == '20s'
            reduced_before = orbit.evaluate('(el) => parseFloat(getComputedStyle(el).strokeDashoffset)')
            page.wait_for_timeout(200)
            reduced_after = orbit.evaluate('(el) => parseFloat(getComputedStyle(el).strokeDashoffset)')
            assert reduced_after < reduced_before, (reduced_before, reduced_after)
            page.emulate_media(reduced_motion='no-preference')
            checks.append('LED do contorno horário, cor da barra, apagado sem data, cliques livres e movimento reduzido')
            for width in (1440, 1366, 768, 390):
                page.set_viewport_size({'width': width, 'height': 1000})
                for theme in ('light', 'dark'):
                    page.evaluate('(theme) => document.documentElement.dataset.vtTheme = theme', theme)
                    page.wait_for_timeout(150)
                    for collapsed in (False, True):
                        if width >= 768:
                            toggle = page.locator('.sidebar-toggle--desktop')
                            target = 'Abrir menu' if collapsed else 'Recolher menu'
                            if toggle.get_attribute('aria-label') != target:
                                toggle.click()
                                page.wait_for_timeout(350)
                                page.locator('.sidebar-toggle--desktop').blur()
                                page.locator('.sidebar').evaluate('(el) => {el.scrollLeft=0}')
                        elif not collapsed:
                            page.get_by_role('button', name='Abrir menu', exact=True).click()
                            expect(page.locator('.sidebar--mobile-open')).to_be_visible()
                            page.locator('.sidebar-toggle--mobile').click()
                            expect(page.locator('.sidebar--mobile-open')).to_have_count(0)
                        data = page.evaluate('''() => ({width: innerWidth, overflow: document.documentElement.scrollWidth > innerWidth,
                            columns: getComputedStyle(document.querySelector('.dashboard-pets-grid')).gridTemplateColumns,
                            cards: [...document.querySelectorAll('.dashboard-pet-card')].map(el => {const r=el.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height,overflow:el.scrollWidth>el.clientWidth};})})''')
                        assert not data['overflow'] and not any(c['overflow'] for c in data['cards']), data
                        if len(data['columns'].split()) == 2:
                            assert abs(data['cards'][0]['h'] - data['cards'][1]['h']) < 1, data
                        cards = data['cards']
                        for i, a in enumerate(cards):
                            for b in cards[i+1:]:
                                assert a['x']+a['w'] <= b['x']+.5 or b['x']+b['w'] <= a['x']+.5 or a['y']+a['h'] <= b['y']+.5 or b['y']+b['h'] <= a['y']+.5, data
                        geometry.append({**data, 'theme': theme, 'collapsed': collapsed})
                        if not collapsed:
                            page.evaluate('window.scrollTo(0,0)')
                            page.screenshot(path=str(OUT / f'{width}-{theme}.png'), full_page=True)
            checks.append('16 combinações de largura, tema e navegação sem overflow ou sobreposição')
            page.set_viewport_size({'width': 1440, 'height': 1000})
            page.locator('#vettech-mascote').click()
            expect(page.locator('#vettech-support-chat')).to_be_visible()
            page.screenshot(path=str(OUT / 'chat-aberto.png'))
            page.get_by_role('button', name='Fechar chat', exact=True).click()
            expect(page.locator('#vettech-support-chat')).not_to_be_visible()
            checks.append('chat abre e fecha sem impedir a retomada das ações')
            page.locator('.dashboard-pet-actions').first.get_by_role('button', name='Ver Dashboard do pet', exact=True).click()
            expect(page.locator('.dashboard-pet-card')).to_have_count(0)
            expect(page.get_by_text('Atividade recente', exact=True)).to_be_visible()
            checks.append('filtro individual preserva a visão detalhada')
            dashboard()
            page.locator('.dashboard-pet-vaccines').first.focus()
            page.keyboard.press('Enter')
            page.wait_for_url('**/prontuario?secao=vacinas&pet_id=1')
            checks.append('LED acionado por Enter abre Vacinas do pet 1')
            dashboard()
            page.locator('.dashboard-pet-vaccines').nth(1).click()
            page.wait_for_url('**/prontuario?secao=vacinas&pet_id=2')
            checks.append('LED sem data acionado por clique abre Vacinas do pet 2')
            dashboard()
            page.locator('.dashboard-pet-actions').nth(1).get_by_role('button', name='Prontuário', exact=True).click()
            page.wait_for_url('**/prontuario?secao=inicio&pet_id=2')
            checks.append('ação Prontuário navega para a seção clínica')
            dashboard()
            page.locator('.dashboard-pet-actions').first.get_by_role('button', name='Agendar consulta', exact=True).click()
            expect(page.get_by_role('dialog')).to_be_visible()
            page.screenshot(path=str(OUT / 'agendamento.png'))
            page.keyboard.press('Escape')
            checks.append('ação de agendamento abre fluxo existente')
            fixture.ERROR_MODE = True
            page.goto(origin + '/dashboard')
            page.get_by_role('button', name='Atualizar', exact=True).click()
            expect(page.get_by_role('button', name='Tentar novamente')).to_be_visible()
            page.screenshot(path=str(OUT / 'erro.png'))
            fixture.ERROR_MODE = False
            page.get_by_role('button', name='Tentar novamente').click()
            expect(page.locator('.dashboard-pet-card')).to_have_count(3)
            checks.append('recuperação de erro')
            EMPTY = True
            page.goto(origin + '/login')
            # Nova sessão para que a lista de pets vazia seja carregada no login.
            context.clear_cookies()
            page.evaluate('localStorage.clear(); sessionStorage.clear()')
            page.goto(origin + '/login')
            page.get_by_label('E-mail', exact=True).fill('tutor@example.invalid')
            page.get_by_label('Senha', exact=True).fill('synthetic-password')
            page.get_by_role('button', name='Login', exact=True).click()
            expect(page.get_by_role('heading', name='Perfil do tutor', exact=True)).to_be_visible()
            page.goto(origin + '/dashboard')
            expect(page.get_by_role('heading', name='Nenhum pet cadastrado')).to_be_visible()
            page.get_by_role('button', name='Cadastrar pet', exact=True).click()
            expect(page.get_by_label('Nome do pet', exact=True)).to_be_visible()
            checks.append('lista vazia oferece cadastro funcional')
            assert not errors, errors
            browser.close()
        (OUT / 'results.json').write_text(json.dumps({'checks':checks, 'geometry':geometry, 'javascript_errors':errors}, ensure_ascii=False, indent=2))
        print(json.dumps({'checks': checks, 'javascript_errors': errors}, ensure_ascii=False))
    finally:
        REMOTE_RELEASE.set()
        SLOW_PET_RELEASE.set()
        os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=20)
        api.shutdown()
        api.server_close()
        log.close()
        if original_frontend_env is not None:
            frontend_env.write_bytes(original_frontend_env)

if __name__ == '__main__':
    run()
