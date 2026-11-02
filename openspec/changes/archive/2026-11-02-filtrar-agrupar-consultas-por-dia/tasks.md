# Tasks

## 1. Contrato dos filtros

- [x] 1.1 Ajustar a Lambda da agenda para Hoje, Próximas incluindo hoje + 4 dias e estados corretos, preservando modo dia, busca autorizada, foto null, ordenação e paginação; verificar com testes determinísticos de fronteiras, virada de mês/ano, fuso, mais de 25 registros e combinação de filtros, e documentar o novo contrato em docs/clinical-flow.md.

## 2. Lista agrupada

- [x] 2.1 Derivar grupos diários do estado carregado com rótulos Hoje/Amanhã/data e requisito de contrato novo para Próximas; verificar grupos, continuidade entre páginas, vazio, troca de filtro e respostas antigas com testes unitários.
- [x] 2.2 Renderizar divisórias reutilizando os cards e tokens existentes, preservando resumo, fotos, histórico, ações e paginação; compilar Reflex com a versão do processo existente e verificar disposição, foco e temas em desktop/celular com dados sintéticos, registrando evidências e limitações.

## 3. Publicação e integração

- [x] 3.1 Conferir novamente a versão remota e publicar somente o endpoint de agenda via CLI Xano autenticada, após dry-run; reler o contrato publicado e verificar Hoje/Próximas/Concluídas/Canceladas, busca, paginação e revogação com dados sintéticos descartáveis, registrando resultados e removendo apenas os dados desse teste.
- [x] 3.2 Executar regressão apropriada e build de produção; reiniciar com segurança o processo correto e conferir HTTP e fluxo integrado de filtros, divisórias e seleção; atualizar documentação simples e evidências, sem alterar dados reais.

## 4. População manual da Jessy

- [x] 4.1 Identificar inequivocamente Jessy e o médico com consentimento ativo no workspace autenticado, fixar hoje em America/Sao_Paulo e conferir horários livres nos cinco dias; verificar os vínculos e registrar o alvo no manifesto privado, pedindo identificação se houver ambiguidade sem criar ou reativar consentimento.
- [x] 4.2 Criar exatamente cinco consultas agendadas de teste para Jessy, uma por dia de hoje até hoje + 4 dias, com motivo identificado e horários sem conflito; usar operação administrativa pontual para hoje se a regra pública de futuro impedir sua criação, sem alterar essa regra, e verificar leitura remota, manifesto de IDs e proteção contra duplicação em reexecução.
- [x] 4.3 Conferir as cinco consultas no filtro Próximas e suas divisórias Hoje/Amanhã/data e a consulta de hoje na aba Hoje; documentar datas/horários efetivos e entregar os IDs ao usuário. Manter esses cinco registros para exclusão posterior pelo usuário, separando-os da limpeza dos dados sintéticos automatizados.

As tarefas 2.2 e 3.2 foram encerradas após o usuário informar que concluiu os testes e autorizar sua conclusão. O aceite é do usuário; não representa inspeção visual executada pelo agente. Ver verification.md.

- [x] 4.4 Excluir as cinco consultas da população após aceite e solicitação expressa do usuário, conferindo IDs e identificação no manifesto e ausência de vínculos clínicos; verificar por releitura que os IDs não existem mais e registrar a limpeza sem alterar outros registros.
