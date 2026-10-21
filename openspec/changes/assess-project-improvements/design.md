# Design

## Context

O repositório contém visão de produto e domínio em `docs/`, aplicação Reflex,
APIs de tutor/pets, tabelas Xano e testes. Os contratos existentes, lacunas e
responsabilidades estão registrados em `docs/backend-foundation.md`.
A solução deve permanecer em Python com Reflex no frontend e Xano no backend e
deve tratar dados de tutores e de saúde animal como sensíveis. Ver `proposal.md`
para a motivação e `specs/` para os contratos comportamentais.

## Objetivos / Não objetivos

**Objetivos:**

- Criar uma base executável pequena, com configuração por ambiente e
  integração isolada com Xano.
- Representar as invariantes de domínio antes dos módulos de negócio.
- Centralizar a decisão de autorização no backend e tornar a auditoria
  inseparável das operações sensíveis.
- Permitir testes com dublês e dados sintéticos, sem depender de uma conta
  produtiva.

**Não objetivos:**

- Implementar todos os cadastros, telas ou fluxos clínicos nesta mudança.
- Criar pagamento, telemedicina, aplicativo nativo ou notificações completas.
- Substituir o Xano por outro banco, framework ou serviço de backend.
- Definir detalhes visuais do dashboard além do necessário para exercitar os
  fluxos protegidos.

## Decisões

### Separar configuração, domínio e integração

A configuração de ambiente ficará separada da lógica de domínio e do cliente
Xano. Valores obrigatórios serão lidos por uma única camada de configuração,
com validação explícita e mensagens sem revelar segredos. Isso facilita testes
locais e impede que telas ou regras de negócio acessem credenciais diretamente.

Alternativas consideradas: colocar URLs e tokens nas telas (rejeitado por
acoplamento e risco de exposição) ou adicionar outro backend local (rejeitado
por contrariar a arquitetura definida).

### Tratar autorização como política de backend

As operações de prontuário passarão por uma política única que verifica
identidade, vínculo com o pet, status ativo da autorização e ação solicitada.
O frontend poderá ocultar ações indisponíveis, mas não será responsável pela
decisão. A revogação será verificada em cada operação, evitando sessões que
continuem válidas após a retirada do consentimento.

Alternativas consideradas: autorização apenas na interface (rejeitada porque
pode ser contornada) e autorização permanente por clínica (rejeitada porque o
domínio exige consentimento individual do tutor).

### Registrar auditoria junto da operação protegida

Visualização, edição e exportação serão pontos explícitos do serviço de
prontuário. Após uma operação permitida, será criado um registro imutável com
pet, veterinário, ação e horário. A persistência da auditoria deverá usar
permissões distintas das operações comuns, e falhas de auditoria não poderão
ser convertidas em sucesso silencioso.

### Evoluir o modelo em fatias verificáveis

O contrato de entidades e invariantes será definido antes dos fluxos de
cadastro. Em seguida, a implementação deverá avançar por fatias: configuração
e execução, identidade e autorização, pet/tutor, prontuário, notificações e
exportação. Cada fatia terá testes de regra e integração com dados sintéticos.

## Riscos / Trade-offs

- **[Risco]** O Xano pode ter diferenças entre o modelo documentado e a API
  disponível → **Mitigação:** validar o contrato de integração com dados de
  desenvolvimento antes de acoplar telas.
- **[Risco]** Uma falha na criação do log pode deixar uma operação sensível
  sem rastreabilidade → **Mitigação:** tratar auditoria como parte obrigatória
  do fluxo e expor falhas explicitamente.
- **[Risco]** O escopo inicial crescer ao incluir todos os módulos do domínio →
  **Mitigação:** manter esta mudança limitada à fundação e aos controles de
  acesso; demais módulos entram em mudanças OpenSpec próprias.
- **[Risco]** Testes dependerem de serviços externos → **Mitigação:** separar
  testes unitários de domínio dos testes de contrato/integracão com Xano.

## Plano de migração

Há implementação existente e não se pode pressupor uma base vazia. Seguir o
inventário, a reconciliação de vínculos e o rollback de
`docs/backend-foundation.md`, preservando histórico e autoria. Não truncar
tabelas nem inventar referências. Testes locais não comprovam migração ou
publicação remota.

## Questões em aberto

- Os artefatos locais confirmam autenticação de tutor e APIs de pets. A
  identidade veterinária usa a política definida abaixo; não confundir login
  genérico de `user` com o domínio.
- O formato final de exportação do prontuário deve ser definido em uma mudança
  específica de exportação, sem alterar os requisitos de autorização desta
  proposta.

## Decisão de identidade e implementação local (2026-10-20)

O usuário autorizou resolver as decisões e continuar a aplicação. A mesma pessoa
pode ter e-mail em tutor e veterinário; a unicidade continua sendo por tabela.
O endpoint compartilhado `profiles/login` verifica as duas senhas de domínio
independentemente e emite tokens somente para as identidades comprovadas.
Senhas diferentes autenticam somente o perfil correspondente; senhas iguais
permitem retornar ambos. IDs iguais entre tabelas não são a mesma identidade.
Não criar tabela genérica ou unificar senhas automaticamente. Essa escolha
substitui a pendência de política de e-mail e orienta `unificar-acesso-perfis`.

Detalhes dos endpoints, índices, migração preservando histórico, evidências e
testes reproduzíveis em `docs/record-foundation-verification.md`. Os artefatos
locais não equivalem a publicação ou integração remota concluída.
