# Verificação

## Implementação

O agendamento e o nascimento do pet agora usam `calendar_panel`, o mesmo painel da área médica: mensagem contextual, tartaruga, LED de contorno, seletores de mês/ano, destaque de hoje e data selecionada. Cada domínio mantém seu próprio estado e seus eventos; navegação de calendário não consulta APIs.

No agendamento, o painel integra a primeira etapa de dia e horário. Datas passadas ficam visíveis e desabilitadas, e o evento rejeita seleção passada/inválida. O envio e operações de resultado incerto bloqueiam alterações. A seleção não fecha o agendamento; Continuar valida 08h–17h e data/hora futura. Voltar conserva a seleção e Cancelar fecha usando o evento existente. A segunda etapa mostra a data brasileira e conserva pet, motivo, profissional e consentimento.

O nascimento substitui o seletor nativo no cadastro direto e no modal Novo pet. Rejeita dias futuros/inválidos, aceita bissexto válido, conserva ISO no rascunho e no payload e exibe formato brasileiro. Limpar apaga somente o campo; fechar/cancelar preserva o rascunho. Reset do formulário e logout limpam o painel. Nenhum endpoint ou contrato Xano foi alterado.

## Verificação automática

- `PYTHONPATH=tests/unit .venv/bin/python -m unittest test_tutor_calendar test_attendance_calendar test_date_contract test_dashboard test_auth_state test_clinical_validation`: **91 testes passaram**.
- Cobertura específica: mês/ano sem mudar seleção, grade de 42 posições, passado no agendamento, futuro no nascimento, bissexto, datas malformadas, bloqueio de envio e resultado incerto, limites de horário, ida/volta de etapas, cancelamento, limpeza e logout.
- `reflex compile --dry`: passou.
- O roteiro de navegador realizou build de produção com sucesso. Compilação final com escrita executada para atualizar a interface em uso.
- `openspec validate padronizar-calendarios-tutor --strict`: validação da mudança.

## Navegador

`tests/integration/tutor_calendar_browser.py` inicia Reflex de produção e API HTTP sintética locais; não usa contas ou dados reais. O roteiro restaura a configuração frontend após o build e ao encerrar e finaliza somente os processos que inicia.

Passaram os cenários de:

- Agendamento: painel compartilhado, mês/ano, dia passado desabilitado, seleção futura, rejeição de 07h59, aceitação de 08h, segunda etapa, retorno com seleção preservada e cancelamento.
- Nascimento: dia futuro desabilitado, seleção de 29/02/2024, exibição brasileira, limpeza e preservação dos outros campos.
- Novo pet: diálogo aninhado fecha por Escape ou seleção sem fechar o cadastro; navegar no calendário não envia formulário; cadastro sintético recebeu `data_nasc: 2024-02-29`.
- Regressão médica: a agenda mantém o painel compartilhado e seus seletores.
- Capturas e verificação de ausência de overflow horizontal em 1440 e 390 px, nos temas claro e escuro, para os dois painéis.

Não houve erros JavaScript. Resultados em [results.json](evidence/results.json).

## Evidências visuais

- [Agendamento — desktop claro](evidence/agendamento-1440-light.png)
- [Agendamento — desktop escuro](evidence/agendamento-1440-dark.png)
- [Agendamento — celular](evidence/agendamento-390-dark.png)
- [Nascimento — desktop](evidence/nascimento-1440-light.png)
- [Nascimento — celular](evidence/nascimento-390-dark.png)
- [Agenda médica preservada](evidence/calendario-medico.png)

## Ajustes identificados e limites

O teste encontrou falha de fechamento ao cancelar após retornar da segunda etapa: os controles de fechar do painel receberam callback explícito do agendamento/nascimento, preservando o mecanismo padrão dos consumidores anteriores. A regra global de botões pill foi excluída somente dentro dos novos painéis para respeitar o arredondamento dos controles compartilhados.

Não foram confirmados agendamentos contra Xano real nem criados pets reais. Horários disponíveis e compatibilidade de profissional continuam sujeitos aos serviços existentes; a API sintética não oferece profissionais, por isso algumas capturas exibem essa mensagem de ausência. A inspeção de responsividade e foco não equivale a auditoria completa de acessibilidade.


## Tela vazia no servidor de desenvolvimento — correção

Reproduzido no Chromium contra localhost:3000: o console registrou `Error loading route module` e `does not provide an export named ...` no componente memoizado do Dashboard. Os arquivos em disco continham os exports esperados (97 imports conferidos), mas o grafo de módulos do Vite mantinha versões incompatíveis após recompilações/builds compartilhados. Atualizar o mtime de `.web/vite.config.js` forçou o restart do grafo sem reiniciar o backend ou alterar dados. A consulta real seguinte carregou a rota e redirecionou a sessão de diagnóstico sem login para `/login`, sem erro de importação, pageerror ou requestfailed. Permaneceu um aviso de hidratação de atributos de tema, não bloqueante, fora do escopo desta correção.

O teste de calendário agora usa workspace temporário: copia app/config e arquivos gerados, reutiliza apenas dependências instaladas e assets de leitura, e produz todos os módulos e o build fora da `.web` ativa. O fluxo isolado executou todos os cenários de calendário com zero erros JavaScript. Houve uma corrida na limpeza final do diretório temporário após o sucesso dos cenários; o cleanup passou a ser best-effort e o ciclo de criação/limpeza foi verificado separadamente. A proteção por comparação de bytes de módulos/configuração ativos foi incorporada ao roteiro; hashes da aplicação em uso permaneceram iguais durante o teste isolado. A rota real foi conferida novamente após esse teste.

Nenhuma compilação da aplicação ativa foi executada após o restart do grafo, para evitar reintroduzir o conflito durante a recuperação. Nenhuma sessão real foi acessada pelo diagnóstico e nenhum registro remoto foi modificado.

## Campo de data junto ao horário

A seleção anteriormente aparecia apenas na lateral; o campo inferior era exclusivo do horário. Adicionado campo próprio “Data selecionada”, somente leitura, vinculado a booking_day e à apresentação brasileira, imediatamente acima do horário. Selecionar um dia preenche esse campo sem inventar horário. A indicação lateral permanece. O navegador isolado confirmou valor 08/01/2027 após seleção, atributo readonly e horário ainda vazio, e passou novamente pelos demais cenários com nenhum erro JavaScript. Captura em `evidence/agendamento-data-preenchida.png`. O build isolado passou, os módulos/configuração ativos foram preservados e o componente gerado pelo servidor de desenvolvimento contém o novo campo. Não foi executada compilação externa na .web ativa.
