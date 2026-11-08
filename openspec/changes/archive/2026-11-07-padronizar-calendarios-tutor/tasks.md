# Tasks

## 1. Painel compartilhado e agendamento

- [x] 1.1 Estender o painel para dias indisponíveis, cabeçalho contextual e bloqueio de operação com defaults compatíveis; compilar e verificar calendário médico existente.
- [x] 1.2 Integrar o painel na primeira etapa do agendamento, com mês/ano, data brasileira, horário e continuação; testar dias passados, navegação, horários inválidos, bloqueio e ida/volta de etapas.

## 2. Nascimento do pet

- [x] 2.1 Adicionar estado de calendário de nascimento com mês/ano, dias, seleção e limpeza; testar futuro, data inválida, bissexto, fechamento, bloqueio e reset de sessão.
- [x] 2.2 Substituir o input nativo pelo painel compartilhado, mantendo ISO e dica brasileira; verificar seleção, cancelar e limpar no cadastro direto e modal Novo pet sem enviar formulário.

## 3. Integração e documentação

- [x] 3.1 Registrar o uso dos painéis e regras em docs/architecture.md e compilar a interface com escrita; verificar imports, CSS público e URL atualizada.
- [x] 3.2 Executar regressões de datas e calendário e teste de navegador com API sintética para agendamento/nascimento, temas e celular; registrar capturas e resultados, restaurando o frontend do servidor ativo.

- [x] 3.3 Corrigir a tela vazia no servidor ativo causada por imports de módulos desatualizados no Vite após recompilações; verificar a rota real no Chromium sem erro de export inexistente.

- [x] 3.4 Apresentar a data selecionada em campo próprio abaixo do calendário, junto ao horário, preenchido em formato brasileiro e somente leitura; verificar vínculo com a seleção no navegador sem preencher horário automaticamente.
