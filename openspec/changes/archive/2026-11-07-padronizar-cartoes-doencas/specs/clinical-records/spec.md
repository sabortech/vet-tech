# Spec Delta

## ADDED Requirements

### Requirement: Aba Doenças compartilha apresentação das abas clínicas
A aba Doenças SHALL apresentar cabeçalho com título, descrição, identificação do pet e ação Atualizar, alinhado a Vacinas e Medicamentos. Cada condição SHALL usar cartão com dados à esquerda, painel decorativo à direita e contorno verde animado no padrão existente. No celular o painel SHALL ficar abaixo dos dados, sem corte de textos nem rolagem horizontal. Os dois temas SHALL manter contraste e leitura; animação reduzida SHALL seguir a preferência já aplicada aos cartões clínicos.

#### Scenario: Ler doença no desktop e no celular
- **WHEN** o tutor abre Doenças de seu pet em tema claro ou escuro
- **THEN** vê cartões padronizados com Vacinas e Medicamentos, com todos os textos legíveis e ação de atualização acessível

### Requirement: Cartão de doença preserva conteúdo publicado e origem
O cartão SHALL mostrar nome, estado registrado em português legível, data de evolução, consulta de origem, veterinário disponível e descrição. SHALL preservar quebras de linha e textos extensos. Ausências SHALL permanecer explícitas, sem atribuir estado clínico, profissional ou consulta fictícios. “Notas recentes” SHALL NOT ser fabricadas a partir da descrição ou de registros não retornados pela fonte atual. A ação de consulta SHALL existir somente quando houver vínculo e SHALL reutilizar a leitura autorizada existente.

#### Scenario: Condição com estado registrado
- **WHEN** a fonte retorna estado em_tratamento, data de evolução, descrição e consulta vinculada
- **THEN** o cartão mostra Em tratamento, a data legível e o conteúdo publicado, permitindo abrir a consulta correta

#### Scenario: Registro incompleto ou anterior
- **WHEN** faltam estado, evolução, veterinário ou consulta
- **THEN** as lacunas permanecem identificáveis e não aparece botão de consulta sem vínculo

#### Scenario: Acesso preservado
- **GIVEN** uma sessão sem propriedade do pet ou autorização profissional exigida
- **WHEN** tenta ler o histórico ou a consulta por ação do cartão
- **THEN** o backend mantém a negativa de acesso e a auditoria aplicável, sem exposição de dados no novo layout

### Requirement: Lista de doenças preserva estados de carregamento e isolamento
A aba SHALL distinguir carregamento, erro com nova tentativa e ausência de doenças publicadas. A padronização SHALL preservar descarte de respostas antigas após troca de pet ou sessão e não SHALL introduzir consultas extras para decoração.

#### Scenario: Lista vazia e falha
- **WHEN** a leitura termina vazia ou falha
- **THEN** a aba apresenta respectivamente orientação de ausência de doenças ou erro com nova tentativa, sem mostrar registros fictícios
