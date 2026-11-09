# Design

## Context

O tutor exporta diretamente pelo cabeçalho de `pages/profile.py`. `request_consultation_pdf` e `generate_consultation_pdf`, em `features/clinical/state.py`, validam apenas o perfil tutor e usam o endpoint `tutor/pets/{pet_id}/consultas/{consulta_id}/exportar`. O mapeador `map_consultation_document` filtra complementos pelo par pet/consulta; o renderizador ReportLab já tem layout aprovado.

O atendimento veterinário apresenta confirmação de finalização em `components/clinical.py`; a listagem de consultas e abertura de atendimentos estão em `components/veterinary_schedule.py`. O histórico profissional existente valida `Clinical/assert_access` e audita leituras. Ver `proposal.md` para motivação.

## Goals / Non-Goals

**Goals:** compartilhar painel e pipeline entre os dois perfis; separar conferência de download; revalidar autorização no servidor; manter o template aprovado.

**Non-Goals:** envio por WhatsApp/e-mail, exportação de cada categoria avulsa, edição no painel, novas tecnologias ou armazenamento de documentos.

## Decisions

1. **Um diálogo Reflex compartilhado.** Criar `components/consultation_pdf.py`, conforme separação de componentes em `docs/architecture.md`, renderizado uma vez por página relevante. Corpo com páginas reais do PDF em área rolável e rodapé fixo com Fechar e Baixar PDF. Reutilizar mascote local com transparência, posicionada sobre a lateral visual; em telas estreitas reservar área própria sem ocultar texto. Usar estilos escopados em `assets/vet_tech.css`. O refinamento solicitado pelo usuário exige o próprio PDF: usar PDF.js local para renderizar páginas em canvas, com rolagem e carregamento progressivo, inclusive no celular. Isso justifica a biblioteca de visualização sem alterar o framework ou o gerador aprovado.

2. **Duas fases com autorização própria.** Acrescentar endpoints GET de prévia para tutor e veterinário no padrão `.../pets/{pet_id}/consultas/{consulta_id}/previa-pdf`, e POST de exportação para veterinário no padrão já usado pelo tutor. Ambos os GET retornam recorte publicado compatível com o mapeador e `auditoria_id` de visualização. POST conserva `operacao` UUID e a semântica atual de liberação para emissão. A fase de prévia não chama o POST existente, pois fechar o painel não deve registrar emissão.

3. **Reutilizar validações, filtragem e auditoria Xano.** Preferir funções compartilhadas em `xano/functions/clinical/` para montar o recorte por par pet/consulta, seguindo a estrutura real `xano/function/clinical/`. Tutor usa `assert_owner`; profissional usa `assert_access` com o mesmo bloqueio transacional de consentimento já usado em `vet_history_GET.xs`. Exportação profissional aceita consulta publicada do pet autorizado, preservando a distinção entre autor da consulta e ator. Incluir perfil e ID do ator na chave de operação para impedir colisão entre tutor e veterinário de mesmo ID; preservar chaves de retries do endpoint tutor existente. Não alterar entidades/DER: os campos de auditoria atuais devem ser reutilizados com eventos e contrato documentados.

4. **Contexto explícito da prévia.** Guardar alvo, perfil, rota e geração privada, distintos do detalhe do tutor e do atendimento veterinário. Manter no State serializado somente título, token de instância e estados de carregamento; enviar o PDF em evento efêmero para o visualizador, sem base64 persistente no State; DTO, tokens, bytes de PDF e chave idempotente permanecem privados. Fechar, navegar e expirar sessão limpam dados e invalidam operações. Guardar assinatura privada do DTO mostrado; comparar com DTO reconsultado para download. Se divergir, atualizar prévia e exigir novo clique, sem renderizar o PDF. Auditoria do POST continua significando liberação autorizada, não comprovação de arquivo salvo.

5. **Acessos do médico após publicação.** Ao concluir com sucesso, substituir o bloco simples de confirmação por mensagem e Exportar PDF. Ao reabrir finalizada, apresentar a ação no cabeçalho do atendimento somente leitura. Não oferecer exportação em rascunhos ou estados desconhecidos. Todos os acionadores, inclusive tutor, abrem o diálogo; a abertura gera a prévia autorizada e apenas Baixar PDF inicia o download após revalidação.

## Risks / Trade-offs

- [Prévia e download exigem leituras distintas] → carregamento explícito e bloqueio de duplo clique; auditoria separa conferência de emissão.
- [Consentimento revogado com painel aberto] → revalidar a cada operação, limpar a prévia em negativa e descartar respostas fora do contexto.
- [Dados sensíveis serializados para a prévia] → limitar ao recorte autorizado mostrado, sem persistência em storage/cache e limpar ao fechar/logout.
- [Mascote invade o conteúdo ou sai da tela] → espaço reservado e verificações visuais desktop/celular em ambos os temas.
- [Backend remoto não atualizado] → preparar e verificar os contratos em desenvolvimento antes de habilitar os novos acessos na entrega; registrar limitações de ambiente sem declarar integração não executada como aprovada.

## Migration Plan

Implementar e verificar funções/endpoints Xano antes da interface dependente; atualizar documentação de contratos e harness sintético. Validar State, mapeador, compilação e navegador em projeto isolado. A entrega remota deve usar o procedimento autorizado do projeto; não pressupõe publicação nesta etapa de planejamento. Rollback usa o desligamento de exportação existente; logs anteriores permanecem preservados.

## Otimização solicitada na aplicação

A prévia usa uma única leitura por abertura, deduplicada enquanto o mesmo painel está aberto. Fechar não consulta o backend; confirmar faz apenas um POST autorizado, sem recarregar histórico, agenda ou catálogos. O recorte compartilhado filtra todos os complementos por pet/consulta no banco e obtém nomes de diagnósticos por join, sem carregar o histórico completo ou o catálogo global. O PDF é gerado para a prévia após a leitura autorizada e seus bytes são mantidos somente em campo privado enquanto o painel estiver aberto. A confirmação revalida o acesso e reutiliza esses bytes quando o DTO não mudou, evitando renderização duplicada. O visualizador carrega páginas progressivamente, cancela renderizações e destrói o documento ao fechar.

O fluxo atual redireciona automaticamente para a agenda ao finalizar; a implementação manterá a confirmação no atendimento, com Exportar PDF e Voltar às consultas. Essa permanência permite a ação solicitada sem navegação/recarregamento. Ao abrir atendimento já finalizado, não carregar o catálogo de doenças destinado à edição. Não criar polling, prefetch nem cache global de prontuários.

## Refinamento visual confirmado pelo usuário

Painel com a mesma linguagem visual do seletor de data, mascote externa ao conteúdo, cabeçalho organizado e rodapé fixo. PDF.js com módulos/worker locais e versão fixa; importação somente ao abrir o visualizador, sem CDN e sem armazenamento em localStorage. Atualizar a versão da URL do CSS global para evitar a folha antiga observada na captura. O erro real de carregamento depende também da publicação pendente dos endpoints de prévia; não substituir autorização por cache visual.
