# Verificação da unificação dos menus do tutor

## Resultado

Meus Pets, Configurações e Prontuário usam `layout_com_menu` e o catálogo visual
de `components/sidebar.py`. A antiga composição de sidebar clínica foi retirada;
`components/navigation.py` mantém somente ações e modal por composição.

As rotas existentes foram preservadas. Links clínicos usam `secao` validada,
respeitam a seleção do pet, o cache e o guard de alterações pessoais. O drawer
móvel usa somente `NavigationState.drawer_open`, independentemente da preferência
desktop. Dashboard e Exames continuam indisponíveis.

## Verificações executadas

| Verificação | Resultado |
| --- | --- |
| `python -m unittest discover -s tests/unit` pela `.venv` | 152 testes aprovados |
| `reflex compile --dry` pela `.venv` | Compilação aprovada |
| `openspec validate unificar-menus-tutor --strict` | Aprovada |
| `git diff --check` | Sem erros de whitespace |
| Matriz visual de navegador | 36 casos aprovados |
| Fluxo de navegação em 1366 e 390 px | Aprovado |
| Regressão de loading em 1366 e 390 px | Aprovada |

Os sete testes unitários adicionais verificam o catálogo e os destinos,
query válida/inválida, ausência de seleção automática, reuso de cache e pet,
entrada sem sessão, bloqueio de destinos inválidos/externos, guard durante
gravação, destino exato e modal sem redirect. As suítes existentes também passaram.

## Referência e comparação visual

Foram capturadas oito referências anteriores de Meus Pets e Configurações em
1366×900, nos temas claro/escuro e modos expandido/rail. Elas estão em
`evidence/before-*.png` e `evidence/before-measurements.json`.

A versão unificada foi verificada nas três áreas, em 1366×900, 1024×768 e
390×844, nos dois temas e com a preferência desktop expandida/recolhida:
36 capturas em `evidence/after-*.png` e medidas em
`evidence/after-measurements.json`.

Os testes compararam largura, cor de fundo e texto da sidebar, bordas, fonte,
fundo/borda/altura do item ativo com a referência. Conferiram a ordem das nove
entradas, somente um `aria-current="page"`, centralização dos ícones no rail,
ausência de overflow horizontal e alcance das ações inferiores por rolagem.
No celular, o drawer aberto sempre usa a largura expandida e começa fechado,
mesmo com a preferência desktop expandida. Esc e backdrop fecham e devolvem foco
ao botão móvel. As imagens de Meus Pets claro e Prontuário claro também foram
inspecionadas visualmente.

## Navegação, segurança e acessibilidade

Com o aplicativo real compilado e o servidor HTTP sintético local:

- Vacinas abre sem pet e mantém a intenção até a seleção explícita; não consulta
  histórico antes dessa escolha.
- Durante uma carga clínica lenta, navegar para Medicamentos mantém o loading
  e não duplica chamadas. Renderizar/recolher o menu não faz HTTP.
- Novo pet abre com foco no primeiro campo; Cancelar e Esc fecham sem mudar URL,
  seção ou pet. Cancelar devolve foco ao acionador. O botão tem handler explícito
  para fechar o modal controlado, além da composição Radix.
- Configurações com rascunho pede confirmação; Continuar editando conserva os
  campos e devolve foco ao link pretendido. Descartar vai precisamente a
  `/prontuario?secao=vacinas`, sem desvio para Meus Pets.
- O drawer fecha depois de uma navegação concluída, sem backdrop residual;
  cancelar descarte conserva a tela atual.
- Voltar/avançar entre seções reaplica a seção da URL. A seleção e o cache
  continuam válidos: uma leitura de detalhe e duas clínicas por seleção no caso
  sintético, sem repetição por seção.
- O teste de loading existente foi adaptado de botões clínicos para links e
  para o drawer compartilhado. Passaram falha 503, Tentar novamente, espera por
  429 sem bloquear navegação, troca rápida A→B, leituras auxiliares e logout.
- Nenhum erro JavaScript foi capturado nesses percursos.

Na regressão de loading com 2 segundos artificiais por leitura, o loading surgiu
em 96 ms (desktop) e 77 ms (celular); a carga concluiu em 2645/2438 ms e a navegação
em cache levou 122/133 ms, incluindo a interação do menu. São tempos locais
controlados, sem promessa de desempenho no Xano remoto.

## Reprodução

```powershell
# Terminal do stub: somente dados sintéticos, bind em 127.0.0.1:9010.
.\.venv\Scripts\python.exe tests/integration/pet_loading_browser.py --serve

# Outro terminal, durante o teste controlado.
$env:XANO_API_BASE_URL = 'http://127.0.0.1:9010'
.\.venv\Scripts\reflex.exe run --env prod --single-port --frontend-port 3000

# Terminal de testes com acesso ao Chrome headless e ao servidor local.
.\.venv\Scripts\python.exe tests/integration/unified_menu_browser.py
.\.venv\Scripts\python.exe tests/integration/pet_loading_browser.py --browser
```

`unified_menu_browser.py --baseline` é o modo de captura de referência, executado
antes de alterar a aplicação. `--navigation-only` repete somente os percursos
funcionais. As fontes externas são bloqueadas no navegador de teste para que a
rede de terceiros não interfira; a fonte computada foi comparada com a mesma
condição nas referências.

## Limites e ambiente

As verificações de dados autenticados usaram exclusivamente HTTP sintético local,
com o frontend, WebSocket, estado e cliente HTTP reais do Reflex 0.9.11. Nenhuma
conta clínica real foi utilizada ou alterada, e nenhum schema/API foi publicado.
As evidências não contêm tokens nem dados pessoais reais. `.env.example` já estava
alterado pelo usuário e foi preservado.

Após os testes, o servidor sintético foi encerrado e o aplicativo foi restaurado
em produção local na porta 3000, usando o Xano do `.env`. A verificação de
disponibilidade retornou HTTP 200 em `/ping` e `/login` e HTTP 101 no upgrade do
WebSocket `/_event/`. Isso confirma a disponibilidade local; não substitui um
percurso autenticado com dados do Xano real.
