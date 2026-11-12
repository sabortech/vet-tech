import json,sys,os
from pathlib import Path
from uuid import uuid4
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright,expect
load_dotenv('.env')
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from clinical_smoke import Smoke,PRIVATE
import argparse
parser=argparse.ArgumentParser(description='Duas sessoes reais com fixtures sinteticas; o contexto inicial e preparado pela API, sem simular publicacao n8n.')
parser.add_argument('--run',required=True)
parser.add_argument('--development',action='store_true',required=True)
parser.add_argument('--url',default='http://localhost:3002')
parser.add_argument('--chromium',default='C:/Program Files/Google/Chrome/Application/chrome.exe')
args=parser.parse_args()
s=Smoke(PRIVATE/args.run)
code,data=s.api('POST','tutor/chat','ta',{'bridge_key':os.environ['SUPPORT_CHAT_BRIDGE_SECRET'],'payload':{'action':'create','conversation_id':str(uuid4()),'pet_id':s.data['pets']['a'],'consent':True,'reason':'Fluxo sintético navegador','context':[{'role':'user','content':'Pergunta sintética navegador'}]}},'vettech-support')
if code!=200:
    (s.folder/'support-browser-error.json').write_text(json.dumps(data))
    raise SystemExit('Falha ao preparar chamado sintético')
tid=data['ticket']['id'];s.data.setdefault('support_tickets',[]).append(tid);s.persist()
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=args.chromium)
    tutor=browser.new_page();vet=browser.new_page()
    for page,actor in ((tutor,'ta'),(vet,'va')):
        page.set_default_timeout(60000)
        page.add_init_script("window.supportProbe=[]; window.addEventListener('vettech:support-response', e=>supportProbe.push({action:e.detail.action,ok:e.detail.ok,status:e.detail.ticket?.status}));")
        page.goto(args.url.rstrip('/')+'/login')
        page.wait_for_function('window.__vetTechChatReady === true')
        page.get_by_label('E-mail',exact=True).fill(s.data['actors'][actor]['email'])
        page.get_by_label('Senha',exact=True).fill(s.data['actors'][actor]['password'])
        for attempt in range(3):
            page.get_by_role('button',name='Login',exact=True).click()
            try:
                page.wait_for_function("document.getElementById('vettech-chat-session')?.dataset.chatKey",timeout=15000)
                break
            except Exception:
                text=page.locator('body').inner_text()
                if 'limitou temporariamente' in text and attempt<2:
                    print('manual_login_retry_after_rate_limit',flush=True)
                    page.wait_for_timeout(20000)
                    continue
                (s.folder/'support-browser-error.txt').write_text(text,encoding='utf-8')
                print(json.dumps({'failed_login':actor,'connect_error':'Não foi possível conectar ao Xano' in text,'rate_limited':'limitou temporariamente' in text}),flush=True)
                raise
        print('login_ready_'+actor,flush=True)
    for page,actor in ((tutor,'ta'),(vet,'va')):
        page.locator('#vettech-mascote').click()
        page.get_by_role('dialog',name='Assistente Vet Tech').evaluate('el => Promise.all(el.getAnimations().map(a => a.finished))')
        page.get_by_role('button',name='Atendimentos',exact=True).click()
        print('support_list_requested_'+actor,flush=True)
        try:
            page.get_by_role('button',name=f'#{tid} · aguardando'+(' · Meu atendimento' if actor=='ta' else ''),exact=True).click(timeout=35000)
        except Exception:
            print('support_status_'+actor,page.locator('[role=status]').all_text_contents(),flush=True)
            raise
        print('ticket_selected_'+actor,flush=True)
        if actor=='va':
            expect(page.get_by_text('Pergunta sintética navegador',exact=False)).to_be_visible()
    tutor.get_by_role('textbox',name='Digite sua pergunta').wait_for(state='visible')
    try:
        expect(tutor.get_by_role('textbox',name='Digite sua pergunta')).to_be_enabled(timeout=60000)
    except Exception:
        print('tutor_support_events',tutor.evaluate('supportProbe'),flush=True)
        print('tutor_support_status',tutor.locator('[role=status]').all_text_contents(),flush=True)
        raise
    tutor.get_by_role('textbox',name='Digite sua pergunta').fill('Mensagem sintética da interface')
    tutor.get_by_role('button',name='Enviar mensagem',exact=True).click()
    expect(vet.get_by_text('Tutor: Mensagem sintética da interface',exact=True)).to_be_visible(timeout=60000)
    vet.get_by_role('textbox',name='Digite sua pergunta').fill('Orientação sintética da interface')
    vet.get_by_role('button',name='Enviar mensagem',exact=True).click()
    expect(tutor.get_by_text('Veterinário: Orientação sintética da interface',exact=True)).to_be_visible(timeout=60000)
    vet.get_by_role('textbox',name='Motivo do encerramento').fill('Verificação sintética concluída')
    vet.get_by_role('button',name='Encerrar atendimento',exact=True).click()
    expect(tutor.get_by_text('Atendimento encerrado: Verificação sintética concluída',exact=True)).to_be_visible(timeout=60000)
    expect(tutor.get_by_role('textbox',name='Digite sua pergunta')).to_be_disabled()
    print('PASS: tutor e veterinário em sessões reais, assunção, mensagens bidirecionais e encerramento.',flush=True)
    browser.close()
