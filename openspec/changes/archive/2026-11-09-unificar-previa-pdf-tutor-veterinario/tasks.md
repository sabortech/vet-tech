# Tasks

## 1. Contratos autorizados de prévia e exportação

- [x] 1.1 Compartilhar a montagem do recorte publicado por pet/consulta em função Xano reutilizável e adicionar GET de prévia para tutor e veterinário; verificar propriedade, consentimento ativo, negativa para rascunho/legado e auditoria de visualização em harness sintético de desenvolvimento.
- [x] 1.2 Adicionar POST de exportação profissional com revalidação transacional de acesso e operação idempotente por perfil/ator, preservando o POST tutor; verificar retry, colisão entre perfis, consulta/pet divergente, revogação e falha de auditoria sem liberação de dados.
- [x] 1.3 Documentar contratos, códigos de erro, distinção ator/autoria via consulta e procedimentos de verificação em `docs/consulta-pdf.md`; verificar que não exige alteração de entidades e que scripts de teste não expõem credenciais ou dados reais.

## 2. Estado compartilhado para conferir e baixar

- [x] 2.1 Separar abertura/carregamento/fechamento da prévia e confirmação do download em `features/clinical/state.py`, com alvo e geração próprios por perfil; adicionar testes que comprovem abertura sem download automático e equivalência das informações da prévia com o DTO do PDF.
- [x] 2.2 Reutilizar mapeador/renderizador no download após nova autorização, comparando assinatura do conteúdo com a prévia; testar atualização que exige reconfirmação, retry idempotente, clique duplo, limites, falhas e preservação do template aprovado.
- [x] 2.3 Limpar prévia e invalidar operações ao fechar, navegar, trocar pet/consulta/perfil ou sessão; testar respostas atrasadas, consentimento revogado, logout e duas sessões isoladas, sem bytes ou tokens no State serializado.

## 3. Painel com mascote e acessos dos dois perfis

- [x] 3.1 Criar `components/consultation_pdf.py` e CSS escopado com título, informações completas, tartaruga espreitando lateralmente, rolagem e Baixar PDF abaixo; verificar tema claro/escuro, textos longos, campos ausentes, foco, fechamento por teclado e 390 px sem obstrução ou overflow.
- [x] 3.2 Alterar o acionador do tutor para abrir o painel e adicionar os acionadores do veterinário na confirmação de finalização e no atendimento finalizado reaberto; verificar todas as entradas pelo navegador e ausência em estados inelegíveis ou sem autorização.
- [x] 3.3 Atualizar `docs/architecture.md` e `docs/consulta-pdf.md` para o componente e fluxo compartilhados; executar compilação conforme `reflex-process-management` e registrar resultado sem modificar módulos fora do escopo.

## 4. Integração do fluxo completo

- [x] 4.1 Ampliar os harnesses sintéticos existentes de PDF para tutor/veterinário, prévia cancelada, download confirmado, reabertura de finalizada, revogação, troca de contexto e falhas; executar testes de State/DTO e verificação de backend em desenvolvimento, registrando evidências e limites de ambiente em `verification.md`.
- [x] 4.2 Executar verificação visual/browser desktop e celular nos dois temas, confirmar arquivo correto e ausência de download antes de Baixar PDF, e validar a change com `openspec validate unificar-previa-pdf-tutor-veterinario --strict`.

## 5. Otimização de requisições

- [x] 5.1 Medir por testes que cada abertura faz um GET, cada confirmação faz um POST e fechar/rolar/repetir abertura no mesmo painel não fazem novas leituras; confirmar renderização única da prévia reutilizada no download e ausência de recarga da agenda ao finalizar e de catálogo de edição ao reabrir finalizada.

## 6. Refinamento: próprio PDF rolável e painel no padrão do calendário

- [x] 6.1 Substituir a lista textual por páginas reais do PDF em visualizador local progressivo, com limpeza ao fechar e reutilização dos bytes na confirmação; testar geração, reconfirmação e isolamento.
- [x] 6.2 Reorganizar o painel como o seletor de data, com tartaruga ao lado e rodapé fixo; atualizar versão do CSS e verificar capturas desktop/celular nos dois temas.
- [x] 6.3 Validar rolagem por todas as páginas, ausência de download automático, orçamento de chamadas e liberação do documento no navegador; registrar dependência/licença do PDF.js e resultados.
