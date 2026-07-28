/* Launch Forte, Pass 8: theme toggle.
   Starts INLINE in the .studio-nav-right container at the top of the page.
   When the viewport scrolls past a threshold, the button gets .scrolled and
   swaps to fixed positioning above the scroll-to-top arrow (bottom-right).
   Same pattern as the pre-Pass-8 toggle.

   Sets data-theme on <html> which studio.css responds to. Persists to
   localStorage under "lf-theme". Auto-detects system preference on first
   visit. Renders on every page that loads this script. */
(function () {
  var KEY = 'lf-theme';
  var SCROLL_TRIGGER = 120;   /* px scrolled before toggle floats out of the nav */

  function saved() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function persist(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  /* Apply as early as possible to avoid FOUC. This script is in <head>. */
  var initial = saved();
  if (!initial) {
    initial = (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
  }
  document.documentElement.setAttribute('data-theme', initial);

  var SUN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>';
  var MOON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';

  function apply(v) {
    document.documentElement.setAttribute('data-theme', v);
    persist(v);
    var btn = document.getElementById('studio-theme-toggle');
    if (btn) {
      btn.setAttribute('aria-label', v === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
      btn.innerHTML = v === 'dark' ? SUN : MOON;
    }
  }

  function inject() {
    if (document.getElementById('studio-theme-toggle')) return;

    var css = document.createElement('style');
    css.textContent =
      /* Inline (in the nav) — pill on the dark panel, matches Contact button rhythm */
      '#studio-theme-toggle{display:inline-flex;align-items:center;justify-content:center;' +
      'width:42px;height:42px;border-radius:8px;border:1px solid rgba(255,255,255,0.24);' +
      'background:transparent;color:#FFFFFF;cursor:pointer;padding:0;' +
      'transition:transform 180ms ease,border-color 180ms ease,background 180ms ease,color 180ms ease,box-shadow 200ms ease,' +
      'position 0ms ease,top 0ms,right 0ms,bottom 0ms}' +
      '#studio-theme-toggle:hover{border-color:var(--accent);color:var(--accent)}' +
      '#studio-theme-toggle svg{width:18px;height:18px;display:block}' +

      /* Scrolled — floats to bottom-right, above the scroll-top arrow, styled to read on paper */
      '#studio-theme-toggle.scrolled{position:fixed;right:2rem;bottom:8.5rem;z-index:1001;' +
      'width:42px;height:42px;border-radius:50%;border:1px solid rgba(0,0,0,0.14);' +
      'background:#FFFFFF;color:#0A0A0A;box-shadow:0 4px 15px rgba(0,0,0,0.10)}' +
      '#studio-theme-toggle.scrolled:hover{transform:translateY(-2px);border-color:var(--accent);color:var(--accent);' +
      'box-shadow:0 6px 20px rgba(0,136,219,0.28)}' +
      '[data-theme="dark"] #studio-theme-toggle.scrolled{background:#171717;color:#FFFFFF;' +
      'border-color:rgba(255,255,255,0.18);box-shadow:0 4px 15px rgba(0,0,0,0.45)}' +
      '[data-theme="dark"] #studio-theme-toggle.scrolled:hover{border-color:var(--accent);color:var(--accent)}' +

      '@media(max-width:480px){#studio-theme-toggle.scrolled{right:1.25rem;bottom:8rem;width:38px;height:38px}' +
      '#studio-theme-toggle.scrolled svg{width:16px;height:16px}}';
    document.head.appendChild(css);

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.id = 'studio-theme-toggle';
    var cur = document.documentElement.getAttribute('data-theme') || initial;
    btn.setAttribute('aria-label', cur === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    btn.innerHTML = cur === 'dark' ? SUN : MOON;
    btn.addEventListener('click', function () {
      var next = (document.documentElement.getAttribute('data-theme') === 'dark') ? 'light' : 'dark';
      apply(next);
    });

    /* Placement: inline in .studio-nav-right when it exists (Pass 8 pages),
       otherwise fixed-floating from the start (legacy pages we haven't restyled yet). */
    var host = document.querySelector('.studio-nav-right');
    if (host) {
      host.insertBefore(btn, host.firstChild);
    } else {
      btn.classList.add('scrolled');
      document.body.appendChild(btn);
    }

    /* Scroll behaviour: only if we started inline. */
    if (host) {
      var scrollHandler = function () {
        if (window.scrollY > SCROLL_TRIGGER) {
          if (!btn.classList.contains('scrolled')) {
            document.body.appendChild(btn);   /* move out of the nav */
            btn.classList.add('scrolled');
          }
        } else {
          if (btn.classList.contains('scrolled')) {
            btn.classList.remove('scrolled');
            host.insertBefore(btn, host.firstChild);   /* move back into the nav */
          }
        }
      };
      window.addEventListener('scroll', scrollHandler, { passive: true });
      /* Initial check in case the page loads already scrolled (deep link, refresh, etc). */
      scrollHandler();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }
})();
