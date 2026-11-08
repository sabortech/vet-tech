# Proposal

## Why
A lista e o detalhe de Consultas usam textos soltos e cartões genéricos, destoando das demais abas clínicas. Organizar conteúdo e ações na mesma linguagem visual melhora a leitura do prontuário completo.

## What Changes
- Cabeçalho compartilhado com pet e Atualizar.
- Lista com cartões divididos, LED e símbolo de calendário em disco com 70% de opacidade sobre cenário existente.
- Detalhe com identificação da consulta, metadados em grade e motivo, diagnóstico e observações em blocos com título acima do valor.
- Vacinas, Medicamentos e Doenças com os mesmos cartões completos de suas abas, incluindo ilustrações translúcidas, e Exames em cartão dividido no mesmo padrão; sem repetir ação para a consulta já aberta.
- Catálogo de quatro fundos para os cartões ilustrados, incluindo fundinho.jpeg, com sorteio estável e variedade antes de repetir.
- Agrupamento discreto de permissões/auditoria e preservação de exportação, retorno, vazio, loading e erros.

## Capabilities
### New Capabilities
Nenhuma.
### Modified Capabilities
- `clinical-records`: apresentação padronizada da lista e do detalhe de consultas do tutor.

## Impact
Componentes Reflex, composição e CSS locais, documentação e verificação sintética. Sem alteração de API, modelo, autorização no Xano ou geração do PDF. Preservar propriedade, consentimento e auditoria existentes; dados sensíveis continuam no fluxo autorizado, sem nova persistência ou notificações.
