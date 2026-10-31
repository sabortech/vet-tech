# Proposal

## Why

O Vet Tech precisa de um ponto de entrada consistente para o futuro assistente. Esta entrega introduz somente a mascote flutuante, com movimento suave e sem comunicação de animação com o servidor.

## What Changes

- Botão global acessível com tartaruga inteira proporcional, rastreamento local provisório e sombra CSS.
- Pose feliz de frente com braços abaixado antes de passar o mouse, e ao passar o mouse as nadadeiras levantem fazendo a letra "V" e glow verde ao apontar, focar ou pressionar por toque; modo RGB opcional.
- Idle único de 160 px desktop, menor no mobile, offsets de 24 px e safe area; fundo do login cobre a viewport inteira.
- Evento público `vettech:mascote-click`, sem abrir interface.
- Assets transparentes com fallback, respeito a movimento reduzido e verificação de desempenho e navegação.

## Capabilities

### New Capabilities

Nenhuma nova capacidade nesta revisão.

### Modified Capabilities

- `floating-mascot`: preserva presença global e gancho; passa a usar imagem inteira proporcional, sombra CSS, tamanho maior e fundo completo no login.

## Impact

Altera o registro global em `vet_tech/vet_tech.py`; adiciona componente em `vet_tech/components/`, CSS/JS e imagens em `assets/`, além de verificação em navegador. Usa Reflex 0.9.11 e APIs nativas do navegador, sem dependências de runtime adicionais. Não acessa dados sensíveis, prontuário, autenticação, autorizações ou notificações; RF01–RF10 e RN01–RN24 permanecem inalterados. Chat fica para outra change.
