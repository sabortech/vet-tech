# Tarefas

## 1. Migração e identidade profissional

- [x] 1.1 Preparar inventário privado e simulação de migração de e-mails, CRMVs, clínicas, especialidades e hashes; entregar relatório de conflitos, contagens e plano de restauração sem modificar dados remotos nesta tarefa.
- [x] 1.2 Implementar reserva única de e-mail e criação transacional de identidades/vínculos, cobrindo cadastro tutor legado; verificar concorrência cruzada, falha intermediária e ausência de reservas órfãs com testes de backend.
- [x] 1.3 Habilitar autenticação veterinária e migrar CRMV/UF com chave única, clínica opcional, especialidades e espécies múltiplas; verificar hashes preservados, CRMVs inválidos/repetidos, referências inválidas e pares associativos únicos em ambiente de teste.
- [x] 1.4 Documentar contratos de migração e atualizar domínio/DER para clínica opcional, unicidade global de e-mail e CRMV sintático sem comprovação externa; conferir coerência com schemas e ausência de alterações em vínculos de pets.

## 2. Cadastro compartilhado

- [x] 2.1 Implementar cadastro veterinário e catálogos públicos mínimos de opções, com conjunto mínimo versionado de especialidades; testar payloads válidos, clínica ausente/inexistente, catálogos vazios, e-mail cruzado e respostas sem senha/hash ou dados privados.
- [x] 2.2 Adaptar `/cadastro` com escolha do perfil, campos profissionais, múltiplas aptidões e confirmação de senha, preservando formulário/CPF tutor; verificar validações locais, erros reais da API e retorno ao login nos dois perfis, em desktop e celular.
- [x] 2.3 Documentar campos, formato CRMV/UF e opções de cadastro; executar testes de regressão do cadastro tutor e conferir que nenhum cadastro autentica automaticamente.

## 3. Login e isolamento de sessão

- [x] 3.1 Implementar login compartilhado e endpoints protegidos de identidade por perfil, preservando o contrato tutor legado; testar senha incorreta, duplicidade histórica, reserva inconsistente, expiração e omissão de informações sensíveis.
- [x] 3.2 Integrar perfil/identidade ao estado Reflex e à tela existente sem seletor de perfil no login; testar encaminhamento, falha de login, logout, troca de identidade e descarte de resposta atrasada, sem duplicar estado de sessão.
- [x] 3.3 Preparar área veterinária identificada e sem dados clínicos; provar no backend que tokens cruzados, perfil forjado e IDs iguais entre tabelas não permitem acesso, e documentar limites da área veterinária.

## 4. Menu e contexto do tutor

- [x] 4.1 Extrair composição da área autenticada e implementar menu retrátil na ordem aprovada, seção ativa, Início e mensagens honestas dos módulos futuros; verificar teclado, nomes acessíveis, desktop e celular sem overflow, preservando o pet ao recolher.
- [x] 4.2 Reutilizar Mudar pet com os fluxos de seleção e limpeza existentes; testar ausência de seleção automática, pet alheio, troca rápida, falha de catálogo, erro de abertura e logout com resposta pendente.
- [x] 4.3 Mover Novo pet para modal reutilizando formulário/API; verificar cancelar sem escrita, foco/Escape/retorno, envio sem duplicação, erro recuperável, atualização da lista e manutenção explícita do pet atual após cadastro.
- [x] 4.4 Documentar a composição e os pontos de extensão para seções futuras; executar suíte unitária e compilação conforme a skill de processos Reflex, registrando os resultados sem atribuir funcionalidades clínicas aos placeholders.

## 5. Verificação conjunta e implantação

- [x] 5.1 Executar dry-run da migração/publicação e percurso real em ambiente de teste com tutor e veterinário, emails disputados e IDs coincidentes; confirmar ausência de regressão dos endpoints tutor e preservação de dados anteriores, guardando evidências em `verification.md`.
- [x] 5.2 Verificar navegador desktop/celular para cadastro/login de ambos os perfis, menu, modal, troca de pet e sessão; registrar resultados, limitações e limpeza das fixtures sem modificar registros preexistentes.
- [x] 5.3 Aplicar sequência de implantação após verificação dos conflitos e testar smoke de ambos os perfis, cadastros legados e proteção de pets; registrar versão, contagens e procedimento de rollback exercitado, sem excluir histórico ou contas.

## Workflow follow-up

- Revisar as evidências e sincronizar specs ao concluir a implementação; arquivar apenas após o encerramento do fluxo de revisão do projeto.
- Executar a carga revisada de `popular-catalogos-especies-racas` quando o ambiente precisar das espécies/raças iniciais; não confundir catálogo disponível com autorização veterinária.
