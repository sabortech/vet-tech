# Tasks

## 1. Composição e catálogo únicos

- [x] 1.1 Registrar referências visuais do menu personalizado de Meus Pets/Configurações e a matriz rota/seção/ativo; verificar screenshots e medidas em claro/escuro, expandido/rail, sem dados pessoais reais.
- [x] 1.2 Centralizar as nove entradas, destinos e disponibilidade em `components/sidebar.py`, com allowlist das seções; adaptar `tests/unit/test_navigation_state.py` para verificar ordem, destinos, Dashboard/Exames indisponíveis e um único item ativo.
- [x] 1.3 Integrar `tutor_area` ao `layout_com_menu`, permitindo ações por composição e retirando a sidebar/backdrop/margens paralelos; verificar compilação, ausência de imports circulares e uso de uma só composição visual nas três áreas do tutor.
- [x] 1.4 Documentar referência visual, catálogo e pontos de extensão em `docs/architecture.md` ou na documentação existente de navegação; verificar correspondência com o catálogo testado e ausência de outra árvore visual de menu do tutor.

## 2. Navegação clínica e proteção de contexto

- [x] 2.1 Aplicar `secao` validada ao entrar em `/prontuario`, ao trocar parâmetros na mesma rota e ao voltar/avançar; testar valores válidos/inválidos, entrada sem pet, seleção posterior e preservação do pet entre Meus Pets/Configurações/Prontuário.
- [x] 2.2 Transportar o destino exato do link pelo guard de Configurações, incluindo a seção, com allowlist no servidor; testar continuar editando, descartar, recusar destinos externos/inválidos, bloquear durante gravação e navegar diretamente quando o formulário estiver limpo.
- [x] 2.3 Integrar Novo pet, Mudar pet e Sair ao acabamento compartilhado no contexto clínico e retirar o redirect de abertura/fechamento do modal; testar preservação de rota/seção, retorno de foco, cancelamento sem escrita, limpeza de contexto e descarte de respostas antigas.
- [x] 2.4 Adaptar os testes de contexto e `tests/integration/pet_loading_browser.py` às novas entradas; verificar zero novas leituras ao renderizar/recolher o menu, navegação sem duplicar carga em andamento e cache clínico mantido.
- [x] 2.5 Atualizar `docs/clinical-flow.md` com o mapeamento de seções e preservação de contexto; verificar os passos documentados no percurso integrado com HTTP controlado.

## 3. Drawer, tema e verificação integrada

- [x] 3.1 Usar somente `NavigationState.drawer_open` no celular e a preferência persistente atual no desktop; testar início fechado abaixo de 768 px, Esc/backdrop, fechamento após navegação concluída, cancelamento do descarte, alvos acessíveis e ausência de overlay residual.
- [x] 3.2 Comparar o menu nas três áreas em 1366×900, 1024×768 e 390×844, claro/escuro e expandido/rail; registrar screenshots/medidas de marca, cor, pill ativo, alinhamento, foco, rolagem e ações inferiores, sem overflow horizontal ou diferenças inesperadas de estilo.
- [x] 3.3 Executar as suítes de navegação, configurações, perfil, seleção e carregamento clínico, `reflex compile --dry` e validação OpenSpec; registrar comandos e resultados em `verification.md`, distinguindo navegador com HTTP sintético de qualquer verificação no Xano real.
