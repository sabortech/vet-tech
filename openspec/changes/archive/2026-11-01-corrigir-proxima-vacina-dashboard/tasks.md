## 1. Reproduzir a divergência

- [x] 1.1 Comparar um registro publicado de vacina com a resposta autenticada do Dashboard para o mesmo pet, verificando `pet_id`, `data_aplicacao`, `data_prox_dose`, fuso e fonte do endpoint em uso; registrar a causa com evidência sanitizada. Usar dados sintéticos para escritas e não alterar o cadastro do usuário para reproduzir.
- [x] 1.2 Seguir a resposta pela projeção `project_pet` e pelos cartões geral/individual; conferir também ausência de chaves em `proxima_vacina` e documentar em qual camada o valor desaparece.
- [x] 1.3 Mapear entrada, payload, tipo Xano, resposta e exibição das datas de nascimento, vacinas, atendimento, medicamentos, exames, agenda e auditoria; comparar representação real e identificar inversões, deslocamentos de dia ou rótulos americanos.
- [x] 1.4 Registrar a cobertura dos demais dados cadastrados no resumo (medicamentos, doenças, exames e consultas legadas), distinguindo escopo atual de defeito; não implementar novos cartões como consequência automática do inventário.

## 2. Corrigir o percurso confirmado

- [x] 2.1 Criar uma regressão que falhe para a divergência reproduzida e aplicar a correção mínima na consulta, normalização, projeção ou renderização responsável, preservando o layout e a regra de próxima dose de hoje ou futura.
- [x] 2.2 Verificar e corrigir, se necessário, o estado sem próxima dose: mensagem legível nos dois cartões, sem data inventada, sem apresentar data ultrapassada como futura e sem converter erro de leitura em ausência de registros.
- [x] 2.3 Corrigir a ordenação confirmada da atividade recente usando valores de data antes de formatá-los em DD/MM/AAAA; demonstrar consulta recente antes de vacina antiga.
- [x] 2.4 Corrigir divergências de entrada/serialização/exibição identificadas no mapa: preservar ISO para datas civis, apresentação brasileira, timestamps/fuso de agenda e auditoria, validação estrita e ausência de conversão ambígua. Preservar tipos e dados persistidos.

## 3. Verificação e entrega

- [x] 3.1 Executar regressões de hoje/futuro/passado, ausência de próxima dose, ordenação de várias doses, representação de data recebida, histórico extenso e troca de pet/sessão; reutilizar `tests/unit/test_dashboard.py` e testar apenas as lacunas relevantes ao defeito.
- [x] 3.2 Executar os testes focados do Dashboard e do cliente clínico, `reflex compile --dry` e `openspec validate corrigir-proxima-vacina-dashboard --strict`.
- [x] 3.3 Verificar no navegador, com sessão de teste, nome/data da próxima vacina em “Todos os pets” e no pet individual, estado vazio e recuperação de falha; guardar resultados sanitizados e não marcar como comprovado um percurso não executado.
- [x] 3.4 Documentar a causa, os arquivos alterados e os resultados em verification.md. Se a causa depender da versão remota, preparar o endpoint corrigido e registrar a necessidade de publicação e sua validação sem considerar compilação local como comprovação remota.
- [x] 3.5 Testar ciclo de entrada → payload → resposta → exibição com 03/04/2026, datas com dia maior que 12, bissexto, data inválida, ausência, transição de dia e navegadores pt-BR/en-US; verificar que datas civis não mudam de dia e que instantes respeitam America/Sao_Paulo.
