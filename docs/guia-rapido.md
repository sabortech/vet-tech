# Guia rápido do Vet Tech

## Acesso

Entre com o e-mail e a senha cadastrados. O sistema identifica automaticamente
se a conta pertence a um tutor ou a um veterinário.

## Tutor

- **Dashboard:** alterne entre todos os pets e um pet específico para consultar
  perfil, peso cadastrado, próxima dose registrada, consulta finalizada mais
  recente, próximo evento conhecido e atividade recente. As mensagens descrevem
  somente os registros consultados; não representam uma avaliação de saúde.
  Use os atalhos para iniciar um agendamento ou abrir Vacinas e Prontuário para
  o pet escolhido.
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

O Dashboard depende da publicação do endpoint `tutor/dashboard` no grupo clínico
do Xano; o código-fonte correspondente fica em
`xano/api/clinical/tutor_dashboard_GET.xs`. Sem esse endpoint, a tela apresenta
um erro de leitura e permite tentar novamente. A API é chamada por pet; no escopo
geral, o app carrega apenas os pets da lista autenticada, com no máximo quatro
chamadas simultâneas. As consultas clínicas validam novamente a propriedade do
tutor e retornam prévias ordenadas e limitadas, não o histórico clínico completo.

As alterações foram reunidas na branch `integracao/vet-tech`, no PR #5.
A verificação incluiu 134 testes unitários, compilação, build de produção,
validação do OpenSpec e navegação com os dois perfis.

O merge do código não publica automaticamente os contratos no Xano.
Os detalhes técnicos estão em [Verificação da integração](integration-verification.md).
