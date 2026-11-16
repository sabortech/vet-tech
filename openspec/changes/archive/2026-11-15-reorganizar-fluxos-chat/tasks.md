# Tasks

## 1. Ponte e encaminhamento
- [x] 1.1 Separar leitura de pets da lista de tickets e verificar com teste unitário sem serviços externos.

## 2. Interface e economia
- [x] 2.1 Reorganizar cabeçalho, LED, cartões, formulário e erro; verificar screenshots mobile/desktop e temas com ponte simulada.
- [x] 2.2 Preservar retry e isolamento; suspender polling ocioso; verificar por teste de navegador com contagem de requisições.
- [x] 2.3 Documentar comportamento e limites de consumo em docs/chat-veterinario.md.

## 3. Integração
- [x] 3.1 Executar testes unitários relacionados, validação OpenSpec e compilação Reflex; registrar resultados.

## 4. Ajuste solicitado do banner

- [x] 4.1 Restaurar largura integral e altura proporcional 16:9, removendo limites de 120/150/90px; verificar no navegador e manter documentação coerente.
- [x] 4.2 Sincronizar as cópias geradas de CSS do servidor em execução e verificar dimensões do banner na aplicação real: 378 × 213px, sem limite de altura.

## 5. Navegação integrada

- [x] 5.1 Integrar visualmente os botões superiores ao cabeçalho e conferir na aplicação real em celular e desktop.

## 6. Título da lista

- [x] 6.1 Centralizar o título Atendimentos na faixa da lista com regra restrita ao modo list e sincronizar o CSS servido.
- [x] 6.2 Remover a divisória abaixo do título Atendimentos somente na lista e sincronizar os estilos servidos.
- [x] 6.3 Igualar o fundo da faixa Atendimentos ao fundo da lista usando o token de página e sincronizar os estilos servidos.
- [x] 6.4 Apresentar Atendimentos como título de 18px em negrito, centralizado e com cor principal; sincronizar os estilos servidos.

## 7. Linha de ações da lista

- [x] 7.1 Alinhar título à esquerda e ações compactas à direita na mesma linha; verificar os fluxos no navegador e sincronizar assets servidos.

## 8. Falha real de encaminhamento

- [x] 8.1 Restaurar a configuração privada existente de encaminhamento no ambiente local sem expor valores ou alterar a credencial remota; verificar presença e carregamento.
- [x] 8.2 Diferenciar erro de configuração de falha transitória, com teste unitário que comprove ausência de chamada Xano sem credencial e mensagem específica na ponte.
- [x] 8.3 Verificar testes relacionados, compilação e atualização do processo em execução; documentar o resultado e limites.

## 9. Cores da fila veterinária

- [x] 9.1 Aplicar vermelho/aguardando, amarelo/em atendimento e verde/encerrado aos cartões veterinários e verificar visualmente nos dois temas.

## 10. Detalhes do atendimento em pop-up

- [x] 10.1 Mover informações e ações do ticket para diálogo acessível, aberto por ícone flutuante dentro do chat com cor de status; verificar abertura, fechamento, preservação de motivo, cancelamento e ausência de chamada extra ao abrir.

## 11. Cores da lista do tutor

- [x] 11.1 Compartilhar a paleta de status entre tutor e veterinário e verificar as três cores nos dois temas com dados simulados.

## 12. Halo contextual do ícone

- [x] 12.1 Fazer o halo global de hover/foco do ícone flutuante acompanhar o status e verificar vermelho no estado aguardando.

## 13. Fotos do pet

- [x] 13.1 Acrescentar foto na projeção autorizada da lista/detalhe sem consultas adicionais, deduplicando por pet; verificar a projeção com teste.
- [x] 13.2 Renderizar foto circular com fallback na lista e pop-up; verificar foto válida, ausente e inválida nos dois temas.
- [x] 13.3 Publicar seletivamente a função preservando versão anterior e verificar o contrato remoto e assets servidos; documentar resultado.

## 14. LEDs nos cartões e fotos

- [x] 14.1 Adicionar SVG decorativo com segmento horário e halo contextual nos cartões e molduras das fotos, inclusive no pop-up, e verificar animação, movimento reduzido e ações no navegador.

## 15. Foto e identidade dos participantes

- [x] 15.1 Corrigir recorte circular da foto no pop-up, diferenciar ícones de tutor/veterinário e atualizar cabeçalho pelo interlocutor; verificar transição e retorno ao bot no navegador.

## 16. LED contextual da janela e pop-up

- [x] 16.1 Atualizar LED e halo do chat pelo status e adicionar perímetro animado ao pop-up; verificar mudança de status e retorno ao assistente no navegador.

## 17. Paleta completa do chat

- [x] 17.1 Aplicar cores de status em cabeçalho, controles, ícones, balões e campo sem alterar o tema externo; verificar cores e restauração ao assistente nos dois temas.

- [x] 17.2 Fazer contorno e anel de foco do pop-up herdarem a cor do status, eliminando o verde do tema ao selecionar o campo.

## 18. Emojis em todos os compositores

- [x] 18.1 Adicionar painel local com busca/categorias, inserção no cursor, limite e fechamento acessível; testar assistente e atendimento humano sem chamadas extras.

- [x] 18.2 Posicionar o botão de emojis imediatamente antes do botão Enviar, após o campo de mensagem, e sincronizar o asset servido.


## 19. Encerramento exclusivo pelo veterinário responsável

- [ ] 19.1 Restringir encerramento no Xano e ponte Reflex por perfil/estado; verificar tutor negado, responsável permitido e cancelamento antes da assunção.
- [ ] 19.2 Ocultar motivo/encerramento do tutor após assunção; verificar os dois perfis no navegador.
- [ ] 19.3 Publicar seletivamente a função com backup, executar verificações remotas sem alterar chamados reais e atualizar assets/documentação.

## 20. Nomes dos participantes

- [x] 20.1 Projetar nome do tutor no detalhe autorizado sem exposição na fila; verificar projeção e publicar somente esse ajuste com backup.
- [x] 20.2 Mostrar rótulos acima de avatar/mensagem e nome confirmado no cabeçalho; verificar dois perfis, fallback e ausência de prefixo no texto.

## 21. Entrega/leitura e tutor nos cartões

- [x] 21.1 Projetar tutor no cartão próprio e persistir leitura monotônica de mensagens recebidas dentro da transação existente; testar autorização, referências inválidas e idempotência.
- [x] 21.2 Mostrar Entregue/Lido e nome do tutor, coletar visualização apenas no chat ativo e aproveitar sincronização existente; verificar dois perfis, rolagem, aba oculta e ausência de chamadas por mensagem.
- [x] 21.3 Publicar seletivamente preservando a decisão pendente de finalização, validar contrato remoto e sincronizar assets/documentação.

## 22. Correção de leitura na troca de perfil

- [x] 22.1 Sincronizar leitura observada em lote sem esperar polling e atualizar recibos no retorno; verificar dois perfis com estado compartilhado, troca rápida de aba e rótulo Visto.

## 23. Nome do tutor real e checks compactos

- [x] 23.1 Verificar presença do nome no cadastro e projeção real do detalhe; explicitar Nome não informado quando o cadastro estiver vazio, sem inventar ou alterar identidade.
- [x] 23.2 Usar ícone SVG único de checks compactos para o recibo e verificar apresentação e atualização no navegador.

## 24. Contato do tutor nas informações veterinárias

- [x] 24.1 Acrescentar telefone/e-mail na projeção autorizada somente do veterinário, sem ampliar fila ou dados sensíveis; verificar projeção e publicar seletivamente com backup.
- [x] 24.2 Mostrar seção Tutor responsável no pop-up com nome/telefone/e-mail e fallback; verificar ambos os perfis e ausência de chamada extra ao abrir.

## 25. Editar e apagar mensagens próprias

- [x] 25.1 Implementar operações autorizadas edit/delete com revisão, idempotência e auditoria privada; testar autoria, estado, concorrência e recibos por revisão.
- [x] 25.2 Adicionar seleção/menu, editor e confirmação de remoção para mensagens próprias ativas; verificar ambos os perfis, erro/retry e preservação do texto.
- [x] 25.3 Publicar seletivamente sem incluir a regra pendente de finalização, verificar contrato remoto e sincronizar assets/documentação.

- [x] 25.4 Exibir lápis e lixeira nas mensagens próprias, com acesso direto ao editor e à confirmação de exclusão; verificar fluxo no navegador.
- [x] 25.5 Exibir círculo com traço diagonal junto ao texto Mensagem apagada e sincronizar os assets servidos.
- [x] 25.6 Restaurar reticências na mensagem e manter lápis/lixeira nas opções do pop-up; verificar no navegador.

## 26. Prazo de 10 minutos e símbolo após exclusão

- [x] 26.1 Aplicar prazo no Xano pelo envio original, preservando retry idempotente e revisão; testar limite, vencimento e relógio inválido.
- [x] 26.2 Expirar ações na interface com referência de tempo do servidor e preservar rascunho; verificar editor aberto e símbolo após Mensagem apagada.
- [x] 26.3 Publicar seletivamente com backup e verificar contrato, sem tocar mensagens reais; atualizar assets e documentação.

- [x] 26.4 Exibir um horário HH:mm centralizado no início de cada conversa sem duplicar ao atualizar; verificar assistente e atendimento.

## 27. Fila geral e responsável exclusivo

- [x] 27.1 Confirmar trava transacional, proteção de participação e retirada da fila de outros médicos; executar disputa remota usando apenas atores e chamado sintéticos, encerrando o chamado após a verificação.

## 28. Cabeçalho, rótulos do tutor e ações vencidas

- [x] 28.1 Empilhar informações do cabeçalho, ajustar rótulos da lista do tutor e manter menu de mensagem vencida com opções bloqueadas e aviso; verificar os estados no navegador.

- [x] 28.2 Restaurar Ver conversa nos cartões do tutor em todos os estados, conforme ajuste solicitado; sincronizar o JavaScript servido.
