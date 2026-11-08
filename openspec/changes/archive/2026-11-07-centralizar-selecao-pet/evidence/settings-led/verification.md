# LEDs nos cartões de Configurações

Minha conta e Segurança recebem um contorno cada; Preferências recebe um
contorno em Aparência e outro em Navegação. Cada cartão define posição relativa
e isolamento diretamente no componente, com SVG ancorado ao próprio cartão,
curvas de 19 px e halo verde suave, sem interceptar cliques.

Compilação completa aprovada em 3,265 segundos. O roteiro
`tests/integration/settings_led_browser.py` passou nas portas 3000 e 3001,
em 1440/390 px e claro/escuro. Verifica troca real das três abas, ausência
de overflow, limites de cartão/LED medidos atomicamente com tolerância de
2 px (32 cartões verificados), pointer-events none e ciclo reduzido de
20 segundos. Nenhum dado de conta ou senha foi enviado para alteração.
Capturas e results.json nas pastas 3000/3001. Whitespace validado.
