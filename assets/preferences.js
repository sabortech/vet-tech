/* Applied in <head> before the first paint, including public pages and portals. */
(() => {
  if (window.vetTechPreferences) return;
  const key = 'vet_tech_theme';
  let persistent = true;
  // Reflex also reads the existing sidebar preference: provide a page-local
  // store when the browser denies localStorage so hydration remains usable.
  try {
    const probe = '__vettech_storage_probe__';
    localStorage.setItem(probe, '1'); localStorage.getItem(probe); localStorage.removeItem(probe);
  } catch (_) {
    persistent = false;
    const values = new Map();
    const memory = {getItem: key => values.get(String(key)) ?? null,
      setItem: (key, value) => values.set(String(key), String(value)),
      removeItem: key => values.delete(String(key)), clear: () => values.clear(),
      key: index => [...values.keys()][index] ?? null, get length() { return values.size; }};
    try { Object.defineProperty(window, 'localStorage', {value: memory, configurable: true}); } catch (_) {}
  }
  let theme = 'light';
  try { theme = localStorage.getItem(key) === 'dark' ? 'dark' : 'light'; } catch (_) {}
  const syncControls = () => {
    const control = document.getElementById('theme-switch');
    if (control) { control.checked = theme === 'dark'; control.setAttribute('aria-checked', String(control.checked)); }
  };
  const apply = value => {
    theme = value === 'dark' ? 'dark' : 'light';
    document.documentElement.dataset.vtTheme = theme;
    document.documentElement.style.colorScheme = theme;
    syncControls();
  };
  apply(theme);
  window.vetTechPreferences = {getTheme: () => theme};
  window.addEventListener('storage', event => {
    if (event.key === key || event.key === null) apply(event.newValue);
  });
  document.addEventListener('change', event => {
    if (event.target.matches('[data-vt-preference="theme"]')) {
      apply(event.target.checked ? 'dark' : 'light');
      let saved = persistent;
      try { localStorage.setItem(key, theme); } catch (_) { saved = false; }
      const feedback = document.getElementById('theme-feedback');
      if (feedback) feedback.textContent = saved ? 'Preferência atualizada neste navegador.' : 'Tema aplicado nesta página. Não foi possível salvar neste navegador.';
    }
  });
  document.addEventListener('click', event => {
    const button = event.target.closest('[data-password-target]');
    if (!button) return;
    const input = document.getElementById(button.dataset.passwordTarget);
    const show = input.type === 'password';
    input.type = show ? 'text' : 'password';
    button.setAttribute('aria-pressed', String(show));
    button.setAttribute('aria-label', (show ? 'Ocultar ' : 'Mostrar ') + document.querySelector(`label[for="${input.id}"]`).textContent.toLowerCase());
  });
  document.addEventListener('keydown', event => {
    const tab = event.target.closest('.settings-tab');
    if (!tab || !['ArrowRight', 'ArrowLeft', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    const tabs = [...document.querySelectorAll('.settings-tab')];
    let index = tabs.indexOf(tab);
    index = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : (index + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
    tabs[index].focus(); tabs[index].click();
  });
  const dirty = () => {
    const root = document.querySelector('.settings-page');
    if (!root || !document.getElementById('settings-account-form')) return false;
    try {
      const baseline = JSON.parse(root.dataset.baseline || '{}');
      return Object.entries(baseline).some(([key, value]) =>
        document.getElementById('settings-' + key)?.value.trim() !== value);
    } catch (_) { return root.dataset.dirty === 'true'; }
  };
  // Clean links navigate in the client router; only unsaved edits need the server guard.
  document.addEventListener('click', event => {
    const link = event.target.closest('.sidebar a.sidebar-item');
    if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const destination = new URL(link.href, location.href);
    if (destination.pathname.replace(/\/$/, '') === location.pathname.replace(/\/$/, '')) {
      event.preventDefault(); event.stopImmediatePropagation(); return;
    }
    const saving = document.querySelector('.settings-page')?.dataset.saving === 'true';
    if (!dirty() && !saving) return;
    event.preventDefault(); event.stopImmediatePropagation();
    if (!saving) document.getElementById('settings-sidebar-guard')?.click();
  }, true);
  window.addEventListener('beforeunload', event => {
    if (dirty()) { event.preventDefault(); event.returnValue = ''; }
  });
  let restoring = false, leaving = false;
  window.vetTechLeaveHistory = () => { leaving = true; history.back(); };
  window.addEventListener('popstate', event => {
    if (restoring) { restoring = false; event.stopImmediatePropagation(); return; }
    if (leaving) { leaving = false; return; }
    if (dirty()) {
      event.stopImmediatePropagation(); restoring = true; history.go(1);
      document.getElementById('settings-history-guard')?.click();
    }
  });
  new MutationObserver(syncControls).observe(document.documentElement, {childList: true, subtree: true});
})();
