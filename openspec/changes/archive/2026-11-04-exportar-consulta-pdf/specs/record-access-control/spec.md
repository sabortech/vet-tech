## ADDED Requirements

### Requirement: Exportação do tutor revalida proprietário e publicação no backend
O backend SHALL validar identidade de tutor autenticada, propriedade atual do pet, vínculo da consulta ao mesmo pet e status explícito finalizada a cada exportação e a cada retry. IDs, perfil, status ou campos clínicos enviados pelo cliente SHALL NOT substituir esses controles. SHALL devolver somente dados autorizados publicados e mínimos para o documento; não SHALL confirmar existência de consulta alheia em mensagens. Esta V1 SHALL NOT habilitar exportação veterinária nem ampliar consentimentos.

#### Scenario: Consulta de terceiro ou ID forjado
- **GIVEN** o solicitante não é dono do pet ou envia consulta de outro pet
- **WHEN** tenta exportar alterando identificadores ou perfil
- **THEN** o backend nega, não devolve dados ou PDF e não gera registro que declare exportação autorizada

#### Scenario: Revalidação no retry
- **GIVEN** houve uma tentativa anteriormente autorizada
- **WHEN** uma repetição chega sem sessão válida, sem propriedade vigente ou com consulta inelegível
- **THEN** o backend nega sem reaproveitar autorização antiga ou expor dados

### Requirement: Exportação autorizada possui auditoria imutável e idempotente
O backend SHALL registrar `exportar_consulta` com pet, consulta, tutor ator e timestamp na trilha imutável existente antes de liberar os dados da exportação. A identificação do veterinário responsável, quando presente, SHALL ser distinta do tutor que executa a ação. Falha da auditoria SHALL impedir liberação de dados e PDF. A auditoria SHALL representar a liberação autorizada para emissão, sem afirmar que o arquivo foi salvo pelo navegador. Repetições da mesma operação SHALL produzir no máximo um registro; nova exportação explícita SHALL ter nova operação. Uma chave de operação SHALL ficar vinculada a ator, pet e consulta, sem permitir reutilização para outro alvo. Usuários SHALL NOT editar ou excluir esses registros.

#### Scenario: Auditoria confirmada
- **GIVEN** a exportação da consulta finalizada é autorizada
- **WHEN** o backend libera os dados para emissão
- **THEN** existe exatamente um registro exportar_consulta associado ao tutor ator, pet, consulta e horário

#### Scenario: Auditoria indisponível
- **GIVEN** as validações de propriedade e publicação passaram
- **WHEN** a gravação da auditoria falha
- **THEN** a operação falha sem liberar dados para exportação ou entregar PDF

#### Scenario: Retry concorrente ou resposta perdida
- **GIVEN** duas solicitações representam a mesma operação do mesmo tutor para a mesma consulta
- **WHEN** chegam simultaneamente ou após perda de resposta
- **THEN** as verificações de acesso são repetidas e há somente um registro de liberação autorizada

#### Scenario: Reutilização de chave para outro alvo
- **GIVEN** uma chave já foi usada para uma consulta
- **WHEN** a mesma chave é enviada para outro pet ou consulta pelo mesmo ator
- **THEN** o backend rejeita a reutilização sem liberar dados de outro alvo

#### Scenario: Tentativa negada e adulteração
- **GIVEN** o acesso foi negado ou um log autorizado já existe
- **WHEN** o cliente tenta declarar sucesso ou alterar/excluir o log
- **THEN** não é criado sucesso falso e o registro existente permanece imutável
