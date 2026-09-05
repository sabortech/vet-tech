
## 1. Visão geral

VetTech é uma plataforma web de prontuário digital para pets, que centraliza o histórico médico completo de cada animal em um único ambiente seguro e acessível. O sistema conecta tutores e veterinários, permitindo que o histórico de saúde do pet acompanhe o animal ao longo de toda a vida — independentemente de mudanças de clínica, cidade ou veterinário responsável.

 ## 2. Problema

Atualmente, o histórico médico de pets está fragmentado entre cadernetas de papel, arquivos físicos e sistemas isolados de cada clínica. Isso gera repetição desnecessária de exames, risco de erro médico por falta de informação (ex: alergias não comunicadas), perda de continuidade no acompanhamento de doenças crônicas e dificuldade de controle de vacinas e medicações por parte do tutor.


## 3. Objetivos

Centralizar o histórico médico completo de cada pet em um único sistema
Garantir que o prontuário acompanhe o pet independentemente da clínica atendida
Reduzir riscos médicos causados por falta de informação em atendimentos
Dar ao tutor controle sobre quem acessa os dados do seu animal
Facilitar o acompanhamento de vacinas, medicações e retornos através de lembretes automáticos

## 4. Público-alvo / usuários


Tutores de pets — buscam organização e controle sobre a saúde de seus animais
Veterinários e clínicas veterinárias — precisam de acesso rápido e confiável ao histórico do paciente
Clínicas de emergência/plantão — se beneficiam do acesso rápido a informações críticas em situações urgentes

## 5. Escopo


O projeto contempla o desenvolvimento de uma aplicação web com cadastro de tutores, veterinários e clínicas; perfil completo do pet; registro de consultas, exames, vacinas, medicamentos e doenças; sistema de permissões de acesso; e notificações automáticas. Não fazem parte do escopo inicial: módulo de pagamento, telemedicina em vídeo, ou aplicativo mobile nativo (podendo ser considerados como evolução futura).


## 6. Principais funcionalidades


Cadastro e autenticação de tutores e veterinários
Perfil digital do pet (dados, foto, espécie, raça)
Histórico médico (consultas, exames, diagnósticos)
Carteira de vacinação com alertas de reforço
Controle de medicamentos (contínuos, vermífugo, antipulgas)
Registro de doenças (diagnóstico pontual e histórico consolidado)
Sistema de permissões — tutor autoriza/revoga acesso de veterinários
Log de auditoria (quem acessou, editou ou exportou dados)
Notificações automáticas (vacina, retorno, medicamento)
Exportação de relatório em PDF do histórico completo


## 7. Requisitos e restrições importantes

Apenas o tutor pode autorizar ou revogar o acesso de um veterinário ao prontuário do seu pet
Um veterinário só pode visualizar/editar dados de pets aos quais foi explicitamente autorizado
Toda ação sensível (visualização, edição, exportação) deve ser registrada em log, alinhado a princípios da LGPD
Senhas devem ser armazenadas com hash, nunca em texto puro
O sistema deve suportar múltiplas clínicas e múltiplos veterinários por pet, sem duplicar o histórico


## 8. Arquitetura tecnológica

Banco de dados:Xano

Backend: camada de API responsável pelas regras de negócio, autenticação e validações

Frontend: interface web responsiva, com dashboards distintos para tutor e veterinário, feita com python usando a biblioteca reflex


Armazenamento de arquivos: suporte a anexos (exames, laudos, receitas) via URL/arquivo vinculado ao pet


## 9. Princípios de desenvolvimento

Modelagem orientada ao usuário final (pet e tutor no centro do sistema, não a clínica)
Normalização do banco de dados para evitar inconsistência (ex: Espécie/Raça padronizadas)
Uso de tabelas associativas para relacionamentos N:N (Pet-Veterinário, Pet-Doença, Consulta-Doença)
Documentação incremental do modelo à medida que novas necessidades são identificadas


## 10. Segurança e integridade

Controle de acesso baseado em autorização explícita do tutor
Auditoria completa de acessos e alterações via LOG_ACESSO
Separação de responsabilidades entre perfis de usuário (tutor x veterinário)
Integridade referencial garantida por chaves estrangeiras (FK) entre todas as entidades relacionadas
Recomendação de validação adicional na camada de aplicação (ex: raça deve pertencer à espécie selecionada)

## 11. Estratégia de desenvolvimento

Modelagem do banco de dados (DER e xanoscript)
Definição da arquitetura (backend/frontend)
Desenvolvimento incremental por módulo (cadastro → prontuário → permissões → notificações)
Testes com dados simulados (mock data)
Ajustes de usabilidade nas telas do tutor e do veterinário
Documentação final para entrega acadêmica


## 12. Fonte de verdade e documentação
O modelo de dados (DER) e o Xano/xanoscript são a fonte de verdade da estrutura do sistema, servindo de base para o desenvolvimento do backend e frontend. Toda alteração na modelagem deve ser refletida tanto no diagrama quanto no script xanoscript, mantendo consistência entre documentação técnica e implementação.