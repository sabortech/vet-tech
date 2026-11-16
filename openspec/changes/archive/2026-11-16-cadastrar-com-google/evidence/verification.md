# Verificação e pendências

Implementação publicada seletivamente no Xano com backup sem ambiente. Validador oficial: 14/14 XanoScript válidos. Compilação Reflex concluída. Regressões Python: 93 testes passaram, incluindo 9 testes específicos de cadastro Google e falha na confirmação de sessão. Política de senha JS passou, incluindo primeira senha de conta Google após código verificado e uso único.

Xano: 10 testes OAuth nativos com mocks passaram, incluindo prova de cadastro sem sessão prematura. Teste real dos endpoints com fixtures `.invalid` para tutor e veterinário: dados incompletos rejeitados, concorrência com somente um cadastro, ausência real de senha, sessão confirmada por `/me`, login por senha aleatória negado. Fixtures e helper temporário removidos, sem envio para destinatários reais.

Layout Playwright: 390/1100 px, temas claro/escuro reais, 12 px entre todos os campos, sem rolagem horizontal, feedback CPF acessível. Evidências em layout.json e capturas locais.

Pendências preservadas: tarefas 1.2 e 5.1 dependem de confirmar audiência no console Google e percorrer OAuth real com contas novas autorizadas para cada perfil. Não foram criadas contas Google ou usados dados pessoais sem autorização. Passos manuais: escolher perfil, Cadastrar com Google, autorizar, completar dados obrigatórios sem senha, concluir e conferir área correta; sair e entrar novamente por Google. Para senha opcional, Configurações > Segurança > Definir uma senha e confirmar o código por e-mail. A entrega de boas-vindas real continua dependendo do provedor.

Arquivamento de todas as changes solicitado explicitamente pelo usuário; pendências não foram marcadas como concluídas.
