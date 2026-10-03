# Proposta

## Por quê

O repositório já documenta o domínio, as regras de privacidade e a arquitetura pretendida do VetTech, mas ainda não possui uma implementação funcional, modelo Xano, aplicação Reflex, testes ou uma estratégia operacional verificável. Uma fundação técnica explícita é necessária antes de desenvolver módulos de negócio, para evitar divergências entre o domínio documentado, as autorizações do prontuário e as futuras camadas de frontend e backend.

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

Nenhuma. O projeto ainda não possui especificações de capacidade existentes; as regras atuais estão documentadas em `docs/`.

## Impacto

- **Código e estrutura:** criação da aplicação Reflex, módulos de domínio, configuração de ambiente e testes automatizados; atualmente esses elementos ainda não existem no repositório.
- **Backend e dados:** definição do contrato de integração com Xano e do modelo das entidades descritas em `docs/domain-model.md`, incluindo vínculos obrigatórios e relacionamentos opcionais.
- **Segurança:** dados de tutores e prontuários de saúde animal exigem credenciais em variáveis de ambiente, autorização no backend, revogação imediata e logs imutáveis de leitura, edição e exportação.
- **Operação:** será necessário documentar como executar, testar e validar a aplicação, sem introduzir dependências ou tecnologias alternativas à arquitetura registrada.
