# Tarefas

Verificacao concluida em 11/11/2026. A URL foi corrigida pelo usuario e validada sem reescrever o .env. A instancia de producao ja estava ativa e passou no smoke completo, dispensando reinicio. Specs dispensadas por `skip_specs: true`: a correção restaura a integração já especificada. Design dispensado por se tratar de ajuste operacional localizado, sem nova arquitetura.

## 1. Correção da configuração

- [x] 1.1 Alterar somente a URL n8n no `.env` local para o endpoint de produção já validado, preservando o segredo; verificar que o caminho usa `/webhook/`, que o arquivo continua ignorado pelo Git e que nenhum valor privado aparece em diff ou evidência.
- [x] 1.2 Documentar em `docs/n8n-chat.md` a causa confirmada, uso de produção versus teste e necessidade de recarregar o ambiente do processo; verificar que as instruções correspondem à configuração corrigida e não contêm credenciais.

## 2. Verificação operacional reproduzível

- [x] 2.1 Criar ferramenta de smoke em `scripts/` que carregue a configuração privada e reutilize `request_chat` com pergunta genérica de visitante; verificar que reporta somente sucesso, código de erro seguro e duração e termina com código diferente de zero em falha, sem imprimir resposta, URL privada, payload ou segredo.
- [x] 2.2 Documentar o comando da ferramenta e executar contra produção; verificar sucesso do cliente com contrato válido, registrando somente metadados seguros. Usar os testes existentes de `test_n8n_client` para regressão da validação de IDs, erros e credenciais.

## 3. Verificação pelo aplicativo

- [x] 3.1 Identificar o processo Reflex e a porta efetiva; iniciar ou reiniciar em produção conforme a skill `reflex-process-management`, carregando o `.env` corrigido e mantendo log privado; verificar inicialização sem erros e disponibilidade da página de login.
- [x] 3.2 Executar `tests/integration/n8n_bridge_smoke.py` na URL local efetiva; verificar que o ciclo navegador → Reflex → n8n → navegador recebe sucesso verdadeiro do workflow, e não somente retorno de erro pela ponte.
- [x] 3.3 Registrar em `docs/n8n-chat.md` data e resultado da verificação de visitante, sem afirmar validação de consultas clínicas autenticadas; verificar ausência de segredos e confirmar que a change de chat tutor–veterinário não foi implementada por esta correção.
