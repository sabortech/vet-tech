# Proposta

## Por quê

O repositório já possui aplicação Reflex, cadastro/login de tutor, cadastro e listagem de pets, cliente Xano, tabelas XanoScript e testes. Faltam configuração obrigatória sem fallback remoto, integridade dos vínculos clínicos, identidade veterinária autenticada, autorização e auditoria imutável. A fundação deve completar essas lacunas reutilizando o código existente.

## O que muda

- Estabelecer uma fundação executável do projeto, respeitando Python com Reflex no frontend e Xano como backend/banco de dados.
- Definir a estrutura mínima de configuração, execução e dependências para desenvolvimento local sem expor credenciais.
- Transformar as entidades e vínculos centrais documentados em um contrato técnico rastreável para a API e o modelo Xano.
- Definir uma camada inicial de autenticação, autorização por tutor e auditoria para que módulos que lidam com prontuários não contornem essas regras.
- Criar uma estratégia de testes verificável para invariantes do domínio, autorização, auditoria e validações de relacionamentos.
- Registrar critérios de evolução incremental para os módulos de cadastro, prontuário, permissões e notificações.

## Capacidades

### Novas capacidades

- `project-foundation`: estrutura inicial executável, configuração segura, contrato de domínio, verificações e estratégia de testes que sustentam o desenvolvimento do VetTech.
- `record-access-control`: autenticação, autorização explícita do tutor para acesso veterinário ao prontuário e auditoria das operações sensíveis.

### Capacidades modificadas

Nenhuma alteração dos contratos visuais ou de cadastro nesta change. Já existem capacidades em `openspec/specs/`; os controles de prontuário serão reutilizados nas entregas do roadmap `planejar-core-prontuario`.

## Impacto

- **Código e estrutura:** evolução da aplicação existente, configuração em `shared/`, testes de transporte e controles de backend; seguir a organização gradual de `docs/architecture.md`.
- **Backend e dados:** definição do contrato de integração com Xano e do modelo das entidades descritas em `docs/domain-model.md`, incluindo vínculos obrigatórios e relacionamentos opcionais.
- **Segurança:** dados de tutores e prontuários de saúde animal exigem credenciais em variáveis de ambiente, autorização no backend, revogação imediata e logs imutáveis de leitura, edição e exportação.
- **Operação:** será necessário documentar como executar, testar e validar a aplicação, sem introduzir dependências ou tecnologias alternativas à arquitetura registrada.
