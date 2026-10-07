# Organização da aplicação

Este documento registra a estrutura recomendada para o código Python/Reflex do
VetTech. A organização deve evoluir gradualmente conforme cada funcionalidade
for implementada; não é necessário criar pastas vazias nem mover todo o código
existente de uma vez.

## Estrutura recomendada

```text
vet_tech/
├── vet_tech.py             # ponto de entrada Reflex e registro do app/páginas
├── pages/                  # telas associadas a rotas
├── components/             # componentes de interface reutilizados
├── features/               # estado e lógica agrupados por funcionalidade
│   ├── auth/
│   ├── tutors/
│   └── pets/
└── shared/                 # integrações e utilitários compartilhados
    └── xano_client.py

tests/
├── unit/
└── integration/

xano/                       # artefatos XanoScript do backend
docs/                       # documentação durável do projeto
openspec/                   # propostas, especificações, designs e tarefas
```

Os diretórios podem ser introduzidos à medida que forem necessários. A
estrutura acima é uma direção para novos módulos, não exige que a aplicação
atual seja reescrita antes de continuar o desenvolvimento.

## Responsabilidade de cada pasta

- **`pages/`**: funções de página e composição das telas ligadas a rotas do
  Reflex. Nem toda view precisa ter uma rota própria; fluxos como alternar
  entre login e cadastro podem ser partes da mesma página.
- **`components/`**: funções que retornam componentes Reflex reutilizáveis,
  como campos de formulário, cabeçalhos e cartões. Evitar colocar aqui estado
  de negócio, chamadas ao Xano ou páginas inteiras que não sejam reutilizadas.
- **`features/`**: estado Reflex, manipuladores de eventos, validações e
  operações específicas de cada capacidade do produto. Agrupar por domínio
  (`auth`, `tutors`, `pets`) mantém próximas as partes que mudam juntas.
- **`shared/`**: código realmente comum a várias funcionalidades, como o
  cliente HTTP do Xano e configuração compartilhada. Não antecipar abstrações
  antes de haver reutilização concreta.
- **`tests/`**: testes unitários e de integração. Testes que usam serviços
  externos devem ser identificados como integração e não depender de produção.

## Convenções de dependência

- `pages/` compõe componentes e conecta a interface ao estado das
  funcionalidades.
- `components/` não deve importar páginas nem controlar autenticação ou regras
  de domínio.
- `features/` pode usar `shared/` para integração, mas regras de autorização
  devem continuar garantidas pelo backend Xano.
- Segredos e credenciais não devem ser escritos em código, páginas,
  componentes ou documentação; usar configuração por ambiente.
- Manter os artefatos do backend em XanoScript e continuar tratando Xano como
  backend. Esta organização não introduz outro framework ou serviço.

## Aplicação gradual

O arquivo `vet_tech/vet_tech.py` atualmente concentra a entrada do app, estado,
comunicação HTTP, páginas e componentes. Novas funcionalidades podem ser
separadas por domínio sem exigir uma migração total imediata. Ao extrair um
módulo, preservar os fluxos existentes e verificar imports, registro de rotas
e build do Reflex.

O repositório contém diretórios XanoScript na raiz e também dentro de `xano/`.
Até confirmar qual localização é a fonte oficial usada pelo fluxo de trabalho,
não mover nem apagar esses arquivos e não manter novas cópias sincronizadas
manualmente.
