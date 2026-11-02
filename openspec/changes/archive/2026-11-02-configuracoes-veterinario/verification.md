# Verificação — Configurações do veterinário

## Entrega

Configurações integrada ao menu médico, reutilizando a página e as abas do tutor.
Minha conta médica tem nome/telefone editáveis e e-mail/CRMV/UF bloqueados;
Segurança e Preferências usam os mesmos componentes, estilos e comportamentos.
O menu médico permite retornar a Horários/Consultas com descarte protegido.

## Backend publicado

A prévia, executada com acesso de rede permitido, confirmou somente três novos
endpoints no workspace 167758: GET/PATCH veterinario/account e POST
veterinario/password. Publicação restrita, transacional, sem --force, tabelas,
records ou env: três documentos enviados e GUIDs sincronizados aos arquivos.
Os contratos existentes do tutor e outros endpoints pendentes não foram enviados.
O parser oficial XanoScript retornou zero erros para os três documentos.

`tests/integration/veterinarian_settings_live.py` verificou no Xano publicado:
- Leitura da própria conta e projeção mínima sem credenciais.
- Rejeição sem token, token inválido e token de tutor nas três operações médicas.
- Token médico continua rejeitado na conta de tutor.
- Allowlist de escrita ignora IDs e campos profissionais/e-mail/senha forjados;
  outra conta médica permanece igual e entrada inválida não causa escrita parcial.
- Senha atual errada/confirmação divergente rejeitadas; senha nova, incluindo
  espaços, aceita exatamente; senha antiga rejeitada e outra conta preservada.

Somente fixtures com environment=development, synthetic=true e e-mails
@example.invalid foram utilizadas. Nome/telefone da fixture foram restaurados;
a senha da fixture vet_a foi rotacionada e sua credencial atualizada imediatamente
no arquivo ignorado, com permissão 600. Nenhuma conta real foi alterada. Resultado
sanitizado em evidence/backend-live.json. Nenhum prontuário foi lido ou modificado.

## Verificação local e navegador real

- 237 testes unitários passaram com `python -m unittest discover -s tests/unit`.
- Reflex compile --dry e build de produção passaram para todas as páginas.
- Casos novos: endpoint por perfil; campos permitidos; identidade do menu após
  salvar; senha médica/sessão limpa; contexto trocado por perfil, identidade ou
  geração mesmo com token reutilizado; guard de destino e retorno à agenda.
- `tests/integration/veterinarian_settings_browser.py` usou a aplicação real em
  localhost:3000 com a fixture vet_b: leitura, CRMV/e-mail bloqueados, cancelar,
  salvar/restaurar nome, continuar edição, descartar e navegar a Consultas,
  senha inválida sem logout, limpeza de senha, tema e expansão do menu.
- Chromium 1440×1000 e 390×844: desktop, modo escuro, preferências e drawer móvel
  sem overflow; retorno a Horários e fechamento do drawer confirmados.
- Contexto separado de tutor confirmou CPF mascarado/endereço e menu anteriores.
  Nenhuma exceção JavaScript. Evidências sanitizadas e capturas em evidence/.
- OpenSpec estrito, specs principais e git diff --check validados.

## Reprodução

No ambiente com Playwright, executar o roteiro browser com --chromium e --output.
O roteiro live exige as fixtures de desenvolvimento existentes e rotaciona somente
a senha sintética; executar os dois em sequência para respeitar a cota do Xano.
Não substituir fixtures por credenciais reais. O menu, APIs e tela médica já estão
ativos; o endpoint de foto da agenda de outra change permanece fora desta entrega.
