# Visualizador PDF local

PDF.js (`pdfjs-dist`) 6.5.438, Mozilla, licença Apache-2.0 em `LICENSE`.
Somente módulos de produção e worker, obtidos do pacote npm oficial.
Carregados sob demanda para renderizar o PDF gerado pelo servidor, sem CDN.
Não recebe URLs ou scripts clínicos. Nenhum PDF é persistido nestes assets.

Atualização: baixar uma versão explícita com `npm pack pdfjs-dist@<versão>` e substituir juntos `build/pdf.mjs` e `build/pdf.worker.mjs`, preservando a licença e verificando o harness de navegador.
