# Tarefas

As marcações registram implementação e verificação dos critérios, com evidências em `verification.md` e `smoke-result.json`. Concluir as tarefas não arquiva automaticamente a change.

## 1. Modelo e compatibilidade

- [x] 1.1 Inventariar tabelas clínicas/permissões e divergências locais/remotas específicas, incluindo `exame`; entregar relatório de contagens, conflitos e digests privados sem dados pessoais no repositório, identificando migrações bloqueadas sem escrever remotamente.
- [x] 1.2 Preparar evolução aditiva de consulta, vacinas, medicamentos, exames, autorizações e logs, com estado, timestamps, versões, origem e índices; verificar scripts e dry-run restrito, preservando IDs e campos legados conforme o relatório.
- [x] 1.3 Preparar catálogo/associativas de doença e plano de migração não destrutivo; testar mapeamentos, ausência de associação inventada e preservação de referências, atualizando domínio/DER e documentação dos campos antes de aplicar.

## 2. Consentimento e auditoria

- [x] 2.1 Implementar verificações compartilhadas de dono, perfil, consentimento e responsabilidade pela consulta; testar tokens cruzados, IDs coincidentes/alheios e outro veterinário autorizado que tenta escrever consulta de terceiro.
- [x] 2.2 Implementar concessão vinculada ao agendamento, consulta/reativação/revogação pelo dono e serialização com escrita clínica; verificar unicidade do vínculo, revogação durante atendimento, retomada após reativação e falha sem concessão órfã.
- [x] 2.3 Implementar auditoria transacional de leituras/gravações clínicas e consulta dos logs pelo tutor; testar falha de log sem sucesso clínico, imutabilidade, propriedade e não duplicação em repetição de operação; documentar os contratos.

## 3. Agendamento e agenda

- [x] 3.1 Implementar busca autenticada de veterinários por espécie do pet próprio com projeção mínima; testar incompatibilidade, pet alheio e ausência de profissional, sem expor credenciais, email ou dados clínicos.
- [x] 3.2 Implementar reserva idempotente com consentimento atômico, faixa 08h–17h inclusiva e fuso America/Sao_Paulo; testar limites, passado, dupla reserva concorrente por profissional/pet e chave repetida com payload divergente.
- [x] 3.3 Implementar listagens do tutor, agenda diária de Horários e lista paginada de próximas consultas/pendências do profissional; testar ordenação, limites de dia no fuso, agendada atrasada, atendimento aberto, exclusão de finalizadas, isolamento e resposta mínima sem consentimento; documentar parâmetros e códigos.
- [x] 3.4 Implementar começo/retomada da consulta pelo responsável; testar início antes do horário agendado, idempotência, consentimento revogado e impossibilidade de reiniciar finalizada sem criar outro atendimento.

## 4. Rascunho e complementos clínicos

- [x] 4.1 Implementar leitura e salvamento versionado do rascunho estruturado; verificar retomada, conflito entre editores, campos/IDs forjados e ausência de rascunho nas respostas do tutor, documentando dados obrigatórios e opcionais.
- [x] 4.2 Implementar linhas de vacinação com nome, aplicação, lote e próxima dose; testar datas inconsistentes, dose futura distinta de aplicação e ausência legítima de vacinação na consulta.
- [x] 4.3 Implementar prescrições com dose/unidade, frequência, via, tipo e período; testar decimais, uso contínuo sem fim, fim anterior ao início e leitura legível dos campos legados sem conversão destrutiva.
- [x] 4.4 Implementar busca/criação mínima de doença, diagnóstico pontual e evolução individual datada; testar catálogo normalizado, isolamento entre pets, versões concorrentes e consulta antiga finalizada depois sem regressão do estado mais recente.
- [x] 4.5 Implementar solicitação e resultado textual de exames com datas e estados, sem exigir arquivo; testar solicitação sem resultado, realização válida, vínculo cruzado inválido e preservação de exames/arquivos legados; atualizar o requisito documental antigo de anexo obrigatório.

## 5. Finalização e leitura publicada

- [x] 5.1 Implementar finalização transacional de cabeçalho, complementos, condições e auditoria; verificar rollback de falha intermediária, clique duplo, versão conflitante e revogação concorrente sem publicação parcial.
- [x] 5.2 Implementar detalhe publicado e projeções por pet para Vacinas, Medicamentos e Doenças com data, autoria e consulta de origem; testar mesmos IDs nas duas leituras, filtros de propriedade, ocultação de rascunhos e tratamento explícito de registros legados sem consulta.
- [x] 5.3 Proteger consultas finalizadas contra edição/reabertura nesta entrega e respostas de repetição contra acesso indevido; verificar que o tutor mantém histórico após revogar o profissional e documentar os limites de edição e atualização posterior de exames.

## 6. Interface do tutor e do veterinário

- [x] 6.1 Implementar Agendar consulta no dashboard do tutor e pop-up de duas etapas (dia/horário; pet/motivo/profissional compatível), com consentimento antes da confirmação; verificar abertura sem pet global, seleção independente, Voltar preservando campos, fechamento sem escrita/foco, tutor sem pets, conflitos, timeout idempotente e descarte de buscas antigas ao trocar pet no diálogo.
- [x] 6.2 Compor menu veterinário com Horários e Consultas, tela de calendário vertical diário e lista de próximos atendimentos/pendências; verificar Hoje, mudança de dia, ordem cronológica entre dias, mesma reserva nas duas visões, estados vazios, teclado/celular e Começar/Retomar na lista Consultas levando à tela clínica sem trava pelo relógio.
- [x] 6.3 Implementar tela própria de atendimento com cabeçalho do pet, dados gerais, complementos repetíveis, Salvar rascunho e Terminar consulta; verificar URL direta, versão, perda de resposta, retorno à agenda e aviso de alterações locais não salvas.
- [x] 6.4 Integrar agendamentos criados no pop-up do dashboard, detalhe finalizado, seções clínicas e permissões/logs a Consultas e ao menu do tutor; verificar consulta no pet correto sem troca silenciosa do pet global, datas/origem, navegação de volta, revogação e mesmos registros entre consulta e seção.
- [x] 6.5 Integrar novos estados à única sessão existente e limpeza de pet/consulta; testar logout, expiração, troca de perfil e respostas antigas, executar suíte pertinente e compilação conforme skills Reflex e atualizar documentação da composição.

## 7. Verificação conjunta e implantação

- [x] 7.1 Executar percurso integrado dashboard tutor → pop-up etapa 1/etapa 2 → reserva/consentimento → Horários (calendário vertical) → Consultas (próximas e Começar consulta) → leitura prévia → início manual → rascunho → finalização → consulta completa e seções do tutor; comprovar múltiplos pets/profissionais e complementos vazios/válidos em desktop/celular, distinguindo mocks de execução real.
- [x] 7.2 Preparar bundle/dry-run, plano de smoke compatível com a conta disponível e reversão preservando histórico; apresentar destino, efeitos e fixtures antes da implantação e, após autorização, publicar somente artefatos necessários, confirmar integridade dos registros anteriores e remover apenas fixtures sintéticas criadas para essa verificação.
- [x] 7.3 Reconciliar documentação final e evidências com as cinco specs da change; executar validação estrita, revisar cobertura de cada cenário e registrar explicitamente qualquer bloqueio, sem marcar tarefas completas com teste omitido ou funcionalidade parcial.

## Workflow follow-up

- Revisar os padrões do MVP descritos no design antes da implementação, em especial fuso, limites inclusivos, conflito por início idêntico e exclusões de cancelamento/remarcação.
- Sincronizar specs e arquivar somente após entrega e revisão; não tratar a change aberta `assess-project-improvements` como concluída automaticamente.
