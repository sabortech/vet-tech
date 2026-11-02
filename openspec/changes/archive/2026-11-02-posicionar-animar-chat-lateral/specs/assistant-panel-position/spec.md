# Spec Delta

## Purpose
Manter a mascote acessível durante a conversa e suavizar a abertura e o fechamento do assistente em todas as telas.

## ADDED Requirements

### Requirement: Painel adjacente e animado
O chat SHALL aparecer à esquerda da mascote em desktop e acima em telas estreitas, mantendo o botão visível e acionável. SHALL animar abertura e fechamento, sem transição para preferência de movimento reduzido, e permitir fechamento pela mascote, controles e Escape.

#### Scenario: Alternar o painel
- **WHEN** a pessoa clica na mascote para abrir e fechar
- **THEN** o painel transiciona suavemente sem cobrir a mascote, e uma nova abertura funciona normalmente

#### Scenario: Celular e movimento reduzido
- **WHEN** o painel abre em celular com movimento reduzido
- **THEN** o botão permanece acessível abaixo, o envio permanece dentro da tela e não ocorre transição
