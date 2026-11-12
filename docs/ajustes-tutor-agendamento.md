# Ajustes da área do tutor

- Veterinários aparecem pelo nome nos registros, autorizações e PDF. Se o nome estiver ausente, aparece “Nome não informado”; os IDs continuam internos.
- O peso aparece com a unidade `Kg` no Dashboard, Prontuário e resumos clínicos. Valores ausentes continuam sem unidade.
- O painel inicial de agendamento permite escolher pet, veterinário compatível, dia e horário. Cada consulta mantém o par pet/médico escolhido, com autorização de acesso existente.
- Nas telas sem pet selecionado, o convite de agendamento abre dois cards: escolher em Mudar pet ou cadastrar em Meus Pets. A tartaruga fica na borda do painel; o layout se adapta ao celular.
- Controles habilitados recebem halo ao passar o mouse ou focar pelo teclado, respeitando as cores de status e de ação.
- Consultas e complementos usam cores de acompanhamento conforme os dados registrados, sem inferir medicação tomada ou saúde geral.

## Verificação

Testes unitários das projeções, nomes, peso, agendamento, calendário e PDF; compilação `reflex compile --dry`; validação OpenSpec. Prévias visuais dos temas claro/escuro em desktop/celular estão nas mudanças OpenSpec correspondentes.

## Publicação

O merge publica o código no repositório. Para disponibilizar os nomes, publicar também os artefatos Xano alterados: `Clinical/history`, `Clinical/consultation_document` e as leituras de consultas, acessos e auditoria do tutor. O frontend precisa ser atualizado no ambiente de execução. Nenhuma migração de dados é necessária.
