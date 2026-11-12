# Tarefas funcionais

Implementação em andamento. Backend publicado em desenvolvimento; testes e dependências externas registrados em verification.md. `design.md` foi omitido por solicitação do usuário; esta lista define entregas e verificações funcionais, sem prescrever desenho visual ou arquitetura detalhada.

## 1. Chamados e controle de acesso

- [x] 1.1 Persistir chamados, participantes, conversa de origem, contexto compartilhado, mensagens e eventos em Xano/XanoScript; verificar vínculos obrigatórios e atualizar o DER e a documentação de domínio de forma consistente.
- [x] 1.2 Disponibilizar criação autenticada e idempotente de chamado após confirmação do tutor; verificar pet alheio, conversa forjada, ausência de consentimento, concorrência e retry com resposta perdida em testes de backend.
- [x] 1.3 Disponibilizar fila mínima e assunção exclusiva; verificar que a fila não expõe contexto clínico e que duas assunções concorrentes atribuem somente um responsável, sem vazamento ao outro.
- [x] 1.4 Disponibilizar leitura de chamados e mensagens somente aos participantes autorizados; verificar tentativas de outro tutor, outro veterinário, visitante e sessão expirada, inclusive com IDs conhecidos.
- [x] 1.5 Disponibilizar envio textual persistente e idempotente; verificar autoria pelo servidor, ordenação estável, texto vazio, falha de gravação e repetição após timeout sem duplicação.
- [x] 1.6 Disponibilizar cancelamento e encerramento com motivo, ator e horário; verificar concorrência entre cancelamento e assunção, orientação final e bloqueio de mensagens após encerramento.
- [x] 1.7 Registrar eventos operacionais protegidos sem segredos ou transcrições em logs técnicos; verificar tentativa de adulteração e separação da auditoria clínica em testes e documentar as permissões do chat.

## 2. Continuidade a partir do assistente

- [x] 2.1 Estender o contrato n8n para intenção estruturada opcional de encaminhamento, preservando respostas atuais; ampliar a cobertura de `tests/unit/test_n8n_client.py` com resposta antiga, intenção válida/inválida, IDs divergentes e erro remoto.
- [x] 2.2 Integrar o encaminhamento ao contexto privado do servidor e à confirmação de pet e compartilhamento; ampliar `tests/unit/test_support_chat_state.py` para impedir contexto forjado, visitante, perfil veterinário e resposta de sessão antiga.
- [x] 2.3 Encerrar a participação automática do bot no chamado confirmado; verificar que resposta tardia não altera a transcrição compartilhada e mensagens humanas não são enviadas automaticamente ao n8n.
- [x] 2.4 Atualizar `docs/n8n-chat.md` com contrato funcional, confirmação, separação bot/humano e requisitos de publicação; verificar em ambiente de teste que o workflow publicado oferece encaminhamento real e mantém a conversa comum sem ele.

## 3. Operação pelos participantes

- [x] 3.1 Permitir ao tutor confirmar encaminhamento e acompanhar chamado aguardando, em atendimento e encerrado; verificar o ciclo com conta autenticada, pet próprio e cancelamento antes de criar chamado.
- [x] 3.2 Permitir ao veterinário consultar fila, assumir, ler contexto, trocar mensagens e encerrar; verificar com dois profissionais que somente o responsável acessa a transcrição e responde.
- [x] 3.3 Permitir retomada e consulta de chamados pelos participantes após fechar, recarregar e novo login; verificar persistência, histórico encerrado somente leitura, troca de pet e isolamento após troca de conta.
- [x] 3.4 Disponibilizar avisos internos de criação, assunção, mensagens e encerramento sem duplicação nem texto clínico fora da conversa; verificar destinatário conectado/desconectado e diferenciação entre falha de serviço e espera por profissional.
- [x] 3.5 Documentar o fluxo funcional em `docs/`, incluindo fila compartilhada, identidade do responsável, privacidade, encerramento e independência do prontuário; verificar coerência com os cenários desta change sem acrescentar requisitos visuais.

## 4. Verificação integrada

- [x] 4.1 Executar o ciclo navegador → Reflex → n8n → chamado Xano → veterinário → resposta ao tutor → encerramento em ambiente de teste; registrar resultado com duas sessões autenticadas e sem credenciais ou conteúdo sensível na evidência.
- [x] 4.2 Verificar falhas de rede, retry, concorrência de assunção, retomada e respostas atrasadas ponta a ponta; confirmar ausência de duplicações e de acesso entre contas.
- [x] 4.3 Verificar chat com e sem autorização clínica e após revogação; confirmar que só as mensagens compartilhadas ficam acessíveis, acesso ao prontuário continua protegido/auditado e nenhuma consulta ou prescrição é criada automaticamente.
- [x] 4.4 Executar os testes relevantes de chat e autorização, regressão do chat temporário de visitante e compilação Reflex conforme as skills do projeto; registrar resultados antes de considerar a implementação concluída.
