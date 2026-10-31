# Proposal

## Why

A mascote precisa ficar um pouco menor e a iluminação deve chamar atenção apenas
na entrada da interação, permanecendo suave e estável depois.

## What Changes

- Reduzir o botão de 160 para 140 px no desktop e de 112 para 96 px no mobile.
- Executar duas piscadas verdes lentas em aproximadamente 4 s e manter LED aceso
  enquanto houver hover/foco; apagar na saída e reiniciar na próxima entrada.
- Preservar overlay global, animação local, pose feliz e movimento reduzido.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `floating-mascot`: tamanho e sequência finita de iluminação.

## Impact

CSS, documentação e teste de navegador. Sem alterar login, backend, dados
sensíveis, autorizações, auditoria, notificações ou chat.
