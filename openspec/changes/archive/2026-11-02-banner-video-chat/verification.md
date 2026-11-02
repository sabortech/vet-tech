# Verificação

- Build de produção concluído e aplicação recarregada em localhost:3000.
- Chromium confirmou reprodução automática, silenciosa, inline e repetição real após os oito segundos do vídeo.
- Banner manteve a mesma posição durante rolagem de 30 mensagens e continuou visível no histórico.
- Temas claro/escuro e viewport móvel 390 × 844: banner dentro do painel e envio acessível.
- Fechar pausa o vídeo; reabrir retoma. Sem erros JavaScript e sem chamadas à IA.
- Evidências em evidence/results.json, light.png e dark.png.
- node --check e openspec validate --strict aprovados.
