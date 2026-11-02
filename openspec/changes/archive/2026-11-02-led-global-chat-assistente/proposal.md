# Proposal

## Why
O usuário deseja no chat o mesmo traço luminoso suave do calendário, para todas as telas e perfis.

## What Changes
- Adicionar traço verde somente no perímetro da janela aberta do chat, circulando no sentido horário.
- Manter ciclo linear de 6s e ritmo reduzido de 12s, igual ao calendário.
- Adaptar o contorno ao painel arredondado desktop e chat fullscreen móvel, sem afetar mensagens, tema ou interação.

## Capabilities
### New Capabilities
Nenhuma.
### Modified Capabilities
- `interface-preferences`: borda luminosa global do assistente, independente de tela ou perfil.

## Impact
Controlador visual JS e CSS compartilhados do chat. Sem backend, dados, permissões ou mudanças de transporte n8n. Testes usam respostas simuladas e não enviam perguntas à IA.
