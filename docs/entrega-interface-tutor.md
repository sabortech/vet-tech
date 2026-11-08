# Entrega da interface do tutor

## Alterações

- Navegação lateral consistente, seleção de pet em lista própria e cadastro em Meus Pets.
- Calendários compartilhados para agendamento e nascimento, com validações de data.
- Cards padronizados em Vacinas, Medicamentos, Doenças e Consultas; campos de consulta reunidos e cenários variados por registro.
- Dashboard com card completo por pet; LED conforme o prazo da próxima dose e sombra correspondente na visão individual.
- LED e sombra verde no login, cadastro e cards das áreas solicitadas.
- Imagens otimizadas, histórico carregado ao entrar na área clínica e leituras independentes com concorrência limitada.

O uso está descrito no [guia rápido](guia-rapido.md). Decisões técnicas estão em [arquitetura](architecture.md). As sete mudanças OpenSpec e suas evidências estão em `openspec/changes/archive/2026-11-07-*`; não há mudanças abertas.

## Verificação para integração

- Suíte unitária completa: **333 testes aprovados**. Execução fora do isolamento necessária para os testes de PDF com subprocessos locais.
- Compilação Reflex: aprovada.
- OpenSpec: sete mudanças e 26 especificações validadas antes do arquivamento.
- Navegador: evidências arquivadas cobrem navegação, calendário, cards, temas claro/escuro e celular. Dashboard individual validado nos cinco estados de prazo; login e cadastro verificados em 1440 e 390 px.
- Verificação de whitespace: aprovada.

## Publicação

O merge integra os arquivos do projeto, mas não publica contratos no Xano. A projeção de `foto` no endpoint `pets/{pet_id}` foi incluída na fonte XanoScript e deve ser publicada pelo fluxo de backend para ser refletida no ambiente remoto.
