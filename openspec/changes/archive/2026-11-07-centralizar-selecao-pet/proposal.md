# Proposal

## Why
A lista de pets se repete em todas as seções clínicas quando não há seleção. Centralizar a escolha em Meus Pets e orientar o tutor com uma tela ilustrada comum.

## What Changes
- Substituir lista por tela padrão nas cinco seções clínicas sem contexto de pet.
- Encaminhar seleção, Mudar pet e Voltar à lista para Meus Pets.
- Preservar carregamento, erros, autorização e descarte de respostas antigas.

## Capabilities
### New Capabilities
Nenhuma.
### Modified Capabilities
- `authenticated-navigation`: seleção centralizada em Meus Pets e estado comum sem pet.

## Impact
Componentes de perfil/pets, eventos de troca/fechamento, CSS e testes de seleção. Sem alteração de APIs ou dependências. Dashboard global e Configurações permanecem disponíveis.
