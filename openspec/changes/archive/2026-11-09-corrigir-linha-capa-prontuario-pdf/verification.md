# Verificação

A linha divisória da capa passou a ser desenhada antes da mascote de canto. Coordenadas, cores, espessura e dimensões foram preservadas.

## Evidência visual

- PDF gerado localmente com a fixture sintética `export_payload` de `tests/unit/test_consultation_pdf.py`: [prontuario-sintetico.pdf](evidence/prontuario-sintetico.pdf).
- Capa rasterizada por `pdftoppm` e inspecionada visualmente: [capa.png](evidence/capa.png).
- A linha permanece à esquerda e fica encoberta pela tartaruga, sem atravessar o rosto. Identificação e textos da capa permanecem legíveis.
- Nenhum dado real ou chamada ao backend foi utilizado.

## Regressão

Comando: `.venv/bin/python -m unittest discover -s tests/unit -p test_consultation_pdf.py`.

Resultado: 9 testes passaram. A suíte verifica PDF válido, A4, acentos, conteúdo clínico, paginação com textos extensos, ausência de truncamento e limites do gerador.

Implementação concluída; especificação principal sincronizada e change arquivada por solicitação do usuário.

## Refinamento solicitado

A tartaruga foi deslocada 15 mm para a esquerda, preservando escala, altura e sobreposição à linha. PDF e imagem de evidência foram regenerados com a mesma fixture sintética. Inspeção visual confirmou o rosto mais afastado da borda direita e a linha encoberta. Os 9 testes passaram novamente (1,302 s).

### Posição final junto à borda

Após nova orientação do usuário, a posição horizontal passou a ser largura da página menos largura da imagem (220 pontos). Isso desloca a mascote aproximadamente 2,65 mm para a direita em relação ao refinamento anterior e alinha sua extremidade direita à borda da folha. Prévia e PDF foram atualizados; inspeção visual confirmou ausência de margem branca à direita da mascote e linha atrás dela. Os 9 testes passaram novamente (1,263 s).

### Aumento de 20%

A largura passou de 220 para 264 pontos, com posição horizontal igual à largura da página menos 264. Proporção, coordenada vertical e alinhamento à borda direita foram preservados. PDF e prévia foram regenerados e inspecionados: mascote maior, linha encoberta e textos livres. Os 9 testes passaram (1,277 s). O bitmap original de 202 × 166 pixels permanece intacto; a ampliação no layout não adiciona detalhes e pode evidenciar a resolução limitada, conforme informado ao usuário, que não possui outra versão da imagem.
