# Tasks

## 1. Navegação compartilhada

- [x] 1.1 Criar estado compartilhado para expansão desktop e drawer móvel, mantendo o drawer fechado por padrão; cobrir alternância e estado inicial com testes unitários executáveis por `python -m unittest discover -s tests/unit`.
- [x] 1.2 Criar `layout_com_menu(conteudo, pagina_ativa)` e o componente único da sidebar com marca, sete opções, item ativo, opções “Em breve”, controle sempre visível, atributos acessíveis, foco por teclado, backdrop e fechamento por Esc; verificar compilação Reflex e ausência de destino inválido nas opções sem tela.
- [x] 1.3 Centralizar tokens de cor, tipografia, espaçamento, raios e transição; verificar que sidebar e conteúdo consomem os mesmos tokens e que patinha e “Vet Tech” compartilham a cor definida.

## 2. Perfil do tutor responsivo

- [x] 2.1 Integrar o wrapper ao `profile_view()` existente com `pagina_ativa="meus_pets"` e remodelar os cartões e campos, preservando todos os textos, nomes de campo, eventos e a rota atual; verificar o fluxo existente com `python -m unittest discover -s tests/unit`.
- [x] 2.2 Implementar formatação de data e normalização visual de aliases de sexo sem alterar valores enviados ao Xano; adicionar testes para datas válidas/inválidas, aliases conhecidos e valores não reconhecidos e executar `python -m unittest discover -s tests/unit`.
- [x] 2.3 Adicionar o mascote como decoração não interativa, sem cobrir controles e oculto em telas pequenas; verificar que cadastro, upload, atualização da lista e logout continuam acessíveis.

## 3. Foto na listagem de pets

- [x] 3.1 Acrescentar ao retorno autenticado de `list_GET.xs` a imagem já associada ao pet, sem remover ou renomear outros campos; verificar que a resposta permanece limitada ao tutor autenticado.
- [x] 3.2 Mapear `foto` para uma URL consumível quando disponível, sem expor caminhos privados, e exibir patinha como fallback; cobrir respostas com URL e sem URL nos testes unitários e executar `python -m unittest discover -s tests/unit`.

## 4. Verificação integrada

- [x] 4.1 Executar compilação do app e validar visualmente 1920, 1366, 1024, 768 e 390 px, com sidebar aberta/fechada, sem rolagem horizontal, sobreposição ou controles inacessíveis.
- [x] 4.2 Verificar no navegador que o perfil segue na rota existente, que a preferência de navegação se mantém entre telas aplicáveis e que cadastro, lista, foto e logout continuam funcionais; apresentar o resultado para validação do usuário e não arquivar antes dessa validação.
