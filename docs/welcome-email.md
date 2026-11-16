# E-mail de boas-vindas

Tutores e veterinários recebem orientações distintas após um novo cadastro. Nome, e-mail e perfil são derivados da conta criada no Xano. O envio não valida o e-mail nem autentica a pessoa. Login por senha/Google e recuperação de senha não geram boas-vindas.

## Personalizar e revisar

Fontes: `xano/templates/welcome_email.html`, `.txt` e `.json`. A imagem é a original `assets/mascote/clinicturtle.jpeg`, publicada por versão fixa em HTTPS. Não há anexos. As URLs dos desenvolvedores reutilizam as fotos já autorizadas. Marca, próximos passos e copyright permanecem como texto quando imagens são bloqueadas.

```bash
.venv/bin/python scripts/sync_welcome_email.py
.venv/bin/python scripts/sync_welcome_email.py --check
.venv/bin/python scripts/preview_welcome_email.py
.venv/bin/python tests/integration/welcome_email_preview.py
```

A prévia gera dois HTML/TXT com nomes fictícios em `openspec/changes/archive/2026-11-16-enviar-boas-vindas-cadastro/evidence/email/`. Só a prévia embute bytes das imagens; o e-mail enviado mantém HTTPS. Por autorização explícita do usuário, o botão Acesse nosso sistema aponta temporariamente para `http://localhost:3000/login`, também presente no TXT. Esse endereço só funciona no aparelho onde o app está rodando. `system_url` no JSON poderá receber a URL pública HTTPS quando disponível. Publicar o aplicativo não é necessário nesta etapa.

## Contrato e configuração

Os endpoints existentes `tutor/signup` e `veterinario/signup` continuam retornando `{success:true}`. O evento é gravado na mesma transação da identidade e só existe se o cadastro completo for confirmado. `util.post_process` inicia o envio após a resposta, fora da transação de cadastro. Falha do Brevo não desfaz a conta nem solicita recadastro.

As funções `Notifications/welcome_identity` e `Notifications/send_welcome_email` recebem somente `event_id`; resolvem a tabela pelo perfil do evento e conferem a reserva de e-mail. O transporte `Notifications/deliver_welcome_email` é função interna, sem endpoint público, e usa `BREVOS_API` e `PASSWORD_EMAIL_FROM` já configurados no Xano. Não colocar chave em frontend, código ou conversa. Não há mudança no remetente de códigos de senha.

`welcome_email_event.key` é único por `perfil:identidade_id`. `welcome_email_attempt.event_id` é único: a inserção antes do HTTP reserva uma tentativa, impedindo duas chamadas mesmo sob concorrência. Dados operacionais não duplicam nome, e-mail ou corpo. Estados: evento sem tentativa é pendente; tentativa `reservado`, `aceito`, `falhou` ou `incerto`. Aceitação exige HTTP 2xx e messageId; não comprova entrega. Erros HTTP 4xx são falha definitiva da chamada, outros resultados sem confirmação são incertos. Se o processo cair após a reserva, não há reenvio automático. Dados são mantidos como registro operacional de idempotência; não expor CRUD público.

Uma conta por e-mail e uma tentativa por evento não substituem proteção contra abuso do cadastro. A cota Brevo é compartilhada com os códigos de senha; acompanhar consumo e falhas no provedor. Não há disparo retroativo, job pago ou retry automático. O histórico das funções e dos endpoints com senha é desativado.

## Publicação e rollback

Validar/publicar somente as duas tabelas, quatro funções de Notifications e dois endpoints alterados, nesta ordem de dependências. Preservar dados, envs, autorizações e demais rotas. Conferir imagem por GET anônimo e corpos gerados antes do envio real.

Rollback: remover o bloco de criação do evento e `util.post_process` dos dois endpoints, preservando o cadastro original; manter tabelas/metadados para diagnóstico e envs. Não modificar o login ou a segurança de senha. Conta criada não depende da disponibilidade do e-mail.

Testes reais de entrega usam somente caixas autorizadas. Cadastros sintéticos usam e-mails `.invalid` e não comprovam entrega; provedor simulado deve ser identificado como tal. Um cadastro real com chegada à caixa exige endereço novo explicitamente indicado pelo usuário; não alterar ou excluir contas existentes para viabilizar o teste.

Observação da inspeção final: já existia o endpoint demonstrativo Quick Start `message/send_welcome_email`, baseado em `user` e no provedor nativo Xano. Ele permanece inalterado e não chama Notifications nem participa dos cadastros de tutor/veterinário. Esta implementação não cria endpoint público de envio ou reenvio.

## Verificações de integração

```bash
.venv/bin/python tests/integration/welcome_email_live.py
.venv/bin/python tests/integration/welcome_email_rollback_live.py
```

Executar somente no workspace de desenvolvimento confirmado pela fixture privada. O primeiro ensaio cria contas `.invalid`, verifica login com falha de envio, rejeição de cadastro inválido e reserva concorrente com transporte simulado. O segundo usa clones privados dos endpoints e força erro após a inserção do evento para verificar rollback. Ambos removem os registros e diagnósticos temporários e não enviam e-mails reais. `.invalid` é reservado e rejeitado antes de qualquer HTTP ao Brevo. O primeiro ensaio limita chamadas administrativas e guarda checkpoint ignorado `.env.welcome-test-pending.json`; em falha de limpeza, reconciliar esse checkpoint antes de repetir. Não publicar os diagnósticos de `tests/fixtures/` como parte do aplicativo.

As funções Xano também contêm 13 testes unitários nativos nomeados: perfil/identidade, entrega confirmada, recusa/cota e resultado incerto. Neles, o provedor e os acessos ao banco são simulados por test case; execução normal usa as dependências reais. A prévia real pode ser enviada administrativamente pela função interna `Notifications/deliver_welcome_email` somente para destinatário explicitamente autorizado. Não criar endpoint para esse ensaio.

## Revisão do cabeçalho e fundo

O fundo externo usa o original `assets/optimized/fundo.webp` por HTTPS, com fallback #4c5c34. O cabeçalho usa verde-oliva #526b35 e texto creme #fff9e7; a mascote original em V fica à esquerda da marca em tabela. O rodapé mantém superfície sólida na mesma paleta para contraste sobre o cenário. `background_image_url`, `mascot_image_url` e `header_color` ficam no JSON canônico; a prévia resolve os arquivos locais, enquanto o envio mantém URLs HTTPS imutáveis, sem anexos.

A mascote do e-mail usa a cópia `mascote-v-clean.png`, editada para remover o halo claro; o PNG original continua preservado. O alinhamento inferior compensa 1,7 px de transparência do arquivo. O teste de prévia compara o limite alfa visível com a divisória, além das medidas do elemento HTML.
