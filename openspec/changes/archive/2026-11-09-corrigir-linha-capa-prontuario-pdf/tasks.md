# Tasks

## 1. Corrigir composição da capa

- [x] 1.1 Em `_cover` de `consultation_pdf_template.py`, desenhar a linha divisória antes de `mascote-canto.png`, mantendo coordenadas e estilos; gerar PDF com dados sintéticos e conferir visualmente que a linha desaparece atrás da silhueta da tartaruga.
- [x] 1.2 Executar `.venv/bin/python -m unittest discover -s tests/unit -p test_consultation_pdf.py` e registrar resultado e prévia sintética em `verification.md` e `evidence/` desta change, confirmando preservação do conteúdo e paginação.

O artefato opcional `design.md` foi dispensado: correção localizada de ordem de desenho, sem alterações arquiteturais, dependências novas ou decisões técnicas em aberto.

## 2. Refinar posição da tartaruga

- [x] 2.1 Deslocar a tartaruga 15 mm para a esquerda, preservando altura, escala e linha atrás; atualizar a prévia sintética, inspecionar a capa e executar novamente os testes de PDF, registrando o resultado.
- [x] 2.2 Refinar a posição para alinhar a extremidade direita da tartaruga à borda do papel, eliminando a margem branca; regenerar e inspecionar a prévia e executar os testes de PDF.
- [x] 2.3 Aumentar a tartaruga de 220 para 264 pontos (20%), preservando proporção, alinhamento direito e linha atrás; verificar prévia sintética e testes de PDF.
