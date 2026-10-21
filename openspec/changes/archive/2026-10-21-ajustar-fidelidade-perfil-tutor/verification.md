# Verificação do perfil

## Implementação e verificações

- Mantidos controles externos de 48 px, grade com gap de 16 px e upload de 148 px.
  O input interno Radix mede 46 px dentro do controle com bordas de 48 px.
- Data nativa mantém calendário e payload ISO. Corrigidos segmentos invisíveis no
  foco e o posicionamento do indicador; foco visual centralizado no controle.
- Placeholder vazio/hover/foco observado em `rgb(98, 107, 102)`; seleção em
  `rgb(26, 54, 41)`. Contraste calculado entre `#626b66` e `#eef0f2`: 4,82:1.
- Preview local verificado por seleção, troca e limpeza após cadastro. Nenhuma
  chamada Xano ocorreu durante seleção. Upload via multipart contém `foto` e
  `data_nasc=2026-10-05`; cadastro sem foto usa JSON sem esse campo.
- Preview também trata drop e rejeita imagem acima de 5 MiB localmente; essa
  extensão foi conferida no código, sem ensaio automatizado de drag-and-drop.
- Listagem com URL de foto válida e fallback sem foto, atualização e logout
  exercitados com dados sintéticos. URLs privadas continuam filtradas pelo estado.
- Sidebar alterna nos dois sentidos; ícone, nome e aria-expanded verificados em
  1920, 1366 e 1024 px; sete itens preservam `title`. Preferência e estado visual
  persistiram após reload e navegação para `/login` na sessão autenticada.
- No rail, os centros dos sete ícones mediram x=38 px; marca tem 28 px e sidebar
  tem 76 px. Estado expandido tem 260 px.
- Corrigido botão móvel coberto pelo drawer: permanece visível acima do backdrop,
  no canto superior direito quando aberto; abertura e fechamento pelo controle
  passaram na execução final.
- Mascote de 200–220 px fica depois da lista, junto à borda inferior em duas
  colunas e oculto quando empilha. Dados de teste com lista maior também foram
  capturados, sem sobreposição.

## Matriz de largura e estado

Chromium headless, aplicação Reflex em produção com backend HTTP fictício local.
Em 768 px aplica-se desktop, pois o breakpoint móvel é estritamente abaixo disso.

| Viewport | Estado | Cartões | Mascote | Overflow horizontal |
|---|---|---|---|---|
| 1920×1080 | Aberta / rail | Duas colunas | Visível, base em y=1080 | Ausente |
| 1366×768 | Aberta | Duas colunas após calibração do container para 1000 px internos | Visível, base em y=768 | Ausente |
| 1366×768 | Rail | Duas colunas | Visível, base em y=768 | Ausente |
| 1024×768 | Aberta / rail | Empilhados | Oculto | Ausente |
| 768×1024 | Aberta / rail | Empilhados | Oculto | Ausente |
| 390×844 | Drawer aberto / fechado | Empilhados, campos em coluna | Oculto | Ausente |

Em 1920×1080 a altura do documento foi 1080 px, sem rolagem vertical adicional.
Nas larguras menores, a rolagem vertical corresponde ao conteúdo empilhado e ao
tamanho da lista. Medições em `evidence/profile-measurements.json`; capturas de
viewport em `evidence/vet-tech-<largura>-<estado>.png`, com True indicando aberta.
As primeiras capturas de página inteira exibiram artefato de posição sticky do
Chromium; foram substituídas por capturas da viewport.

## Comandos e limites

- `python -m unittest discover -s tests/unit`: 36 testes passaram.
- `reflex compile --dry`: passou.
- `openspec validate --all --strict`: 8 itens passaram.
- `git diff --check`: passou.
- Testes de navegador usaram Playwright instalado somente em `/tmp`; não foi
  adicionada dependência ao projeto. Nenhum dado foi gravado no Xano.
- Na execução anterior, o foco da data recebeu CSS diretamente no navegador.
  Na continuação abaixo, uma nova instância compilou os arquivos atuais; a
  instância do usuário não foi reiniciada.

Na execução inicial, a imagem original do protótipo não estava disponível.
Naquela etapa não houve comparação direta com ela, aprovação visual do usuário
nem acesso a ferramenta de navegador integrado. Naquela etapa, as tarefas que exigiam expressamente esse navegador
(1.2, 4.2 e 4.3) permaneceram abertas, apesar da cobertura headless registrada.
Arquivamento não realizado.

## Revalidação em 2026-10-20

Nova instância Reflex em produção na porta 3011 com mock Xano em localhost:8099,
sem acesso a backend real. Os testes funcionais passaram novamente para seleção,
troca/limpeza do preview, ausência de envio na seleção, multipart com foto e data
ISO, JSON sem foto, atualização, persistência da sidebar e logout. O teste dos
controles confirmou placeholders vazios/hover/foco em rgb(98,107,102), seleção
em rgb(26,54,41), ícones e atributos acessíveis nos dois estados.

Capturas finais da viewport e medições renovadas para 1920×1080, 1366×768,
1024×768, 768×1024 e 390×844, com os dois estados aplicáveis. Todas foram
inspecionadas visualmente: upload com 148 px, borda verde tracejada e cantos
arredondados; nenhum overflow horizontal; sidebar íntegra e ícones alinhados;
mascote junto à base nos layouts de duas colunas, sem sobreposição. Em 1920×1080
a altura do documento foi 1080 px. Resultados na matriz existente permanecem
válidos. A lista sintética foi ampliada pelos cadastros funcionais.

Limite preservado: esta sessão dispõe de Chromium headless e inspeção das
capturas, mas não de navegador integrado nem da referência original. Assim,
1.2, 4.2 e 4.3 não foram marcadas como integralmente verificadas. Não houve
aprovação visual ou arquivamento.

## Comparação com a referência recebida em 2026-10-21

O usuário forneceu a imagem original, agora preservada em
[`evidence/prototype-reference.jpeg`](evidence/prototype-reference.jpeg).
A referência contém a interface do navegador e a barra do sistema; suas
dimensões totais não equivalem à viewport CSS. A comparação abaixo foi feita
com as capturas de viewport já existentes e inspecionadas nesta sessão; não
representa uma nova execução dos fluxos nem aprovação visual do usuário.

| Elemento | Comparação | Pendência |
|---|---|---|
| Upload | Borda verde tracejada, cantos arredondados, câmera central e botão abaixo seguem a composição da referência; medição existente de 148 px | Conferência no meio de inspeção definido pela tarefa |
| Campos | Grade com duas colunas em desktop e identificação da data reproduzem a composição; textos atuais foram preservados conforme a spec | Não substituir placeholders ou controles por textos/controles desenhados no protótipo |
| Sidebar | Mesma ordem de opções, destaque branco em Meus Pets e marca verde/branca; a referência não mostra o rail recolhido | Rail permanece avaliado pelos critérios da spec e capturas existentes |
| Cartões em desktop | A referência mostra cadastro e lista lado a lado com sidebar aberta; a captura atual de 1366 px empilha os cartões | Ajustar a quebra pela largura disponível e revalidar as cinco larguras |
| Mascote | A pose com os dois braços erguidos corresponde à referência | Na captura de 1366 px com sidebar aberta ela fica oculta devido ao empilhamento; corrigir junto da quebra de layout |
| Lista de pets | Avatar circular, nome e metadados seguem a referência; fixtures têm conteúdo diferente | Não usar nomes/fotos do protótipo como dados reais do sistema |

A regra atual `@container profile (max-width: 1099px)` considera a largura
interna após o padding. Na captura de 1366 px com sidebar de 260 px, esse
container fica abaixo do limite mesmo quando a composição da referência
comportaria os dois cartões. Essa divergência exige ajuste e nova verificação;
não declarar fidelidade concluída somente porque não há overflow horizontal.

A ausência da referência foi resolvida. O navegador integrado continua
indisponível; foi solicitada autorização para substituir essa exigência por
Chromium e inspeção das capturas. As tarefas 1.2, 4.2 e 4.3 continuam abertas,
sem arquivamento ou alteração silenciosa dos critérios de aceite.

## Resultado final após autorização do Chromium (2026-10-21)

O usuário autorizou usar o meio de inspeção mais adequado, resolvendo a
restrição de navegador integrado. Foram usados Chromium via Playwright e
inspeção visual das dez capturas, com a referência original disponível.
Não foi solicitada instalação de dependência permanente nem usado Xano real.

Ajuste realizado: o container de conteúdo exclui os paddings. Seu limite de
empilhamento passou de 1100 para 1000 px internos, mantendo o limite de
viewport de 1100 px. Em 1366 px com sidebar aberta, os cartões medem cerca de
567,5 e 435,1 px, começam na mesma altura e mantêm campos em duas colunas.
A mascote fica centralizada sob a lista, com a base em y=768 e sem sobreposição.
Isso corrige a divergência com a composição desktop da referência.

A matriz no início deste documento e `evidence/profile-measurements.json`
representam a execução final com três pets sintéticos. As dez capturas
`vet-tech-<largura>-<estado>.png` foram renovadas e inspecionadas. Nos dez
estados, a largura do documento coincide com a viewport e o upload mede
148 px. Em 1920×1080 e 1366×768, os dois estados desktop mantêm duas colunas
e a altura do documento coincide com a viewport, sem scroll vertical adicional.
Em 1024, 768 e 390 px os cartões empilham, com rolagem correspondente ao
conteúdo. Em 768 px com rail os três pets cabem na altura de 1024 px.

Verificações funcionais e de apresentação concluídas:

- Upload: altura 148 px, borda tracejada de 2 px e raio de 12 px. Seleção,
  troca, preview, limpeza e ausência de envio antes do cadastro passaram.
- O teste instrumentou `URL.createObjectURL` e `URL.revokeObjectURL`: a URL
  anterior é revogada na troca e a última é revogada ao limpar após cadastro.
- Cadastro com foto enviou multipart com campo `foto` e data ISO; cadastro
  sem foto enviou JSON sem campo de foto. Atualização da lista e logout passaram.
- Espécie/raça, placeholders vazio/hover/foco/preenchido e data nativa passaram
  com o CSS compilado, sem injetar estilos de correção no navegador.
- Sidebar: abrir/recolher nos dois sentidos, ícone/aria do toggle, títulos dos
  sete itens, persistência após reload/navegação e drawer móvel passaram.
- No rail, os sete ícones continuam com eixo central em x=38 px. Capturas
  confirmam centralização do pill e ausência de espaço residual dos rótulos.
- Alinhamento superior dos cartões, centralização da mascote e ausência de
  sobreposição foram conferidos visualmente e por medições.
- A execução anterior com seis pets também passou: em 1366 px a altura passou
  para 777 px para acomodar a lista e a mascote; em 1920 px permaneceu 1080 px.
  Registros em `profile-long-list-measurements.json` e capturas com sufixo
  `-long-list.png`. A mascote permanece no fluxo, depois do cartão.

A comparação validou composição, upload, campos, cartões, sidebar e pose da
mascote. Textos, opções, dados, ícones e tokens existentes foram preservados
conforme a spec; a imagem gerada de referência não substitui os contratos
funcionais nem determina dados reais de pets. Não se declara igualdade de
pixels entre a imagem de referência e o navegador.

Verificações locais: 39 testes unitários passaram; `reflex compile --dry`
passou; `openspec validate ajustar-fidelidade-perfil-tutor --strict` passou;
`git diff --check` passou. As tarefas 1.2, 4.3 e, por último, 4.2 foram
concluídas. Total: 18/18. A change não foi arquivada; autorização do meio de
teste não foi tratada como aprovação visual final para arquivamento.

## Correção da conexão da instância do usuário (2026-10-21)

Após os testes visuais, a instância original na porta 3000 estava servindo
arquivos gerados com destino de eventos na porta 3011, usada pela instância
temporária já encerrada. O diagnóstico com Chromium confirmou tentativas de
WebSocket em `127.0.0.1:3011` e aviso de falha de conexão; por isso o evento de
login não chegava ao backend. O processo original também estava sem a variável
obrigatória `XANO_API_BASE_URL`.

Foi criado `.env` local ignorado pelo Git, contendo somente a origem do Xano
configurado, sem token administrativo. O processo que escutava a porta 3000
foi interrompido e a aplicação recompilada/reiniciada em produção com frontend
e backend na porta única 3000 e ambiente carregado. A instância permanece ativa.

A verificação final com Chromium confirmou WebSocket na porta 3000 e retorno
real `Credenciais inválidas.` do Xano após submissão de e-mail fictício
`@example.invalid` e senha de teste inválida. Não foi utilizada conta real e
não se declara autenticação bem-sucedida de usuário. Nenhum endpoint, senha
ou registro do Xano foi alterado. Os testes futuros em outra porta devem usar
saída de build isolada ou restaurar a compilação/instância principal ao final.

## Aprovação e arquivamento (2026-10-21)

O usuário aprovou a coerência do resultado e autorizou explicitamente o
arquivamento. As 18 tarefas estão concluídas. Antes de arquivar, os deltas de
`application-navigation` e `tutor-profile-presentation` foram sincronizados
com as specs principais, preservando os requisitos e cenários não alterados.
As capturas e demais evidências permanecem junto dos artefatos arquivados.
