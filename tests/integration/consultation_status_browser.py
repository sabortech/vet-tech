"""Synthetic browser verification of tutor card colors and separate date/time."""
import json
import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import sys
import threading
import time
from http.server import ThreadingHTTPServer

import httpx
from playwright.sync_api import expect, sync_playwright
import consultation_cards_browser as fixture

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'openspec/changes/colorir-consultas-tutor-por-status/evidence'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fixture.CONSULTATIONS[0]['agendada_para'] = '2026-11-03T13:00:00Z'
    fixture.CONSULTATIONS[1]['agendada_para'] = '2026-12-01T03:05:00Z'
    api = ThreadingHTTPServer(('127.0.0.1', 0), fixture.API)
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
    results, errors = [], []
    try:
        for _ in range(120):
            if process.poll() is not None:
                raise RuntimeError('Synthetic backend stopped')
            try:
                if httpx.get(f'http://localhost:{port}/ping', timeout=.5).status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(.5)
        else:
            raise RuntimeError('Synthetic backend did not start')
        if env_file.read_bytes() != original:
            env_file.write_bytes(original)
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path='/home/usuario/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome', args=['--no-sandbox'])
            page = browser.new_page(viewport={'width':1440, 'height':1000})
            def endpoints(route):
                response = route.fetch()
                body = re.sub(r'((?:https?|ws)://localhost):\d+', lambda m: m[1] + f':{port}', response.text())
                route.fulfill(response=response, body=body)
            page.route('**/env.json*', endpoints)
            page.route('https://fonts.googleapis.com/**', lambda r: r.abort())
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto('http://localhost:3000/login', wait_until='domcontentloaded')
            page.wait_for_function('!!window.__reflex', timeout=60000)
            page.get_by_label('E-mail', exact=True).fill('tutor@example.invalid')
            page.get_by_label('Senha', exact=True).fill('synthetic-password')
            page.get_by_role('button', name='Login', exact=True).click()
            expect(page.locator('.pet-entry__action').first).to_be_visible()
            page.locator('.pet-entry__action').first.click()
            expect(page).to_have_url('http://localhost:3000/dashboard')
            page.locator('#vet-tech-sidebar').get_by_label('Consultas', exact=True).click()
            cards = page.locator('.consultation-card')
            expect(cards).to_have_count(5)
            expect(cards.nth(0)).to_have_attribute('data-status', 'finalizada')
            expect(cards.nth(0).locator('.consultation-list-fields .medication-field-value').nth(1)).to_have_text('Profissional sintético')
            expect(cards.nth(1).locator('.consultation-list-fields .medication-field-value').nth(1)).to_have_text('Nome não informado')
            expect(cards.nth(0).get_by_role('heading', name='Consulta: 43', exact=True)).to_be_visible()
            expect(cards.nth(0).locator('.consultation-date-time .medication-field-value')).to_have_text(['03/11/2026', '10:00'])
            expect(cards.nth(1).locator('.consultation-date-time .medication-field-value')).to_have_text(['01/12/2026', '00:05'])
            expect(cards.nth(3).locator('.consultation-date-time .medication-field-value')).to_have_text(['Não informado', 'Não informado'])
            for width in (1440, 390):
                page.set_viewport_size({'width':width, 'height':1000})
                for theme in ('light', 'dark'):
                    page.evaluate('(t)=>{document.documentElement.dataset.vtTheme=t;document.documentElement.classList.toggle("dark",t==="dark")}', theme)
                    for motion in ('no-preference', 'reduce'):
                        page.emulate_media(reduced_motion=motion)
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                        for index, color in ((0,'rgb(105, 202, 73)'), (1,'rgb(255, 82, 82)'), (3,'rgb(250, 204, 21)')):
                            card = cards.nth(index)
                            computed = card.evaluate('''e=>{const s=getComputedStyle(e), l=getComputedStyle(e.querySelector('.vet-date-led-track'));return {stroke:l.stroke,shadow:s.boxShadow,background:s.backgroundColor,duration:l.animationDuration,icons:e.querySelectorAll('.consultation-date-time svg').length}}''')
                            assert computed['stroke'] == color, computed
                            assert computed['icons'] == 2, computed
                            for field in card.locator('.consultation-date-time .medication-field').all():
                                icon = field.locator('.medication-field-icon').bounding_box()
                                value = field.locator(':scope > :not(.medication-field-icon)').bounding_box()
                                assert abs(icon['y'] + icon['height']/2 - value['y'] - value['height']/2) < 1, (icon, value)
                            title = card.locator('.consultation-card-title').bounding_box()
                            main_icon = card.locator('.medication-title-icon').bounding_box()
                            assert title['y'] + title['height'] <= main_icon['y'], (title, main_icon)
                            assert abs(title['x'] - main_icon['x']) < 1, (title, main_icon)
                            # Compare actual rendered shadow colors with the existing green default.
                            green = cards.nth(0).evaluate('e=>getComputedStyle(e).boxShadow')
                            assert (computed['shadow'] == green) == (index == 0), computed
                            assert computed['duration'] == ('20s' if motion == 'reduce' else '8s'), computed
                            assert card.get_by_role('button', name='Ver prontuário').count() == (1 if index == 0 else 0)
                            if index == 0:
                                fields = card.locator('.consultation-list-fields').bounding_box()
                                footer = card.locator('.vaccine-record-footer').bounding_box()
                                assert footer['y'] - fields['y'] - fields['height'] >= 15.5, (fields, footer)
                            results.append({'width':width,'theme':theme,'motion':motion,'status':card.get_attribute('data-status'),**computed})
                            if motion == 'no-preference':
                                card.screenshot(path=str(OUT / f'{index}-{width}-{theme}.png'))
                    for index in (2,4):
                        assert cards.nth(index).evaluate('e=>getComputedStyle(e).boxShadow') == green
            cards.nth(0).get_by_role('button', name='Ver prontuário').click()
            detail = page.locator('.consultation-detail')
            expect(detail.locator('.consultation-care')).to_have_count(7)
            expect(detail.locator('.care-status')).to_have_count(2)
            for width in (1440, 390):
                page.set_viewport_size({'width':width, 'height':1000})
                for theme in ('light', 'dark'):
                    page.evaluate('(t)=>{document.documentElement.dataset.vtTheme=t;document.documentElement.classList.toggle("dark",t==="dark")}', theme)
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                    for care in detail.locator('.consultation-care').all():
                        tone = care.get_attribute('data-care-tone')
                        expected = {'red':'rgb(255, 82, 82)', 'yellow':'rgb(250, 204, 21)', 'green':'rgb(105, 202, 73)', 'neutral':'rgb(148, 163, 184)'}[tone]
                        assert care.locator('.vet-date-led-track').evaluate('e=>getComputedStyle(e).stroke') == expected
                        assert care.locator('.vaccine-record-card').evaluate('e=>getComputedStyle(e).boxShadow') != 'none'
                    detail.screenshot(path=str(OUT / f'care-detail-{width}-{theme}.png'))
            assert not errors, errors
            browser.close()
        (OUT / 'results.json').write_text(json.dumps({'checks':results,'errors':errors}, ensure_ascii=False, indent=2))
        print(f'PASS: {len(results)} status/theme/viewport/motion combinations; date, time, absent values and actions')
    finally:
        if env_file.read_bytes() != original:
            env_file.write_bytes(original)
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGINT)
            process.wait(timeout=20)
        api.shutdown()
        log.close()


if __name__ == '__main__':
    main()
