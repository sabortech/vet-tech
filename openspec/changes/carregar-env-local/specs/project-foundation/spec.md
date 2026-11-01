## ADDED Requirements

### Requirement: Configuração local automática

O sistema SHALL carregar o `.env` da raiz do projeto ao iniciar, independentemente do diretório de execução, sem sobrescrever variáveis já definidas no ambiente e sem imprimir seus valores. A ausência do arquivo SHALL permitir configuração por ambiente; a validação Xano existente SHALL continuar obrigatória.

#### Scenario: Arquivo local disponível

- **WHEN** a aplicação inicia com `.env` válido na raiz e sem variável Xano no ambiente
- **THEN** a configuração Xano utiliza o valor do arquivo mesmo com outro diretório de execução

#### Scenario: Ambiente tem prioridade

- **WHEN** o arquivo e o ambiente definem a mesma variável
- **THEN** o valor do ambiente é preservado

#### Scenario: Arquivo ausente

- **WHEN** não existe `.env`
- **THEN** a aplicação utiliza as variáveis do ambiente e rejeita uma origem Xano ausente ou inválida
