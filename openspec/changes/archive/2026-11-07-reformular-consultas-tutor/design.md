# Design

## Context
`tutor_consultations` concentra lista, detalhe e bloco auxiliar. `consultation_detail` apresenta campos em texto e usa `record_card` genérico. Estado atual já carrega reservas e histórico por pet e exporta PDF mediante critérios próprios. Ver proposal.md.

## Goals / Non-Goals
Reorganizar apresentação sem modificar agendamento, fonte autorizada ou critérios de publicação/exportação. Nenhum diagnóstico ou estado será inferido a partir de datas ou apresentação.

## Decisions
- Reutilizar cabeçalho compartilhado, shell dividido/LED, disco translúcido e campos título/valor existentes. Símbolo calendar-days identifica consulta; sem imagem nova ou serviço externo.
- Lista distingue status conhecidos com rótulos portugueses, preserva valor legado/desconhecido, mostra data, motivo e profissional e mantém acesso a prontuário somente finalizada/legado conforme regra atual.
- Detalhe usa um único cartão dividido com número/status, grade de datas/profissional e narrativas pre-wrap à esquerda; cenário sorteado da consulta e símbolo de prancheta translúcido à direita. Voltar e PDF elegível ficam no cabeçalho junto ao pet e Atualizar, sem toolbar separada ou espaço para feedback vazio. Dados ausentes mostram Não informado, e nome do veterinário prevalece sobre ID quando disponível.
- Conforme revisão solicitada, Vacinas e Medicamentos reutilizam seus cartões completos de aba com show_origin=False. Doenças reutiliza o mesmo cartão com modo de diagnóstico pontual, exibindo data de diagnóstico e observações sem substituir pelo consolidado do pet. Exames usa cartão dividido com test-tubes em disco translúcido. Todos permanecem sem botão recursivo.
- Preservar handlers e estruturas de dados; agrupar permissões/auditoria em superfície própria, sem carregamento automático extra.
- CSS consultation-* limita impacto e adapta grade ao celular; complementos ocupam uma coluna para acomodar os mesmos painéis ilustrados das abas.

## Risks / Trade-offs
- Perda de campos clínicos → manter todos os campos anteriores e conferir dados sintéticos por categoria.
- Textos extensos/zoom → quebra de palavras, grades minmax e verificação em 390/1440 px, dois temas.
- Regressão PDF ou troca de contexto → manter eventos e guardas, rodar regressões existentes e navegação real.

## Migration Plan

Revisão solicitada: Exames passa a usar cartão dividido com test-tubes em disco
translúcido. `fundinho.jpeg` será otimizado e incluído no catálogo junto aos três
cenários existentes. O sorteio por sessão/pet/grupo/registro abrange vacinas,
medicamentos, doenças, diagnósticos, exames e consultas; mantém escolhas após
reordenação/atualização e prioriza variedade até esgotar os quatro fundos.
Consultas de histórico e listagem reutilizam a escolha do mesmo ID.
Compilar conjunto completo e verificar em backend sintético isolado. Atualizar frontends ativos completos sem copiar módulos individuais; reiniciar caches de módulos se necessário. Reversão restrita à composição e estilos, sem migração de dados.
