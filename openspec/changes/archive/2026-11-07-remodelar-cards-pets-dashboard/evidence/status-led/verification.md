# Contorno do Dashboard segue a barra de status

O seletor do contorno foi restrito ao SVG filho direto de cada card e seu
halo usa os mesmos tokens --dose-led/--dose-glow da barra. Não modifica datas,
cálculo de estado ou sombra dos cartões. Sem próxima dose, o LED fica apagado.

`dashboard_status_led_browser.py` aprovado com cinco pets sintéticos, um para
cada estado, nos temas claro e escuro. Compara a cor stroke calculada do
contorno à cor do indicador da barra, verifica LED oculto sem data,
pointer-events none e ciclo de 20 segundos com movimento reduzido.
Nenhuma exceção JavaScript. Capturas e results.json nesta pasta. CSS servido
sincronizado e whitespace validado.
