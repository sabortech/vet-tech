# Design

## Context

Ver motivação em `proposal.md`. A rota `/dashboard` compõe `tutor_dashboard_page`; `_overview_pet` hoje usa foto circular de 88 px e dados em linhas, enquanto `dashboard_content` lista os cards em uma pilha. `_individual_pet` possui uma visão detalhada separada. O filtro usa `dashboard_scope`, independente do pet clínico ativo. A arquitetura e os contratos atuais estão descritos em `docs/architecture.md` e `openspec/specs/tutor-dashboard/spec.md`.

O arquivo `assets/fundopets.jpeg` foi inspecionado: contém textura bege, patinhas e silhuetas de animais. Há assets de tartarugas no projeto e um mascote global existente. A imagem enviada pelo usuário é a referência de composição; Jessy é o modelo estrutural para todos os cards, mesmo que os demais cards do protótipo estejam simplificados.

## Goals / Non-Goals

**Goals:** aproximar proporções, cores e hierarquia visual da referência; manter apresentação consistente e acessível com conteúdo variável e dados reais.

**Non-Goals:** redesenhar sidebar e cabeçalho globais, alterar contratos Xano ou recalcular regras clínicas. Não reproduzir sobreposição acidental de cartões, textos em inglês nem dados fictícios do protótipo.

Revisão solicitada: a visão individual de qualquer pet reúne identificação,
indicadores, evento, acompanhamentos, atividade e ações em um único contêiner
com perímetro LED. Os blocos internos tornam-se seções e tiles sem cartões
independentes; o LED usa os tokens do estado da próxima dose já calculado,
assim como a sombra do cartão individual. Conforme revisão do tutor, sem data
o LED fica apagado e a sombra usa o tom neutro da barra. A visão Todos os pets
mantém sua sombra anterior e o contorno apagado sem data.

## Decisions

1. **Aproveitar componentes existentes.** Remodelar `_overview_pet` e a composição da listagem em `vet_tech/components/dashboard.py`, reutilizando eventos de escopo, agendamento e navegação clínica. Preservar a visão individual detalhada e aplicar o fundo ao contêiner principal de ambos os escopos. A alternativa de criar outra página duplicaria autenticação e ações.

2. **Card completo em fluxo normal.** Foto com aproximadamente 150 × 185 px no desktop, `object-fit: cover`, cantos de 8–10 px; área lateral flexível com nome em aproximadamente 30–34 px, três indicadores e faixa de vacinas. Acompanhamento e rodapé ocupam a largura completa abaixo. Usar borda clara, sombra discreta e padding de aproximadamente 8–12 px; ajustar as medidas pela comparação visual. Evitar posicionamento absoluto de conteúdo e alturas fixas: o protótipo contém sobreposição que não deve ocorrer com dados reais. Uma única estrutura serve todos os pets.

3. **Grade depende da área útil.** Usar grade com duas colunas quando cada card puder ocupar cerca de 470–500 px; abaixo disso, uma coluna. A sidebar altera a área útil, portanto não depender apenas da largura da janela. No celular, reorganizar foto, identificação e indicadores e permitir quebra dos botões. Validar em 1366, 1440, 768 e 390 px com menu expandido e recolhido.

4. **Fundo local e contínuo.** Aplicar URL `/fundopets.jpeg` apenas ao contêiner principal, com base bege, tamanho inicial `cover`, posição central superior e altura mínima preenchendo a área visível. Conferir captura longa; ajustar tamanho/repetição se necessário para preservar estampas sem distorção ou cortes abruptos. Usar classes prefixadas de Dashboard em `assets/vet_tech.css`, sem alterar tokens globais de outras telas. No tema escuro, manter textura visível com sobreposição tonal e superfícies/contraste apropriados.

5. **Faixa ilustrativa sem métrica clínica.** A projeção atual não fornece denominador de doses nem percentual de cobertura. Usar faixa verde como decoração, sem `progressbar`, porcentagens ou posição da tartaruga associada a um score; texto explícito descreve a próxima dose ou ausência. Reutilizar um asset existente de tartaruga que se mantenha reconhecível em tamanho pequeno, com alternativa vazia e sem foco. Não acrescentar uma segunda tartaruga grande fixa: manter o mascote global existente para evitar duplicação e bloqueio dos botões.

6. **Sem novas leituras.** Reutilizar `mensagem_acompanhamento`, `acompanhamentos`, indicação de prévia limitada e `proximo_evento`. Preservar os cálculos de idade, datas e peso existentes. A ausência de próxima dose não equivale a cuidados em dia; uma data ultrapassada não comprova que o cuidado deixou de ocorrer. Manter limites, autorização e comportamento de erro existentes.

## Risks / Trade-offs

- [Quatro botões e três indicadores em cards estreitos] → labels curtos em português e quebra responsiva, sem ocultar ações.
- [Texto clínico maior que o protótipo] → altura automática e linhas da grade dimensionadas pelo conteúdo, com ações legíveis.
- [Imagem externa de pet indisponível] → verificar fallback para falha de carregamento além da URL ausente.
- [Fidelidade visual versus tema escuro e legibilidade] → preservar textura e hierarquia, adaptando superfícies e contraste ao tema existente.
- [Interferência do mascote/chat] → verificar camadas e área de toque com widgets abertos e fechados; correções restritas ao Dashboard se necessárias.

## Migration Plan

Não há migração de dados. Antes de implementar, ler `reflex-docs` e confirmar disponibilidade de `setup-python-env` e `reflex-process-management`; usar a skill de processos para compilação e execução. Entregar componentes e CSS juntos, executar regressões existentes do Dashboard/datas e registrar evidências visuais com dados sintéticos. Reversão consiste em restaurar somente as alterações de apresentação desta mudança; o asset e os contratos de dados permanecem válidos.


## Evolução: LED de prazo autorizado

O indicador passa a ter significado temporal, sem representar cobertura vacinal. A projeção adiciona `indicador_vacina` com estado, texto, nome e data. Reutiliza a próxima dose futura já escolhida; sem futura, seleciona a data prevista ultrapassada mais recente. Os limites de sete dias são regra de apresentação solicitada, não recomendação de calendário clínico. O dia de referência usa o fuso existente America/Sao_Paulo no carregamento do resumo. A faixa inteira vira botão com o handler clínico existente; decorações permanecem fora da árvore acessível. As decisões anteriores sobre faixa exclusivamente decorativa são substituídas por esta evolução. Não criar notificações nem temporizadores ou chamadas extras ao backend.


## Evolução: carregamento sem bloquear a sessão

Inspeção confirmou `load_dashboard` e `set_dashboard_scope` aguardando todo o lote HTTP em eventos comuns; o transporte cria um AsyncClient por request e o grupo clínico pode aguardar Retry-After em três tentativas. Separar o início rápido do carregamento de um worker background, com snapshots sob lock, HTTP fora do lock e commit sob lock validando sessão/token/geração. Deduplicar eventos do mesmo escopo enquanto carregam e workers da mesma geração. Preservar quatro chamadas concorrentes e nova leitura em entrada/escopo, sem introduzir cache clínico. Reutilizar um cliente HTTP apenas dentro do lote via ContextVar/async context manager, com headers fornecidos a cada chamada e encerramento garantido; demais consumidores preservam seu ciclo atual. Os cards usam stretch na grade e flex column com rodapé empurrado à base; a altura continua determinada pelo conteúdo mais alto da linha. Não migrar o servidor do usuário entre modos nem atribuir a lentidão total ao frontend sem medições do backend real.

## Evolução: LED horário do card

O contorno reutiliza as variáveis de cor do indicador. Dois rects SVG normalizados com pathLength 100 formam segmento e halo; stroke-dashoffset negativo move o segmento no sentido horário. A animação usa somente CSS, sem filtros de blur, temporizadores JavaScript ou consultas adicionais. SVG absoluto com pointer-events none não altera altura nem intercepta ações. Sem data, fica oculto; prefers-reduced-motion desativa movimento.


## Evolução: primeiro card e retorno ao Dashboard

A versão anterior só fazia commit após gather de todos os pets e ocultava a lista durante qualquer leitura. O worker agora usa as_completed com commits sob lock por resumo, sempre ordenados pela lista própria e protegidos por sessão/token/geração/membership. A UI mostra resumos disponíveis junto do status de carregamento. O cliente e as tarefas pendentes continuam sendo encerrados/cancelados de modo controlado em erro ou descarte.

Resultados de lotes completos recebem timestamps monotônicos privados por pet, válidos por 15 segundos, com dia civil local e IDs próprios. Esses campos são limpos no logout e ações clínicas/agendamento. Não há persistência ou cache entre sessões. Mudança de lista/dia, expiração, erro ou botão Atualizar forçam novas leituras; seleção de escopo pode reutilizar resumos válidos. Essa decisão substitui a ausência de cache dentro da sessão descrita na primeira otimização. Não alterar a política global de retries nem atribuir os tempos sintéticos à API real.


## Evolução: cabeçalho do Dashboard
Usar a hierarquia de Consultas: título, descrição e botão sólido no cabeçalho; abaixo, barra com superfície do tema, borda e raio de 18 px contendo o filtro Mostrar e a ação condicional de agendamento. Em telas estreitas permitir quebra e ocupar a largura disponível. Validar compilação com escrita e regressões existentes.
