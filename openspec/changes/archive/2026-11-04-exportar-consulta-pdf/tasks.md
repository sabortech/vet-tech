# Tasks

## 1. Checkpoints de ambiente e modelo

- [x] 1.1 Confirmar o ambiente Xano de desenvolvimento autorizado e comparar rotas/grupos, funções de histórico/proprietário, tabela log_acesso e índice único de operacao com os contratos locais; entregar registro sanitizado em verification.md, sem credenciais, e interromper integração funcional se houver divergência de autorização ou auditoria.
- [x] 1.2 Identificar runtime/limites reais da hospedagem e executar prova isolada de ReportLab no Python de destino, com fonte Unicode licenciada e geração A4 em memória; registrar versão candidata, licença, consumo, tamanho/base64, tempo e limites de bytes/concorrência em verification.md. Fixar a dependência somente após sucesso; se outro motor for necessário, revisar o design antes de continuar.
- [x] 1.3 Adotar o PDF oficial fornecido pelo usuário em docs/templates/vettech-prontuario-referencia.pdf, conferir mascotes, marca d’água, verde, margens e paginação, sem assinatura/CRMV inventados; registrar a origem e a decisão visual em verification.md.

## 2. Operação Xano autorizada e auditada

- [x] 2.1 Implementar o endpoint proposto export_consultation_POST.xs com auth tutor, assert_owner, vínculo pet/consulta, exigência de finalizada e recorte por consulta_id usando Clinical/history; acrescentar testes adjacentes ao smoke clínico para próprio tutor, terceiro, token de outro perfil, IDs inexistentes/forjados, agendada, em atendimento, cancelada e sem status, comprovando ausência de dados clínicos em negativas.
- [x] 2.2 Registrar exportar_consulta na mesma transação antes da resposta, com tutor ator, profissional responsável, pet/consulta e timestamp, reutilizando log_acesso.operacao; testar falha de auditoria, retries concorrentes, resposta perdida, mesma chave com alvo diferente, nova emissão e imutabilidade, verificando exatamente um log por operação autorizada e nenhum sucesso falso.
- [x] 2.3 Documentar novo contrato, erros, semântica de liberação para emissão e idempotência em docs/consulta-pdf.md; publicar/verificar somente no ambiente de desenvolvimento autorizado e conferir resposta e trilha de auditoria com fixtures sintéticas. Antes de usar scripts/clinical_smoke.py, confirmar seu destino explícito e ledger; guardar comandos/resultados sanitizados em verification.md.

## 3. DTO e documento em memória

- [x] 3.1 Criar normalização em features/clinical/consultation_pdf.py, aceitando apenas envelope autorizado/auditado e IDs/status consistentes, usando shared/dates.py; adicionar testes unitários para campos opcionais, zero, datas civis/instantes, dose/unidade, complementos do mesmo pet/consulta, legados sem vínculo, doença consolidada e resposta inválida, sem usar o cache visual como fonte.
- [x] 3.2 Implementar template/renderizador isolado no mesmo domínio, com A4 e identidade aprovados, fonte Unicode local, bytes em memória, conteúdo escapado e assets fixos; testar assinatura %PDF-, conteúdo extraído correspondente, português, múltiplas páginas, texto/linha maior que uma página, campos ausentes e markup/URLs/caminhos maliciosos sem acesso externo ou persistência. Registrar inspeção visual sintética em verification.md.
- [x] 3.3 Registrar em requirements.txt a versão homologada do único motor PDF e documentar fonte/licença, configuração, limites de tamanho/tempo/concorrência e execução do teste do gerador em docs/consulta-pdf.md; verificar instalação no runtime alvo e ausência de dependências alternativas não utilizadas.

## 4. Evento e botão no detalhe do tutor

- [x] 4.1 Adicionar evento de exportação ao ClinicalMixin existente, com xano_request, chave privada de retry, loading, geração própria, renderização fora do event loop e revalidação antes de rx.download; ampliar test_clinical_state.py para clique repetido, retry, falha de geração, 401/403/404/409/429/5xx, timeout e falha de auditoria, garantindo ausência de download parcial e liberação correta de loading.
- [x] 4.2 Invalidar exportação em logout, troca de sessão/pet/consulta e saída do detalhe, inclusive ida e volta ao mesmo ID; testar resposta HTTP e renderização atrasadas e finally de operação antiga, confirmando que não entregam PDF nem alteram loading/feedback de outra operação ou sessão.
- [x] 4.3 Inserir Exportar PDF junto a Voltar à lista em consultation_detail(), somente para consulta finalizada elegível, com processamento e mensagens acessíveis; verificar em navegador sintético download application/pdf com nome seguro, permanência no detalhe, falhas tratadas, legados ainda legíveis e dois tutores exportando sem mistura. Reutilizar padrão de tests/integration/consultations_browser.py; registrar capturas e atualizar docs/consulta-pdf.md com a experiência final.
- [x] 4.4 Ampliar a allowlist de mensagens de xano_client apenas para novos erros de domínio necessários; estender test_xano_client_clinical.py para status, bearer/tenant preservados e corpo arbitrário contendo dados sensíveis, comprovando sanitização sem expor tokens ou payload.

## 5. Verificação integrada e liberação

- [x] 5.1 Executar testes unitários clínicos e do cliente, regressão de consultas/permissões em navegador, reflex compile --dry e smoke remoto de desenvolvimento com exportação/auditoria confirmadas; conferir correspondência entre consulta exibida, conteúdo PDF e log, além de não haver arquivos públicos ou logs sensíveis, registrando comandos e resultados em verification.md.
- [x] 5.2 Validar a change com openspec validate exportar-consulta-pdf --strict, revisar docs/consulta-pdf.md e evidências, confirmar checkpoints de deploy/Xano/modelo e ensaiar retirada da ação de exportação preservando dados/logs; liberar somente com todas as verificações aplicáveis concluídas.
