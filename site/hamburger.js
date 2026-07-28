(function () {
    var css = [
        '.site-header{z-index:200!important}',

        /* Active nav indicator: strong accent color + underline beneath the active tab */
        '.header-nav a{position:relative}',
        '.header-nav a.active{color:var(--accent,#0088DB)!important;opacity:1!important;font-weight:600!important;background:transparent!important}',
        '.header-nav a.active::after{content:"";position:absolute;left:0.75rem;right:0.75rem;bottom:-2px;height:2px;background:var(--accent,#0088DB);border-radius:2px}',
        '[data-theme="dark"] .header-nav a.active{color:#4ab5ed!important}',
        '[data-theme="dark"] .header-nav a.active::after{background:#4ab5ed}',

        '#hamburger{display:none;flex-direction:column;justify-content:center;align-items:center;gap:5px;width:42px;height:42px;background:transparent;border:1px solid var(--border,#1e293b);border-radius:8px;cursor:pointer;padding:0;flex-shrink:0;transition:border-color 0.2s ease}',
        '#hamburger:hover{border-color:var(--accent,#0088DB)}',
        '#hamburger span{display:block;width:18px;height:2px;background:var(--text-primary,#f0f4f8);border-radius:2px;transition:transform 0.3s cubic-bezier(0.16,1,0.3,1),opacity 0.2s ease}',
        '#hamburger.open span:nth-child(1){transform:translateY(7px) rotate(45deg)}',
        '#hamburger.open span:nth-child(2){opacity:0}',
        '#hamburger.open span:nth-child(3){transform:translateY(-7px) rotate(-45deg)}',

        /* Overlay is always dark, both themes (matches Studio: nav overlay is a black panel). */
        '#mobile-nav{display:none;position:fixed;top:0;left:0;right:0;bottom:0;z-index:199;background:#0A0A0A;padding:100px 2rem 2rem;overflow-y:auto;flex-direction:column;gap:0;opacity:0;transition:opacity 0.3s ease}',
        '#mobile-nav.open{display:flex;opacity:1}',
        '#mobile-nav a{display:block;color:#FFFFFF;font-size:1.35rem;font-weight:600;font-family:"Mona Sans",-apple-system,BlinkMacSystemFont,"Inter",system-ui,sans-serif;letter-spacing:-0.015em;text-decoration:none;padding:1.15rem 0;border-bottom:1px solid rgba(255,255,255,0.10);transition:color 0.2s ease,padding-left 0.2s ease}',
        '#mobile-nav a:hover{color:var(--accent,#4AB5ED);padding-left:0.5rem}',
        '#mobile-nav a.active{color:var(--accent,#4AB5ED)!important;opacity:1!important;font-weight:600!important}',
        '#mobile-nav a:last-child{border-bottom:none}',

        /* Close (X) button — always on the dark overlay */
        '#mobile-nav-close{position:absolute;top:1.25rem;right:1.5rem;width:42px;height:42px;display:flex;align-items:center;justify-content:center;background:transparent;border:1px solid rgba(255,255,255,0.24);border-radius:8px;cursor:pointer;padding:0;color:#FFFFFF;transition:border-color 0.2s ease,color 0.2s ease}',
        '#mobile-nav-close:hover{border-color:var(--accent,#4AB5ED);color:var(--accent,#4AB5ED)}',
        '#mobile-nav-close svg{width:18px;height:18px;display:block}',

        /* Always hamburger, regardless of screen size. */
        '#hamburger{display:flex!important}',
        '.header-nav{display:none!important}'
    ].join('');

    var style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);

    var btn = document.createElement('button');
    btn.id = 'hamburger';
    btn.setAttribute('aria-label', 'Toggle menu');
    btn.setAttribute('aria-expanded', 'false');
    btn.innerHTML = '<span></span><span></span><span></span>';

    var overlay = document.createElement('div');
    overlay.id = 'mobile-nav';
    overlay.setAttribute('aria-hidden', 'true');

    var closeBtn = document.createElement('button');
    closeBtn.id = 'mobile-nav-close';
    closeBtn.setAttribute('aria-label', 'Close menu');
    closeBtn.type = 'button';
    closeBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';
    overlay.appendChild(closeBtn);

    var desktopNav = document.querySelector('.header-nav');
    if (desktopNav) {
        var links = desktopNav.querySelectorAll('a');
        links.forEach(function (link) {
            var a = document.createElement('a');
            a.href = link.href;
            a.textContent = link.textContent;
            if (link.classList.contains('active')) a.classList.add('active');
            a.addEventListener('click', closeMenu);
            overlay.appendChild(a);
        });
    }

    // Append site-wide extras that are not part of every page's .header-nav.
    // Keeps the overlay in sync as new destinations get added, without
    // requiring an edit to each page's header markup.
    var extras = [{ href: '/writing.html', text: 'Writing' }];
    var currentPath = location.pathname.replace(/\/$/, '');
    extras.forEach(function (item) {
        // Skip if this link is already in the overlay (from the cloned nav).
        if (overlay.querySelector('a[href="' + item.href + '"]')) return;
        var a = document.createElement('a');
        a.href = item.href;
        a.textContent = item.text;
        if (currentPath === item.href.replace(/\.html$/, '').replace(/\/$/, '')) {
            a.classList.add('active');
        }
        a.addEventListener('click', closeMenu);
        overlay.appendChild(a);
    });

    /* Prefer the Studio nav host when present (Pass 8), otherwise the legacy header container. */
    var headerContainer = document.querySelector('.studio-nav-right') || document.querySelector('.header-container');
    if (headerContainer) headerContainer.appendChild(btn);
    document.body.appendChild(overlay);

    function openMenu() {
        btn.classList.add('open');
        overlay.classList.add('open');
        btn.setAttribute('aria-expanded', 'true');
        overlay.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }

    function closeMenu() {
        btn.classList.remove('open');
        overlay.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
        overlay.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    btn.addEventListener('click', function () {
        if (btn.classList.contains('open')) closeMenu();
        else openMenu();
    });

    closeBtn.addEventListener('click', closeMenu);

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeMenu();
    });
})();
