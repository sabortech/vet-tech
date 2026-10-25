# Proposal

## Why

Cada troca entre Vacinas, Medicamentos, Doenças e Consultas executa quatro leituras sequenciais no Xano. A espera ocupa o evento da sessão e transmite a sensação de que os cliques não funcionam; selecionar o pet deve preparar os dados uma vez e manter a navegação responsiva, com loading explícito.

## What Changes

- Carregar dados básicos e o conjunto clínico do tutor ao selecionar ou trocar o pet, em background, sem manter o bloqueio do estado durante HTTP.
- Reutilizar histórico e consultas nas seções do mesmo pet, sem novas chamadas enquanto a cópia da sessão estiver válida por 60 segundos.
- Agrupar o carregamento inicial com consultas independentes concorrentes aos contratos existentes; não criar endpoint agregado nesta etapa. Autorizações e auditoria ficam sob demanda, sem download de anexos.
- Apresentar spinner/skeleton com texto acessível durante a espera, distinguir lista vazia de falha e oferecer nova tentativa e atualização manual.
- Invalidar dados após operações relacionadas, troca de seleção, logout, expiração ou negação de acesso; descartar respostas atrasadas.
- Verificar quantidade de chamadas, navegação durante espera e isolamento entre pets com testes determinísticos e navegador.

## Capabilities

### New Capabilities

- `pet-clinical-loading`: carregamento clínico por seleção de pet, reutilização temporária na sessão, loading acessível e recuperação de falhas sem bloquear navegação.

### Modified Capabilities

Nenhuma. A capacidade complementa `pet-management` e `authenticated-navigation`, preservando seleção explícita, propriedade e descarte de respostas antigas. Reutiliza os contratos implementados pela change concluída `fluxo-consultas-prontuario`, ainda não sincronizada com as specs principais.

## Impact

- Reflex: `features/auth/state.py`, `features/clinical/state.py`, `pages/profile.py`, `components/clinical.py` e componentes de detalhes do pet. Reutilizar o padrão de background de `features/settings/state.py`, sem reorganização ampla de módulos.
- Integração: contratos Xano existentes de detalhe do pet, histórico, consultas, acessos e auditoria. Sem mudanças de schema, autenticação ou publicação remota.
- Privacidade: dados de saúde e dados pessoais permanecem no estado da sessão do servidor, sem cache global, LocalStorage ou inclusão em logs. Seleção não comprova propriedade; Xano continua autorizando cada requisição. Não ampliar cache para leitura veterinária de prontuário, que exige consentimento e auditoria próprios.
- RN01–RN08/RN05 e RF de prontuário permanecem aplicáveis. Não modificar semântica de auditoria nem notificações automáticas.
- Escopo: área do tutor por pet; agenda e edição de atendimento veterinário, login, preferências e ajuste de infraestrutura não integram esta otimização.
