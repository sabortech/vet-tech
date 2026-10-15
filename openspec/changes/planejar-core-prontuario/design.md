# Design

## Context

Ver `proposal.md` para o objetivo e `roadmap.md` para a divisão das entregas.
A exploração confirmou frontend funcional de tutor e pets, mas não identificou
APIs ou telas de prontuário, autorização veterinária ou agenda no repositório.
As tabelas clínicas existentes ainda não representam todas as regras do DER.

## Goals / Non-Goals

**Goals:** entregar um ciclo de atendimento consultável por pet, consentido
pelo tutor, com complementos clínicos opcionais, alternância de pets e agenda.

**Non-Goals:** implementar nesta change, substituir a stack, desenvolver gestão
completa de clínicas, pagamentos, PDF, notificações, OAuth ou upload.

## Decisions

### Prontuário é o histórico do pet

Não criar um documento independente que precise ser copiado para o tutor.
Cada consulta pertence obrigatoriamente a um pet e ao veterinário autenticado;
o prontuário reúne suas consultas e registros clínicos vinculados. O tutor
visualiza o mesmo histórico persistido, sem depender de qual veterinário o criou.
Não incluir exclusão de histórico nesta entrega.

### Complementos opcionais, vínculos consistentes

Uma consulta pode ser concluída sem doença, medicamento, vacina ou exame.
Quando um complemento existir, seus dados mínimos e vínculos serão validados
no backend. Todo item pertence a um pet; se vinculado a uma consulta, ambos
devem apontar para o mesmo pet. Relação de medicamento com doença pode ser
opcional, permitindo uso preventivo. Medicamento registra prescrição/tratamento,
não garante cura nem atualiza automaticamente o estado de uma doença.

### Planejado não equivale a realizado

Vacina prevista e vacina aplicada precisam ser distinguíveis, sem inventar data
de aplicação ou lote. Exame solicitado pode não ter resultado; exame concluído
tem seu resultado e data próprios. Agendamento é intenção de atendimento e
não deve criar consulta clínica vazia. As futuras deltas definirão os estados,
campos e transições antes da implementação.

### Identidade e autorização antes do prontuário

Autenticar com `tutor` e `veterinario`, sem reutilizar a tabela genérica `user`.
Autorizações são individuais por pet e veterinário, concedidas apenas pelo dono.
Cada leitura ou escrita verifica novamente identidade, pet e autorização ativa.
Revogação impede novas operações mesmo com token ou tela ainda abertos.
Auditoria deve existir desde o primeiro endpoint clínico; logs não podem ser
alterados pelo usuário. Consulta do log pelo tutor integra o controle de acesso.
Concluir operação clínica sem conseguir registrar sua auditoria não é sucesso.

### Cadastro e login compartilhados entre perfis

Decisão confirmada pelo usuário e sua equipe: reutilizar `/cadastro` e `/login`
para tutor e veterinário, preservando a identidade visual. O cadastro adapta
os campos ao perfil a cadastrar: dados de tutor ou dados profissionais,
incluindo CRMV e especialidades. Não criar páginas de entrada independentes.

No login, a pessoa informa suas credenciais na mesma tela; o backend valida
as credenciais e identifica o perfil da conta. A resposta e a sessão devem
conter identidade e perfil verificáveis no servidor. A interface direciona
à área de tutor ou veterinário, mas não decide permissões a partir de um
seletor, parâmetro ou estado manipulável pelo cliente.

Manter as identidades nas entidades de domínio `tutor` e `veterinario`, sem
introduzir a tabela genérica `user` apenas para unificar a interface. A futura
change `unificar-acesso-perfis` definirá a resolução de credenciais, emissão
de token e identificação do perfil compatíveis com o Xano. IDs iguais nas
duas tabelas não podem ser confundidos. A política para e-mail presente nos
dois perfis precisa ser decidida antes dessa implementação; não escolher o
primeiro perfil encontrado nem conceder privilégios pela ordem das consultas.

Reutilização das páginas não significa que o tutor poderá executar operações
clínicas do veterinário. Logout ou mudança de identidade limpa perfil, pet
selecionado e dados anteriores. Verificar o encaminhamento correto de ambos
os perfis e a rejeição de tentativas de forjar o perfil em chamadas à API.

### Pet selecionado é contexto de navegação

Selecionar um pet no perfil do tutor, não fazer login do animal. Trocar o pet
limpa histórico, formulários, agenda e permissões carregados para o anterior;
respostas atrasadas não podem preencher o pet atual. IDs enviados pela tela
são sempre revalidados no backend. Logout e troca de identidade limpam contexto.

### Especialidade e espécie são conceitos diferentes

O campo textual `veterinario.especialidade` não comprova quais espécies atende.
A change de identidade veterinária precisa modelar essa aptidão e as
especialidades usadas na busca. O tutor agenda para o pet selecionado com um
profissional compatível; reservar horário não concede acesso aos dados clínicos.

### Entregas por capacidade, não por camada

Cada change menor inclui sua API, validação, interface necessária, testes e
documentação. Não deixar todo frontend ou toda segurança para o final.
Aplicar gradualmente `features/pets`, `features/veterinarians`, `features/access`,
`features/records` e `features/appointments`, seguindo `docs/architecture.md`;
não criar pastas vazias antecipadamente. Backend oficial permanece em `xano/`.

## Risks / Trade-offs

- [Modelo divergente] → `cmv` sem unicidade, veterinário não autenticável,
  `doenca.pet_id` divergente do catálogo do DER, associativas ausentes,
  medicamento sem frequência/consulta/doença e log com data sem hora exigem
  avaliação de dados e correção na change responsável; atualizar DER e Xano juntos.
- [Plano atual impede upload relatado pelo usuário] → Exames precisam de decisão
  explícita sobre solicitação sem arquivo e arquivo externo antes de implementação;
  não remover silenciosamente o requisito de anexo do domínio.
- [Escopo ampliado] → As prioridades ordenam a entrega, não eliminam itens aceitos.
  As etapas 1–4 formam o primeiro fluxo utilizável; as etapas 5–9 completam este núcleo.
- [Agenda não existe] → Tratar disponibilidade e conflito como trabalho próprio,
  sem prometer reserva confirmada a partir de um simples cadastro de consulta.

## Migration Plan

Esta change não migra dados. Cada change de execução deve verificar registros
existentes, definir migração e rollback antes de alterar tabelas ou publicar.
Histórico e autoria existentes serão preservados; não usar push com truncamento
ou exclusão de registros como estratégia de implantação.

## Open Questions

Decisões que bloqueiam somente as futuras changes correspondentes, não este
mapa de trabalho:

1. Antes de `unificar-acesso-perfis`: confirmar vínculo com clínica obrigatório
   ou opcional, critérios de CRMV, especialidade e espécies atendidas e a
   política para uma pessoa/e-mail com ambos os perfis. O compartilhamento
   das páginas e a identificação do perfil no backend já estão aprovados.
2. Antes de `solicitar-exames-pet`: confirmar solicitação inicialmente sem anexo
   e política para resultado/arquivo externo; reconciliar conflito documental.
3. Antes de `agendar-consulta-pet`: escolher reserva de horário disponível ou
   solicitação com confirmação do veterinário; definir duração, disponibilidade,
   cancelamento e fuso. Não implementar agenda antes dessa decisão.
