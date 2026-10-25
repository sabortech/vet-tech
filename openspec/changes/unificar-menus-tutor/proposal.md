# Proposal

## Why

Meus Pets e Configurações usam a sidebar verde personalizada, enquanto Prontuário monta outro menu com componentes padrão do Reflex. A troca de área muda aparência, itens ativos e comportamento móvel; Vacinas e Consultas ainda aparecem indisponíveis no menu personalizado apesar de já existirem no fluxo clínico.

## What Changes

- Adotar o menu personalizado de `components/sidebar.py` e as classes `.sidebar-*` de `assets/vet_tech.css` como referência única de marca, cores, pill ativo, ícones, dimensões, foco e transições.
- Usar a mesma composição visual em Meus Pets, Configurações e Prontuário do tutor, substituindo a composição visual paralela de `components/navigation.py`.
- Apresentar um único catálogo ordenado: Dashboard, Prontuário, Vacinas, Medicamentos, Doenças, Consultas, Exames, Meus Pets e Configurações. Prontuário representa a seção clínica Início; Dashboard e Exames continuam indisponíveis.
- Tornar as seções clínicas existentes acessíveis também pelo menu das outras telas, preservando a seleção autorizada; sem pet, orientar escolha sem selecionar automaticamente um animal.
- Preservar Novo pet e Mudar pet no contexto clínico e a saída acessível nas telas atuais, usando o mesmo acabamento visual para ações do menu.
- Compartilhar tema, preferência de expansão e drawer móvel, sem overlay desktop em celular. Fechar o drawer após navegação bem-sucedida.
- Preservar o guard de alterações não salvas das configurações com o destino exato solicitado e a otimização de carregamento por pet já entregue.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `application-navigation`: menu do tutor compartilhado com catálogo atualizado, entradas clínicas funcionais, ativo coerente e destino preservado após descarte de edições.
- `authenticated-navigation`: integrar as seções clínicas ao menu visual comum, mantendo o pet e as ações clínicas existentes.

## Impact

- Frontend: `components/sidebar.py`, `components/navigation.py`, `pages/profile.py`, `pages/configuracoes.py`, `features/navigation/state.py`, `features/settings/state.py`, `features/clinical/state.py`, `features/auth/state.py` e `assets/preferences.js`; CSS somente para apoiar a composição existente.
- Testes: navegação, configurações, contexto do pet e navegador desktop/celular com tema claro/escuro e menu aberto/recolhido.
- Não alterar rotas públicas, contratos Xano, schema, notificações automáticas nem permissões. A renderização do menu não autoriza acesso a dados; backend mantém as regras existentes (RN01–RN08/RN05).
- Pet e dados pessoais permanecem na sessão atual; nenhuma informação clínica entra na preferência local. Não introduzir novas leituras clínicas só para renderizar ou recolher o menu, nem alterar a auditoria das leituras existentes.
- Escopo: os dois menus do tutor. O menu veterinário, a reformulação de cartões/formulários e a retirada do cadastro permanente em Meus Pets ficam fora desta change.
