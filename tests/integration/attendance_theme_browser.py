"""Theme checks for attendance and its portals, using the synthetic completion preview."""
import argparse
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url', default='http://localhost:3027')
parser.add_argument('--chromium', required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
results = []


def rgb(value):
    return [int(v)/255 for v in re.findall(r'[\d.]+', value)[:3]]


def contrast(foreground, background):
    def luminance(value):
        channels = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb(value)]
        return sum(v*w for v, w in zip(channels, [.2126, .7152, .0722]))
    a, b = sorted([luminance(foreground), luminance(background)])
    return (b+.05)/(a+.05)


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=args.chromium, args=['--no-sandbox'])
    for initial in ('light', 'dark'):
        context = browser.new_context(viewport={'width':1440, 'height':1000})
        context.add_init_script(f"localStorage.setItem('vet_tech_theme', {json.dumps(initial)})")
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(args.url+'/atendimento/43')
        page.get_by_role('heading', name='Jessy', exact=True).wait_for()
        expect(page.locator('html')).to_have_attribute('data-vt-theme', initial)
        expected = {'light':'rgb(26, 54, 41)', 'dark':'rgb(238, 243, 239)'}
        def switch(theme):
            page.evaluate("""theme=>{localStorage.setItem('vet_tech_theme',theme);window.dispatchEvent(new StorageEvent('storage',{key:'vet_tech_theme',newValue:theme}))}""", theme)
            expect(page.locator('html')).to_have_attribute('data-vt-theme', theme)
        def readable(locator, name):
            colors = locator.evaluate('''e=>{const text=getComputedStyle(e).color;let background=getComputedStyle(e).backgroundColor;while(e.parentElement && (background==='rgba(0, 0, 0, 0)' || background==='transparent')){e=e.parentElement;background=getComputedStyle(e).backgroundColor}return {text,background}}''')
            ratio = contrast(colors['text'], colors['background'])
            assert ratio >= 4.5, (name, colors, ratio)
            results.append(f'{initial}: {name}, contraste {ratio:.2f}:1')
        expect(page.locator('#clinic-diagnostico')).to_have_css('color', expected[initial])
        page.locator('#clinic-diagnostico').fill('Rascunho preservado nos dois temas')
        page.locator('#clinic-diagnostico').focus()
        assert page.locator('#clinic-diagnostico').evaluate('(e)=>getComputedStyle(e.parentElement).boxShadow') != 'none'
        readable(page.locator('#clinic-data_atendimento'), 'campo de data')
        readable(page.get_by_role('button', name='Terminar consulta', exact=True), 'ação principal')
        for card in page.locator('.attendance-record-card').all():
            card.get_by_role('button', name='Adicionar', exact=True).click()
        page.screenshot(path=str(args.output/f'{initial}-attendance.png'), full_page=True, animations='disabled')
        page.get_by_role('button', name='Data do atendimento', exact=True).click()
        calendar = page.locator('.attendance-date-dialog')
        expect(calendar).to_be_visible()
        expect(calendar).to_have_css('color', expected[initial])
        readable(calendar.get_by_role('button', name='2026-11-02', exact=True), 'dia selecionado')
        calendar.get_by_role('combobox', name='Mês do calendário').click()
        expect(page.locator('.attendance-date-select-menu')).to_be_visible()
        readable(page.locator('.attendance-date-select-menu [data-highlighted]'), 'opção destacada de mês')
        page.screenshot(path=str(args.output/f'{initial}-calendar-month.png'), animations='disabled')
        page.keyboard.press('Escape')
        other = 'light' if initial == 'dark' else 'dark'
        switch(other)
        expect(calendar).to_have_css('color', expected[other])
        switch(initial)
        expect(calendar).to_have_css('color', expected[initial])
        track = calendar.locator('.vet-date-led-track')
        assert track.evaluate('(e)=>getComputedStyle(e).filter').count('drop-shadow') == 3
        calendar.get_by_role('button', name='Fechar calendário', exact=True).click()
        page.get_by_role('button', name='Consultar histórico anterior', exact=True).click()
        history = page.locator('.attendance-history-dialog')
        expect(history.get_by_text('Avaliação anterior de Jessy', exact=True)).to_be_visible()
        expect(history).to_have_css('color', expected[initial])
        readable(history.locator('.attendance-history-section').first, 'histórico')
        readable(history.locator('.attendance-history-empty').first, 'texto secundário do histórico')
        switch(other)
        expect(history).to_have_css('color', expected[other])
        switch(initial)
        page.screenshot(path=str(args.output/f'{initial}-history.png'), animations='disabled')
        history.get_by_role('button', name='Fechar histórico', exact=True).click()
        expect(page.locator('#clinic-diagnostico')).to_have_value('Rascunho preservado nos dois temas')
        page.get_by_role('button', name='Salvar rascunho', exact=True).click()
        toast = page.locator('.attendance-saved-toast')
        expect(toast).to_be_visible()
        expect(toast).to_have_css('color', expected[initial])
        readable(toast, 'toast')
        switch(other)
        expect(toast).to_have_css('color', expected[other])
        switch(initial)
        page.screenshot(path=str(args.output/f'{initial}-toast.png'), animations='disabled')
        page.locator('#clinic-obs').fill('Alteração local')
        page.get_by_role('button', name='Voltar às consultas', exact=True).click()
        discard = page.get_by_role('alertdialog')
        expect(discard).to_be_visible()
        page.screenshot(path=str(args.output/f'{initial}-discard.png'), animations='disabled')
        discard.get_by_role('button', name='Continuar editando', exact=True).click()
        page.set_viewport_size({'width':390, 'height':844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(args.output/f'{initial}-mobile.png'), full_page=True, animations='disabled')
        page.get_by_role('button', name='Data do atendimento', exact=True).click()
        expect(calendar).to_have_css('color', expected[initial])
        assert calendar.evaluate('(e)=>e.scrollWidth <= e.clientWidth')
        page.screenshot(path=str(args.output/f'{initial}-mobile-calendar.png'), animations='disabled')
        calendar.get_by_role('button', name='Fechar calendário', exact=True).click()
        page.reload()
        page.get_by_role('heading', name='Jessy', exact=True).wait_for()
        expect(page.locator('html')).to_have_attribute('data-vt-theme', initial)
        expect(page.locator('#clinic-diagnostico')).to_have_css('color', expected[initial])
        assert not errors, errors
        context.close()
    browser.close()
(args.output/'results.md').write_text('Prévia sintética: preferência clara/escura persistida, formulário e quatro grupos, foco, calendário e seletor de mês, histórico, toast, confirmação de descarte e mobile 390px. Troca com calendário, histórico e toast abertos preserva valores e atualiza cores; sem overflow ou exceções JavaScript. Contrastes medidos nos campos/ações selecionados. Backend remoto não exercitado.\n\n'+'\n'.join(results)+'\n')
print('PASS: atendimento e painéis nos dois temas, preferência persistida e troca ao vivo')
