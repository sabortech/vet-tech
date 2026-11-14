"""Photo frames in real chat assets with a simulated bridge; no Xano/AI calls."""
import argparse
import base64
from pathlib import Path
import runpy
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'openspec/changes/reorganizar-fluxos-chat/evidence'
MOCK=runpy.run_path(str(ROOT/'tests/integration/chat_flows_browser.py'))['MOCK']


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--chromium');args=parser.parse_args()
 photo='data:image/png;base64,'+base64.b64encode((ROOT/'assets/mascote/chat-avatar.png').read_bytes()).decode()
 mock=MOCK.replace("[{id:19,status:'encerrado',own:true,created_at:1700000000000}]", "[{id:21,pet_id:7,status:'aguardando',own:true},{id:20,pet_id:8,status:'em_atendimento',own:true},{id:19,pet_id:9,status:'encerrado',own:true}]")
 mock=mock.replace("status:d.action==='support_close'?'encerrado':'aguardando'","status:d.action==='support_close'?'encerrado':(window.ticketStatus||'aguardando')")
 mock=mock.replace("pet:{name:'Luna'}", "pet:{name:'Luna',photo:window.petPhoto}")
 mock=mock.replace("queueMicrotask(()=>", "if(detail.ticket&&window.ticketStatus==='em_atendimento'){detail.ticket.tutor={name:'Ana <Silva>',phone:'11999999999',email:'qa@example.invalid'};detail.ticket.veterinarian={name:'Marina',crmv:'123',uf:'SP'};detail.ticket.messages=[{author_profile:'veterinario',text:'Olá',at:1700000000000},{author_profile:'tutor',text:'Olá também',at:1700000000001}];}if(detail.ticket&&window.blankTutor)detail.ticket.tutor={name:''};if(d.action==='support_list')detail.pet_photos={'7':window.petPhoto,'9':'data:image/png;base64,AAAA'};queueMicrotask(()=>")
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path=args.chromium)
  for profile,theme,width in [('tutor','dark',390),('veterinario','light',1366)]:
   page=browser.new_page(viewport={'width':width,'height':900})
   page.route('https://chat.test/**',lambda route:route.fulfill(body=''))
   page.goto('https://chat.test/')
   page.set_content(f'<div id="vettech-chat-session" data-chat-key="{profile}:7"></div><form id="vettech-chat-bridge"><input id="vettech-chat-payload"></form><button id="vettech-mascote">Abrir</button>')
   page.add_style_tag(path=str(ROOT/'assets/vet_tech.css'));page.add_style_tag(path=str(ROOT/'assets/support-chat.css'))
   page.evaluate('value=>window.petPhoto=value',photo)
   page.evaluate('theme=>document.documentElement.dataset.vtTheme=theme',theme)
   page.evaluate('('+mock+')()');page.add_script_tag(path=str(ROOT/'assets/support-chat.js'))
   page.evaluate("window.dispatchEvent(new Event('vettech:mascote-click'))")
   page.get_by_role('button',name='Atendimentos',exact=True).click()
   expect(page.locator('.vt-chat-ticket-card')).to_have_count(3)
   if profile=='tutor':expect(page.get_by_role('button',name='Ver conversa',exact=True)).to_have_count(3)
   expect(page.locator('.vt-chat-pet-avatar img')).to_have_count(1)
   expect(page.locator('.vt-chat-pet-avatar .vt-chat-icon svg')).to_have_count(2)
   assert page.locator('.vt-chat-pet-avatar img').evaluate('el=>el.complete&&el.naturalWidth>0')
   assert page.locator('.vt-chat-pet-avatar').first.evaluate('el=>getComputedStyle(el).borderRadius')=='50%'
   assert page.evaluate("probe.requests.filter(r=>r.action==='support_list').length")==1
   assert page.locator('.vt-chat-ticket-card>.vt-chat-status-led').count()==3
   assert page.locator('.vt-chat-pet-avatar>.vt-chat-status-led').count()==3
   rect=page.locator('.vt-chat-ticket-card>.vt-chat-status-led rect').first
   assert rect.evaluate('el=>getComputedStyle(el).animationDuration')=='6s'
   page.emulate_media(reduced_motion='reduce')
   assert rect.evaluate('el=>getComputedStyle(el).animationDuration')=='12s'
   page.emulate_media(reduced_motion='no-preference')
   page.screenshot(path=str(OUT/f'pet-photos-{profile}-{theme}.png'))
   page.get_by_role('button',name='Ver conversa',exact=True).first.click()
   page.get_by_role('button',name='Informações do atendimento: Aguardando veterinário',exact=True).click()
   expect(page.locator('.vt-chat-detail-pet img')).to_have_count(1)
   assert page.locator('.vt-chat-led-track').evaluate('el=>getComputedStyle(el).stroke')=='rgb(255, 82, 82)'
   assert page.locator('.vt-chat-header').evaluate('el=>getComputedStyle(el).backgroundColor')=='rgb(255, 82, 82)'
   assert page.locator('#vt-chat-ticket-details>.vt-chat-status-led rect').evaluate('el=>getComputedStyle(el).stroke')=='rgb(255, 82, 82)'
   page.screenshot(path=str(OUT/f'pet-details-{profile}-{theme}.png'))
   assert page.evaluate("probe.requests.filter(r=>r.action==='support_get').length")==1
   image=page.locator('.vt-chat-detail-pet img')
   assert image.evaluate('el=>getComputedStyle(el).clipPath')=='circle(50%)'
   page.evaluate("window.ticketStatus='em_atendimento'")
   page.get_by_role('button',name='Atualizar atendimento',exact=True).click()
   assert page.locator('.vt-chat-led-track').evaluate('el=>getComputedStyle(el).stroke')=='rgb(250, 204, 21)'
   assert page.locator('#vt-chat-ticket-details>.vt-chat-status-led rect').evaluate('el=>getComputedStyle(el).stroke')=='rgb(250, 204, 21)'
   assert page.locator('.vt-chat-header').evaluate('el=>getComputedStyle(el).backgroundColor')=='rgb(250, 204, 21)'
   assert page.locator('.vt-chat-send').evaluate('el=>getComputedStyle(el).backgroundColor')=='rgb(250, 204, 21)'
   assert page.locator('.vt-chat-header').evaluate('el=>getComputedStyle(el).color')=='rgb(25, 27, 20)'
   if profile=='tutor':
    expect(page.get_by_role('region',name='Dados do tutor')).to_have_count(0)
    expect(page.get_by_role('button',name='Encerrar atendimento',exact=True)).to_have_count(0)
    expect(page.get_by_role('textbox',name='Motivo do encerramento')).to_have_count(0)
   else:
    expect(page.get_by_role('region',name='Dados do tutor')).to_contain_text('11999999999')
    expect(page.get_by_role('region',name='Dados do tutor')).to_contain_text('qa@example.invalid')
    expect(page.get_by_role('button',name='Encerrar atendimento',exact=True)).to_be_visible()
    expect(page.get_by_role('textbox',name='Motivo do encerramento')).to_be_visible()
   lines=page.locator('.vt-chat-status>span').evaluate_all('els=>els.map(el=>({top:el.getBoundingClientRect().top,bottom:el.getBoundingClientRect().bottom}))')
   assert len(lines)==3 and all(lines[i]['bottom']<=lines[i+1]['top'] for i in range(2)),lines
   expected_peer='tutor' if profile=='veterinario' else 'veterinario'
   expect(page.locator('.vt-chat-header>.vt-chat-avatar')).to_have_attribute('data-profile',expected_peer)
   expect(page.locator('#vt-chat-title')).to_have_text('Ana <Silva>' if profile=='veterinario' else 'Marina')
   expect(page.locator('.vt-chat-messages .vt-chat-author-label').filter(has_text='Tutor · Ana <Silva>')).to_have_count(1)
   expect(page.locator('.vt-chat-messages .vt-chat-author-label').filter(has_text='Veterinário · Marina')).to_have_count(1)
   expect(page.locator('.vt-chat-messages .vt-chat-bubble p').filter(has_text='Veterinário:')).to_have_count(0)
   expect(page.locator('.vt-chat-messages .vt-chat-bubble p').filter(has_text='Tutor:')).to_have_count(0)
   expect(page.locator('.vt-chat-messages .vt-chat-avatar[data-profile=tutor]')).to_have_count(1)
   expect(page.locator('.vt-chat-messages .vt-chat-avatar[data-profile=veterinario]')).to_have_count(1)
   expect(page.locator('.vt-chat-messages .is-user .vt-chat-avatar')).to_have_attribute('data-profile',profile)
   page.screenshot(path=str(OUT/f'participant-details-{profile}-{theme}.png'))
   page.get_by_role('button',name='Fechar informações do atendimento').click()
   page.screenshot(path=str(OUT/f'participant-chat-{profile}-{theme}.png'))
   if profile=='veterinario':
    page.evaluate('window.blankTutor=true')
    page.get_by_role('button',name='Informações do atendimento: Em atendimento',exact=True).click()
    page.get_by_role('button',name='Atualizar atendimento',exact=True).click()
    expect(page.locator('.vt-chat-status')).to_contain_text('Nome não informado')
    expect(page.get_by_role('region',name='Dados do tutor')).to_contain_text('Não informado')
    expect(page.locator('.vt-chat-author-label').filter(has_text='Tutor · Nome não informado')).to_have_count(1)
    page.get_by_role('button',name='Fechar informações do atendimento').click()
   page.get_by_role('button',name='Nova conversa',exact=True).click()
   expect(page.locator('#vt-chat-title')).to_have_text('Assistente Vet Tech')
   assert page.locator('#vettech-support-chat').get_attribute('data-status') is None
   expect(page.locator('.vt-chat-header>.vt-chat-avatar img')).to_have_count(1)
   page.close()
  browser.close()
 print('OK: photos, circular frames, absent/invalid fallback and popup without per-pet requests.')


if __name__=='__main__':main()
