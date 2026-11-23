# Veterinários da clínica

A área da clínica oferece cadastro de uma conta nova e solicitação de vínculo de uma conta existente. No cadastro a clínica informa uma senha provisória; o veterinário pode alterá-la em Configurações. A senha é enviada ao backend para criação e não deve ser registrada em logs, documentos ou mensagens de suporte.

O vínculo existente é solicitado pelo e-mail e fica pendente até o profissional entrar na própria conta e aceitá-lo. O convite aparece na área veterinária; esta versão não envia e-mail de convite. A aceitação revalida a ausência de clínica dentro de transação com trava por profissional. O administrador ativo e a clínica são validados no backend, que ignora identificadores de clínica enviados pelo cliente. As regras de acesso aos prontuários permanecem independentes.

Para disponibilizar a funcionalidade, publique em ambiente Xano isolado as tabelas `clinica_veterinario_convite` e `veterinario_vinculo_lock` e os endpoints `clinica/veterinarios` POST, `clinica/veterinarios/convites` POST, `veterinario/convites` GET e `veterinario/convites/aceitar` POST. As funções de identidade e boas-vindas existentes também precisam estar publicadas. Verifique cadastro, duplicidade, conta administrativa inativa, aceite por outro usuário, veterinário já vinculado e aceites concorrentes antes de publicar em produção. Testes locais não demonstram a validade ou o comportamento remoto do XanoScript.

Para rollback, retire os novos endpoints e reverta o frontend; preserve as tabelas de convites e vínculos existentes para investigação e não apague contas ou associações criadas.
