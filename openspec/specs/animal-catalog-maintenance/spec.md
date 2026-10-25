# animal-catalog-maintenance Specification

## Purpose

Manter catálogos iniciais de espécies e raças por carga administrativa revisável e repetível, preservando os registros e relacionamentos já utilizados pelo sistema.

## Requirements

### Requirement: Registros são revisáveis antes da carga
O sistema SHALL permitir revisar conjunto versionado de espécies/raças, origem, cobertura inicial e vínculo de cada raça com uma espécie. A simulação SHALL mostrar inclusões, reutilizações e conflitos sem modificar o banco. Registros sem nome, referência inválida ou correspondência ambígua SHALL impedir a aplicação do lote.

#### Scenario: Revisão sem escrita
- **WHEN** o operador simula a carga do conjunto
- **THEN** recebe o plano agrupado por espécie e nenhum registro é criado ou alterado

#### Scenario: Raça sem espécie
- **WHEN** o conjunto contém raça com referência de espécie inexistente
- **THEN** a validação falha antes de escrever

### Requirement: Carga é idempotente e preserva vínculos
O sistema SHALL reutilizar espécies e raças correspondentes e criar apenas entradas ausentes, sem alterar IDs, pets ou aptidões existentes. Nomes SHALL ser comparados por normalização documentada; raça SHALL ser única por espécie e nome normalizado. SRD SHALL continuar representado por raça não informada.

#### Scenario: Reexecutar conjunto
- **WHEN** o operador reaplica o mesmo conjunto concluído
- **THEN** não são criadas duplicidades e os IDs já utilizados permanecem iguais

#### Scenario: Correspondência ambígua
- **WHEN** existem duas espécies equivalentes pela normalização ou sinônimos sem mapeamento explícito
- **THEN** a carga é interrompida antes da escrita para revisão das correspondências

### Requirement: Aplicação é administrativa e rastreável
O sistema SHALL restringir a carga a operador com credenciais administrativas e execução explícita no ambiente escolhido, sem escrita pública. SHALL informar resultado real, inclusive falhas parciais, e registrar versão do conjunto e entradas criadas sem expor credenciais.

#### Scenario: Aplicação concorrente ou retomada
- **WHEN** duas execuções tentam inserir as mesmas entradas ou um lote incompleto é retomado
- **THEN** nenhuma duplicidade é criada e o relatório distingue entradas criadas, existentes e falhas

### Requirement: Reversão preserva dados em uso
O sistema SHALL permitir identificar as entradas criadas por um lote e reverter somente as que não tenham referências ou alterações posteriores. SHALL NOT excluir entradas anteriores ou alterar dados de pets para reverter a carga.

#### Scenario: Entrada passou a ser utilizada
- **WHEN** a reversão encontra uma raça criada pelo lote que já é usada por um pet
- **THEN** preserva a raça e o pet e informa a pendência no resultado
