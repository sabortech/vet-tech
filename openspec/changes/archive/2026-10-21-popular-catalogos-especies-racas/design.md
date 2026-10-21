# Design

## Context

Ver `proposal.md`. `especie` possui nome e ID; `raca` possui nome e `especie_id`. As tabelas ainda não têm chaves normalizadas únicas. Pets e a futura aptidão veterinária referenciam IDs existentes; SRD é ausência de raça, não um registro obrigatório de catálogo.

## Goals / Non-Goals

**Goals:** revisar o conteúdo separado do código da interface e permitir carga repetível, rastreável e sem perda de vínculos.

**Non-Goals:** lista universal de animais, taxonomia científica, importação de registros pessoais, alteração de pets, administração pública de catálogos, especialidades veterinárias ou download automático durante a execução.

## Decisions

### Seção exclusiva de revisão dos registros

Recorte solicitado em 21/10/2026: cães e gatos, aproximadamente 20 raças por espécie. O conjunto `xano/seed/animal-catalog.json` usa as primeiras 20 raças do ranking AKC de registros de 2025 e a Shih Tzu já existente; para gatos, as dez raças CFA da lista de 2026 e dez adicionais do GCCF 2025. Fontes, nomenclatura, limitações geográficas e tabela de correspondências estão em `xano/seed/README.md`. A grafia legada `Shitzu` é alias explícito de Shih Tzu e deve manter seu nome/ID, sem fusão de registros.

Na implementação, preparar arquivo de dados versionado em `xano/seed/` e relatório privado/local dos registros existentes, com resumo revisável sem credenciais. Cada espécie terá chave estável, nome de exibição e origem; cada raça terá chave, nome e referência à chave da espécie. A origem permite revisar a nomenclatura e evitar listas inventadas. Não fixar IDs remotos no arquivo.

O catálogo inicial será limitado e declarado como tal. Antes da carga, apresentar tabela de adições, correspondências e conflitos, agrupada por espécie. Usar fonte identificada para os registros que forem selecionados; a lista concreta é produto da tarefa de curadoria, não uma promessa de cobertura completa nesta proposta. Não publicar dados sem resolver correspondências ambíguas.

### Normalização sem fusão destrutiva

Comparar nomes por Unicode NFC, trim, espaços internos colapsados e casefold; preservar acentos e nome legível. Espécies usam nome normalizado; raças usam par espécie/nome normalizado. Sinônimos como Cão/Cachorro exigem mapeamento explícito no relatório, não heurística de fusão. Não renomear, excluir, trocar espécie de raça ou reassociar registros existentes automaticamente.

Criar proteção de unicidade normalizada no backend após inventário de duplicidades; entradas ambíguas bloqueiam o lote antes das escritas. A ferramenta administrativa usa o cliente/metadados Xano disponível com configuração por ambiente, fora da interface pública. Executar dentro de transação quando disponível; se a carga precisar de lotes, persistir manifesto por lote e só relatar sucesso completo após todos verificados. Uma falha informa contagens reais e possibilita retomar sem duplicar.

Implementação: campo técnico interno e anulável `nome_normalizado`, índice único nesse campo em `especie` e composto com `especie_id` em `raca`. A carga só começa após confirmar os índices publicados; preenche a chave técnica dos registros anteriores sem alterar os campos de domínio. Escritas dos catálogos são administrativas e passam pela mesma normalização. A API pública mantém projeção explícita de ID/nome, sem expor o campo técnico. O manifesto é salvo antes e depois de cada escrita; resultado incerto exige conciliação por leitura, não repetição cega de POST.

### Simulação, aplicação e reversão

Modo padrão é simulação sem escrita. Aplicação exige opção explícita de execução no ambiente escolhido, revalida o plano contra estado atual e evita IDs definidos por posição. Credenciais não entram em arquivos versionados ou logs. Reexecutar arquivo idêntico produz zero novas entradas. Registrar manifesto com versão/hash do conjunto e IDs somente criados nessa execução.

Rollback remove somente entradas criadas pelo lote que continuem sem referências e sem modificações posteriores; registros usados permanecem com aviso. Nunca remover entradas preexistentes ou pets para completar reversão. Verificar APIs de espécies/raças e cadastro SRD após a carga; cadastro veterinário deve enxergar as mesmas espécies quando implementado.

A reversão administrativa exige suspensão de escritas nos catálogos, pets e aptidões durante a operação, pois a API de metadados não fornece transação única entre consulta de referências e exclusão. O comando exige `--writes-suspended`; a lista de referências consultadas é `pet`, `raca` e `veterinario_especie`, conforme o modelo atual. Essa suspensão não se aplica à carga aditiva.

Em 21/10/2026, após o bloqueio de tenant/sandbox no plano Free, o usuário autorizou explicitamente publicar e carregar diretamente no workspace atual, dispensando testes remotos prévios. Executar novo inventário e dry-run, publicação restrita aos dois schemas e carga com manifesto; depois conferir por leitura todas as entradas, IDs, relações, ausência de duplicidades e preservação dos registros anteriores. Consultar as opções públicas do cadastro veterinário. Não criar contas ou pets de teste nem declarar executados os cenários autenticados de cadastro, concorrência e reversão remota; os testes locais já realizados permanecem como evidência separada.

## Risks / Trade-offs

- [Nomes equivalentes] → mapeamento explícito e revisão; rejeitar conflito em vez de fundir IDs.
- [Mudança no banco entre simulação e aplicação] → nova validação de plano e chaves únicas no momento da escrita.
- [Lista incompleta] → documentar cobertura inicial e permitir ampliar o arquivo versionado por revisão futura.

## Migration Plan

Inventariar dados e referências; simular no destino sem escrita; resolver conflitos; publicar somente os índices/campos técnicos dos catálogos sem reescrever vínculos; executar carga revisada; comparar IDs/vínculos preexistentes e conferir os catálogos por leitura, conforme a dispensa de ambiente isolado autorizada acima. Guardar manifesto para reexecução ou reversão restrita. Coordenar com `unificar-acesso-perfis` para não publicar scripts divergentes da tabela `especie`.
