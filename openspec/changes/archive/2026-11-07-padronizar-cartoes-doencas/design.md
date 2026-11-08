# Design

## Context
Ver proposal.md. `records("doencas")` ainda usa `record_card`; Vacinas e Medicamentos possuem cartões divididos próprios. `_records_header` atende só essas duas abas. A projeção `cards` já fornece estado, descrição, evolução legível e origem; não fornece uma lista estruturada de notas recentes.

## Goals / Non-Goals
Aplicar a linguagem visual existente exclusivamente à listagem de Doenças. Preservar o cartão genérico dentro de consultas e o fluxo clínico/autorização. Não introduzir API, migração ou histórico de notas novo.

## Decisions
- Criar `disease_record_card` no módulo de componentes existente e selecioná-lo apenas na aba. Reutilizar a estrutura visual e tokens de `vaccine-record-card`, `perimeter_led` e campos compartilháveis de Medicamentos, evitando copiar toda a folha de estilos. Alterar o genérico afetaria consultas sem necessidade.
- Exibir estado uma vez, como badge legível para ativa, em_tratamento, curada e controlada. Ausente recebe Não informado; valor desconhecido continua identificável sem inferência clínica. Cor não substitui texto.
- Organizar evolução, consulta e veterinário em grade; descrição em bloco com whitespace preservado e quebra de palavras longas. Nomes profissionais prevalecem sobre ID; não fabricar CRMV.
- Reutilizar painel decorativo com cenário otimizado e, conforme revisão visual solicitada, ícone de coração com pulso no mesmo disco com 70% de opacidade de Vacinas e Medicamentos. Utilizar fundo padrão existente: sorteio por registro não é necessário para esta padronização e ampliaria o estado sem benefício funcional.
- Estender `_records_header` para Doenças, conservando seleção, loading e Atualizar. Vazio tem orientação específica; erro e retry continuam no wrapper clínico.
- A imagem é referência de hierarquia; notas recentes não serão simuladas. Consulta de origem abre o detalhe atual pelo ID existente.
- Ajuste visual solicitado após revisão: descrição e consulta de origem usam ícones e título em bloco acima do valor. Consulta aparece uma única vez abaixo da descrição, sem duplicação na grade.

## Risks / Trade-offs
- CSS compartilhado afetar Vacinas/Medicamentos → limitar ajustes exclusivos a classes disease-* e comparar as três abas.
- Descrição extensa deformar cartão → grade responsiva, min-width zero, quebra de linha e validação com textos longos.
- Módulos compilados divergirem na entrega → compilar conjunto completo, validar imports/navegação reais e reiniciar frontend se retiver módulos antigos; evitar cópias parciais de arquivos gerados.

## Migration Plan
Compilar e verificar em navegador com dados sintéticos. Aplicar entrega completa no servidor local preservando configuração de ambiente. Reversão restrita ao componente e composição/estilos desta mudança; sem alteração de dados persistidos.
