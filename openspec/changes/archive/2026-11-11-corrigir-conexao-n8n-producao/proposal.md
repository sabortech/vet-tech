# Proposta: corrigir conexão do assistente com n8n

## Why

Em 11/11/2026, a configuração local do assistente apontava para `/webhook-test/`, que respondeu HTTP 404 com mensagem de webhook não registrado. O endereço equivalente `/webhook/` respondeu HTTP 200 com `ok: true`, IDs correspondentes, resposta textual não vazia e `error: null`, usando o mesmo segredo e uma pergunta genérica de visitante. A falha observada é o uso do endpoint de teste sem registro ativo, enquanto o endpoint de produção funciona.

## What Changes

- Corrigir na implementação a configuração local para usar o webhook de produção validado, preservando o segredo somente no ambiente privado.
- Documentar a diferença operacional entre webhook de teste e de produção e o diagnóstico de HTTP 404 por endpoint não registrado.
- Disponibilizar verificação operacional reproduzível que use o cliente real do assistente, envie somente uma pergunta genérica de visitante e reporte sucesso apenas com resposta válida do workflow, sem imprimir credenciais ou conteúdo da conversa.
- Carregar a configuração corrigida no processo do aplicativo e verificar o ciclo real navegador → Reflex → n8n → navegador com o smoke existente.

## Capabilities

### New Capabilities

Nenhuma. Não há nova funcionalidade de produto.

### Modified Capabilities

Nenhuma. A correção restaura o comportamento já especificado em `n8n-chat-integration`; `skip_specs: true` declara uma mudança de configuração, documentação e ferramenta de verificação, sem deltas de comportamento.

## Impact

- Áreas afetadas: `.env` local ignorado pelo Git, documentação `docs/n8n-chat.md`, ferramenta de verificação em `scripts/` e operação do processo Reflex. `.env.example` já indica `/webhook/` e não precisa de correção da URL. Não armazenar a URL privada efetiva ou segredo em evidências.
- Referências consultadas: `docs/project-overview.md`, `docs/architecture.md`, `docs/n8n-chat.md`, `openspec/specs/n8n-chat-integration/spec.md`, cliente `vet_tech/shared/n8n_client.py` e smoke `tests/integration/n8n_bridge_smoke.py`.
- Diagnóstico confirmado por chamadas reais: configuração presente e HTTPS; URL local usa `/webhook-test/`; endpoint de teste não registrado; produção equivalente válida com o mesmo segredo. Não foi necessário modificar nem publicar workflow para obter sucesso em produção.
- Limite da evidência: o teste de produção foi direto pelo contrato HTTP, como visitante. Ainda não comprova a ponte do navegador nem consultas clínicas autenticadas. A porta 3000 registrada no log não estava escutando no momento da investigação.
- Privacidade: a verificação usa pergunta genérica, sem login, dados de pets ou prontuários. Não muda autorização clínica, auditoria ou notificações. Não expor o segredo, payloads, transcrições ou tokens nos logs da ferramenta.
- Não inclui implementação do chat tutor–veterinário, alterações visuais, mudanças no contrato do n8n, novos serviços, publicação do workflow ou correções clínicas não comprovadas. A change `chat-tutor-veterinario-pos-bot` permanece independente.
- Somente planejamento nesta etapa; a configuração ainda não foi alterada. Sem `design.md`: correção operacional localizada, sem novo modelo de dados, dependência ou decisão arquitetural.
