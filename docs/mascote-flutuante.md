# Mascote flutuante

Disponível em todas as páginas pelo `extra_app_wraps` do Reflex 0.9.11,
registrado em `vet_tech/vet_tech.py`. Componente em
`vet_tech/components/mascote_flutuante.py`, estilo em `assets/mascote.css` e
controlador local em `assets/mascote.js`. Não há estado Reflex de animação;
o chat usa eventos de background para suas chamadas HTTP.

A mascote é `position: fixed` e o wrapper global é um Fragment sem elemento
HTML de layout. Não há faixa inferior, padding reservado nem scrollport próprio;
a página mantém sua altura e centralização originais. O toaster aparece acima
do botão sem alterar o fluxo do conteúdo.

`mascote_flutuante(glow_mode="green")` é o padrão. Para RGB, usar `"rgb"` na
chamada dentro de `mascote_app_wrap`. Só o glow recebe mudanças de hue-rotate;
o modo reduzido mantém a iluminação estática.

Idle usa `assets/mascote/mascote_idle.png` (320×320 RGBA), com imagem inteira
em `object-fit: contain`, botão de aspect-ratio 1, 140 px desktop/96 px mobile
 e offsets de 24 px mais safe area. O rastreamento provisório move a imagem
inteira até 4 px/4 graus, com pivô nos pés. Sem piscadas/respiração segmentadas.
Ao entrar em hover/foco, o LED verde faz duas pulsações lentas e suaves em
aproximadamente 4 segundos, depois fica aceso estável enquanto a interação durar.
Ao sair apaga; na próxima entrada recomeça. Reduced-motion mostra luz estática.
A sombra elíptica é CSS; se hover falhar, idle permanece com glow/pop.
O fundo decorativo do login cobre a página e toda a viewport.

O clique publica uma única ocorrência de `vettech:mascote-click` no `window`.
O controlador `assets/support-chat.js` consome o evento e abre um dialog modal
com fundo escurecido. No desktop, o painel permanece acima da tartaruga; no mobile,
ocupa a tela. Esc, clique fora, minimizar, voltar ou fechar restauram o foco à mascote.

O chat usa a integração servidor-servidor do n8n descrita em `docs/n8n-chat.md`;
credenciais e contexto ficam no backend. Sem configuração válida, mostra erro
amigável, sem inventar dados clínicos. Cada abertura começa limpa. Conversas com interação são arquivadas no botão de relógio “Histórico de conversas”, com retorno à conversa atual; somente as últimas 20 ficam em memória nesta aba. Recarregar ou trocar de sessão apaga tudo. Os chips
orientam navegação sem contornar autenticação. O status “Ajuda do sistema” não
promete atendimento humano online. Estilos em `assets/support-chat.css`.

Verificação: `tests/integration/support_chat_browser.py --url http://localhost:3000`
(com Playwright disponível e `--chromium` opcional para o executável instalado).

## Testar localmente

Com o ambiente e configuração de backend existentes:

```bash
bash scripts/run-local.sh
```

Abrir o endereço impresso pelo Reflex. Conferir login/cadastro e, com uma conta
de teste, Meus Pets, Configurações, Prontuário e Atendimento. Mover o cursor,
apontar e focar por Tab; Enter e Espaço devem emitir o evento.
Emular toque e `prefers-reduced-motion: reduce` no navegador. Após mudanças em
produção, parar e reiniciar o processo para recompilar.

No console, antes de clicar:

```javascript
window.addEventListener("vettech:mascote-click", () => console.count("mascote"));
```

O teste automatizado `tests/integration/mascote_browser.py` usa o navegador
Chromium do Playwright e o endereço local informado por `--url`. Não exige
credenciais nem chama serviços externos para exercitar a animação isolada;
também verifica montagem e navegação pública no app real.

## Login local sem conexão ao servidor

O launcher carrega .env e executa frontend e backend juntos, por padrão na porta
3001. Se o navegador mostrar erro de WebSocket em localhost:8000, há um frontend
sem o backend correspondente. Pare as instâncias antigas deste projeto e execute
o launcher; use o endereço mostrado em reflex.log. Para outra porta, defina
`VET_TECH_PORT`. Não use o stub sintético de testes na instância de uso diário.

Enquanto o chat estiver aberto, a mascote mantém os braços em V e o glow aceso estático, mesmo sem hover/foco. O evento local `vettech:chat-state` sincroniza esse estado e pausa o rastreamento. Fechar ou minimizar restaura o comportamento anterior.

## Saudação e ciclo de conversa
O wrapper renderiza `vettech-chat-session` com nome e chave pública da identidade
confirmada pelo `State` (perfil e ID), sem token. Com login, a saudação usa o nome;
sem login, é genérica. Essas informações são apenas apresentação e não autorizam
acesso a dados. O controlador observa mudanças para limpar conversa e histórico
no login, logout ou troca de identidade. Fechar por qualquer caminho cancela a
resposta pendente e arquiva apenas conversas com mensagem do usuário. Minimizar
também encerra a conversa atual. A próxima abertura exibe nova saudação.

O histórico é somente leitura, não vai ao servidor e não persiste em storage.
O botão de relógio no cabeçalho abre a lista; “Voltar à conversa” retorna ao chat.
