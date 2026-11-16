# Tasks

## 1. Conteúdo e apresentação dos dois perfis

- [x] 1.1 Criar HTML/TXT/JSON canônicos de boas-vindas com nome escapado e variantes tutor/veterinário; testar acentos, caracteres de HTML, perfis inválidos e ausência de credenciais/dados clínicos na mensagem.
- [x] 1.2 Compor cartão com a `assets/mascote/clinicturtle.jpeg` original, desenvolvedores arredondados sem sombras e copyright; entregar prévias em 390/900 px para ambos os perfis, verificando ausência de overflow, proporção da imagem e leitura sem imagens.
- [x] 1.3 Criar sincronização para o renderizador Xano e comandos de prévia, documentando edição e URL temporária de acesso autorizada; verificar paridade de renderização e executar os comandos documentados com dados fictícios.

## 2. Evento e controle de tentativa no Xano

- [x] 2.1 Adicionar evento único por perfil/identidade e reserva de tentativa com índice único por evento, sem CRUD público; atualizar DER e validar XanoScript, demonstrando que IDs iguais em perfis distintos não colidem e que a reserva concorrente tem um vencedor.
- [x] 2.2 Implementar resolução privada da identidade pelo evento e leitura de nome/e-mail do backend; testar perfil inválido, evento inexistente, identidade divergente e rejeição de destinatário arbitrário, documentando o contrato interno.
- [x] 2.3 Implementar transporte Brevo de boas-vindas com envs existentes, aceitação 2xx/messageId, timeout, falhas sanitizadas e ausência de retry automático; testar recusa, resultado incerto e duplicidade com provedor simulado, preservando regressão do remetente de senha se houver extração comum.

## 3. Integração aos cadastros

- [x] 3.1 Registrar evento na transação e disparar somente após commit do cadastro de tutor; testar sucesso, rollback e cadastro duplicado, incluindo sucesso da conta quando o provedor falha e resposta `{success:true}` preservada.
- [x] 3.2 Integrar o cadastro veterinário após conclusão da identidade/reserva/vínculos; testar destinatário/perfil corretos, falha em vínculo e indisponibilidade do provedor, sem enviar antes da confirmação.
- [x] 3.3 Verificar que login por senha/Google, recuperação e chamadas Quick Start de `user` não acionam boas-vindas; executar testes de regressão relevantes e documentar que não haverá envio retroativo a contas existentes.

## 4. Imagem pública e entrega seletiva

- [x] 4.1 Disponibilizar somente a imagem clínica em HTTPS na infraestrutura gratuita de imagens e fixar sua versão no template; verificar GET anônimo, MIME/bytes e ausência de anexo, sem publicar o aplicativo ou qualquer segredo.
- [x] 4.2 Publicar seletivamente tabelas/funções e depois os dois endpoints; conferir índices, configuração privada, histórico desativado e ausência de alterações em login, códigos de senha ou permissões clínicas, registrando rollback.
- [x] 4.3 Validar no backend de desenvolvimento cadastros sintéticos dos dois perfis e controle de duplicidade sem atingir caixas reais não autorizadas; registrar evidências sanitizadas e distinguir testes simulados de chamadas reais ao provedor.
- [ ] 4.4 Enviar prévias reais das duas variantes somente à caixa explicitamente autorizada e confirmar eventos/visual; testar cadastro real completo apenas com novos endereços de teste indicados pelo usuário, registrando resultado sem prometer entrega universal, e validar a change no OpenSpec.

## 5. Fundo e cabeçalho da revisão visual

- [x] 5.1 Aplicar fundo02.webp externo, cabeçalho verde-oliva e mascote em V à esquerda; publicar as duas imagens em HTTPS, verificar bytes/MIME, prévias dos dois perfis com/sem imagens, paridade dos renderizadores e publicar somente a função de renderização.

- [x] 5.2 Aumentar a mascote do cabeçalho para 110 px e encostar sua base na divisória inferior, mantendo a marca à direita; verificar alinhamento em 390/900 px nos dois perfis e publicar o renderizador.

- [x] 5.3 Remover o halo claro do PNG por edição de imagem preservando o original, compensar a margem alfa inferior para que a base visível encoste na divisória e verificar as quatro prévias antes de publicar o renderizador.

- [x] 5.4 Adicionar botão Acesse nosso sistema com URL temporária localhost:3000/login autorizada, equivalente TXT e validação de URL; conferir ambos os perfis, celular/desktop e publicar somente o renderizador.

- [x] 5.5 Substituir o cenário externo por assets/optimized/fundo.webp, verificar a imagem HTTPS e prévias dos dois perfis e publicar o renderizador.
