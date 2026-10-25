# Revisão da implantação clínica

Execução autorizada pelo usuário com “pode publicar e testar” em 21/10/2026. Publicação e verificação concluídas; resultado em `verification.md` e `smoke-result.json`. O plano abaixo registra o escopo apresentado antes de executar.

## Destino e pacote

Instância `x8ki-letl-twmt.n7.xano.io`, workspace **167758**, perfil CLI `vetech`, branch padrão do perfil. Não fornecer `-b live`: esse nome não existe neste destino e a tentativa de dry-run com esse parâmetro foi recusada sem escrita. O dry-run sem sobrescrever a branch foi aceito.

Pacote reproduzível: `.venv/clinical-bundle`, construído por `scripts/prepare_clinical_bundle.py`. Os 32 arquivos e seus hashes estão em `bundle-manifest.json`. Contém somente dez schemas clínicos, seis funções, um grupo e quinze endpoints. Preview: **3 tabelas criadas, 7 atualizadas, 6 funções criadas, 1 grupo e 15 endpoints criados**. Sem importar registros, credenciais, variáveis de ambiente ou fontes de autenticação existentes; sem sincronização destrutiva.

O preview inicial sinalizou UPDATE_FIELD no attachment legado `exame.arquivo`. O snapshot tinha tipo attachment, único, público e não obrigatório. A fonte final explicita a anulabilidade normalizada pelo importador (`attachment? arquivo?`) para exames sem arquivo. Tipo, visibilidade, estilo e campo preservados; sem excluir arquivos. Filtros de texto restaurados pelo schema canônico e conferidos remotamente. Preview final: nenhuma diferença. Detalhes em `verification.md`.

Frontend preparado localmente; compilação seca não publica nem inicia servidor. Publicar os endpoints é necessário antes de usar as novas telas com o backend real. A conta atual não fornece tenant isolado nem outro workspace. Não executar smoke sobre pets ou contas existentes.

## Verificação remota proposta — requer autorização

1. Repetir inventário somente de leitura e salvar snapshot privado. Bloquear se surgirem conflitos de referência, consentimentos duplicados ou dados que tornem os índices incompatíveis. Registrar os IDs e digests anteriores de cada tabela antes de criar fixtures.
2. Publicar exclusivamente o bundle revisado, com a transação do import habilitada, confirmação interativa e sem `--force`, `--delete`, `--truncate`, `--records` ou `--no-transaction`.
3. Criar **duas identidades de tutor, duas identidades veterinárias e três pets sintéticos**, todos identificados por um prefixo único `qa-clinical-<uuid>`, emails no domínio reservado `example.invalid` e senhas aleatórias guardadas somente em `.venv`. CRMs e nomes das fixtures são valores de teste, não profissionais reais. Duas espécies já existentes serão referenciadas sem alterar seus catálogos. Dois pets pertencem ao tutor A e um ao B. Vincular os dois veterinários à espécie de teste. Não criar mensagens, emails ou notificações.
4. Limitar a **30 consultas sintéticas**, **3 referências de doença sintéticas** e complementos/logs exclusivamente dessas fixtures. Registrar imediatamente cada ID criado em ledger privado, incluindo vínculos de autenticação/especialização. Não usar tokens de usuários existentes nem gerar dados de saúde para pets reais.
5. Exercitar APIs com tokens cruzados de tutor/veterinário, pet alheio, profissional responsável e outro autorizado; conferir negação e ausência de dados sensíveis. Verificar revogação durante atendimento e retomada depois de reativar, mantendo o histórico do tutor.
6. Reservar em 08h/17h; rejeitar passado e horários externos. Repetir mesma chave e payload divergente. Disputar simultaneamente pet/profissional no mesmo início. Verificar uma única reserva/concessão e nenhum consentimento órfão; não tratar respostas 500 como conflito de negócio aprovado.
7. Confirmar agenda por dia no fuso, lista paginada e pendências antigas, redação de dados sem consentimento, início manual antes do horário e retomada sem modificar o início.
8. Salvar rascunho, ler novamente, disputar versão e tentar IDs forjados. Confirmar ausência do rascunho em todas as respostas do tutor. Testar todos os grupos vazios e válidos, doença com evolução retroativa e exames solicitados/realizados.
9. Finalizar repetidamente e sob concorrência, conferir IDs compartilhados no histórico/seções e bloquear reabertura. Forçar falha intermediária usando referência de doença inexistente **após complemento sintético válido**; conferir rollback de todos os registros e preservação do rascunho. Para falha de auditoria, usar apenas conflito de chave única de fixture previamente reservado no ledger, sem editar logs de usuários nem enfraquecer o endpoint. Remover a fixture de falha antes de repetir.
10. Percorrer as telas com essas contas em desktop/celular e teclado, inclusive fechar modal/foco, Voltar, troca de pet, logout, URL direta e aviso de rascunho. Se automação de navegador não estiver disponível, registrar a parte visual como pendente, sem alegar teste concluído.
11. Limpar somente registros sintéticos cujos IDs constem no ledger e estejam ausentes do inventário anterior, respeitando referências: complementos/evoluções/condições/logs/consentimentos/consultas, pets, vínculos e identidades. Confirmar a ausência de referências reais antes de excluir cada fixture. Não truncar tabelas ou selecionar exclusão por aproximação de nome. Se houver dúvida, preservar o registro e relatar o ID no ledger privado.
12. Repetir inventário: todos os IDs anteriores permanecem com o mesmo conteúdo; nenhuma fixture ou trava residual. Contadores de sequência podem avançar após testes/exclusões e não serão resetados. Registrar apenas contagens/resultados sanitizados no repositório.

## Reversão

Se import falhar, confirmar rollback de metadados antes de repetir. Se o runtime falhar após publicação, desabilitar a entrada do fluxo e voltar o frontend à versão anterior; restaurar somente código de endpoints conforme snapshot revisado. Preservar tabelas, campos, arquivos, históricos e rascunhos. Não restaurar registros antigos sobre gravações posteriores. A entrega permanece aberta até os critérios de autorização, atomicidade e interface serem comprovados.
