## Context

`consultation_card` usa o shell `vaccine-record-card` e LED verde fixo. A agenda veterinária já utiliza vermelho #ff5252 e amarelo #facc15. A regra global ao final do CSS aplica `--vt-card-green-shadow` às superfícies fora do Dashboard; sua especificidade precisa ser respeitada.

## Goals / Non-Goals

**Goals:** aplicar a paleta por status somente à lista de Consultas do tutor, com CSS compartilhado entre cartões.

**Non-Goals:** modificar agenda, detalhe, API, permissões ou ações; alterar finalizadas, legados e canceladas.

## Decisions

- Derivar uma classe ou atributo do status já presente em cada linha. Evitar novo estado serializado ou chamadas de rede.
- Criar seletores locais para `agendada` e `em_atendimento` e variáveis de cor para superfície, borda, ícones, selo, disco ilustrado, LED e halo. Reutilizar a animação do LED existente e as cores da agenda, com acentos legíveis por tema.
- Sobrescrever a sombra global apenas nesses dois estados, com especificidade suficiente; não modificar o token verde global. Copiar o componente inteiro duplicaria estrutura e dificultaria manutenção.
- Manter intacta a condição de renderização do rodapé.
- Projetar data e horário separadamente a partir de `agendada_para` usando o conversor de instantes existente no fuso local; sem agendamento válido, manter a data clínica disponível e explicitar ausência de horário. Compor os dois campos com `_medication_field`, calendário e relógio, em uma linha que quebra conforme espaço disponível.
- Conforme revisão visual do usuário, agrupar cada ícone ao conjunto compacto de título e valor, com 2 px entre os textos e centralização vertical do ícone ao conjunto. Remover a grade que separava o título do ícone. Apresentar `Consulta: <id>` como heading h3 independente, no canto superior esquerdo do corpo, acima do calendário principal.

## Risks / Trade-offs

Complementos do detalhe recebem projeção local `care_label`/`care_tone` ao abrir a consulta. Datas civis usam `calendar_date` e o dia de São Paulo. Vacina futura de legado é previsão, não aplicação; próxima dose ultrapassada é apenas data registrada ultrapassada. Medicamento contínuo sem fim e com início válido fica dentro do período prescrito; sem início ou intervalo inválido fica neutro. Wrapper local aplica paleta apenas aos cartões do detalhe, sem alterar as abas clínicas. Vacinas e medicamentos recebem selo de situação; exames e doenças mantêm seus textos de status existentes.

A linha do rodapé de cada cartão de consulta recebe margem superior de 16 px para separar os campos do botão Ver prontuário. O seletor fica restrito a `.consultation-card .vaccine-record-footer`.

O endpoint `tutor/consultas` deve obter `veterinario_nome` com left join de `consulta.veterinario_id` a `veterinario.id`, após `assert_owner`. Incluir apenas o nome na projeção e preservar a remoção dos dados não publicados. O left join preserva consultas com profissional ausente, sem N+1. O cartão usa fallback “Nome não informado”. O XanoScript exige publicação no ambiente remoto para disponibilizar os nomes; a interface permanece compatível com respostas antigas sem nome.

- Cascata global restaura o halo verde → verificar cores computadas do LED e sombra no navegador.
- Amarelo pouco legível no tema claro → usar acento escuro e superfície tingida, preservando amarelo vivo no LED.
- Imagens multicoloridas → preservar o cenário e aplicar a paleta ao disco e elementos do cartão.

## Migration Plan

Sem migração. Recompilar a interface após a implementação. Reverter apenas os seletores e o marcador de status para restaurar a apresentação anterior.
