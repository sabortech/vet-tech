# Verificação das configurações

Os testes de backend devem ser executados exclusivamente no workspace de
desenvolvimento confirmado. Os endpoints são aditivos, publicados em conjunto
restrito de três documentos; não usar push integral de schemas antigos.
O inventário e o ambiente de referência estão em `record-foundation-verification.md`.

## Verificação local

```bash
.venv/bin/python -m unittest discover -s tests/unit
.venv/bin/reflex compile --dry
openspec validate adicionar-configuracoes-tutor --strict
```

## Integração real com fixtures

O harness `tests/integration/run_settings_live.py` exige o arquivo ignorado
`.env.foundation-fixtures.json`, com `environment=development`, `synthetic=true`,
origem HTTPS e credenciais de veterinário sintético já descritos na documentação
da fundação. Não imprime respostas pessoais, senhas ou tokens. As novas contas
ficam em `.env.settings-fixtures.json`, ignorado pelo Git e criado com permissão 600.

```bash
.venv/bin/python tests/integration/run_settings_live.py --phase prepare
.venv/bin/python tests/integration/run_settings_live.py --phase verify
```

Prepare cria dois tutores fictícios com e-mails `@example.invalid`, CPFs válidos
gerados e senhas aleatórias. Verify testa leituras da própria conta e bloqueio
sem token, token inválido e tokens de outros domínios, edição por allowlist,
campos protegidos, ausência de escrita parcial e troca de senha. Cria ainda um
usuário genérico sintético para testar a separação de identidades.
A senha alterada pertence somente à fixture. Não usar a conta do usuário como teste.
Os registros sintéticos permanecem no desenvolvimento como evidências.

Executar o harness e o navegador em sequência para respeitar a cota do Xano:
10 requisições por 20 segundos no ambiente observado. O harness espaça chamadas
em três segundos; qualquer HTTP 429 é uma falha explícita, sem retry automático.
Se uma chamada de troca de senha for confirmada antes de falhar uma etapa posterior,
o arquivo registra a nova senha antes de tentar outros logins. Se houver resultado
incerto de rede, reconciliar a fixture explicitamente em vez de repetir a escrita.

No navegador, verificar entrada, navegação, edição/Cancelamento/salvamento,
descarte/continuação, senha atual inválida, senha nova e redirecionamento para login.
Capturar Configurações nos temas claro e escuro em 1366, 1920, 768 e 390 px, menu
expandido/recolhido e gaveta móvel. Abrir selects de pets e diálogos nos dois temas.
Conferir tema em login e cadastro após logout e em primeiro paint com preferência
prévia. Testar também navegação por teclado e indisponibilidade de armazenamento.
Evidências sanitizadas ficam na change; mocks não comprovam autorização remota.

## Navegador automatizado

Com Playwright/Chromium disponíveis no ambiente, executar o roteiro sobre a
mesma instância que será usada pelo usuário (não reutilizar `.web` em servidores
simultâneos de portas diferentes):

```bash
NODE_PATH=/caminho/para/node_modules node tests/integration/settings_browser.cjs
```

`VETTECH_TEST_URL` permite indicar a origem local e `VETTECH_CHROMIUM_PATH` o
executável já instalado. O script lê somente a fixture sintética ignorada,
altera a senha do segundo tutor de teste e atualiza sua credencial nesse arquivo
após confirmação. Não usar valores reais ou outro arquivo de conta.

O roteiro `tests/integration/settings_visual.cjs` complementa a integração com
confirmação ao voltar no histórico, contraste dos campos bloqueados, capturas
responsivas e abertura do seletor de pets no tema escuro. Usa as mesmas variáveis
de ambiente e fixtures do roteiro principal.

`tests/integration/navigation_browser.cjs` mede três idas e voltas entre Meus Pets
e Configurações e verifica descarte real, continuação da edição e saída limpa de
Segurança/Preferências. Usa as mesmas fixtures sintéticas e variáveis de Chromium
já descritas. A medição local inclui clique e aparecimento do título, não garante
um SLA para redes ou dispositivos diferentes.
