# Verificação da prévia compartilhada de PDF

## Resultado final

Implementação e publicação concluídas após autorização do usuário. As 15 tarefas estão completas. O PDF real aparece no painel em todos os acessos de tutor/veterinário, com rolagem, tartaruga lateral no padrão do calendário e Baixar PDF no rodapé. Não foi necessário reiniciar o aplicativo real após publicar os endpoints.

## Backend publicado

Os cinco arquivos de `backend-manifest.json` foram publicados no perfil “Davi Diniz”, workspace 167758: função compartilhada, GET de prévia dos dois perfis e POST de exportação dos dois perfis. Nenhuma tabela, variável de ambiente ou registro real foi alterado. Metadados e execuções reais confirmaram referências resolvidas, apesar dos avisos do CLI sobre dependências fora do conjunto parcial.

O teste real identificou que o nome do diagnóstico associado precisava de `eval = {nome: $db.doenca.nome}`. A função foi corrigida/republicada, e a projeção unitária e as respostas reais confirmaram o nome correto e os quatro tipos de complemento.

56 checks remotos passaram: propriedade, correspondência pet/consulta, estado finalizado, dois perfis, auditoria de prévia, correspondência prévia/exportação, operações por ator/perfil, idempotência/concorrência, revogação/restauração e falha de auditoria sem inserção duplicada. [Resultados sem dados clínicos](evidence/backend-results.json).

As contas fictícias rastreadas precisaram renovar sessões expiradas. Consentimento e complementos foram criados somente para o pet fictício do ledger validado por prefixo. Registros sintéticos permanecem rastreados em `.venv/clinical-smoke/pdf-export-local/`, fora do versionamento; logs de auditoria foram preservados.

## Aplicativo real e Xano publicado

Duas sessões fictícias isoladas, sem usar a sessão pessoal do navegador:

- Tutor em `localhost:3000`: selecionar o pet/consulta, abrir PDF, rolar até a última página e baixar; arquivo contém Vacina e Exame sintéticos corretos. [Resultado](evidence/live/results.json).
- Veterinário em `localhost:3000`: reabrir o atendimento finalizado, abrir o PDF, rolar e baixar o mesmo recorte autorizado. [Resultado](evidence/live/veterinario-results.json).
- Três páginas em ambos os documentos, sem erros JavaScript. Capturas e PDFs exclusivamente sintéticos em `evidence/live/`.

## Testes locais e navegador isolado

- Suíte completa: 343 testes passaram, 10,409 s. [Log](evidence/unit-tests.log). Após ajustar `eval`, o teste da projeção foi repetido e passou.
- `reflex compile --dry`: sucesso, 5,080 s.
- Navegador com API sintética: quatro acessos (tutor, atendimento finalizado, consulta reaberta e agenda), quatro downloads corretos, primeira/última página acessíveis por rolagem, retorno de foco, temas claro/escuro, 1280 × 900 e 390 × 844, sem overflow ou erros JavaScript. [Resultado](evidence/pdf-viewer/results.json).
- O teste visual usa `data-vt-theme`, seletor real do projeto. [Desktop escuro](evidence/pdf-viewer/perfil-tutor-desktop-dark.png), [celular na última página](evidence/pdf-viewer/perfil-tutor-mobile-dark-last-page.png).
- Node precisa estar no PATH para os testes de projeções. Os testes asyncio foram executados fora do sandbox, que travava ao encerrar o executor.

## Requisições e memória

Uma abertura faz um GET autorizado e uma renderização; cliques repetidos no mesmo painel, rolagem, mudança de tema e fechamento não fazem consultas adicionais. Confirmar faz um POST para revalidar acesso e conteúdo. O mesmo PDF é reutilizado quando o DTO coincide; se mudou, a prévia é atualizada e exige nova confirmação. Finalizar não redireciona/recarrega agenda, e atendimento finalizado não carrega catálogo destinado à edição.

Os bytes ficam privados e limitados a 2 MiB durante o painel aberto. Um evento efêmero os entrega ao PDF.js, sem base64 no State serializado, URL pública, storage ou cache global. O visualizador carrega módulos locais sob demanda e mantém apenas canvases próximos da área visível; documento, worker e canvases são liberados ao fechar. Fechamento, sessão, rota, pet e consulta invalidam respostas atrasadas; negativa de acesso limpa a prévia.

PDF.js 6.5.438 e sua licença Apache-2.0 estão em `assets/pdf-viewer/`. A URL do CSS global foi versionada para invalidar a folha antiga observada pelo usuário. O feedback duplicado fora do diálogo foi removido. A mensagem de falha anterior vinha dos endpoints de prévia ausentes; após publicação, o aplicativo real foi validado.

## Referências técnicas

- [Reflex Dialog](https://reflex.dev/docs/library/overlay/dialog/)
- [Reflex Background Events](https://reflex.dev/docs/events/background-events/)
- [Xano database operations](https://docs.xano.com/xanoscript/function-reference/database-operations.md)
- [PDF.js examples](https://mozilla.github.io/pdf.js/examples/)

Change concluída e arquivada por solicitação do usuário; especificação principal sincronizada.
