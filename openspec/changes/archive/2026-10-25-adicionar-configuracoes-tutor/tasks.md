# Tasks

## 1. Contratos da conta no backend

- [x] 1.1 Implementar `GET tutor/account` com autenticação de tutor, identidade derivada do token, campos permitidos e CPF mascarado no servidor; verificar XanoScript e testes diretos com dois tutores, ausência/token inválido, token de user/veterinário e tentativa de escolher outra conta.
- [x] 1.2 Implementar `PATCH tutor/account` com allowlist de nome/telefone/endereço, validação antes da escrita e resposta segura; verificar persistência, rejeição de obrigatórios vazios e preservação de CPF/e-mail/senha/vínculos e dados de outro tutor em requisições forjadas.
- [x] 1.3 Implementar `POST tutor/password` conferindo senha atual, nova senha não vazia e confirmação exata, sem trim nem nova política de complexidade; verificar com fixture senha incorreta, divergência, troca válida, login com nova senha e rejeição da anterior, sem expor hash ou credenciais.
- [x] 1.4 Documentar contratos, identidade, erros e verificação de conta em `docs/backend-foundation.md` e roteiro de integração apropriado; conferir publicação em desenvolvimento contra inventário, registrar evidências sanitizadas e preservar todos os registros preexistentes e endpoints legados.

## 2. Integração de estado e edição da conta

- [x] 2.1 Acrescentar classificação/status de erro ao cliente Xano e mensagens seguras de conta/senha sem quebrar chamadas existentes; testar token inválido versus senha atual incorreta, 429, timeout e corpo sensível, sem repetição automática de escrita.
- [x] 2.2 Criar estado específico de configurações usando a sessão privada existente e limpeza coordenada no logout; testar guarda sem sessão, carregamento somente ao abrir configurações, falha recuperável e descarte de resposta tardia após logout ou troca de identidade.
- [x] 2.3 Implementar snapshot, rascunho e edição de nome/telefone/endereço com Salvar e Cancelar; testar comparação de alterações, restauração, sucesso somente após API, erro preservando campos e bloqueio de envios duplicados com feedback anterior à requisição.
- [x] 2.4 Integrar troca de senha, mostrar/ocultar por campo e limpeza ao sair da seção; testar validação, senha atual rejeitada sem logout, troca confirmada limpando sessão e dados e redirecionando a `/login` com confirmação, além de falha de rede sem retry.
- [x] 2.5 Documentar estado, proteção de dados, política atual de senha e limite da saída local em `docs/backend-foundation.md`; conferir que não há persistência local de dados pessoais, senha ou token e que a documentação não promete revogação global.

## 3. Tela e navegação

- [x] 3.1 Criar `/configuracoes` e habilitar seu item na sidebar compartilhada, preservando Meus Pets e áreas futuras; testar navegação nos dois sentidos, item ativo, acesso direto sem sessão e logout, e atualizar o teste de rotas existentes.
- [x] 3.2 Construir Minha conta, Segurança e Preferências com os estados integrados e a tartaruguinha existente, seguindo os dois protótipos; preservar cópias das referências nas evidências e conferir rótulos, cadeados, CPF mascarado, botões, abas por teclado e ausência de quadros flutuantes ou sobreposição.
- [x] 3.3 Implementar confirmação de descarte para abas, navegação interna e Sair, incluindo restauração de foco e aviso nativo para recarga/fechamento quando disponível; testar Continuar editando, Descartar alterações e execução da intenção original, sem confirmar formulário limpo.
- [x] 3.4 Documentar rota, organização dos módulos e limitações do aviso de saída na documentação apropriada; verificar a tela em 1366 e 390 px com sidebar expandida/recolhida e gaveta móvel, sem rolagem horizontal ou controles encobertos.

## 4. Preferências e tema escuro

- [x] 4.1 Integrar o controle Manter o menu lateral expandido à preferência existente; testar sincronização com o botão da sidebar, entre páginas e abas, persistência no navegador e independência da gaveta móvel fechada por padrão.
- [x] 4.2 Implementar preferência local claro/escuro com aplicação imediata e bootstrap antes de qualquer tela visível; testar ausência/valor inválido, persistência, sincronização entre abas, armazenamento indisponível e reentrada sem flash do tema oposto.
- [x] 4.3 Aplicar tokens escuros a Configurações, Meus Pets, login, cadastro, cor da sidebar, campos, seletores, diálogos, mensagens e estados; verificar legibilidade, contraste e foco com componentes abertos nos dois temas e verificar que login/cadastro também ficam escuros após logout.
- [x] 4.4 Documentar chaves locais, padrões, escopo visual e comportamento de fallback; conferir que os controles não fazem chamadas ao Xano nem armazenam dados de conta e registrar capturas claras/escuras em 1366, 1920, 768 e 390 px.

## 5. Verificação integrada da entrega

- [x] 5.1 Executar testes unitários, `reflex compile --dry` e validação OpenSpec estrita; registrar comandos e resultados em `verification.md`, incluindo regressões do login, cadastro de tutor, cadastro/listagem de pets e navegação existente.
- [x] 5.2 Executar o percurso real em navegador com fixture de desenvolvimento: entrar, abrir configurações, editar/cancelar/salvar, testar descarte, alternar preferências, trocar senha e entrar novamente; verificar isolamento com segundo tutor, ausência de dados antigos, APIs de acesso negado e registrar evidências sanitizadas sem alterar credenciais reais.

## 6. Refinamento visual após revisão do usuário

- [x] 6.1 Posicionar a mascote na linha das abas e compactar/centralizar Segurança; verificar desktop e celular sem overflow e sem grandes áreas vazias.
- [x] 6.2 Unificar o switch de navegação com o de tema, mantendo o estado compartilhado; verificar tamanho, cores, teclado e expansão real da sidebar.
- [x] 6.3 Compilar, validar OpenSpec e registrar capturas do refinamento em desktop/celular e nos dois temas.

## 7. Otimização da navegação

- [x] 7.1 Remover roundtrip de navegação limpa e manter descarte apenas para edições reais; medir troca e verificar guard nas abas sem campos pessoais.
- [x] 7.2 Carregar conta fora da fila de eventos, com cache curto da mesma sessão e descarte de resposta antiga; testar consulta, expiração, logout e falhas sem bloquear navegação.
- [x] 7.3 Verificar testes, compilação e navegação real, registrando medições e regressões de descarte.
