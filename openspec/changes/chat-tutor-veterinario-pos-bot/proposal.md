# Proposta: chat tutor–veterinário após o bot

## Why

O VetTech já oferece conversa com o assistente via n8n, mas não permite que um veterinário continue o atendimento quando a dúvida do tutor exige acompanhamento humano. Esta mudança amplia o escopo funcional documentado para conectar a conversa inicial do bot a um chamado e a um chat entre tutor e veterinário sobre o mesmo pet, conforme a issue #25.

## What Changes

- Após conversar com o bot, o tutor autenticado pode confirmar o encaminhamento proposto pelo assistente para atendimento veterinário. O bot solicita a abertura do chamado; a confirmação identifica o pet e autoriza compartilhar o conteúdo daquela conversa com o profissional que assumir.
- Criar chamado persistente vinculado ao tutor, a um único pet e à conversa de origem, com estados aguardando, em atendimento e encerrado.
- Disponibilizar fila de chamados aos veterinários autenticados, com informações operacionais mínimas; somente quem assumir recebe as mensagens e o contexto compartilhado. Como regra inicial, a fila é compartilhada entre veterinários cadastrados, sem roteamento por clínica ou especialidade.
- Permitir que um único veterinário assuma o chamado e converse por texto com o tutor, preservando autoria, ordem, histórico e contexto do bot.
- Informar criação, assunção, novas mensagens e encerramento dentro do aplicativo. Se ninguém assumir, manter o chamado aguardando sem prometer atendimento imediato.
- Retomar o chamado após fechar o chat, recarregar ou entrar novamente na mesma conta; impedir duplicação de chamados e mensagens em repetições de envio.
- Permitir cancelamento pelo tutor enquanto aguarda e encerramento pelo tutor ou profissional responsável durante o atendimento, com motivo e orientação final quando houver.
- Manter as permissões do prontuário independentes: encaminhar ou assumir não concede acesso clínico e não cria consulta, diagnóstico, receita ou agendamento automaticamente.

## Capabilities

### New Capabilities

- `veterinary-support-chat`: ciclo do chamado, fila, assunção exclusiva, mensagens persistentes, avisos, privacidade e encerramento.

### Modified Capabilities

- `n8n-chat-integration`: sinal estruturado de encaminhamento, validado pelo servidor, sem interpretar texto livre do bot como comando ou autorização.
- `support-chat`: distinguir conversa temporária com o bot de atendimento humano persistente e permitir a continuidade autenticada do chamado.

## Impact

- Contexto consultado: `docs/project-overview.md` (escopo, RF07–RF09 e RN01–RN08), `docs/domain-model.md`, `docs/architecture.md`, `docs/n8n-chat.md`, specs atuais de chat e controle de acesso; implementação em `features/support_chat/state.py`, `shared/n8n_client.py` e ponte do chat. Referência externa: https://github.com/sabortech/vet-tech/issues/25 e seu anexo `ChatBotTurtle.md`.
- Comparação: o escopo atual centraliza prontuário, consentimento e auditoria; ainda não descreve atendimento humano por chat. O código atual aceita apenas resposta textual do n8n, mantém contexto limitado e apaga a conversa ao fechar. A proposta adiciona explicitamente a continuidade humana sem transformar esse chat em prontuário ou substituir o fluxo clínico existente.
- Evolução futura em Reflex, Xano/XanoScript e workflow n8n, preservando a stack. Persistência de chamados/mensagens e operações autenticadas serão novas; o DER e XanoScript deverão refletir os vínculos na implementação. O workflow remoto precisará suportar o novo encaminhamento; sua publicação deverá ser verificada separadamente.
- Privacidade: mensagens podem conter dados do tutor e da saúde do pet. Compartilhar apenas a conversa explicitamente encaminhada, sem anexar prontuário ou conversas de outros pets. Validar identidade, propriedade e participação no backend em cada operação. Registrar eventos de criação, assunção e encerramento com ator e horário, sem duplicar conteúdo sensível em logs técnicos. Leitura/edição/exportação do prontuário continua exigindo autorização ativa e auditoria clínica já existente.
- Avisos internos do chat são novos eventos operacionais, separados dos lembretes clínicos existentes destinados ao tutor. Não incluir dados clínicos no aviso da fila nem introduzir e-mail, WhatsApp ou push externo nesta etapa.
- Fora do escopo: design visual, layouts, temas, mascote, migração para React, anexos, avaliação por estrelas, chamadas de áudio/vídeo, pagamentos, transferência entre profissionais e mudanças no raciocínio clínico do bot. O protótipo da issue é apenas referência de comportamento, não contrato de implementação.
- Esta change contém somente proposta, requisitos funcionais e tarefas de verificação; não inclui `design.md`, decisões de desenho técnico detalhado nem alterações na aplicação.
