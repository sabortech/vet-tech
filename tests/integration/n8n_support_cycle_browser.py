"""Ciclo real n8n/Xano, com perda deliberada de confirmação e retry, usando fixtures existentes."""
import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--run', required=True)
parser.add_argument('--development', action='store_true', required=True)
parser.add_argument('--url', default='http://localhost:3003')
parser.add_argument('--chromium', default='C:/Program Files/Google/Chrome/Application/chrome.exe')
args = parser.parse_args()
root = Path('.venv/clinical-smoke').resolve()
folder = (root / args.run).resolve()
if not folder.is_relative_to(root):
    raise SystemExit('Ledger fora da pasta privada')
ledger_path = folder / 'ledger.json'
data = json.loads(ledger_path.read_text(encoding='utf-8'))
checks = []
expect.set_options(timeout=65000)


def check(name):
    checks.append({'check': name, 'passed': True})
    (folder / 'n8n-support-cycle-results.json').write_text(json.dumps(checks, indent=2), encoding='utf-8')
    print('PASS', name, flush=True)


PROBE = """window.probe={bot:[],support:[],sent:[]};
document.addEventListener('submit',e=>{if(e.target.id==='vettech-chat-bridge'){
  const d=JSON.parse(document.getElementById('vettech-chat-payload').value);
  probe.sent.push({action:d.action,operation_id:d.operation_id});
}},true);
window.addEventListener('vettech:chat-response',e=>probe.bot.push(e.detail));
const originalDispatch=window.dispatchEvent.bind(window);
window.dispatchEvent=e=>{
  if(e.type==='vettech:support-response' && e.detail.action==='send' && e.detail.ok && window.dropNextSend){
    window.dropNextSend=false;window.droppedSend=true;return true;
  }
  return originalDispatch(e);
};
window.addEventListener('vettech:support-response',e=>probe.support.push({
  action:e.detail.action,ok:e.detail.ok,ticketId:e.detail.ticket?.id,status:e.detail.ticket?.status
}));"""


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=args.chromium)
    tutor, vet, rival = [browser.new_page() for _ in range(3)]

    def login(page, actor):
        page.set_default_timeout(65000)
        page.add_init_script(PROBE)
        page.goto(args.url + '/login')
        page.wait_for_function('window.__vetTechChatReady === true')
        page.get_by_label('E-mail', exact=True).fill(data['actors'][actor]['email'])
        page.get_by_label('Senha', exact=True).fill(data['actors'][actor]['password'])
        for attempt in range(3):
            page.get_by_role('button', name='Login', exact=True).click()
            try:
                page.wait_for_function("document.getElementById('vettech-chat-session')?.dataset.chatKey", timeout=15000)
                return
            except Exception:
                if attempt < 2 and 'limitou temporariamente' in page.locator('body').inner_text():
                    page.wait_for_timeout(20000)
                else:
                    raise

    def open_chat(page):
        page.locator('#vettech-mascote').click()
        page.get_by_role('dialog', name='Assistente Vet Tech').evaluate('el=>Promise.all(el.getAnimations().map(a=>a.finished))')

    for page, actor in ((tutor, 'ta'), (vet, 'va'), (rival, 'vb')):
        login(page, actor)
        print('login_ready_' + actor, flush=True)
    open_chat(tutor)
    question = 'Quero falar com um veterinário humano sobre meu pet. Pode propor o atendimento pelo chat?'
    tutor.get_by_role('textbox', name='Digite sua pergunta').fill(question)
    tutor.get_by_role('button', name='Enviar mensagem', exact=True).click()
    for attempt in range(3):
        tutor.wait_for_function('probe.bot.length > 0', timeout=70000)
        outcome = tutor.evaluate('({ok:probe.bot.at(-1).ok,code:probe.bot.at(-1).error?.code})')
        if outcome['ok']:
            break
        if attempt == 2 or outcome.get('code') not in ('XANO_UNAVAILABLE', 'AI_UNAVAILABLE'):
            raise RuntimeError('Resposta real do bot sem sucesso: ' + str(outcome))
        print('manual_bot_retry_after_' + outcome['code'], flush=True)
        tutor.wait_for_timeout(20000)
        tutor.evaluate('probe.bot=[]')
        tutor.get_by_role('button', name='Tentar de novo', exact=True).click()
    expect(tutor.get_by_role('combobox', name='Pet do atendimento')).to_be_visible(timeout=90000)
    assert tutor.evaluate('probe.bot.some(r=>r.ok && r.handoff)')
    tutor.get_by_role('button', name='Confirmar encaminhamento', exact=True).click()
    assert tutor.evaluate("probe.sent.filter(r=>r.action==='support_create').length") == 0
    tutor.get_by_role('combobox', name='Pet do atendimento').select_option(str(data['pets']['a']))
    tutor.get_by_role('checkbox').check()
    tutor.get_by_role('button', name='Confirmar encaminhamento', exact=True).click()
    tutor.wait_for_function("probe.support.some(r=>r.action==='create' && r.ok)")
    tid = tutor.evaluate("probe.support.find(r=>r.action==='create' && r.ok).ticketId")
    data.setdefault('support_tickets', []).append(tid)
    ledger_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
    check('real_n8n_handoff_requires_pet_and_consent')
    bot_requests = tutor.evaluate("probe.sent.filter(r=>r.action==='message').length")
    tutor.evaluate("window.dispatchEvent(new CustomEvent('vettech:chat-response',{detail:probe.bot[0]}))")
    expect(tutor.get_by_role('combobox', name='Pet do atendimento')).not_to_be_visible()
    check('late_real_bot_response_replay_ignored_after_creation')

    for page in (vet, rival):
        open_chat(page)
        page.get_by_role('button', name='Atendimentos', exact=True).click()
        page.get_by_role('button', name=f'#{tid} · aguardando', exact=True).wait_for()
        expect(page.get_by_text('Tutor: ' + question, exact=True)).not_to_be_visible()
    for page in (vet, rival):
        page.get_by_role('button', name=f'#{tid} · aguardando', exact=True).evaluate('el=>el.click()')
    for page in (vet, rival):
        page.wait_for_function("probe.support.some(r=>r.action==='claim')")
    outcomes = [page.evaluate("probe.support.find(r=>r.action==='claim').ok") for page in (vet, rival)]
    assert sum(outcomes) == 1
    if not outcomes[0]:
        vet, rival = rival, vet
    expect(vet.get_by_text('Tutor: ' + question, exact=True)).to_be_visible()
    expect(rival.get_by_text('Tutor: ' + question, exact=True)).not_to_be_visible()
    check('concurrent_claim_two_real_veterinarians_one_participant')

    expect(tutor.get_by_role('textbox', name='Digite sua pergunta')).to_be_enabled()
    print('tutor_ready_for_real_send', flush=True)
    tutor.evaluate('window.dropNextSend=true')
    tutor.get_by_role('textbox', name='Digite sua pergunta').fill('Mensagem sintética da interface')
    tutor.get_by_role('button', name='Enviar mensagem', exact=True).click()
    for attempt in range(4):
        try:
            tutor.wait_for_function("window.droppedSend === true || probe.support.some(r=>r.action==='send' && !r.ok)", timeout=35000)
        except Exception:
            print('send_diagnostic', tutor.evaluate("({sent:probe.sent.map(r=>r.action),responses:probe.support.map(r=>({action:r.action,ok:r.ok})),disabled:document.querySelector('.vt-chat-input')?.disabled})"), flush=True)
            raise
        if tutor.evaluate('window.droppedSend === true'):
            break
        if attempt == 3:
            raise RuntimeError('Serviço não confirmou mensagem após tentativas manuais')
        print('manual_support_retry_after_service_failure', flush=True)
        tutor.wait_for_timeout(15000)
        tutor.evaluate("probe.support=probe.support.filter(r=>r.action!=='send')")
        tutor.get_by_role('button', name='Tentar atendimento novamente', exact=True).click()
    print('real_send_confirmation_dropped', flush=True)
    tutor.get_by_role('button', name='Tentar atendimento novamente', exact=True).click(timeout=40000)
    tutor.wait_for_function("probe.support.some(r=>r.action==='send' && r.ok)")
    sent = tutor.evaluate("probe.sent.filter(r=>r.action==='support_send')")
    assert len(sent) >= 2 and len({r['operation_id'] for r in sent}) == 1
    assert tutor.get_by_text('Tutor: Mensagem sintética da interface', exact=True).count() == 1
    expect(vet.get_by_text('Tutor: Mensagem sintética da interface', exact=True)).to_be_visible()
    check('lost_real_send_confirmation_retry_without_duplicate')
    vet.get_by_role('textbox', name='Digite sua pergunta').fill('Orientação sintética da interface')
    vet.get_by_role('button', name='Enviar mensagem', exact=True).click()
    expect(tutor.get_by_text('Veterinário: Orientação sintética da interface', exact=True)).to_be_visible()
    assert tutor.evaluate("probe.sent.filter(r=>r.action==='message').length") == bot_requests
    check('bidirectional_human_messages_without_bot_calls')
    tutor.context.set_offline(True)
    tutor.get_by_role('button', name='Fechar chat', exact=True).click()
    expect(tutor.get_by_role('dialog', name='Assistente Vet Tech')).not_to_be_visible()
    tutor.context.set_offline(False)
    tutor.reload()
    tutor.wait_for_function('window.__vetTechChatReady === true')
    tutor.wait_for_function("document.getElementById('vettech-chat-session')?.dataset.chatKey")
    open_chat(tutor)
    tutor.get_by_role('button', name='Atendimentos', exact=True).click()
    tutor.get_by_role('button', name=f'#{tid} · em_atendimento · Meu atendimento', exact=True).click()
    expect(tutor.get_by_text('Veterinário: Orientação sintética da interface', exact=True)).to_be_visible()
    check('offline_reconnect_reload_resumes_persistent_ticket')
    vet.get_by_role('textbox', name='Motivo do encerramento').fill('Verificação sintética concluída')
    vet.get_by_role('button', name='Encerrar atendimento', exact=True).click()
    expect(tutor.get_by_text('Atendimento encerrado: Verificação sintética concluída', exact=True)).to_be_visible()
    expect(tutor.get_by_role('textbox', name='Digite sua pergunta')).to_be_disabled()
    check('real_cycle_closed_read_only')
    browser.close()
