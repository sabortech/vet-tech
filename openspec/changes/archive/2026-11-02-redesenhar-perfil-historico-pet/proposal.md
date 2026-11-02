# Proposal

## Why
O histórico anterior precisa de uma identidade visual de perfil, valorizando a foto do animal e colocando informações e contagens no topo.

## What Changes
- Cabeçalho do paciente inspirado em perfil: foto circular, nome, sexo, nascimento, peso informado e contagens reais das cinco categorias.
- Melhor hierarquia visual e responsividade mantendo mascote, registros, estados de leitura e fechamento existentes.
- Foto obtida somente após leitura autorizada: campo aditivo no contrato do pet e fallback para foto da agenda da mesma sessão quando disponível; patinha quando ausente ou imagem falha.

## Capabilities
### New Capabilities
Nenhuma.
### Modified Capabilities
- `veterinarian-schedule-presentation`: apresentação do histórico compartilhado como perfil do paciente.

## Impact
Composição em clinical.py, CSS e projeção do histórico no estado existente; campo foto na projeção Xano assert_access. Dados clínicos continuam sujeitos a autorização/auditoria do endpoint; sem novas mutações ou notificações. Sem biblioteca ou dependência de rede nova.
