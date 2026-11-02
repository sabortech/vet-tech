# Design

## Context
Consultas usa a agenda autenticada paginada de 25 itens. O modelo pet não tem campo de alergias; o histórico fornece doenças e diagnósticos nomeados, e seu endpoint já valida consentimento e audita a leitura.

## Goals / Non-Goals
Reproduzir composição, verde suave, cards selecionáveis e resumo lateral do protótipo, preservando navegação, assistente, tema e fluxos clínicos. Listar registros com status cancelada sem introduzir uma operação para cancelar ou confirmar consultas.

## Decisions
- Novo componente de Consultas junto ao componente de agenda; estado no ClinicalMixin existente, sem segunda sessão.
- Parâmetros aditivos na agenda para aba/busca/estado, aplicados antes da paginação. Sem parâmetros, o comportamento da agenda permanece igual. Não mostrar contagens fictícias; total se refere ao filtro ativo.
- Resumo é carregado apenas por seleção explícita através do histórico autorizado e auditado. Contador próprio de geração, limpeza ao atualizar/navegar/sair e validação de sessão impedem respostas antigas.
- Alergias: mostrar nomes e estados dos registros de doenças/diagnósticos cujo nome identifica alergia (raiz alerg). Informar a fonte e ausência como “Alergias não informadas”; não inferir substâncias de texto livre. Campo dedicado e cadastro de alergias ficam fora deste redesign.
- Peso preserva unidade original sem inventar kg. Última vacina/consulta são ordenadas por data. Motivo do agendamento não será rotulado como observação do tutor.
- babyturtle.png decorativa no rodapé do resumo, com espaço reservado, sem posicionamento flutuante.

- Aba Canceladas filtra status cancelada; consultas canceladas ficam fora das abas ativas e não oferecem iniciar/retomar. Contrato da agenda sobe para 2; versão 1 continua aceita para filtros anteriores, mas não comprova suporte a Canceladas.
- Campo de busca usa radius full e CSS em seu contorno real; ícone sliders-horizontal acompanha o seletor no mesmo contorno arredondado.

## LED por estado da consulta
- Reutilizar perimeter_led SVG existente, com retângulo arredondado no perímetro do card e stroke-dashoffset negativo (sentido horário). Usar classe de estado para definir cor e drop-shadow em camadas no segmento, sem sombra colorida fixa na caixa.
- Verde #79ed4d para finalizada, vermelho #ff5252 para agendada e amarelo #facc15 para em_atendimento. Canceladas/estados desconhecidos ficam sem LED. O estado textual permanece visível.
- SVG decorativo absoluto não ocupa célula do grid, não intercepta eventos e permite halo externo sem recorte. Perímetro em Consultas e moldura da foto em Horários; preservar menu, assistente e LEDs do calendário/agenda do dia. Movimento reduzido desacelera para 12s, mantendo circulação.

## Risks / Trade-offs
- Endpoint remoto antigo ignora filtros novos: frontend verifica eco do filtro e apresenta aviso de contrato não atualizado, evitando resultados incorretos. Publicação Xano é necessária para ativar filtros globais.
- Dados incompletos: placeholders explícitos e alternativa neutra para foto.
- Celular: resumo abaixo da lista e controles quebrando linha; tokens existentes para temas.

## Migration Plan
Publicar o contrato aditivo de agenda no Xano antes do frontend. Sem migração de tabelas. Reverter componente, estado, CSS e agenda para rollback.

## LED no resumo do paciente
O resumo reutiliza o mesmo componente SVG e as cores dos cards. Status da consulta selecionada acompanha os dados do resumo somente após leitura autorizada confirmada, sob a mesma proteção de sessão/geração. Limpar seleção, trocar de filtro, falhar a leitura ou sair remove também o LED. Sem seleção, canceladas e estados desconhecidos permanecem sem LED. A cor representa a consulta selecionada, mesmo que o pet possua outras consultas.

## Paleta completa por estado
Centralizar tokens de destaque, ação sólida e texto da ação nos próprios cards/resumo. Aplicar vermelho/agendada, amarelo/em atendimento e verde/finalizada a botões, ícones Lucide, badge, nome do pet, título do resumo, contornos, foco e superfícies suaves. No tema claro, amarelo de texto usa tom ocre escuro para contraste; botão amarelo usa texto escuro. Estados cancelados/desconhecidos ou sem seleção usam neutro. Foto real e babyturtle preservam pixels. Substituir emoji azul do fallback por ícone vetorial decorativo, oculto quando o avatar carrega foto, inclusive preservando fallback em erro de imagem. Menu, toolbar global, assistente e histórico em portal mantêm seus temas; o gatilho Ver prontuário no card segue seu status. Sem mudança de dados, eventos ou API.

## Uniformidade do resumo e card selecionado
Resumo confirmado e card selecionado compartilham a mesma regra CSS de fundo (88% superfície, 12% cor do estado) e borda de destaque. Isso elimina a diferença anterior entre fundo do resumo a 3% e seleção a 12%, em todos os status e temas.

## Paleta compartilhada em Horários
Estender os seletores dos tokens de consulta para vet-schedule-card e seus estados existentes. Remover regras verdes fixas antigas e usar os mesmos tokens de ações, ícones, nome, badge, bordas, fundo e foco de Consultas. LED circular da foto preserva geometria, velocidade e movimento reduzido, mas traço/halo seguem a cor do status. A agenda do dia e calendário mantêm seus LEDs verdes. Preservar dados, horários, histórico e início/retomada; sem API nova.

## Faixa lateral em atendimento
A faixa lateral do card de Horários em atendimento usa amarelo claro #fde047 em ambos os temas. Textos/ícones preservam o tom contextual com contraste; a mudança é apenas na borda esquerda.

## Atendimento contextual e LED do formulário
Classe attendance-page--status deriva de clinical_status confirmado pelo fluxo existente. Estender os tokens compartilhados por estado ao formulário e, por seletores html:has da página, aos portais de histórico/calendário/seletor de data, sem alterar seu tema fora do atendimento. Adaptar tokens --vet-* preservando vidro, wallpaper, texto neutro e contraste. Ações sólidas usam cor de ação e texto contrastante; títulos, ícones, foco e outline usam o destaque legível. Sem alteração de eventos, contratos ou regras clínicas.
Reutilizar consultation_status_led parametrizado com raio 23px e classe própria para o painel inteiro, absoluto e sem eventos. Altura acompanha adição de registros e viewport. Movimento horário em 6s com halo do segmento; preferência reduzida usa 12s, sobrepondo a antiga regra que desativava todas as animações no atendimento. Sem status válido, nenhum LED.
