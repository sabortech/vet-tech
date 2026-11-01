## Context

Ver motivação em proposal.md. A investigação local confirmou:

- `vacina` possui `data_aplicacao` e `data_prox_dose` opcionais; finalizar atendimento grava os dois campos. Um rascunho não é publicação de vacina.
- O endpoint canônico consulta a próxima dose com data maior ou igual ao dia atual em America/Sao_Paulo, ordena ascendente e retorna uma linha. A Lambda mescla próximas, ultrapassadas e recentes por ID.
- `project_pet` seleciona novamente doses de hoje ou futuras e monta `proxima_vacina`; os dois cartões consomem nome e data.
- Quando não há dose elegível, a projeção retorna `{}`, embora o componente consulte chaves de nome/data. Esse descompasso é um ponto de investigação do estado vazio, não uma causa confirmada da ausência com registro válido.
- Existem duas fontes locais para `tutor/dashboard`. Testes atuais exercitam a fonte em `clinical/tutor/dashboard_GET.xs`; a versão efetivamente publicada não foi comparada nesta análise.
- A validação clínica exige strings `AAAA-MM-DD`; campos nativos `type=date` enviam esse valor, mas sua aparência depende do navegador/sistema operacional. ISO não é o formato americano `MM/DD/AAAA`.
- Cadastro de pet usa `date` para nascimento; agendamento usa `timestamp` e fuso America/Sao_Paulo. Não devem receber o mesmo tratamento de conversão.
- A ordenação de atividade recente tenta interpretar datas já formatadas em `DD/MM/AAAA` com um parser ISO. Reprodução sintética apresentou vacina de 01/01/2026 antes de consulta de 31/10/2026.
- Medicamentos e doenças não são consultados/projetados pelo resumo; exames realizados não entram na atividade e consultas legadas sem status não entram na última consulta. São achados de cobertura a classificar, não autorização para novos cartões.

## Goals / Non-Goals

**Objetivo:** restabelecer a próxima vacina já prevista no contrato existente e demonstrar sua consistência no percurso registro → resposta → projeção → cartão.

**Fora do escopo:** campos cadastrais adicionais, edição de vacina, cálculo de calendário vacinal, notificações e reformulação do Dashboard. Não preencher próxima dose por intervalo presumido a partir da aplicação.

## Decisions

1. Preservar a regra atual: próxima dose é a menor `data_prox_dose` válida a partir de hoje. Uma dose passada permanece nos itens de acompanhamento; aplicação sem próxima dose não constitui evento futuro. Evita alterar comportamento clínico sob o rótulo de correção.
2. Comparar o mesmo pet e registro no histórico e na resposta autenticada antes de escolher o conserto. Se houver próxima dose válida no histórico e não na API, corrigir seleção/contrato/publicação; se houver na API e não na projeção, corrigir normalização; se houver na projeção e não no cartão, corrigir renderização. Usar regressão que reproduza o descompasso encontrado.
3. Tratar explicitamente ausência de próxima dose e falha de leitura. Nunca apresentar falha como ausência confirmada nem deixar o cartão vazio por acessar chave ausente.
4. Manter uma requisição de resumo por pet, sem fallback de histórico completo e sem ler dados de outro tutor. Reutilizar os componentes e estado existentes.
5. Separar valor técnico e rótulo: nascimento, aplicação, próxima dose e demais datas civis circulam como `AAAA-MM-DD`, sem converter para instante UTC nem deslocar o dia. Na interface, mostrar `DD/MM/AAAA`. Instantes de agenda e auditoria mantêm timestamp em milissegundos no contrato atual e são exibidos como `DD/MM/AAAA HH:mm` em America/Sao_Paulo. Confirmar a representação real de cada campo na resposta Xano antes de normalizar; não presumir que todo número seja uma data civil.
6. Nunca adivinhar se `03/04/2026` é março ou abril: a entrada brasileira, quando textual, deve ser convertida explicitamente para ISO; a API clínica mantém validação estrita. Campos nativos preservam valor ISO e devem ter rótulos/instruções claros. Verificar a aparência em navegador pt-BR e en-US; `lang=pt-BR` sozinho não garante o formato visual do controle nativo. Se houver necessidade de substituir um controle para apresentação uniforme, manter acessibilidade e as tecnologias atuais, sem biblioteca nova automaticamente.
7. Ordenar e comparar os valores técnicos antes de formatar para exibição. Reutilizar formatação compartilhada onde apropriado, sem criar dependência circular entre o estado de autenticação e o Dashboard. Não migrar nem regravar dados históricos para mudar a apresentação.

## Risks / Trade-offs

- [Causa ainda não reproduzida] → conferir se o registro tem próxima dose, se foi finalizado e qual resposta chega ao cliente; registrar evidência sanitizada antes de editar.
- [Fontes e publicação divergentes] → identificar a fonte efetiva e comparar o endpoint publicado; não fazer push integral do workspace.
- [Diferença de dia/fuso] → verificar ontem, hoje e amanhã no mesmo fuso, incluindo a transição de dia.
- [Dados legados ou formato inválido] → testar as representações efetivamente recebidas e não fabricar data.
- [Troca de pet ou sessão durante leitura] → preservar descarte por geração e os testes de isolamento existentes.

## Verificação de aceitação

- Próxima dose hoje e futura exibem nome e dd/mm/aaaa nos escopos geral e individual.
- Entre duas próximas doses, a menor data vence, mesmo com muitas aplicações recentes no histórico.
- Aplicação sem próxima dose mostra ausência legível; data ultrapassada mantém seu acompanhamento sem se tornar evento futuro.
- Falha de rede tem feedback e nova tentativa; não aparenta ausência de vacina.
- Outro tutor não recebe os dados; resposta antiga não preenche o pet atual.
- `2026-04-03` é exibido como `03/04/2026` e continua sendo enviado como `2026-04-03`, sem inversão de dia/mês.
- Datas civis conservam o mesmo dia em navegadores com fusos distintos; instantes são convertidos explicitamente para o fuso de negócio.
- Verificar ano bissexto, data inexistente, valor ausente, limite de dia e ordenação recente entre meses/anos.
- Comparar apresentação e payload dos controles no cadastro e no atendimento em pt-BR e en-US; registrar limites do calendário nativo e a solução adotada.

## Fontes técnicas

- MDN: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/date — valor do campo nativo é ISO, aparência depende da localidade.
- Xano: https://www.xano.com/learn/xano-timestamps/ — timestamps representam milissegundos desde a época Unix; apresentação pode variar por fuso.

## Migration Plan

Não requer migração de dados nem schema. Se o defeito for no backend publicado, preparar alteração apenas do endpoint responsável e verificar o contrato no ambiente confirmado; código local compilado não comprova publicação. Reversão restaura a versão anterior do arquivo/endpoint sem alterar registros de vacina.
