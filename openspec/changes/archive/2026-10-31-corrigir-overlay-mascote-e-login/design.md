# Design

## Context

Reflex 0.9.11 e extra_app_wraps global já existem. `.mascote-app` atualmente
subtrai 208/160 px da viewport e cria overflow auto. O login foi reduzido para
acomodar essa faixa. Dois `reflex run` do projeto estão em 3000/3001; frontend
de desenvolvimento tenta ws://localhost:8000/_event sem listener em 8000.
A origem Xano válida está no .env, mas não no ambiente inicial desses processos.
Autenticação direta no Xano e confirmação da identidade retornaram 200.

## Goals / Non-Goals

**Goals:** overlay real, páginas com geometria original, login local funcional.
**Non-Goals:** chat, alteração de senha/conta, mock no servidor de uso do usuário.

## Decisions

- O wrapper passa a Fragment: mascote fixed é irmã do outlet; não haverá container
  com altura/overflow próprios. Variável de tamanho vai para o próprio botão.
- Remover min-height percentual do wrapper e restaurar altura desktop do painel
  `min(92vh,708px)`. Fundo de login continua cobrindo a viewport.
- Preservar um registro global: duplicar em páginas violaria unicidade e manutenção.
- Criar script shell local que carrega o .env do projeto e inicia Reflex produção
  single-port na porta 3001 por padrão, com log. Corrigir a causa operacional do
  login; não relaxar checks de identidade ou registrar payloads.
- Nos testes de overlay, comparar geometria com e sem o botão: nenhuma mudança de
  posição/tamanho de conteúdo ou altura de documento. Fazer QA do login real sem
  screenshots da conta autenticada nem dados pessoais nos artefatos.

## Risks / Trade-offs

- [Overlay pode cruzar conteúdo durante rolagem] → manter hitbox do botão e testar
  ações essenciais acessíveis; não reintroduzir faixa nem redimensionar páginas.
- [Instâncias simultâneas recompilam .web compartilhado] → encerrar somente os dois
  launchers identificados por PID/cwd e manter uma instância local completa.

## Migration Plan

Executar launcher com .env existente e usar endereço do log. Rollback visual não
exige migração de dados. Não mudar ou expor senha/tokens.
