## Why

Iniciar com `reflex run` não carrega o `.env`, e a validação rejeita a configuração Xano mesmo com o arquivo preenchido.

## What Changes

- Carregar o `.env` da raiz uma vez ao importar a configuração compartilhada.
- Preservar variáveis existentes no ambiente e a validação de origem Xano.
- Declarar python-dotenv e documentar a inicialização direta no Windows.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `project-foundation`: carregamento automático da configuração local.

## Impact

Configuração compartilhada, dependências, documentação e testes. Sem alterações em dados clínicos, autorização, auditoria ou notificações; atende à configuração operacional de RF01 sem alterar RN01–RN24.
