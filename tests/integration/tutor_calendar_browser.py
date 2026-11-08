"""Painéis reais com API sintética: calendário do tutor, nascimento e regressão médica."""
from datetime import timedelta
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import signal
import shutil
import tempfile
import socket
import subprocess
import sys
import threading
import time

import httpx
from playwright.sync_api import expect, sync_playwright
import dashboard_dates_browser as fixture

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'openspec/changes/archive/2026-11-07-padronizar-calendarios-tutor/evidence'


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    # Keep generated routes, memoized components and build output away from
    # the running development server. Only installed dependencies are reused.
    active_files = [ROOT / '.web/env.json', ROOT / '.web/app/routes/[dashboard]._index.jsx',
                    ROOT / '.web/app_components/vet_tech/pages/dashboard.jsx']
    workspace = tempfile.TemporaryDirectory(prefix='vet-tech-tutor-calendar-', ignore_cleanup_errors=True)
    test_root = Path(workspace.name)
    shutil.copytree(ROOT / 'vet_tech', test_root / 'vet_tech', ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy2(ROOT / 'rxconfig.py', test_root / 'rxconfig.py')
    shutil.copytree(ROOT / '.web', test_root / '.web', ignore=shutil.ignore_patterns('node_modules', 'build', '__pycache__'))
    (test_root / '.web/node_modules').symlink_to(ROOT / '.web/node_modules', target_is_directory=True)
    (test_root / 'assets').symlink_to(ROOT / 'assets', target_is_directory=True)
    api = ThreadingHTTPServer(('127.0.0.1', 0), fixture.SyntheticAPI)
    threading.Thread(target=api.serve_forever, daemon=True).start()
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    origin = f'http://localhost:{port}'
    log = (OUT / 'reflex.log').open('w')
    env = {**os.environ, 'XANO_API_BASE_URL': f'http://127.0.0.1:{api.server_port}', 'XANO_TENANT': ''}
    process = subprocess.Popen([sys.executable, '-m', 'reflex', 'run', '--env', 'prod', '--single-port', '--backend-port', str(port)], cwd=test_root, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    checks, errors = [], []
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
        # Source edits may legitimately finish hot-reloading during startup.
        # Snapshot after the isolated build, before browser interactions.
        original_active_files = {path: path.read_bytes() for path in active_files}
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path='/home/usuario/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome', args=['--no-sandbox'])
            context = browser.new_context(viewport={'width': 1440, 'height': 1050}, locale='pt-BR')
            page = context.new_page()
            page.set_default_timeout(15000)
            page.on('pageerror', lambda e: errors.append(str(e)))

            def login(email):
                page.goto(origin + '/login')
                page.get_by_label('E-mail', exact=True).fill(email)
                page.get_by_label('Senha', exact=True).fill('synthetic-password')
                page.get_by_role('button', name='Login', exact=True).click()

            def pick_month_year(dialog, year, month):
                dialog.get_by_role('combobox', name='Ano do calendário', exact=True).click()
                page.get_by_role('option', name=str(year), exact=True).click()
                dialog.get_by_role('combobox', name='Mês do calendário', exact=True).click()
                page.get_by_role('option', name=month, exact=True).click()

            login('tutor@example.invalid')
            expect(page.get_by_role('heading', name='Perfil do tutor', exact=True)).to_be_visible()
            page.goto(origin + '/dashboard')
            expect(page.locator('.dashboard-pet-card')).to_have_count(2)
            page.locator('.dashboard-pet-actions').first.get_by_role('button', name='Agendar consulta', exact=True).click()
            booking = page.locator('.tutor-booking-calendar')
            expect(booking).to_be_visible()
            expect(booking.locator('.vet-date-led')).to_be_visible()
            past = fixture.TODAY - timedelta(days=1)
            if past.month == fixture.TODAY.month:
                expect(booking.get_by_role('button', name=past.isoformat(), exact=True)).to_be_disabled()
            for width in (1440, 390):
                page.set_viewport_size({'width': width, 'height': 1050})
                for theme in ('light', 'dark'):
                    page.evaluate('(t)=>document.documentElement.dataset.vtTheme=t', theme)
                    page.wait_for_timeout(100)
                    page.screenshot(path=str(OUT / f'agendamento-{width}-{theme}.png'))
                    assert booking.evaluate('(el)=>el.scrollWidth<=el.clientWidth'), (width, theme)
            page.set_viewport_size({'width': 1440, 'height': 1050})
            target_year = fixture.TODAY.year + 1
            pick_month_year(booking, target_year, 'Janeiro')
            target = f'{target_year}-01-08'
            booking.get_by_role('button', name=target, exact=True).click()
            expect(booking.get_by_text(f'Dia selecionado: 08/01/{target_year}', exact=True)).to_be_visible()
            expect(booking.get_by_label('Data selecionada', exact=True)).to_have_value(f'08/01/{target_year}')
            expect(booking.get_by_label('Data selecionada', exact=True)).to_have_attribute('readonly', '')
            expect(booking.locator('#booking-time')).to_have_value('')
            page.screenshot(path=str(OUT / 'agendamento-data-preenchida.png'))
            booking.locator('#booking-time').fill('07:59')
            booking.get_by_role('button', name='Continuar', exact=True).click()
            expect(booking.get_by_text('Escolha dia e horário futuros entre 08h e 17h.', exact=True)).to_be_visible()
            booking.locator('#booking-time').fill('08:00')
            booking.get_by_role('button', name='Continuar', exact=True).click()
            expect(page.get_by_label('Motivo', exact=True)).to_be_visible()
            page.get_by_role('button', name='Voltar', exact=True).click()
            expect(booking).to_be_visible()
            expect(booking.get_by_role('button', name=target, exact=True)).to_have_attribute('aria-pressed', 'true')
            booking.get_by_role('button', name='Cancelar', exact=True).click()
            expect(booking).not_to_be_visible()
            checks.append('agendamento: painel, mês/ano, passado bloqueado, horário, etapas, volta e cancelamento')

            page.goto(origin + '/')
            expect(page.get_by_role('heading', name='Perfil do tutor', exact=True)).to_be_visible()
            page.get_by_label('Nome do pet', exact=True).fill('Rascunho preservado')
            page.get_by_role('button', name='Data de nascimento', exact=True).click()
            birth = page.locator('.pet-birth-calendar')
            expect(birth).to_be_visible()
            future = fixture.TODAY + timedelta(days=1)
            if future.month == fixture.TODAY.month:
                expect(birth.get_by_role('button', name=future.isoformat(), exact=True)).to_be_disabled()
            for width in (1440, 390):
                page.set_viewport_size({'width': width, 'height': 1050})
                for theme in ('light', 'dark'):
                    page.evaluate('(t)=>document.documentElement.dataset.vtTheme=t', theme)
                    page.wait_for_timeout(100)
                    page.screenshot(path=str(OUT / f'nascimento-{width}-{theme}.png'))
                    assert birth.evaluate('(el)=>el.scrollWidth<=el.clientWidth'), (width, theme)
            page.set_viewport_size({'width': 1440, 'height': 1050})
            pick_month_year(birth, 2024, 'Fevereiro')
            birth.get_by_role('button', name='2024-02-29', exact=True).click()
            expect(birth).not_to_be_visible()
            expect(page.locator('#pet-birth-date')).to_contain_text('29/02/2024')
            expect(page.get_by_label('Nome do pet', exact=True)).to_have_value('Rascunho preservado')
            page.get_by_role('button', name='Data de nascimento', exact=True).click()
            birth.get_by_role('button', name='Limpar data', exact=True).click()
            expect(page.locator('#pet-birth-date')).to_contain_text('Data de nascimento')
            checks.append('nascimento direto: futuro bloqueado, mês/ano, bissexto, ISO e limpeza preservando rascunho')

            page.goto(origin + '/dashboard')
            expect(page.locator('.dashboard-pet-card')).to_have_count(2)
            page.get_by_role('button', name='Novo pet', exact=True).click()
            expect(page.get_by_role('heading', name='Novo pet', exact=True)).to_be_visible()
            page.get_by_label('Nome do pet', exact=True).fill('Pet sintético calendário')
            page.get_by_role('button', name='Data de nascimento', exact=True).click()
            expect(birth).to_be_visible()
            page.keyboard.press('Escape')
            expect(birth).not_to_be_visible()
            expect(page.get_by_role('heading', name='Novo pet', exact=True)).to_be_visible()
            expect(page.get_by_label('Nome do pet', exact=True)).to_have_value('Pet sintético calendário')
            assert not any(r['method']=='POST' and r['path']=='pets' for r in fixture.REQUESTS)
            page.get_by_role('button', name='Data de nascimento', exact=True).click()
            pick_month_year(birth, 2024, 'Fevereiro')
            birth.get_by_role('button', name='2024-02-29', exact=True).click()
            expect(page.get_by_role('heading', name='Novo pet', exact=True)).to_be_visible()
            dialog = page.get_by_role('dialog')
            dialog.get_by_role('combobox').first.click()
            page.get_by_role('option', name='Cachorro', exact=True).click()
            dialog.get_by_role('button', name='Cadastrar pet', exact=True).click()
            for _ in range(100):
                if any(r['method']=='POST' and r['path']=='pets' for r in fixture.REQUESTS):
                    break
                page.wait_for_timeout(20)
            assert any(r['method']=='POST' and r['path']=='pets' and r['payload'].get('data_nasc')=='2024-02-29' for r in fixture.REQUESTS)
            checks.append('Novo pet: calendário aninhado fecha por Escape/seleção sem fechar pai; cadastro enviou data ISO')
            context.close()

            context = browser.new_context(viewport={'width':1440,'height':1050}, locale='pt-BR')
            page = context.new_page()
            page.on('pageerror', lambda e: errors.append(str(e)))
            login('vet@example.invalid')
            expect(page.get_by_role('button', name='Horários', exact=True)).to_be_visible()
            page.get_by_role('button', name='Horários', exact=True).click()
            page.get_by_role('button', name='Escolher data', exact=True).click()
            expect(page.get_by_role('heading', name='Um dia de cada vez', exact=True)).to_be_visible()
            expect(page.get_by_role('combobox', name='Mês do calendário', exact=True)).to_be_visible()
            page.screenshot(path=str(OUT / 'calendario-medico.png'))
            checks.append('regressão: calendário da agenda médica mantém painel e seletores')
            assert not errors, errors
            assert all(path.read_bytes() == content for path, content in original_active_files.items())
            checks.append('build e testes isolados preservaram módulos e configuração do servidor ativo')
            (OUT / 'results.json').write_text(json.dumps({'checks':checks,'javascript_errors':errors}, ensure_ascii=False, indent=2))
            print(json.dumps({'checks':checks,'javascript_errors':errors}, ensure_ascii=False))
            browser.close()
    finally:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=20)
        api.shutdown()
        api.server_close()
        log.close()
        workspace.cleanup()

if __name__ == '__main__':
    run()
