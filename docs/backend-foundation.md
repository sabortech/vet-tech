# Fundação do backend: estado e contrato

## Estrutura atual

`vet_tech/vet_tech.py` registra aplicação e páginas. `pages/` compõe as telas;
`components/` contém interface reutilizável. `features/auth/state.py` controla
sessão e fluxos de pets; `features/navigation/state.py` controla sidebar/drawer.
`shared/config.py` valida configuração e `shared/xano_client.py` concentra HTTP.
Separar o estado de pets futuramente deve seguir a evolução gradual de
`docs/architecture.md`, sem mover módulos apenas para reorganizar pastas.

O backend autoritativo é `xano/`. Tabelas clínicas não comprovam API funcional,
autorização ou auditoria. `assess-project-improvements` publica controles transversais no workspace
de desenvolvimento confirmado; `openspec/changes/archive/2026-10-25-planejar-core-prontuario/roadmap.md` ordena as futuras entregas
de identidade, acesso e prontuário, que devem reutilizar esses controles.

## Contratos encontrados

| Operação | Entrada relevante | Identidade e resposta |
|---|---|---|
| `POST Authentication/tutor/login` | E-mail, senha | Token da tabela `tutor`; login genérico de `user` não é identidade clínica |
| `POST Pet/pets` | `nome`, `especie_id`; raça, data ISO, metadados e foto opcionais | `auth = tutor`; `tutor_id` vem de `$auth.id`; retorna dados do pet |
| `GET Pet/pets` | Token de tutor | Lista filtrada pelo tutor autenticado; foto depende de URL acessível autorizada |
| Catálogos de espécie e raça | Token e espécie no filtro | Cadastro revalida compatibilidade da raça |

O cliente usa grupos `H62nB-j2` e `vettech-pets`. A origem vem somente de
`XANO_API_BASE_URL`; tokens são enviados em Authorization. Somente mensagens
conhecidas de domínio podem ser propagadas em erros, preservando feedback sem
revelar credenciais ou dados clínicos contidos em respostas arbitrárias.

## Divergências entre domínio e persistência

| Vínculo/regra | Estado no XanoScript | Contrato necessário |
|---|---|---|
| Pet → tutor | `pet.tutor_id` obrigatório; cadastro atribui `$auth.id` | Um único tutor existente; cliente não escolhe outro proprietário |
| Raça → espécie | `raca.especie_id` obrigatório no schema publicado; cadastro valida compatibilidade | Toda raça pertence a uma espécie existente |
| Consulta → pet e veterinário | Obrigatórios no schema publicado; endpoint autenticado em `clinical_records/` | Ambos obrigatórios e existentes; autoria autenticada no backend |
| Exame → pet | Obrigatório no schema publicado | Pet obrigatório e existente |
| Exame → consulta | Opcional | Continuar opcional; se presente, consulta deve pertencer ao mesmo pet |
| Identidade veterinária | `auth = true`, campo legado `cmv`, índices únicos de e-mail/CRMV | Login por perfil valida credenciais no backend; cadastro profissional na futura change |
| Log de acesso | Timestamp e vínculos obrigatórios no schema publicado; legado requer reconciliação | Timestamp com hora, vínculos e ação obrigatórios; imutabilidade |

Os contratos possuem implementação XanoScript local em `xano/api/clinical_records/`
e funções reutilizáveis em `xano/function/records/`, publicados em desenvolvimento.
A cobertura e os resultados de integração estão registrados na change. `event_log` genérico não substitui log clínico.
Contrato, política de identidade por domínio e comandos em
[`record-foundation-verification.md`](record-foundation-verification.md).

## Migração preservando histórico

1. Em desenvolvimento, inventariar nulos, órfãos, raças incompatíveis e vínculos
   clínicos inconsistentes. Guardar backup e contagens antes de mudar o schema.
2. Corrigir referências somente com evidência. Não inventar tutor, veterinário,
   consentimento ou horário histórico. Resolver ambiguidades antes da migração.
3. Validar endpoints antes de restringir campos, impedindo novos dados inválidos.
4. Tornar vínculos obrigatórios depois da reconciliação; manter consulta do exame
   opcional. Atualizar DER e XanoScript juntos.
5. Migrar horário de log somente com fonte confiável. Datas sem hora devem ter
   sua precisão histórica documentada; não inventar um instante exato.
6. Verificar contagens, autoria e histórico com fixtures em desenvolvimento.
   Rollback reverte endpoints/schema pelo backup sem truncar tabelas ou apagar logs.

A decisão de identidade foi reconciliada por autorização explícita do usuário:
o e-mail é único entre tutor e veterinário. O contrato remoto `acesso/login`
valida `reserva_email`, a senha e a tabela de domínio, retornando um único perfil
autenticado. Não publicar o contrato local alternativo `profiles/login`.
O workspace foi confirmado como desenvolvimento; a publicação e as verificações
são registradas na change antes de declarar os controles operacionais.

## Limite temporário de requisições no login

Se o Xano responder HTTP 429, o cliente informa que o serviço limitou
temporariamente as solicitações e orienta aguardar. Não classifica esse retorno
como senha inválida nem repete credenciais automaticamente. A limitação foi
observada no ambiente configurado; não foram alterados plano, cotas ou contas.
