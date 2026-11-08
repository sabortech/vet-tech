# Spec Delta

## ADDED Requirements

### Requirement: Nascimento do pet usa painel compartilhado de calendário
O cadastro de pet SHALL oferecer o painel visual compartilhado com a área médica para selecionar nascimento, com seletores de mês/ano, LED, dia atual e seleção destacados e opção de limpar o campo opcional. Datas futuras SHALL ficar indisponíveis e ser rejeitadas no evento de seleção. A data SHALL continuar armazenada no rascunho como ISO e exibida em formato brasileiro, sem conversão de fuso. Abrir, navegar ou cancelar o painel SHALL NOT enviar o cadastro nem alterar os outros campos. Encerrar a sessão ou reiniciar o formulário SHALL limpar o painel.

#### Scenario: Escolher nascimento
- **WHEN** o tutor escolhe uma data de hoje ou anterior no painel
- **THEN** a data é preenchida em ISO no rascunho, apresentada em formato brasileiro e o painel fecha retornando ao cadastro

#### Scenario: Limpar ou cancelar
- **WHEN** o tutor limpa a data ou fecha sem escolher outro dia
- **THEN** o campo respectivamente fica vazio ou mantém a seleção anterior, sem submeter o formulário

#### Scenario: Futuro ou envio em andamento
- **WHEN** o tutor tenta escolher uma data futura ou mudar a seleção durante envio do cadastro
- **THEN** o evento impede a alteração, mantendo a validação final do cadastro existente
