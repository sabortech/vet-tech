# Sombra verde dos cartões

Token CSS `--vt-card-green-shadow` aplicado às superfícies de cartões de
Meus Pets, Configurações, prontuário, registros clínicos, consultas e áreas
profissionais. Descendentes de `.dashboard-page` explicitamente excluídos.
Campos/botões e blocos internos sem superfície de cartão não recebem sombra.

`tests/integration/card_shadows_browser.py` aprovado com backend sintético:
verifica a cor verde calculada nos dois cartões de Meus Pets, nas três abas
de Configurações, resumo/seções/cartões de Consultas e permissões. Confirma
a cor original da sombra do Dashboard nos temas claro e escuro. Sem exceções
JavaScript. CSS servido sincronizado integralmente; nenhuma alteração em dados
ou ações. Resultados e capturas nesta pasta; whitespace validado.
