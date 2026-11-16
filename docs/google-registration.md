# Cadastro com Google

A tela `/cadastro` oferece **Cadastrar com Google** quando `GOOGLE_LOGIN_ENABLED` está ativo. Reutiliza cliente OAuth, segredo e redirect URI configurados no Xano. Em ambiente Google de teste, a conta escolhida precisa estar na audiência autorizada; a aplicação não contorna essa limitação.

Google importa nome e e-mail verificado. Não fornece CPF, endereço, telefone ou registro profissional. Após autorização, completar esses dados: tutor exige CPF/endereço/telefone; veterinário exige telefone, CRMV/UF, espécies e especialidades, com clínica opcional. Não há senha nem confirmação nesse fluxo. E-mail importado não pode ser alterado no formulário.

`GET acesso/google/inicio?intencao=cadastro` registra intenção no state. `POST acesso/google/retorno` troca código com PKCE e valida claims; devolve prova opaca temporária para cadastro, não sessão. `POST acesso/google/cadastro` recebe prova e dados restantes, resolve e-mail/sub exclusivamente no servidor e conclui conta/reserva/vínculos/evento de boas-vindas numa transação. Consumo único arbitra concorrência. Login Google existente continua sem criar contas. Conta existente deve entrar pelo login.

A credencial local é opcional somente para o cadastro Google interno. Endpoints convencionais continuam exigindo senha. **Esqueceu a senha?** permite cadastrar a primeira senha após código por e-mail, com as mesmas proteções e sem remover Google. Configurações orientam esse fluxo quando o backend informa ausência de senha, sem divulgar hashes. O endpoint protegido de conta retorna apenas `possui_senha` como informação adicional.

Não registrar provas, código OAuth, tokens ou dados pessoais em logs. Prova é guardada apenas no estado privado Reflex e tem validade de dez minutos. Cancelamento limpa o estado local; a prova abandonada expira sem criar conta.

Verificação: `PYTHONPATH=tests/unit .venv/bin/python -m unittest test_google_registration test_google_login test_auth_state test_settings_state test_veterinarian_settings -q`; validar XanoScript e compilar Reflex com `reflex compile --dry`. Testar OAuth real manualmente em conta autorizada, completar os dados e entrar novamente pelo Google em ambos os perfis. Testes nativos usam destinatários `.invalid` sem entrega real.

Publicação: backup seletivo sem ambiente; schema opcional/provas e helpers antes dos endpoints/UI. Rollback desabilita cadastro Google na interface e restaura endpoints compatíveis, preservando contas/vínculos e schema opcional. Não restaurar campo obrigatório enquanto existir conta Google sem senha.
