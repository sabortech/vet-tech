# Proposta

## Why

O tutor já cadastra e lista seus pets, mas não consegue abrir um animal nem
manter um contexto claro para navegar entre eles. Esta é a primeira entrega
P0 de `planejar-core-prontuario`: preparar a área individual de cada pet sem
misturar dados e com a propriedade verificada pelo backend (RF02, RN05 e RN15).

## What Changes

- Acrescentar à lista uma ação de abrir um pet e exibir seus dados cadastrais básicos.
- Permitir trocar entre os pets do tutor e voltar à lista sem excluir ou editar registros.
- Criar consulta autenticada de um pet por ID, autorizada exclusivamente ao tutor dono.
- Exibir carregamento, indisponibilidade e dados opcionais vazios; falha não mantém dados de outro pet na área atual.
- Invalidar seleção e respostas pendentes ao alternar, sair ou estabelecer outra sessão.
- Preservar cadastro, listagem e páginas compartilhadas de cadastro/login; a identificação veterinária permanece na próxima change.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `pet-management`: acrescentar abertura autenticada, seleção e alternância dos próprios pets; ampliar o requisito de operações permitidas para incluir consulta individual, mantendo edição e exclusão fora do escopo.

## Impact

- **Reflex:** evoluir o estado atualmente em `features/auth/state.py` e os
  componentes de `components/pets.py`, reutilizando as páginas atuais; consultar
  `docs/architecture.md` antes de introduzir qualquer módulo adicional.
- **Xano:** novo endpoint de leitura no grupo `Pet`; usar a entidade `tutor`
  autenticada e verificar propriedade no backend. Schema e DER não mudam.
- **Privacidade:** a leitura individual expõe apenas dados básicos do pet do
  dono. Não retornar dados de outros tutores, senha, token ou foto privada.
- **Auditoria:** esta etapa não abre prontuário clínico nem acesso veterinário;
  a auditoria de prontuário entra na change de autorização, antes dos endpoints clínicos.
- **Notificações:** sem impacto.
- **Verificação:** testes de API com dois tutores, cenários de estado e
  respostas atrasadas, regressões de cadastro/listagem e verificação desktop/celular.

## Fora do escopo

Prontuário, consultas, vacinas, doenças, medicamentos, exames, agenda,
consentimento veterinário, upload, edição/exclusão e persistência da seleção
entre sessões. Selecionar o animal não cria uma identidade autenticada de pet.
