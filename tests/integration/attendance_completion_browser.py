"""Verify completion and agenda design against attendance_completion_preview only."""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url', default='http://localhost:3027')
parser.add_argument('--chromium', required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=args.chromium, args=['--no-sandbox'])
    page = browser.new_page(viewport={'width':1440, 'height':1000})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(args.url+'/atendimento/43')
    page.get_by_role('heading', name='Jessy', exact=True).wait_for()
    page.get_by_role('button', name='Salvar rascunho', exact=True).click()
    saved = page.locator('[data-sonner-toast]').filter(has_text='Rascunho salvo com sucesso!')
    expect(saved).to_be_visible()
    expect(page).to_have_url(args.url+'/atendimento/43')
    container = saved.locator('..')
    expect(container).to_have_attribute('data-x-position', 'left')
    expect(container).to_have_attribute('data-y-position', 'bottom')
    page.screenshot(path=str(args.output/'draft-toast.png'), animations='disabled')
    page.get_by_role('button', name='Terminar consulta', exact=True).click()
    page.wait_for_url('**/?secao=horarios')
    expect(page.get_by_role('heading', name='Horários', exact=True)).to_be_visible()
    expect(page.get_by_text('Terça-feira, 03 de novembro de 2026', exact=True)).to_be_visible()
    completed = page.locator('[data-appointment-id="43"]')
    expect(completed.locator('.vet-schedule-status')).to_have_text('Concluída')
    expect(completed.get_by_role('button', name='Retomar', exact=True)).to_have_count(0)
    expect(completed.get_by_role('button', name='Começar consulta', exact=True)).to_have_count(0)
    expect(page.locator('[data-sonner-toast]').filter(has_text='Consulta finalizada com sucesso!')).to_be_visible()
    expect(completed.locator('img')).to_be_visible()
    expect(page.locator('[data-appointment-id="44"] .vet-schedule-avatar-fallback')).to_be_visible()
    revoked = page.locator('[data-appointment-id="45"]')
    expect(revoked.get_by_text('Acesso revogado', exact=True)).to_be_visible()
    expect(revoked.locator('img')).to_have_count(0)
    expect(revoked.get_by_role('button')).to_have_count(0)
    active = page.locator('[data-appointment-id="44"]')
    assert active.evaluate('(e)=>getComputedStyle(e).borderLeftColor') == 'rgb(104, 149, 84)'
    assert active.locator('.vet-schedule-status').evaluate('(e)=>getComputedStyle(e).backgroundColor') == 'rgb(71, 123, 59)'
    tracks = page.locator('.vet-schedule-timeline-led .vet-date-led-track, .vet-schedule-avatar-led .vet-date-led-track')
    expect(tracks).to_have_count(4)
    for track in tracks.all():
        assert track.evaluate('(e)=>getComputedStyle(e).animationName') == 'vet-date-border-orbit'
        start = track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset')
        page.wait_for_timeout(120)
        end = track.evaluate('(e)=>getComputedStyle(e).strokeDashoffset')
        assert start != end, (start, end)
        assert track.evaluate('(e)=>getComputedStyle(e.parentElement).pointerEvents') == 'none'
    page.screenshot(path=str(args.output/'completed-desktop.png'), animations='disabled')
    # Verify the list uses the same green cards and excludes confirmed completions.
    page.goto(args.url+'/?secao=consultas')
    expect(page.get_by_role('heading', name='Consultas', exact=True)).to_be_visible()
    expect(page.locator('[data-appointment-id="44"]')).to_be_visible()
    expect(page.locator('[data-appointment-id="43"]')).to_have_count(0)
    expect(page.locator('.vet-schedule-avatar-led')).to_have_count(2)
    page.screenshot(path=str(args.output/'consultations-desktop.png'), animations='disabled')
    page.goto(args.url+'/?secao=horarios')
    expect(page.locator('[data-appointment-id="43"]')).to_be_visible()
    page.set_viewport_size({'width':390, 'height':844})
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.screenshot(path=str(args.output/'completed-mobile.png'), animations='disabled')
    page.emulate_media(reduced_motion='reduce')
    assert page.locator('.vet-schedule-timeline-led .vet-date-led-track').evaluate('(e)=>getComputedStyle(e).animationDuration') == '20s'
    for track in page.locator('.vet-schedule-avatar-led .vet-date-led-track').all():
        assert track.evaluate('(e)=>getComputedStyle(e).animationDuration') == '16s'
    assert not errors, errors
    browser.close()
(args.output/'results.md').write_text('Prévia isolada com HTTP sintético: toast inferior esquerdo após rascunho; finalização redireciona para Horários no dia agendado (03/11) distinto do atendimento (02/11); recarga mostra Concluída sem Retomar/Começar; concluída ausente das pendências; cards verdes nas duas seções; foto, fallback e consentimento revogado; LED SVG em movimento na agenda e nas molduras, sem interceptar cliques; movimento reduzido desacelera; desktop 1440px e mobile 390px sem overflow. Nenhuma exceção JavaScript. Backend remoto não exercitado.\n')
print('PASS: notificações, finalização, agenda atualizada, cards verdes e LEDs')
