# Exportação de consulta em PDF

Implementação da change `exportar-consulta-pdf` para execução local. O detalhe de uma consulta finalizada do tutor oferece Exportar PDF, com autorização e auditoria no Xano antes da geração em memória.

## Contrato de exportação

`POST /api:vettech-clinical/tutor/pets/{pet_id}/consultas/{consulta_id}/exportar`

Autenticação de tutor pelo cliente Xano existente, com bearer de sessão no servidor e X-Tenant quando configurado. Corpo: `{"operacao":"<uuid-v4>"}`. IDs devem ser inteiros positivos.

O Xano valida propriedade atual e o par pet/consulta, aceita somente status explícito `finalizada`, reutiliza o histórico publicado e devolve o recorte da consulta com `pet: {id, nome}`, `vacinas`, `medicamentos`, `diagnosticos`, `exames` e `auditoria_id`. Complementos sem consulta ou de outra consulta/pet não integram a resposta. Não retorna rascunho ou condições consolidadas.

A exportação é auditada como `exportar_consulta` antes de devolver os dados. O log identifica tutor ator, profissional responsável, pet, consulta e timestamp. Significa liberação autorizada para emissão; não comprova que o navegador salvou o arquivo. O índice único da operação impede duplicação. Retry da mesma tentativa usa a mesma chave e revalida acesso; nova emissão explícita usa outra chave. Uma chave já associada a outro alvo é rejeitada. Se uma corrida perder a inserção única, a requisição falha sem dados; retry recupera o registro autorizado após revalidação.

Erros: sessão inválida, pet/consulta indisponível, estado inelegível e chave em conflito. Falha interna ou de auditoria nunca devolve documento parcial. Nenhum endpoint genérico público de edição de logs é criado.

## Verificação em desenvolvimento

O harness reaproveita `scripts/clinical_smoke.py` e seu ledger privado. Requer seleção explícita do perfil, workspace e modo desenvolvimento:

```bash
.venv/bin/python scripts/consultation_pdf_smoke.py \
  --profile '<perfil-local>' --workspace <workspace-de-desenvolvimento> \
  --development --folder .venv/clinical-smoke/pdf-export-local
```

Cria identidades e registros **sintéticos**, rastreados em `.venv/clinical-smoke/`, sem imprimir tokens ou prontuários. Não usar em produção. Não versionar ledger, credenciais ou respostas privadas. O harness não remove logs de auditoria; preserva as fixtures para inspeção de desenvolvimento.

Testes locais do DTO:

```bash
.venv/bin/python -m unittest discover -s tests/unit -p test_consultation_pdf.py
```

O modelo e as medições locais do gerador estão em `openspec/changes/archive/2026-11-04-exportar-consulta-pdf/evidence/`. O modelo oficial fornecido pelo usuário e os testes estão registrados em verification.md da change.

## Layout e execução local

A referência oficial é `docs/templates/vettech-prontuario-referencia.pdf`, fornecida pelo usuário. O template Python reproduz capa, verde, mascotes, marca d'água translúcida, cabeçalho e rodapé numerado. Usa apenas dois gráficos individuais extraídos para `assets/consultation-pdf/`; o PDF de referência não é carregado no runtime nem usado como fundo. Todas as informações e tabelas são dinâmicas. Os dados fictícios do exemplo não entram no gerador de produção.

O gerador usa ReportLab 5.1.0 com fontes Unicode Bitstream Vera distribuídas no pacote. A licença dessas fontes permite uso/redistribuição com software; seus avisos permanecem na distribuição ReportLab. Não depende de fontes instaladas no sistema ou downloads de fontes. Instalar dependências com `.venv/bin/pip install -r requirements.txt`; para leitura/validação automatizada do conteúdo PDF, usar `requirements-test.txt`.

Limites locais: 200.000 caracteres clínicos totais, 5.000 complementos, 2 MiB por PDF e 20 segundos de espera. Há duas renderizações simultâneas por processo. Geração acontece em thread fora do event loop; um trabalho que ultrapasse a espera mantém seu slot até a thread terminar. Valores acima dos limites falham sem PDF parcial. PDFs/DTOs/bytes não ficam em State serializado, cache global, diretório público ou storage. Apenas os dois gráficos estáticos e o registro de fontes são reutilizados em memória. A ação consulta o Xano uma vez por tentativa e usa a chave privada para retries.

Na tela de detalhe, Exportar PDF aparece apenas para consulta finalizada. O botão indica processamento, impede clique duplicado e informa falhas seguras. Troca de sessão/pet/consulta, saída do detalhe ou mudança de rota invalidam o resultado; a renderização atrasada não libera download em outro contexto. Uma nova exportação explícita depois do sucesso gera nova operação auditada. A identificação profissional usa o ID real disponível, sem inventar nome, CRMV, assinatura ou clínica.

Para testar o navegador, copiar `tests/integration/consultation_pdf_preview.py` para um projeto Reflex isolado em `/tmp`, com assets da aplicação e `VET_TECH_SOURCE_ROOT` apontando para este checkout. Rodar em produção na porta escolhida; executar `consultation_pdf_browser.py` com `--url`, `--chromium` e `--output`. Usa somente dados sintéticos, incluindo falha de auditoria simulada. Para desligar a ação no rollback, retirar o botão/evento da publicação local; os logs e registros Xano permanecem intactos. A importação de regressão/rollback do componente sem o botão foi validada pela compilação anterior à integração.

Rollback sem remover código: definir `VET_TECH_CONSULTATION_PDF_ENABLED=false` no servidor e reiniciar a aplicação. Isso oculta o botão e bloqueia a solicitação no servidor; não modifica registros clínicos, PDFs já baixados ou logs Xano. O padrão é habilitado. O teste unitário verifica que a desativação não chama o Xano nem altera os dados da consulta.

## Prévia compartilhada e exportação profissional

Todos os acessos de Exportar PDF da consulta abrem um painel no padrão do seletor de data, com tartaruga espreitando ao lado, páginas reais do PDF roláveis e Baixar PDF no rodapé. Abrir gera o PDF para visualização após a leitura autorizada, sem download automático. PDF.js local renderiza somente páginas próximas da área visível e libera documento/canvases ao fechar. Não há edição.

Contratos adicionais no grupo `vettech-clinical`:

- `GET /tutor/pets/{pet_id}/consultas/{consulta_id}/previa-pdf`
- `GET /veterinario/pets/{pet_id}/consultas/{consulta_id}/previa-pdf`
- `POST /veterinario/pets/{pet_id}/consultas/{consulta_id}/exportar`, corpo `{"operacao":"<uuid-v4>"}`.

GET autoriza e audita `visualizar_previa_pdf`; devolve o recorte publicado e `auditoria_id`, sem emitir PDF. POST autoriza novamente e audita `exportar_consulta`. A chave profissional inclui `veterinario` e o ID do ator; a chave tutor anterior permanece compatível. O ator profissional fica em `log_acesso.veterinario_id`; o autor do prontuário é recuperado pela consulta vinculada, sem trocar a autoria clínica. Leituras e exportação profissional usam `clinical_lock` e `Clinical/assert_access` na mesma transação. Sem consentimento ativo ou em falha de auditoria não há documento liberado.

O médico encontra a ação na confirmação do atendimento finalizado e no cartão de consulta finalizada da agenda/listagem. A conclusão permanece na tela de atendimento, com Voltar às consultas disponível. O painel usa alvo próprio, sem exigir selecionar um pet no perfil tutor. O endpoint de prévia e a função `Clinical/consultation_document` devem estar publicados antes de usar a nova interface; erro de endpoint não dispara fallback para exportação direta.

O frontend faz um GET por abertura e um POST por confirmação; cliques repetidos enquanto a mesma prévia está aberta não duplicam GET. Fechar, rolar ou mudar tema não consulta o Xano. Não há polling/prefetch nem recarga de histórico/agenda. O PDF é gerado uma vez para a prévia e seus bytes ficam em campo privado somente enquanto o painel está aberto; a confirmação revalida o DTO e reutiliza o mesmo arquivo se não mudou. Reabrir atendimento finalizado dispensa catálogo de doenças usado para editar. No backend, a função compartilhada filtra complementos por pet e consulta no banco e obtém os nomes de diagnósticos por join; não lê o histórico completo do pet, condições consolidadas ou catálogo global de doenças.

Mudança de conteúdo entre prévia e download atualiza as informações e exige novo clique. Fechar o painel, trocar pet/consulta/perfil/rota ou encerrar sessão invalida operações e limpa a prévia. Respostas atrasadas são descartadas. Negativa de acesso limpa os dados apresentados. Retry de falha de exportação preserva a operação até o sucesso; outra emissão explícita gera UUID novo. Mensagens não expõem erros internos.

Verificação: `test_consultation_pdf_preview.py` mede o orçamento de chamadas e isolamento; `test_clinical_state.py` conserva as regressões de PDF e `test_attendance_notifications.py` verifica conclusão sem redirecionamento. O harness `consultation_pdf_smoke.py` inclui prévia de ambos os perfis, comparação com o download, idempotência e revogação/restauração de consentimento nas fixtures sintéticas. O harness de navegador existente cobre os quatro acionadores, teclado, temas e 390/1280 px. Nunca executar fixtures em produção nem versionar ledgers privados.

O visualizador usa PDF.js 6.5.438, módulos/worker locais em `assets/pdf-viewer/`, licença Apache-2.0 preservada. O módulo é importado sob demanda, sem CDN, URL pública de prontuário ou base64 no State serializado. O CSS global recebeu uma nova versão na URL para invalidar a folha antiga observada no navegador.

Publicação da prévia compartilhada concluída no workspace 167758 após autorização: 56 checks de backend e verificação em `localhost:3000` nos dois perfis com contas fictícias passaram. Ver `openspec/changes/archive/2026-11-09-unificar-previa-pdf-tutor-veterinario/verification.md`. Um painel que estava aberto em erro pode usar Tentar novamente; não é necessário reiniciar a aplicação para disponibilizar os novos endpoints.
