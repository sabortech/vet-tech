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
    return 'Oi! Eu sou a Turtle, mascote e assistente virtual do grupo Vet Tech! Como posso te ajudar com nosso sistema hoje?';
  }
  const paths = {
    more: '<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
    deleted: '<circle cx="12" cy="12" r="9"/><path d="m6 6 12 12"/>',
    pencil: '<path d="m16 3 5 5M4 16l12-12a2 2 0 0 1 3 0l1 1a2 2 0 0 1 0 3L8 20l-5 1Z"/>',
    trash: '<path d="M3 6h18M9 6V3h6v3M5 6l1 15h12l1-15M10 10v7m4-7v7"/>',
    check: '<path d="m4 12 5 5L20 6"/>',
    checks: '<path d="m2 12 4 4L16 6m-6 9 2 2L22 7"/>',
    emoji: '<circle cx="12" cy="12" r="9"/><path d="M8 14s1 3 4 3 4-3 4-3M8 9h.01M16 9h.01"/>',
    veterinarian: '<path d="M5 3v5a4 4 0 0 0 8 0V3M3 3h4m4 0h4M9 12v3a5 5 0 0 0 10 0v-2"/><circle cx="19" cy="10" r="3"/>',
    tutor: '<circle cx="9" cy="6" r="3"/><path d="M3 21v-3a6 6 0 0 1 10-4"/><path d="M18 16c-3-3-6 1 0 5 6-4 3-8 0-5Z"/>',
    info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7h.01"/>',
    refresh: '<path d="M20 7v5h-5M4 17v-5h5"/><path d="M6 7a7 7 0 0 1 12-1l2 6M4 12l2 6a7 7 0 0 0 12-1"/>',
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
    img.src = '/optimized/mascote_logo.webp'; img.alt = '';
    frame.append(img); return frame;
  }
  function appendChatStart(at = conversationStartedAt) {
    if(log.querySelector('.vt-chat-start-time'))return;
    const date=new Date(at||conversationStartedAt);
    const label=node('div','vt-chat-start-time',new Intl.DateTimeFormat('pt-BR',{hour:'2-digit',minute:'2-digit'}).format(Number.isNaN(date.getTime())?new Date(conversationStartedAt):date));
    label.setAttribute('aria-label','Início da conversa às '+label.textContent);log.append(label);
  }
  function participantAvatar(profile) {
    const face=node('span','vt-chat-avatar vt-chat-human-avatar');
    face.dataset.profile=profile;face.setAttribute('role','img');face.setAttribute('aria-label',profile==='veterinario'?'Veterinário':'Tutor');
    face.append(icon(profile==='veterinario'?'veterinarian':'tutor'));return face;
  }
  function updateChatIdentity(ticket = null) {
    const head=dialog.querySelector('.vt-chat-header'),current=head.querySelector('.vt-chat-avatar');
    const title=head.querySelector('h2'),status=head.querySelector('.vt-chat-status');
    if(!ticket){delete dialog.dataset.status;current.replaceWith(avatar());title.textContent='Turtle · Vet Tech';status.textContent='Ajuda do sistema';log.setAttribute('aria-label','Conversa com o assistente');return;}
    if(ticket.kind==='direct')delete dialog.dataset.status;else dialog.dataset.status=ticket.status;
    const viewer=session().key.split(':')[0],peer=viewer==='veterinario'?'tutor':'veterinario';
    current.replaceWith(participantAvatar(peer));
    const state={aguardando:'Aguardando veterinário',em_atendimento:'Em atendimento',encerrado:'Encerrado'}[ticket.status]||ticket.status;
    title.textContent=peer==='veterinario'?(ticket.veterinarian?.name||'Atendimento veterinário'):(ticket.tutor?.name||'Tutor');
    const role=peer==='veterinario'?'Veterinário':ticket.tutor&&!ticket.tutor.name?'Nome não informado':'Tutor';
    const lines=ticket.kind==='direct'?[role,'Conversa privada']:[role,'Pet: '+ticket.pet.name,state];
    status.replaceChildren(...lines.map((text,index)=>node('span',index===2?'vt-chat-ticket-state':'vt-chat-heading-detail',text)));
    log.setAttribute('aria-label',peer==='veterinario'?'Conversa com veterinário':'Conversa com tutor');
  }
  function statusLed(circular = false) {
    const ns='http://www.w3.org/2000/svg';
    const svg=document.createElementNS(ns,'svg');
    svg.setAttribute('class',`vt-chat-status-led${circular?' is-circular':''}`);
    svg.setAttribute('aria-hidden','true');svg.setAttribute('focusable','false');
    const shape=document.createElementNS(ns,circular?'circle':'rect');shape.setAttribute('pathLength','100');
    if(circular){svg.setAttribute('viewBox','0 0 100 100');shape.setAttribute('cx','50');shape.setAttribute('cy','50');shape.setAttribute('r','48');}
    else{shape.setAttribute('x','1.5');shape.setAttribute('y','1.5');shape.setAttribute('rx','15');}
    svg.append(shape);return svg;
  }
  function petAvatar(photo, label = 'Foto do pet') {
    const frame=node('span','vt-chat-pet-avatar');
    frame.setAttribute('role','img');frame.setAttribute('aria-label',label);
    const image=node('span','vt-chat-pet-image');frame.append(image,statusLed(true));
    const candidate=typeof photo==='string'?photo.trim():photo?.url;
    const safe=typeof candidate==='string'&&(/^https?:\/\//i.test(candidate)||/^data:image\/(png|jpe?g|webp|gif);base64,[a-z0-9+/=\s]+$/i.test(candidate));
    const fallback=()=>{image.replaceChildren(icon('paw'));frame.setAttribute('aria-label','Pet sem foto disponível');};
    if(!safe){fallback();return frame;}
    const img=node('img');img.alt='';img.loading='lazy';img.decoding='async';img.width=56;img.height=56;
    img.onerror=fallback;img.src=candidate;image.append(img);return frame;
  }
  function button(label, name, cls) {
    const b = node('button', cls); b.type = 'button'; b.setAttribute('aria-label', label); b.title = label; b.append(icon(name)); return b;
  }
  let dialog, log, input, submit, footer, historyView, historyButton, bannerVideo, shade;
  let emojiButton, emojiPanel;
  let messageActionDialog, messageActionBody, messageActionStatus, messageActionTarget;
  let ticketInfoButton, ticketInfoDialog, ticketDetails, ticketInfoStatus;
  let updateLedPath = () => {};
  let pending = false, lastQuestion = '', errorRow, responseTimer, generation = 0;
  let conversation = [], history = [], sessionKey = session().key;
  let conversationId = '', activeRequest = null;
  let supportPending = null, humanTicket = null, supportTimer, supportPanel, supportStatus;
  let supportRetry = null, offeredHandoff = false;
  let renderedSupportVersion = '';
  let supportListVisible = false;
  let lastSupportRead = 0;
  let readCandidate = null;
  let serverClock = null;
  let conversationStartedAt = Date.now();
  let readFlushTimer, focusRefreshTimer, focusFollowUpTimer, lastReadSync = 0, lastFocusRefresh = 0;
  function canObserveMessages() {
    return Boolean(dialog?.open&&!dialog.classList.contains('is-closing')&&humanTicket&&dialog.dataset.mode==='ticket'&&historyView.hidden&&!document.hidden&&document.hasFocus()&&!ticketInfoDialog?.open&&!directPicker?.open&&!messageActionDialog?.open&&(!emojiPanel||emojiPanel.hidden));
  }
  function collectVisibleReads() {
    if(!canObserveMessages())return;
    const messages=humanTicket.messages||[],bounds=log.getBoundingClientRect();
    let candidate=readCandidate?.ticketId===humanTicket.id?messages.findIndex(m=>m.id===readCandidate.messageId):-1;
    if(candidate>=0&&(messages[candidate].read_at||messages[candidate].deleted_at||(messages[candidate].revision||0)!==(readCandidate.revision||0))){readCandidate=null;candidate=-1;}
    for(const row of log.querySelectorAll('[data-incoming=true]')){
      const index=messages.findIndex(m=>m.id===row.dataset.messageId);
      if(index<0||messages[index].read_at||messages[index].deleted_at||index<candidate)continue;
      const rect=row.querySelector('.vt-chat-bubble').getBoundingClientRect();
      if(rect.bottom<=bounds.bottom+1&&rect.bottom>bounds.top&&rect.top<bounds.bottom){
        const changed=readCandidate?.ticketId!==humanTicket.id||readCandidate?.messageId!==messages[index].id||readCandidate?.revision!==(messages[index].revision||0);
        readCandidate={ticketId:humanTicket.id,messageId:messages[index].id,revision:messages[index].revision||0};candidate=index;
        if(changed)scheduleReadSync();
      }
    }
  }
  function scheduleReadSync(delay = 350) {
    if(readFlushTimer||!readCandidate)return;
    readFlushTimer=setTimeout(()=>{readFlushTimer=null;flushReadCandidate();},delay);
  }
  function flushReadCandidate() {
    if(!humanTicket||readCandidate?.ticketId!==humanTicket.id||!dialog?.open||messageActionDialog?.open)return;
    const message=(humanTicket.messages||[]).find(m=>m.id===readCandidate.messageId);
    if(!message||message.read_at||message.deleted_at||(message.revision||0)!==(readCandidate.revision||0)){readCandidate=null;return;}
    if(supportRetry)return;
    if(supportPending){scheduleReadSync(500);return;}
    const delay=5000-(Date.now()-lastReadSync);
    if(delay>0){scheduleReadSync(delay);return;}
    lastReadSync=Date.now();
    // This marker was collected while visible; changing tabs must not discard it.
    supportAction('get',{ticket_id:humanTicket.id,read_through:readCandidate.messageId,read_revision:readCandidate.revision||0});
  }
  function refreshOnFocus() {
    if(focusRefreshTimer)return;
    focusRefreshTimer=setTimeout(()=>{
      focusRefreshTimer=null;
      if(!canObserveMessages())return;
      collectVisibleReads();
      if(supportPending){refreshOnFocus();return;}
      if(supportRetry)return;
      const delay=Math.max(5000-(Date.now()-lastFocusRefresh),250-(Date.now()-lastSupportRead));
      if(delay>0){focusRefreshTimer=setTimeout(()=>{focusRefreshTimer=null;refreshOnFocus();},delay);return;}
      lastFocusRefresh=Date.now();supportAction('get',{ticket_id:humanTicket.id});
      clearTimeout(focusFollowUpTimer);
      focusFollowUpTimer=setTimeout(()=>{
        const profile=session().key.split(':')[0];
        if(canObserveMessages()&&!supportPending&&!supportRetry&&(humanTicket.messages||[]).some(m=>m.author_profile===profile&&!m.read_at))supportAction('get',{ticket_id:humanTicket.id});
      },5500);
    },350);
  }
  function messageWithinWindow(message) {
    const now=serverClock?serverClock.time+performance.now()-serverClock.observedAt:Date.now();
    const age=now-message.at;
    return Number.isFinite(message.at)&&age>=0&&age<=600000;
  }
  function expireMessageControls() {
    if(!humanTicket)return;
    for(const row of log.querySelectorAll('[data-message-id]')){
      const stored=(humanTicket.messages||[]).find(m=>m.id===row.dataset.messageId);
      if(!stored||messageWithinWindow(stored))continue;
      row.querySelectorAll('.vt-chat-message-menu-trigger').forEach(el=>{el.classList.add('is-expired');el.title='Prazo de 10 minutos encerrado';});
    }
    if(messageActionDialog?.open&&messageActionTarget&&!messageWithinWindow(messageActionTarget)){
      messageActionStatus.textContent='O prazo de 10 minutos para editar ou apagar esta mensagem terminou.';
      messageActionBody.querySelectorAll('button[data-time-limited],.vt-chat-confirm-delete').forEach(el=>el.disabled=true);
    }
  }
  function actionStatus() {return messageActionDialog?.open?messageActionStatus:ticketInfoDialog?.open?ticketInfoStatus:supportStatus;}
  function clearMessageActions() {
    messageActionDialog?.close();messageActionBody?.replaceChildren();if(messageActionStatus)messageActionStatus.textContent='';messageActionTarget=null;
  }
  function openMessageActions(row, action = null) {
    if(supportPending||humanTicket?.status!=='em_atendimento'||row.deleted_at||row.author_profile!==session().key.split(':')[0])return;
    closeEmojis();messageActionTarget={...row,ticket_id:humanTicket.id};if(humanTicket.kind==='direct')delete messageActionDialog.dataset.status;else messageActionDialog.dataset.status=humanTicket.status;
    messageActionStatus.textContent='';messageActionBody.replaceChildren();
    const preview=node('p','vt-chat-message-preview',row.text);
    const edit=supportButton('Editar mensagem',()=>{
      const field=node('textarea','vt-chat-message-editor');field.value=row.text;field.maxLength=1000;field.rows=4;field.setAttribute('aria-label','Editar mensagem');
      const save=supportButton('Salvar alteração',()=>{
        const text=field.value.trim();if(!text){messageActionStatus.textContent='Escreva a mensagem antes de salvar.';field.focus();return;}
        if(text===row.text){messageActionDialog.close();return;}
        supportAction('edit',{ticket_id:messageActionTarget.ticket_id,message_id:row.id,expected_revision:row.revision||0,message:text});
      });
      save.dataset.timeLimited='true';
      messageActionBody.replaceChildren(field,save,supportButton('Cancelar',()=>messageActionDialog.close()));field.focus();
    });
    const remove=supportButton('Apagar mensagem',()=>{
      const confirm=supportButton('Confirmar exclusão',()=>supportAction('delete',{ticket_id:messageActionTarget.ticket_id,message_id:row.id,expected_revision:row.revision||0}));confirm.dataset.timeLimited='true';
      messageActionBody.replaceChildren(node('p','','Apagar esta mensagem para os dois participantes? Ela será substituída por “Mensagem apagada”.'),confirm,supportButton('Cancelar',()=>messageActionDialog.close()));
    });
    edit.dataset.timeLimited='true';remove.dataset.timeLimited='true';
    edit.prepend(icon('pencil'));remove.prepend(icon('trash'));
    messageActionBody.append(preview,edit,remove);messageActionDialog.showModal();expireMessageControls();
    if(action==='edit')edit.click();else if(action==='delete')remove.click();
  }
  const emojiGroups = {
    'Carinhas':[['😀','sorriso'],['😃','feliz'],['😄','alegre'],['😁','radiante'],['😊','sorriso gentil'],['🙂','sorrindo'],['😉','piscando'],['😂','rindo'],['🤣','gargalhada'],['😍','apaixonado'],['🥰','carinho'],['😘','beijo'],['😎','óculos'],['🤔','pensando'],['😅','alívio'],['🥹','emocionado'],['😢','triste'],['😭','chorando'],['😟','preocupado'],['😴','sono'],['😮','surpresa'],['😡','bravo'],['🤗','abraço'],['🙏','obrigado']],
    'Gestos':[['👍','positivo'],['👎','negativo'],['👏','palmas'],['👋','oi tchau'],['🤝','acordo'],['👌','tudo bem'],['✌️','paz'],['💪','força'],['🫶','mãos coração'],['🙌','comemoração'],['🤞','torcendo'],['👀','olhos']],
    'Pets':[['🐶','cachorro'],['🐕','cão'],['🐱','gato'],['🐈','gatinho'],['🐾','patinhas'],['🐢','tartaruga'],['🐰','coelho'],['🐹','hamster'],['🐦','pássaro'],['🐴','cavalo'],['🐠','peixe'],['🦜','papagaio'],['🦎','lagarto'],['🐇','coelhinho'],['🦮','cão guia'],['🦴','osso']],
    'Corações':[['❤️','coração vermelho'],['💛','coração amarelo'],['💚','coração verde'],['💙','coração azul'],['💜','coração roxo'],['🧡','coração laranja'],['🩷','coração rosa'],['🤍','coração branco'],['🖤','coração preto'],['💕','dois corações'],['💖','coração brilhante'],['💔','coração partido']],
    'Cuidados':[['🩺','estetoscópio veterinário'],['💊','remédio'],['💉','vacina'],['🩹','curativo'],['🌡️','temperatura'],['🏥','hospital clínica'],['🧼','higiene'],['🛁','banho'],['🥣','comida ração'],['💧','água'],['📅','calendário consulta'],['⏰','horário']],
    'Símbolos':[['✅','confirmado'],['❌','cancelado'],['⚠️','atenção'],['❓','pergunta'],['❗','importante'],['⭐','estrela'],['✨','brilho'],['🎉','festa'],['🎂','aniversário'],['☀️','sol'],['🌙','noite'],['📍','local'],['📞','telefone'],['💬','mensagem'],['📷','foto'],['🎁','presente']]
  };
  function closeEmojis(returnFocus = false) {
    if(!emojiPanel)return;
    emojiPanel.hidden=true;emojiButton.setAttribute('aria-expanded','false');
    if(returnFocus&&!emojiButton.disabled)emojiButton.focus();
  }
  function buildEmojiPicker() {
    emojiButton=button('Abrir emojis','emoji','vt-chat-emoji-toggle');
    emojiButton.setAttribute('aria-haspopup','dialog');emojiButton.setAttribute('aria-expanded','false');emojiButton.setAttribute('aria-controls','vt-chat-emojis');
    emojiPanel=node('section','vt-chat-emoji-panel');emojiPanel.id='vt-chat-emojis';emojiPanel.hidden=true;emojiPanel.setAttribute('role','dialog');emojiPanel.setAttribute('aria-label','Emojis');
    const heading=node('div','vt-chat-emoji-heading');heading.append(node('strong','','Emojis'));
    const dismiss=button('Fechar emojis','close','vt-chat-list-action');dismiss.onclick=()=>closeEmojis(true);heading.append(dismiss);
    const search=node('input');search.type='search';search.placeholder='Buscar emoji…';search.setAttribute('aria-label','Buscar emoji');
    const categories=node('select');categories.setAttribute('aria-label','Categoria de emojis');
    for(const name of ['Todos',...Object.keys(emojiGroups)]){const option=node('option','',name);option.value=name;categories.append(option);}
    const controls=node('div','vt-chat-emoji-filters');controls.append(search,categories);
    const grid=node('div','vt-chat-emoji-grid');grid.setAttribute('aria-label','Escolha um emoji');
    const notice=node('p','vt-chat-emoji-notice');notice.setAttribute('role','status');
    const normalize=value=>value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
    const render=()=>{
      grid.replaceChildren();notice.textContent='';const query=normalize(search.value.trim());
      for(const [group,items] of Object.entries(emojiGroups)){
        if(categories.value!=='Todos'&&categories.value!==group)continue;
        for(const [value,label] of items){
          if(query&&!normalize(label+' '+group+' '+value).includes(query))continue;
          const choice=node('button','vt-chat-emoji-choice',value);choice.type='button';choice.title=label;choice.setAttribute('aria-label',label);
          choice.onclick=()=>{
            if(input.disabled)return;
            const start=input.selectionStart??input.value.length,end=input.selectionEnd??start;
            if(input.value.length-(end-start)+value.length>input.maxLength){notice.textContent='Limite de 1000 caracteres atingido.';return;}
            input.setRangeText(value,start,end,'end');input.dispatchEvent(new Event('input',{bubbles:true}));closeEmojis();input.focus();
          };grid.append(choice);
        }
      }
      if(!grid.childElementCount)notice.textContent='Nenhum emoji encontrado.';
    };
    search.oninput=render;categories.onchange=render;
    emojiButton.onclick=()=>{if(input.disabled)return;if(!emojiPanel.hidden){closeEmojis(true);return;}search.value='';categories.value='Todos';render();emojiPanel.hidden=false;emojiButton.setAttribute('aria-expanded','true');search.focus();};
    emojiPanel.append(heading,controls,grid,notice);
    new MutationObserver(()=>{emojiButton.disabled=input.disabled;if(input.disabled)closeEmojis();}).observe(input,{attributes:true,attributeFilter:['disabled']});
    document.addEventListener('pointerdown',event=>{if(!emojiPanel.hidden&&!emojiPanel.contains(event.target)&&!emojiButton.contains(event.target))closeEmojis();});
    return emojiButton;
  }
  function supportMode(mode) {
    if(!dialog)return;
    closeEmojis();
    if(ticketInfoButton)ticketInfoButton.hidden=mode!=='ticket'||humanTicket?.kind==='direct';
    if(mode!=='ticket'){clearMessageActions();ticketInfoDialog?.close();ticketDetails?.replaceChildren();if(ticketInfoStatus)ticketInfoStatus.textContent='';}
    if(!mode&&input)input.placeholder='Digite sua pergunta…';
    supportPanel.hidden=false;supportStatus.hidden=false;bannerVideo.parentElement.hidden=false;historyView.hidden=true;
    bannerVideo.parentElement.style.display=mode?'none':'';
    dialog.querySelector('.vt-chat-chips').style.display=mode?'none':'';
    dialog.dataset.mode=mode||'assistant';
    updateChatIdentity(mode==='ticket'?humanTicket:null);
    supportPanel.style.flex=['list','handoff'].includes(mode)?'1':'0 1 auto';
    supportPanel.style.minHeight='0';
    supportPanel.style.maxHeight=['list','handoff'].includes(mode)?'none':'25vh';
    log.hidden=['list','handoff'].includes(mode);footer.hidden=['list','handoff'].includes(mode);
    footer.querySelector('.vt-chat-notice').textContent=mode?'Atendimento por texto. Acesso ao prontuário depende de autorização.':'Sou um assistente do sistema, não substituo o veterinário.';
    directPicker?.close();
    if(mode)bannerVideo.pause();else if(dialog.open)bannerVideo.play().catch(()=>{});
    requestAnimationFrame(updateLedPath);
  }
  function supportAction(action, fields = {}, retry = null) {
    if (!session().key) {supportStatus.textContent='Entre como tutor ou veterinário para acessar atendimentos.';return;}
    if (supportPending) return;
    if(['edit','delete'].includes(action)&&messageActionTarget&&!messageWithinWindow(messageActionTarget)){expireMessageControls();return;}
    if(humanTicket&&fields.ticket_id===humanTicket.id&&['get','send','close'].includes(action)&&canObserveMessages()){
      collectVisibleReads();
      if(readCandidate?.ticketId===humanTicket.id)fields={...fields,read_through:readCandidate.messageId,read_revision:readCandidate.revision||0};
    }
    const direct=retry?.channel==='direct'||(['get','send','edit','delete'].includes(action)&&humanTicket?.kind==='direct')||['tutors','veterinarians','threads','start'].includes(action);
    if(direct&&fields.ticket_id){fields={...fields,thread_id:fields.ticket_id};delete fields.ticket_id;}
    const wireAction=action==='threads'?'list':action;
    const requestId = crypto.randomUUID();
    const operationId = retry?.operation_id || crypto.randomUUID();
    const payload = {request_id:requestId, operation_id:operationId, ...fields};
    supportPending = {requestId, action, channel:direct?'direct':'support', fields:{...fields}, operation_id:operationId};
    lastSupportRead=Date.now();
    [supportPanel,ticketDetails,messageActionBody,directPickerBody].filter(Boolean).forEach(box=>box.querySelectorAll('button,select,input,textarea').forEach(el=>el.disabled=true));
    if(humanTicket){submit.disabled=true;if(action==='send'){input.disabled=true;input.value='';}}
    if (supportStatus && action !== 'get') actionStatus().textContent = 'Carregando atendimento…';
    clearTimeout(supportTimer);
    supportTimer = setTimeout(() => supportFailure('Não foi possível confirmar a operação. Tente novamente.'), 30000);
    try { bridge((direct?'direct_':'support_') + wireAction, payload); }
    catch (_) { supportFailure('Não foi possível conectar. Tente novamente.'); }
  }
  function supportFailure(text, retryable = true) {
    clearTimeout(supportTimer);
    supportRetry = retryable ? supportPending : null; supportPending = null;
    [supportPanel,ticketDetails,messageActionBody,directPickerBody].filter(Boolean).forEach(box=>box.querySelectorAll('button,select,input,textarea').forEach(el=>el.disabled=false));
    if(humanTicket?.status==='em_atendimento'){
      submit.disabled=false;input.disabled=false;
      if(supportRetry?.action==='send'&&!input.value)input.value=supportRetry.fields.message;
    }
    const errorStatus=directPicker?.open?directPickerBody:actionStatus();
    errorStatus.replaceChildren(node('span','',text));
    if (supportRetry) {
      const retry=node('button','vt-chat-retry','Tentar atendimento novamente'); retry.type='button';
      retry.onclick=()=>{const old=supportRetry;if(!old||supportPending)return;retry.disabled=true;supportAction(old.action,old.fields,old);};
      errorStatus.append(retry);
    }
  }
  function supportButton(label, action) {
    const b=node('button','vt-chat-chip',label); b.type='button'; b.onclick=action; return b;
  }
  function offerHandoff() {
    offeredHandoff=true;
    supportMode('handoff');
    supportPanel.replaceChildren(node('h3','','Falar com um veterinário'),node('p','','Carregando seus pets…'));
    supportAction('pets');
  }
  function handoffForm(pets) {
    if(!offeredHandoff) return;
    const box=node('section','vt-chat-handoff');
    box.append(node('h3','','Falar com um veterinário'));
    box.append(node('p','','O assistente recomenda atendimento veterinário. Confirme o pet e o compartilhamento desta conversa. Isso não libera o prontuário.'));
    const select=node('select'); select.setAttribute('aria-label','Pet do atendimento');select.id='vt-chat-pet';
    const placeholder=node('option','','Selecione o pet');placeholder.value='';placeholder.disabled=true;placeholder.selected=true;select.append(placeholder);
    for(const pet of pets||[]) { const option=node('option','',pet.name); option.value=pet.id; select.append(option); }
    const label=node('label','vt-chat-consent'); const consent=node('input'); consent.type='checkbox';
    label.append(consent,document.createTextNode('Autorizo compartilhar esta conversa com o veterinário que assumir.'));
    const petLabel=node('label','vt-chat-field-label','Qual pet precisa de atendimento?');petLabel.htmlFor=select.id;
    box.append(petLabel,select,label,supportButton('Confirmar encaminhamento',()=>{
      if(!consent.checked||!select.value) {supportStatus.textContent='Escolha seu pet e confirme o compartilhamento.';return;}
      supportAction('create',{pet_id:Number(select.value),consent:true});
    }),supportButton('Continuar com o assistente',()=>{
      offeredHandoff=false;supportListVisible=false;supportPanel.replaceChildren();
      supportStatus.textContent='';supportMode(false);showConversation();input.disabled=false;submit.disabled=false;
    }));
    if(!pets?.length)box.append(node('p','','Cadastre um pet antes de solicitar atendimento.'));
    supportPanel.replaceChildren(box);
    supportStatus.textContent='Confirme o encaminhamento';
  }
  function renderTicket(ticket) {
    supportListVisible=false;
    const version=JSON.stringify(ticket);
    if(humanTicket?.id===ticket.id && renderedSupportVersion===version){
      supportStatus.textContent='';ticketInfoStatus.textContent='';
      input.disabled=ticket.status!=='em_atendimento';submit.disabled=input.disabled;
      requestAnimationFrame(collectVisibleReads);
      return;
    }
    const previousId=humanTicket?.kind===ticket.kind?humanTicket?.id:null, draft=input.value;
    const previousScroll=log.scrollTop,atBottom=log.scrollHeight-log.clientHeight-log.scrollTop<48;
    if(previousId!==ticket.id)readCandidate=null;
    const reasonDraft=ticketDetails.querySelector('input')?.value||'';
    humanTicket=ticket;renderedSupportVersion=version;offeredHandoff=false;
    supportMode('ticket');
    if(previousId!==ticket.id)cancelResponse();
    historyView.hidden=true;log.hidden=false;footer.hidden=false;log.replaceChildren();
    appendChatStart(ticket.created_at||ticket.messages?.[0]?.at||conversationStartedAt);
    if(previousId===ticket.id)input.value=draft;else input.value='';
    const vet=ticket.veterinarian;
    supportStatus.textContent='';supportPanel.replaceChildren();ticketDetails.replaceChildren();ticketInfoStatus.textContent='';
    ticketInfoButton.dataset.status=ticket.status;ticketInfoDialog.dataset.status=ticket.status;
    const status={aguardando:'Aguardando veterinário',em_atendimento:'Em atendimento',encerrado:'Encerrado'}[ticket.status]||ticket.status;
    ticketInfoButton.title=`Informações do atendimento · ${status}`;
    ticketInfoButton.setAttribute('aria-label',`Informações do atendimento: ${status}`);
    if(ticket.kind!=='direct'){
    const petIdentity=node('div','vt-chat-detail-pet');const petCopy=node('div','vt-chat-pet-copy');
    petCopy.append(node('strong','',ticket.pet.name),node('span','vt-chat-detail-status',status));
    petIdentity.append(petAvatar(ticket.pet.photo,`Foto de ${ticket.pet.name}`),petCopy);ticketDetails.append(petIdentity);
    if(session().key.startsWith('veterinario:')){
      const tutorSection=node('section','vt-chat-tutor-details');tutorSection.setAttribute('aria-label','Dados do tutor');
      const heading=node('h4');heading.append(icon('tutor'),document.createTextNode('Tutor responsável'));
      const fields=node('dl');
      for(const [label,value] of [['Nome',ticket.tutor?.name],['Telefone',ticket.tutor?.phone],['E-mail',ticket.tutor?.email]]){
        const field=node('div');field.append(node('dt','',label),node('dd','',typeof value==='string'&&value.trim()?value:'Não informado'));fields.append(field);
      }
      tutorSection.append(heading,fields);ticketDetails.append(tutorSection);
    }
    if(vet)ticketDetails.append(node('p','',`${vet.name} · CRMV ${vet.crmv}/${vet.uf}`));
    if(ticket.status==='aguardando')ticketDetails.append(node('p','vt-chat-waiting','Seu chamado foi enviado. Aguarde um veterinário assumir. A atualização acontece a cada 20 segundos.'));
    ticketDetails.append(node('p','','Atendimento por texto. O acesso ao prontuário depende de autorização.'));
    if(ticket.status==='encerrado')ticketDetails.append(node('p','','Este atendimento foi encerrado.'),supportButton('Iniciar nova conversa',resetConversation));
    else ticketDetails.append(supportButton('Atualizar atendimento',()=>supportAction('get',{ticket_id:ticket.id})));
    }else{ticketInfoButton.hidden=true;footer.querySelector('.vt-chat-notice').textContent='Conversa privada com o interlocutor. Não é um atendimento.';}
    for(const row of ticket.context||[]){const role=row.role==='assistant'?'assistant':'tutor';message(row.content,role==='tutor'&&session().key.startsWith('tutor:'),false,null,role);}
    const timeline=[...(ticket.events||[]).filter(e=>['claim','close'].includes(e.action)).map(e=>({...e,system:true})),...(ticket.messages||[])];
    const instant=at=>at?new Date(at).getTime():0;
    timeline.sort((a,b)=>instant(a.at)-instant(b.at));
    for(const row of timeline) {
      if(row.system){
        const event=message(row.action==='claim'?'Veterinário assumiu o atendimento.':'Atendimento encerrado: '+row.reason,false,false,row.at);
        event.classList.add('vt-chat-system');event.querySelector('.vt-chat-avatar')?.remove();
      }else{
        const own=row.author_profile===session().key.split(':')[0];
        const item=message(row.deleted_at?'Mensagem apagada':row.text,own,false,row.at,row.author_profile);
        item.dataset.messageId=row.id||'';item.dataset.incoming=String(!own&&!row.deleted_at);
        if(row.deleted_at){item.classList.add('is-deleted');item.querySelector('.vt-chat-bubble p').append(icon('deleted'));}
        else if(row.edited_at)item.querySelector('.vt-chat-time').append(node('span','vt-chat-edited',' · Editada'));
        if(own&&!row.deleted_at){
          const receipt=node('span',`vt-chat-receipt${row.read_at?' is-read':''}`);
          receipt.append(icon(row.read_at?'checks':'check'),node('span','',row.read_at?'Visto':'Entregue'));
          receipt.setAttribute('aria-label',row.read_at?'Mensagem vista':'Mensagem entregue');
          if(row.read_at)receipt.title='Vista em '+new Date(row.read_at).toLocaleString('pt-BR');
          item.querySelector('.vt-chat-time').append(receipt);
          if(ticket.status==='em_atendimento'&&row.id){
            const bubble=item.querySelector('.vt-chat-bubble');bubble.tabIndex=0;bubble.setAttribute('role','group');bubble.setAttribute('aria-label','Mensagem própria. Pressione Enter para abrir opções.');
            const control=button('Opções da mensagem','more','vt-chat-message-menu-trigger');control.setAttribute('aria-haspopup','dialog');
            control.onclick=event=>{event.stopPropagation();openMessageActions(row);};item.querySelector('.vt-chat-time').append(control);
            bubble.onclick=event=>{if(!event.target.closest('button')&&!window.getSelection()?.toString())openMessageActions(row);};
            bubble.oncontextmenu=event=>{event.preventDefault();openMessageActions(row);};
            bubble.onkeydown=event=>{if(event.target===bubble&&['Enter',' '].includes(event.key)){event.preventDefault();openMessageActions(row);}};
          }
        }
      }
    }
    if(previousId===ticket.id&&!atBottom)log.scrollTop=previousScroll;
    requestAnimationFrame(collectVisibleReads);
    input.placeholder=ticket.status==='em_atendimento'?'Digite sua mensagem…':ticket.status==='aguardando'?'Aguardando um veterinário…':'Atendimento encerrado';
    input.disabled=ticket.status!=='em_atendimento'; submit.disabled=input.disabled;
    const canClose=ticket.kind!=='direct'&&((ticket.status==='aguardando'&&session().key.startsWith('tutor:'))||(ticket.status==='em_atendimento'&&session().key.startsWith('veterinario:')));
    if(ticket.kind!=='direct'&&ticket.status==='em_atendimento'&&session().key.startsWith('tutor:'))ticketDetails.append(node('p','','O encerramento do atendimento é feito pelo veterinário responsável.'));
    if(canClose && !ticketDetails.querySelector('input')) {
      const reason=node('input');reason.placeholder='Motivo do encerramento / orientação final';reason.maxLength=1000;
      reason.value=previousId===ticket.id?reasonDraft:'';
      reason.setAttribute('aria-label','Motivo do encerramento');reason.id='vt-chat-close-reason';
      const reasonLabel=node('label','vt-chat-field-label','Motivo do encerramento / orientação final');reasonLabel.htmlFor=reason.id;
      ticketDetails.append(reasonLabel,reason,supportButton(ticket.status==='aguardando'?'Cancelar chamado':'Encerrar atendimento',()=>{
        if(!reason.value.trim()){ticketInfoStatus.textContent='Informe o motivo ou orientação final.';reason.focus();return;}
        supportAction('close',{ticket_id:ticket.id,reason:reason.value,expected_status:ticket.status});
      }));
    }
  }
  function directDirectory(data) {
    const contacts=data.tutors||data.veterinarians,isDirectory=Boolean(contacts),isTutor=session().key.startsWith('tutor:'),contactLabel=isTutor?'veterinário':'tutor',directoryAction=isTutor?'veterinarians':'tutors';
    const directory=isDirectory?directPickerBody:supportPanel;
    if(!directory)return;
    if(!isDirectory){supportMode('list');humanTicket=null;readCandidate=null;}
    directory.replaceChildren();supportStatus.textContent='';
    const toolbar=node('div','vt-chat-list-toolbar');
    const title=node('h3','',isDirectory?'Escolher '+contactLabel:'Conversas');toolbar.append(title);directory.append(toolbar);
    if(isDirectory)directory.append(node('p','vt-chat-direct-caption','Selecione um '+contactLabel+' para iniciar uma conversa privada.'));
    if(isDirectory){
      const form=node('form','vt-chat-direct-search'),search=node('input');search.placeholder='Buscar '+contactLabel+' por nome ou ID';search.maxLength=100;search.value=directSearch;
      search.setAttribute('aria-label','Buscar '+contactLabel);const find=node('button','vt-chat-chip','Buscar');find.type='submit';
      form.append(search,find);form.onsubmit=e=>{e.preventDefault();directSearch=search.value.trim();supportAction(directoryAction,{search:directSearch});};directory.append(form);
    }else{
      const actions=node('div','vt-chat-list-actions');const refresh=button('Atualizar conversas','refresh','vt-chat-list-action');refresh.onclick=()=>supportAction('threads');actions.append(refresh);
      {const start=button(isTutor?'Falar com veterinário':'Falar com tutor',isTutor?'veterinarian':'tutor','vt-chat-list-action');start.onclick=openTutorPicker;actions.append(start);}
      toolbar.append(actions);
    }
    const rows=contacts||data.threads||[];
    for(const row of rows){
      const card=node('article','vt-chat-ticket-card vt-chat-direct-card');card.append(statusLed());
      const identity=node('div','vt-chat-direct-identity');identity.append(participantAvatar(isDirectory?(isTutor?'veterinario':'tutor'):row.peer?.profile|| (session().key.startsWith('tutor:')?'veterinario':'tutor')));
      identity.append(node('strong','',isDirectory?(row.name||(isTutor?'Veterinário #':'Tutor #')+row.id):(row.peer?.name||'Nome não informado')));card.append(identity);
      if(!isDirectory){
        if(row.unread)card.append(node('small','',row.unread+' mensagem(ns) não vista(s)'));
        if(row.last_message)card.append(node('p','',row.last_message.text));
      }
      card.append(supportButton(isDirectory?'Conversar':'Abrir conversa',()=>supportAction(isDirectory?'start':'get',isDirectory?(isTutor?{veterinario_id:row.id}:{tutor_id:row.id}):{thread_id:row.id},{channel:'direct'})));directory.append(card);
    }
    if(!rows.length)directory.append(node('p','',isDirectory?'Nenhum '+contactLabel+' encontrado.':'Você ainda não tem conversas.'));
    if(data.page>1)directory.append(supportButton('Página anterior',()=>supportAction(isDirectory?directoryAction:'threads',{page:data.page-1,search:directSearch})));
    if(data.has_next)directory.append(supportButton('Próxima página',()=>supportAction(isDirectory?directoryAction:'threads',{page:data.page+1,search:directSearch})));
  }
  let directSearch='',directPicker=null,directPickerBody=null;
  function openTutorPicker(){
    if(pending||supportPending)return;
    const isTutor=session().key.startsWith('tutor:'),label=isTutor?'Falar com veterinário':'Falar com tutor';
    directPicker?.remove();directPicker=node('dialog','vt-chat-ticket-dialog vt-chat-direct-picker');directPicker.setAttribute('aria-label',label);
    const close=button('Fechar seleção de contato','close','vt-chat-list-action');close.onclick=()=>directPicker.close();
    directPickerBody=node('div','vt-chat-direct-directory');
    const heading=node('header','vt-chat-details-header');heading.append(node('h3','',label),close);
    const mascot=node('img','vt-chat-direct-mascot');mascot.src='/optimized/espreitando.webp';mascot.alt='';mascot.setAttribute('aria-hidden','true');
    directPicker.append(statusLed(),mascot,heading,directPickerBody);document.body.append(directPicker);directPicker.showModal();
    directSearch='';supportAction(isTutor?'veterinarians':'tutors');
  }
  window.addEventListener('vettech:direct-response',event=>{
    const data=event.detail||{};
    if(!dialog?.open||supportPending?.channel!=='direct'||data.request_id!==supportPending.requestId||data.conversation_id!==conversationId)return;
    clearTimeout(supportTimer);
    if(!data.ok){supportFailure(data.error||'Não foi possível abrir a conversa.');return;}
    if(Number.isFinite(data.server_time))serverClock={time:data.server_time,observedAt:performance.now()};
    const mutation=['edit','delete'].includes(supportPending.action);supportPending=null;supportRetry=null;
    [supportPanel,ticketDetails,messageActionBody,directPickerBody].filter(Boolean).forEach(box=>box.querySelectorAll('button,select,input,textarea').forEach(el=>el.disabled=false));
    if(data.thread){directPicker?.close();renderTicket({...data.thread,kind:'direct',status:'em_atendimento',pet:{name:''},context:[],events:[]});}
    else directDirectory(data);
    if(mutation&&messageActionDialog.open){messageActionStatus.textContent='';messageActionDialog.close();}
  });
  window.addEventListener('vettech:support-response', event=>{
    const data=event.detail||{};
    if(!dialog?.open||!supportPending||supportPending.channel==='direct'||data.request_id!==supportPending.requestId||data.conversation_id!==conversationId)return;
    clearTimeout(supportTimer);
    if(Number.isFinite(data.server_time))serverClock={time:data.server_time,observedAt:performance.now()};
    if(!data.ok){supportFailure(data.error||'Não foi possível concluir o atendimento.',data.retryable!==false);return;}
    const completedMutation=['edit','delete'].includes(supportPending.action);
    supportPending=null;supportRetry=null;
    [supportPanel,ticketDetails,messageActionBody,directPickerBody].filter(Boolean).forEach(box=>box.querySelectorAll('button,select,input,textarea').forEach(el=>el.disabled=false));
    if(data.pets){handoffForm(data.pets);return;}
    if(data.ticket)renderTicket(data.ticket);
    else if(data.tickets){
      supportListVisible=true;
      supportMode('list');
      humanTicket=null;input.disabled=true;submit.disabled=true;
      supportStatus.textContent='';supportPanel.replaceChildren();
      const toolbar=node('div','vt-chat-list-toolbar');
      const actions=node('div','vt-chat-list-actions');
      const refresh=button('Atualizar atendimentos','refresh','vt-chat-list-action');
      refresh.onclick=()=>supportAction('list');
      const assistant=button('Falar com assistente','clinic','vt-chat-list-action');
      assistant.onclick=resetConversation;
      actions.append(refresh,assistant);
      toolbar.append(node('h3','','Atendimentos'),actions);
      supportPanel.append(toolbar);
      for(const t of [...data.tickets].reverse()) {
        const card=node('article','vt-chat-ticket-card');card.append(statusLed());
        card.dataset.status=t.status;card.dataset.profile=session().key.split(':')[0];
        const status={aguardando:'Aguardando veterinário',em_atendimento:'Em atendimento',encerrado:'Encerrado'}[t.status]||t.status;
        const identity=node('div','vt-chat-ticket-identity'),copy=node('div','vt-chat-pet-copy'),heading=node('div','vt-chat-ticket-heading');
        heading.append(node('strong','',`Atendimento #${t.id}`),node('span','vt-chat-ticket-status',status));copy.append(heading);
        if(t.tutor)copy.append(node('small','vt-chat-ticket-tutor','Tutor: '+(t.tutor.name||'Nome não informado')));
        if(t.created_at)copy.append(node('small','',new Date(t.created_at).toLocaleDateString('pt-BR')));
        identity.append(petAvatar(data.pet_photos?.[t.pet_id],`Foto do pet do atendimento #${t.id}`),copy);card.append(identity);
        const label=t.own?'Ver conversa':'Assumir atendimento';
        card.append(supportButton(label,()=>supportAction(t.own?'get':'claim',{ticket_id:t.id})));
        supportPanel.append(card);
      }
      if(!data.tickets.length)supportPanel.append(node('p','','Nenhum atendimento disponível.'));

    }
    if(completedMutation&&messageActionDialog.open){messageActionStatus.textContent='';messageActionDialog.close();}
  });
  setInterval(()=>{
    expireMessageControls();
    if(document.hidden||!document.hasFocus()||!dialog?.open||ticketInfoDialog?.open||directPicker?.open||messageActionDialog?.open||!historyView.hidden||supportPending||supportRetry||Date.now()-lastSupportRead<20000)return;
    collectVisibleReads();
    if(humanTicket&&(humanTicket.status!=='encerrado'||readCandidate?.ticketId===humanTicket.id))supportAction('get',{ticket_id:humanTicket.id});
  },1000);
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
    closeEmojis();
    clearTimeout(responseTimer); generation++; activeRequest = null;
    pending = false; lastQuestion = ''; errorRow = null;
    if (input) { input.disabled = false; input.value = ''; submit.disabled = false; }
  }
  function showConversation() {
    historyView.hidden = true; historyView.replaceChildren(); log.hidden = false; footer.hidden = false;
    historyButton.setAttribute('aria-expanded', 'false');
    supportMode(dialog.dataset.mode==='assistant'?false:dialog.dataset.mode);
    if(!footer.hidden)input.focus();
  }
  function resetConversation() {
    supportMode(false);
    supportListVisible=false;
    renderedSupportVersion='';readCandidate=null;serverClock=null;clearTimeout(readFlushTimer);readFlushTimer=null;clearTimeout(focusRefreshTimer);focusRefreshTimer=null;clearTimeout(focusFollowUpTimer);
    directPicker?.close();directPickerBody?.replaceChildren();clearTimeout(supportTimer);supportPending=null;supportRetry=null;humanTicket=null;offeredHandoff=false;
    supportPanel?.replaceChildren();if(supportStatus)supportStatus.textContent='';
    cancelResponse(); conversation = []; log.replaceChildren();conversationStartedAt=Date.now();
    conversationId = crypto.randomUUID();
    showConversation(); message(welcome());
    try { bridge('open'); } catch (_) { /* First send displays a recoverable error. */ }
  }
  function showHistory() {
    closeEmojis();
    historyView.replaceChildren();
    const back = button('Voltar à conversa','back','vt-chat-list-action');
    back.type = 'button'; back.onclick = showConversation;
    const heading=node('div','vt-chat-list-toolbar');heading.append(node('h3','','Histórico de conversas'),back);historyView.append(heading);
    historyView.append(node('p','vt-chat-history-caption','Suas conversas anteriores com a Turtle nesta sessão.'));
    if (!history.length){
      const empty=node('div','vt-chat-history-empty'),face=avatar();
      empty.append(face,node('h4','','Vamos começar uma conversa?'),node('p','','Quando você iniciar uma nova conversa, as anteriores aparecerão aqui durante esta sessão.'),supportButton('Voltar para a Turtle',showConversation));historyView.append(empty);
    }
    for (const entry of [...history].reverse()) {
      const details = node('details', 'vt-chat-history-entry');
      details.append(statusLed());
      const summary=node('summary');summary.append(node('small','',entry.date),node('strong','',entry.title),node('span','vt-chat-history-count',entry.messages.length+' mensagens · Toque para expandir'));details.append(summary);
      for (const item of entry.messages) {
        const row = node('p', 'vt-chat-history-message');
        row.append(node('strong', '', item.user ? 'Você: ' : 'Turtle: '), document.createTextNode(item.text));
        details.append(row);
      }
      historyView.append(details);
    }
    ticketInfoButton.hidden=true;ticketInfoDialog.close();
    supportPanel.hidden=true;supportStatus.hidden=true;bannerVideo.parentElement.hidden=true;
    log.hidden = true; footer.hidden = true; historyView.hidden = false;
    historyButton.setAttribute('aria-expanded', 'true'); back.focus();
  }
  function message(text, user = false, record = true, at = null, author = null) {
    if (record) conversation.push({text, user});
    appendChatStart();
    const row = node('div', `vt-chat-row${user ? ' is-user' : ''}`);
    if(author||user){
      const profile=author||(session().key.startsWith('veterinario:')?'veterinario':'tutor');
      const role=profile==='assistant'?'Assistente':profile==='veterinario'?'Veterinário':'Tutor';
      const name=profile==='tutor'?humanTicket?.tutor?.name:profile==='veterinario'?humanTicket?.veterinarian?.name:null;
      const confirmed=name|| (user?session().name:'')||(profile==='tutor'&&humanTicket?.tutor?'Nome não informado':'');
      row.dataset.author=profile;row.append(node('span','vt-chat-author-label',role+(confirmed?' · '+confirmed:'')));
    }
    if (!user) row.append(author&&author!=='assistant'?participantAvatar(author):avatar());
    const bubble = node('div', 'vt-chat-bubble');
    bubble.append(node('p', '', text));
    const time = node('div', 'vt-chat-time', new Intl.DateTimeFormat('pt-BR', {hour:'2-digit',minute:'2-digit'}).format(at ? new Date(at) : new Date()));
    if (user&&!humanTicket) time.append(node('span', 'vt-chat-check', ' ✓✓'));
    bubble.append(time); row.append(bubble);
    if(user)row.append(participantAvatar(author|| (session().key.startsWith('veterinario:')?'veterinario':'tutor')));
    log.append(row); log.scrollTop = log.scrollHeight;
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
    if (historyView.hidden&&!footer.hidden) input.focus();
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
    closeEmojis();
    const clean = text.trim().slice(0,1000);
    if (!clean || pending) return;
    if(humanTicket){
      if(humanTicket.status==='em_atendimento'&&!supportPending){
        const retry=supportRetry?.action==='send'&&supportRetry.fields.message===clean&&(supportRetry.fields.ticket_id||supportRetry.fields.thread_id)===humanTicket.id?supportRetry:null;
        supportAction('send',{ticket_id:humanTicket.id,message:clean},retry);input.value='';
      }
      return;
    }
    lastQuestion = clean; message(clean, true); input.value = ''; respond(clean);
  }
  function close() {
    directPicker?.close();
    clearMessageActions();
    ticketInfoDialog?.close();
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
    const name = node('h2', '', 'Turtle · Vet Tech'); name.id = 'vt-chat-title';
    title.append(name, node('span', 'vt-chat-status', 'Ajuda do sistema'));
    const minimize = button('Minimizar chat', 'minus', 'vt-chat-control'); minimize.onclick = close;
    const dismiss = button('Fechar chat', 'close', 'vt-chat-control'); dismiss.onclick = close;
    historyButton = button('Histórico de conversas', 'history', 'vt-chat-control');
    historyButton.setAttribute('aria-expanded', 'false');
    historyButton.onclick = () => historyView.hidden ? showHistory() : showConversation();
    const supportEntry=supportButton('Atendimentos',()=>{if(pending)return;offeredHandoff=false;supportAction('list');});
    head.append(back, avatar(), title, historyButton, minimize, dismiss);
    const navigation=node('nav','vt-chat-navigation');navigation.setAttribute('aria-label','Navegação do chat');
    navigation.append(supportEntry,supportButton('Nova conversa',resetConversation),supportButton('Conversas',()=>{if(!pending)supportAction('threads');}));
    const directStart=supportButton('Falar com tutor',openTutorPicker);directStart.classList.add('vt-chat-vet-direct');navigation.append(directStart);
    const updateDirectAccess=()=>{const isTutor=session().key.startsWith('tutor:');directStart.hidden=!session().key;directStart.textContent=isTutor?'Falar com veterinário':'Falar com tutor';};updateDirectAccess();
    new MutationObserver(updateDirectAccess).observe(document.getElementById('vettech-chat-session')||document.body,{attributes:true,attributeFilter:['data-chat-key'],subtree:true,childList:true});
    const banner = node('div', 'vt-chat-banner');
    bannerVideo = node('video', 'vt-chat-banner-video');
    bannerVideo.muted = true; bannerVideo.defaultMuted = true;
    bannerVideo.autoplay = true; bannerVideo.loop = true; bannerVideo.playsInline = true;
    bannerVideo.preload = 'metadata';
    bannerVideo.setAttribute('aria-hidden', 'true');
    bannerVideo.src = '/gifturtle.mp4';
    banner.append(bannerVideo);
    log = node('div', 'vt-chat-messages'); log.setAttribute('role', 'log'); log.setAttribute('aria-live', 'polite'); log.setAttribute('aria-label', 'Conversa com o assistente');
    log.addEventListener('scroll',collectVisibleReads,{passive:true});
    document.addEventListener('visibilitychange',()=>{if(document.hidden)flushReadCandidate();else refreshOnFocus();});
    window.addEventListener('blur',flushReadCandidate);
    window.addEventListener('focus',refreshOnFocus);
    supportStatus=node('div','vt-chat-support-status');supportStatus.setAttribute('role','status');
    supportPanel=node('section','vt-chat-support-panel');supportPanel.setAttribute('aria-label','Atendimento veterinário');
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
    form.append(input,buildEmojiPicker(),submit); form.onsubmit=e=>{e.preventDefault();send(input.value);};
    foot.append(emojiPanel,chips,form,node('p','vt-chat-notice','Sou um assistente do sistema, não substituo o veterinário.'));
    ticketInfoButton=button('Informações do atendimento','info','vt-chat-floating-info');ticketInfoButton.hidden=true;
    ticketInfoButton.setAttribute('aria-haspopup','dialog');ticketInfoButton.setAttribute('aria-controls','vt-chat-ticket-details');
    ticketInfoDialog=node('dialog','vt-chat-ticket-dialog');ticketInfoDialog.id='vt-chat-ticket-details';ticketInfoDialog.setAttribute('aria-labelledby','vt-chat-details-title');
    const detailsHead=node('header','vt-chat-details-header');
    const detailsTitle=node('h3','','Informações do atendimento');detailsTitle.id='vt-chat-details-title';
    const detailsClose=button('Fechar informações do atendimento','close','vt-chat-list-action');detailsClose.onclick=()=>ticketInfoDialog.close();
    detailsHead.append(detailsTitle,detailsClose);
    ticketDetails=node('section','vt-chat-ticket-details');ticketInfoStatus=node('div','vt-chat-detail-error');ticketInfoStatus.setAttribute('role','status');
    ticketInfoDialog.append(statusLed(),detailsHead,ticketInfoStatus,ticketDetails);
    ticketInfoButton.onclick=()=>{ticketInfoDialog.showModal();};
    ticketInfoDialog.addEventListener('close',()=>{if(dialog.open&&!ticketInfoButton.hidden)ticketInfoButton.focus();});
    ticketInfoDialog.addEventListener('click',e=>{if(e.target!==ticketInfoDialog)return;const r=ticketInfoDialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)ticketInfoDialog.close();});
    messageActionDialog=node('dialog','vt-chat-ticket-dialog vt-chat-message-dialog');messageActionDialog.setAttribute('aria-labelledby','vt-chat-message-actions-title');
    const messageHead=node('header','vt-chat-details-header'),messageTitle=node('h3','','Opções da mensagem');messageTitle.id='vt-chat-message-actions-title';
    const messageClose=button('Fechar opções da mensagem','close','vt-chat-list-action');messageClose.onclick=()=>messageActionDialog.close();messageHead.append(messageTitle,messageClose);
    messageActionStatus=node('div','vt-chat-detail-error');messageActionStatus.setAttribute('role','status');messageActionBody=node('section','vt-chat-message-actions');
    messageActionDialog.append(statusLed(),messageHead,messageActionStatus,messageActionBody);
    messageActionDialog.addEventListener('close',()=>{
      const target=messageActionTarget&&[...log.querySelectorAll('[data-message-id]')].find(el=>el.dataset.messageId===messageActionTarget.id)?.querySelector('.vt-chat-bubble');
      if(dialog.open){if(target?.tabIndex===0)target.focus();else if(!input.disabled)input.focus();}
      requestAnimationFrame(collectVisibleReads);if(readCandidate)scheduleReadSync();
      if(messageActionStatus.textContent&&humanTicket&&!supportPending){supportRetry=null;supportAction('get',{ticket_id:humanTicket.id});}
    });
    messageActionDialog.addEventListener('click',event=>{if(event.target!==messageActionDialog)return;const rect=messageActionDialog.getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)messageActionDialog.close();});
    dialog.append(led,head,navigation,banner,supportStatus,supportPanel,historyView,log,foot,ticketInfoButton); document.body.append(dialog,ticketInfoDialog,messageActionDialog);
    // The decorative path follows the outer frame in every view.
    // Local layout coordinates avoid the scale used by the opening animation.
    updateLedPath = () => {
      const width = dialog.clientWidth, height = dialog.clientHeight;
      if(ticketInfoButton)ticketInfoButton.style.bottom=`${footer.offsetHeight+16}px`;
      if (!dialog.open || width < 48 || height < 96) return;
      const left = 1.5, right = width - 1.5, top = 1.5, bottom = height - 1.5;
      const radius = Math.min(22.5, width / 4, height / 4);
      track.setAttribute('d', [
        `M ${left + radius} ${top} H ${right - radius}`,
        `Q ${right} ${top} ${right} ${top + radius} V ${bottom - radius}`,
        `Q ${right} ${bottom} ${right - radius} ${bottom} H ${left + radius}`,
        `Q ${left} ${bottom} ${left} ${bottom - radius} V ${top + radius}`,
        `Q ${left} ${top} ${left + radius} ${top} Z`,
      ].join(' '));
    };
    const ledResize = new ResizeObserver(updateLedPath);
    ledResize.observe(dialog); ledResize.observe(banner);ledResize.observe(footer);

    dialog.addEventListener('click', e => { if (e.target === dialog) { const r=dialog.getBoundingClientRect(); if(e.clientX<r.left || e.clientX>r.right || e.clientY<r.top || e.clientY>r.bottom) close(); } });
    document.addEventListener('keydown', e => {
      if(e.key==='Escape'&&messageActionDialog.open){e.preventDefault();messageActionDialog.close();return;}
      if(e.key==='Escape'&&emojiPanel&&!emojiPanel.hidden){e.preventDefault();closeEmojis(true);return;}
      if(e.key==='Escape'&&ticketInfoDialog.open){e.preventDefault();ticketInfoDialog.close();return;}
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
      history = []; sessionKey = user.key;directPicker?.close();directPickerBody?.replaceChildren();directSearch='';
      clearMessageActions();ticketInfoDialog?.close();ticketDetails?.replaceChildren();if(ticketInfoStatus)ticketInfoStatus.textContent='';
      clearTimeout(supportTimer);supportPending=null;humanTicket=null;supportRetry=null;
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
