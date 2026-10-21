# Design

## Context

Ver `proposal.md`. `especie` possui nome e ID; `raca` possui nome e `especie_id`. As tabelas ainda não têm chaves normalizadas únicas. Pets e a futura aptidão veterinária referenciam IDs existentes; SRD é ausência de raça, não um registro obrigatório de catálogo.

## Goals / Non-Goals

**Goals:** revisar o conteúdo separado do código da interface e permitir carga repetível, rastreável e sem perda de vínculos.

**Non-Goals:** lista universal de animais, taxonomia científica, importação de registros pessoais, alteração de pets, administração pública de catálogos, especialidades veterinárias ou download automático durante a execução.

## Decisions

### Seção exclusiva de revisão dos registros

Na implementação, preparar arquivo de dados versionado em `xano/seed/` e relatório privado/local dos registros existentes, com resumo revisável sem credenciais. Cada espécie terá chave estável, nome de exibição e origem; cada raça terá chave, nome e referência à chave da espécie. A origem permite revisar a nomenclatura e evitar listas inventadas. Não fixar IDs remotos no arquivo.

O catálogo inicial será limitado e declarado como tal. Antes da carga, apresentar tabela de adições, correspondências e conflitos, agrupada por espécie. Usar fonte identificada para os registros que forem selecionados; a lista concreta é produto da tarefa de curadoria, não uma promessa de cobertura completa nesta proposta. Não publicar dados sem resolver correspondências ambíguas.

### Normalização sem fusão destrutiva

Comparar nomes por Unicode NFC, trim, espaços internos colapsados e casefold; preservar acentos e nome legível. Espécies usam nome normalizado; raças usam par espécie/nome normalizado. Sinônimos como Cão/Cachorro exigem mapeamento explícito no relatório, não heurística de fusão. Não renomear, excluir, trocar espécie de raça ou reassociar registros existentes automaticamente.

Criar proteção de unicidade normalizada no backend após inventário de duplicidades; entradas ambíguas bloqueiam o lote antes das escritas. A ferramenta administrativa usa o cliente/metadados Xano disponível com configuração por ambiente, fora da interface pública. Executar dentro de transação quando disponível; se a carga precisar de lotes, persistir manifesto por lote e só relatar sucesso completo após todos verificados. Uma falha informa contagens reais e possibilita retomar sem duplicar.

### Simulação, aplicação e reversão

Modo padrão é simulação sem escrita. Aplicação exige opção explícita de execução no ambiente escolhido, revalida o plano contra estado atual e evita IDs definidos por posição. Credenciais não entram em arquivos versionados ou logs. Reexecutar arquivo idêntico produz zero novas entradas. Registrar manifesto com versão/hash do conjunto e IDs somente criados nessa execução.

Rollback remove somente entradas criadas pelo lote que continuem sem referências e sem modificações posteriores; registros usados permanecem com aviso. Nunca remover entradas preexistentes ou pets para completar reversão. Verificar APIs de espécies/raças e cadastro SRD após a carga; cadastro veterinário deve enxergar as mesmas espécies quando implementado.

## Risks / Trade-offs

- [Nomes equivalentes] → mapeamento explícito e revisão; rejeitar conflito em vez de fundir IDs.
- [Mudança no banco entre simulação e aplicação] → nova validação de plano e chaves únicas no momento da escrita.
- [Lista incompleta] → documentar cobertura inicial e permitir ampliar o arquivo versionado por revisão futura.

## Migration Plan

Inventariar dados e referências; simular em teste; resolver conflitos; aplicar índices sem reescrever vínculos; executar carga revisada; comparar IDs/vínculos preexistentes e consultar catálogos pelas APIs atuais. Guardar manifesto para reexecução ou reversão restrita. Coordenar com `unificar-acesso-perfis` para não publicar scripts divergentes da tabela `especie`.
