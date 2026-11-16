# Tasks

## 1. Prova Google para cadastro

- [x] 1.1 Adicionar intenção de cadastro ao OAuth e prova temporária com hash, expiração e consumo único; validar XanoScript e testes de state, PKCE, claims, intenção forjada, replay e expiração.
- [ ] 1.2 Documentar contratos e configuração OAuth em docs, confirmando que login existente continua sem criar contas e que audiência Google permite o ambiente de testes.

## 2. Criação de identidade sem senha

- [x] 2.1 Permitir credencial ausente para contas Google e reutilizar validações de CPF/CRMV/aptidões em helpers internos; testar cadastro convencional e ausência de campos nos dois perfis.
- [x] 2.2 Criar conclusão transacional com consumo de prova, reserva, identidade, vínculo Google e evento de boas-vindas; testar concorrência, unicidade cruzada, rollback e rejeição de e-mail/sub forjados.
- [x] 2.3 Reutilizar emissão e confirmação de sessão e envio pós-transação; testar perfil correto, resposta tardia, conta existente e evento único mesmo com falha do provedor.
- [x] 2.4 Atualizar documentação de arquitetura/domínio e rollback; conferir que nenhum token ou dado sensível entra em logs/artefatos.

## 3. Compatibilidade de senha

- [x] 3.1 Tratar credencial ausente no login e recuperação, permitindo primeira senha somente com código válido; testar erros genéricos, uso único, limites e manutenção do vínculo Google.
- [x] 3.2 Orientar contas sem senha nas configurações dos dois perfis; testar autorização no backend e regressão de alteração/recuperação convencional, documentando a primeira senha opcional.

## 4. Interface de cadastro

- [x] 4.1 Ativar “Cadastrar com Google” e completar formulário sem senha/confirmar após OAuth, preservando perfil e coletando todos os demais campos; testar estado, cancelamento, erros e e-mail verificado não editável.
- [x] 4.2 Uniformizar gap dos campos e exibir feedback CPF somente quando presente; verificar desktop/celular e temas claro/escuro sem corte, com mensagens acessíveis.
- [x] 4.3 Documentar fluxo visual e executar testes do estado mais compilação Reflex; reiniciar aplicação local conforme skill e confirmar UI publicada localmente.

## 5. Integração

- [ ] 5.1 Publicar seletivamente artefatos Xano compatíveis e validar cadastro/entrada Google para tutor e veterinário em contas de teste autorizadas, sem assumir dados pessoais nem destinatários de e-mail.
- [x] 5.2 Executar regressões de login convencional, Google existente, cadastro convencional, recuperação, configurações e boas-vindas; registrar resultados e limitações reais na change.
