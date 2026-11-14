# Verificação — 14/11/2026

- Compilação Reflex `compile --dry`: passou.
- Python: 39 testes relacionados passaram, incluindo descarte de resposta após reset e 3 testes de conversa direta.
- JavaScript: suítes direct_messages e cinco regressões support_* passaram.
- Navegador: diretório com busca explícita, pop-up, caixa do tutor, nomes, envio, edição, exclusão e roteamento privado passaram nos dois perfis; regressão de opções de mensagens do atendimento passou.
- OpenSpec estrito: passou.
- Publicação Xano transacional seletiva: somente direct_conversation, Direct/operate e POST tutor/conversas + veterinario/conversas. GUIDs sincronizados. Nenhum registro importado e nenhuma alteração em Support/operate.
- Smoke real somente com contas qa-clinical existentes: diretório mínimo, negação de busca/início ao tutor, par único em início concorrente, envio idempotente, isolamento de outro tutor e outro médico em leitura/escrita/lista, leitura, resposta, edição, exclusão com auditoria privada e reabertura passaram.
- O primeiro lote esbarrou no rate limit do plano; a repetição espaçada passou integralmente. Evidência detalhada fica no ledger privado `.venv/clinical-smoke/pdf-export-local/direct-results.json`, sem copiar credenciais.
- JS/CSS sincronizados em `.web/public` e `.web/styles`; imagens de evidência usam somente dados simulados.

## Extensão: início pelo tutor e mascote
40 testes Python, testes JavaScript do domínio, compilação e navegador passaram. Função Direct/operate atualizada seletivamente. Smoke real sintético confirmou diretório de veterinários, início pelo tutor e mesmo par nos dois sentidos, além das verificações de isolamento, leitura e mutação. Imagem espreitando.webp carregada e capturada nos dois seletores. Assets sincronizados novamente.
