# Fundo nos cantos da sidebar

A estampa foi estendida de `.app-content` para `.app-layout`, responsável
pelo fundo exposto atrás dos cantos arredondados da sidebar. Os mesmos
arquivos e cores são usados nos dois contêineres, no claro e no escuro.

`pet_page_backgrounds_browser.py` aprovado na porta 3001: verifica cores e
imagens calculadas de ambos os contêineres em Meus Pets, Mudar pet,
Configurações e Prontuário sem seleção, em 1440/390 px e nos dois temas.
16 combinações aprovadas sem overflow horizontal nem exceções JavaScript.
Capturas/results.json na pasta 3001. CSS servido sincronizado; whitespace
validado. Bordas e cor do menu não foram alteradas.
