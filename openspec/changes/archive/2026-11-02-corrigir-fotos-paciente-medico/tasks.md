# Tasks

## 1. Foto no estado e na interface

- [x] 1.1 Incluir foto sanitizada na projeção clínica e priorizar a resposta atual no resumo; reutilizar cache autorizado do mesmo pet somente após sucesso clínico e omissão da chave foto; null/vazio explícito prevalece. Verificar com testes de resposta atual, contrato anterior, paciente diferente, falha, revogação e resposta antiga.
- [x] 1.2 Exibir avatar no cabeçalho do atendimento reutilizando o componente existente; verificar fallback por renderização compilada e preservação dos tokens/estrutura responsiva e atualizar docs/clinical-flow.md com o comportamento implementado.

## 2. Contrato Xano

- [x] 2.1 Conferir e, se necessário, publicar as projeções de foto da agenda e de Clinical/assert_access, preservando consentimento e auditoria; verificar respostas com paciente sintético autorizado e acesso revogado. Registrar evidências e situação real de publicação nos documentos pertinentes.

## 3. Integração

- [ ] 3.1 Executar testes relevantes e compilar Reflex conforme skills do projeto; verificar foto em Horários, Consultas, resumo, atendimento e histórico no navegador em desktop/celular, incluindo imagem ausente ou quebrada, e registrar resultados sem dados reais.

- [x] 3.2 Recuperar arquivos gerados ausentes do template Reflex 0.9.12 usado pelo usuário; verificar build de produção e resposta HTTP 200 da aplicação.

A tarefa 3.1 permanece pendente somente na inspeção visual desktop/celular: testes e compilação passaram; acesso ao Chrome foi rejeitado pela revisão automática de permissões. Ver verification.md.
