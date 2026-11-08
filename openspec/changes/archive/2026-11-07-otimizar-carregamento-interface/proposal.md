# Proposal

## Why
A navegação ficou lenta com leituras desnecessárias na abertura do pet, consultas sequenciais de raças e imagens decorativas grandes. Reduzir trabalho de rede e bytes transferidos preservando aparência e segurança.

## What Changes
- Carregar histórico/consultas do tutor ao entrar na área clínica, dispensando esse lote na abertura pelo Dashboard.
- Reutilizar transporte HTTP dentro de operações e limitar paralelismo de catálogos a quatro consultas.
- Servir versões WebP menores de cenários/mascotes e favicon compacto, mantendo originais.
- Medir contagem de chamadas, duração sintética e tamanho dos assets; verificar regressões e navegação.

## Capabilities
### New Capabilities
- `interface-performance`: eficiência de carregamento sem ampliar cache clínico ou permissões.
### Modified Capabilities
Nenhuma.

## Impact
Estados de autenticação/clínica, transporte Xano já existente, assets/referências e testes. Sem novas dependências de execução, APIs ou tecnologias. Preservar modo de execução atual do servidor, política de retries e autorização do backend.
