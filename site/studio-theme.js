/* Launch Forte, Pass 8: theme toggle.
   Sets data-theme on <html>. studio.css responds to [data-theme="dark"]
   and [data-theme="light"]. Persists to localStorage. Auto-detects
   system preference on first visit. Renders a small toggle inside the
   .studio-nav-right container on every page that has it. */
(function () {
  var KEY = 'lf-theme';

  function saved() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function persist(v) {
    try { localStorage.setItem(KEY, v); } catch (e) {}
  }

  /* Apply as early as possible to avoid FOUC. This script is in <head>. */
  var initial = saved();
  if (!initial) {
    initial = (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
  }
  document.documentElement.setAttribute('data-theme', initial);

  function apply(v) {
    document.documentElement.setAttribute('data-theme', v);
    persist(v);
    var btn = document.getElementById('studio-theme-toggle');
    if (btn) {
      btn.setAttribute('aria-label', v === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
      btn.innerHTML = v === 'dark' ? SUN : MOON;
    }
  }

  var SUN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>';
  var MOON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';

  function inject() {
    var host = document.querySelector('.studio-nav-right');
    if (!host || document.getElementById('studio-theme-toggle')) return;
    var css = document.createElement('style');
    css.textContent =
      '#studio-theme-toggle{display:inline-flex;align-items:center;justify-content:center;' +
      'width:42px;height:42px;border-radius:8px;border:1px solid rgba(255,255,255,0.24);' +
      'background:transparent;color:#FFFFFF;cursor:pointer;padding:0;' +
      'transition:border-color 180ms ease,color 180ms ease,background 180ms ease}' +
      '#studio-theme-toggle:hover{border-color:var(--accent);color:var(--accent)}' +
      '#studio-theme-toggle svg{width:18px;height:18px;display:block}';
    document.head.appendChild(css);

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.id = 'studio-theme-toggle';
    btn.setAttribute('aria-label', initial === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    btn.innerHTML = initial === 'dark' ? SUN : MOON;
    btn.addEventListener('click', function () {
      var next = (document.documentElement.getAttribute('data-theme') === 'dark') ? 'light' : 'dark';
      apply(next);
    });
    /* Sit before the Contact button so it reads left-to-right: [theme] [Contact] [hamburger] */
    host.insertBefore(btn, host.firstChild);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }
})();
