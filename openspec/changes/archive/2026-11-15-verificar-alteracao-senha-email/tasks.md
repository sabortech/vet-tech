# Tasks

## 1. Persistência e proteção dos desafios

- [x] 1.1 Adicionar desafios, contadores e eventos de segurança em XanoScript e atualizar o DER; verificar consistência entre tabelas, índices, relações de identidade e documentação do modelo.
- [ ] 1.2 Implementar geração criptográfica, hash protegido, expiração, consumo atômico e invalidação por mudança de credencial; comprovar no backend de desenvolvimento rejeição por expiração, replay, conta/finalidade diferentes e confirmações concorrentes.
- [ ] 1.3 Implementar limites persistentes de emissão, tentativas e origem, reenvio com invalidação e limpeza por retenção acionada pelo backend Reflex local; testar limites inclusive sob concorrência e documentar valores e origem confiável.
- [ ] 1.4 Configurar sanitização do histórico de requests e logs de aplicação e eventos; verificar que senha, código, autorização restrita e token não aparecem em logs nem respostas genéricas e documentar retenção.

## 2. Template e entrega de e-mail

- [x] 2.1 Criar HTML canônico e versão textual com marca, cores, títulos por finalidade, código e validade dinâmicos; verificar renderização e escape das variáveis nas duas variantes, inclusive código com zero inicial.
- [x] 2.2 Criar função compartilhada de renderização/envio Xano e sincronização com o template canônico; verificar que a prévia e o conteúdo enviado usam a mesma fonte e que a API nunca retorna o código.
- [x] 2.3 Entregar prévias locais fictícias em desktop/celular e guia de personalização de marca, cores, textos e sincronização; verificar leitura com imagens bloqueadas e instruções executáveis de geração.
- [ ] 2.4 Validar destinatário, remetente permitido para teste e envio HTML/texto via Brevo pelo Xano; comprovar entrega em caixa de teste explicitamente configurada e falha segura sem retries automáticos, registrando dependências de ambiente sem segredos.

- [x] 2.5 Reproduzir a referência visual com cabeçalho ilustrado, fundo verde-água e código tracejado; usar a imagem por URL HTTPS sem anexos, mantendo o aplicativo local, verificar paridade, ambas as finalidades e prévias em desktop/celular com imagens bloqueadas.

- [x] 2.6 Inserir a imagem de pets fornecida pelo usuário abaixo da linha divisória e acima de “Não foi você?”, usando URL HTTPS sem anexo; verificar as duas finalidades em celular/desktop e publicar o renderizador.

- [x] 2.7 Incluir “O melhor sistema para seu melhor amigo!” centralizado acima da imagem de pets; verificar ambas as finalidades no celular/desktop e publicar o renderizador.

- [x] 2.8 Centralizar “SEGURANÇA DA SUA CONTA” e o título principal nas duas finalidades; conferir celular/desktop e publicar o renderizador.

- [x] 2.9 Adicionar seção de desenvolvedores abaixo da imagem de pets, com título centralizado e três fotos arredondadas em linha, nomes abaixo, prévia responsiva e publicação após autorização específica para hospedar as fotos pessoais.

- [x] 2.10 Destacar as três fotos com sombra verde e moldura de fallback compatível com Gmail, centralizar o aviso final e adicionar “© by Vet Tech Team” no rodapé; verificar celular/desktop e publicar o renderizador.

- [x] 2.11 Remover sombra e moldura extra das fotos, corrigir para “Copyright © by Vet Tech Team” e aplicar fundo do oceano externo ao cartão; validar imagens, fallback, celular/desktop e publicar o renderizador.

- [x] 2.12 Alterar a caixa do código para verde-escuro e os dígitos para branco; conferir contraste e celular/desktop nas duas finalidades e publicar o renderizador.

- [x] 2.13 Uniformizar títulos, trechos em negrito e nomes com o verde-escuro da caixa do código, preservando seus dígitos brancos; verificar ambas as finalidades e publicar.

- [x] 2.14 Adicionar referência independente por envio em X-Entity-Ref-ID para evitar agrupamento no Gmail e reduzir rodapé oculto; validar sintaxe, publicar o remetente e enviar teste, sem prometer controle da interface do destinatário.

- [x] 2.15 Migrar o remetente compartilhado para Brevo com `BREVOS_API` somente no Xano, configurar remetente verificado, testar validação e aceitação, publicar seletivamente e verificar entrega na caixa autorizada; preservar template, falha genérica e ausência de retry automático.

## 3. Endpoints de alteração e recuperação

- [ ] 3.1 Implementar solicitação autenticada de código por perfil e atualizar endpoints de senha para exigir desafio/código e senha atual; testar diretamente ausência de código, senha errada, tokens cruzados, IDs coincidentes e sucesso isolado da conta autenticada.
- [ ] 3.2 Implementar solicitação pública de recuperação com resolução única de tutor/veterinário e resposta uniforme; testar contas existentes, e-mail desconhecido e ambíguo sem revelar existência/perfil, incluindo verificação de tempo de resposta e limites.
- [ ] 3.3 Implementar verificação do código e autorização opaca restrita de cinco minutos, seguida de conclusão atômica sem login automático; testar token expirado, reutilizado, de outra finalidade e sem permissão de acesso clínico.
- [ ] 3.4 Revisar rotas legadas de alteração/recuperação que alcancem tutor/veterinário e impedir bypass; documentar contratos, incompatibilidade com clientes antigos e separação dos endpoints Quick Start de user, verificando chamadas diretas.

## 4. Interface compartilhada de Segurança

- [x] 4.1 Adaptar formulário de Segurança para envio, entrada do código, reenvio e conclusão nos dois perfis; verificar senha atual obrigatória, nova confirmação consistente, estados de processamento e bloqueio de envio duplicado.
- [x] 4.2 Implementar limpeza de segredos e descarte de respostas antigas ao trocar aba, conta, cancelar ou sair; incluir testes relevantes em `tests/unit/test_settings_state.py` e `test_veterinarian_settings.py` com cenários de sessão substituída e falhas.
- [x] 4.3 Atualizar documentação de Configurações e verificar no navegador ambos os perfis, claro/escuro, teclado e largura de 390 px, sem interferir nos dados pessoais, preferências ou menu.

## 5. Recuperação pelo login

- [x] 5.1 Tornar “Esqueceu a senha?” acionável e implementar etapas e-mail, código e nova senha com voltar/cancelar; verificar recuperação para os dois perfis sem seletor de identidade ou solicitação de senha atual.
- [x] 5.2 Integrar estado temporário de recuperação e autorização restrita, limpando segredos e respostas atrasadas; testar falha, cancelamento, timeout, reenvio e mudança de fluxo em `tests/unit/test_auth_state.py`.
- [x] 5.3 Documentar a recuperação e seu limite quanto a sessões previamente emitidas; verificar no navegador acessibilidade, colagem do código, mensagens seguras e retorno ao login sem autenticação automática.

## 6. Integração e entrega coordenada

- [ ] 6.1 Executar testes de integração reais com contas sintéticas para alteração e recuperação de ambos os perfis; registrar evidências sanitizadas de código inválido/expirado/reutilizado, reenvio, limites, concorrência e login com senha nova e rejeição da anterior.
- [ ] 6.2 Confirmar ausência de envio de código no login normal e preservação de isolamento de perfis e acesso clínico; executar suíte relevante e compilação conforme `reflex-process-management`, registrando resultados na change.
- [x] 6.3 Validar a change com OpenSpec e registrar plano de publicação seletiva e rollback seguro; verificar que frontend/backend são compatíveis na entrega e que rollback desabilita os fluxos sem reabrir troca de senha desprotegida.

## 7. Marca e campos de senha na interface

- [x] 7.1 Exibir Vet Tech Team acima da mascote em V antes do título da recuperação; verificar desktop/celular.
- [x] 7.2 Reutilizar controle de mostrar/ocultar em todos os campos de senha do login, cadastro, recuperação e Configurações, com rótulos acessíveis, preservação de valor e reset da visibilidade; verificar comportamento no navegador, suíte relevante e compilação, e atualizar o servidor local.

- [x] 7.3 Corrigir Voltar na primeira etapa de recuperação para retornar ao login, preservando descarte de segredos e respostas antigas nas etapas seguintes; verificar testes e navegador e atualizar o servidor local.
