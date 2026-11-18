# Spec Delta

## MODIFIED Requirements

### Requirement: Menu do tutor mantém entradas e saída em posições consistentes
Todas as telas autenticadas do tutor SHALL mostrar Adoção imediatamente abaixo de Meus Pets e antes de Mudar pet, e Configurações logo depois de Mudar pet, com somente Sair no rodapé. Novo pet SHALL NOT aparecer como entrada do menu; cadastro SHALL permanecer em Meus Pets. Em telas baixas a lista de navegação SHALL poder rolar, preservando a saída acessível. Configurações SHALL manter confirmação de descarte antes de Mudar pet ou Sair com dados não salvos. O menu veterinário SHALL preservar suas entradas próprias.

#### Scenario: Navegar entre abas
- **WHEN** o tutor abre Meus Pets, Adoção, Dashboard, seções clínicas ou Configurações
- **THEN** encontra as mesmas entradas na mesma ordem, Adoção abaixo de Meus Pets e Sair no rodapé

#### Scenario: Abrir Adoção
- **WHEN** o tutor autenticado seleciona Adoção
- **THEN** abre a área de adoção com Adoção identificada como item ativo e o menu móvel fecha após a navegação
