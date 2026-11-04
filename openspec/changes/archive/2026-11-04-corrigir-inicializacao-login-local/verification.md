# Verificação

- Antes: frontend dev em 3000; tentativas WebSocket em 8000 falhavam, impedindo envio do login.
- Depois: build de produção compilado pelo launcher, aplicação em http://localhost:3000/ e WebSocket de eventos na mesma porta.
- Navegador Chromium: nenhuma exceção JavaScript; envio de conta fictícia recebeu “Credenciais inválidas.” do fluxo de autenticação, sem erro de conexão.
- `bash -n scripts/run-local.sh`, `git diff --check` e `openspec validate corrigir-inicializacao-login-local --strict`: passaram.
- Nenhuma senha válida foi fornecida; entrada completa em conta existente não foi testada. Não foram alterados usuários nem credenciais.
