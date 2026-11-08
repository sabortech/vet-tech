# Proposal

## Why

A listagem atual do Dashboard usa cartões verticais simples e não reproduz a composição visual desejada. Remodelar a visão geral a partir do card completo da Jessy no protótipo permite reunir identificação, indicadores e acompanhamento em uma apresentação consistente para todos os pets.

## What Changes

- Adotar cards brancos com foto retangular à esquerda, nome marrom em destaque, espécie, raça e idade; três indicadores bege para peso cadastrado, próxima vacina e última consulta.
- Exibir faixa visual de vacinas, bloco “Acompanhamento detalhado”, próximo evento e quatro ações em todos os cards, inclusive quando faltarem dados.
- Organizar os pets em duas colunas no desktop e uma coluna em telas menores, sem sobreposição entre cards.
- Aplicar `assets/fundopets.jpeg` ao fundo da área principal do Dashboard, conservando a navegação compartilhada e a convivência com o mascote e o chat existentes.
- Manter textos em português brasileiro, filtro de escopo, dados reais e estados de carregamento, erro e ausência de pets.

- Evolução autorizada: dar função temporal à faixa de vacinas com LED de prazo, texto acessível e abertura da seção Vacinas do pet, sem percentual de imunização nem notificações adicionais.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `tutor-dashboard`: apresentação responsiva da listagem, card completo compartilhado e fundo conforme referência visual.

## Impact

- Implementação concentrada em `vet_tech/components/dashboard.py` e estilos locais em `assets/vet_tech.css`; preservar composição da rota em `vet_tech/pages/dashboard.py`.
- Reutilizar estado e projeções de `vet_tech/features/dashboard/state.py`, ações existentes e backend Xano. Não exigir novos endpoints, dependências ou mudanças no modelo de dados.
- Os resumos contêm dados de saúde dos pets: manter validação de propriedade no backend e mecanismos existentes de auditoria nos destinos clínicos; não adicionar exposição pública ou telemetria clínica.
- Não alterar notificações automáticas nem criar alertas com base apenas na aparência do protótipo.
- Verificação visual em navegador e regressão dos testes existentes de Dashboard e datas.


## Evolução: cabeçalho semelhante a Consultas
Padronizar o topo com título e descrição, atualização verde à direita e filtro em superfície separada. Preservar fundo, escopos e ações existentes.
