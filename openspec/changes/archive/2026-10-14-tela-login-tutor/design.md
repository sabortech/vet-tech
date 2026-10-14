# Design

## Context

Ver `proposal.md` para o motivo deste registro retrospectivo. A pasta continha
somente metadados e proposta vazia. A entrega visual já foi documentada em
`openspec/changes/archive/2026-10-10-estilizar-tela-login/` e na spec principal
`openspec/specs/login-screen-presentation/spec.md` (caminhos relativos à raiz).

## Goals / Non-Goals

**Goals:** identificar os arquivos e comportamentos entregues e encerrar a
pasta incompleta com evidências verificáveis.

**Non-Goals:** alterar a tela ou declarar funcionalidades adicionais de login.

## Decisions

### Registrar o estado atual sem duplicar a entrega

Usar `skip_specs: true`, pois esta change passa a registrar uma organização
documental de comportamento já especificado. Criar outra delta de apresentação
duplicaria a change `estilizar-tela-login` sem representar uma nova mudança.

### Implementação identificada

- `vet_tech/components/auth.py`: `login_view()` compõe o cartão arredondado,
  painel branco, mascote, marca, boas-vindas, campos, botão e painel florestal.
- Os campos `email` e `password` são obrigatórios; o formulário usa
  `on_submit=State.login`, botão desabilitado durante `State.is_busy` e
  `State.login_message` em um elemento com `role="status"`.
- O cartão ocupa até 1040px; os painéis desktop têm larguras de 52% e 48%.
  Em telas estreitas o formulário ocupa 100% e o painel de imagem é ocultado.
- Fonte Nunito, tons verdes, `assets/mascote_logo.png` e `assets/fundo02.jpeg`
  compõem a identidade visual. O ícone Google usa uma URL externa existente.
- `State.show_signup` permanece ligado à chamada de cadastro.
- `vet_tech/pages/index.py` apresenta login ou perfil conforme a autenticação;
  `vet_tech/vet_tech.py` registra `/` e `/login`.
- Lembrar acesso, recuperação de senha e Google são elementos visuais sem
  handlers. O texto “E-mail ou CPF” não muda o campo `type="email"` nem
  adiciona suporte de autenticação por CPF.

## Risks / Trade-offs

- [Artefatos originais vazios] → O registro descreve o código observado e o
  histórico existente; não afirma recuperar decisões originais desconhecidas.
- [Confundir código responsivo com teste visual] → Separar inspeção de código,
  testes unitários e compilação de uma inspeção de navegador não realizada.

## Migration Plan

Preencher a documentação, verificar testes e compilação, validar a change e
arquivar preservando seus metadados. Não há migração ou publicação de código.
