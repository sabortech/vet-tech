# Configurações da conta do tutor

## Why

O tutor ainda não consegue consultar e atualizar seus dados pessoais ou alterar sua senha pela interface. Os protótipos aprovados permitem entregar essa área com a identidade visual existente e reunir as preferências de navegação e o novo modo escuro.

## What Changes

- Disponibilizar `/configuracoes`, acessível pela sidebar, com as abas Minha conta, Segurança e Preferências, inicialmente em Minha conta.
- Consultar dados reais do tutor e editar somente nome, telefone e endereço; e-mail permanece somente leitura e CPF é retornado mascarado.
- Alterar senha mediante conferência da senha atual no backend; após sucesso, limpar a sessão atual e retornar ao login com confirmação.
- Exibir estados reais de carregamento, validação, salvamento, sucesso e falha; impedir duplicatas e confirmar descarte de alterações não salvas.
- Oferecer modo escuro para todo o sistema, incluindo login, cadastro e a cor da sidebar e controle de menu expandido reutilizando a preferência existente. Ambas as preferências são imediatas e locais ao navegador.
- Reproduzir os protótipos com Nunito, tokens existentes, sidebar compartilhada e tartaruguinha, com adaptação móvel e componentes acessíveis.
- Criar contratos Xano próprios de `tutor`; os endpoints genéricos autenticados em `user` não atendem a essa conta.

## Capabilities

### New Capabilities

- `tutor-account-settings`: consulta e edição restrita da conta, troca de senha, proteção de acesso e apresentação das configurações.
- `interface-preferences`: preferência local de tema claro/escuro e controle sincronizado da expansão da sidebar.

### Modified Capabilities

- `application-navigation`: acesso à nova rota protegida e confirmação ao abandonar alterações pendentes.

## Impact

Frontend Reflex: nova página e estado de configurações conforme `docs/architecture.md`, integração com sessão e navegação existentes, cliente HTTP e tokens CSS. Backend Xano: leitura/edição da própria conta e alteração de senha no grupo Authentication, sem novos campos de domínio ou alterações no DER. Documentar contratos e verificar implementação local e integração em desenvolvimento.

RF01 e RN09: identidade e campos únicos preservados. Nome, contato, endereço e credenciais exigem proteção por identidade no servidor; não são persistidos em armazenamento local nem registrados em evidências. Não há leitura ou escrita de prontuário, alteração de consentimentos ou impacto em notificações; o log clínico continua reservado às operações clínicas. Cadastro/login existentes e senhas atuais permanecem compatíveis.

Fora do escopo: configuração de veterinário, edição de CPF/e-mail, foto do tutor, notificações, recuperação de senha, revogação global de tokens, persistência de login após recarregar, exclusão de conta, novas tecnologias e alteração estrutural de login/cadastro (a adaptação de cores ao tema está incluída). A saída após troca de senha encerra a sessão atual da interface, sem prometer invalidar tokens em outros dispositivos.
