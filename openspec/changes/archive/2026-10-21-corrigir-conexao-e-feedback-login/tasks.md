# Tasks

Estas tarefas registram correções e verificações já realizadas durante o
diagnóstico, reunidas nesta change por autorização de arquivamento do usuário.

## 1. Conexão da instância

- [x] 1.1 Identificar a divergência entre a porta da página e a conexão de eventos; restaurar o build da instância principal e reiniciar em produção na porta única 3000, com a origem Xano carregada pelo ambiente local.
- [x] 1.2 Conferir pelo Chromium que o WebSocket usa a porta 3000 e que o formulário recebe a resposta do Xano, sem encerrar a instância principal ao final.

## 2. Feedback temporário seguro

- [x] 2.1 Distinguir HTTP 429 de falhas genéricas no cliente Xano e orientar a espera, sem repetir credenciais automaticamente nem propagar o corpo arbitrário da resposta.
- [x] 2.2 Verificar 429 em JSON/texto, uma única chamada, mensagem segura, propagação ao estado do login e liberação do formulário após erro.

## 3. Verificação e preservação

- [x] 3.1 Verificar cadastro/login e leitura autenticada de catálogo e pets com uma conta sintética temporária, confirmar a abertura do perfil pela interface e remover somente os registros criados pelo teste, preservando IDs preexistentes.
- [x] 3.2 Conferir a identidade da conta indicada sem alterar sua senha; registrar HTTP 429 observado e resposta normal após a espera, sem atribuir uma causa única à tentativa específica do usuário.
- [x] 3.3 Executar a suíte unitária (41 testes), compilar o Reflex e conferir o diff; consolidar evidências e limites, sincronizar a spec de feedback e validar o arquivamento.
