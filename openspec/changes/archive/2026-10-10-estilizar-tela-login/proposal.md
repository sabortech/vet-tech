# Proposta

## Por quê

A tela de login funcional atual não corresponde à identidade visual do cadastro nem ao protótipo fornecido. Esta mudança alinha sua apresentação ao protótipo e à linguagem visual já adotada, sem alterar autenticação ou qualquer outro comportamento funcional.

## O que muda

- Atualizar a composição visual da tela de login existente no Reflex para refletir o protótipo: cartão amplo com cantos arredondados, painel branco para o formulário e imagem de fundo florestal no painel lateral.
- Reutilizar os recursos visuais e convenções já existentes no projeto, incluindo a fonte Nunito, o logotipo/mascote e a imagem `assets/fundo02.jpeg`.
- Aproximar tipografia, cores, espaçamentos, campos, botões, divisor e posicionamento dos elementos da referência.
- Adaptar a composição a telas menores sem prejudicar o acesso ao formulário.
- Manter o envio do formulário ligado ao fluxo de login existente e preservar seu estado, mensagens, rota e navegação atuais.
- Manter os elementos de lembrar acesso, recuperação de senha e Google, se exibidos como parte da composição visual, sem implementar ou conectar novos comportamentos nesta mudança.
- Não alterar endpoints, validação ou suporte de autenticação; o contrato funcional atual continua aceitando e-mail e senha.

## Capacidades

### Novas capacidades

- `login-screen-presentation`: apresentação responsiva da tela de login alinhada ao protótipo, sem alterar o contrato funcional de autenticação.

### Capacidades modificadas

Nenhuma.

## Impacto

- **Reflex:** alteração visual concentrada na view de login existente em `vet_tech/components/auth.py`; o registro da página e o estado permanecem nos módulos atuais.
- **Recursos visuais:** uso dos assets já existentes em `assets/`, sem introduzir dependências ou serviços.
- **Autenticação e backend:** sem alterações em `vet_tech/features/auth/state.py`, cliente Xano ou arquivos em `xano/`; login continua usando e-mail e senha. O texto do protótipo “E-mail ou CPF” não representa suporte novo a CPF nesta mudança.
- **Privacidade e autorização:** nenhum novo dado é coletado ou exposto e nenhum acesso ao prontuário é introduzido. Regras de autorização do tutor não são afetadas.
- **Notificações:** sem impacto.
- **Verificação:** conferir a composição em viewport desktop e estreito, e validar que o formulário continua acionando o fluxo atual de login.
