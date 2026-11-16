# Proposal

## Why

O cadastro de tutor e de veterinário cria a conta, mas não envia agradecimento ou orientação inicial. O protótipo usa outra marca, texto em inglês e conteúdo genérico; o e-mail deve representar o Vet Tech e reconhecer corretamente o perfil criado.

## What Changes

- Enviar boas-vindas pelo Brevo após confirmação de um novo cadastro no Xano, tanto pelos formulários quanto por chamadas diretas aos endpoints de cadastro.
- Personalizar saudação pelo nome e próximos passos conforme a identidade persistida: pets e acompanhamento para tutores; agenda e atendimentos autorizados para veterinários.
- Criar HTML e alternativa textual próprios, reutilizando marca, paleta, desenvolvedores e copyright do e-mail existente, com `assets/mascote/clinicturtle.jpeg` no corpo por URL HTTPS, sem anexo.
- Substituir PetSync, título em inglês, cabeçalhos simulados e promessas genéricas por conteúdo real em português; manter o app em localhost e incluir botão com URL local temporária expressamente autorizada pelo usuário.
- Isolar falha de envio do sucesso do cadastro, limitar a tentativa por conta criada e não enviar em login, recuperação de senha, cadastro rejeitado ou para contas antigas em massa.
- Disponibilizar prévias locais dos dois perfis e documentação de configuração e verificação, sem contratar domínio, plano ou hospedagem do aplicativo.

## Capabilities

### New Capabilities

- `registration-welcome-email`: agradecimento transacional por perfil após novo cadastro, com template acessível e controle de envio no backend.

### Modified Capabilities

Nenhuma alteração nas regras de cadastro, autenticação, senha ou autorização clínica existentes; o novo comportamento de notificação fica na capacidade acima.

## Impact

- Xano: `auth/tutor_signup_POST.xs` e `veterinario/signup_POST.xs`, novas funções/tabelas internas para evento e tentativa de boas-vindas, DER atualizado. O perfil e o destinatário vêm da conta criada no backend.
- Templates e ferramentas: novo conjunto canônico em `xano/templates/`, renderizador, prévia, sincronização e testes; reutilizar URLs já públicas dos desenvolvedores.
- Infraestrutura existente: Brevo com `BREVOS_API` e remetente verificado; publicar somente a imagem clínica necessária em HTTPS, sem publicar o app nem embutir credenciais.
- Dados pessoais: nome/e-mail apenas para esta notificação; não transmitir CPF, CRMV, contatos adicionais, senha, tokens ou dados clínicos. Mensagem não concede acesso ao prontuário.
- O envio é consequência do cadastro já concluído e não pode desfazer a conta, mudar `{success:true}` ou criar notificações duplicadas em retry.
