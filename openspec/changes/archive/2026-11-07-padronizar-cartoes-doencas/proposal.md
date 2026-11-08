# Proposal

## Why
A aba Doenças ainda apresenta cartões genéricos, diferentes de Vacinas e Medicamentos. Padronizar a leitura com a hierarquia da referência enviada e a identidade visual já implementada nas abas clínicas.

## What Changes
- Cabeçalho com título, descrição, foto/nome do pet e Atualizar no padrão das duas abas.
- Cartão dividido com nome, estado legível, evolução, consulta, veterinário e descrição; painel decorativo e LED verde horário existentes.
- Legibilidade de textos longos, temas claro/escuro, celular e estados vazio, carregando e erro.
- Preservar consulta de origem e informações ausentes, sem inventar notas recentes ou estados.

## Capabilities

### New Capabilities
Nenhuma.

### Modified Capabilities
- `clinical-records`: apresentação padronizada da lista de condições do pet na aba Doenças.

## Impact
Componentes clínicos, composição da página, estilos locais e documentação de arquitetura; sem nova tecnologia, API ou dependência. Dados de saúde já autorizados continuam no fluxo atual, com autorização no backend, isolamento por pet/sessão e auditoria existente preservados. Nenhuma nova persistência, exposição pública ou notificação automática. RF de prontuário e RN de propriedade/autorização continuam aplicáveis.
