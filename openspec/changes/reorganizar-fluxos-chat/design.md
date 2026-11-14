# Design

## Context
A UI é JavaScript/CSS com ponte privada Reflex; Support/operate mantém autorização e idempotência no Xano. Ver proposal.md. O workflow n8n externo continua com duas requisições por troca.

## Goals / Non-Goals
Organizar os estados no painel existente, sem nova tecnologia. Não alterar persistência clínica, contratos do workflow externo ou conceder acesso ao prontuário.

## Decisions
- Criar ação de leitura de pets na ponte privada, sem listar tickets; manter consentimento explícito e contexto confirmado no servidor. Evita acoplar novo encaminhamento ao histórico.
- Cabeçalho com navegação em linha separada, cartões e formulário em área rolável e mensagens/rodapé com espaço garantido. LED externo único evita divisória fantasma quando banner some.
- Retry manual preserva snapshot da operação; botões ficam desabilitados durante requisição. Polling de ativos a 20s, sem lista automática, sem aba oculta e sem encerrados; elimina chamadas ociosas mantendo atualização de mensagens.
- Manter mensagens de pergunta/resposta no contrato atual, sem cache global de conteúdo clínico. A economia é nas leituras auxiliares, sem alegar redução do custo intrínseco do workflow.

## Risks / Trade-offs
- Atualização remota pode levar até 20s → mostrar orientação e atualização manual.
- Timeout pode ocorrer com operação em andamento → preservar chave idempotente; não repetir escrita automaticamente.
- Backend remoto pode falhar por configuração → UI deve mostrar erro recuperável; testes simulados não comprovam disponibilidade externa.

## Migration Plan
Publicar assets e backend Reflex juntos. Não requer migração ou publicação Xano. Reverter esses arquivos restaura o fluxo anterior.

## Correção da configuração local

A credencial de criação estava ausente no ambiente local. Recuperar somente o
valor existente da configuração remota para o .env ignorado, sem rotação ou
alteração remota. A ponte deve diferenciar a ausência dessa configuração de
falhas transitórias e não sugerir retry enquanto não houver configuração.

## Fotos do pet

Projetar pet_id e foto na consulta com join já existente da lista, mantendo
filtros de propriedade/participação. Entregar pet_photos indexado por pet_id
para não repetir base64 em vários tickets do mesmo animal. Detalhe autorizado
acrescenta photo no pet já retornado. Não buscar cada pet separadamente.
A fila passa a mostrar foto do animal, sem tutor, nome ou dados clínicos.
O frontend valida protocolos/formatos e usa imagem lazy com fallback.
Publicação seletiva de Support/operate exige preservar versão anterior para
rollback e conferir ausência de divergência remota antes de atualizar.

## Confirmações de leitura e tutor nos cartões

Entregue significa mensagem persistida no atendimento, sem afirmar recebimento
por um dispositivo específico. read_through é o UUID da última mensagem recebida
visível; o servidor verifica a referência e marca read_at nas recebidas até ela.
Não há nova tabela nem eventos de leitura por polling: atualizar apenas mensagens
ainda não lidas dentro da transação existente e reutilizar get/send. Isso preserva
idempotência e evita consultas por mensagem. O navegador acumula mensagens vistas
com janela/aba em foco, preserva a posição de rolagem e envia o marcador em um lote após cerca de 350ms, com intervalo mínimo de
cinco segundos entre lotes adicionais, aproveitando consultas/envios quando
já em curso. Retorno à aba consulta recibos e reconfere uma vez após a janela
de agrupamento, se ainda houver mensagens próprias não vistas. Em encerrados, uma sincronização adicional somente quando
houver leitura nova pendente; sem polling contínuo para esses tickets.
Nomes do tutor vêm do join da listagem e são projetados apenas para cartões
próprios/atribuídos, sem identificação pessoal nova na fila aguardando assunção.
A publicação desta entrega exclui a regra de finalização ainda pendente.

## Edição e remoção de mensagens

Novas operações edit/delete usam UUID da mensagem, expected_revision e
operation_id no agregado existente. Validações de autoria usam perfil e ID
autenticados; participante de ticket alheio é barrado antes da transição.
Revisões avançam apenas com alteração de conteúdo; recibos não alteram revisão.
Eventos armazenam snapshot anterior em value, que já é removido da projeção
pública, e assinatura da operação para retry exato. Soft delete conserva
metadados e auditoria, removendo text na mensagem projetada.
Edição invalida o recibo da versão anterior; read_revision impede que marcador
antigo confirme a nova versão sem visualizá-la. Leituras em lote não marcam
versões editadas anteriores ao alvo que não foram explicitamente observadas.
A interface abre diálogo ao selecionar mensagem própria ou usar reticências;
pausa polling/observação enquanto edita e preserva o rascunho até confirmação.
O assistente conserva contexto imutável: essas ações abrangem mensagens
humanas persistidas, sem reescrever perguntas que já geraram resposta do bot.
