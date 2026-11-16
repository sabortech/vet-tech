# Design

## Context

Ver motivação em `proposal.md`. A tela `pages/configuracoes.py` e `features/settings/state.py` é compartilhada entre perfis. Os endpoints `tutor/password` e `veterinario/password` verificam respectivamente `password` e `senha`, mas não confirmação por e-mail. `components/auth.py` apresenta “Esqueceu a senha?” sem evento. O login `acesso/login` resolve e-mail entre tabelas e confirma `reserva_email`; esse mesmo critério deve orientar recuperação. Quick Start usa `user`, links demonstrativos e não serve a esse contrato.

`docs/backend-foundation.md` documenta logout local, sem revogação global dos tokens existentes. Não prometer encerramento de sessões em outros dispositivos nesta entrega. A documentação de arquitetura exige organização por domínio, Xano como autoridade e atualização conjunta de DER e XanoScript.

## Goals / Non-Goals

**Goals:** centralizar emissão e consumo dos desafios no Xano, separar finalidade e identidade, compartilhar apresentação e envio dos e-mails e preservar os guards de sessão da aplicação.

**Non-Goals:** 2FA no login, alteração de e-mail, recuperação sem acesso ao e-mail, mudanças de política de senha, revogação global de sessões, múltiplos provedores ou fallback automático ou alteração de autorização clínica.

## Decisions

### 1. Contratos separados com lógica comum no Xano

Adicionar POST autenticado `<perfil>/password/request-code`, recebendo senha atual e derivando conta/e-mail de `auth.id`. Manter POST `<perfil>/password` para conclusão, acrescentando `challenge_id` e `code` e revalidando senha atual e novos campos. O endpoint atual passa a rejeitar chamadas sem código; não deixar rota legada equivalente que contorne a exigência.

Adicionar POST público `acesso/password-reset/request` com e-mail; `verify` com desafio/código; `complete` com autorização restrita, nova senha e confirmação. A verificação emite autorização opaca de curta duração (cinco minutos), de uso único e sem privilégios de login; a conclusão deriva conta e finalidade dessa autorização. Não retornar token de acesso. Alternativa de usar magic link Quick Start foi descartada porque pertence a `user` e diverge do código solicitado.

Recuperação retorna mensagem “Se houver uma conta para este e-mail, enviaremos um código.” e um identificador opaco de mesmo formato inclusive para e-mail desconhecido ou ambíguo. Pedidos fictícios não geram e-mail; suas verificações falham genericamente. Não retornar e-mail mascarado ou perfil na recuperação pública. Evitar diferenças sistemáticas de tempo entre conta existente e inexistente, desacoplando envio ou uniformizando a resposta; comprovar o comportamento no ambiente alvo.

### 2. Persistência, consumo e limites

Criar entidade de desafio com identificador público aleatório de alta entropia, perfil, identidade, finalidade, hash protegido do código, criação/expiração, tentativas, estado de envio, consumo e hash/expiração da autorização restrita de recuperação. Nunca persistir senha ou código em claro. Usar hash com segredo do servidor para código de baixa entropia; segredo fora do repositório. Não usar códigos aleatórios comuns ou hash simples sem proteção contra enumeração offline.

Persistir limites por conta/finalidade e origem independentemente da duração de um desafio: dez minutos de validade, cinco erros, sessenta segundos entre envios, cinco envios por hora por conta/finalidade. Recuperação pública também limita solicitações por origem (inicialmente vinte por hora), com origem confiável fornecida pelo servidor/proxy, nunca por campo livre do cliente. Solicitações de e-mails desconhecidos também contam nos limites públicos. Reenvio substitui desafio e código anteriores sem resetar contadores agregados. Validar formato sem perder zeros iniciais.

Consumo e atualização de senha devem ocorrer atomicamente, com trava/condição de estado que garanta no máximo um vencedor. Implementação deve comprovar as primitivas de transação/concorrência suportadas pelo Xano de destino; não substituir por leitura seguida de escrita desprotegida. Senha atual é revalidada no commit de alteração; autorizações de recuperação são vinculadas à versão da credencial para rejeitar desafio anterior a outra mudança. Uma troca concluída invalida todos os desafios pendentes dessa conta.

Falha definitiva de entrega invalida o desafio; resultado incerto não dispara retry automático nem permite contornar limites. Código somente por e-mail. O usuário aprovou substituir o job pago do Xano por rotina no backend Reflex local. Um lifespan executa limpeza ao iniciar e a cada hora enquanto o processo estiver ativo; ao reiniciar recupera a limpeza pendente. Remover desafios e contadores sem atualização há 24 horas; manter eventos sanitizados de segurança por 30 dias, conforme configuração documentada, sem credenciais, códigos, cabeçalhos de autorização ou e-mail completo em logs de aplicação. Conferir também configurações de histórico de requests do backend para impedir registro de segredos.

### 3. Fluxo Reflex e estado temporário

Manter a experiência em Segurança compartilhada. Solicitar senha atual e envio; apresentar e-mail mascarado somente no contexto autenticado, código, reenviar e os campos de nova senha. A conclusão exige senha atual novamente se ela tiver sido limpa. Campos secretos não entram em armazenamento persistente; manter apenas o mínimo pelo tempo do fluxo e limpar ao sair, trocar aba/identidade, cancelar ou concluir.

Em login, abrir uma experiência de recuperação acessível com etapas e-mail → código → nova senha, com Voltar, Cancelar e confirmação final. Não requerer seleção de perfil. Validar autorização no backend, nunca apenas na etapa visual. Usar `features/auth/` para estado e `components/auth.py` para composição; `features/settings/` continua responsável por Segurança. Integração comum pode ficar em `shared/` somente onde houver reutilização concreta. Preservar a geração de sessão/operação contra respostas atrasadas, sem retry automático de escritas.

### 4. Template e prévia

Centralizar renderização numa função Xano de mensagens e manter HTML canônico editável em `xano/templates/password_verification.html`, versão textual adjacente e mecanismo documentado de sincronização para o XanoScript. A prévia deve ser gerada desse mesmo template com dados fictícios, evitando divergência entre prévia e envio. Um único conjunto de cores e marca textual e dois conjuntos de assunto/título: “Confirme a alteração da sua senha” e “Recupere seu acesso ao Vet Tech”.

Layout com tabelas e CSS inline, largura máxima de 600 px e fundo verde-água, cabeçalho submarino ilustrado, marca, código textual selecionável em bloco verde claro com borda tracejada, validade e aviso de solicitação desconhecida. Fonte de sistema com fallback; não depender de JavaScript, fontes remotas ou imagens para conteúdo essencial. O usuário decidiu manter o aplicativo no localhost; o usuário pediu posteriormente o cabeçalho ilustrado da referência. Após o ensaio CID falhar na caixa Gmail do usuário, a imagem passa a ser referenciada por URL HTTPS no HTML, sem anexos. Somente o banner precisa estar acessível publicamente; o aplicativo continua local. Marca alternativa e todo o conteúdo de segurança permanecem em texto. Variáveis limitadas e escapadas, assunto sem código, nunca incluir senha ou dados de pet. Documentar onde editar cores, marca e textos e como regenerar/publicar o template.

O usuário autorizou migrar do Resend para Brevo no plano gratuito, sem comprar domínio nem publicar o aplicativo. Usar `api.request` no Xano para `POST https://api.brevo.com/v3/smtp/email`, com `sender` e destinatário em objetos, `htmlContent` e `textContent`. A chave fica somente na variável Xano `BREVOS_API`, nome escolhido pelo usuário. `PASSWORD_EMAIL_FROM` mantém o formato `Vet Tech <vet.tech.impact@gmail.com>`; o remetente é validado antes do envio. Aceitar apenas resposta 2xx com `messageId` não vazio; falha genérica e nenhuma repetição automática ou fallback para Resend. Preservar o template, a referência independente `X-Entity-Ref-ID` e o escopo de destinatário derivado no backend. Publicar função e remetente juntos, em importação parcial transacional, preservando as demais variáveis de ambiente. A configuração antiga do Resend não é usada pela nova função.

Antes do teste, conferir chave válida, remetente ativo e envio transacional habilitado. Foram observados diferentes IPs de saída do Xano Free e falhas intermitentes após três liberações individuais. O usuário autorizou desativar somente o bloqueio de IP desconhecido para API no Brevo, mantendo chave privada e controles SMTP independentes. Essa decisão remove uma camada adicional de proteção e não contrata IP estático. Uma verificação saindo do computador não comprova o acesso nativo do Xano. Enviar testes somente para caixa explicitamente autorizada, sem alterar senhas reais. Aceitação não comprova entrega: verificar evento do provedor e/ou confirmação da caixa. Teste adicional com outro endereço cadastrado depende de o usuário indicar o destinatário. O plano gratuito tem cota diária do provedor; domínio Gmail não permite DKIM próprio e pode ser reescrito pelo Brevo. Não contratar plano ou domínio.

A limpeza usa POST interno `acesso/password-reset/cleanup`, assinado com HMAC de `password-cleanup:<timestamp>` e validade de cinco minutos. O segredo também fica no `.env` privado do backend Reflex, nunca em State ou no navegador. O endpoint valida assinatura e usa a mesma trava transacional das operações de senha. Com o aplicativo desligado, a remoção física aguarda o próximo início, mas códigos e autorizações vencidos continuam rejeitados pelo Xano. Não incluir tarefas agendadas na importação do plano Free.

## Risks / Trade-offs

- [Atrasos e filtros de spam] → validade visível, reenvio controlado e validação real com caixa de teste.
- [Enumeração e abuso de envio] → respostas públicas uniformes, limitação persistente por conta e origem e sem perfil na resposta.
- [Roubo do e-mail] → a confirmação prova acesso à caixa, sem oferecer garantia além disso; senha atual continua obrigatória em Segurança.
- [Sessões antigas permanecem válidas] → comunicar o limite existente na documentação técnica; não afirmar revogação global.
- [Concorrência ou logs do Xano expõem segredos] → validação no backend real e inspeção das configurações de logging antes de liberar.

## Migration Plan

1. Criar tabelas/funções aditivas, atualizar DER e configurar segredos/remetente no desenvolvimento.
2. Implementar endpoints e template; validar entrega com destinatário de teste explicitamente configurado, nunca usando conta real do usuário.
3. Atualizar frontend e endpoints de conclusão em entrega coordenada; clientes antigos devem falhar de forma segura.
4. Executar testes de identidade, expiração, replay e concorrência, confirmar que endpoints legados não oferecem bypass e revisar layout/entrega.
5. Publicar apenas os artefatos afetados, sem push integral de schemas antigos. Em rollback, desabilitar fluxos de senha com mensagem temporária, invalidar desafios/autorização pendentes e preservar login; não restaurar troca sem código inadvertidamente.

## Open Questions

- Confirmar entrega pelo Brevo e testar uma segunda caixa cadastrada indicada pelo usuário; não publicar o aplicativo nem contratar hospedagem.

### Refinamento visual solicitado pelo usuário

Reproduzir a referência enviada: fundo verde-água, cartão branco com borda verde arredondada, banner submarino com a tartaruga, título Vet Tech e código em caixa verde clara tracejada. A arte canônica fica em `xano/templates/password-email-header.jpg`. A tentativa inline CID chegou como anexo separado e deixou o cabeçalho quebrado no Gmail, conforme evidência do usuário; não considerar aceitação pelo Resend como validação visual da caixa.

O HTML passa a usar `header_image_url`, HTTPS, sem campo `attachments` no envio. A prévia resolve somente a imagem para bytes locais. O upload pelo Metadata API do Xano foi recusado com HTTP 403: “Not supported. Please upgrade your Xano instance.” Nenhum plano foi contratado. Foi preparada uma URL gratuita proposta para um repositório separado `7offdvx/vet-tech-assets`, contendo somente a imagem; o usuário autorizou explicitamente a criação/publicação e ela foi concluída, contendo somente o banner. A URL do HTML é fixada no commit publicado. Não publicar template remoto apontando para URL inexistente. Após hospedar a imagem, verificar GET anônimo com MIME image/jpeg e bytes corretos, publicar somente as duas funções e enviar novo teste autorizado. Validar ambas as finalidades em 390/900 px e leitura com imagens bloqueadas.

### Ilustração acima do aviso final

A pedido do usuário, incluir a imagem `fundinho.jpeg` fornecida, sem alterações de conteúdo, entre a linha divisória e “Não foi você?”. A cópia canônica fica em `xano/templates/password-email-pets.jpg` e a URL HTTPS em `footer_image_url`. Publicar somente essa arte no repositório de imagens já autorizado, fixar a URL no commit e preservar o cabeçalho e o conteúdo de segurança. Imagem responsiva dentro do padding do cartão, sem anexos; ambos os fluxos compartilham o template.

Acima da imagem de pets, após a linha divisória, apresentar o texto exato “O melhor sistema para seu melhor amigo!”, centralizado em verde e negrito. O texto permanece HTML selecionável, com quebra natural no celular.

Centralizar também o rótulo “SEGURANÇA DA SUA CONTA” e o título principal nas duas finalidades, conforme pedido do usuário, preservando o alinhamento do restante do conteúdo.

### Desenvolvedores no e-mail

Abaixo da imagem de pets, apresentar “Desenvolvedores do Sistema:” e uma tabela de três colunas com fotos de moldura arredondada, na ordem Davi Diniz, Vitor Sousa e Danikelly Alves, com nomes em uma linha de células abaixo. Usar as fotos fornecidas pelo usuário, com nomes como texto HTML e na alternativa TXT. Preparar primeiro a prévia local; a hospedagem pública dessas fotos pessoais foi autorizada explicitamente pelo usuário. Publicar somente as três fotos no repositório de imagens existente, fixar URLs por commit e verificar acesso anônimo antes de atualizar o renderizador remoto.

### Destaque verde e aviso final

Adicionar sombra verde suave às molduras das três fotos e centralizar o aviso “Não foi você?”. Como `box-shadow` não consta na lista de propriedades CSS suportadas pelo Gmail, incluir fundo verde e padding assimétrico na tabela da moldura, preservando o destaque mesmo sem o blur. Não modificar as fotos públicas. Conferir três colunas, nomes abaixo, ausência de overflow e fallback sem box-shadow.

Adicionar também “© by Vet Tech Team” centralizado ao final do rodapé, após a mensagem automática, com equivalente na versão textual.

### Revisão final: oceano e fotos sem sombra

O usuário pediu remover a shadow box e corrigir o rodapé para “Copyright © by Vet Tech Team”. Retirar as tabelas de fundo/sombra das três fotos, mantendo só a borda arredondada original. Aplicar a imagem existente `assets/fundo_mar.jpeg` como fundo externo por URL HTTPS no atributo background e em CSS inline na tabela externa; preservar o cartão branco e o conteúdo. Hospedar somente essa arte adicional no repositório autorizado. Usar fallback verde-escuro e rodapé branco para contraste mesmo com imagem bloqueada; conferir carregamento real e layout responsivo.

A caixa do código passa a usar o verde-escuro semelhante ao fundo do oceano (#0d403a), com fundo também no atributo bgcolor, e dígitos brancos (#ffffff), mantendo código selecionável, tamanho, borda tracejada e prazo.

Títulos, rótulo de segurança, slogan, trechos strong e nomes dos desenvolvedores usam o mesmo #0d403a da caixa de código; `brand_color` acompanha esse tom. Os dígitos do código permanecem brancos, conforme a solicitação anterior.

### Agrupamento e rodapé oculto no Gmail

As capturas do usuário mostram o rodapé completo ao expandir “Mostrar conteúdo cortado”, após vários testes com mesmo assunto. Usar `X-Entity-Ref-ID` distinto por envio no campo `headers` do payload Resend, conforme orientação oficial do provedor para evitar agrupamento Gmail. Gerar 16 bytes criptográficos e codificar imediatamente em base64 na mesma variável, independentemente do código/desafio e sem incluir segredos. Não alterar assuntos com códigos, não randomizar texto visível e não prometer que o HTML force a interface do Gmail. A aceitação do provedor não comprova remoção das reticências; confirmar com o usuário no novo envio.

O título de recuperação passa a ser “Recupere seu acesso ao Vet Tech!”, com exclamação final, tanto no assunto quanto no título dentro do e-mail.

### Marca na recuperação e visibilidade das senhas

Na recuperação, apresentar “Vet Tech Team” acima da mascote em V (`/consultation-pdf/mascote-v.png`), antes do título. Nos campos de senha do login, cadastro dos dois perfis, recuperação e Configurações, oferecer botão Mostrar/Ocultar com ícones, aria-controls e aria-pressed, preservando valor e autocomplete. Reutilizar a delegação JavaScript existente de `preferences.js` e extrair botão/wrapper em `components/password_input.py`, sem armazenar senha/visibilidade no servidor ou localStorage. Ao resetar o formulário ou ocultar a página, voltar a esconder os campos. Preservar o controle existente de Configurações e endurecer sua resolução de rótulos para inputs com aria-label. Verificar teclado, independência entre campos, reset, tema e celular; compilar e reiniciar o servidor local.

Na primeira etapa de recuperação (e-mail), Voltar encerra o fluxo e retorna ao login. Em código/nova senha, Voltar reinicia pela etapa de e-mail, descartando desafio, autorização, mensagem e respostas antigas; não reutilizar código já consumido.
