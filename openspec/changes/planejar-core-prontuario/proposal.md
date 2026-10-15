# Proposta

## Why

O VetTech já permite cadastrar tutores, autenticar e cadastrar/listar pets,
mas ainda não entrega o prontuário compartilhado entre tutor e veterinário.
Esta change registra o planejamento do núcleo solicitado, com entregas menores
ordenadas por dependência e critérios verificáveis, sem estabelecer datas.

## What Changes

- Planejar seleção e alternância do pet, identidade veterinária, permissões e auditoria.
- Reutilizar as páginas existentes de cadastro e login para os dois perfis; após validar as credenciais, o backend identifica tutor ou veterinário e a aplicação abre a área correspondente.
- Planejar registro de consulta e consulta do prontuário por pet pelos perfis autorizados.
- Organizar a área inicial do tutor em menu lateral retrátil com Início, Vacinas, Medicamentos, Doenças e Consultas, sempre no contexto do pet selecionado.
- Em Consultas, apresentar os atendimentos e os prontuários anexados/vinculados individualmente a cada consulta.
- Colocar Novo pet e Mudar pet na parte inferior do menu; Novo pet abre o formulário existente em um pop-up/modal, em vez de mantê-lo na página principal.
- Incluir doenças, medicamentos, vacinas previstas/aplicadas e exames como complementos opcionais de uma consulta.
- Incluir agendamento com profissionais aptos a atender a espécie do pet selecionado e especialidade pertinente.
- Separar as futuras changes, seu conteúdo, dependências e critérios de conclusão em `roadmap.md`.
- Registrar decisões ainda necessárias, especialmente agenda, especialidades e arquivos de exames.

## Capabilities

### New Capabilities

Nenhuma implementada ou incorporada às specs principais nesta change documental.
As capacidades futuras estão mapeadas em `roadmap.md`; cada change de execução
criará sua própria proposta, design, delta specs e tarefas antes de implementar.
Esta change declara `skip_specs: true` porque entrega somente planejamento.

### Modified Capabilities

Nenhuma nesta etapa documental. Nas changes de execução, a seleção de pet
evoluirá `pet-management`, e o acesso compartilhado revisará os contratos de
cadastro/login existentes sem duplicar suas telas.

## Impact

- Agora: somente artefatos OpenSpec de planejamento; nenhuma API ou dado alterado.
- Futuro: Reflex/Python, backend e banco Xano, DER e documentação de domínio,
  mantendo a organização de `docs/architecture.md`.
- Dados de saúde e identidade exigem autorização no backend e auditoria;
  agendamento não concede automaticamente acesso ao prontuário.
- Fotos, upload, PDF, notificações automáticas e gestão completa de clínicas
  ficam fora desta entrega; datas previstas de vacina continuam consultáveis.
- A change antiga `assess-project-improvements` permanece intacta como referência
  de intenção; suas premissas sobre ausência de código e tabelas estão desatualizadas.
