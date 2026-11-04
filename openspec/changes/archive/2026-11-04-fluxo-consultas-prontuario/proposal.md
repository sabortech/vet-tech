# Proposta

## Why

O tutor já cadastra e seleciona pets, e o veterinário já possui identidade autenticada, mas não existe percurso entre marcar um atendimento e consultar seus resultados. Esta change entrega esse ciclo do MVP: agendamento, agenda do profissional, prontuário estruturado durante o atendimento e publicação para o tutor ao finalizar.

## What Changes

- Disponibilizar Agendar consulta no dashboard/tela inicial do tutor, abrindo um pop-up de duas etapas: primeiro selecionar dia e horário livre entre 08h e 17h; depois selecionar pet próprio, motivo e veterinário compatível. Não exigir pet previamente aberto no dashboard. Ao confirmar, conceder acesso prévio ao histórico desse pet ao profissional escolhido, com indicação clara na interface.
- Criar duas entradas no menu lateral veterinário: Horários abre uma tela de calendário vertical com as consultas agendadas; Consultas abre a lista dos próximos atendimentos com Começar consulta/Retomar. Essas ações levam à tela de prontuário sem exigir que o relógio tenha atingido o horário agendado.
- Abrir tela própria de atendimento com motivo, diagnóstico, observações e registros datados de vacinas, doenças, prescrições e exames. Prontuário significa dados preenchidos na plataforma e persistidos no banco; não exige documento ou upload.
- Salvar rascunhos protegidos durante o atendimento; Terminar consulta valida e publica o conjunto de forma atômica, sem duplicar dados em cliques repetidos.
- Disponibilizar ao tutor a consulta completa com data/autoria e os mesmos registros nas seções Vacinas, Medicamentos e Doenças do pet, mantendo a entrada Consultas no menu. Exames ficam acessíveis dentro da consulta.
- Implementar autorização por pet/veterinário, revogação pelo tutor e auditoria no backend, necessárias para leitura prévia e escrita clínica.
- Reconciliar tabelas clínicas legadas com o domínio, preservando IDs, histórico e referências; substituir os placeholders das áreas envolvidas.

## Capabilities

### New Capabilities

- `appointment-management`: pop-up de agendamento em duas etapas, horário comercial, conflitos, calendário vertical em Horários e lista de próximos atendimentos em Consultas do veterinário.
- `clinical-records`: atendimento com rascunho, registros clínicos estruturados, finalização e histórico consolidado por pet.
- `record-access-control`: consentimento no agendamento, consulta prévia, revogação e auditoria das operações clínicas.

### Modified Capabilities

- `authenticated-navigation`: botão no dashboard do tutor abre o agendamento em duas etapas; seções clínicas apresentam registros reais e acesso à consulta de origem.
- `veterinarian-identity`: menu profissional com Horários e Consultas, levando ao calendário vertical e à lista com início/retomada do atendimento autorizado.

## Impact

Frontend Reflex: composição das áreas em `vet_tech/pages/profile.py`, menu em `vet_tech/components/navigation.py`, novas páginas/componentes de agenda e atendimento e estados próprios integrados à sessão existente. Backend Xano: novas operações autenticadas e revisão de `consulta`, `vacina`, `medicamento`, `doenca`, `exame`, `acesso_autorizado`, `log_acesso` e associativas clínicas ausentes. Sem nova tecnologia ou dependência de plano Pro/sandbox para a proposta.

Há dados sensíveis de saúde e identificação: cada operação valida identidade, propriedade ou consentimento ativo no backend; a agenda expõe somente informações necessárias e os rascunhos não são visíveis ao tutor. Agendar é uma ação explícita de consentimento, não uma permissão derivada apenas de conhecer o ID do pet. Revogar bloqueia o veterinário imediatamente, preservando os registros que o tutor continua podendo ler.

Esta entrega reúne etapas antes separadas no roadmap arquivado: agenda, autorização/auditoria, consulta e complementos clínicos. A proposta aberta `assess-project-improvements` contém requisitos relacionados a acesso, mas não é uma implementação nem será automaticamente encerrada por esta change. O planejamento anterior permanece como histórico.

Ficam fora desta entrega: documentos/PDF/upload, pagamentos, telemedicina, notificações automáticas, confirmação manual de agenda, duração/grade de disponibilidade, cancelamento/remarcação e alteração/reabertura de consulta finalizada. Datas de próxima dose e de retorno são armazenadas quando informadas, sem prometer envio de lembretes. Os limites de horário e outros padrões do MVP são explicitados no design para revisão.
