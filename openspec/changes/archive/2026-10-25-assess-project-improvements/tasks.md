# Tasks

## 1. Fundação e configuração segura

- [x] 1.1 Reutilizar a estrutura existente em `pages/`, `components/`, `features/` e `shared/`, corrigindo as premissas de ausência de código da proposta e do design; registrar a responsabilidade de cada módulo e a sobreposição com `planejar-core-prontuario`, verificando coerência com `docs/architecture.md` e o roadmap sem declarar funcionalidades futuras como prontas.
- [x] 1.2 Centralizar a configuração do cliente Xano, exigir `XANO_API_BASE_URL` explicitamente e remover o fallback de ambiente remoto; verificar com testes de configuração ausente, vazia e válida, sem chamadas externas ou exposição de valores sensíveis.
- [x] 1.3 Validar a configuração no início da aplicação, preservando imports para testes isolados; documentar instalação, variáveis sem credenciais, execução em produção e verificações locais no README, e conferir inicialização válida e erro acionável quando faltar configuração.
- [x] 1.4 Cobrir o cliente compartilhado com transporte HTTP simulado para sucesso, autenticação, JSON, multipart, timeout e erros do backend; verificar que mensagens e logs não revelam token, senha nem prontuário.

## 2. Contrato de domínio e integridade

- [x] 2.1 Confrontar DER e XanoScript existentes para tutor/pet, espécie/raça, consulta e exame; documentar divergências, contratos de entrada/saída e plano de migração dos dados existentes, verificando que a migração preserva histórico e não pressupõe base vazia.
- [x] 2.2 Garantir no backend pet com um tutor responsável e raça pertencente à espécie informada, reutilizando as validações de `pet/create_POST.xs`; verificar por testes de integração com dados sintéticos raça incompatível, espécie inexistente, tentativa de forjar tutor e listagem por outro tutor.
- [x] 2.3 Garantir no contrato e na persistência de consulta os vínculos obrigatórios com pet e veterinário existentes, rejeitando ausência ou referência inválida sem escrita parcial; atualizar DER/documentação e verificar casos positivos e negativos em ambiente de desenvolvimento.
- [x] 2.4 Garantir exame sempre associado a um pet, aceitando consulta ausente e rejeitando consulta de outro pet; manter o formato de arquivo já existente sem introduzir exportação ou novo modelo de anexos, atualizar documentação e verificar os três cenários com dados sintéticos.

## 3. Identidade e autorização no backend

- [x] 3.1 Definir e documentar o contrato autenticado de identidade veterinária em conjunto com a futura `unificar-acesso-perfis`, resolvendo antes da implementação a política de e-mail com dois perfis registrada no roadmap; verificar que o backend determina a identidade e que nenhum perfil fornecido pelo cliente concede acesso.
- [x] 3.2 Implementar uma política reutilizável Xano de acesso ao prontuário, verificando identidade, pet, ação solicitada e autorização ativa em cada chamada; testar autorização ativa, inexistente, revogada, pet diferente e identidade forjada por chamadas diretas ao backend.
- [x] 3.3 Implementar concessão, manutenção e revogação por tutor proprietário do pet, sem acesso concedido por vínculo com clínica; documentar os endpoints e verificar outro tutor, múltiplos veterinários e revogação seguida imediatamente de leitura, edição e exportação negadas.

## 4. Auditoria inseparável da operação

- [x] 4.1 Adequar `log_acesso` para pet, veterinário, ação e timestamp com horário obrigatório, documentando migração e limites dos registros antigos de tipo date; conferir consistência entre tabela, DER e contrato com dados sintéticos.
- [x] 4.2 Integrar a política e a auditoria aos pontos protegidos de leitura, edição e exportação, sem construir geração de PDF nesta change; verificar exatamente um log por operação bem-sucedida, nenhum log de sucesso para negativa e falha explícita sem escrita parcial quando a auditoria falhar.
- [x] 4.3 Impedir alteração e exclusão dos logs por usuários da aplicação nas APIs e permissões do backend; documentar a proteção e verificar tentativas autenticadas de adulteração preservando o registro original.

## 5. Verificação integrada da fundação

- [x] 5.1 Disponibilizar comando reproduzível para os testes de configuração, invariantes, autorização e auditoria, separando testes unitários de integrações Xano e documentando preparo/limpeza de dados sintéticos; verificar execução sem dados pessoais reais e sem dependência de produção.
- [x] 5.2 Executar a suíte unitária, compilar com `reflex compile --dry`, validar esta change com `openspec validate assess-project-improvements --strict` e conferir `git diff --check`; registrar comandos, resultados e limitações em `verification.md`, sem tratar teste de frontend como prova de autorização backend.
- [x] 5.3 Executar integração em ambiente Xano de desenvolvimento cobrindo dois tutores, múltiplos pets e veterinários, revogação imediata, invariantes e auditoria imutável; registrar evidências e reconciliar a cobertura com o roadmap antes de solicitar aprovação para arquivamento.
