# Proposal

## Why

Clínicas precisam divulgar pets sob sua responsabilidade e consultar seus profissionais sem depender de alterações manuais no Xano. O modelo atual exige um tutor para cada pet e ainda não oferece identidade administrativa de clínica.

## What Changes

- Criar acesso autenticado de pessoal da clínica, provisionado pela equipe da plataforma, limitado à própria clínica.
- Exibir somente veterinários vinculados à clínica, sem gestão de vínculos nesta entrega.
- Permitir cadastrar novos pets para adoção, sob responsabilidade provisória da clínica que os cadastrou, e disponibilizá-los ou retirá-los da listagem.
- Apresentar pets disponíveis na área de adoção do tutor, acessível pela navegação junto ao painel existente.
- **BREAKING:** permitir que um pet tenha como responsável exatamente uma clínica ou um tutor; a adoção transfere a responsabilidade da clínica ao tutor, preservando histórico e revogando autorizações anteriores.
- Prever conta de teste solicitada por configuração segura, exclusivamente em ambiente isolado, sem persistir senha nos artefatos.

## Capabilities

### New Capabilities

- `clinic-access`: identidade administrativa de clínica e consulta de veterinários vinculados.
- `clinic-adoption-management`: cadastro e gestão de disponibilidade de pets sob responsabilidade provisória da clínica.

### Modified Capabilities

- `pet-adoption`: inclusão de pets sob responsabilidade de clínica e transferência ao tutor.
- `pet-management`: responsabilidade exclusiva de clínica ou tutor.

## Impact

Afeta identidade, banco e APIs Xano, navegação e estado Reflex, modelo de domínio e testes. O cadastro e a divulgação expõem dados do pet e resumo clínico estritamente permitido; a clínica não recebe acesso automático a prontuários existentes. Para pets já pertencentes a tutor, a autorização do tutor continua obrigatória e o fluxo existente permanece separado. Auditoria administrativa deve identificar ator, clínica, pet e ação, sem reutilizar falsamente o log clínico de veterinário. Não há notificações automáticas novas. Implantação e testes persistentes dependem de ambiente Xano isolado.
