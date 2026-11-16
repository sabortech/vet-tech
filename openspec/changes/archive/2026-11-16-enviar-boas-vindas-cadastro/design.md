# Design

## Context

Ver motivação e escopo em `proposal.md`. Os endpoints `xano/api/authentication/auth/tutor_signup_POST.xs` e `veterinario/signup_POST.xs` já persistem identidade e `reserva_email` em transação e respondem `{success:true}`. O veterinário também grava espécies/especialidades. `State.signup` deriva o endpoint da escolha de cadastro e volta ao login; a autoridade sobre o perfil permanece no endpoint Xano. Login Google não cria contas.

A integração de senha usa Brevo com `BREVOS_API`/`PASSWORD_EMAIL_FROM`, template canônico HTML/TXT/JSON, prévias e publicação seletiva. Desenvolvedores já possuem URLs HTTPS públicas autorizadas em `7offdvx/vet-tech-assets`. A arte solicitada existe em `assets/mascote/clinicturtle.jpeg` e foi inspecionada: tartaruga em clínica, com cachorro, gato, coelho e hamster, sem gesto em V. Usar o arquivo original, sem gerar imagem nova nem afirmar no texto que está fazendo V.

## Goals / Non-Goals

**Goals:** acrescentar notificação confiável quanto à origem e ao perfil, preservar contrato e sucesso dos cadastros, reutilizar infraestrutura gratuita e permitir revisar visualmente os dois e-mails antes da publicação.

**Non-Goals:** verificação de e-mail, código de segurança, campanha de marketing, envio para contas antigas, cadastro Google, publicação do aplicativo, mudança de política de cadastro ou autorização clínica, reenvio automático após falha/incerteza.

## Decisions

### 1. Direção visual e editorial

Título compartilhado: “Que bom ter você no Vet Tech!”. Saudação “Olá, {{name}}!” e agradecimento por escolher o sistema. Usar branco no cartão, verde-escuro #0d403a em títulos/destaques e fundo suave que combine com a clínica. Banner com a imagem inteira e proporção original, cantos arredondados e texto alternativo; sem cabeçalhos falsos de cliente de e-mail.

Tutor: “Obrigado por escolher o Vet Tech para acompanhar o cuidado do seu melhor amigo!”; próximos passos: entrar na conta, cadastrar seus pets e consultar as informações registradas. Veterinário: “Obrigado por fazer parte do Vet Tech e contribuir para o cuidado dos nossos melhores amigos!”; próximos passos: entrar, organizar a agenda e acompanhar atendimentos; explicar que prontuários dependem da autorização dos tutores. Assuntos diferentes identificam boas-vindas ao tutor e ao profissional, sem dados sensíveis. Linguagem acolhedora sem inferir gênero, selos ou validação profissional externa.

Depois do texto, seção de desenvolvedores como no template de senha: três fotos arredondadas, nomes reais centralizados, sem sombras. Rodapé: “Vet Tech · Cuidado que acompanha você.” e “Esta é uma mensagem automática de boas-vindas.”, com “Copyright © by Vet Tech Team”. Não reutilizar o aviso de solicitação de senha desconhecida ou blocos de código, pois não pertencem a boas-vindas.

Revisão autorizada pelo usuário: incluir “Acesse nosso sistema” com destino temporário `http://localhost:3000/login`, configurado em `system_url` e acompanhado do mesmo link na alternativa TXT. O usuário confirmou o uso local ciente de que o link só funciona no aparelho onde o aplicativo está rodando. Usar botão em tabela com verde-oliva e texto creme, preservando legibilidade em e-mail. Validar URL permitindo apenas esse endereço HTTP local exato ou HTTPS; futura substituição pelo endereço público fica configurável, sem publicar o app nesta etapa.

### 2. Template canônico independente

Criar `xano/templates/welcome_email.{html,txt,json}` e função `Notifications/render_welcome_email`, com parâmetros restritos nome/perfil, validação de perfil e escape. Reutilizar os padrões de tabelas/estilos inline, cores e URLs já aprovadas, sem incluir boas-vindas como finalidade de código de senha. Criar sincronização e prévia próprias em `scripts/`, seguindo os padrões existentes; extrair só o utilitário que demonstrar reutilização, sem reestruturar os fluxos de senha.

A referência de imagem será HTTPS e fixada por versão no repositório de imagens já utilizado. Primeiro preparar prévia local com a imagem original; na implementação, publicar somente essa arte e conferir GET anônimo, MIME e bytes antes de atualizar renderizador remoto. Não alterar fotos, duplicar anexos nem publicar o app. As prévias podem resolver imagens localmente, mas o HTML enviado conserva URLs HTTPS.

### 3. Evento no commit e tentativa após o commit

Adicionar evento interno `welcome_email_event`, único por `perfil:identidade_id`, criado na mesma transação da conta; rollback elimina também o evento. Depois do commit, chamar função privada `Notifications/send_welcome_email` por evento, dentro de tratamento de erro que preserve `{success:true}`. Destinatário e nome são lidos da identidade persistida e conferidos contra perfil/reserva; não aceitar destinatário, HTML ou perfil livres do navegador. Só tutores/veterinários passam por esse fluxo; não modificar Quick Start `auth/signup` de `user`.

Reservar a tentativa com inserção em tabela interna `welcome_email_attempt`, índice único por evento, antes do HTTP. A unicidade do banco garante um vencedor sem depender de leitura seguida de escrita; conflitos não enviam novamente. Guardar apenas evento, estado/momento da tentativa e identificador do provedor quando aceito, sem duplicar nome/e-mail, corpo ou credenciais. Estados distinguem pendente sem tentativa, tentativa reservada, aceito, falhou e incerto; um processo interrompido depois da reserva não é reenviado automaticamente. Não prender chamada HTTP dentro da transação do cadastro.

A alternativa de envio no frontend foi descartada porque não cobre chamadas diretas, mistura origem/perfil e pode duplicar em retry. A alternativa de serviço/tarefa paga não cabe no ambiente gratuito. Nesta etapa há uma tentativa imediata após o commit; queda do processo entre commit e envio pode deixar pendência, inspecionável internamente e sem afirmar entrega garantida. Eventual tratamento operacional de evento nunca tentado usa o mesmo guard interno; não criar endpoint público de reenvio.

### 4. Brevo e segurança

Usar o remetente e chave já configurados no Xano, HTTP com timeout limitado e aceitação somente 2xx com `messageId` não vazio. Sem retry/fallback automático. Manter referência independente por mensagem, sem código/token no assunto ou cabeçalhos. Não generalizar o remetente de segurança em endpoint público. Qualquer extração de transporte comum exige regressão do e-mail de senha.

Desativar histórico de requests/funções com entrada sensível, não imprimir payloads de cadastro e registrar somente IDs/perfil/estado sanitizados. Uma tentativa por cadastro não substitui proteção do próprio cadastro contra abuso: observar consumo da cota gratuita e documentar o risco de esgotamento compartilhado com códigos de senha. Não enviar testes a endereços reais sem indicação explícita; o destinatário anteriormente autorizado continua sendo a caixa Vet Tech.

## Risks / Trade-offs

- [Falha do processo após commit] → evento persistido e diagnóstico honesto, sem exigir recadastro nem prometer entrega exata.
- [Resultado HTTP incerto] → priorizar não duplicar; nenhuma repetição automática após reservar tentativa.
- [E-mail informado incorretamente ou spam] → não prometer chegada universal; verificar eventos do Brevo e a caixa de teste.
- [Cota compartilhada com segurança] → sem disparo retroativo, uma tentativa por conta e documentação de consumo/monitoramento; não contratar plano.
- [Exposição de dados pessoais] → só nome/e-mail necessários ao envio, sem CPF, CRMV, prontuários, tokens ou senha.
- [Mudança de transporte afeta códigos] → preferir função de boas-vindas separada, reutilizando padrões; regressão obrigatória se houver extração comum.

## Migration Plan

1. Preparar templates e prévias dos perfis com dados fictícios; verificar 390/900 px, texto sem imagens e correspondência com a arte original.
2. Adicionar tabelas internas, funções, testes e DER; não enfileirar contas existentes.
3. Disponibilizar a imagem HTTPS e validar anonimamente; não publicar segredos/app.
4. Publicar tabelas/funções antes dos dois endpoints, de forma seletiva; verificar que as respostas de cadastro continuam compatíveis.
5. Testar novos cadastros sintéticos de cada perfil com destinatário de teste explicitamente autorizado, inclusive falha de envio, duplicidade e concorrência. Confirmar eventos e caixa real sem usar contas antigas.
6. Rollback remove somente o disparo dos dois endpoints, preservando criação da conta, registros de diagnóstico e envs; não reabrir regras de cadastro ou tocar códigos de senha.

Observação da inspeção final: já existia o endpoint demonstrativo Quick Start `message/send_welcome_email`, baseado em `user` e no provedor nativo Xano. Ele permanece inalterado e não chama Notifications nem participa dos cadastros de tutor/veterinário. Esta implementação não cria endpoint público de envio ou reenvio.

### Revisão visual solicitada após recebimento

Aplicar `assets/optimized/fundo02.webp` no fundo externo por atributo HTML background e CSS inline, com fallback verde-oliva. O cabeçalho passa de verde-petróleo para verde-oliva #526b35, com marca em creme claro e mascote original `assets/consultation-pdf/mascote-v.png` à esquerda. Usar tabela para alinhamento compatível com e-mail, proporções preservadas e URLs HTTPS imutáveis sem anexos. O rodapé deve manter contraste sobre o cenário com uma superfície sólida na mesma paleta. Preservar o conteúdo dos dois perfis e a foto clínica. Validar celular/desktop e imagens bloqueadas antes de publicar somente o renderizador.

Ajuste seguinte solicitado pelo usuário: mascote do cabeçalho ampliada de 86 para 110 px, célula alinhada embaixo e sem padding inferior no cabeçalho. O texto mantém padding próprio; a base do elemento da mascote coincide com a divisória inferior. Verificar por medidas no navegador em ambas as larguras.

Refinamento de borda: o PNG original possui halo branco/cinza e 10 linhas transparentes inferiores. Usar uma cópia limpa por edição de imagem, mantendo a fonte original. A cópia gerada tem 23 linhas inferiores até o limite opaco; em largura 110 px a compensação é 1,7 px. Validar a posição da base visível usando o limite alfa opaco, não apenas o retângulo do img. Aplicar margem inferior de -1,7 px ao img para apoiar a silhueta na divisória.

Revisão seguinte: o usuário substituiu o cenário externo fundo02.webp por assets/optimized/fundo.webp, mantendo cabeçalho, mascote, conteúdo e botão autorizados. Usar arquivo original por URL HTTPS imutável e conferir a paridade das prévias.
