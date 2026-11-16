# Spec Delta

## Purpose

Confirmar a posse do e-mail cadastrado na alteração e recuperação de senha de tutores e veterinários, com desafios temporários e mensagens consistentes com o Vet Tech.

## ADDED Requirements

### Requirement: Recuperação de acesso pelo login atende os dois perfis
O sistema SHALL tornar “Esqueceu a senha?” uma ação acessível no login, permitindo informar e-mail, receber e validar código, e cadastrar nova senha com confirmação sem senha atual. SHALL resolver a identidade única no backend, normalizando o e-mail conforme o cadastro, sem aceitar perfil ou ID como autorização. Recuperação SHALL NOT emitir sessão de acesso ao aplicativo; após concluir, SHALL orientar novo login. O login normal SHALL continuar apenas com e-mail e senha.

#### Scenario: Recuperação válida
- **GIVEN** uma conta de tutor ou veterinário com acesso ao e-mail cadastrado
- **WHEN** a pessoa valida seu código de recuperação e confirma nova senha consistente
- **THEN** somente essa conta tem sua senha atualizada, sem receber sessão automática
- **AND** pode entrar com a nova senha, sem código adicional no login

#### Scenario: E-mail desconhecido ou identidade ambígua
- **GIVEN** um e-mail inexistente ou conflitante entre perfis
- **WHEN** solicita recuperação
- **THEN** recebe a mesma mensagem genérica e o mesmo formato de resposta de uma solicitação válida, sem indicação de perfil, existência ou destinatário real
- **AND** nenhuma credencial é modificada e nenhuma conta ambígua recebe código

### Requirement: Desafios têm escopo restrito e uso único
O backend SHALL gerar códigos imprevisíveis de seis dígitos, válidos por dez minutos, vinculados ao desafio, conta e finalidade alteração ou recuperação. SHALL aceitar no máximo cinco tentativas incorretas por desafio, impor intervalo mínimo de sessenta segundos entre envios e máximo de cinco envios por conta/finalidade por hora, além de limite por origem na recuperação pública. Reenvio SHALL invalidar o código anterior sem zerar limites acumulados. Código, autorização de redefinição ou desafio SHALL NOT conceder acesso a endpoints clínicos ou outra conta. Verificação de uso único e escrita da nova senha SHALL ser protegidas contra concorrência.

#### Scenario: Código inválido ou expirado
- **WHEN** um código errado, expirado, consumido ou invalidado por reenvio é apresentado
- **THEN** a operação é rejeitada sem alteração de senha
- **AND** a interface permite nova solicitação conforme os limites do backend

#### Scenario: Limites e concorrência
- **GIVEN** tentativas ou reenvios concorrentes
- **WHEN** atingem os limites ou duas confirmações disputam o mesmo desafio
- **THEN** os limites continuam aplicados e no máximo uma alteração é aceita

#### Scenario: Troca de conta ou finalidade
- **GIVEN** um código ou autorização de recuperação emitido para uma conta
- **WHEN** é usado para outra identidade, perfil, finalidade ou acesso ao prontuário
- **THEN** o backend rejeita sem revelar nem modificar dados

### Requirement: Interface limpa segredos e comunica falhas com segurança
O sistema SHALL oferecer verificar, reenviar e cancelar com indicação de processamento, impedir submissão duplicada e permitir colar o código completo. SHALL preservar caracteres das senhas e a política vigente do perfil, sem armazenamento persistente de senha, código ou autorização de recuperação no navegador. Sair do fluxo, trocar identidade ou concluir SHALL limpar segredos e invalidar respostas atrasadas na interface. Falhas de rede ou de envio SHALL NOT confirmar alteração de senha ou provocar reenvio automático. Falhas públicas SHALL NOT revelar a existência da conta.

#### Scenario: Cancelamento com resposta pendente
- **WHEN** a pessoa cancela ou troca de fluxo antes da resposta
- **THEN** os dados sensíveis são limpos e a resposta não restaura o formulário anterior

#### Scenario: Entrega indisponível
- **WHEN** o envio falha ou fica com resultado incerto
- **THEN** a senha permanece igual, o código não aparece na interface e uma nova tentativa depende de ação explícita dentro dos limites

### Requirement: E-mail possui identidade visual e conteúdo acessível
O sistema SHALL enviar template HTML compartilhado em português brasileiro, com marca Vet Tech, verde institucional, título específico de alteração ou recuperação, código destacado como texto selecionável, prazo de validade e aviso para ignorar solicitação desconhecida. SHALL oferecer equivalente textual, leitura em celular e conteúdo essencial compreensível com imagens bloqueadas. Senhas, tokens de sessão e dados clínicos SHALL NOT constar do e-mail. A entrega SHALL incluir prévia local com dados fictícios e instruções para editar marca, cores e textos. A mensagem SHALL apresentar o cabeçalho ilustrado solicitado, referenciado por URL HTTPS no HTML, sem enviar anexos e sem exigir hospedagem pública do aplicativo. Marca alternativa e conteúdo essencial SHALL permanecer legíveis com imagens bloqueadas.

#### Scenario: Mensagem de cada finalidade
- **WHEN** um código de alteração ou recuperação é enviado
- **THEN** o assunto e o título identificam a finalidade e o código e a validade correspondem ao desafio emitido

#### Scenario: Imagens bloqueadas e celular
- **WHEN** o destinatário abre a mensagem em celular ou sem carregar imagens
- **THEN** consegue identificar o Vet Tech, ler e copiar o código e entender sua validade

### Requirement: Dados e eventos de segurança têm exposição limitada
O backend SHALL armazenar apenas representação protegida do código, metadados necessários de expiração, consumo e limites e eventos sanitizados de solicitação, rejeição e conclusão. SHALL NOT retornar código, hash, senha ou autorização sensível em respostas genéricas ou registrá-los em logs de aplicação e auditoria. Desafios e metadados temporários SHALL ser eliminados conforme retenção documentada, preservando somente eventos de segurança necessários. No modo local gratuito, a remoção física SHALL ocorrer na inicialização do backend Reflex e em ciclos de uma hora enquanto estiver ativo; durante pausas, a expiração SHALL continuar sendo imposta pelo Xano. O fluxo SHALL NOT alterar permissões de acesso aos pets ou enviar lembretes clínicos.

#### Scenario: Auditoria de uma redefinição
- **GIVEN** uma redefinição concluída ou rejeitada
- **WHEN** o evento de segurança é registrado
- **THEN** contém momento, finalidade e resultado sem credenciais, código ou dados clínicos

### Requirement: Campos de senha oferecem visibilidade controlada
O sistema SHALL oferecer botão acessível de mostrar/ocultar em cada campo de senha do login, cadastro, recuperação e Configurações dos dois perfis. A alternância SHALL preservar o valor digitado, atuar somente no campo associado e não submeter o formulário. Resetar o formulário ou ocultar a página SHALL restaurar o mascaramento, sem persistir credenciais ou visibilidade. A recuperação SHALL apresentar o nome Vet Tech Team acima da mascote em V e antes do título do formulário.

#### Scenario: Alternar senha pelo teclado
- **GIVEN** um campo de senha preenchido
- **WHEN** a pessoa ativa o botão Mostrar senha pelo teclado e depois Ocultar senha
- **THEN** somente esse campo alterna visibilidade, preserva os caracteres e comunica seu estado por rótulo e aria-pressed
- **AND** o formulário não é enviado automaticamente

#### Scenario: Voltar na solicitação inicial
- **GIVEN** a etapa inicial de recuperação por e-mail está aberta
- **WHEN** a pessoa aciona Voltar
- **THEN** o sistema retorna ao login e limpa o estado temporário
- **AND** uma resposta pendente não reabre o fluxo cancelado

### Requirement: Entrega transacional pelo Brevo sem publicação do aplicativo
O backend SHALL usar a API transacional Brevo e a variável privada Xano `BREVOS_API`, com remetente verificado e destinatário derivado da identidade. SHALL enviar os corpos HTML e textual do template canônico sem anexos, preservando o aplicativo local e sem contratar serviços pagos. SHALL considerar aceitação somente resposta 2xx com `messageId` não vazio; falhas SHALL permanecer genéricas, sem revelar código/chave e sem retry automático ou fallback para Resend.

#### Scenario: Provedor aceita o envio
- **WHEN** o Brevo responde 2xx com identificador não vazio
- **THEN** a função interna confirma somente aceitação, sem afirmar chegada à caixa

#### Scenario: Chave, IP ou remetente recusado
- **WHEN** o Brevo recusa a solicitação ou não confirma sua aceitação
- **THEN** o desafio não autoriza troca de senha e o sistema preserva a falha segura sem repetir envio automaticamente
