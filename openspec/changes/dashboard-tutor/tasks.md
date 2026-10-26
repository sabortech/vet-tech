## 1. Leitura agregada protegida no backend

- [ ] 1.1 Implementar a leitura autenticada por pet, com consultas e campos limitados, validação de propriedade em cada consulta clínica e testes locais do contrato; validar no Xano que um tutor não consegue obter perfil nem registros de outro tutor antes de concluir.
- [x] 1.2 Implementar projeções determinísticas de próxima dose, última consulta finalizada, próximo evento, registros recentes e itens a acompanhar; verificar datas passadas, hoje, futuras, campos ausentes e exame solicitado sem realização com testes unitários.

## 2. Dashboard do tutor

- [x] 2.1 Registrar a rota `/dashboard` e habilitar o destino na navegação do tutor mantendo `/` e `/prontuario`; verificar navegação, indicação de seção ativa, acesso sem sessão e responsividade.
- [x] 2.2 Implementar seletor “Todos os pets”/pet individual em estado independente do pet clínico selecionado; verificar que trocar o filtro não inicia seleção clínica, não altera o pet ativo e descarta respostas atrasadas de escopos anteriores.
- [x] 2.3 Compor a visão geral por pet e o perfil individual com foto opcional, nome, espécie, raça, idade derivada, peso sem unidade inferida, resumos e prévias recentes; verificar estado sem pets, campos opcionais, ordenação e ausência de dados fictícios.
- [x] 2.4 Integrar ações rápidas para iniciar agendamento com o pet escolhido, abrir Vacinas e abrir o Prontuário; verificar que o pet de contexto do agendamento é explícito, a seleção clínica não muda silenciosamente e nenhum destino indisponível de Exames é apresentado como funcional.

## 3. Verificação e documentação

- [x] 3.1 Executar os testes unitários focados do Dashboard e as regressões de navegação, seleção de pet, agendamento e carregamento clínico; verificar que todos passam com `python -m unittest discover -s tests\unit`.
- [x] 3.2 Compilar/exportar a aplicação Reflex e verificar que a nova rota e os componentes do Dashboard não produzem erros de compilação.
- [x] 3.3 Atualizar `docs/architecture.md` e o guia rápido para refletir o Dashboard habilitado, seu filtro independente e os limites dos dados; verificar links e consistência com os contratos OpenSpec.
- [ ] 3.4 Executar verificação de navegador com tutor sem pets, com múltiplos pets, filtro individual e agendamento; confirmar visualmente que os dados exibidos correspondem ao pet/escopo e que erro de leitura não aparece como ausência de pendências.
