# Design

## Contexto
Login e cadastro usam cards divididos entre formulário e imagem. Ver motivação em proposal.md. O acabamento foi aplicado em ambos e o percurso em infinito foi revertido a pedido do usuário.

## Objetivos e limites
Reutilizar a decoração existente sem alterar campos, validações ou eventos de autenticação.

## Decisões
Reutilizar perimeter_led de date_input nos dois cards, em vez de duplicar SVG. Aplicar classe auth-led-card para posicionamento relativo, isolamento e sombra verde; preservar o recorte e os raios existentes. O SVG ignora ponteiro e tecnologia assistiva. A regra compartilhada de movimento reduzido mantém o ciclo mais lento. A alternativa de dois laços pela divisória foi descartada por solicitação final do usuário.

## Riscos e mitigação
Recorte ou sobreposição da decoração → verificar as duas rotas em desktop e celular, manter SVG sem eventos de ponteiro e dimensões relativas ao card.

## Entrega e reversão
Compilar Reflex e sincronizar o CSS servido. Para reverter o acabamento, remover somente a decoração e a classe dos dois cards. Sem migração de dados.
