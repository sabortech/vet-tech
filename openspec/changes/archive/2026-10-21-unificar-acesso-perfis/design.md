# Design

## Context

Ver `proposal.md`. A branch `alternar-pet` já contém seleção segura de pets e testes reais arquivados. `State` concentra sessão, catálogos e cadastro/seleção; `profile_view` compõe detalhes, lista e formulário permanentes. As APIs de produção usadas pelo app são `tutor/login` e `tutor/signup`; os endpoints quick-start de `user` não representam o domínio e não serão reaproveitados.

`veterinario` está com `auth = false`, campo `cmv`, senha `senha`, especialidade textual e clínica opcional no schema, sem índices únicos profissionais. `docs/domain-model.md` contradiz a obrigatoriedade da clínica e afirma habilitação garantida pelo CRMV. A decisão atual é clínica opcional e validação sintática, que precisa ser refletida na documentação durante a implementação.

## Goals / Non-Goals

**Goals:** identidade de domínio verificável, e-mail globalmente único e navegação que reutiliza o contexto seguro de pet. Entregar as fatias de cadastro, login e menu com seus próprios testes antes da verificação conjunta.

**Non-Goals:** dupla identidade por e-mail, comprovação externa de CRMV, edição de conta, administração de clínicas, acesso clínico veterinário, agenda, upload clínico, notificações e importação ampla de catálogos. A carga de espécies/raças terá change independente.

## Decisions

### Cadastro e login

Manter `/cadastro` e `/login` e a identidade visual Nunito/verde existente. Somente o cadastro possui escolha de perfil. Criar `POST /acesso/login` no grupo Authentication para e-mail/senha, respondendo `{authToken, perfil, identidade_id}`; o servidor resolve e valida a única identidade. Manter a resposta legada de `tutor/login` para compatibilidade. Cadastro tutor continua por `tutor/signup`, agora protegido pela unicidade global; criar `POST /veterinario/signup`. Ambos retornam confirmação sem sessão. Não alterar os endpoints quick-start de `user` para acomodar o domínio.

O frontend usa perfil da resposta como encaminhamento, e confirma a identidade por endpoint protegido da respectiva entidade (`tutor/me` ou `veterinario/me`). Um perfil manipulado pode no máximo escolher uma tentativa de rota, nunca obter identidade ou permissões. Tokens são gerados contra sua própria tabela, com validade de 24 horas e claims emitidas pelo backend; preservar tokens tutor existentes. Nenhum endpoint tutor aceita token veterinário, mesmo com IDs iguais. Não implementar um decodificador caseiro de token nem confiar em claims sem validação.

A documentação oficial descreve tokens vinculados à tabela autenticável e autenticação com múltiplas tabelas: https://www.xano.com/learn/all-about-authentication-in-xano/ . Verificar as assinaturas XanoScript atuais antes de editar e provar o isolamento na integração real.

### Reserva atômica de e-mail

Um simples índice único em cada tabela permite duplicidade cruzada. Adicionar registro técnico de reserva de e-mail normalizado com índice único, sem senha e sem autenticação: ele aponta para perfil e identidade de domínio. Não é uma entidade `user`, não concede autorização e não substitui tutor/veterinário.

Cadastro reserva e-mail, cria identidade e vínculos e conclui a reserva numa transação de banco. Falha reverte todos os passos; índice único arbitra concorrência. Todos os caminhos de criação de tutor/veterinário devem usar a reserva. Login exige correspondência entre reserva e entidade e falha de forma genérica se houver divergência ou ambiguidade. Alternativa rejeitada: consultar as tabelas e depois inserir sem proteção concorrente. Não concluir a tarefa sem comprovar transação e disputa real de cadastros no Xano.

### Registro profissional e catálogos

Proposta de formato simples: CRMV de 1–20 caracteres ASCII `[A-Za-z0-9]`, trim externo, uppercase e UF brasileira em campo separado. A chave única é `(UF, CRMV normalizado)`; não exigir somente números, tamanho fixo ou serviço externo. A interface pede o registro sem prefixo CRMV/UF. Este formato é uma decisão técnica desta proposta, não uma regra de habilitação legal.

Migrar `cmv` sem descartar o original; preservar `senha` e seu hash ou renomeá-la de forma compatível com o mecanismo nativo, após conferir os dados existentes. Não tentar reprocessar hashes como senhas em texto. Habilitar autenticação veterinária no mecanismo nativo do Xano.

Espécies usam `especie` já existente. Introduzir catálogo `especialidade` e associativas veterinário/espécie e veterinário/especialidade, com pares únicos. Exigir pelo menos uma entrada em cada seleção; clínica pode ficar nula. Caso informada, validar sua existência sem oferecer gestão de clínicas. Disponibilizar opções mínimas de clínicas existentes, especialidades e espécies para o formulário público, com projeção explícita de ID/nome; isso não amplia as APIs tutor protegidas de catálogo. Não expor contatos privados ou registros de pessoas.

Definir conjunto mínimo de especialidades versionado como parte desta change (incluindo Clínica geral), garantindo que o formulário funcione em banco novo; a expansão de espécies e raças pertence à outra change. Catálogos vazios ou indisponíveis mostram erro recuperável e não criam vínculos fictícios. Selecionar aptidões é declaração profissional e não autoriza consultar pets.

### Navegação e estado

Extrair componentes de navegação/modal para `components/` e composição da área autenticada para `pages/`, seguindo `docs/architecture.md`. Manter uma única fonte de sessão; adicionar lógica profissional em `features/veterinarians/` sem duplicar token, identidade ou clientes HTTP. Preservar a limpeza por gerações já existente em `State`.

Menu tutor: Início, Vacinas, Medicamentos, Doenças, Consultas; rodapé com Novo pet/Mudar pet e saída acessível. Usar estado de seção e expansão, sem exigir novas rotas para placeholders. Em celular usar painel sobreposto recolhível; em desktop reservar espaço para o menu, com região principal flexível. Indicar seção ativa, nome do pet e nomes acessíveis mesmo recolhido. A área veterinária é uma apresentação autenticada própria com nome/perfil e saída, sem reutilizar dados de tutor.

Início reaproveita detalhes autorizados do pet; sem seleção mantém orientação e escolha explícita. As demais seções informam que o módulo ainda não está disponível, sem exibir falsa lista clínica vazia. Mudar pet abre a escolha existente e utiliza o fluxo de autorização atual.

Novo pet reutiliza o formulário em diálogo acessível, com foco inicial, Escape, retorno de foco e limpeza de mensagens/campos/arquivos ao cancelar ou encerrar sessão. Não tratar fechamento como cancelamento de requisição já enviada: durante envio impedir fechamento para não ocultar resultado incerto. Em erro manter modal; em sucesso fechar, atualizar a lista e revalidar o pet ativo sem selecionar automaticamente o recém-criado. Respostas de sessão anterior não alteram modal ou lista.

## Risks / Trade-offs

- [Dados legados ambíguos] → simular migração, relatar conflitos sem PII em logs compartilhados e interromper publicação até reconciliação explícita; não escolher proprietário/perfil automaticamente.
- [Validação local não comprova profissional] → remover afirmação de habilitação garantida; cadastro não concede acesso clínico.
- [Carga de catálogo separada] → testes usam fixtures mínimas, interface trata ausência; executar a carga revisada antes de disponibilizar cadastro que dependa de espécies ausentes.
- [Modal e respostas concorrentes] → testar atraso, logout, cadastro e seleção simultâneos, sem alterar isolamento já entregue.

## Migration Plan

1. Inventariar tutor/veterinário, e-mails normalizados, CRMVs, hashes, clínicas e especialidades; preservar backup privado e hashes/contagens dos registros. Simular em cópia de teste. Não imprimir dados pessoais em evidências públicas.
2. Parar temporariamente escritas de cadastro durante backfill; resolver conflitos encontrados com o responsável pelos dados. Criar estruturas aditivas, índices e reservas para contas existentes, sem alterar IDs ou pets. Verificar completude antes de reabrir escrita por endpoints que usam a reserva.
3. Migrar campos profissionais e relações, mantendo originais durante transição; validar UF/CRMV existentes antes do índice único. Publicar APIs e testar contratos antigos e novos; publicar frontend só após esses contratos funcionarem.
4. Executar percurso tutor/veterinário e testes negativos reais, incluindo IDs iguais, concorrência e sessão antiga. Registrar evidências em `verification.md`.
5. Em rollback, retornar frontend e APIs a versões compatíveis com reserva de e-mail ou manter cadastros suspensos; não reativar caminho legado que viole unicidade. Manter estruturas e dados novos até reconciliação; não truncar tabelas, excluir contas ou perder vínculos.
