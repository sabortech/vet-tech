# Mudar pet: seleção isolada

Mudar pet limpa contexto pelo fluxo existente e abre `/?selecionar=pet`.
A projeção da query mostra somente a lista reutilizada, com a mesma imagem
espreitando do seletor de datas à esquerda. `/` mantém cadastro e lista;
link de retorno e histórico do navegador alternam os modos sem flag persistente.
Layout conserva LED/sombra e adapta tartaruga/lista ao celular. Mensagens
de listagem continuam visíveis mesmo sem o formulário de cadastro.

32 testes unitários de navegação, seleção e carregamento clínico aprovados.
Compilação completa aprovada em 3,402 segundos. Roteiro
`tests/integration/change_pet_list_browser.py` aprovado nas portas 3000 e
3001, nos dois temas e em 1440/390 px: seleção isolada sem formulário,
tartaruga à esquerda sem overflow, vazio/erro/atualização, retorno à tela
completa, voltar/avançar e escolha autorizada do segundo pet no Dashboard
e Prontuário. Nenhuma exceção JavaScript; nenhuma alteração de dados reais.
O acabamento final de espaçamento/contraste foi reconferido na porta 3001.
OpenSpec estrito e whitespace aprovados. Capturas e results.json por porta.
