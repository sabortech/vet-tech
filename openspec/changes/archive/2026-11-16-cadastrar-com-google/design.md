# Design

## Context

Ver proposta para motivação. `cadastro.py` renderiza feedback CPF vazio entre campos; o botão Google é desabilitado. `start_google_login` e `finish_google_login` aceitam somente sessão existente. OAuth Xano já valida claims e PKCE/state, e `vinculo_google` resolve sub estável. Signup convencional exige senha, valida CPF ou CRMV/aptidões e grava reserva e evento de boas-vindas em transação. Tutor tem campo password obrigatório; veterinário tem senha opcional.

## Goals / Non-Goals

Garantir cadastro sem senha com todos os dados reais do perfil. Reutilizar infraestrutura OAuth, validações e emissão de sessão; não transformar login em criação automática nem inferir CPF/CRMV a partir de Google. Não criar nova integração de e-mail, nem alterar autorizações de prontuário.

## Decisions

1. Intenção `login` ou `cadastro` é registrada com state no servidor. O callback existente despacha pela intenção persistida, nunca por parâmetro de retorno não confiável. Cadastro retorna prova opaca aleatória, hash persistido, validade dez minutos e nome/e-mail verificados; frontend a mantém no estado privado Reflex, amarrada à aba. Não retornar token de sessão antes da conclusão.
2. Após OAuth, mostrar nome importado editável e e-mail verificado não editável; pedir todos os campos restantes e ocultar senha/confirmar. Não depender de dados não salvos do formulário antes do redirecionamento. Perfil selecionado é preservado e validado como escolha de cadastro, não autorização. Cancelar permite voltar ao cadastro convencional e limpa prova/rascunho Google.
3. Novo endpoint de conclusão e helpers internos compartilham validações com signup convencional. Transação consome prova mediante restrição única e cria conta, reserva, vínculos profissionais, vínculo Google e evento de boas-vindas. Falha reverte tudo. Duplicidade prévia orienta login sem substituir vínculo. Reaproveitar confirmação de sessão via `/me` e limpeza por geração.
4. Tornar credencial do tutor opcional para novas contas Google, sem modificar hashes existentes; manter campo veterinário opcional. Não gerar senha fictícia. Login por senha verifica ausência antes de check_password. Recuperação representa ausência de credencial por marcador interno determinístico, preservando fingerprint e uso único, e permite criar primeira senha após verificação de e-mail. Expor somente booleano de existência de senha no `/me` quando necessário para orientar configurações.
5. Manter evento de boas-vindas e envio pós-transação existentes. Mover feedback CPF para renderização condicional junto ao campo; usar gap único para campos, sem ocultar mensagens reais.

## Risks / Trade-offs

- Google não entrega CPF/endereço/telefone/CRMV → etapa complementar obrigatória, sem conta parcial.
- Reutilização de prova ou dupla conclusão → consumo atômico e índices únicos, testes concorrentes.
- Credencial ausente altera suposições de recuperação/configurações → testar primeira senha, login e contas legadas dos dois perfis.
- Resultado incerto após conclusão → não reenviar automaticamente; orientar login para verificar conta criada, sem duplicar notificações.
- OAuth depende de configuração e audiência Google → verificar ambiente e restrições de usuários de teste antes de afirmar disponibilidade geral.

## Migration Plan

Validar XanoScript e backup seletivo sem segredos; publicar schema opcional e provas/índices, funções e endpoints compatíveis antes da UI. Manter login e signup convencionais. Compilar Reflex e reiniciar processo local conforme skill. Rollback desabilita cadastro Google e restaura UI/endpoints anteriores; preservar contas/vínculos criados e campo opcional, permitindo login Google existente. Não restaurar schema obrigatório enquanto houver contas sem senha.
