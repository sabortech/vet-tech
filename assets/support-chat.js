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
  let pending = false, lastQuestion = '', errorRow, responseTimer, generation = 0;
  let conversation = [], history = [], sessionKey = session().key;
  let conversationId = '', activeRequest = null;
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
  function message(text, user = false, record = true) {
    if (record) conversation.push({text, user});
    const row = node('div', `vt-chat-row${user ? ' is-user' : ''}`);
    if (!user) row.append(avatar());
    const bubble = node('div', 'vt-chat-bubble');
    bubble.append(node('p', '', text));
    const time = node('div', 'vt-chat-time', new Intl.DateTimeFormat('pt-BR', {hour:'2-digit',minute:'2-digit'}).format(new Date()));
    if (user) time.append(node('span', 'vt-chat-check', ' ✓✓'));
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
    const track = document.createElementNS(svgNS, 'rect');
    track.setAttribute('class', 'vt-chat-led-track');
    track.setAttribute('x', '1.5'); track.setAttribute('y', '1.5');
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
    dialog.append(led,head,banner,historyView,log,foot); document.body.append(dialog);
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
    bannerVideo.play().catch(() => { /* Browser autoplay policy may defer playback. */ });
    window.dispatchEvent(new CustomEvent('vettech:chat-state', {detail:{open:true}}));
    input.focus();
  });
})();
