## INTRODUCAO - OQUE É O VET TECH?

O VetTech é um sistema que atende clínicas veterinárias, veterinários e tutores de pets, com o objetivo de centralizar o histórico de saúde dos animais.
 
 ## REGRAS DE NEGÓCIOS DO SISTEMA

Cada tutor se cadastra no sistema informando nome, CPF, e-mail, telefone, endereço e senha. Um tutor pode possuir um ou mais pets. 

Cada pet possui nome, espécie, raça, sexo, data de nascimento, peso, cor da pelagem, número de microchip(quando houver)e foto. Todo pet está vinculado a exatamente um tutor responsável.

As espécies (cachorro, gato, ave etc.) e raças são cadastradas de forma padronizada no sistema, sendo que cada raça pertence a uma única espécie.

Os veterinários também se cadastram no sistema, informando nome, CRMV (registro profissional), especialidade, e-mail, telefone e senha. 

Cada veterinário está vinculado a uma clínica, que possui nome, CNPJ, endereço e telefone. Uma clínica pode empregar vários veterinários.

Quando um pet é levado a atendimento, é registrada uma consulta, contendo a data, o motivo do atendimento, o diagnóstico do veterinário e observações adicionais. Uma consulta está sempre associada a um pet e a um veterinário responsável pelo atendimento. 

A partir de uma consulta, podem ser solicitados um ou mais exames, cada um contendo tipo, data, resultado e, quando aplicável, um arquivo anexado (laudo, imagem etc.). Também é possível registrar exames sem vínculo direto a uma consulta específica.

Durante o acompanhamento do pet, também são registradas vacinas aplicadas — com nome da vacina, data de aplicação, lote e data prevista para a próxima dose — e medicamentos prescritos, com nome, dosagem, frequência, período de uso e tipo (contínuo, vermífugo, antipulgas, entre outros).

O sistema também mantém um cadastro de doenças conhecidas, com nome, descrição, tipo e gravidade. Uma doença pode ser diagnosticada em uma consulta específica, e também pode ser registrada no histórico consolidado do pet, indicando se está ativa, em tratamento, curada ou controlada — permitindo que o tutor e qualquer veterinário autorizado saibam rapidamente das condições de saúde do animal.

Por questões de privacidade, um veterinário só pode visualizar ou editar o prontuário de um pet se o tutor tiver concedido autorização de acesso. Essa autorização pode ser concedida ou revogada pelo tutor a qualquer momento. Todo acesso ao prontuário — seja visualização, edição ou exportação — é registrado em um histórico de auditoria, contendo a data, o veterinário responsável e a ação realizada.

## Relacionamentos

## TUTOR

Um tutor deve possuir CPF e e-mail únicos no sistema (não pode haver dois cadastros com o mesmo CPF ou e-mail)
Um tutor pode cadastrar um ou mais pets
Um tutor é o único que pode conceder ou revogar acesso de veterinários aos seus pets
Um tutor só pode visualizar e gerenciar os pets vinculados a ele
Relaciona-se com: PET (1:N) e NOTIFICACAO (1:N)

## VETERINARIO
Um veterinário deve possuir CRMV único no sistema, garantindo que é um profissional habilitado
opcional:Um veterinário está sempre vinculado a uma clínica
Um veterinário só pode acessar o prontuário de um pet se possuir autorização ativa concedida pelo tutor
Um veterinário pode realizar consultas, aplicar vacinas e registrar diagnósticos em qualquer pet ao qual tenha acesso autorizado
Relaciona-se com: CLINICA (N:1), CONSULTA (1:N), VACINA (1:N), ACESSO_AUTORIZADO (1:N), LOG_ACESSO (1:N)

## CLINICA
Uma clínica deve possuir CNPJ único
Uma clínica pode empregar vários veterinários
Uma clínica não acessa diretamente o prontuário dos pets — esse acesso é sempre individual, por veterinário autorizado
Relaciona-se com: VETERINARIO (1:N)

## ESPECIE
Toda espécie cadastrada deve ter nome único (ex: não pode haver duas entradas para "Cachorro")
Uma espécie pode conter várias raças
Relaciona-se com: RACA (1:N), PET (1:N)

## RACA
Uma raça pertence obrigatoriamente a uma única espécie
Não é permitido vincular uma raça a uma espécie diferente da qual ela pertence (ex: "Labrador" não pode ser associado a "Gato")
O campo raça no pet pode ficar em branco, representando um animal sem raça definida (SRD)
Relaciona-se com: ESPECIE (N:1), PET (1:N)

## PET
Todo pet deve estar vinculado a exatamente um tutor responsável
Um pet pode ter vários veterinários autorizados a acessar seu histórico, mas apenas mediante permissão do tutor
Um pet acumula, ao longo do tempo, múltiplas consultas, exames, vacinas, medicamentos e diagnósticos de doenças
O histórico do pet nunca é apagado, mesmo que o tutor mude de clínica ou de veterinário
Relaciona-se com: TUTOR (N:1), ESPECIE (N:1), RACA (N:1), CONSULTA (1:N), EXAME (1:N), VACINA (1:N), MEDICAMENTO (1:N), PET_DOENCA (1:N), ANEXO (1:N), NOTIFICACAO (1:N), ACESSO_AUTORIZADO (1:N), LOG_ACESSO (1:N)

## CONSULTA
Toda consulta deve estar vinculada a um pet e a um veterinário responsável pelo atendimento
Uma consulta pode gerar um ou mais exames complementares
Uma consulta pode resultar no diagnóstico de uma ou mais doenças, registradas através da associação com DOENCA
Relaciona-se com: PET (N:1), VETERINARIO (N:1), EXAME (1:N), CONSULTA_DOENCA (1:N)

## EXAME
Um exame está sempre vinculado a um pet
Um exame pode ou não estar vinculado a uma consulta específica (é possível registrar exames avulsos, sem consulta associada)
Um exame contem no minimo 1 arquivo anexado (laudo, imagem, PDF)
Relaciona-se com: PET (N:1), CONSULTA (N:1, opcional)

## VACINA
Toda vacina aplicada deve estar vinculada a um pet e ao veterinário responsável pela aplicação
O sistema deve armazenar a data de aplicação e, quando aplicável, a data prevista da próxima dose, para permitir a geração de lembretes automáticos
Relaciona-se com: PET (N:1), VETERINARIO (N:1), NOTIFICACAO (1:N, indireta via referência)

## MEDICAMENTO
Todo medicamento prescrito deve estar vinculado a um pet
Um medicamento pode ser classificado como contínuo (sem data de fim definida), vermífugo, antipulgas/carrapatos, ou outro
Relaciona-se com: PET (N:1)

## DOENCA
Uma doença é um cadastro genérico (ex: "Dermatite"), reutilizável entre diferentes pets e consultas
Uma doença pode estar associada a várias consultas (diagnóstico pontual) e a vários pets (histórico consolidado)
Relaciona-se com: CONSULTA (N:N, via CONSULTA_DOENCA), PET (N:N, via PET_DOENCA)

## ANEXO
Um anexo está sempre vinculado a um pet, podendo ser uma foto, receita, laudo ou outro tipo de documento
Um anexo não depende de uma consulta ou exame específico para existir
Relaciona-se com: PET (N:1)
 
## OPCIONAL

## NOTIFICACAO
Toda notificação está vinculada a um pet e ao tutor que deve recebê-la
Uma notificação pode se referir a um evento específico (vacina, medicamento, retorno), identificado por uma referência genérica
O sistema deve controlar se a notificação já foi enviada e se já foi visualizada pelo tutor
Relaciona-se com: PET (N:1), TUTOR (N:1)

## ACESSO_AUTORIZADO
Só o tutor do pet pode criar, manter ou revogar uma autorização de acesso
Um pet pode ter múltiplos veterinários autorizados simultaneamente
Um veterinário só pode consultar, editar ou exportar dados de um pet enquanto sua autorização estiver com status "ativo"
Ao revogar o status, o veterinário perde imediatamente o acesso ao prontuário daquele pet
Relaciona-se com: PET (N:1), VETERINARIO (N:1)

## LOG_ACESSO
Todo acesso de um veterinário a um prontuário — visualização, edição ou exportação — gera automaticamente um registro de log
O log não pode ser editado ou apagado por nenhum usuário, servindo como trilha de auditoria imutável
O log permite ao tutor (e à administração do sistema) verificar quem acessou os dados do pet e quando
Relaciona-se com: PET (N:1), VETERINARIO (N:1)