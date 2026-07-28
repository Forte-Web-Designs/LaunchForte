/* Launch Forte: hamburger + full-screen nav overlay.
   Rebuilt Pass 8 to match Studio's exact overlay pattern: dark panel with
   the primary nav rendered as a 2-column grid of huge Mona Sans cells,
   each with a hover-tint that pulls in from the outer edge. Overlay always
   dark, both themes. */
(function () {
    var css = [
        '.site-header{z-index:100}',

        /* Hamburger button — sits on the paper pane */
        '#hamburger{display:flex!important;flex-direction:column;justify-content:center;align-items:center;gap:5px;width:42px;height:42px;background:transparent;border:1px solid var(--border-strong,rgba(0,0,0,0.16));border-radius:8px;cursor:pointer;padding:0;flex-shrink:0;transition:border-color 0.2s ease}',
        '#hamburger:hover{border-color:var(--accent,#0088DB)}',
        '#hamburger span{display:block;width:18px;height:2px;background:var(--ink,#0A0A0A);border-radius:2px;transition:transform 0.3s cubic-bezier(0.16,1,0.3,1),opacity 0.2s ease}',
        '#hamburger.open span:nth-child(1){transform:translateY(7px) rotate(45deg)}',
        '#hamburger.open span:nth-child(2){opacity:0}',
        '#hamburger.open span:nth-child(3){transform:translateY(-7px) rotate(-45deg)}',
        '[data-theme="dark"] #hamburger span{background:#FAFAFA}',

        /* Hide the legacy .header-nav (its links are cloned into the overlay) */
        '.header-nav{display:none!important}',

        /* ============= Overlay ============= */
        /* Always dark, both themes. Studio's approach: black panel, no gradient.
           z-index above the header so the header's own logo/Contact/hamburger don't peek through. */
        '#mobile-nav{position:fixed;inset:0;z-index:9999;background:#0A0A0A;color:#FFFFFF;display:none;flex-direction:column;overflow-y:auto;opacity:0;transition:opacity 0.3s ease}',
        '#mobile-nav.open{display:flex;opacity:1}',

        /* Top bar inside the overlay: logo left, close X right. STICKY so the X is always reachable. */
        '#mobile-nav .mn-top{position:sticky;top:0;z-index:2;background:#0A0A0A;display:flex;align-items:center;justify-content:space-between;padding:1.5rem 2rem;max-width:1280px;margin:0 auto;width:100%}',
        '#mobile-nav .mn-logo{display:inline-flex;align-items:center}',
        '#mobile-nav .mn-logo img{height:28px;width:auto;display:block;filter:brightness(0) invert(1)}',
        '#mobile-nav-close{width:42px;height:42px;display:flex;align-items:center;justify-content:center;background:transparent;border:1px solid rgba(255,255,255,0.24);border-radius:8px;cursor:pointer;padding:0;color:#FFFFFF;transition:border-color 0.2s ease,color 0.2s ease}',
        '#mobile-nav-close:hover{border-color:var(--accent,#4AB5ED);color:var(--accent,#4AB5ED)}',
        '#mobile-nav-close svg{width:18px;height:18px;display:block}',

        /* The nav grid: compact cells so every link + the X fit without scrolling */
        '#mobile-nav .mn-links{display:grid;grid-template-columns:1fr;gap:1px;background:#262626;max-width:960px;margin:1rem auto 0;width:100%;padding:0 2rem}',
        '@media(min-width:640px){#mobile-nav .mn-links{grid-template-columns:1fr 1fr;padding:0}}',

        '#mobile-nav .mn-cell{position:relative;isolate:isolate;display:block;background:#0A0A0A;padding:1rem 1.5rem;font-family:"Mona Sans",-apple-system,BlinkMacSystemFont,"Inter",system-ui,sans-serif;font-weight:500;font-size:1.15rem;letter-spacing:-0.01em;line-height:1.3;color:#FFFFFF;text-decoration:none;overflow:hidden;transition:color 0.2s ease}',
        '@media(min-width:640px){#mobile-nav .mn-cell{padding:1.25rem 1.75rem;font-size:1.25rem}#mobile-nav .mn-cell:nth-child(even){border-left:1px solid #262626}}',
        '#mobile-nav .mn-cell::before{content:"";position:absolute;inset:0;z-index:-1;background:#171717;opacity:0;transition:opacity 0.2s ease}',
        '#mobile-nav .mn-cell:hover{color:var(--accent,#4AB5ED)}',
        '#mobile-nav .mn-cell:hover::before{opacity:1}',
        '#mobile-nav .mn-cell.active{color:var(--accent,#4AB5ED)}',

        /* Bottom of overlay — subtle contact/social strip */
        '#mobile-nav .mn-foot{margin-top:auto;padding:1.5rem 2rem 2rem;max-width:960px;margin-left:auto;margin-right:auto;width:100%;border-top:1px solid #262626;display:flex;flex-wrap:wrap;gap:1.5rem;justify-content:space-between;color:#A3A3A3;font-size:0.8125rem}',
        '#mobile-nav .mn-foot a{color:#FFFFFF;text-decoration:none;font-weight:600}',
        '#mobile-nav .mn-foot a:hover{color:var(--accent,#4AB5ED)}'
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

    /* Top: logo + close */
    var top = document.createElement('div');
    top.className = 'mn-top';
    var logoLink = document.createElement('a');
    logoLink.className = 'mn-logo';
    logoLink.href = '/';
    logoLink.setAttribute('aria-label', 'Launch Forte home');
    var logoImg = document.createElement('img');
    logoImg.src = '/images/home/launch-forte.png';
    logoImg.alt = 'Launch Forte';
    logoLink.appendChild(logoImg);
    top.appendChild(logoLink);

    var closeBtn = document.createElement('button');
    closeBtn.id = 'mobile-nav-close';
    closeBtn.setAttribute('aria-label', 'Close menu');
    closeBtn.type = 'button';
    closeBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';
    top.appendChild(closeBtn);
    overlay.appendChild(top);

    /* The 2-col grid of primary nav links */
    var grid = document.createElement('div');
    grid.className = 'mn-links';

    var desktopNav = document.querySelector('.header-nav');
    if (desktopNav) {
        desktopNav.querySelectorAll('a').forEach(function (link) {
            var a = document.createElement('a');
            a.className = 'mn-cell';
            a.href = link.href;
            a.textContent = link.textContent;
            if (link.classList.contains('active')) a.classList.add('active');
            a.addEventListener('click', closeMenu);
            grid.appendChild(a);
        });
    }

    /* Site-wide extras that aren't in every page's .header-nav (Writing) */
    var extras = [{ href: '/writing.html', text: 'Writing' }];
    extras.forEach(function (item) {
        if (grid.querySelector('a[href$="' + item.href + '"]')) return;
        var a = document.createElement('a');
        a.className = 'mn-cell';
        a.href = item.href;
        a.textContent = item.text;
        a.addEventListener('click', closeMenu);
        grid.appendChild(a);
    });
    overlay.appendChild(grid);

    /* Footer: email + social */
    var foot = document.createElement('div');
    foot.className = 'mn-foot';
    foot.innerHTML =
        '<div><a href="mailto:seth@launchforte.com">seth@launchforte.com</a></div>' +
        '<div><a href="https://www.linkedin.com/company/forte-web-designs" target="_blank" rel="noopener">LinkedIn</a></div>';
    overlay.appendChild(foot);

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
        if (e.key === 'Escape' && overlay.classList.contains('open')) closeMenu();
    });
})();
