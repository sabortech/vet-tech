# Verificação

`consultation_card` exibe Ver prontuário somente quando a consulta tem status `finalizada`, dentro do controle de autorização existente. Histórico em Horários e no atendimento permanece no fluxo anterior. Nenhum endpoint ou chamada adicional foi criado.

- Compilação Reflex: passou (6,377 s).
- Navegador em produção isolada: seis cartões sintéticos. Botão ausente em agendada, em atendimento, cancelada, desconhecida e finalizada sem autorização; presente na finalizada autorizada. Iniciar/retomar preservados. Sem erros JavaScript.
- Evidências e harnesses em `evidence/`, sem dados reais.
- `openspec validate restringir-prontuario-consultas-finalizadas --strict`: passou.

## Ajuste de rótulo

O acionador da aba Consultas passou a se chamar **Ver histórico anterior**, conforme solicitado. Apenas o texto mudou; a condição de finalização, a autorização e o painel aberto são os mesmos. O harness foi atualizado e a importação do componente foi verificada.

## Tamanho e linha única

O rótulo passou a **Ver Histórico anterior**. As ações de PDF e histórico usam a mesma classe com largura total e altura de 40 px. A coluna de ações tem 192 px em desktop/tablet e acompanha a largura do cartão no celular; o texto não quebra linha. A URL do CSS foi versionada para atualizar o navegador.

Verificação no navegador passou em 1280, 1100, 768 e 390 px: dimensões iguais, texto sem quebra/corte e sem overflow horizontal. A matriz de estados continuou passando. Compilação Reflex passou em 6,999 s. Evidências em `evidence/results.json` e `evidence/buttons-*.png`.
