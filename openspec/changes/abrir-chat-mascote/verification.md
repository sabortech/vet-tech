# Verificação

- `reflex compile --dry`: compilação concluída.
- `openspec validate abrir-chat-mascote --strict`: válido.
- `node --check assets/support-chat.js`: válido.
- Playwright no app real em localhost:3000: desktop 1366x900, mobile 390x844 e viewport baixa 1366x650; backdrop, posição acima da mascote, Tab contido, restauração de foco, Esc, clique fora, minimizar, voltar, fechar, reabrir com histórico, texto seguro, chips e erro/retry sem duplicação passaram.
- Evidências locais: `output/chat-verification/desktop.png` e `mobile.png`.
- Instância existente na porta 3000 já carregou os assets recompilados; não foi necessário iniciar outro servidor ou reiniciar o backend para esta interação local.
- Orientações locais; sem IA, acesso a prontuário ou integração de atendimento humano.

Pose persistente: Playwright confirmou classe ativa, opacidade 1 da pose em V e glow .85 com ponteiro fora da mascote; fechamento remove o estado. Compilação, sintaxe JS e validação OpenSpec passaram novamente.

## Reinício, saudação e histórico
- Compilação Reflex e validação estrita OpenSpec passaram.
- Playwright no app real passou: reabertura limpa; histórico acessível com retorno; texto de usuário seguro; reset ao mudar os atributos de identidade; saudação personalizada com nome contendo caracteres HTML como texto; logout simulado; fechamento durante digitação seguido de nova conversa sem resposta antiga; desktop/mobile e foco preservados.
- A identidade foi simulada no bridge de apresentação durante o teste de navegador, sem login real ou chamada ao Xano. O JSX compilado confirma os atributos vinculados a `State.is_authenticated`, `identity_name`, `profile` e `identity_id`; nenhuma credencial foi publicada.
