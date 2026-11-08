# Enquadramento dos LEDs de Meus Pets

Cadastro e lista definem posicionamento relativo e isolamento diretamente
nos componentes, além da classe local. SVGs têm âncora absoluta direta no
respectivo cartão, curvas de 19 px para a borda de 20 px e halo suavizado.

Compilação aprovada em 3,519 segundos. `tests/integration/pets_led_browser.py`
passou nas portas 3000 e 3001, em 1440/390 px e claro/escuro. Os testes
comparam x/y/largura/altura reais dos dois LEDs com os respectivos cartões,
com tolerância de 2 px de borda, em 16 combinações. Também verificam ausência
de overflow horizontal, eventos de formulário/lista, pointer-events none e
ciclo de 20 segundos com movimento reduzido. Capturas e resultados nas pastas
3000/3001. Nenhum LED usa os limites da página nesses testes.
