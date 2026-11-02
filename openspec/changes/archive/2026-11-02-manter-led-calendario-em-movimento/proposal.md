# Proposal

## Why
O usuário voltou a observar LED estático. Há uma regra de movimento reduzido que desliga a animação e ilumina a borda inteira, contrariando a solicitação explícita de percurso contínuo e suave.

## What Changes
- Manter segmento verde em movimento horário contínuo e linear, com ciclo suave de seis segundos.
- No modo de movimento reduzido, desacelerar para doze segundos sem congelar o traço ou acender toda a borda.
- Preservar efeito somente no pop-up e atualizar testes para observar movimento real, sem pausá-lo para validar.

## Capabilities
### New Capabilities
Nenhuma.
### Modified Capabilities
- `veterinarian-schedule-presentation`: manter circulação do LED também em movimento reduzido, com velocidade menor.

## Impact
CSS isolado do LED e testes visuais. Sem alterações em chat, calendários, dados, APIs ou autenticação.
