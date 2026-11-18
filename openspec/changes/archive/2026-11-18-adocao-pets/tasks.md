# Tasks

## 1. Contratos e autorização no Xano

- [x] 1.1 Adicionar `disponivel_adocao` desativado por padrão ao modelo de pet e verificar que cadastro/listagem atuais não ativam nem expõem o campo.
- [x] 1.2 Implementar a listagem autenticada agregada com identificação e somente os campos clínicos autorizados; validar o XanoScript e revisar a lista vazia, filtro de disponibilidade, estados publicados e whitelist sem notas, resultados, anexos, microchip ou dados de tutor/veterinário.
- [x] 1.3 Implementar adoção transacional com `pet_id` como único alvo, identidade `$auth.id`, trava/revalidação de disponibilidade, revogação de autorizações veterinárias e retorno dos dados do pet; validar a estrutura da transação e o contrato do cliente, sem aceitar tutor informado pelo cliente.
- [ ] 1.4 Executar testes de workflow/integração do Xano em ambiente de desenvolvimento para transferência única, concorrência, identidade/perfil, revogação e preservação do histórico; não usar dados de produção.

## 2. Estado e integração da interface

- [x] 2.1 Integrar o carregamento de adoção ao estado autenticado do tutor com uma leitura por entrada explícita, proteção contra resposta de sessão antiga, estado vazio/erro e atualização manual; verificar com testes unitários que renderização e visualização não disparam consultas adicionais.
- [x] 2.2 Implementar confirmação, cancelamento e adoção com clique duplicado bloqueado; verificar que o pedido envia somente o ID do pet e que sucesso atualiza localmente a lista de adoção e `State.pets` usando a resposta, sem segunda leitura, seleção automática ou repetição automática.
- [x] 2.3 Adicionar testes unitários para sucesso, cancelamento sem POST, falha/conflito sem mutação, resposta incompatível e sessão encerrada durante leitura/escrita.

## 3. Navegação e tela de adoção

- [x] 3.1 Registrar `/adocao` para tutor autenticado e incluir Adoção abaixo de Meus Pets na sidebar compartilhada; verificar rota protegida, ordem, item ativo e preservação das rotas/menu veterinário.
- [x] 3.2 Construir cards responsivos com foto, identificação e resumo clínico permitido, além de “Ver prontuário” e “Adotar”; verificar que a pré-visualização usa somente dados em memória e não abre o prontuário completo.
- [x] 3.5 Aplicar aos cards de adoção o LED de perímetro verde compartilhado, com órbita no sentido horário e respeito à preferência de movimento reduzido.
- [x] 3.6 Adicionar ícones semânticos aos cabeçalhos de vacinação, medicamentos, condições de saúde e exames nos cards de adoção, mantendo legibilidade nos temas claro e escuro.
- [x] 3.7 Exibir a mascote `mascote_logo.webp` ampliada, centralizada no espaço entre o título e o botão de fechar e flutuando acima da borda do diálogo, com a base visível encostada nela; aplicar o LED verde perimetral compartilhado com órbita horária e preferência por movimento reduzido, verificando tamanho, posição, contato visual, animação, ordem e carregamento no navegador.
- [x] 3.8 Exibir o resumo clínico da prévia em quatro seções com ícones semânticos e LED verde perimetral compartilhado; verificar seções, ícones, cor e direção da animação no navegador.
- [x] 3.9 Exibir `mascote_logo.webp` centralizada acima da borda do diálogo de resumo clínico, com a base visível encostada e sem reservar altura; verificar imagem, alinhamento e espaçamento no navegador.
- [x] 3.10 Deslocar a mascote do resumo clínico à direita e posicionar o botão “Fechar” no canto inferior direito; verificar ambos os alinhamentos no navegador.
- [x] 3.11 Exibir a foto do pet à esquerda e o resumo clínico à direita em painéis separados por divisor, com os quatro campos alinhados em uma coluna compacta; empilhar os painéis em telas estreitas, usar os dados já carregados e verificar alinhamento, responsividade e ausência de chamadas extras no navegador.
- [x] 3.3 Implementar o diálogo de confirmação conforme a referência visual e os estados de carregamento/erro; verificar Cancelar/Escape sem escrita e confirmação com feedback acessível.
- [x] 3.4 Adicionar teste de navegador com respostas Xano simuladas cobrindo navegação, lista/carregamento/vazio, resumo, abrir/cancelar/confirmar diálogo e atualização imediata em Meus Pets e Mudar pet.

## 4. Verificação integrada

- [x] 4.1 Executar validação OpenSpec estrita, testes unitários focados, `reflex compile --dry` e o teste de navegador da adoção; corrigir falhas relacionadas e registrar qualquer dependência de publicação Xano ainda pendente.

## 5. Perfis demonstrativos locais

- [x] 5.1 Implementar modo demonstrativo local opt-in por `VET_TECH_ADOPTION_DEMO`, com os seis perfis e fotos fornecidos, identificador visual de demonstração, dados fictícios apenas de perfil e sem fixtures clínicos ou fallback automático.
- [x] 5.2 Verificar cards, fotos, “Não informado” nas seções clínicas, prévia, cancelamento e adoção simulada em sessão; comprovar que listagem, prévia e confirmação não chamam endpoints de adoção nem alteram `State.pets`.

## Verificação pendente de ambiente

Os XanoScripts passam na validação estática; os fluxos de navegador real-sintético e demonstrativo local foram verificados contra APIs sintéticas isoladas. O modo demonstrativo local não substitui a validação de transação/concorrência, publicação dos endpoints ou adoção persistente; esses itens permanecem pendentes até haver um workspace Xano de desenvolvimento isolado.
