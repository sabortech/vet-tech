# Verificação de aplicação

## Resultado

Implementação local concluída na mesma change. A referência oficial é `docs/templates/vettech-prontuario-referencia.pdf`, fornecida pelo usuário na continuação. Como esse caminho não existia no checkout, foi criada uma cópia do PDF entregue em `docs/VetTech — relatório clínico pronto para orientar a implementação.pdf`, preservando o original. SHA-256: `acf5b3f7c4e24468024a21a5074aa22123b5093def82f0f802b9c03a3624e6e7`.

O template ReportLab gera a capa, marca d'água, cabeçalho, texto, tabelas e paginação dinamicamente. Somente dois gráficos individuais com transparência foram extraídos para `assets/consultation-pdf/`; nenhuma página é usada como fundo. Dados fictícios não fazem parte do template de produção. Evidência sintética revisável: `evidence/relatorio-referencia-implementado.pdf`, capa e página interna em PNG.

## Ambiente e desempenho

- Alvo confirmado: apenas execução local, Linux/Python 3.13.5, Reflex 0.9.11, ReportLab 5.1.0. Sem homologação implícita de hospedagem externa.
- Fonte Bitstream Vera Unicode distribuída com ReportLab e licença original conferidas. Não depende de fontes externas ou da fonte comercial do arquivo de referência.
- Medição local atual: PDF curto de duas páginas com 434.114 bytes, 0,201 s na primeira geração e 0,169 s com gráficos reutilizados. Documento longo de 20 páginas: 455.596 bytes, 2,558 s; último marcador preservado. Pico RSS do processo de medição: 55.636 KiB. São medições de amostras sintéticas, não limites universais de capacidade; detalhes em `evidence/template-performance.json`.
- Limites: 200.000 caracteres, 5.000 complementos, 2 MiB por PDF, espera de 20 s e dois slots de renderização por processo. Trabalho em thread fora do event loop; slot continua ocupado até a thread terminar após timeout. Cache contém apenas gráficos estáticos, nunca dados clínicos/documentos. Uma chamada Xano por tentativa, com chave privada reaproveitada nos retries.
- Download em memória com MIME application/pdf e nome baseado em ID numérico. Nenhum arquivo clínico vai para assets, URLs públicas, State serializado ou storage. Arquivos de evidência são exclusivamente sintéticos.

## Backend remoto

- Pull somente leitura do workspace de desenvolvimento 167758: 97 documentos, sem registros ou variáveis de ambiente no export. Comparação de proprietário, histórico, leituras tutor, auditoria, log_acesso e índice único de operacao não encontrou divergência semântica de autorização/auditoria; diferenças de formatação foram inspecionadas. Artefatos privados em /tmp, resumo em evidence/contract-comparison.json.
- Publicação limitada a um novo endpoint de exportação após dry-run. Nenhum esquema de tabela, função de auditoria ou endpoint preexistente foi sobrescrito. O runtime recusou error_type=conflict; corrigido para inputerror (400), conforme os padrões existentes, e repetido com sucesso.
- `scripts/consultation_pdf_smoke.py --profile '<perfil configurado>' --workspace 167758 --development --folder .venv/clinical-smoke/pdf-export-local`: passou. Reutiliza o harness clínico e ledger privado. As credenciais não são impressas. Configuração opcional do perfil foi adicionada aos construtores existentes mantendo os padrões anteriores.
- Checks: consulta própria finalizada, ausência de rascunhos/condições consolidadas, negativa de outro tutor/pet/perfil, ID inexistente, anônimo, agendada, em atendimento, cancelada e sem status; retry e concorrência sem duplicação; rejeição da chave reaproveitada para outro alvo; tutor ator e profissional responsável corretos; dados remotos autorizados renderizados em PDF e associados ao audit_id real.
- Falha real de auditoria exercitada diretamente na função Clinical/audit pelo debugger, com chave de um log sintético já existente: result.status=exception por duplicidade, sem novo log ou alteração do original. Tentativa de DELETE pela API de usuário recusada. Não foi desligada a auditoria global nem alterada a função compartilhada para induzir pane no endpoint. O bloqueio de download quando a API/auditoria falha foi conferido no estado e no navegador sintético.
- As fixtures e logs de desenvolvimento foram preservados no ledger privado; nenhum prontuário real ou log histórico foi apagado. Resumo sanitizado em evidence/remote-export-checks.json.

## Testes e regressão

- `PATH=/home/usuario/.nvm/versions/node/v24.20.0/bin:$PATH .venv/bin/python -m unittest discover -s tests/unit`: **299 testes passaram**. Inclui testes existentes e novos de DTO, renderização, texto/linha maior que uma página, acentuação, texto parecido com HTML/URL tratado como texto, campos opcionais, limites, concorrência, timeout, erros HTTP, sessão, troca de pet/consulta, ida e volta ao mesmo ID, resposta atrasada e finally antigo sem desbloquear operação nova.
- A execução assíncrona precisou ocorrer fora da restrição de sockets do sandbox para os callbacks de threads. A primeira execução completa também encontrou Node fora do PATH padrão; repetida com o Node do projeto, passou.
- `reflex compile --dry`: passou com o botão e a chave de rollback.
- `openspec validate exportar-consulta-pdf --strict`: passou.
- `git diff --check`: passou.
- Prévia de produção isolada em /tmp/vet-pdf-preview na porta 3041, usando `tests/integration/consultation_pdf_preview.py`, sem APIs reais.
- `PYTHONPATH=/tmp/vet-tech-browser-tools .venv/bin/python tests/integration/consultation_pdf_browser.py --chromium /home/usuario/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome --output openspec/changes/exportar-consulta-pdf/evidence/browser`: passou. Download %PDF- com nome correto e dados correspondentes, permanência na tela, dois contextos simultâneos, legado sem botão, troca de consulta durante solicitação sem download atrasado, falha de auditoria simulada sem arquivo, desktop e celular sem overflow nem exceção JavaScript.
- O primeiro teste móvel identificou falta de wrap nos botões de controle do harness, corrigida no próprio harness; não foi necessário alterar o layout da aplicação.
- Inspeção visual da capa e página interna confirma identidade do PDF oficial, tartaruga V, marca d'água e tabelas dinâmicas; a fonte Unicode sans serif é uma aproximação local documentada.

## Rollback e pendências

`VET_TECH_CONSULTATION_PDF_ENABLED=false` e reinício desativam botão e solicitação no servidor, preservando o conteúdo clínico e os logs. O teste de rollback confirmou que não ocorre chamada Xano nem alteração do detalhe. A execução local está validada; uma futura hospedagem externa precisará da sua própria homologação. Não foram criados commit, PR ou nova change nesta implementação.

## Ajuste visual posterior

Texto VetTech da marca d’água interna baixado 8 mm. Comparação automatizada dos PDFs antes/depois com pypdf confirmou mesmo número de páginas, mesmo texto extraído e mesmas posições de todos os textos, exceto o deslocamento esperado do VetTech em fonte 40. Inspeção visual confirmou o espaço abaixo da tartaruga. Evidência sintética em evidence/marca-dagua-espacada.pdf.
