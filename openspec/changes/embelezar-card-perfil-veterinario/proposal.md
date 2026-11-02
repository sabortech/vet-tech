# Proposal

## Why
O card do veterinário na sidebar precisa comunicar melhor a identidade profissional e acompanhar o design do Vet Tech.

## What Changes
- Card com avatar de iniciais, nome em destaque, identificação da área médica, CRMV/UF e botão Sair redesenhado.
- Registro carregado do endpoint autenticado de conta já existente, com loading, ausência e falha honestos.
- Layout legível em temas claro/escuro, menu compacto e drawer móvel, mantendo os três destinos médicos e guard de saída das configurações.

## Capabilities
### New Capabilities
Nenhuma.
### Modified Capabilities
- `veterinarian-schedule-presentation`: card profissional compartilhado na sidebar médica.

## Impact
Componente veterinary_actions, metadados mínimos no estado autenticado, reaproveitamento da leitura de Configurações e CSS isolado. Sem API ou dependência nova, sem mutação do prontuário ou acesso de terceiros. CRMV/UF somente da própria conta autenticada; sem selo de verificação externa ou notificações.
