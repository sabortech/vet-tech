# Verificação da implementação

## Estado entregue

Publicadas no Xano as duas tabelas internas, quatro funções Notifications e os dois endpoints de cadastro, por importações parciais transacionais sem registros, exclusões, envs ou contratação de serviços. Nome, perfil e destinatário vêm da identidade criada e da reserva de e-mail. O evento é gravado dentro da transação; `util.post_process` envia depois da resposta. Falha de envio não altera `{success:true}` nem impede login.

A implementação está ativa para novos cadastros de tutor e veterinário. Login, Google, recuperação de senha e Quick Start continuam independentes. O endpoint demonstrativo Quick Start de boas-vindas a `user` já existia e não foi alterado ou reutilizado. Não há rota pública nova de envio.

## Arte e renderização

- Imagem original: `assets/mascote/clinicturtle.jpeg`, sem edição, publicada somente como imagem no repositório `7offdvx/vet-tech-assets` autorizado para os e-mails. Commit da arte `0d062f022b868b62338b6f82307ba6469a4f0994`; GET anônimo 200, MIME JPEG e mesmos bytes, conforme `evidence/image-hosting.json`.
- HTML/TXT/JSON canônicos próprios; nenhuma finalidade de senha foi alterada. Títulos e agradecimento em português, instruções distintas por perfil, nome escapado, quatro imagens HTTPS sem anexos, desenvolvedores sem sombras e copyright aprovado.
- Quatro prévias de 390/900 px, duas por perfil, com fotos carregadas, proporção clínica preservada e sem overflow. Também capturadas versões sem imagens. Evidência: `evidence/email/visual-results.json` e PNGs adjacentes.
- Sincronização do renderizador e paridade entre Python/JavaScript aprovadas. Não há botão localhost ou URL pública fictícia.

## Testes automatizados

- **84 testes Python passaram**, incluindo template de boas-vindas, template de senha, autenticação, login Google e Configurações dos dois perfis. Não houve alteração em componentes Reflex; não foi necessário reiniciar o servidor.
- **13 testes nativos Xano passaram** na versão final: resolução por perfil com IDs coincidentes, evento ausente, perfil inválido, reserva divergente, aceitação, 401, 429, 500, 2xx sem identificador e registro dos resultados. Neles, provedor e banco são simulados; não comprovam entrega real. Evidência: `evidence/native-unit-tests.json`.
- **Oito documentos XanoScript válidos**: duas tabelas, quatro funções e dois endpoints. Metadados remotos conferidos: índices únicos, histórico desativado, resposta de cadastro preservada e pós-processamento fora da transação. Evidência: `evidence/publication-verification.json`.
- **Integração real com contas sintéticas dos dois perfis passou**: criação da conta/evento, login após rejeição do destinatário reservado, cadastro duplicado rejeitado, repetição do evento ignorada e um vencedor em duas reservas concorrentes. A disputa usa clone privado do orquestrador com transporte simulado; os demais acessos ao banco são reais. Cadastros inválidos de tutor e veterinário não criaram identidades. Nenhum e-mail real enviado nesse ensaio. Evidência: `evidence/live-integration.json`.
- **Rollback nativo passou**: clones privados dos dois endpoints forçaram erro após inserir identidade/evento dentro da transação. A identidade não permaneceu e não houve disparo. Evidência: `evidence/native-rollback.json`.
- Todas as contas sintéticas e funções de diagnóstico foram removidas. A primeira execução encontrou HTTP 429 na limpeza administrativa; a limpeza foi recuperada e verificada em `evidence/cleanup-recovery.json`. O ensaio foi então ajustado com ritmo administrativo e checkpoint privado e repetido integralmente com sucesso; nenhum resultado incompleto foi promovido a sucesso.

## Entrega real das prévias

Enviadas duas mensagens pela função interna publicada para a caixa `vet.tech.impact@gmail.com`, já autorizada pelo usuário, com nomes fictícios Ana Silva e Alex Oliveira. Nenhuma conta real foi criada ou modificada para esse envio. O Brevo confirmou `delivered` para os dois IDs, conforme `evidence/real-delivery-previews.json`. Eventos de abertura também foram observados, mas não equivalem à aprovação visual pelo usuário. Entrega do provedor não é promessa universal de caixa de entrada.

## Pendente

A tarefa **4.4 permanece aberta** para confirmar o cadastro real completo com novos endereços explicitamente indicados pelo usuário — um para tutor e outro para veterinário — e a revisão visual na caixa real. A pergunta foi enviada durante a implementação; não houve indicação desses endereços até esta atualização. Os cadastros nativos com `.invalid` e a entrega das prévias foram comprovados separadamente, sem afirmar uma validação end-to-end real que ainda não aconteceu. Nenhuma credencial foi registrada na evidência.

## Operação e rollback

Ver `docs/welcome-email.md`. O remetente guarda a chave apenas no Xano; a validação de `.invalid` impede chamada ao provedor para fixtures. O resultado de timeout/erro sem confirmação permanece incerto e não é repetido automaticamente. Não há disparo para contas antigas. Retenção dos marcadores de tentativa preserva a idempotência; não expor CRUD. A cota gratuita Brevo continua compartilhada com os códigos de senha.

Em rollback, remover apenas os blocos de criação do evento e pós-processamento dos dois endpoints, preservando as validações e a criação da conta. Backup privado dos endpoints pré-publicação foi preservado fora do repositório. Não apagar metadados ou alterar envs/login/permissões clínicas.

## Revisão visual: cenário e tartaruga no cabeçalho

A pedido do usuário, o fundo externo passou a usar `assets/optimized/fundo02.webp`; o cabeçalho agora é verde-oliva #526b35, com texto creme e a mascote em V original à esquerda da marca. O rodapé recebeu superfície na mesma paleta para manter legibilidade sobre a arte. Imagens publicadas no repositório de assets autorizado, fixadas por commit; GETs anônimos retornaram MIME correto e bytes idênticos aos originais (`evidence/style-hosting.json`). Sem anexos e sem modificar imagens.

Seis testes do template/paridade passaram. As quatro prévias dos perfis em 390/900 px passaram, incluindo posição da mascote, cenário, imagem clínica proporcional, ausência de overflow e conteúdo sem imagens. Publicada somente `Notifications/render_welcome_email` (ID 360483), preservando cadastro, transporte e controles. Duas prévias reais da revisão enviadas à caixa Vet Tech autorizada; aceitação registrada separadamente em `evidence/real-delivery-style.json`. A mensagem anterior recebida não muda: conferir as mensagens mais recentes. Tarefa 5.1 concluída; o teste final de novos cadastros da tarefa 4.4 continua pendente como já registrado.

### Mascote ampliada e apoiada na divisória

Mascote ampliada de 86 para 110 px, com alinhamento inferior e padding inferior do cabeçalho zerado. O texto conserva espaçamento independente. Seis testes de template passaram e as quatro prévias confirmaram por bounding boxes que a base do elemento coincide com a base do cabeçalho (diferença menor que 1 px), sem overflow. Renderizador publicado seletivamente; prévias da revisão em `evidence/real-delivery-mascot-size.json`. Tarefa 5.2 concluída.

### Remoção do halo e compensação da transparência

A captura do usuário mostrou que medir a borda do elemento img não bastava: o PNG original tinha halo claro e 10 linhas de transparência inferior. Criada cópia limpa com edição de imagem, em `assets/consultation-pdf/mascote-v-clean.png`, preservando o arquivo original e suas demais utilizações. O limite opaco da cópia termina em y=1030 de uma altura 1053; a 110 px de largura a diferença é compensada com margem inferior -1,7 px. As quatro prévias agora verificam a base visível da silhueta por limite alfa opaco, com tolerância de 0,3 px em relação à divisória. Sem halo claro observado na prévia. Seis testes de template passaram. PNG público verificado por MIME/bytes e hash em `evidence/clean-mascot-hosting.json`; publicado somente o renderizador 360483 e enviada uma nova prévia para a caixa autorizada, com aceitação em `evidence/real-delivery-clean-mascot.json`. Tarefa 5.3 concluída.

Publicação da revisão limpa: a CLI ficou sem resposta e foi interrompida; o PUT direto expirou, mas a atualização foi aplicada no servidor. Uma execução posterior confirmou a nova URL e a margem. Uma segunda leitura expirou por lentidão; a consulta isolada final retornou as três verificações verdadeiras em `evidence/clean-mascot-native.json`. A prévia enviada antes dessa confirmação foi separada como `real-delivery-clean-mascot-before-confirmation.json`; a prévia final só foi disparada após a confirmação do HTML remoto. Nenhuma falha de publicação foi considerada sucesso sem essa leitura.

### Botão temporário de acesso local autorizado

Após esclarecer que localhost só funciona no aparelho em que o sistema roda, o usuário autorizou explicitamente o destino `http://localhost:3000/login`. Adicionado botão Acesse nosso sistema no HTML e link equivalente no TXT, configuráveis por `system_url`. A validação permite esse HTTP local exato ou HTTPS e rejeita outros esquemas. A decisão anterior de não incluir CTA local foi substituída nesta revisão. Seis testes de template/paridade e as quatro prévias passaram; o navegador verificou o href sem navegar. Publicado somente o renderizador por importação parcial transacional (HTTP 200). As versões nativas de tutor e veterinário confirmaram label, href, TXT e imagem limpa preservada em `evidence/local-button-native.json`. Prévia da revisão em `evidence/real-delivery-local-button.json`. Tarefa 5.4 concluída; nenhuma mudança no cadastro ou login.

### Substituição do cenário por fundo.webp

A pedido do usuário, substituído somente o cenário externo por `assets/optimized/fundo.webp`. Arte publicada por commit imutável; GET anônimo 200, MIME WebP e mesmos bytes (`evidence/fundo-hosting.json`). Seis testes de template e as quatro prévias responsivas passaram. Publicado somente o renderizador por importação parcial transacional HTTP 200; confirmação nativa do novo fundo, mascote limpa e botão local preservados em `evidence/fundo-native.json`. Uma nova prévia foi aceita para a caixa Vet Tech autorizada, registrada em `evidence/real-delivery-fundo.json`. Tarefa 5.5 concluída.
