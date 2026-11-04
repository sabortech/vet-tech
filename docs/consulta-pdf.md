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
