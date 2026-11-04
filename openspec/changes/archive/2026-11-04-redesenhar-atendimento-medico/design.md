# Design

## Context
Reflex/Python com assets/vet_tech.css, fonte Nunito, ícones Lucide, date_hint e mascote global. attendance_content concentra a apresentação; clinical_line preserva os campos clínicos e attendance_history_dialog compartilha o histórico com os cards.

## Goals / Non-Goals
Reorganizar o atendimento e os pontos associados de agenda, histórico, chat, identidade e comandos conforme as seções abaixo. Preservar regras clínicas e integrações. Um evento de preparação limpa apenas os dados e mensagens anteriores do modal. Falhas do histórico possuem mensagem independente, sem ocultar os cards da agenda.

## Decisions
- Centralizar tokens --vet-* no stylesheet existente e ativar estilos por .attendance-page. Evitar alterar tokens globais do tutor.
- Reutilizar date_hint e clinical_line; manter condicionais e argumentos de eventos. Na agenda e em Consultas, reutilizar o mesmo diálogo de histórico do atendimento. No atendimento, usar dialog Radix com trigger local e o mesmo open_prior_history, sem novo estado de negócio ou HTTP. Executar prepare_prior_history antes da leitura para limpar dados e clinic_message ao solicitar para distinguir espera de erro; histórico vazio confirmado é representado pelas listas retornadas.
- Usar placeholder de pata: pet_summary não fornece foto. Manter nascimento disponível, sem acrescentar cálculo de idade fora do escopo.
- Diagnóstico e observações usam textarea com o mesmo valor e on_change. Data e retorno ficam juntos; demais campos ocupam a largura.
- Wallpaper via pseudo-elemento fixo, fallback branco opaco e @supports para vidro. Responsividade CSS e redução de movimento.

- Modal com título/descrição acessíveis, fechamento por X, botão, Escape e clique externo, foco restaurado ao gatilho. Cabeçalho verde, mascote_logo.png decorativa acima da divisória entre cabeçalho e conteúdo, com a base alinhada à linha e deslocada levemente à esquerda (24px no desktop e 16px no mobile) e categorias com contagens; área de conteúdo rolável em desktop/mobile e tokens locais que acompanham o tema do documento inclusive em portais.

## Calendários dos campos clínicos
- Substituir inputs nativos de data do atendimento e das linhas por botões com valor brasileiro e ícone de calendário. O valor gravado continua ISO.
- Compartilhar o painel visual, seletores de mês/ano e LED SVG da agenda em components/date_input.py. A agenda preserva seus eventos, estado e textos.
- Um único diálogo do atendimento mantém alvo (campo/grupo/linha), mês em navegação e abertura. Abrir inicia no valor atual ou hoje; cancelar não altera dados. Selecionar/limpar usa clinical_field/clinical_line_field existentes, marca edição e fecha. Fechar devolve foco ao campo original.
- Validar alvo por lista permitida, identidade estável da linha e consulta ativa. Bloquear alteração durante salvamento ou reconciliação; limpar calendário ao sair, limpar sessão ou abrir outra consulta. Não realizar HTTP ao navegar ou selecionar. Datas futuras continuam sujeitas à validação existente ao salvar/finalizar.
- Reutilizar cores, tartaruga e borda SVG com deslocamento contínuo no sentido horário. Em movimento reduzido, desacelerar como na agenda. Testar seleção/limpeza/cancelamento, ano bissexto, isolamento entre campos e agenda, LED em movimento e mobile.

## Confirmação das ações de gravação
- Emitir toast de sucesso no canto inferior esquerdo somente após resposta confirmada do backend, inclusive na reconciliação. Preservar também clinic_message existente. Falha, conflito ou resposta de sessão/consulta antiga não emitem sucesso. Texto sem dados clínicos, com ícone de sucesso, cores verdes, fechamento manual e duração de 5 segundos.

## Retorno à agenda e acabamento dos cards
- Após finalização confirmada (resposta normal ou reconciliação), retornar a /?secao=horarios, selecionar o dia agendado em America/Sao_Paulo, reiniciar paginação e recarregar pela entrada existente. O dia agendado é derivado de agendada_para ao abrir a consulta, separado da data clínica.
- Atualizar estado/label do card em cache somente após confirmação, remover da lista de pendências e invalidar leituras antigas; a leitura autenticada ao retornar é autoritativa. Falhas ou sessão/consulta antiga não redirecionam nem declaram conclusão.
- Reutilizar o card médico em Consultas e Horários, preservando dados autorizados e ações. Faixa lateral, badge e bordas usam verdes nos estados agendada/em atendimento/finalizada, com texto do estado além da cor.
- Compartilhar contorno SVG decorativo entre calendário, agenda do dia e moldura da foto. Deslocamento negativo do tracejado mantém circulação no sentido horário, sem girar foto/conteúdo, sem interceptar cliques. Movimento reduzido desacelera o LED. Sem foto, a moldura envolve o fallback existente; consentimento revogado mantém dados privados ocultos.

## Halo móvel dos LEDs
- Aplicar drop-shadow em camadas ao traço SVG tracejado, usando a mesma cor verde do LED. A sombra acompanha exclusivamente o segmento animado nos calendários, agenda do dia, molduras dos pets e chat. Não aplicar sombra verde fixa à caixa completa.
- Permitir o halo externo sem recorte: calendário mantém rolagem no layout interno; chat mantém mensagens/histórico roláveis com cantos arredondados nos painéis internos. Velocidade, direção, foco e cliques permanecem iguais.

## Preferência de tema no atendimento
- Escopo somente atendimento, histórico, calendário clínico, confirmação de saída e toast clínico. Reutilizar data-vt-theme e preferences.js existentes, sem criar preferência paralela ou alterar agenda/chat.
- Centralizar superfícies, campos, bordas, texto, verde de ação, vidro e overlay do wallpaper em tokens --vet-* com variantes claras/escuras. Remover cores claras fixas nesses componentes e manter os portais sincronizados sem recarregar nem apagar rascunho.
- Toast usa classe própria e variáveis CSS para atualizar mesmo enquanto visível. Manter layout, mascotes, LEDs, foco, estados desabilitados e movimento reduzido. Verificar contraste, troca com painéis abertos, preferência persistida e mobile com dados sintéticos.

## Histórico compartilhado e botões arredondados
- Parametrizar o diálogo existente com pet, texto do acionador, id do botão e rótulo de retorno. Os cards reutilizam seu carregamento, erro/nova tentativa, vazio, tema e tartaruga; retirar a renderização inline antiga. Nova tentativa conserva o pet do card, independentemente da consulta aberta anteriormente. Fechar restaura o foco ao acionador correto.
- Arredondar comandos globalmente por CSS com raio pill, incluindo botões Radix, nativos e links com aparência de botão. Preservar switches, checkboxes, rádios e mascote com suas formas próprias. A regra muda apenas os cantos e mantém handlers, foco e estados.

## Risks / Trade-offs
Tema escuro global → tokens locais por tema, incluindo variáveis Radix dos portais. Dados clínicos → validação com fixture sintética isolada. Botões de cor principal → texto branco em peso forte e foco explícito.

## Migration Plan
Sem migração. Reverter apenas os arquivos de apresentação e seus artefatos se necessário.

## Percurso do LED do chat em oito
- Substituir o retângulo do LED do chat por um único path SVG contínuo que alterna duas voltas: cabeçalho/banner e mensagens/rodapé. O trecho compartilhado acompanha exatamente a divisória inferior do banner, sem diagonais sobre texto ou vídeo.
- Recalcular o caminho com ResizeObserver no painel e banner, usando dimensões locais sem transformações da animação de abertura. Manter um segmento luminoso com halo, ciclo de 6s/12s em movimento reduzido, sem interceptar cliques nem movimentar conteúdo. Fechado não anima; calendários, agenda e fotos mantêm seus percursos.

## Favicon global do mascote
- Configurar link icon no head global do App para todas as páginas. Reutilizar o arquivo mascote_logo.png existente em um SVG autocontido, com enquadramento que inclui toda a tartaruga visível no arquivo original, incluindo cabeça e braços, sem alterar o original.
- Usar também link PNG explícito para mascote_logo.png como fallback; preservar os pixels do arquivo original. URL explícita versionada evita reutilizar o ícone Reflex em cache. Sem bibliotecas/dependências novas.
- Verificar documento compilado global, acesso aos assets e renderização do SVG em 16px/32px.

## Hierarquia dos títulos de campos
- Padronizar rótulos do atendimento em Nunito 18px, peso 800, linha 1.4 e cor temática. Aplicar aos dados principais, registros adicionados, seletores e catálogo. Títulos de seção ficam em 22px e títulos dos grupos em 20px para manter hierarquia.
- O seletor Doença também usa label associado ao acionador, mantendo a mesma apresentação e associação acessível dos demais campos.
