# Recuperação da navegação lateral — 07/11/2026

## Falha reproduzida

Após login com conta sintética existente, Dashboard e Configurações abriam,
mas Prontuário, Vacinas, Medicamentos, Doenças e Consultas falhavam ao importar
`/app/routes/[prontuario]._index.jsx`. O módulo de rota referenciava um export
`Foreach_comp_*` ausente no módulo servido de `pages/profile.jsx`.
React Router recarregava a página e recuperava o destino anterior; a hidratação
da sessão exibia temporariamente o login. Não foi necessário alterar as regras
de autenticação nem persistir credenciais no navegador.

## Correção operacional

Executado `.venv/bin/reflex compile` com sucesso (6,303 segundos) para regenerar
o conjunto completo da interface. A recompilação isolada ainda deixou um módulo
antigo no cache do servidor Vite; o frontend foi então reiniciado na porta
original 3000, mantendo o modo de desenvolvimento existente e o backend 8000.
Nenhuma edição parcial de módulos compilados foi usada na recuperação.

Para entregas futuras, regenerar o conjunto completo e reiniciar o frontend
quando houver mudança nos exports gerados. Não copiar apenas uma rota ou apenas
um módulo de componentes para um servidor em execução.

## Verificação

- `tests/integration/sidebar_navigation_live.py`: 16 cliques aprovados nos oito
  destinos funcionais, desktop claro 1440 px e celular escuro 390 px; URL e item
  ativo corretos, sem erro JavaScript/importação ou retorno ao login.
- Evidências: `navigation-live.json`, `navigation-1440.png`, `navigation-390.png`.
- Oito testes unitários de navegação e três de eficiência aprovados.
- Mais 48 testes de autenticação, carregamento clínico por pet e transporte
  Xano aprovados (59 testes unitários no total). OpenSpec validado pelo CLI.
- A verificação usa somente navegação/leitura com conta sintética existente;
  não cria, edita ou exclui registros clínicos.
- Os avisos preexistentes de hidratação de atributos/React Helmet não impediram
  a navegação. Não foram alterados nesta recuperação.
- Medidas de assets e concorrência permanecem em `metrics.json`; verificações
  anteriores de carregamento adiado e temas permanecem em `browser-results.json`.
