# Proposal

## Why
Configurações já oferece conta, senha e preferências ao tutor, mas a rota e seus endpoints rejeitam o perfil veterinário. O usuário deseja a mesma experiência no menu médico.

## What Changes
- Adicionar Configurações ao menu do veterinário e reutilizar a tela/abas existentes.
- Minha conta médica: nome e telefone editáveis; e-mail e CRMV/UF somente leitura. Não inventar CPF ou endereço ausentes no cadastro médico.
- Adicionar endpoints autenticados veterinario/account (GET/PATCH) e veterinario/password (POST), com allowlist e identidade derivada do token.
- Compartilhar preferências e proteção de rascunhos, isolando contexto, cache e resultados por perfil/sessão.
- Permitir retornar a Horários e Consultas pelo menu médico, preservando confirmação de descarte e logout.

## Capabilities
### New Capabilities
- `veterinarian-account-settings`: manutenção da conta médica e acesso à experiência compartilhada de configurações.
### Modified Capabilities
- `veterinarian-schedule-presentation`: adicionar Configurações aos destinos do menu médico.
Os contratos exclusivos de tutor continuam inalterados.

## Impact
Tela e estado de configurações compartilhados, menu médico, roteamento da agenda e três novos endpoints Xano sem migração de tabelas. São dados pessoais do médico: respostas mínimas, credenciais nunca retornadas e campos profissionais bloqueados. Não envolve leitura ou escrita de prontuário, novas autorizações de pet, notificações ou alteração da auditoria clínica. A validação de identidade ocorre no backend (RN01–RN08); não ampliar acesso de médicos às rotas do tutor.
