# auth-decoration Specification

## Purpose

Padronizar o acabamento dos cards de login e cadastro com LED de perímetro e sombra verde sem interferir na autenticação.

## Requirements

### Requirement: LED e sombra na autenticação
Os cards de login e cadastro SHALL apresentar LED verde de perímetro e sombra verde, respeitando bordas arredondadas e preferência de movimento reduzido.

#### Scenario: Abrir autenticação
- **WHEN** o visitante acessa login ou cadastro
- **THEN** o card exibe LED e sombra verde sem bloquear os campos e ações
