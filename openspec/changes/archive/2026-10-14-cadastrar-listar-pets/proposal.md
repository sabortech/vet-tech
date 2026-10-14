## Why

O modelo do VetTech coloca o pet no centro do histórico e exige que cada animal pertença a um único tutor. Esta mudança entrega o primeiro fluxo funcional do perfil: o tutor cadastra seus pets e consulta somente a lista dos animais sob sua responsabilidade.

## What Changes

- Usar a tabela `tutor` do modelo de domínio como identidade autenticada, sem depender da tabela `user` ou de outras tabelas externas ao domínio.
- Permitir que o tutor cadastre pets associados obrigatoriamente ao próprio perfil por `pet.tutor_id`.
- Permitir que o tutor liste somente seus próprios pets; o identificador do tutor usado para filtrar os resultados deve vir da identidade autenticada, não de um valor arbitrário informado pelo cliente.
- Validar espécie e, quando informada, garantir que a raça pertença à espécie escolhida. Raça vazia representa SRD.
- Disponibilizar ao tutor autenticado as espécies cadastradas e as raças da espécie selecionada para preencher o cadastro com opções vindas do modelo de domínio.
- Disponibilizar as ações funcionais de cadastro e listagem no perfil do tutor, sem especificar o layout ou o estilo visual das telas nesta etapa.
- Não incluir edição dos dados do pet, prontuário clínico, autorização de veterinários, notificações ou exportação.

## Capabilities

### New Capabilities
- `pet-management`: cadastro e listagem dos pets do tutor autenticado, com validação de propriedade e dos vínculos de espécie e raça.

### Modified Capabilities
- Nenhuma.

## Impact

- XanoScript: tabelas do modelo de domínio `tutor`, `pet`, `especie` e `raca`; ativação da autenticação do tutor e operações autenticadas de consulta de catálogos, criação e listagem de pets.
- Reflex: integração funcional do perfil do tutor com cadastro e listagem de pets; decisões de composição visual ficam para uma etapa posterior.
- Segurança e privacidade: dados do pet ficam acessíveis ao tutor responsável; o backend deriva a propriedade da identidade autenticada e rejeita tentativas de associar ou listar pets de outro tutor. Esta etapa não acessa nem altera dados do prontuário clínico e não implementa acesso veterinário.
- Nenhuma tabela fora de `docs/domain-model.md`, incluindo `user`, será usada por esta mudança. Não há impacto em notificações automáticas.