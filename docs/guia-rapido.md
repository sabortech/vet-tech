# Guia rápido do Vet Tech

## Acesso

Entre com o e-mail e a senha cadastrados. O sistema identifica automaticamente
se a conta pertence a um tutor ou a um veterinário.

## Tutor

- **Meus Pets:** consulte os animais cadastrados, selecione um pet ou cadastre
  um novo animal.
- **Prontuário:** acesse a área clínica para acompanhar consultas e o histórico
  do pet, conforme as opções disponíveis.
- **Configurações → Minha conta:** atualize nome, telefone e endereço. E-mail e
  CPF são exibidos apenas para consulta.
- **Configurações → Segurança:** informe a senha atual, a nova senha e sua
  confirmação. Após a alteração, entre novamente.
- **Configurações → Preferências:** ative o modo escuro e escolha se o menu
  lateral deve permanecer expandido. Essas preferências ficam salvas no navegador.
  O tema vale para todo o sistema, incluindo o menu lateral, login e cadastro.

## Veterinário

A área veterinária reúne horários, consultas e atendimentos. O acesso aos dados
clínicos segue as permissões aplicadas pelo backend.

## Integração

As alterações foram reunidas na branch `integracao/vet-tech`, no PR #5.
A verificação incluiu 134 testes unitários, compilação, build de produção,
validação do OpenSpec e navegação com os dois perfis.

O merge do código não publica automaticamente os contratos no Xano.
Os detalhes técnicos estão em [Verificação da integração](integration-verification.md).
