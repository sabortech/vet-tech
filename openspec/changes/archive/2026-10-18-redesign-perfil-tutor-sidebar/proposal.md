# Proposta

## Por quê

A tela autenticada “Perfil do tutor” ainda usa uma apresentação simples e não oferece a navegação lateral verde prevista para o produto. A remodelação melhora a hierarquia e a responsividade sem criar outra rota nem alterar os fluxos existentes de autenticação, cadastro, listagem ou envio de pets.

## O que muda

- Remodelar a apresentação da tela de perfil já existente, com formulário e lista de pets em cartões responsivos, identidade visual consistente e dados de exibição formatados.
- Criar um componente reutilizável de navegação lateral, com estado compartilhado, comportamento de rail no desktop e drawer no mobile; itens sem tela implementada não navegam para rotas inexistentes.
- Acrescentar à resposta de listagem de pets o campo da foto já armazenada, para que o perfil possa mostrar o avatar ou usar a patinha como fallback.
- Preservar nomes de campos, textos de ações, rota atual do perfil, regras de autenticação e integração existente com o Xano.

## Capacidades

### Novas capacidades

- `application-navigation`: navegação lateral reutilizável, responsiva, acessível e segura para telas ainda não implementadas.
- `tutor-profile-presentation`: apresentação responsiva do perfil autenticado, incluindo formulário, lista e formato de exibição dos dados dos pets.

### Capacidades modificadas

- `pet-management`: incluir a foto já associada ao pet na resposta da listagem, mantendo os campos e operações existentes.

## Impacto

- Interface Reflex: `vet_tech/components/pets.py`, novo componente de navegação e estado compartilhado, estilos/tokens globais e composição da aplicação.
- Estado de pets: `vet_tech/features/auth/state.py` para preparar a foto e os valores de exibição sem alterar os dados enviados ao backend.
- Xano: `xano/api/application_data_persistence/pet/list_GET.xs`, adicionando o campo da imagem já existente ao retorno autenticado.
- Verificação: testes unitários para formatação e estado de navegação, além de validação responsiva nos tamanhos definidos.
- Não requer nova dependência, nova página ou nova rota. Os dados continuam limitados ao tutor autenticado pelo backend existente.
