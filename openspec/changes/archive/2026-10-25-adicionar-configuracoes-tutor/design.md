# Design das configurações do tutor

## Context

Ver motivação e escopo em `proposal.md`. A exploração identificou:

- `vet_tech/vet_tech.py` registra `/`, `/login` e `/cadastro`; Configurações está visível mas desabilitada em `components/sidebar.py`.
- `features/auth/state.py` mantém token privado e autenticação na sessão Reflex; não há restauração persistente de login. O login só guarda token, sem dados pessoais de conta.
- `auth/me` e `reset/update_password` autenticam em `user`. Não podem ser usados com o token de `tutor` nem copiados com a auditoria genérica que inclui o objeto do usuário.
- `NavigationState.sidebar_preference` já usa armazenamento local e sincronização entre abas. Não criar uma segunda preferência para a mesma sidebar.
- `assets/vet_tech.css` concentra cores em variáveis, mas componentes e estados de biblioteca precisam de revisão para o tema escuro.
- As specs existentes protegem o layout e contrato de Meus Pets. Esta change acrescenta configurações e aparência sem mover o perfil de sua rota.

## Goals / Non-Goals

**Goals:** entregar a conta funcional integrada ao Xano, com identidade estrita por tutor, composição visual reutilizada e preferências sem depender de chamadas de rede.

**Non-Goals:** criar um novo mecanismo de login, revogar tokens globalmente, alterar dados clínicos, migrar o schema ou alterar a estrutura das telas públicas. A troca de senha muda a credencial no backend e encerra a sessão atual no frontend; tokens emitidos anteriormente podem continuar válidos conforme a política existente.

## Decisions

### 1. Estado por funcionalidade e sessão compartilhada

Criar `pages/configuracoes.py` e `features/settings/state.py` (ou nome equivalente alinhado à arquitetura), compondo o layout existente. O estado consulta o token privado do estado de autenticação no servidor; não duplica token em variável pública nem o envia ao armazenamento local. Centralizar a limpeza da sessão para logout normal, expiração e troca de senha, preservando a mensagem de confirmação no redirecionamento.

Carregar conta somente após confirmação da sessão e entrada na página. Não acrescentar essa consulta ao caminho crítico de login. Dados carregados, rascunho e senha não sobrevivem a logout ou mudança de identidade. Operações capturam uma identidade de sessão e só aplicam resultados se ela ainda corresponder à sessão atual. Preferir eventos sequenciais com publicação de progresso; se necessários eventos de background, usar o controle de estado documentado do Reflex durante a implementação.

Alternativa descartada: concentrar todos os campos em `auth/state.py`, aumentando o acoplamento entre login, pets e configurações.

### 2. Contratos Xano específicos de tutor

O inventário remoto durante apply encontrou `GET tutor/me`, usado para identidade (`perfil`, `identidade_id`, `nome`). Ele permanece intacto. Os contratos novos de dados pessoais usam `tutor/account` para evitar quebrar esse consumidor; o caminho sugerido inicialmente foi ajustado antes da publicação.

Contratos planejados no grupo Authentication, reutilizando a origem configurada:

| Método e endpoint | Entrada | Resultado |
|---|---|---|
| `GET tutor/account` | Token de tutor; sem ID de conta no payload | `{nome, email, cpf_mascarado, telefone, endereco}` |
| `PATCH tutor/account` | `{nome, telefone, endereco}` obrigatórios e não vazios após trim | Mesmo formato seguro com valores persistidos |
| `POST tutor/password` | `{current_password, new_password, password_confirmation}` | Confirmação sem objeto da conta ou credenciais |

Todos usam `auth = tutor` e `$auth.id` como identidade. Validar existência da conta. No PATCH, usar allowlist de escrita: campos extras não são copiados; ID, CPF, e-mail, senha e vínculos permanecem intactos. Validar todos os campos antes de uma única escrita. Telefone e endereço continuam textos como no cadastro; não introduzir uma nova modelagem de endereço ou validação geográfica.

CPF é mascarado no servidor, por exemplo `***.456.789-**`; entrada ausente ou malformada nunca deve vazar o valor bruto como fallback. Não retornar CPF completo para depois ocultá-lo no browser. Nenhuma resposta inclui hash ou senha.

Senha atual é verificada com a função de hash do Xano. Nova senha não vazia e confirmação exata; sem `trim` nos campos de senha. A política de complexidade/tamanho do tutor permanece a atual (o cadastro existente exige presença, sem mínimo adicional). Isso preserva senhas atuais e evita importar o mínimo do endpoint legado de `user`. Qualquer endurecimento futuro deve ser tratado como decisão própria.

Não usar `Quick Start/log_event` com objetos pessoais ou credenciais. Não gerar `log_acesso`, reservado ao prontuário veterinário. O escopo não altera regras RN01–RN08, vínculos ou histórico clínico.

### 3. Erros distinguíveis sem vazamento

O cliente compartilhado deve disponibilizar classificação/status suficiente para distinguir autenticação inválida de erro de domínio. Planejar 401 para token ausente/inválido e rejeição de domínio com código seguro próprio para senha atual incorreta; adaptar ao formato efetivo do Xano sem classificar todo 403 como sessão expirada. Acrescentar à allowlist apenas mensagens conhecidas da conta e da senha; não propagar corpos arbitrários. Preservar 429, timeout e comportamento das chamadas existentes. Nenhum retry automático de PATCH ou troca de senha.

Após troca confirmada: limpar campos, rascunho, conta e sessão; voltar a `/login` com “Senha atualizada. Entre novamente com sua nova senha.” Falhas não simulam sucesso. Preferências locais permanecem. Validar a nova credencial somente em fixture de teste, sem alterar a senha do usuário como ensaio.

### 4. Formulário e confirmação de descarte

Manter snapshot dos últimos dados confirmados e rascunho editável. Comparar valores normalizados de nome/telefone/endereço para identificar alterações. Salvar e Cancelar habilitados quando aplicável; bloquear duplicatas e publicar estado antes da rede. Erro preserva o rascunho, sucesso atualiza snapshot e só então informa confirmação.

A troca de abas, links internos e Sair passam por um guard quando há edição pessoal pendente; registrar a intenção e executá-la apenas após Descartar alterações. Continuar editando cancela a intenção e restaura foco. Confirmar descarte também ao usar navegação interna por histórico quando suportada pela integração de roteamento; para recarga/fechamento usar `beforeunload`, condicionado à edição e às limitações do navegador. Não transformar falha de salvamento em saída automática.

Senhas não são restauradas entre abas: limpar ao sair de Segurança e resetar visibilidade. Não enviar senha em eventos de digitação desnecessários nem manter cópias em logs. Representar somente visibilidade e feedback como estado de interface quando possível.

### 5. Preferências locais e tema

Reutilizar a chave existente `vet_tech_sidebar_expanded`. O switch de Preferências e o botão da sidebar atualizam a mesma fonte; gaveta móvel continua separada. Tema utiliza chave própria com valores claros (`light`/`dark`), local ao navegador e compartilhada entre abas. Sem chave válida, usar claro; não introduzir modo automático do sistema. Storage indisponível: preferência em memória e interface funcional.

Aplicar atributo de tema no documento e sobrescrever tokens de todo o sistema, incluindo login, cadastro, portais e cor da sidebar. A inicialização precisa ler a preferência local antes de revelar qualquer tela (bootstrap no cliente com guarda de renderização até resolver a preferência, se necessário), sem depender da ida e volta de um evento ao servidor. Evitar duas fontes de verdade entre componente de tema e CSS; conferir hidratação e seletores/portais da biblioteca. Consultar documentação/versionamento Reflex na implementação antes de escolher a integração concreta.

Paleta escura inicial para ajuste visual: fundo `#141715`, cartão `#202622`, campos `#2B332E`, texto `#EEF3EF`, secundário `#B4C0B7`, borda `#445248`, sidebar verde profundo `#183A2A`. Preservar `#689554` como identidade; ajustar cores de texto de botões e estados para legibilidade em ambos os temas. O item ativo pode preservar o pill claro existente. Validar contraste dos pares reais; não assumir que o mesmo verde funciona para qualquer texto.

Alternativa descartada: armazenar preferências em Xano, que adicionaria latência e sincronização de conta sem necessidade aprovada.

### 6. Fidelidade visual e referências

Primeiro protótipo: base clara e organização de Minha conta. Segundo protótipo: referência escura e distribuição de botões; suas janelas menores representam conteúdos das abas, não popovers reais. Arquivos apresentados pelo usuário:

- `/home/usuario/Downloads/Gemini_Generated_Image_ixfbocixfbocixfb.jpeg`
- `/home/usuario/Downloads/Gemini_Generated_Image_kwdz7mkwdz7mkwdz.jpeg`

Na implementação, preservar cópias das referências junto às evidências da change para não depender de Downloads. Usar a tartaruguinha existente `assets/mascote-perfil.png`; não gerar uma mascote nova nem reproduzir moldura do navegador/barra do sistema das imagens.

Minha conta: cabeçalho Dados pessoais / Perfil: Tutor; nome/e-mail na primeira linha, CPF/telefone na segunda e endereço em largura total. Rótulos simples e cadeados com explicação acessível para e-mail e CPF. Botões Cancelar e Salvar alterações à direita; em celular podem ocupar a largura disponível. Segurança exibe somente o cartão Alterar senha; Preferências exibe Aparência e Navegação. Mascote secundária inteira quando couber, oculta em telas estreitas. Título, ação Sair, abas e controles devem caber sem sobreposição.

## Risks / Trade-offs

- [Rotas novas expõem a ausência de persistência de sessão] → acesso direto sem sessão vai ao login; restaurar login não integra esta change.
- [Portal de select ou diálogo escapa do ancestral do tema] → validar componentes abertos em Meus Pets e Configurações e garantir contexto de tema coerente.
- [Storage/hidratação causa flash claro] → testar primeiro conteúdo visível após reentrada com preferência escura previamente salva.
- [Resposta atrasada ou token antigo] → comparar sessão antes de aplicar dados e limpar estado no encerramento; não prometer revogação remota de tokens.
- [Rascunho perdido em navegação] → guard interno e aviso nativo quando disponível; sem promessa de bloquear fechamento forçado do navegador.
- [API local diverge da remota] → inventariar contratos de desenvolvimento antes de publicar; testar duas identidades e validar endpoints diretamente, sem aceitar mock como prova de autorização.
- [Falha de rede durante troca de senha deixa resultado incerto] → mostrar falha sem repetir operação nem afirmar que a senha foi mantida; permitir voltar ao login e conferir credencial.

## Migration Plan

1. Implementar e validar XanoScript no ambiente de desenvolvimento já documentado, preservando endpoints existentes; confirmar destino antes de publicação se a conexão disponível não o comprovar.
2. Publicar endpoints aditivos e testar com dois tutores sintéticos, além de tokens de outros domínios. Não modificar registros preexistentes nem credenciais reais.
3. Integrar rota, estado, navegação e temas. Executar suíte unitária, compilação e testes reais de navegador no fluxo completo.
4. Registrar endpoints, comandos, evidências e limites na documentação. Não alterar schema/DER: não há novo campo ou relacionamento.
5. Rollback: restaurar interface anterior e remover somente endpoints novos desta entrega após inventário. Preservar alterações pessoais e senhas já confirmadas pelo usuário; não tentar revertê-las automaticamente. Chaves locais de aparência podem permanecer sem efeito na versão anterior.

## Refinamento visual solicitado após revisão

A tartaruguinha fica na linha das abas, imediatamente ao lado de Preferências,
fora do tablist semântico. Em celular permanece oculta para preservar as abas.
O cartão Segurança fica centralizado com largura máxima de 640 px, formulário
compacto, título/explicações e ação centralizados. As etiquetas dos campos
permanecem à esquerda para leitura. Navegação e Modo escuro usam o mesmo switch
nativo e os mesmos tokens de trilho, tamanho e foco; a preferência de expansão
continua ligada ao estado já existente.

Ajuste de tamanho solicitado: mascote da linha de abas ampliada de 96 × 84 px para 112 × 98 px, mantendo proporção e alinhamento pela base.

Ajuste de hover solicitado: links navegáveis da sidebar usam texto e ícones em verde escuro (#1A3629) sobre fundo verde claro (#EBEEE5), também no foco por teclado, substituindo a cor azul padrão dos links.

Visibilidade de senha: ícone eye-off para caracteres ocultos e eye para senha visível, sincronizados com aria-pressed e restaurados ao limpar o formulário.

Campos de Minha conta e Segurança recebem ícones decorativos à esquerda, usando o conjunto existente: pessoa, envelope, documento, telefone, localização, cadeado, chave e escudo de confirmação. Rótulos, cadeados de somente leitura e olhos de visibilidade permanecem acessíveis, sem sobrepor o texto.

Refinamento dos ícones solicitado: Nome usa pessoa em círculo (circle-user-round), Telefone mantém telefone (phone) e Endereço usa prédio (building-2).

Refinamento de Meus Pets solicitado: ícones de traço decorativos por campo (nome, espécie, raça, sexo, nascimento, peso, pelagem e microchip) e câmera na seleção de foto. São adornos sem alteração de contrato, nomes acessíveis ou comportamento dos controles.

Correção solicitada: Meus Pets usa rx.icon do mesmo conjunto de Configurações, em cor neutra adaptada ao tema, substituindo todos os emojis.

## Otimização da navegação solicitada

Os links da sidebar estavam sempre cancelando a navegação local para pedir um
redirect ao servidor. A leitura da conta no evento enter também mantinha a fila
de eventos ocupada durante a consulta ao Xano. Links limpos passam a usar a
navegação nativa do router; o guard intercepta apenas rascunho real ou escrita em
curso. A leitura de conta será um evento de background com bloqueio de estado
apenas antes/depois da rede e cache de 60 segundos restrito à mesma sessão.
Logout/invalidação continuam limpando os dados. Dados de sessão anterior são
descartados; sem persistência local de conta. Durante revalidação, edição fica
desabilitada para não sobrescrever um rascunho.
