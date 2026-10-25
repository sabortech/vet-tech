# Design

## Context

Esta change documenta trabalho já executado e aprovado para arquivamento. O
login de tutor usa o estado Reflex e o cliente Xano existentes. Não há alteração
de identidade, senha, perfil, endpoint ou autorização. O relato do usuário
motivou diagnósticos separados de conexão, limitação temporária e autenticação.

## Goals / Non-Goals

- Restaurar a conexão da instância local e tornar HTTP 429 identificável.
- Preservar mensagens seguras, sessão e contrato atuais.
- Não redefinir senhas, implementar CPF/login veterinário, ampliar permissões
  ou afirmar que a senha da conta relatada foi validada.

## Decisions

### Restaurar o ambiente e os arquivos gerados da instância principal

Os testes visuais haviam deixado o build apontando eventos para a instância
temporária na porta 3011. A aplicação principal foi recompilada e reiniciada em
produção na porta única 3000, com `.env` carregado e frontend/backend na mesma
porta. O arquivo local guarda somente a origem Xano e é ignorado pelo Git.
O navegador confirmou WebSocket na porta 3000 e retorno do evento de login.

Testes em outra porta devem isolar a saída gerada ou restaurar o build e a
instância principal depois. Esta correção não introduz isolamento automático
de builds nem fixa uma nova configuração global de portas em `rxconfig.py`.

### Tratar HTTP 429 na fronteira HTTP compartilhada

Antes do tratamento genérico de erros, `xano_request` identifica o status 429
e lança a mensagem de limite temporário. O corpo remoto não é interpretado
como mensagem confiável. Não há retry automático, que repetiria credenciais
e poderia prolongar a limitação. O estado existente apresenta o erro e limpa
o indicador de ocupação no `finally`.

## Risks / Trade-offs

- O Xano pode impor limites compartilhados; a orientação de espera não promete
  uma duração que o serviço não informou.
- Recompilar o mesmo diretório para outra instância pode reproduzir o problema
  de conexão; a execução principal foi restaurada e essa limitação registrada.
- A entrada válida da fixture comprova o fluxo de tutor, mas não comprova a
  credencial particular do usuário. O diagnóstico não alterou sua senha.

## Migration Plan

Não há migração de schema ou dados de usuários. A fixture de teste e sua
reserva de e-mail foram removidas com verificação de preservação dos IDs
preexistentes. A configuração de execução fica local, fora do arquivo Git.
Uma reversão do feedback afeta somente o tratamento de 429 e seus testes.
