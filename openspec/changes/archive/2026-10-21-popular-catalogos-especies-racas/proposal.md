# Proposta

## Why

O cadastro de pets já depende das tabelas de espécie e raça, e a identidade veterinária usará as mesmas espécies. A carga desses registros precisa de entrega própria para permitir revisão e repetição sem duplicar entradas ou alterar vínculos existentes.

## What Changes

- Preparar um conjunto inicial versionado de espécies e raças e uma seção exclusiva para revisar os registros, suas fontes e o mapeamento ao banco existente.
- Curar cerca de 20 raças de cães e 20 de gatos a partir de fontes identificadas. A seleção inicial tem 21 caninas (incluindo a Shih Tzu legada) e 20 felinas, sem impor limite permanente nem afirmar ranking brasileiro.
- Executar carga administrativa com simulação, validação de nomes/vínculos, criação apenas do que falta e relatório de resultado.
- Preservar IDs e registros existentes, inclusive pets e futuras aptidões veterinárias; não cadastrar uma raça artificial SRD.
- Tornar a reexecução idempotente e interromper conflitos ambíguos antes de escrever.

## Capabilities

### New Capabilities

- `animal-catalog-maintenance`: preparação, revisão e carga administrativa segura dos catálogos de espécies e raças.

### Modified Capabilities

Nenhuma: as operações de consulta e os contratos de cadastro de `pet-management` permanecem os mesmos.

## Impact

Dados de catálogo no Xano, arquivos versionados de carga, ferramenta administrativa e testes. Sem alteração de pets, identidades, prontuários ou autorização. Sem endpoint público de escrita, novas tecnologias ou chamadas externas durante a importação. A lista concreta será preparada e revisada na seção de registros durante a execução; esta proposta não declara uma lista completa nem dados já carregados.
