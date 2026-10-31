"""UI real com ponte simulada no navegador; nenhuma chamada à IA ou ao Xano."""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

MOCK = r"""() => {
  window.__vetTechChatReady = true;
  window.chatProbe = {requests:[], mode:'success', held:[]};
  document.addEventListener('submit', e => {
    if (e.target.id !== 'vettech-chat-bridge') return;
    e.preventDefault(); e.stopImmediatePropagation();
    const data = JSON.parse(document.getElementById('vettech-chat-payload').value);
    chatProbe.requests.push(data);
    if(data.action !== 'message') return;
    const result = {request_id:data.request_id, conversation_id:data.conversation_id,
      ok:chatProbe.mode !== 'error', reply:chatProbe.mode === 'error' ? 'Não consegui responder agora. Tente novamente.' : 'Resposta de teste: ' + data.message,
      error:chatProbe.mode === 'error' ? {code:'AI_UNAVAILABLE'} : null};
    if(chatProbe.mode === 'hold') chatProbe.held.push(result);
    else setTimeout(() => window.dispatchEvent(new CustomEvent('vettech:chat-response',{detail:result})),80);
  }, true);
}"""


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--url',default='http://localhost:3000')
    parser.add_argument('--chromium',default=None)
    args=parser.parse_args()
    evidence=Path('output/chat-verification');evidence.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=args.chromium)
        page=browser.new_page(viewport={'width':1366,'height':900})
        page.add_init_script('(' + MOCK + ')();')
        page.goto(args.url+'/login',wait_until='domcontentloaded')
        mascot=page.locator('#vettech-mascote');expect(mascot).to_be_visible()
        page.wait_for_function("document.getElementById('vettech-mascote')?.classList.contains('assets-ready') && window.__vetTechChat")
        mascot.click()
        chat=page.get_by_role('dialog',name='Assistente Vet Tech');expect(chat).to_be_visible()
        page.mouse.move(20,20)
        expect(mascot.locator('.mascote-hover')).to_have_css('opacity','1')
        expect(mascot.locator('.mascote-glow')).to_have_css('opacity','0.85')
        assert page.evaluate("getComputedStyle(document.querySelector('dialog'),'::backdrop').backgroundColor !== 'rgba(0, 0, 0, 0)'")
        chat.evaluate('el => Promise.all(el.getAnimations().map(a => a.finished))')
        assert chat.bounding_box()['y']>=0
        question=page.get_by_role('textbox',name='Digite sua pergunta')
        question.fill('Qual é a função do prontuário?')
        page.get_by_role('button',name='Enviar mensagem',exact=True).click()
        expect(chat).to_contain_text('Resposta de teste: Qual é a função do prontuário?')
        request=page.evaluate("chatProbe.requests.filter(r=>r.action==='message').at(-1)")
        assert 'user' not in request and 'history' not in request and 'token' not in request
        assert request['request_id'] and request['conversation_id']
        assert page.locator('#vettech-chat-payload').input_value()==''
        question.fill('<script>alert(1)</script>')
        page.get_by_role('button',name='Enviar mensagem',exact=True).click()
        expect(chat).to_contain_text('Resposta de teste: <script>alert(1)</script>')
        assert chat.locator('script').count()==0
        for _ in range(14):
            page.keyboard.press('Tab')
            assert page.evaluate("document.querySelector('dialog').contains(document.activeElement)")
        page.evaluate("chatProbe.mode='error'")
        page.get_by_role('button',name='Ver vacinas',exact=True).click()
        expect(chat).to_contain_text('Não consegui responder agora. Tente novamente.')
        page.evaluate("chatProbe.mode='success'")
        page.get_by_role('button',name='Tentar de novo',exact=True).click()
        expect(chat).to_contain_text('Resposta de teste: Ver vacinas')
        assert chat.locator('.is-user').filter(has_text='Ver vacinas').count()==1
        page.screenshot(path=str(evidence/'n8n-desktop-mock.png'))
        assert 'payload=' not in page.url
        page.keyboard.press('Escape');expect(chat).not_to_be_visible();expect(mascot).to_be_focused()
        mascot.click();expect(chat).not_to_contain_text('Qual é a função do prontuário?')
        opens=page.evaluate("chatProbe.requests.filter(r=>r.action==='open')")
        assert opens[-1]['conversation_id'] != opens[-2]['conversation_id']
        page.get_by_role('button',name='Histórico de conversas',exact=True).click()
        chat.locator('summary').first.click()
        expect(chat).to_contain_text('Resposta de teste: Qual é a função do prontuário?')
        page.get_by_role('button',name='Voltar à conversa',exact=True).click()
        page.evaluate("""() => { const e=document.getElementById('vettech-chat-session'); e.dataset.chatKey='tutor:fixture';e.dataset.chatName='Ana <Silva>'; }""")
        expect(chat).to_contain_text('Olá, Ana <Silva>!')
        page.get_by_role('button',name='Histórico de conversas',exact=True).click()
        expect(chat).to_contain_text('Nenhuma conversa anterior nesta sessão.')
        page.get_by_role('button',name='Voltar à conversa',exact=True).click()
        page.evaluate("chatProbe.mode='hold'")
        page.get_by_role('button',name='Agendar consulta',exact=True).click()
        expect(question).to_be_disabled()
        page.get_by_role('button',name='Minimizar chat').click();expect(chat).not_to_be_visible()
        mascot.click()
        page.evaluate("chatProbe.held.forEach(detail=>window.dispatchEvent(new CustomEvent('vettech:chat-response',{detail})))")
        expect(chat).not_to_contain_text('Resposta de teste: Agendar consulta')
        page.evaluate("""() => {const e=document.getElementById('vettech-chat-session'); e.dataset.chatKey='';e.dataset.chatName='';}""")
        expect(chat).to_contain_text('Olá! Eu sou o assistente')
        expect(chat).not_to_contain_text('Ana <Silva>')
        page.get_by_role('button',name='Fechar chat').click();mascot.click();page.mouse.click(20,20)
        expect(chat).not_to_be_visible()
        page.set_viewport_size({'width':390,'height':844});mascot.click()
        chat.evaluate('el => Promise.all(el.getAnimations().map(a => a.finished))')
        assert chat.bounding_box()=={'x':0,'y':0,'width':390,'height':844}
        page.screenshot(path=str(evidence/'n8n-mobile-mock.png'))
        page.get_by_role('button',name='Voltar para a página').click();expect(chat).not_to_be_visible()
        page.emulate_media(reduced_motion='reduce');page.set_viewport_size({'width':1366,'height':650});mascot.click()
        assert chat.bounding_box()['y']>=0
        browser.close()
        print('PASS: UI com transporte simulado; UUIDs, respostas, erro/retry, texto seguro, histórico, sessão, atrasadas, foco, desktop/mobile e pose.')


if __name__=='__main__':main()
