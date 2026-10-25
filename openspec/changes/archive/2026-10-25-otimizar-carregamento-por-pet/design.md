# Design

## Context

Ver motivação em `proposal.md`. `State.open_pet` aguarda `_load_pet_detail`; `ClinicalMixin.clinical_section` chama `load_tutor_clinical` a cada seção diferente de Início. Esse método apaga as projeções e aguarda histórico, consultas, acessos e auditoria em série. O cliente abre um `httpx.AsyncClient` por chamada e repete 429 até três vezes para o grupo clínico. Há texto de carregamento em `notice()`, mas os eventos clínicos não usam background. `SettingsState.load_account` já demonstra captura/aplicação de estado com HTTP fora do lock.

Os testes existentes de seleção e clínica usam respostas HTTP controladas, úteis para reproduzir corridas. A change concluída `fluxo-consultas-prontuario` contém contratos clínicos ainda não sincronizados; preservá-los e não arquivar essa outra change nesta implementação.

## Goals / Non-Goals

**Goals:** reduzir chamadas por navegação, liberar eventos da sessão durante espera e distinguir carregando, carregado vazio e erro; manter isolamento e revalidação verificáveis.

**Non-Goals:** não consolidar o backend remoto em um endpoint novo, não alterar schema nem cachear leituras veterinárias; não tornar esta change uma refatoração geral do login ou do cliente HTTP. A conexão HTTP reutilizável pode ser avaliada separadamente se medições justificarem.

## Decisions

### 1. Uma carga lógica por seleção, usando contratos existentes

Ao selecionar, o evento curto limpa o contexto anterior, registra alvo/geração, publica loading e agenda evento background. O detalhe básico é validado primeiro em `GET vettech-pets/pets/{id}`; somente após a propriedade confirmada, carregar histórico e consultas de `vettech-clinical` concorrentemente, com limite de duas leituras clínicas simultâneas. Usar `asyncio.gather(..., return_exceptions=True)` ou equivalente para observar ambos os resultados e tratar 401/403 antes de qualquer publicação.

Uma carga lógica continua tendo múltiplas requisições HTTP; esta etapa não promete uma única requisição de rede. Endpoint agregado reduziria viagens, mas exigiria publicação Xano e ampliaria o escopo. Quatro chamadas concorrentes em cada clique manteriam redundância e aumentariam pressão sobre os limites do serviço.

Histórico fornece consultas publicadas e complementos; o endpoint de consultas fornece reservas. Não buscar anexos. Acessos e auditoria deixam a carga comum e ganham entrada explícita sob demanda na área de consultas, com loading/erro próprios e sem busca automática ao montar uma área oculta.

### 2. Background com snapshots e publicação condicionada

Reutilizar o padrão documentado do Reflex e já adotado por configurações: capturar token, identidade, alvo e gerações sob `async with self`; executar HTTP fora do bloco; reacquirir o estado para validar a captura e aplicar resultados. Não chamar métodos que mutam estado diretamente fora do lock. Se uma refatoração do detalhe for necessária, separar obtenção de resposta e aplicação, sem criar uma segunda sessão autenticada.

Manter os contadores atuais de sessão/contexto e acrescentar identificação de carga clínica quando necessário. Mudança de pet, volta à lista, operação confirmada, logout ou 401/403 invalida as cargas anteriores. O `finally` só limpa loading se a carga ainda for a atual. Cancelamento é uma otimização; descarte por geração é obrigatório mesmo quando não se consegue cancelar HTTP.

### 3. Cache somente da seleção atual

Conservar uma cópia privada no servidor para o pet selecionado, identificada por sessão/identidade/pet e validade monotônica de 60 segundos a partir da conclusão bem-sucedida. Não manter histórico de cache de vários pets: trocar A por B elimina A; voltar a A realiza nova carga. Isso limita memória e atende à limpeza já exigida por `pet-management`.

Trocar seção é um evento curto: atualiza seção e reutiliza a cópia válida. Se não existir carga válida, agenda uma carga; se já estiver em andamento, não agenda outra. A expiração é verificada na próxima abertura de seção ou entrada na área do pet, sem polling. Atualizar força uma nova carga e invalida a anterior. Não apresentar dados vencidos como atuais durante revalidação.

Histórico e reservas são publicados como conjunto completo; falha de um impede marcar o conjunto como sucesso e preserva detalhe básico já autorizado. Erros 401/403 têm prioridade sobre sucessos parciais, limpando o contexto protegido. Respostas antigas não renovam TTL.

### 4. Loading local à área de conteúdo

Spinner ou skeleton acompanhado de “Carregando dados do pet…” com `role="status"`, texto anunciado com moderação e `aria-busy` no conteúdo. Manter menu, Mudar pet e Sair utilizáveis; evitar overlay que bloqueie a página inteira. Não apresentar “nenhum registro” antes de confirmar a leitura. Conclusão vazia usa o estado vazio existente; falha oferece Tentar novamente e mantém troca de pet disponível.

Revalidação e carregamento auxiliar usam estados próprios para não desligar o loading de outra carga. Permitir navegação para configurações enquanto HTTP está pendente. Não confundir término do detalhe básico com término da carga clínica.

### 5. Atualização após alterações

Agendamento confirmado invalida reservas; se o pet do modal for o selecionado, executar revalidação das consultas, sem disparar recarga do histórico sem necessidade. Se for outro pet, não substituir o contexto atual. Mudança de consentimento revalida acessos e auditoria já solicitada. Incrementar geração antes da atualização para que leituras anteriores à escrita não a sobrescrevam. Uma falha de escrita não confirma mudança nem repete a operação automaticamente.

Eventos veterinários de consulta, agenda, consentimento remoto e auditoria mantêm comportamento existente. Um tutor pode observar mudanças externas com Atualizar ou na próxima navegação após TTL; não prometer sincronização em tempo real.

## Risks / Trade-offs

- [Xano pode responder 429 mesmo com duas leituras] → manter o tratamento atual, sem rajadas de repetição adicionais, e medir respostas/quantidade de chamadas; navegação permanece liberada durante espera.
- [Dados externos mudam antes do TTL] → limitar a 60 segundos, fornecer Atualizar e revalidar após mutações conhecidas. Não reutilizar esse cache na autorização de escrita.
- [Corridas de seleção e atualização] → validar sessão, alvo e geração em sucesso, falha e finalização; testar A→B, A→B→A, logout, volta à lista e leitura anterior a agendamento.
- [Confusão entre vazio, falha e dados antigos] → estados explícitos; nenhuma resposta parcial clínica é publicada como carga completa.
- [Cache de dados sensíveis] → apenas sessão atual no servidor; limpar em troca, expiração e negação; não armazenar payloads em evidências, logs ou navegador.
- [Retirar leituras auxiliares quebra informações existentes] → conservar as visualizações de acessos/auditoria e dar a elas carregamento explícito sob demanda, com testes de contagem e erros independentes.

## Migration Plan

1. Registrar contagens e comportamento atuais com HTTP mockado e percurso de navegador em rede lenta controlada.
2. Implementar estado e eventos, depois loading e ações de recuperação, preservando contratos Xano e seleção explícita.
3. Executar testes de seleção/clínica/configurações, `reflex compile --dry` e navegador desktop/celular. Medir clique→loading, clique→seção e carga completa separadamente.
4. Reiniciar o processo Reflex com `.venv`, configuração Xano carregada e acesso de rede disponível; validar `/ping`, WebSocket e percurso real sem gravar dados clínicos nos logs.
5. Rollback reverte apenas aplicação e descarta o cache da sessão; não há migração de dados nem reversão de registros clínicos.
