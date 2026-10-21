# Tarefas

## 1. Revisão exclusiva dos registros

- [ ] 1.1 Inventariar espécies, raças e referências existentes sem escrita; entregar contagens e tabela de correspondências/conflitos, preservando IDs e omitindo credenciais ou dados pessoais.
- [ ] 1.2 Preparar conjunto inicial versionado em `xano/seed/` com nomes, chaves estáveis, espécie de cada raça e fontes; entregar tabela de revisão agrupada por espécie e documentar cobertura e mapeamentos de sinônimos, sem criar registro artificial SRD.
- [ ] 1.3 Validar o conjunto e resolver correspondências ambíguas antes da aplicação; testes devem rejeitar duplicidades normalizadas, nomes vazios, raça sem espécie e sinônimos sem mapeamento.

## 2. Carga administrativa

- [ ] 2.1 Implementar simulação padrão sem escrita, plano revalidado antes da aplicação e credenciais por ambiente; verificar que a simulação não altera contagens/IDs e documentar os comandos exatos.
- [ ] 2.2 Preparar proteção de unicidade normalizada no Xano e carga somente de ausentes, com manifesto por execução/lote; testar reexecução, disputa concorrente, falha parcial e retomada sem duplicação nem renomear registros existentes.
- [ ] 2.3 Implementar reversão restrita às entradas criadas e ainda sem uso/alterações posteriores; testar que entradas antigas e registros referenciados são preservados e documentar o resultado parcial de reversão.

## 3. Verificação integrada

- [ ] 3.1 Executar simulação e aplicação em ambiente de teste, reaplicar e comparar IDs e referências anteriores; confirmar zero duplicidades e registrar relatório real em `verification.md` sem credenciais.
- [ ] 3.2 Verificar APIs atuais de espécies/raças, filtro por espécie e cadastro de pet com e sem raça; quando disponível, verificar seleção das mesmas espécies no cadastro veterinário, registrando explicitamente se essa integração ainda não existe.
- [ ] 3.3 Apresentar o plano concreto de carga para o ambiente de destino, executar a carga revisada e registrar contagens/manifesto e smoke das APIs; nenhuma confirmação de sucesso pode ocultar lote incompleto ou conflitos.

## Workflow follow-up

- Sincronizar a capacidade e arquivar após revisão das evidências e do conjunto carregado.
