# Proposal

## Why

A alteração de senha de tutor e veterinário aceita atualmente apenas a senha atual, enquanto “Esqueceu a senha?” no login é um texto sem ação. É necessário confirmar a posse do e-mail cadastrado nos dois fluxos, com mensagens que sigam a identidade visual do Vet Tech.

## What Changes

- Exigir código por e-mail na alteração de senha em Configurações → Segurança dos dois perfis, mantendo a validação da senha atual.
- Implementar recuperação pelo login: informar e-mail, validar código e definir nova senha, sem exigir a senha esquecida.
- Adicionar desafios temporários de uso único, expiração, limite de tentativas e controle de reenvio no Xano.
- Manter o aplicativo em localhost, sem contratar hospedagem; o e-mail usa cabeçalho ilustrado por URL HTTPS, sem anexos; somente a imagem precisa estar disponível publicamente.
- Criar template HTML compartilhado e versão textual em português, com marca, verde, código destacado, validade e orientação sobre solicitação desconhecida; disponibilizar prévia com dados fictícios e documentação de personalização.
- **BREAKING**: os endpoints de alteração de senha passam a exigir desafio e código válidos; clientes antigos não poderão alterar senha sem essa confirmação.
- Manter o login normal com e-mail e senha, sem código, chave de ativação de 2FA ou envio adicional após autenticação.

## Capabilities

### New Capabilities
- `password-email-verification`: desafios e recuperação de senha por e-mail para tutor e veterinário, incluindo template e proteção contra abuso.

### Modified Capabilities
- `tutor-account-settings`: exigir confirmação por código na troca de senha do tutor.
- `veterinarian-account-settings`: exigir confirmação por código na troca de senha do veterinário.

## Impact

- Reflex: `components/auth.py`, `features/auth/`, `features/settings/`, `pages/configuracoes.py` e integração compartilhada com Xano; reutilizar a organização de `docs/architecture.md`.
- Xano: grupo Authentication, endpoints `tutor/password` e `veterinario/password`, novas operações de solicitação/verificação e persistência de desafios. Atualizar o DER e os XanoScripts juntos.
- Não reutilizar os endpoints Quick Start de recuperação de `user`: eles não representam as identidades tutor/veterinario e usam link demonstrativo.
- Dados sensíveis envolvidos: e-mail e credenciais da conta. Não acessar prontuários, alterar autorizações de pets ou transportar dados clínicos no e-mail. Registrar eventos de segurança sanitizados, sem código, senha ou token.
- Envio transacional pelo backend via Brevo, escolhido pelo usuário para substituir o modo restrito de testes do Resend sem comprar domínio, separado dos lembretes clínicos. Configuração de remetente, entrega e limites do provedor precisa ser verificada no ambiente de desenvolvimento, sem segredos no código.
- Verificar backend real com contas sintéticas e destinatários de teste explicitamente configurados; verificar interface nos dois perfis, temas e celular. Nenhum envio a usuários reais faz parte dos testes.
