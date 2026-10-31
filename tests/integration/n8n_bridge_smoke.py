"""Smoke da ponte real. Pode acionar o n8n se o backend tiver credenciais.

Não exige login; envia apenas uma pergunta genérica. Não imprime respostas ou IDs.
"""
import argparse
from playwright.sync_api import sync_playwright, expect


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--url',default='http://localhost:3000')
    parser.add_argument('--chromium',default=None)
    args=parser.parse_args()
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=args.chromium)
        page=browser.new_page(viewport={'width':1366,'height':900})
        page.add_init_script("window.bridgeResponses=[];window.addEventListener('vettech:chat-response',e=>bridgeResponses.push({ok:e.detail.ok,request_id:e.detail.request_id,conversation_id:e.detail.conversation_id}));")
        page.goto(args.url+'/login',wait_until='domcontentloaded')
        page.wait_for_function("document.getElementById('vettech-mascote')?.classList.contains('assets-ready') && window.__vetTechChat")
        page.locator('#vettech-mascote').click()
        page.get_by_role('textbox',name='Digite sua pergunta').fill('Olá! Como uso o Vet Tech?')
        page.get_by_role('button',name='Enviar mensagem',exact=True).click()
        page.wait_for_function('bridgeResponses.length > 0',timeout=65000)
        expect(page.get_by_role('textbox',name='Digite sua pergunta')).to_be_enabled()
        assert page.locator('#vettech-chat-payload').input_value()==''
        print('Ponte real navegador -> Reflex -> cliente n8n -> navegador: OK')
        print('Resposta de sucesso do workflow:',page.evaluate('bridgeResponses[0].ok === true'))
        browser.close()


if __name__=='__main__':main()
