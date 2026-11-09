# Ajustes da agenda do veterinário

Na aba **Consultas**, o botão **Ver Histórico anterior** aparece nas consultas finalizadas com autorização vigente. Ele abre o histórico do pet. O texto fica em uma linha e o botão tem as mesmas dimensões de **Exportar PDF**.

Na aba **Horários**, o LED percorre o contorno do cartão conforme o status:

- Vermelho: consulta agendada, ainda não iniciada.
- Amarelo: em atendimento.
- Verde: finalizada.

Canceladas ou com status desconhecido ficam sem LED no contorno. A animação acompanha o tamanho do cartão e fica mais lenta com movimento reduzido. Ela usa CSS, sem requisições adicionais.

Verificação: compilação Reflex, validação OpenSpec e testes no navegador com dados sintéticos, temas claro/escuro e telas de desktop/celular. Relatórios e evidências ficam nos arquivos arquivados do OpenSpec em `openspec/changes/archive/2026-11-09-*`.
