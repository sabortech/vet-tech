# Proposal

## Why

A clínica já visualiza seus veterinários, mas não consegue cadastrá-los nem vincular profissionais existentes sem intervenção externa.

## What Changes

- Oferecer botões separados para cadastrar uma conta veterinária e vincular uma conta existente.
- Restringir o vínculo a profissionais sem clínica, com validação no backend e atualização segura diante de concorrência.
- Atualizar a lista da clínica após o sucesso e apresentar erros e validações.

## Capabilities

### New Capabilities

- `clinic-veterinarian-management`: cadastro e vínculo de veterinários pela clínica autenticada.

### Modified Capabilities

Nenhuma.

## Impact

Afeta área administrativa Reflex, identidade e APIs Xano. A operação não concede acesso a prontuários nem altera as autorizações do tutor. O cadastro aproveita o fluxo de boas-vindas existente; a política de comunicação do vínculo deve ser definida no desenho. A implantação exige publicação dos artefatos Xano.
