# Menu persistente do tutor

## Revisão: remoção de Novo pet
Novo pet foi retirado da composição do menu, mantendo o cadastro em Meus Pets,
Mudar pet junto às abas e Sair no rodapé. Compilação aprovada em 3,346 segundos.
Roteiro de navegador aprovado na porta 3001 com ausência de Novo pet nas oito
telas e ações/guard restantes preservados. Expectativas dos testes atualizadas.

O layout compartilhado compõe nove entradas do catálogo, seguidas de Novo pet
e Mudar pet no grupo principal. Somente Sair ocupa o rodapé. A lista de navegação
pode rolar em telas baixas; header e rodapé não encolhem. O menu veterinário
continua usando sua composição explícita.

Novo pet abre o modal existente onde não há formulário e foca o formulário
já visível em Meus Pets, evitando duplicação de IDs/campos. Mudar pet mantém
o modo de seleção, com destaque ativo. Em Configurações, Mudar pet e Sair
respeitam o guard de descarte; mudança de pet não é autorizada para perfil
veterinário pelo novo action de Configurações.

32 testes unitários de navegação, configurações e perfis aprovados. Compilação
completa aprovada em 3,584 segundos. `persistent_menu_browser.py` aprovado nas
portas 3000 e 3001: verifica ordem constante em oito telas, footer somente Sair,
foco no formulário, abertura/cancelamento do modal, seleção, bloqueio por
rascunho nas ações Mudar pet/Sair, navegação móvel e saída visível em 1440x600,
1440x900 e 390x844. Sem exceções JavaScript. Nenhum dado real foi alterado.
Capturas e results.json nas pastas por porta. OpenSpec estrito e whitespace
aprovados; expectativa do roteiro de menu anterior atualizada para as 11 entradas.
