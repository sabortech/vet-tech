# Design

## Context
O projeto centraliza cores em assets/vet_tech.css e mantém a preferência em vet_tech_theme. O provedor Reflex usa outra preferência e aplica classes a .radix-themes; essa divergência permite paleta escura em superfícies claras. Componentes clínicos usam principalmente estilos padrão Radix.

## Goals / Non-Goals
Centralizar a correção para atender todas as telas e portais, conservando a hierarquia e identidade verde. Não alterar autenticação, regras clínicas ou estrutura de páginas.

## Decisions
- Reutilizar tokens globais, escurecendo texto secundário e ações no tema claro. Evitar substituições individuais em todas as telas.
- Aplicar cores de texto e paleta semântica no escopo Radix com base no tema do documento; preservar variantes de botões.
- Sincronizar classes de aparência dos contêineres Radix com a preferência existente, inclusive portais criados após carregamento. Reutilizar o observer existente, com escritas condicionais para evitar ciclos.
- Validar em navegador claro/escuro e com preferência Reflex conflitante, usando componentes representativos de telas autenticadas sem requerer credenciais reais.

## Risks / Trade-offs
- Estilos do Radix podem sobrepor os tokens → verificar estilos computados em campos, tabelas, seletores e diálogos.
- Alterações de classes podem causar ciclos no observer → alterar classes somente quando diferirem.

## Migration Plan
Recompilar e reiniciar a instância local em produção. Reversão pelos arquivos alterados; nenhuma migração de dados.
