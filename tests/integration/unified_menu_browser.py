"""Visual and functional checks against Reflex and the local synthetic Xano stub."""
import argparse
import json
import re
from pathlib import Path

from playwright.sync_api import expect, sync_playwright
from pet_loading_browser import control, stats, navigate, open_menu, menu_action

EVIDENCE = Path('openspec/changes/unificar-menus-tutor/evidence')


def login(page):
    page.goto('http://localhost:3000/login', wait_until='domcontentloaded')
    page.get_by_label('E-mail', exact=True).fill('qa@example.invalid')
    page.get_by_label('Senha', exact=True).fill('synthetic-local-only')
    page.get_by_role('button', name='Login', exact=True).click()
    expect(page.get_by_role('heading', name='Perfil do tutor', exact=True)).to_be_visible()


def measure(page):
    return page.locator('#vet-tech-sidebar').evaluate('''el => {
      const css=getComputedStyle(el), item=el.querySelector('.sidebar-item--active');
      const active=item&&getComputedStyle(item);
      return {width:Math.round(el.getBoundingClientRect().width), background:css.backgroundColor,
        color:css.color, radius:css.borderRadius, font:css.fontFamily,
        activeBackground:active?.backgroundColor,activeRadius:active?.borderRadius,
        itemHeight:item?.getBoundingClientRect().height,
        activeCount:el.querySelectorAll('[aria-current="page"]').length,
        overflow:document.documentElement.scrollWidth>innerWidth};
    }''')


def capture_baseline(browser):
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    evidence = []
    for theme in ('light', 'dark'):
        for expanded in (True, False):
            context = browser.new_context(viewport={'width': 1366, 'height': 900})
            context.add_init_script(f"localStorage.setItem('vet_tech_theme','{theme}'); localStorage.setItem('vet_tech_sidebar_expanded','{str(expanded).lower()}')")
            page = context.new_page()
            page.route('https://fonts.googleapis.com/**', lambda route: route.abort())
            page.route('https://fonts.gstatic.com/**', lambda route: route.abort())
            login(page)
            for area in ('meus-pets', 'configuracoes'):
                if area == 'configuracoes':
                    page.get_by_role('link', name='Configurações', exact=True).click()
                    expect(page.get_by_role('heading', name='Configurações', exact=True)).to_be_visible()
                sidebar = page.locator('#vet-tech-sidebar')
                if expanded == ('sidebar--collapsed' in (sidebar.get_attribute('class') or '')):
                    sidebar.locator('.sidebar-toggle--desktop').click()
                if expanded:
                    expect(sidebar).not_to_have_class(re.compile('sidebar--collapsed'))
                else:
                    expect(sidebar).to_have_class(re.compile('sidebar--collapsed'))
                suffix = f"{area}-{theme}-{'expanded' if expanded else 'rail'}"
                page.mouse.move(1360, 0)
                page.locator('#vet-tech-sidebar').screenshot(path=str(EVIDENCE / f'before-{suffix}.png'))
                evidence.append({'area': area, 'theme': theme, 'expanded': expanded, **measure(page)})
            context.close()
    (EVIDENCE / 'before-measurements.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
    print(json.dumps({'baseline_screenshots': len(evidence)}), flush=True)


def set_expanded(page, expanded):
    sidebar = page.locator('#vet-tech-sidebar')
    collapsed = 'sidebar--collapsed' in (sidebar.get_attribute('class') or '')
    if expanded == collapsed:
        sidebar.locator('.sidebar-toggle--desktop').click()
    if expanded:
        expect(sidebar).not_to_have_class(re.compile('sidebar--collapsed'))
    else:
        expect(sidebar).to_have_class(re.compile('sidebar--collapsed'))


def context_page(browser, width, theme='light', expanded=True):
    context = browser.new_context(viewport={'width': width, 'height': 844 if width < 500 else (768 if width == 1024 else 900)})
    context.add_init_script(f"localStorage.setItem('vet_tech_theme','{theme}'); localStorage.setItem('vet_tech_sidebar_expanded','{str(expanded).lower()}')")
    page = context.new_page()
    page.route('https://fonts.googleapis.com/**', lambda route: route.abort())
    page.route('https://fonts.gstatic.com/**', lambda route: route.abort())
    page.set_default_timeout(15000)
    return context, page


def verify_visuals(browser):
    baseline = json.loads((EVIDENCE / 'before-measurements.json').read_text(encoding='utf-8'))
    rows = []
    expected_names = ['Dashboard', 'Prontuário', 'Vacinas', 'Medicamentos', 'Doenças', 'Consultas', 'Exames', 'Meus Pets', 'Configurações']
    for width in (1366, 1024, 390):
        for theme in ('light', 'dark'):
            for expanded in (True, False):
                context, page = context_page(browser, width, theme, expanded)
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                login(page)
                for area, link, heading in [('meus-pets', 'Meus Pets', 'Perfil do tutor'),
                                            ('configuracoes', 'Configurações', 'Configurações'),
                                            ('prontuario', 'Prontuário', 'Início')]:
                    navigate(page, link)
                    expect(page.get_by_role('heading', name=heading, exact=True)).to_be_visible()
                    sidebar = page.locator('#vet-tech-sidebar')
                    if width < 768:
                        expect(sidebar).not_to_be_visible()
                        open_menu(page)
                    else:
                        set_expanded(page, expanded)
                    expect(sidebar.locator('.sidebar-item--active')).to_have_attribute('aria-label', link)
                    assert sidebar.locator('.sidebar-navigation .sidebar-item__label').all_text_contents() == expected_names
                    page.mouse.move(width - 3, 0)
                    sidebar.evaluate('el => el.scrollTop = 0')
                    suffix = f'{area}-{width}-{theme}-{"expanded" if expanded else "rail"}'
                    sidebar.screenshot(path=str(EVIDENCE / f'after-{suffix}.png'))
                    metrics = measure(page)
                    reference = next(row for row in baseline if row['area'] == 'meus-pets' and row['theme'] == theme and row['expanded'] == (expanded if width >= 768 else True))
                    for key in ('width', 'background', 'color', 'radius', 'font', 'activeBackground', 'activeRadius', 'itemHeight'):
                        assert metrics[key] == reference[key], f'{suffix}: {key} differs: {metrics[key]} != {reference[key]}'
                    assert metrics['activeCount'] == 1 and not metrics['overflow'], suffix
                    if width >= 768 and not expanded:
                        centers = sidebar.locator('.sidebar-navigation .sidebar-item__icon').evaluate_all('els => els.map(el => { const r=el.getBoundingClientRect(), p=el.closest(".sidebar").getBoundingClientRect(); return Math.abs(r.x+r.width/2-(p.x+p.width/2)); })')
                        assert max(centers) < 2, 'Rail icons misaligned'
                    if area == 'prontuario':
                        for label in ('Novo pet', 'Mudar pet', 'Sair'):
                            button = page.get_by_role('button', name=label, exact=True)
                            button.scroll_into_view_if_needed()
                            expect(button).to_be_in_viewport()
                    rows.append({'area': area, 'viewport': width, 'theme': theme, 'expanded': expanded, **metrics})
                    if width < 768:
                        page.keyboard.press('Escape')
                        expect(sidebar).not_to_be_visible()
                        expect(page.locator('.sidebar-toggle--mobile')).to_be_focused()
                        open_menu(page)
                        page.locator('.sidebar-backdrop').click(position={'x': width - 5, 'y': 300})
                        expect(sidebar).not_to_be_visible()
                assert not errors, repr(errors)
                context.close()
                print(f'PASS visuals {width} {theme} expanded={expanded}', flush=True)
    (EVIDENCE / 'after-measurements.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')


def verify_navigation(browser):
    for width in (1366, 390):
        control(delay=2, fail=False, rate_limit=False, reset=True)
        context, page = context_page(browser, width)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        login(page)
        navigate(page, 'Vacinas')
        expect(page.get_by_role('heading', name='Vacinas', exact=True)).to_be_visible()
        expect(page.get_by_role('button', name='Abrir Pet QA A', exact=True)).to_be_visible()
        assert not any('/historico' in path for path in stats()), 'Read before explicit selection'
        page.get_by_role('button', name='Abrir Pet QA A', exact=True).click()
        expect(page.get_by_text('Carregando dados do pet…', exact=True).first).to_be_visible()
        navigate(page, 'Medicamentos')
        expect(page.get_by_role('heading', name='Medicamentos', exact=True)).to_be_visible()
        expect(page.get_by_text('Carregando dados do pet…', exact=True).first).to_be_visible()
        expect(page.get_by_text('Nenhum registro publicado para este pet.', exact=True)).to_be_visible()
        navigate(page, 'Vacinas')
        expect(page.get_by_text('Vacina QA 1', exact=True)).to_be_visible()
        calls = stats()
        open_menu(page)
        if width >= 768:
            set_expanded(page, False)
            set_expanded(page, True)
        assert stats() == calls, 'Menu toggle made HTTP requests'
        menu_action(page, 'Novo pet')
        expect(page.get_by_role('dialog')).to_be_visible()
        expect(page.get_by_role('dialog').locator('input').first).to_be_focused()
        before = page.url
        page.get_by_role('button', name='Cancelar', exact=True).click()
        expect(page.get_by_role('dialog')).not_to_be_visible()
        assert page.url == before, 'Modal changed route'
        expect(page.get_by_role('button', name='Novo pet', exact=True)).to_be_focused()
        menu_action(page, 'Novo pet')
        expect(page.get_by_role('dialog')).to_be_visible()
        page.keyboard.press('Escape')
        expect(page.get_by_role('dialog')).not_to_be_visible()
        assert page.url == before
        navigate(page, 'Configurações')
        expect(page.locator('#settings-nome')).to_have_value('Tutor QA')
        page.locator('#settings-nome').fill('Rascunho QA')
        navigate(page, 'Vacinas')
        expect(page.get_by_role('alertdialog')).to_be_visible()
        page.get_by_role('button', name='Continuar editando', exact=True).click()
        expect(page.locator('#settings-nome')).to_have_value('Rascunho QA')
        assert page.url.endswith('/configuracoes')
        expect(page.get_by_role('link', name='Vacinas', exact=True)).to_be_focused()
        navigate(page, 'Vacinas')
        page.get_by_role('button', name='Descartar alterações', exact=True).click()
        expect(page.get_by_role('heading', name='Vacinas', exact=True)).to_be_visible()
        expect(page.get_by_text('Vacina QA 1', exact=True)).to_be_visible()
        assert page.url.endswith('/prontuario?secao=vacinas')
        if width < 768:
            expect(page.locator('#vet-tech-sidebar')).not_to_be_visible()
        navigate(page, 'Medicamentos')
        expect(page.get_by_role('heading', name='Medicamentos', exact=True)).to_be_visible()
        page.go_back(wait_until='domcontentloaded')
        expect(page.get_by_role('heading', name='Vacinas', exact=True)).to_be_visible()
        page.go_forward(wait_until='domcontentloaded')
        expect(page.get_by_role('heading', name='Medicamentos', exact=True)).to_be_visible()
        counts = stats()
        assert counts.get('/api:vettech-pets/pets/1') == 1
        assert counts.get('/api:vettech-clinical/tutor/pets/1/historico') == 1
        assert counts.get('/api:vettech-clinical/tutor/consultas?pet_id=1') == 1
        assert not errors, repr(errors)
        menu_action(page, 'Sair')
        expect(page.get_by_role('button', name='Login', exact=True)).to_be_visible()
        context.close()
        print(f'PASS navigation, guard, modal, history and cache {width}', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', action='store_true')
    parser.add_argument('--navigation-only', action='store_true')
    args = parser.parse_args()
    control(delay=0.5, fail=False, rate_limit=False, reset=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel='chrome', headless=True)
        try:
            if args.baseline:
                capture_baseline(browser)
            else:
                EVIDENCE.mkdir(parents=True, exist_ok=True)
                if not args.navigation_only:
                    verify_visuals(browser)
                verify_navigation(browser)
        finally:
            browser.close()


if __name__ == '__main__':
    main()
