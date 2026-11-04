## MODIFIED Requirements
### Requirement: Gancho público de clique sem chat
Ao ser ativado, o botão SHALL publicar uma única ocorrência de vettech:mascote-click. O consumidor local SHALL abrir o chat de suporte, sem fazer chamadas ao backend pela abertura.
#### Scenario: Ativação
- **WHEN** uma pessoa clica ou ativa com Enter ou Espaço
- **THEN** o evento é disparado uma vez e o chat abre
