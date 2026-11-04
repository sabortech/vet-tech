# Spec Delta

## ADDED Requirements

### Requirement: Card de identidade profissional na sidebar médica
O sistema SHALL apresentar nome, avatar de iniciais, indicação de perfil médico, CRMV/UF reais da própria conta e logout em card consistente com o design existente, nos temas claro/escuro e drawer móvel. A sidebar compacta SHALL preservar avatar e saída acessível sem overflow. Destinos e proteção de saída em Configurações SHALL permanecer iguais. SHALL NOT declarar verificação externa do registro.

#### Scenario: Carregar registro profissional
- **GIVEN** sessão veterinária válida
- **WHEN** o card é montado
- **THEN** obtém CRMV/UF pela leitura autenticada da própria conta, sem bloquear navegação, e reutiliza metadados confirmados da sessão

#### Scenario: Troca de sessão ou perfil
- **GIVEN** uma leitura está em andamento
- **WHEN** a sessão, identidade, token ou perfil muda
- **THEN** a resposta antiga não restaura metadados e os dados profissionais são limpos ao sair

#### Scenario: Ausência ou falha
- **WHEN** o registro não está preenchido ou a leitura falha
- **THEN** apresenta informação honesta e permite repetir em caso de falha, sem inventar CRMV/UF
