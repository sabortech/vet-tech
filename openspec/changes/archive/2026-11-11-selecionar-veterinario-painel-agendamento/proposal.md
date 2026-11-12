## Why
A escolha do médico existe na segunda etapa, mas não aparece no painel de calendário visto pelo tutor. Torná-la visível permite agendar cada pet com o profissional desejado.

## What Changes
- Escolher pet e veterinário pelo nome no painel inicial de data/horário.
- Carregar profissionais cadastrados compatíveis com a espécie e limpar seleção ao trocar pet.
- Mostrar resumo do pet e médico na confirmação; manter motivo e aviso de acesso prévio.
- Preservar vínculo por consulta, sem exclusividade permanente de pet para um médico.

## Capabilities
### Modified Capabilities
- `appointment-management`: escolha de profissional no painel inicial e vínculo explícito por consulta.

## Impact
Componentes e estado Reflex; reutiliza API autorizada existente, sem publicar alterações de backend. Prontuário continua sensível: autorização prévia é concedida apenas ao profissional escolhido, com regras e auditoria existentes. Sem alterações de notificações.
