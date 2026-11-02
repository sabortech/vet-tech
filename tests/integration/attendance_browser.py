"""Verificação visual da prévia isolada; nunca apontar para produção com dados reais."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url', default='http://localhost:3017')
parser.add_argument('--chromium', required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
results = []
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=args.chromium, args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 1920, 'height': 1080}, device_scale_factor=1)
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(args.url)
    page.get_by_role('heading', name='Jessy', exact=True).wait_for()
    page.evaluate('document.fonts.ready')
    def no_overflow():
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    def screenshot(name, full=True):
        page.screenshot(path=str(args.output/name), full_page=full, animations='disabled')
    no_overflow()
    assert 'blur(14px)' in page.locator('.attendance-glass').evaluate('(e)=>getComputedStyle(e).backdropFilter')
    assert page.locator('.attendance-catalog').evaluate('(e)=>getComputedStyle(e).backgroundColor') == 'rgb(231, 239, 226)'
    assert page.locator('#clinic-diagnostico').evaluate('(e)=>getComputedStyle(e.parentElement).borderRadius') == '12px'
    assert page.locator('.attendance-status').inner_text() == 'Em atendimento'
    assert page.locator('#vettech-mascote').count() == 1
    assert page.locator('.attendance-record-card').count() == 4
    assert page.locator('.attendance-fields').evaluate('(e)=>getComputedStyle(e).gridTemplateColumns.split(" ").length') == 2
    screenshot('desktop.png')
    page.evaluate('scrollTo(0,document.body.scrollHeight)')
    screenshot('desktop-rodape.png', False)
    results.append('Desktop 1920x1080: vidro, textarea arredondado, catálogo claro, status, cards e wallpaper ao rolar')
    page.locator('#clinic-diagnostico').fill('Avaliação sintética de apresentação')
    page.locator('#clinic-obs').fill('Observações sintéticas\nSegunda linha')
    page.get_by_text('Há alterações não salvas', exact=True).wait_for()
    for card in page.locator('.attendance-record-card').all():
        card.get_by_role('button', name='Adicionar', exact=True).click()
        expect(card.locator('.attendance-count')).to_have_text('1')
    page.locator('.attendance-record-card').first.get_by_label('Vacina', exact=True).fill('Vacina sintética')
    screenshot('desktop-registros.png')
    page.set_viewport_size({'width': 390, 'height': 844})
    no_overflow()
    assert page.locator('.attendance-fields').evaluate('(e)=>getComputedStyle(e).gridTemplateColumns.split(" ").length') == 1
    screenshot('mobile-registros.png')
    for card in page.locator('.attendance-record-card').all():
        card.get_by_role('button', name='Remover registro', exact=True).click()
        expect(card.locator('.attendance-count')).to_have_text('0')
    page.get_by_role('button', name='Cadastrar doença no catálogo', exact=True).click()
    page.get_by_label('Nome da doença', exact=True).wait_for()
    no_overflow()
    screenshot('mobile-catalogo.png')
    page.get_by_role('button', name='Cadastrar doença no catálogo', exact=True).click()
    page.get_by_role('button', name='Voltar às consultas', exact=True).click()
    page.get_by_role('alertdialog').wait_for()
    page.get_by_role('button', name='Continuar editando', exact=True).click()
    page.get_by_role('alertdialog').wait_for(state='hidden')
    page.evaluate('scrollTo(0,0)')
    screenshot('mobile.png')
    page.evaluate("window.dispatchEvent(new StorageEvent('storage',{key:'vet_tech_theme',newValue:'dark'}))")
    no_overflow()
    assert page.locator('#clinic-diagnostico').evaluate('(e)=>getComputedStyle(e).color') == 'rgb(238, 243, 239)'
    screenshot('mobile-tema-escuro.png')
    page.locator('#clinic-motivo').focus()
    assert page.locator('#clinic-motivo').evaluate('(e)=>getComputedStyle(e.parentElement).boxShadow') != 'none'
    page.emulate_media(reduced_motion='reduce')
    assert page.locator('.attendance-status-dot').evaluate('(e)=>getComputedStyle(e).animationName') == 'none'
    results.append('Mobile 390x844: sem overflow, adicionar/remover nos quatro grupos, edição, accordion, confirmação de saída, foco, tema escuro e movimento reduzido')
    assert not errors, errors
    results.append('Nenhuma exceção JavaScript; nenhuma chamada ao Xano na prévia')
    browser.close()
(args.output/'browser-results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n')
print('\n'.join(results))
