## Context

A configuração compartilhada lê os.environ; apenas o script Bash importa o arquivo. Ver proposal.md para motivação.

## Goals / Non-Goals

Carregar configuração local antes da validação. Não alterar contratos Xano nem regras de domínio.

## Decisions

Usar python-dotenv em shared/config.py no import, com Path(__file__).resolve().parents[2] / '.env', encoding='utf-8-sig' e override=False. O caminho explícito evita dependência do diretório corrente; a biblioteca evita manter parser próprio. Carregar uma vez preserva a validação pura e exige reinício após editar o arquivo.

## Risks / Trade-offs

Variável externa vazia continua prioritária → validação existente informa erro. Arquivo ausente é permitido para implantação com ambiente injetado. Não registrar valores.

## Migration Plan

Instalar requirements.txt e reiniciar. Para reverter, remover o carregamento e voltar a exportar variáveis antes da inicialização.
