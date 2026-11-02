# Proposal

## Why
A tela Atendimento não acompanha a identidade visual do tutor. A apresentação deve melhorar leitura, organização e uso em celulares.

## What Changes
- Wallpaper fixo com overlay, card de vidro e tokens reutilizáveis para o médico.
- Cabeçalho, resumo do paciente, campos organizados, quatro cards clínicos e ações responsivas.
- Histórico anterior em modal responsivo com tartaruga existente, seções com ícones, carregamento, erro e estados vazios; fechamento sem perder o rascunho.
- Campos de data do atendimento e registros clínicos abrem calendário em painel com mês/ano e LED animado, reutilizando a apresentação da agenda. Selecionar/limpar modifica somente o rascunho local pelo fluxo existente.
- Notificação visual de sucesso no canto inferior esquerdo após confirmação de rascunho salvo ou consulta finalizada, inclusive após reconciliação de resposta incerta. Finalização retorna a Horários no dia agendado e recarrega os cards.
- Cards médicos com detalhes verdes; LED SVG circulando no sentido horário no perímetro da agenda do dia e da foto do pet, também nos cards da lista Consultas.
- Halo verde acompanha apenas o segmento do LED em calendários, agenda, moldura do pet e chat.
- Atendimento e seus painéis/notificações seguem imediatamente o tema claro/escuro já salvo pelo usuário, inclusive ao alternar com calendário ou histórico abertos.
- Ícone global da aba com o rosto do mascote em todas as páginas, enquadrado para leitura em tamanho pequeno.
- Histórico dos cards de Horários/Consultas reutiliza exatamente o painel do atendimento com alvo correto por pet. Todos os botões do sistema passam a ter cantos arredondados.
- Preservação de autorizações, rotas, contratos e regras de gravação.

## Capabilities
### New Capabilities
Nenhuma.
### Modified Capabilities
- `interface-preferences`: LED do chat alterna entre o contorno superior e inferior cruzando a divisória do banner, em percurso de oito.
- `veterinarian-schedule-presentation`: retorno à agenda após finalização confirmada, card concluído, estilo verde e LED na agenda/foto.

## Impact
Composição em clinical.py, apresentação compartilhada de calendário em date_input.py e estado transitório em features/clinical/state.py; CSS isolado e composição dos cards em veterinary_schedule.py. O retorno usa a leitura autenticada da agenda já existente, mantendo autorização, auditoria e tratamento de consentimento no backend. Não muda contratos nem cria notificações externas ou dependências de produção. A imagem existente será utilizada. Verificação por compilação e navegador com dados sintéticos, sem mutações no prontuário real.
