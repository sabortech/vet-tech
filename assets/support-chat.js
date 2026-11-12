/* Chat UI: messages travel through the Reflex bridge; credentials stay on the server. */
(() => {
  'use strict';
  if (window.__vetTechChat) return;
  window.__vetTechChat = true;
  // Never allow the bridge to navigate or put message text in a URL before hydration.
  document.addEventListener('submit', e => {
    if (e.target.id === 'vettech-chat-bridge') e.preventDefault();
  }, true);
  function session() {
    const el = document.getElementById('vettech-chat-session');
    return {key: el?.dataset.chatKey || '', name: el?.dataset.chatName?.trim() || ''};
  }
  function welcome() {
    const user = session();
    return `${user.key && user.name ? `Olá, ${user.name}!` : 'Olá!'} Eu sou o assistente do Vet Tech. Como posso ajudar você a usar o sistema hoje?`;
  }
  const paths = {
    history: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    send: '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
    close: '<path d="m6 6 12 12M6 18 18 6"/>',
    minus: '<path d="M5 12h14"/>',
    back: '<path d="m12 5-7 7 7 7M5 12h14"/>',
    paw: '<g transform="translate(0 1) scale(.78)"><ellipse cx="5" cy="9" rx="2" ry="2.6"/><ellipse cx="10" cy="5" rx="2" ry="2.6"/><ellipse cx="16" cy="5" rx="2" ry="2.6"/><ellipse cx="21" cy="9" rx="2" ry="2.6"/><path d="M8 14c2-4 8-4 10 0l2 4c1 3-2 5-5 3a4 4 0 0 0-4 0c-3 2-6 0-5-3Z"/></g><path d="M20 15v7m-3.5-3.5h7"/>',
    vaccine: '<path d="m18 2 4 4m-2-2-3 3m-3-3 6 6M15 5 4 16v4h4L19 9M4 20l-2 2M9 11l3 3m0-6 3 3"/>',
    calendar: '<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M7 3v4m10-4v4M3 11h18"/>',
    clinic: '<path d="M21 11a9 9 0 0 1-9 9 10 10 0 0 1-4-1l-5 2 2-5a9 9 0 1 1 16-5Z"/>'
  };
  function node(tag, cls, text) {
    const el = document.createElement(tag);
    if (cls) el.className = cls;
    if (text) el.textContent = text;
    return el;
  }
  function icon(name) {
    const box = node('span', 'vt-chat-icon');
    // Static, application-owned SVG only. Never insert user text as HTML.
    box.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name]}</svg>`;
    return box;
  }
  function avatar() {
    const frame = node('span', 'vt-chat-avatar');
    const img = node('img');
    img.src = '/mascote/chat-avatar.png'; img.alt = '';
    frame.append(img); return frame;
  }
  function button(label, name, cls) {
    const b = node('button', cls); b.type = 'button'; b.setAttribute('aria-label', label); b.title = label; b.append(icon(name)); return b;
  }
  let dialog, log, input, submit, footer, historyView, historyButton, bannerVideo, shade;
  let updateLedPath = () => {};
  let pending = false, lastQuestion = '', errorRow, responseTimer, generation = 0;
  let conversation = [], history = [], sessionKey = session().key;
  let conversationId = '', activeRequest = null;
  let supportPending = null, humanTicket = null, supportTimer, supportPanel, supportStatus;
  let supportRetry = null, offeredHandoff = false;
  let renderedSupportVersion = '';
  let supportListVisible = false;
  let supportRetryAt = 0;
  const seenSupportEvents = new Set();
  const supportNotices = new Map();
  function supportMode(mode) {
    if(!dialog)return;
    bannerVideo.parentElement.style.display=mode?'none':'';
    dialog.querySelector('.vt-chat-chips').style.display=mode?'none':'';
    supportPanel.style.flex=mode==='list'?'1':'0 1 auto';
    supportPanel.style.minHeight='0';
    supportPanel.style.maxHeight=mode==='list'?'none':'25vh';
    log.hidden=mode==='list';footer.hidden=mode==='list';
    footer.querySelector('.vt-chat-notice').textContent=mode?'Atendimento por texto. Acesso ao prontuário depende de autorização.':'Sou um assistente do sistema, não substituo o veterinário.';
    if(mode)bannerVideo.pause();else if(dialog.open)bannerVideo.play().catch(()=>{});
    requestAnimationFrame(updateLedPath);
  }
  function supportAction(action, fields = {}, retry = null) {
    if (!session().key) {supportStatus.textContent='Entre como tutor ou veterinário para acessar atendimentos.';return;}
    if (supportPending) return;
    const requestId = crypto.randomUUID();
    const operationId = retry?.operation_id || crypto.randomUUID();
    const payload = {request_id:requestId, operation_id:operationId, ...fields};
    supportPending = {requestId, action, fields:{...fields}, operation_id:operationId};
    if(humanTicket){submit.disabled=true;if(action==='send'){input.disabled=true;input.value='';}}
    if (supportStatus && action !== 'get') supportStatus.textContent = 'Carregando atendimento…';
    clearTimeout(supportTimer);
    supportTimer = setTimeout(() => supportFailure('Não foi possível confirmar a operação. Tente novamente.'), 30000);
    try { bridge('support_' + action, payload); }
    catch (_) { supportFailure('Não foi possível conectar. Tente novamente.'); }
  }
  function supportFailure(text) {
    clearTimeout(supportTimer);
    supportRetry = supportPending; supportPending = null;
    supportRetryAt=Date.now()+15000;
    if(humanTicket?.status==='em_atendimento'){
      submit.disabled=false;input.disabled=false;
      if(supportRetry?.action==='send'&&!input.value)input.value=supportRetry.fields.message;
    }
    supportStatus.replaceChildren(node('span','',text));
    if (supportRetry) {
      const retry=node('button','vt-chat-chip','Tentar atendimento novamente'); retry.type='button';
      retry.onclick=()=>{const old=supportRetry; supportAction(old.action,old.fields,old);};
      supportStatus.append(retry);
    }
  }
  function supportButton(label, action) {
    const b=node('button','vt-chat-chip',label); b.type='button'; b.onclick=action; return b;
  }
  function offerHandoff() {
    offeredHandoff=true;
    supportPanel.replaceChildren(node('p','','O assistente recomenda atendimento veterinário. Selecione o pet e confirme o compartilhamento desta conversa. Isso não libera o prontuário.'));
    supportAction('list');
  }
  function handoffForm(pets) {
    if(!offeredHandoff) return;
    const box=node('section');
    box.append(node('p','','O assistente recomenda atendimento veterinário. Confirme o pet e o compartilhamento desta conversa. Isso não libera o prontuário.'));
    const select=node('select'); select.setAttribute('aria-label','Pet do atendimento');
    const placeholder=node('option','','Selecione o pet');placeholder.value='';placeholder.disabled=true;placeholder.selected=true;select.append(placeholder);
    for(const pet of pets||[]) { const option=node('option','',pet.name); option.value=pet.id; select.append(option); }
    const label=node('label'); const consent=node('input'); consent.type='checkbox';
    label.append(consent,document.createTextNode('Autorizo compartilhar esta conversa com o veterinário que assumir.'));
    box.append(select,label,supportButton('Confirmar encaminhamento',()=>{
      if(!consent.checked||!select.value) {supportStatus.textContent='Escolha seu pet e confirme o compartilhamento.';return;}
      supportAction('create',{pet_id:Number(select.value),consent:true});
    }),supportButton('Continuar com o assistente',()=>{
      offeredHandoff=false;supportListVisible=false;supportPanel.replaceChildren();
      supportMode(false);showConversation();input.disabled=false;submit.disabled=false;
    }));
    if(!pets?.length)box.append(node('p','','Cadastre um pet antes de solicitar atendimento.'));
    supportPanel.append(box);
  }
  function renderTicket(ticket) {
    supportListVisible=false;
    const version=JSON.stringify(ticket);
    if(humanTicket?.id===ticket.id && renderedSupportVersion===version){
      const vet=ticket.veterinarian;
      supportStatus.textContent=`${ticket.pet.name} · ${ticket.status}${vet?' · '+vet.name+' · CRMV '+vet.crmv+'/'+vet.uf:''}`;
      input.disabled=ticket.status!=='em_atendimento';submit.disabled=input.disabled;
      return;
    }
    const previousId=humanTicket?.id, draft=input.value;
    const reasonDraft=supportPanel.querySelector('input')?.value||'';
    humanTicket=ticket;renderedSupportVersion=version;offeredHandoff=false;
    supportMode('ticket');
    if(previousId!==ticket.id)cancelResponse();
    historyView.hidden=true;log.hidden=false;footer.hidden=false;log.replaceChildren();
    if(previousId===ticket.id)input.value=draft;
    const vet=ticket.veterinarian;
    supportStatus.textContent=`${ticket.pet.name} · ${ticket.status}${vet?' · '+vet.name+' · CRMV '+vet.crmv+'/'+vet.uf:''}`;
    supportPanel.replaceChildren(supportButton('Meus atendimentos / fila',()=>supportAction('list')));
    for(const row of ticket.context||[])message(`${row.role==='assistant'?'Assistente':'Tutor'}: ${row.content}`,false,false);
    for(const row of ticket.messages||[])message(`${row.author_profile==='tutor'?'Tutor':'Veterinário'}: ${row.text}`,row.author_profile===session().key.split(':')[0],false,row.at);
    for(const event of ticket.events||[]) {
      const key=ticket.id+':'+event.id;
      seenSupportEvents.add(key);
      supportNotices.delete(key);
      if(event.action==='claim')message('Veterinário assumiu o atendimento.',false,false,event.at);
      if(event.action==='close')message('Atendimento encerrado: '+event.reason,false,false,event.at);
    }
    input.disabled=ticket.status!=='em_atendimento'; submit.disabled=input.disabled;
    if(ticket.status!=='encerrado' && !supportPanel.querySelector('input')) {
      const reason=node('input');reason.placeholder='Motivo do encerramento / orientação final';reason.maxLength=1000;
      reason.value=previousId===ticket.id?reasonDraft:'';
      reason.setAttribute('aria-label','Motivo do encerramento');
      supportPanel.append(reason,supportButton(ticket.status==='aguardando'?'Cancelar chamado':'Encerrar atendimento',()=>{
        if(!reason.value.trim()){supportStatus.textContent='Informe o motivo ou orientação final.';return;}
        supportAction('close',{ticket_id:ticket.id,reason:reason.value,expected_status:ticket.status});
      }));
    }
  }
  window.addEventListener('vettech:support-response', event=>{
    const data=event.detail||{};
    if(!dialog?.open||!supportPending||data.request_id!==supportPending.requestId||data.conversation_id!==conversationId)return;
    clearTimeout(supportTimer);
    if(!data.ok){supportFailure(data.error||'Não foi possível concluir o atendimento.');return;}
    supportPending=null;supportRetry=null;
    if(data.ticket)renderTicket(data.ticket);
    else if(data.tickets){
      supportListVisible=true;
      supportMode('list');
      humanTicket=null;input.disabled=true;submit.disabled=true;
      supportStatus.textContent='Atendimentos';supportPanel.replaceChildren();
      supportPanel.append(supportButton('Atualizar atendimentos',()=>supportAction('list')),supportButton('Voltar ao assistente',resetConversation));
      for(const t of data.tickets) {
        supportPanel.append(supportButton(`#${t.id} · ${t.status}${t.own?' · Meu atendimento':''}`,()=>supportAction(t.own?'get':'claim',{ticket_id:t.id})));
        for(const e of t.events||[]) {
          const key=t.id+':'+e.id;
          if(!seenSupportEvents.has(key)) {
            seenSupportEvents.add(key);
            if(e.action==='send'&&e.actor_profile===session().key.split(':')[0])continue;
            supportNotices.set(key,{ticket:t.id,text:`Atendimento #${t.id}: ${e.action==='send'?'Nova mensagem':e.action==='claim'?'Veterinário assumiu':e.action==='close'?'Encerrado':'Criado'}`});
          }
        }
        for(const notice of supportNotices.values())if(notice.ticket===t.id)supportPanel.append(node('p','',notice.text));
      }
      if(!data.tickets.length)supportPanel.append(node('p','','Nenhum atendimento disponível.'));
      handoffForm(data.pets);
    }
  });
  setInterval(()=>{
    if(dialog?.open&&!supportPending&&supportRetry&&['get','list'].includes(supportRetry.action)&&Date.now()>=supportRetryAt){
      supportAction(supportRetry.action,supportRetry.fields);return;
    }
    if(dialog?.open&&humanTicket&&!supportPending&&!supportRetry) supportAction('get',{ticket_id:humanTicket.id});
    else if(dialog?.open&&supportListVisible&&!offeredHandoff&&!supportPending&&!supportRetry) supportAction('list');
  },10000);
  const genericError = 'Não consegui responder agora. Tente novamente.';
  let transportReady = Boolean(window.__vetTechChatReady), bridgeQueue = [];
  function submitBridge(data) {
    const form = document.getElementById('vettech-chat-bridge');
    const payload = document.getElementById('vettech-chat-payload');
    if (!form || !payload) throw new Error('Chat transport unavailable');
    payload.value = JSON.stringify(data);
    form.requestSubmit();
    payload.value = '';
  }
  function bridge(action, fields = {}) {
    const data = {action, conversation_id:conversationId, session_key:session().key, ...fields};
    if (action === 'open' || action === 'close') bridgeQueue = [];
    if (transportReady) submitBridge(data);
    else bridgeQueue.push(data);
  }
  window.addEventListener('vettech:chat-ready', () => {
    transportReady = true;
    const queued = bridgeQueue; bridgeQueue = [];
    for (const data of queued) submitBridge(data);
  });
  function cancelResponse() {
    clearTimeout(responseTimer); generation++; activeRequest = null;
    pending = false; lastQuestion = ''; errorRow = null;
    if (input) { input.disabled = false; input.value = ''; submit.disabled = false; }
  }
  function showConversation() {
    historyView.hidden = true; historyView.replaceChildren(); log.hidden = false; footer.hidden = false;
    historyButton.setAttribute('aria-expanded', 'false');
    input.focus();
  }
  function resetConversation() {
    supportMode(false);
    supportListVisible=false;
    renderedSupportVersion='';
    clearTimeout(supportTimer);supportPending=null;supportRetry=null;humanTicket=null;offeredHandoff=false;
    supportPanel?.replaceChildren();if(supportStatus)supportStatus.textContent='';
    cancelResponse(); conversation = []; log.replaceChildren();
    conversationId = crypto.randomUUID();
    showConversation(); message(welcome());
    try { bridge('open'); } catch (_) { /* First send displays a recoverable error. */ }
  }
  function showHistory() {
    historyView.replaceChildren();
    const back = node('button', 'vt-chat-retry', 'Voltar à conversa');
    back.type = 'button'; back.onclick = showConversation;
    historyView.append(back, node('h3', '', 'Histórico de conversas'));
    if (!history.length) historyView.append(node('p', '', 'Nenhuma conversa anterior nesta sessão.'));
    for (const entry of [...history].reverse()) {
      const details = node('details', 'vt-chat-history-entry');
      details.append(node('summary', '', `${entry.date} · ${entry.title}`));
      for (const item of entry.messages) {
        const row = node('p', 'vt-chat-history-message');
        row.append(node('strong', '', item.user ? 'Você: ' : 'Assistente: '), document.createTextNode(item.text));
        details.append(row);
      }
      historyView.append(details);
    }
    log.hidden = true; footer.hidden = true; historyView.hidden = false;
    historyButton.setAttribute('aria-expanded', 'true'); back.focus();
  }
  function message(text, user = false, record = true, at = null) {
    if (record) conversation.push({text, user});
    const row = node('div', `vt-chat-row${user ? ' is-user' : ''}`);
    if (!user) row.append(avatar());
    const bubble = node('div', 'vt-chat-bubble');
    bubble.append(node('p', '', text));
    const time = node('div', 'vt-chat-time', new Intl.DateTimeFormat('pt-BR', {hour:'2-digit',minute:'2-digit'}).format(at ? new Date(at) : new Date()));
    if (user) time.append(node('span', 'vt-chat-check', humanTicket ? ' ✓' : ' ✓✓'));
    bubble.append(time); row.append(bubble); log.append(row); log.scrollTop = log.scrollHeight;
    return row;
  }
  function finishResponse(result) {
    const current = activeRequest;
    if (!current || !dialog.open || current.generation !== generation
        || result.request_id !== current.requestId || result.conversation_id !== conversationId) return;
    clearTimeout(responseTimer); current.typing.remove(); activeRequest = null;
    const reply = typeof result.reply === 'string' && result.reply.trim() ? result.reply : genericError;
    if (result.ok === true) {
      message(reply);
      if(result.handoff&&session().key.startsWith('tutor:'))offerHandoff();
    } else {
      errorRow = message(reply, false, false);
      if (result.error?.code !== 'SESSION_INVALID') {
        const row = errorRow;
        const retry = node('button', 'vt-chat-retry', 'Tentar de novo'); retry.type='button';
        retry.onclick = () => { row.remove(); respond(current.question); };
        row.querySelector('.vt-chat-bubble').append(retry);
      }
    }
    pending = false; submit.disabled = false; input.disabled = false;
    if (historyView.hidden) input.focus();
  }
  window.addEventListener('vettech:chat-response', event => finishResponse(event.detail || {}));
  function respond(question) {
    if (pending) return;
    pending = true; submit.disabled = true; input.disabled = true;
    const typing = message('', false, false); typing.classList.add('vt-chat-typing');
    const dots = node('span', 'vt-chat-dots'); dots.setAttribute('aria-label', 'Assistente digitando');
    for (let i=0; i<3; i++) dots.append(node('i'));
    typing.querySelector('p').append(dots);
    const requestId = crypto.randomUUID();
    activeRequest = {requestId, generation, question, typing};
    const failed = {request_id:requestId, conversation_id:conversationId, ok:false, reply:genericError};
    responseTimer = setTimeout(() => finishResponse(failed), 65000);
    try { bridge('message', {request_id:requestId, message:question}); }
    catch (_) { finishResponse(failed); }
  }
  function send(text) {
    const clean = text.trim().slice(0,1000);
    if (!clean || pending) return;
    if(humanTicket){
      if(humanTicket.status==='em_atendimento'&&!supportPending){
        const retry=supportRetry?.action==='send'&&supportRetry.fields.message===clean&&supportRetry.fields.ticket_id===humanTicket.id?supportRetry:null;
        supportAction('send',{ticket_id:humanTicket.id,message:clean},retry);input.value='';
      }
      return;
    }
    lastQuestion = clean; message(clean, true); input.value = ''; respond(clean);
  }
  function close() {
    if (!dialog?.open || dialog.classList.contains('is-closing')) return;
    cancelResponse();
    bannerVideo.pause();
    dialog.classList.add('is-closing');
    shade.classList.remove('is-visible');
    const delay = matchMedia('(prefers-reduced-motion:reduce)').matches ? 0 : 200;
    setTimeout(() => { dialog.close(); dialog.classList.remove('is-closing'); }, delay);
  }
  function build() {
    shade = node('div', 'vt-chat-shade');
    shade.setAttribute('aria-hidden', 'true');
    shade.onclick = close;
    (document.getElementById('vettech-mascote')?.parentElement || document.body).append(shade);
    dialog = node('dialog', 'vt-chat'); dialog.id = 'vettech-support-chat';
    dialog.setAttribute('aria-labelledby', 'vt-chat-title');
    const svgNS = 'http://www.w3.org/2000/svg';
    const led = document.createElementNS(svgNS, 'svg');
    led.setAttribute('class', 'vt-chat-led');
    led.setAttribute('aria-hidden', 'true');
    led.setAttribute('focusable', 'false');
    const track = document.createElementNS(svgNS, 'path');
    track.setAttribute('class', 'vt-chat-led-track');
    track.setAttribute('stroke-linejoin', 'round');
    track.setAttribute('pathLength', '100');
    led.append(track);
    const head = node('header', 'vt-chat-header');
    const back = button('Voltar para a página', 'back', 'vt-chat-control vt-chat-back'); back.onclick = close;
    const title = node('div', 'vt-chat-heading');
    const name = node('h2', '', 'Assistente Vet Tech'); name.id = 'vt-chat-title';
    title.append(name, node('span', 'vt-chat-status', 'Ajuda do sistema'));
    const minimize = button('Minimizar chat', 'minus', 'vt-chat-control'); minimize.onclick = close;
    const dismiss = button('Fechar chat', 'close', 'vt-chat-control'); dismiss.onclick = close;
    historyButton = button('Histórico de conversas', 'history', 'vt-chat-control');
    historyButton.setAttribute('aria-expanded', 'false');
    historyButton.onclick = () => historyView.hidden ? showHistory() : showConversation();
    const supportEntry=supportButton('Atendimentos',()=>supportAction('list'));
    head.append(supportEntry);
    head.append(back, avatar(), title, historyButton, minimize, dismiss);
    const banner = node('div', 'vt-chat-banner');
    bannerVideo = node('video', 'vt-chat-banner-video');
    bannerVideo.muted = true; bannerVideo.defaultMuted = true;
    bannerVideo.autoplay = true; bannerVideo.loop = true; bannerVideo.playsInline = true;
    bannerVideo.preload = 'metadata';
    bannerVideo.setAttribute('aria-hidden', 'true');
    bannerVideo.src = '/gifturtle.mp4';
    banner.append(bannerVideo);
    log = node('div', 'vt-chat-messages'); log.setAttribute('role', 'log'); log.setAttribute('aria-live', 'polite'); log.setAttribute('aria-label', 'Conversa com o assistente');
    supportStatus=node('div','vt-chat-notice');supportStatus.setAttribute('role','status');
    supportPanel=node('section');supportPanel.setAttribute('aria-label','Atendimento veterinário');
    supportPanel.style.maxHeight='35vh';supportPanel.style.overflowY='auto';
    const chips = node('div', 'vt-chat-chips');
    for (const [label, shape] of [['Cadastrar um pet','paw'],['Ver vacinas','vaccine'],['Agendar consulta','calendar'],['Falar com a clínica','clinic']]) {
      const chip = node('button', 'vt-chat-chip'); chip.type='button'; chip.append(icon(shape),node('span','',label)); chip.onclick=()=>send(label); chips.append(chip);
    }
    const foot = node('footer','vt-chat-footer'); footer = foot;
    historyView = node('section', 'vt-chat-history'); historyView.hidden = true; historyView.setAttribute('aria-label', 'Histórico de conversas');
    const form = node('form', 'vt-chat-form');
    input = node('input'); input.type='text'; input.placeholder='Digite sua pergunta…'; input.maxLength=1000; input.autocomplete='off'; input.setAttribute('aria-label','Digite sua pergunta');
    submit = button('Enviar mensagem','send','vt-chat-send'); submit.type='submit';
    form.append(input,submit); form.onsubmit=e=>{e.preventDefault();send(input.value);};
    foot.append(chips,form,node('p','vt-chat-notice','Sou um assistente do sistema, não substituo o veterinário.'));
    dialog.append(led,head,banner,supportStatus,supportPanel,historyView,log,foot); document.body.append(dialog);
    // Two continuous loops share the banner divider: a rectangular figure eight.
    // Local layout coordinates avoid the scale used by the opening animation.
    updateLedPath = () => {
      const width = dialog.clientWidth, height = dialog.clientHeight;
      if (!dialog.open || width < 48 || height < 96) return;
      const left = 1.5, right = width - 1.5, top = 1.5, bottom = height - 1.5;
      const radius = Math.min(22.5, width / 4, height / 4);
      const divider = Math.max(top + radius, Math.min(bottom - radius, banner.offsetTop + banner.offsetHeight));
      track.setAttribute('d', [
        `M ${left} ${divider} H ${right} V ${top + radius}`,
        `Q ${right} ${top} ${right - radius} ${top} H ${left + radius}`,
        `Q ${left} ${top} ${left} ${top + radius} V ${divider}`,
        `H ${right} V ${bottom - radius}`,
        `Q ${right} ${bottom} ${right - radius} ${bottom} H ${left + radius}`,
        `Q ${left} ${bottom} ${left} ${bottom - radius} V ${divider} Z`,
      ].join(' '));
    };
    const ledResize = new ResizeObserver(updateLedPath);
    ledResize.observe(dialog); ledResize.observe(banner);

    dialog.addEventListener('click', e => { if (e.target === dialog) { const r=dialog.getBoundingClientRect(); if(e.clientX<r.left || e.clientX>r.right || e.clientY<r.top || e.clientY>r.bottom) close(); } });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && dialog.open) {
        e.preventDefault(); close();
      }
    });
    dialog.addEventListener('close',()=>{
      bannerVideo.pause();
      shade.classList.remove('is-visible');
      try { bridge('close'); } catch (_) { /* UI can close while disconnected. */ }
      const first = conversation.find(item => item.user);
      if (first) {
        history.push({date:new Date().toLocaleString('pt-BR', {dateStyle:'short',timeStyle:'short'}), title:first.text.slice(0,60), messages:conversation.map(item => ({...item}))});
        history = history.slice(-20);
      }
      cancelResponse(); conversation = []; log.replaceChildren(); historyView.replaceChildren();
      document.documentElement.classList.remove('vt-chat-open');
      window.dispatchEvent(new CustomEvent('vettech:chat-state', {detail:{open:false}}));
      const mascot=document.getElementById('vettech-mascote');
      if(mascot){mascot.setAttribute('aria-expanded','false');mascot.focus({preventScroll:true});}
    });

  }
  function watchSession() {
    const el = document.getElementById('vettech-chat-session');
    if (!el) return false;
    new MutationObserver(() => {
      const user = session();
      // Invalidate the previous conversation before the next authenticated request.
      try { if (conversationId) bridge('close'); } catch (_) { /* Server also guards session generation. */ }
      history = []; sessionKey = user.key;
      seenSupportEvents.clear();supportNotices.clear();clearTimeout(supportTimer);supportPending=null;humanTicket=null;supportRetry=null;
      if (dialog) { cancelResponse(); conversation = []; log.replaceChildren(); historyView.replaceChildren(); if (dialog.open) resetConversation(); }
    }).observe(el, {attributes:true, attributeFilter:['data-chat-key','data-chat-name']});
    return true;
  }
  if (!watchSession()) {
    const observer = new MutationObserver(() => { if(watchSession()) observer.disconnect(); });
    observer.observe(document.documentElement, {childList:true,subtree:true});
  }
  window.addEventListener('vettech:mascote-click',()=>{
    if(!dialog) build();
    if(dialog.open) { close(); return; }
    if (sessionKey !== session().key) { history = []; sessionKey = session().key; }
    resetConversation();
    const mascot=document.getElementById('vettech-mascote');
    if(mascot){mascot.setAttribute('aria-controls','vettech-support-chat');mascot.setAttribute('aria-expanded','true');}
    document.documentElement.classList.add('vt-chat-open');
    shade.classList.add('is-visible');
    dialog.show();
    updateLedPath();
    bannerVideo.play().catch(() => { /* Browser autoplay policy may defer playback. */ });
    window.dispatchEvent(new CustomEvent('vettech:chat-state', {detail:{open:true}}));
    input.focus();
  });
})();
