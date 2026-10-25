# Tarefas

## 1. Revisão exclusiva dos registros

- [x] 1.1 Inventariar espécies, raças e referências existentes sem escrita; entregar contagens e tabela de correspondências/conflitos, preservando IDs e omitindo credenciais ou dados pessoais.
- [x] 1.2 Preparar conjunto inicial versionado em `xano/seed/` com nomes, chaves estáveis, espécie de cada raça e fontes; entregar tabela de revisão agrupada por espécie e documentar cobertura e mapeamentos de sinônimos, sem criar registro artificial SRD.
- [x] 1.3 Validar o conjunto e resolver correspondências ambíguas antes da aplicação; testes devem rejeitar duplicidades normalizadas, nomes vazios, raça sem espécie e sinônimos sem mapeamento.

## 2. Carga administrativa

- [x] 2.1 Implementar simulação padrão sem escrita, plano revalidado antes da aplicação e credenciais por ambiente; verificar que a simulação não altera contagens/IDs e documentar os comandos exatos.
- [x] 2.2 Preparar proteção de unicidade normalizada no Xano e carga somente de ausentes, com manifesto por execução/lote; testar reexecução, disputa concorrente, falha parcial e retomada sem duplicação nem renomear registros existentes.
- [x] 2.3 Implementar reversão restrita às entradas criadas e ainda sem uso/alterações posteriores; testar que entradas antigas e registros referenciados são preservados e documentar o resultado parcial de reversão.

## 3. Verificação integrada

- [x] 3.1 Conforme autorização do usuário em 21/10/2026, dispensar ambiente isolado; executar nova simulação e carga direta no workspace atual, comparar IDs/referências anteriores e confirmar conjunto completo sem duplicidades por leitura, registrando evidências reais em `verification.md`.
- [x] 3.2 Verificar após a carga as espécies e raças por leitura administrativa, vínculo/filtro de cada raça à espécie e opções públicas compartilhadas pelo cadastro veterinário; registrar que testes autenticados de cadastro com/sem raça e criação de fixtures foram dispensados pelo usuário.
- [x] 3.3 Apresentar o plano concreto de carga para o ambiente de destino, executar a carga revisada e registrar contagens/manifesto e smoke das APIs; nenhuma confirmação de sucesso pode ocultar lote incompleto ou conflitos.

## Workflow follow-up

- Sincronizar a capacidade e arquivar após revisão das evidências e do conjunto carregado.
