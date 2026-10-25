# Design

## Context

Ver `proposal.md` e `specs/pet-management/spec.md`. Esta change concretiza a
etapa 1 de `planejar-core-prontuario`; a etapa 2 continuará reutilizando as
páginas de cadastro/login para os perfis, sem exigir essa entrega antecipadamente.

`components/pets.py` já contém cadastro e listagem, mas seus itens não abrem
uma área individual. O estado e a autenticação estão em `features/auth/state.py`;
`_load_pets()` mantém somente dados resumidos de apresentação. O cliente HTTP
compartilhado usa o grupo `vettech-pets` e hoje lança `XanoRequestError` sem
status HTTP estruturado. O Xano oferece cadastro/lista e catálogos, sem consulta
individual. `pet.tutor_id` já existe e não precisa de migração.

## Goals / Non-Goals

**Goals:** seleção explícita, detalhes básicos autorizados e alternância segura
na sessão atual, usando a arquitetura e as páginas existentes.

**Non-Goals:** rota pública ou compartilhável de pet, restauração de seleção
após nova sessão, reformulação visual, edição/exclusão, foto privada, prontuário,
agenda ou permissões veterinárias. Não criar campos/estados fictícios de módulos
clínicos futuros; quando surgirem, deverão participar da mesma limpeza de contexto.

## Decisions

### Consultar o pet individualmente no backend

Adicionar `GET /pets/{pet_id}` no grupo `Pet` (`vettech-pets`), com autenticação
pela tabela `tutor`. Validar ID inteiro positivo e consultar o pet usando
simultaneamente o identificador e `$db.pet.tutor_id == $auth.id`. Não aceitar
`tutor_id` como entrada de autorização. A lista é conveniência de navegação;
não é prova de que um ID pode ser aberto nem substitui a checagem do endpoint.

Contrato de resposta: objeto com `id`, `nome`, `especie_id`, `raca_id`, `sexo`,
`data_nasc`, `peso_atual`, `cor_pelo` e `num_microchip`. Retornar campos opcionais
sem inventar conteúdo e sem incluir tutor, credenciais, imagem privada ou dados
clínicos. ID inteiro não positivo recebe 400; identificador não numérico é
rejeitado pelo roteador Xano com 404 antes da execução do endpoint, conforme
verificado na integração. Ausência de autenticação válida recebe 401;
pet inexistente ou pertencente a outro tutor recebe a mesma resposta 404 com
mensagem genérica. Validar essas respostas na execução real do Xano.

Alternativa: abrir somente o objeto já carregado na lista. Rejeitada porque
não fornece validação atual de propriedade nem todos os dados básicos.

### Manter seleção no contexto das páginas existentes

Na área atual do tutor, acrescentar ação acessível de abrir o animal e um
controle de troca usando a própria lista. Mostrar nome do pet ativo e dados
básicos após confirmação da API; oferecer retorno à lista. Preservar o acesso
ao cadastro. Ao entrar, inclusive com um único pet, iniciar sem seleção.
Nenhuma nova rota ou armazenamento em cookie/local storage será necessário.

O ID solicitado durante carregamento é um alvo pendente, não um pet validado.
O objeto selecionado só é preenchido após sucesso para o mesmo ID e sessão.
Na troca, limpar imediatamente o detalhe anterior e enviar o novo pedido.
Catálogos são auxiliares: raça vazia/zero representa SRD; falhas na resolução
de nomes não impedem mostrar o animal autorizado. Campo ausente aparece como
“Não informado” ou é omitido; peso zero não é convertido em ausência.

Alternativa: página dinâmica com seleção na URL. Adiada por acrescentar
contrato de acesso direto e restauração sem necessidade nesta primeira fatia.

### Invalidar requisições antes de aceitar seus resultados

Controlar uma geração de seleção e o contexto de sessão. Cada troca, retorno
à lista, logout ou nova autenticação invalida os pedidos anteriores. Somente
um resultado cuja geração, sessão e ID ainda correspondam ao pedido atual
pode alterar detalhe, erro ou indicador de carregamento. A proteção se aplica
também ao tratamento de erro e ao bloco de finalização da requisição.

Usar eventos assíncronos Reflex compatíveis com a versão instalada e com as
regras de mutação de estado; não introduzir background tasks apenas para este
fluxo. Verificar a invalidação com testes de respostas controladas, inclusive
erro antigo depois de sucesso atual e resposta da sessão anterior.

Alternativa: desabilitar toda interação até terminar o pedido. Não satisfaz
sozinha o logout ou a resposta de sessão encerrada e torna a navegação frágil.

### Falhas, atualização da lista e sessão inválida

Exibir carregamento antes de aguardar a API. Erro de abertura deixa a seleção
sem detalhes, com nova tentativa e lista utilizável. Repetir exige a mesma
validação de propriedade, nunca reutilização silenciosa de objeto anterior.

Na atualização bem-sucedida da lista, se o ID selecionado desapareceu, limpar
o contexto. Se permanece, revalidar detalhes no endpoint individual, limpando
o objeto antigo enquanto a atualização ocorre. Falha de atualização da lista
não escolhe outro animal; preservar a lista anterior como hoje, mas invalidar
os detalhes selecionados e informar que não foi possível atualizá-los.
Cadastro de novo pet não o seleciona automaticamente; a atualização da lista
segue as mesmas regras. O formulário de criar um novo pet é do tutor e não
deve ser tratado como formulário de edição do pet selecionado.

Para distinguir 401 de falha transitória, acrescentar status HTTP opcional a
`XanoRequestError`, preservando `str(error)` e os usos existentes. Rejeição de
autenticação limpa seleção e sessão e apresenta o login existente. Não inferir
autenticação expirada pela comparação textual de mensagens traduzidas.

### Organização gradual e compatibilidade

Integrar inicialmente o estado de seleção ao `State` atual, compartilhando seu
token privado e os pontos de login/logout; componentes permanecem em
`components/pets.py`. Se uma extração pequena se tornar necessária, seguir
`docs/architecture.md`, mas não mover o módulo inteiro de autenticação como
pré-requisito. Testes novos podem ter arquivo próprio reutilizando a fixture
`make_state()` de `tests/unit/test_auth_state.py` ou centralizando-a se houver
reutilização concreta, preservando a suíte existente.

## Risks / Trade-offs

- [Confundir IDs/sessões] → Capturar contexto de sessão e geração em cada pedido,
  invalidar no logout/login e testar retornos fora de ordem.
- [Endpoint aparentemente seguro somente na interface] → Testar chamadas diretas
  com dois tutores e ID alheio; não aceitar apenas mocks como prova do backend.
- [Regressão no cliente compartilhado] → Status opcional e compatível, com testes
  da propagação de 401 e erro transitório, sem imprimir token nas evidências.
- [Catálogo indisponível ou campo opcional vazio] → Não bloquear os detalhes por
  dados auxiliares; preservar comportamento SRD e informar ausência corretamente.
- [Spec anterior limitava operações a cadastro/lista] → O delta modifica o bloco
  completo correspondente para permitir leitura individual sem habilitar edição.

## Migration Plan

1. Implementar e validar o novo endpoint em ambiente de teste, sem alterar tabelas.
2. Implementar cliente/estado/interface e executar testes e `reflex compile --dry`.
3. Testar Xano autenticado com dois tutores e conferir o fluxo no navegador.
4. Documentar respostas e evidências; publicar o endpoint com dry-run antes do push
   e liberar a interface apenas após a verificação dos contratos.

Rollback: remover a ação de seleção e desativar o novo endpoint, preservando
cadastro/listagem e todos os registros. Não há migração nem exclusão de dados.
