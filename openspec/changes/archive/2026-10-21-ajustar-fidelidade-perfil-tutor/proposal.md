# Proposal

## Why

A tela atual do perfil diverge do protótipo aprovado em hierarquia, espaçamento, identificação dos campos, upload, proporção da navegação e posicionamento do mascote. Corrigir essas inconsistências é necessário para que a interface permaneça legível e equilibrada também quando a sidebar reduz a largura disponível.

## What Changes

- Uniformizar o formulário em uma grade responsiva, com espaçamento único, controles de altura consistente e rótulos visíveis para todos os campos.
- Ajustar o upload para a dimensão e aparência do protótipo, preservando seleção, preview e envio de foto.
- Posicionar a pose correta do mascote sob o cartão de pets, respeitando sua transparência e sem sobreposição.
- Calibrar dimensões, espaçamento e estados aberto/recolhido da sidebar, além dos cartões e da lista de pets.
- Consolidar estilos de controles Reflex/Radix nos tokens existentes e adaptar a quebra de layout à largura realmente disponível depois da sidebar.
- Preservar rota, textos e nomes de campos, autenticação, contrato Xano e eventos de cadastro, listagem, atualização e logout.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `tutor-profile-presentation`: ajustar requisitos de apresentação visual do formulário, upload, lista de pets, mascote e responsividade, preservando os fluxos existentes.
- `application-navigation`: calibrar a apresentação da sidebar compartilhada e assegurar que o conteúdo se adapte à largura restante nos estados aberto e recolhido.

## Impact

- Interface existente em `vet_tech/components/pets.py`, `vet_tech/components/sidebar.py`, `assets/vet_tech.css` e configuração de estilos Reflex em `vet_tech/vet_tech.py`.
- Nenhuma nova rota, dependência, alteração de API ou mudança no contrato Xano.
- O perfil continuará exibindo os mesmos dados de tutor e pets apenas no fluxo já autenticado; não haverá ampliação de acesso, mudança de autorização ou nova operação de leitura/escrita. Auditoria e notificações permanecem inalteradas.
