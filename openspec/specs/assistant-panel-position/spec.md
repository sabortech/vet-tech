# assistant-panel-position Specification

## Purpose
Manter a mascote acessível durante a conversa e suavizar a abertura e o fechamento do assistente em todas as telas.

## Requirements

### Requirement: Painel adjacente e animado
O chat SHALL aparecer acima da mascote em todas as telas, com fundo da página escurecido enquanto aberto, mantendo o botão visível e acionável. SHALL animar abertura e fechamento, sem transição para preferência de movimento reduzido, e permitir fechamento pela mascote, controles, clique no fundo escuro e Escape.

#### Scenario: Alternar o painel
- **WHEN** a pessoa clica na mascote para abrir e fechar
- **THEN** o painel transiciona suavemente acima da mascote sem cobri-la, e uma nova abertura funciona normalmente

#### Scenario: Celular e movimento reduzido
- **WHEN** o painel abre em celular com movimento reduzido
- **THEN** o botão permanece acessível abaixo, o envio permanece dentro da tela e não ocorre transição
