# Design

## Context
Ver proposal.md. Dashboard já usa worker background, concorrência 4 e cache curto. Contudo load_selected_pet sempre agenda histórico/consultas mesmo na rota Dashboard. _load_pets percorre espécies sequencialmente. xano_request_batch existe mas só Dashboard o usa. Há PNGs decorativos de 0,75–1,7 MB e cenários JPEG de cerca de 0,5 MB.

## Goals / Non-Goals
Reduzir chamadas e transferência, acelerar catálogos e reutilizar conexões sem compartilhar credenciais entre operações/sessões. Não alterar backend remoto, retries, TTL clínico, visual/LEDs ou migrar o servidor ativo entre modos.

## Decisions
- Após detalhes autorizados do pet, agendar histórico apenas se a rota atual for /prontuario. Entrada clínica continua usando o guard/worker existente, evitando duplicação se leitura ainda estiver em andamento. Testar chegada dos detalhes antes/depois da navegação.
- Reutilizar xano_request_batch em leitura de detalhes e catálogo, listagem/raças e lote clínico. Context manager aninhado reutiliza transporte da operação externa sem fechá-lo prematuramente; headers continuam por request. Nenhum cliente global permanente.
- Catálogos de raças independentes usam semaphore 4 e snapshot de token/geração. HTTP concorrente não publica resultados antes da revalidação da sessão. Preservar falhas parciais e 401.
- Gerar versões WebP de imagens estáticas, sem editar composição ou substituir fontes. Reduzir dimensões excessivas de mascotes transparentes ao necessário para exibição. Favicon PNG 64 px derivado da marca atual. Script reproduzível usa Pillow já instalado; sem dependência nova na execução do app.

## Risks / Trade-offs
- Histórico adiado poderia faltar na primeira seção → testar entrada clínica durante/depois da seleção e nova tentativa.
- Concorrência poderia elevar pressão na API → limite quatro, sem mudar retries e preservando isolamento.
- Compressão poderia afetar transparência/qualidade → preservar originais, alpha, validar decodificação e capturas nos dois temas.
- Medidas sintéticas não representam latência Xano real → registrar metodologia e não atribuir ganho percentual ao sistema completo.

## Migration Plan
Atualizar referências e compilar; sincronizar assets públicos. Verificar servidor ativo sem trocar seu modo. Reversão restrita a alterações desta mudança e referências dos assets.
