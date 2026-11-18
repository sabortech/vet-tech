# Design

## Context

O tutor usa o `State` compartilhado para autenticação, pets e navegação. `GET Pet/pets` e `GET Pet/pets/{pet_id}` filtram por `$auth.id`; o histórico clínico autenticado também valida a propriedade, mas retorna consultas e complementos completos. A tabela `pet` não possui estado de adoção. A sidebar deriva sua navegação de um catálogo e usa páginas Reflex registradas em `vet_tech.py`.

## Goals / Non-Goals

**Goals:**

- Reutilizar a sidebar, os tokens visuais e a coleção de pets do tutor existentes.
- Buscar a lista e o resumo permitido em uma única solicitação agregada por entrada/atualização explícita.
- Transferir a propriedade de forma atômica no Xano e devolver a projeção necessária para as listas locais.
- Isolar o resumo de adoção das leituras completas de prontuário.

**Non-Goals:**

- Criar uma tela para anunciar, aprovar ou retirar pets da adoção; a disponibilidade será gerenciada por equipe no backend após confirmar consentimento.
- Tornar o prontuário completo visível a outros tutores antes da adoção.
- Criar notificações, endpoints clínicos por card ou consultas automáticas periódicas.

## Decisions

### Disponibilidade é uma autorização controlada no backend

Adicionar `disponivel_adocao`, booleano desativado por padrão, ao registro de pet. A equipe controla o campo no Xano somente após confirmar a autorização de divulgação do tutor atual. Nenhuma API de tutor poderá ativar ou alterar esse campo. A rota de listagem exige autenticação de tutor e filtra exclusivamente pets com disponibilidade ativa.

**Alternativas consideradas:** usar qualquer pet sem tutor, o que contradiz o vínculo obrigatório pet → tutor; ou permitir publicação pelo tutor nesta entrega, o que ampliaria o fluxo além da tela solicitada e exigiria interface e operações adicionais.

### Um endpoint agregado alimenta os cards e sua pré-visualização

Adicionar uma leitura autenticada no grupo `Pet` para obter, em uma resposta, pets disponíveis, nomes de espécie/raça e a projeção clínica limitada pelas specs. O Xano consulta cada conjunto clínico em lote, restrito aos pets elegíveis, e agrega por `pet_id`; o frontend não fará consultas por cartão ou seção. Vacinas são resumidas pela aplicação mais recente; medicamentos são incluídos somente quando vigentes pela data de início/fim; condições não curadas usam o estado consolidado registrado; exames mostram somente tipo, data e estado. A derivação não infere diagnóstico, resultado ou condição ausente.

“Ver prontuário” abre um diálogo de resumo a partir do DTO já carregado. Não há endpoint de detalhe nem acesso ao `Clinical/history` antes de adotar, porque esse endpoint retorna narrativas e outros dados clínicos não autorizados para divulgação.

**Alternativas consideradas:** reutilizar o histórico clínico completo e remover campos no cliente, que enviaria informação sensível desnecessária ao navegador; ou fazer consultas individuais por card/seção, que aumentaria chamadas e superfícies de autorização.

### Adoção é uma transferência transacional, não uma cópia

Adicionar uma escrita autenticada no grupo `Pet`, recebendo somente `pet_id`. Em transação, o backend adquire a trava por pet existente em `clinical_lock`, relê e valida a disponibilidade, grava `tutor_id = $auth.id`, desativa `disponivel_adocao`, revoga as autorizações veterinárias ativas anteriores e retorna os dados básicos projetados com espécie/raça. A trava e a releitura garantem um único adotante; tentativa concorrente ou disponibilidade retirada retorna erro de negócio sem sucesso parcial. O endpoint não recebe nem usa um tutor de destino informado pelo cliente.

O histórico clínico e os registros de auditoria existentes não são reescritos nem apagados. Após a transferência, as operações de tutor existentes reconhecem o novo proprietário e as operações veterinárias anteriores deixam de ser autorizadas; o novo tutor poderá conceder novos acessos pelo fluxo existente.

**Alternativas consideradas:** criar uma segunda linha de pet, que dividiria a continuidade do prontuário; ou alterar `tutor_id` sem transação/revalidação, que permitiria adoções duplicadas e autorizações antigas.

### A interface mantém uma única fonte local para pets próprios

Criar a página `/adocao` e o catálogo de navegação deve posicionar Adoção imediatamente abaixo de Meus Pets. O estado de adoção será integrado ao `State` autenticado, sem criar um segundo estado de sessão. A entrada da página carrega uma vez; atualizar é ação explícita. A lista e o diálogo usam somente a resposta em memória e não fazem polling.

Depois de uma resposta de adoção validada, o estado remove o pet da lista de adoção e acrescenta o DTO retornado à coleção `State.pets`, com os mesmos campos projetados usados por Meus Pets/Mudar pet. Não seleciona o novo pet automaticamente. Clique pendente fica desabilitado. Erro, conflito, resposta incompatível ou sessão alterada não atualiza as listas; falha incerta de escrita não é repetida automaticamente.

Os cards seguem o padrão visual atual, usam duas colunas quando houver largura útil e empilham no celular. A prévia apresenta foto à esquerda e as quatro seções do resumo clínico à direita, separadas por divisor vertical; em telas estreitas, a composição empilha os painéis e adapta o divisor. Dentro do painel clínico, as quatro seções ocupam uma coluna de linhas compactas, com cada título e valor alinhados no mesmo eixo, evitando que os cabeçalhos disputem largura entre si. A foto e os dados vêm do pet já carregado, sem consultas adicionais. O resumo usa ícones semânticos, LED verde perimetral compartilhado, mascote ligeiramente à direita acima da borda e botão “Fechar” no canto inferior direito, sem reservar altura para a mascote. A confirmação utiliza diálogo acessível e ações Cancelar/Confirmar adoção. A mascote fica centralizada no espaço entre o título e o botão de fechar, acima e encostada à borda superior; ambos os diálogos usam o LED verde perimetral compartilhado com órbita horária e movimento reduzido. O CSS fica restrito às classes da nova tela.

### Demonstração local isolada

Como o plano Xano atual não permite criar um ambiente de desenvolvimento, oferecer um modo demonstrativo local ativado somente por `VET_TECH_ADOPTION_DEMO=true` no backend Reflex. A configuração padrão permanece desligada. Nesse modo, a página usa seis fixtures locais e as fotos fornecidas, mostra um aviso destacado de demonstração e não chama endpoints Xano de adoção para listar, visualizar ou confirmar. A confirmação remove o perfil somente da lista mantida na sessão e explica que nada foi persistido nem adicionado a Meus Pets/Mudar pet. Não haverá fallback silencioso se a API real falhar. Os dados clínicos fictícios não serão criados; vacinação, medicação, condições e exames ausentes mostrarão “Não informado”. Os perfis de demonstração nunca serão gravados ou promovidos a Xano.

## Risks / Trade-offs

- **A lista só terá pets previamente marcados pela equipe** → documentar a operação manual de disponibilização e exigir consentimento antes da marcação; não expor uma escrita de disponibilidade para tutores.
- **O resumo continua sendo informação de saúde sensível** → autenticar o tutor, devolver somente a projeção especificada, excluir texto livre/anexos/identificadores e verificar disponibilidade no backend a cada leitura.
- **Uma resposta de escrita pode se perder depois do commit** → não repetir automaticamente; apresentar falha recuperável e permitir atualização explícita. O backend impede uma segunda transferência.
- **A adoção altera uma relação de propriedade persistente** → migração aditiva com padrão falso; rollback desativa a interface/endpoints, mas nunca reverte transferências já confirmadas nem apaga histórico.
- **O log clínico existente exige veterinário como ator** → não usar esse log para representar um tutor adotante; manter sua semântica e auditoria imutáveis sem atribuir autoria veterinária falsa.
- **Dados de demonstração podem ser confundidos com anúncios reais** → exigir configuração explícita no backend, exibir aviso persistente e nunca fazer fallback silencioso para fixtures.

## Migration Plan

1. Adicionar o campo de disponibilidade com padrão falso; registros existentes continuam fora da lista sem backfill.
2. Publicar/validar as operações de listagem e adoção com autenticação, projeções e transação.
3. Integrar a tela, navegação e atualização local somente depois do contrato Xano estar disponível no ambiente de desenvolvimento.
4. Enquanto não houver ambiente Xano isolado disponível, ativar a demonstração local somente em execução de desenvolvimento e verificar os seis perfis, o aviso de demonstração e a adoção efêmera sem chamadas de escrita. Os testes de transferência real permanecem pendentes até um ambiente Xano isolado.
5. Se houver rollback, retirar rota/menu/endpoints da aplicação, manter o campo desativado por padrão e preservar as transferências e registros já confirmados. Qualquer reversão de tutor exige operação autorizada específica, nunca uma restauração em lote.

## Open Questions

Nenhuma para a implementação especificada. A equipe que administra o Xano deverá operacionalizar a confirmação de consentimento antes de ativar `disponivel_adocao`; essa gestão não faz parte da interface entregue.
