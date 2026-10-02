## Context

Ver `proposal.md` para motivação e `specs/pet-management/spec.md` para os requisitos funcionais. O modelo do domínio contém `tutor`, `pet`, `especie` e `raca`. Hoje `tutor` possui e-mail e senha, mas não está configurada como entidade autenticável; `pet.tutor_id`, `pet.especie_id` e `pet.nome` estão opcionais. A tabela `raca` aponta para uma espécie. Não há APIs de pets na área de persistência, e a página Reflex ainda é o exemplo inicial. A tabela genérica `user` está fora do domínio e não será usada.

## Goals / Non-Goals

**Goals:**
- Identificar de forma confiável o tutor autenticado sem usar uma tabela fora do modelo de domínio.
- Tornar seguro e consistente o cadastro e a listagem dos pets próprios do tutor.
- Manter a integração com Reflex funcional, sem decidir estrutura visual ou estilo das telas.

**Non-Goals:**
- Desenhar telas ou definir componentes visuais.
- Permitir edição ou exclusão de pets.
- Incluir histórico clínico, consultas, exames, vacinas, medicamentos, acesso veterinário ou notificações.
- Migrar identidades da tabela `user` ou depender dela para autorização.

## Decisions

### Usar `tutor` como origem da identidade autenticada

Configurar o fluxo de autenticação do Xano para identificar o tutor pelo registro da própria tabela `tutor`, reutilizando os dados de e-mail e senha do domínio e o tratamento seguro de senhas do Xano. Operações de pets recebem a identidade autenticada do backend. A tabela `user` e qualquer tabela que não esteja no modelo de domínio ficam fora do fluxo.

Alternativa considerada: autenticar pela tabela genérica `user` e manter uma associação paralela com `tutor`. Essa opção viola o limite de tabelas solicitado e duplica identidade fora do modelo de domínio.

### Derivar a propriedade no backend

No cadastro, definir `pet.tutor_id` a partir do tutor autenticado; não aceitar que o cliente escolha o proprietário. Na listagem, aplicar o filtro de `tutor_id` no backend usando a mesma identidade. Isso impede associação indevida e acesso cruzado mesmo que o cliente altere parâmetros.

Alternativa considerada: receber o identificador do tutor no formulário ou na query de listagem. Um identificador controlado pelo cliente não comprova propriedade.

### Validar os vínculos de espécie e raça antes de gravar

Exigir nome e espécie no cadastro. Confirmar que a espécie existe e, se a raça for informada, que ela pertence à espécie selecionada. Raça ausente permanece válida para SRD. Os demais atributos do pet são aceitos conforme o modelo de domínio; microchip e foto permanecem opcionais quando não informados.

Alternativa considerada: confiar apenas nas FKs para validar os dados. FKs garantem a existência dos registros referenciados, mas não garantem que a raça selecionada pertença à espécie selecionada.

### Carregar espécies e raças a partir do domínio

Criar consultas autenticadas somente de leitura para listar espécies e para listar raças filtradas pela espécie selecionada. O frontend usa esses resultados como opções do formulário; nomes e identificadores não ficam duplicados em código Reflex. O backend continua validando os vínculos no momento do cadastro, pois os catálogos não substituem a validação de integridade.

Alternativa considerada: manter uma lista de espécies/raças fixa no frontend ou pedir IDs numéricos. A lista fixa diverge da fonte de verdade, e IDs digitados não são uma interação funcional adequada para tutores.

### Separar operações de criação e listagem

Expor comportamentos de criação e listagem protegidos por autenticação, sem operação de atualização ou exclusão nesta etapa. A listagem pode retornar estado vazio quando o tutor ainda não possui pets. A interface Reflex apenas consumirá esses comportamentos e apresentará feedback funcional; decisões de layout ficam para uma proposta futura.

Alternativa considerada: criar uma operação genérica de manutenção de pets desde já. Isso ampliaria a superfície de autorização e contrariaria o recorte acordado.

## Risks / Trade-offs

- [A tabela `tutor` já contém dados e não está autenticável] -> Verificar duplicidades de e-mail e a compatibilidade das senhas existentes antes de ativar autenticação; testar login e criação de token em ambiente de desenvolvimento.
- [O projeto possui endpoints genéricos que usam `user`] -> Não reutilizá-los para autorização de pets; confirmar que os endpoints novos recebem identidade autenticada da tabela `tutor`.
- [Campos opcionais atuais podem divergir das regras do domínio] -> Tornar obrigatórios apenas nome, espécie e proprietário neste fluxo; tratar raça opcional e preservar os campos complementares do domínio.
- [Uma FK válida não garante a compatibilidade raça-espécie] -> Validar a relação no backend antes de persistir.
- [O modelo atual permite `tutor_id` ausente] -> Tornar o vínculo obrigatório para novos pets e verificar registros existentes antes de aplicar restrições ao conjunto de dados.

## Migration Plan

1. Verificar os registros existentes em `tutor` e `pet`, incluindo e-mails duplicados e pets sem tutor ou espécie.
2. Configurar a autenticação para usar `tutor` e validar credenciais sem expor senha ou hash.
3. Ajustar o modelo de `pet` para exigir proprietário, nome e espécie, preservando raça opcional.
4. Criar operações autenticadas de consulta de espécies/raças, cadastro e listagem de pets; validar raça-espécie e filtrar pets pela identidade do tutor no backend.
5. Integrar Reflex aos catálogos e às operações de pet e validar os cenários funcionais da spec sem fixar layout visual.

Rollback: desativar as operações de pets e restaurar a configuração anterior se houver falha de autenticação ou de propriedade. Não excluir registros de pets. Reverter restrições somente depois de avaliar os dados existentes e a compatibilidade das operações.