# Fundação do backend: estado e contrato

## Estrutura atual

`vet_tech/vet_tech.py` registra aplicação e páginas. `pages/` compõe as telas;
`components/` contém interface reutilizável. `features/auth/state.py` controla
sessão e fluxos de pets; `features/navigation/state.py` controla sidebar/drawer.
`shared/config.py` valida configuração e `shared/xano_client.py` concentra HTTP.
Separar o estado de pets futuramente deve seguir a evolução gradual de
`docs/architecture.md`, sem mover módulos apenas para reorganizar pastas.

O backend autoritativo é `xano/`. Tabelas clínicas não comprovam API funcional,
autorização ou auditoria. `assess-project-improvements` implementa artefatos locais de controles
transversais; `planejar-core-prontuario/roadmap.md` ordena as futuras entregas
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
| Raça → espécie | `raca.especie_id` obrigatório no artefato local; cadastro valida compatibilidade | Toda raça pertence a uma espécie existente |
| Consulta → pet e veterinário | Obrigatórios no artefato local; endpoint autenticado em `clinical_records/` | Ambos obrigatórios e existentes; autoria autenticada no backend |
| Exame → pet | Obrigatório no artefato local | Pet obrigatório e existente |
| Exame → consulta | Opcional | Continuar opcional; se presente, consulta deve pertencer ao mesmo pet |
| Identidade veterinária | `auth = true`, campo legado `cmv`, índices únicos de e-mail/CRMV | Login por perfil valida credenciais no backend; cadastro profissional na futura change |
| Log de acesso | Timestamp e vínculos obrigatórios no artefato local; legado requer reconciliação | Timestamp com hora, vínculos e ação obrigatórios; imutabilidade |

Os contratos possuem implementação XanoScript local em `xano/api/clinical_records/`
e funções reutilizáveis em `xano/function/records/`. Ainda exigem publicação e
integração em desenvolvimento. `event_log` genérico não substitui log clínico.
Contrato, política de identidade dupla e comandos em
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

Não foi executada migração ou publicação remota. A política de dois perfis foi
definida: mesmo e-mail permitido entre tabelas; cada senha de domínio precisa
ser comprovada e cada token é vinculado à tabela correta. A integração remota
continua necessária antes de considerar os controles operacionais.
