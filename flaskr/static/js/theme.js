(function(){
  const KEY = 'embertech_theme';
  const btn = document.getElementById('theme-toggle');
  if (!btn) return;

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    btn.setAttribute('aria-pressed', theme === 'light' ? 'true' : 'false');
    btn.textContent = theme === 'light' ? '☀️' : '🌙';
    localStorage.setItem(KEY, theme);
  }

  function currentFromStorageOrSystem() {
    const stored = localStorage.getItem(KEY);
    if (stored === 'light' || stored === 'dark') return stored;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  }

  btn.addEventListener('click', () => {
    const now = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
    applyTheme(now);
  });

  try { applyTheme(currentFromStorageOrSystem()); } catch (e) { console.error('theme init failed', e); }
})();
