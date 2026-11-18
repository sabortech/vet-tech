# Proposal

## Why

Tutores não têm uma área para conhecer pets disponíveis para adoção nem para concluir a adoção dentro do Vet Tech. A mudança oferece esse fluxo sem expor o prontuário completo antes da transferência de responsabilidade e sem criar consultas ao Xano por cartão ou seção clínica.

## What Changes

- Criar uma área autenticada de adoção, com cards alinhados à referência visual, resumo clínico autorizado, ação “Ver prontuário” e confirmação antes de adotar.
- Adicionar “Adoção” à navegação do tutor logo abaixo de “Meus Pets”.
- Introduzir um indicador de disponibilidade controlado no backend; a equipe somente o ativa após confirmar a autorização de publicação. Não será criada uma tela para anunciar pets nesta mudança.
- Expor uma listagem agregada para tutores autenticados com identificação do pet e um resumo clínico mínimo, sem notas livres, resultados textuais, anexos, microchip ou dados do tutor.
- Adotar mediante uma operação Xano autenticada que derive o novo tutor de `$auth.id`, transfira o vínculo do pet e retorne os dados necessários para atualizar o estado local sem nova leitura.
- Após a adoção, retirar o pet da lista de adoção, acrescentá-lo às listas locais de “Meus Pets” e “Mudar pet”, preservar seu histórico e revogar autorizações veterinárias anteriores.
- Disponibilizar, enquanto não houver ambiente Xano de desenvolvimento, um modo de demonstração local explicitamente ativado por configuração, com os seis perfis fictícios fornecidos, sem consultas nem gravações de adoção no Xano.

## Capabilities

### New Capabilities

- `pet-adoption`: descoberta autenticada de pets disponíveis, divulgação clínica limitada, confirmação e transferência segura de propriedade.

### Modified Capabilities

- `pet-management`: permitir a transferência de um pet elegível sem quebrar a regra de um único tutor responsável.
- `application-navigation`: incluir a entrada Adoção na posição definida para o menu do tutor.
- `authenticated-navigation`: registrar a área autenticada de adoção e a atualização coerente das listas de pets.
- `clinical-records`: definir o resumo clínico mínimo permitido durante a adoção, mantendo o prontuário completo somente para o tutor proprietário.
- `record-access-control`: delimitar a leitura de resumo de adoção a dados explicitamente autorizados e impedir que ela conceda acesso ao prontuário completo.

## Impact

- **Interface:** novo destino de adoção, integração com a sidebar existente, cards responsivos, visualização do resumo clínico e diálogo de confirmação.
- **Estado e integração:** novo carregamento único e explícito da lista agregada; adoção otimista após resposta válida, com invalidação por sessão e sem recarga automática.
- **Demonstração local:** ativação somente por variável de ambiente, identificação visual de que os perfis são fictícios e simulação em memória que não altera pets reais nem persiste no backend.
- **Xano:** campo de disponibilidade em `pet`, endpoint autenticado de listagem agregada e operação autenticada de adoção; filtros e projeções clínicas aplicados no backend.
- **Autorização e privacidade:** somente tutores autenticados podem consultar a lista; somente campos permitidos são projetados antes da adoção; o tutor de destino vem exclusivamente do token. A transferência revoga autorizações clínicas veterinárias anteriores e preserva registros e auditoria históricos.
- **Verificação:** testes unitários de navegação, resumo, confirmação, concorrência/erros e sincronização local; validação XanoScript; verificação de compilação Reflex e teste de navegador do fluxo.
- **Limite operacional:** a disponibilidade real será gerenciada por equipe no backend, após confirmação de consentimento do tutor atual. Não haverá tela de publicação/retirada de anúncios nem notificações automáticas nesta mudança. O modo demonstrativo não substitui nem valida a adoção persistente.
