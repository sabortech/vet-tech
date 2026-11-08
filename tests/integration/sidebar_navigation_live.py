"""Read-only menu smoke test using existing synthetic foundation accounts.

PYTHONPATH=/tmp/vet-tech-browser-tools .venv/bin/python tests/integration/sidebar_navigation_live.py
"""
import json
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'openspec/changes/archive/2026-11-07-otimizar-carregamento-interface/evidence/navigation-live.json'
DESTINATIONS = {
    'Dashboard': '/dashboard', 'Prontuário': '/prontuario',
    'Vacinas': '/prontuario?secao=vacinas',
    'Medicamentos': '/prontuario?secao=medicamentos',
    'Doenças': '/prontuario?secao=doencas',
    'Consultas': '/prontuario?secao=consultas',
    'Meus Pets': '/', 'Configurações': '/configuracoes',
}


def main():
    credentials = json.loads((ROOT / '.env.foundation-fixtures.json').read_text())['identity_credentials']['tutor_a']
    checks, errors = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path='/home/usuario/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome',
            args=['--no-sandbox'],
        )
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('console', lambda m: errors.append(m.text) if 'Error loading route module' in m.text else None)
        page.route('https://fonts.googleapis.com/**', lambda r: r.abort())
        page.route('https://fonts.gstatic.com/**', lambda r: r.abort())
        page.goto('http://localhost:3000/login', wait_until='domcontentloaded')
        page.wait_for_function('!!window.__reflex', timeout=60000)
        page.get_by_label('E-mail', exact=True).fill(credentials['email'])
        page.get_by_label('Senha', exact=True).fill(credentials['password'])
        page.get_by_role('button', name='Login', exact=True).click()
        expect(page.locator('#vet-tech-sidebar')).to_be_visible(timeout=30000)
        for width, theme in [(1440, 'light'), (390, 'dark')]:
            page.set_viewport_size({'width': width, 'height': 1000})
            page.evaluate('(theme) => document.documentElement.classList.toggle("dark", theme === "dark")', theme)
            for label, destination in DESTINATIONS.items():
                if width < 768:
                    page.locator('.sidebar-toggle--mobile').click()
                page.locator('#vet-tech-sidebar').get_by_label(label, exact=True).click()
                expect(page).to_have_url('http://localhost:3000' + destination)
                expect(page.locator('#vet-tech-sidebar').get_by_label(label, exact=True)).to_have_attribute('aria-current', 'page')
                expect(page.get_by_role('button', name='Login', exact=True)).to_have_count(0)
                # Allow lazy route import failures/reloads to surface, as URL
                # alone can transiently match before React Router recovers.
                page.wait_for_timeout(350)
                assert urlsplit(page.url).path == urlsplit(destination).path
                assert not errors, errors
                checks.append({'width': width, 'theme': theme, 'menu': label, 'destination': destination})
            page.screenshot(path=str(OUT.with_name(f'navigation-{width}.png')))
        browser.close()
    OUT.write_text(json.dumps({'checks': checks, 'errors': errors}, indent=2, ensure_ascii=False))
    print(f'PASS: {len(checks)} cliques, sem falha de módulo ou retorno ao login.')


if __name__ == '__main__':
    main()
