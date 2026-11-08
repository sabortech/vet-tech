# Assets de entrega

Versões WebP dos originais em `assets/`, mais favicon PNG de 64 px derivado da
marca atual. Os originais permanecem como fonte; fotos remotas de pets não são
alteradas. A conversão apenas reduz resolução excessiva/bytes, preservando
composição e transparência.

Para regenerar com Pillow disponível no ambiente de ferramentas:

```bash
.venv/bin/python scripts/optimize_ui_assets.py
```

`manifest.json` registra fontes, saídas, dimensões e tamanhos. Totais de origem
devem contar cada caminho uma única vez: a marca também é fonte do favicon.
O app serve os arquivos diretamente e não depende de Pillow em runtime para
essa otimização.
