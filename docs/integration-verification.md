# Verificação da branch de integração

Data: 2026-10-25. Branch: `integracao/vet-tech`.

A integração preserva os históricos de `cadastro-pet`, `alternar-pet`,
`fundo-login` e `teste`, além das alterações já presentes em `main`.

## Resoluções da integração

- A tela existente de Meus Pets permanece em `/`; a área clínica fica em
  `/prontuario`, com acesso ao atendimento e retorno a Meus Pets e Configurações.
- O login compartilhado identifica tutor ou veterinário pelo backend. Configurações
  permanece restrita ao tutor e limpa seus dados ao trocar de sessão.
- O tema e a preferência de expansão do menu são compartilhados pelas interfaces.
- Os contratos Xano duplicados foram consolidados, preservando as regras de
  autorização e os campos obrigatórios da fundação. As funções locais ficam em
  `xano/function/clinical`, sem diretórios diferenciados apenas por maiúsculas.
- Repetições de HTTP 429 ficam restritas ao grupo clínico; autenticação não repete
  automaticamente credenciais. Mensagens do backend continuam filtradas.
- O cache gerado `reflex.lock` saiu do versionamento para permitir sua regeneração
  com as dependências atuais.
- Os dois registros históricos de planejamento do prontuário foram preservados.
  A change recebida `fluxo-consultas-prontuario` permanece no estado de origem.

## Verificação

- 134 testes unitários passaram (`python -m unittest discover -s tests/unit`).
- `reflex compile --dry` passou.
- `openspec validate --all --strict` validou os 14 itens.
- O build de produção foi concluído e a aplicação iniciou na porta 3000.
- O teste no navegador passou com login de tutor e veterinário, Meus Pets,
  Configurações, tema global, acesso ao prontuário e abertura/fechamento do
  formulário de novo pet, sem erros JavaScript capturados.

Esta integração não publica alterações no Xano nem repete toda a suíte de
mutações clínicas remotas. A publicação do backend continua sendo uma etapa
separada dos commits e do merge do repositório.
