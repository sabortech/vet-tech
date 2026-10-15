# Tasks

## 1. Consulta individual autorizada no Xano

- [x] 1.1 Implementar `GET /pets/{pet_id}` no grupo `Pet`, com identidade `tutor`, ID positivo, projeção dos dados básicos e filtro conjunto de ID/proprietário; validar o XanoScript e documentar o contrato e os códigos de resposta em `verification.md`.
- [x] 1.2 Criar e executar verificação de integração em ambiente de teste com dois tutores e pets distintos, cobrindo pet próprio, ID alheio por chamada direta, ID inexistente/inválido e token ausente/inválido; registrar respostas sem segredos e confirmar ausência de alterações nos registros.

## 2. Cliente e contexto de seleção

- [x] 2.1 Acrescentar status HTTP opcional e compatível a `XanoRequestError` para tratar 401 sem comparar mensagens; testar propagação de status, preservação de `str(error)` e erro transitório, mantendo os contratos atuais do cliente.
- [x] 2.2 Implementar seleção explícita, carregamento, detalhes autorizados e nova tentativa no estado existente, com invalidação por geração/sessão/ID; testar A→B com sucesso e erro fora de ordem, retorno à lista durante pedido e resposta incompatível com o ID solicitado.
- [x] 2.3 Integrar limpeza no logout, autenticação rejeitada e nova sessão, além da reconciliação ao atualizar lista/cadastrar pet; testar conta nova com falha de lista, token rejeitado, pet ausente na lista, atualização do pet atual e nenhuma seleção automática, documentando as transições em `verification.md`.

## 3. Área individual e alternância na interface

- [x] 3.1 Acrescentar ações acessíveis de abrir, trocar, voltar e tentar novamente em `components/pets.py`, com identificação do pet ativo e detalhes básicos; verificar campos opcionais, SRD, peso zero e falha de catálogo sem bloquear a área, mantendo cadastro/listagem e sem apresentar ações clínicas fictícias.
- [x] 3.2 Verificar no navegador desktop e celular a lista vazia, um pet, múltiplos pets, carregamento/falha e alternância, incluindo acesso por teclado; registrar evidências e confirmar que dados do pet anterior deixam de aparecer durante a troca.

## 4. Validação integrada da entrega

- [x] 4.1 Executar a suíte unitária existente e os testes novos e compilar com `reflex compile --dry`; confirmar regressões de login, cadastro/listagem de pets e compartilhamento das páginas existentes, registrando comandos e resultados reais em `verification.md`.
- [x] 4.2 Executar o percurso Reflex→Xano com dois tutores após disponibilizar o endpoint em teste, comprovando abertura, alternância, negativa de pet alheio e limpeza de sessão; registrar evidências separadas de mocks e não marcar concluído sem execução ou confirmação explícita da equipe.

## Workflow follow-up

- Após revisão e autorização, publicar somente os artefatos Xano necessários, com dry-run antes do push, e aplicar a interface validada.
- Sincronizar o delta de `pet-management` e arquivar após verificação; atualizar o plano geral com o estado real da entrega.
