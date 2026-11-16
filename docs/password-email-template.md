# Template de confirmação de senha

## Arquivos editáveis

- `xano/templates/password_verification.html`: estrutura visual do e-mail, usando tabelas e estilos inline.
- `xano/templates/password-email-pets.jpg`: imagem fornecida pelo usuário entre a linha divisória e o aviso “Não foi você?”, com URL HTTPS em `footer_image_url`.
- `xano/templates/password-email-header.jpg`: cabeçalho submarino com a tartaruga, usado no cabeçalho por URL HTTPS, sem anexos.
- `xano/templates/password_verification.txt`: conteúdo equivalente em texto simples.
- `xano/templates/password_verification.json`: cores, assuntos, títulos e mensagens das finalidades `change` (alteração) e `reset` (recuperação).

As variáveis `{{code}}`, `{{validity_minutes}}`, `{{title}}` e `{{intro}}` são preenchidas na renderização. Nunca inserir senhas ou tokens de
acesso. O código fica no corpo, não no assunto. Manter os campos essenciais como
texto para permitir copiar o código e ler o e-mail com imagens bloqueadas.

## Personalização e prévia

Editar as cores hexadecimais e os textos no JSON. Para alterar disposição ou
espaçamento, editar o HTML preservando estilos inline e o layout responsivo.
Para modificar o texto simples, editar também o TXT. Não colocar CSS arbitrário
nas variáveis de cor.

Gerar as duas prévias com dados exclusivamente fictícios:

```bash
.venv/bin/python scripts/preview_password_email.py
```

O comando gera `change.html`, `reset.html` e os equivalentes TXT em
`openspec/changes/archive/2026-11-15-verificar-alteracao-senha-email/evidence/email/`. O código de
exemplo é `042681`. O cabeçalho usa `header_image_url` no HTML enviado, sem anexos. A prévia converte apenas essa referência em data URI com os bytes locais para permitir revisar a arte antes da hospedagem. O envio mantém a URL HTTPS. O aplicativo pode continuar em localhost. Nenhum e-mail é enviado por esse comando.

## Sincronizar o template com o Xano

Após editar HTML, TXT, JSON ou a imagem JPEG, execute:

```bash
.venv/bin/python scripts/sync_password_email.py
.venv/bin/python scripts/sync_password_email.py --check
.venv/bin/python scripts/preview_password_email.py
```

A função gerada é `xano/function/security/render_password_email.xs`.
`Security/send_password_email` usa essa função e envia os dois corpos pela API
oficial do Brevo. Publicar os dois arquivos afetados no Xano após a verificação;
regenerar arquivos localmente não modifica o backend remoto. As prévias validam
apresentação local, não entrega nem todos os clientes de e-mail.

## Configurar Brevo

A pedido do usuário, Brevo substitui o Resend para permitir destinatários cadastrados além da caixa de teste, sem comprar domínio. O aplicativo continua em localhost. No Xano configurar:

| Variável | Valor |
|---|---|
| `BREVOS_API` | Chave **API** do Brevo, não chave SMTP; nome escolhido pelo usuário |
| `PASSWORD_EMAIL_FROM` | Remetente verificado: `Vet Tech <vet.tech.impact@gmail.com>` |
| `PASSWORD_CODE_SECRET` | Segredo aleatório de pelo menos 32 caracteres, no Xano e no backend Python local |

`PASSWORD_CODE_SECRET` também fica no `.env` ignorado do backend Python para assinar a limpeza. Sua rotação invalida desafios pendentes. A chave Brevo fica somente no Xano; não usar variável pública nem compartilhar em conversa/captura. A variável antiga `RESEND_API_KEY` não é lida pela função atual.

Em Brevo → SMTP & API → Chaves API e MCP, gerar chave API e salvar diretamente no Xano. Confirmar remetente ativo e envio transacional habilitado. No ambiente Xano Free consultado, foram observados diferentes IPs de saída. O usuário autorizou desativar somente o bloqueio de IP desconhecido para API no Brevo em Segurança → IPs autorizados; a configuração SMTP permanece independente. Essa decisão remove uma camada adicional de segurança: manter a chave privada no Xano, monitorar uso e preferir permissão limitada a e-mails transacionais. Não contratar IP estático/plano pago. Não confundir IP do computador com IP do Xano.

A função interpreta `PASSWORD_EMAIL_FROM` como `Nome <email>` ou endereço simples (nome padrão Vet Tech). Chama `POST https://api.brevo.com/v3/smtp/email`, com header `api-key`, `sender`, `to`, `subject`, `htmlContent`, `textContent` e referência independente no header da mensagem; sem anexos, CC/BCC ou retry automático. O destinatário autenticado é derivado no Xano, nunca escolhido pela tela. Somente 2xx com `messageId` não vazio é aceito. Isso não comprova chegada à caixa; validar evento de entrega e mensagem recebida.

O plano gratuito está sujeito à cota do Brevo. Remetentes Gmail não permitem autenticação de domínio própria e o Brevo pode reescrever o domínio do remetente. A integração não promete entrega na caixa de entrada. Não é necessário contratar domínio ou publicar o aplicativo.

Publicar a função e o valor de remetente juntos, por importação parcial transacional, preservando todos os demais envs. O histórico da função continua desativado; não registrar payloads, códigos ou credenciais. Falhas não ativam fallback para Resend. Testes de envio ficam restritos à caixa autorizada; testar outra caixa cadastrada exige indicação do usuário.

Documentação oficial: [API de envio](https://developers.brevo.com/reference/send-transac-email), [chaves API](https://help.brevo.com/hc/en-us/articles/209467485-Create-and-manage-your-API-keys) e [remetentes](https://help.brevo.com/hc/en-us/articles/208836149-Create-a-new-sender-From-name-and-From-email).

No plano Free do Xano, a CLI informa que o push direto é sempre permitido, mesmo quando `allow_push` aparece falso. Não alterar essa preferência nem contratar plano pago. A atualização dos endpoints no Xano é necessária mesmo com a interface no localhost. O envio nativo Quick Start `service_provider="xano"` não é
utilizado porque não permite configurar destinatário/remetente.

## Limpeza no modo gratuito

O Xano Free não aceita tarefas agendadas. O lifespan do backend Reflex chama
`POST acesso/password-reset/cleanup` ao iniciar e a cada hora. A chamada usa HMAC
de finalidade exclusiva e timestamp com tolerância de cinco minutos; não usa
credenciais administrativas. Parar o aplicativo pausa a remoção física até o
próximo início, sem tornar válidos códigos expirados.

## Visual da referência

O cartão usa fundo verde-água, contorno verde arredondado e código em bloco verde claro com borda tracejada. A arte do banner foi criada a partir da referência do usuário e da mascote existente, exportada em JPEG de 1200 × 440 para exibição de até 594 px. Todo o código, prazo e orientação de segurança continuam como texto HTML e na alternativa TXT, mesmo com imagens bloqueadas.

O primeiro teste CID apareceu como anexo separado e imagem quebrada no Gmail do usuário. A correção usa a propriedade `header_image_url` no JSON e não envia anexos. Somente o JPEG precisa de acesso público HTTPS; não é necessário publicar o aplicativo. O endpoint de upload de arquivos do Xano recusou o plano atual com HTTP 403 e indicação de upgrade. Não contratar plano para esse ajuste.

O usuário autorizou e foi criado o repositório público separado [7offdvx/vet-tech-assets](https://github.com/7offdvx/vet-tech-assets), contendo somente as imagens do cabeçalho e de pets. Nenhum código do aplicativo foi publicado. `header_image_url` aponta para a versão imutável da imagem no `raw.githubusercontent.com`, fixada pelo commit. O GET anônimo foi verificado com HTTP 200, MIME `image/jpeg` e bytes idênticos ao arquivo canônico. O aplicativo continua local e não houve contratação de plano.

Para trocar a arte: exportar o JPEG, atualizar o arquivo público e `header_image_url`, regenerar o renderizador, conferir as prévias, publicar as duas funções e validar em caixa de teste. A prévia local por si só não comprova que o Gmail consegue carregar a imagem remota.

A imagem de pets foi copiada sem alterações de `fundinho.jpeg`, fornecida pelo usuário. Fica abaixo da linha divisória, antes do aviso final, com largura responsiva de até 546 px e proporção preservada. `footer_image_url` aponta para uma versão fixa por commit no mesmo repositório público. Nenhuma imagem é enviada como anexo.

Acima da imagem de pets, o HTML apresenta a frase centralizada “O melhor sistema para seu melhor amigo!”, em verde e negrito, com quebra natural em telas estreitas.

O rótulo “SEGURANÇA DA SUA CONTA” e o título principal também ficam centralizados, nas variantes de alteração e recuperação.

## Desenvolvedores

A seção abaixo da imagem de pets mostra Davi Diniz, Vitor Sousa e Danikelly Alves em uma linha de três colunas, com fotos de borda verde e cantos arredondados e nomes abaixo. Os nomes também aparecem na versão TXT. `davi_image_url`, `vitor_image_url` e `danikelly_image_url` devem apontar para imagens HTTPS. O usuário autorizou a publicação pública dessas fotos; elas estão no repositório `7offdvx/vet-tech-assets`, em `email/developers/`. As três URLs são fixadas por commit e foram verificadas anonimamente com MIME correto e bytes idênticos aos arquivos locais. A prévia usa os arquivos em `xano/templates/developers/`, sem upload automático.

As fotos dos desenvolvedores recebem `box-shadow` verde suave e uma moldura em tabela com fundo verde claro e padding assimétrico, preservando o destaque quando a sombra CSS é ignorada. A [lista oficial de CSS do Gmail](https://developers.google.com/workspace/gmail/design/css) não inclui `box-shadow`; por isso a apresentação não depende dessa propriedade. O aviso “Não foi você?” e “© by Vet Tech Team” no rodapé ficam centralizados; o copyright também aparece no TXT.

## Aparência atual: fundo do oceano

A revisão solicitada pelo usuário remove as três shadow boxes: as fotos voltam a ter somente a borda arredondada original. O copyright passa a “Copyright © by Vet Tech Team”. `ocean_image_url` aponta para a cópia pública da arte existente `assets/fundo_mar.jpeg`, preservada localmente em `xano/templates/password-email-ocean.jpeg`. A tabela externa usa atributo `background` e CSS inline para a imagem; o cartão continua branco. O fallback é verde-escuro (#0d403a) e os textos externos do rodapé são brancos, preservando leitura com a imagem desativada. Não são enviados anexos.

A caixa do código usa o verde-escuro #0d403a do fundo do oceano (`background_color`), com dígitos brancos (#ffffff). O atributo bgcolor acompanha o fundo inline para compatibilidade com e-mail.

`brand_color` agora acompanha #0d403a: títulos, rótulos de destaque, slogan, strong e nomes usam esse verde-escuro. A caixa do código compartilha o tom e seus dígitos continuam brancos.

## Rodapé cortado pelo Gmail

O Gmail pode esconder conteúdo repetido em conversas atrás de reticências. O remetente inclui uma referência aleatória independente em `headers.X-Entity-Ref-ID` no payload do Brevo, seguindo a [orientação oficial de cabeçalhos personalizados](https://resend.com/changelog/custom-email-headers) para evitar agrupamento. A referência não usa código, desafio, e-mail ou token. Não há alteração do assunto ou texto visível. Isso reduz a causa associada a conversas, mas a interface de exibição continua sob controle do Gmail; verificar a mensagem mais recente na caixa real.
