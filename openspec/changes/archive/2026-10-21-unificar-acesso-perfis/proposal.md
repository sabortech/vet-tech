# Proposta

## Why

O tutor já autentica e alterna pets, mas a identidade veterinária ainda não é autenticável e a área do tutor não possui a navegação aprovada. Esta entrega prepara o acesso dos dois perfis e a base de interface das próximas capacidades clínicas.

## What Changes

- Compartilhar `/cadastro` e `/login`, adaptando os campos de cadastro ao perfil; o backend identifica o perfil após validar as credenciais.
- Manter identidades em `tutor` e `veterinario`, com um único perfil por e-mail normalizado, inclusive entre tabelas e em requisições concorrentes.
- Permitir clínica opcional; validar CRMV localmente por caracteres, sem consulta externa ou promessa de habilitação comprovada; preservar unicidade do registro profissional normalizado.
- Cadastrar múltiplas especialidades e espécies atendidas por referências a catálogos, com validação no backend.
- Entregar menu retrátil com Início, Vacinas, Medicamentos, Doenças e Consultas; Novo pet em modal e Mudar pet na parte inferior, reutilizando a seleção existente.
- Preparar área veterinária identificada, sem acesso clínico antes da entrega de autorização.
- Separar a carga de espécies/raças na change `popular-catalogos-especies-racas`; esta entrega define e consome os catálogos, sem importar uma lista ampla de registros.

## Capabilities

### New Capabilities

- `veterinarian-identity`: cadastro profissional, espécies/especialidades e autenticação com identidade verificada.
- `profile-authentication`: resolução única de e-mail, login compartilhado, isolamento de tokens e sessão por perfil.
- `authenticated-navigation`: menu por pet, Início, modal de cadastro e alternância reutilizada.

### Modified Capabilities

- `tutor-registration`: cadastro compartilhado e unicidade de e-mail entre perfis.
- `login-screen-presentation`: preservar a apresentação existente com login compartilhado e encaminhamento pelo perfil autenticado.

## Impact

Reflex/Python, estado de autenticação, componentes de pets, páginas existentes, cliente Xano, APIs de identidade, tabelas e índices em `xano/`, documentação de domínio e testes. Preservar tokens/fluxos de tutor compatíveis e não reutilizar a tabela `user`. A migração deve auditar duplicidades e preservar IDs, hashes e vínculos. Dados pessoais e credenciais exigem proteção nas respostas e logs; esta change não lê prontuários, não concede autorizações nem introduz notificações.
