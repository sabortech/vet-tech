# Arquivamento do fluxo

Arquivado em 2026-11-15 por solicitação explícita do usuário para encerrar todas as changes abertas antes do PR. O arquivamento preserva o estado registrado; não declara concluídas verificações pendentes.

Specs: deltas sincronizados e comparados com as specs principais; validação global com 29 specs aprovadas.

Tarefas pendentes preservadas (10):

- 1.2 Implementar geração criptográfica, hash protegido, expiração, consumo atômico e invalidação por mudança de credencial; comprovar no backend de desenvolvimento rejeição por expiração, replay, conta/finalidade diferentes e confirmações concorrentes.
- 1.3 Implementar limites persistentes de emissão, tentativas e origem, reenvio com invalidação e limpeza por retenção acionada pelo backend Reflex local; testar limites inclusive sob concorrência e documentar valores e origem confiável.
- 1.4 Configurar sanitização do histórico de requests e logs de aplicação e eventos; verificar que senha, código, autorização restrita e token não aparecem em logs nem respostas genéricas e documentar retenção.
- 2.4 Validar destinatário, remetente permitido para teste e envio HTML/texto via Brevo pelo Xano; comprovar entrega em caixa de teste explicitamente configurada e falha segura sem retries automáticos, registrando dependências de ambiente sem segredos.
- 3.1 Implementar solicitação autenticada de código por perfil e atualizar endpoints de senha para exigir desafio/código e senha atual; testar diretamente ausência de código, senha errada, tokens cruzados, IDs coincidentes e sucesso isolado da conta autenticada.
- 3.2 Implementar solicitação pública de recuperação com resolução única de tutor/veterinário e resposta uniforme; testar contas existentes, e-mail desconhecido e ambíguo sem revelar existência/perfil, incluindo verificação de tempo de resposta e limites.
- 3.3 Implementar verificação do código e autorização opaca restrita de cinco minutos, seguida de conclusão atômica sem login automático; testar token expirado, reutilizado, de outra finalidade e sem permissão de acesso clínico.
- 3.4 Revisar rotas legadas de alteração/recuperação que alcancem tutor/veterinário e impedir bypass; documentar contratos, incompatibilidade com clientes antigos e separação dos endpoints Quick Start de user, verificando chamadas diretas.
- 6.1 Executar testes de integração reais com contas sintéticas para alteração e recuperação de ambos os perfis; registrar evidências sanitizadas de código inválido/expirado/reutilizado, reenvio, limites, concorrência e login com senha nova e rejeição da anterior.
- 6.2 Confirmar ausência de envio de código no login normal e preservação de isolamento de perfis e acesso clínico; executar suíte relevante e compilação conforme `reflex-process-management`, registrando resultados na change.
