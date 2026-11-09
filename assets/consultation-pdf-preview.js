/* Local PDF.js viewer. One document per open panel; no storage or remote URLs. */
(() => {
  if (window.vetTechPDFPreview) return;
  let active = null;
  let library;
  const clear = () => {
    const old = active;
    active = null;
    if (!old) return;
    old.observer?.disconnect();
    old.resize?.disconnect();
    for (const task of old.tasks) task.cancel();
    old.loading?.destroy().catch(() => {});
    old.host.replaceChildren();
  };
  const current = view => active === view && view.host.isConnected && view.host.dataset.previewToken === view.token;
  const show = async (encoded, token) => {
    const host = document.getElementById('consultation-pdf-pages');
    if (!host || host.dataset.previewToken !== token) return;
    clear();
    const view = {host, token, tasks: new Set(), queue: new Set(), working: false};
    active = view;
    host.textContent = 'Carregando as páginas do PDF…';
    try {
      library ||= import('/pdf-viewer/pdf.mjs');
      const pdfjs = await library;
      if (!current(view)) return;
      pdfjs.GlobalWorkerOptions.workerSrc = '/pdf-viewer/pdf.worker.mjs';
      const raw = atob(encoded);
      const data = Uint8Array.from(raw, c => c.charCodeAt(0));
      encoded = null;
      view.loading = pdfjs.getDocument({data, isEvalSupported: false});
      const doc = await view.loading.promise;
      if (!current(view)) return;
      view.doc = doc;
      const first = await doc.getPage(1);
      const dimensions = first.getViewport({scale: 1});
      if (!current(view)) return;
      host.replaceChildren();
      host.dataset.pageCount = String(doc.numPages);
      const renderQueue = async () => {
        if (view.working) return;
        view.working = true;
        try {
          while (current(view) && view.queue.size) {
            const slot = view.queue.values().next().value;
            view.queue.delete(slot);
            if (!slot.visible || slot.dataset.rendered === 'true') continue;
            const page = await doc.getPage(Number(slot.dataset.page));
            if (!current(view) || !slot.visible) continue;
            const width = slot.clientWidth;
            const viewport = page.getViewport({scale: width / dimensions.width});
            const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
            const canvas = slot.querySelector('canvas');
            canvas.width = Math.floor(viewport.width * dpr);
            canvas.height = Math.floor(viewport.height * dpr);
            const task = page.render({canvasContext: canvas.getContext('2d'), viewport,
              transform: dpr === 1 ? null : [dpr, 0, 0, dpr, 0, 0]});
            view.tasks.add(task);
            slot.renderTask = task;
            try { await task.promise; } catch (e) {
              if (e.name !== 'RenderingCancelledException') throw e;
            } finally { view.tasks.delete(task); slot.renderTask = null; }
            if (current(view) && slot.visible) slot.dataset.rendered = 'true';
          }
        } finally { view.working = false; }
      };
      const queue = slot => {
        view.queue.add(slot);
        renderQueue().catch(() => {
          if (current(view)) host.setAttribute('aria-label', 'Não foi possível desenhar uma página. Feche a prévia e tente novamente.');
        });
      };
      view.observer = new IntersectionObserver(entries => {
        for (const entry of entries) {
          const slot = entry.target;
          slot.visible = entry.isIntersecting;
          if (slot.visible) queue(slot);
          else {
            view.queue.delete(slot);
            slot.renderTask?.cancel();
            slot.dataset.rendered = 'false';
            const canvas = slot.querySelector('canvas');
            canvas.width = canvas.height = 0;
          }
        }
      }, {root: host, rootMargin: '160px 0px'});
      for (let n = 1; n <= doc.numPages; n++) {
        const slot = document.createElement('figure');
        slot.dataset.page = String(n);
        slot.style.aspectRatio = `${dimensions.width} / ${dimensions.height}`;
        slot.setAttribute('aria-label', `Página ${n} de ${doc.numPages}`);
        const canvas = document.createElement('canvas');
        canvas.setAttribute('aria-label', `Página ${n} do prontuário`);
        const label = document.createElement('figcaption');
        label.className = 'pdf-preview-page-number';
        label.textContent = `${n} / ${doc.numPages}`;
        slot.append(canvas, label); host.append(slot); view.observer.observe(slot);
      }
      let lastWidth = host.clientWidth;
      view.resize = new ResizeObserver(() => {
        if (host.clientWidth === lastWidth) return;
        lastWidth = host.clientWidth;
        for (const slot of host.children) {
          slot.dataset.rendered = 'false';
          if (slot.visible) queue(slot);
        }
      });
      view.resize.observe(host);
    } catch (_) {
      if (current(view)) host.textContent = 'Não foi possível abrir a prévia. Feche o painel e tente novamente.';
    }
  };
  window.vetTechPDFPreview = {show, clear};
  const observer = new MutationObserver(() => {
    if (active && !current(active)) clear();
  });
  const watch = () => observer.observe(document.body, {childList: true, subtree: true, attributes: true, attributeFilter: ['data-preview-token']});
  if (document.body) watch(); else window.addEventListener('DOMContentLoaded', watch, {once: true});
  window.addEventListener('pagehide', clear);
})();
