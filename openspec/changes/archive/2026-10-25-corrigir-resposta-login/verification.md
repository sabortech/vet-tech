# Verificação

- 43 testes unitários passaram (`.venv/bin/python -m unittest discover -s tests/unit -v`).
- `reflex compile --dry` passou.
- Validação OpenSpec estrita passou.
- Instância iniciada em produção com porta única 3000 e `.env` carregado; `/login` retorna HTTP 200 após redirecionamento.
- Configuração gerada aponta eventos WebSocket e serviços para a porta 3000.
- Testes do gerador comprovam publicação do indicador antes da API e da sessão antes das leituras auxiliares, bloqueio de duplicatas, limpeza de pets antigos e tratamento de rejeição/429. Regressões comprovam preservação de sessão quando catálogos ou pets falham.
- Não foi executado teste visual automatizado em navegador nesta alteração. A validação HTTP não comprova o percurso completo de login no navegador.
- Sem alteração de senha, conta, endpoint Xano ou regras de autorização. Não foram realizados novos logins reais nesta etapa.
- Consultas auxiliares permanecem sequenciais para evitar rajadas no Xano; latência e limites do serviço externo continuam possíveis. Reutilização de conexões HTTP permanece fora do escopo deste ajuste, conforme design.

## Reprodução após novo relato de falha

Executado Chromium headless com Playwright já disponível na máquina, usando a conta indicada pelo usuário, sem imprimir senha ou token de autenticação. Em `http://127.0.0.1:3000/login`, o formulário abriu WebSocket na porta 3000 e exibiu `Perfil do tutor` após o envio. Não houve erro JavaScript nem falha de requisição reportada pelo navegador no percurso observado. O teste comprova o login completo nessa instância, sem comprovar o comportamento da aba/endereço usado pelo usuário. Solicitados endereço e sintoma para localizar a diferença, sem novas alterações especulativas.

Observação de configuração: `.web/env.json` de desenvolvimento passou a apontar 8000, enquanto o bundle de produção efetivamente servido contém porta 3000; o navegador confirmou conexão na porta 3000. Não atribuir a falha ao arquivo de desenvolvimento sem verificar o bundle servido.
