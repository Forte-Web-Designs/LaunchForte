(function () {
    var css = [
        '.site-header{z-index:200!important}',

        '#hamburger{display:none;flex-direction:column;justify-content:center;align-items:center;gap:5px;width:42px;height:42px;background:transparent;border:1px solid var(--border,#1e293b);border-radius:8px;cursor:pointer;padding:0;flex-shrink:0;transition:border-color 0.2s ease}',
        '#hamburger:hover{border-color:var(--accent,#0088DB)}',
        '#hamburger span{display:block;width:18px;height:2px;background:var(--text-primary,#f0f4f8);border-radius:2px;transition:transform 0.3s cubic-bezier(0.16,1,0.3,1),opacity 0.2s ease}',
        '#hamburger.open span:nth-child(1){transform:translateY(7px) rotate(45deg)}',
        '#hamburger.open span:nth-child(2){opacity:0}',
        '#hamburger.open span:nth-child(3){transform:translateY(-7px) rotate(-45deg)}',

        '#mobile-nav{display:none;position:fixed;top:0;left:0;right:0;bottom:0;z-index:199;background:var(--background,#0a0e17);padding:100px 2rem 2rem;overflow-y:auto;flex-direction:column;gap:0;opacity:0;transition:opacity 0.3s ease}',
        '#mobile-nav.open{display:flex;opacity:1}',
        '#mobile-nav a{display:block;color:var(--text-secondary,#94a3b8);font-size:1.15rem;font-weight:500;font-family:"Inter",system-ui,sans-serif;text-decoration:none;padding:1.1rem 0;border-bottom:1px solid var(--border,#1e293b);transition:color 0.2s ease,padding-left 0.2s ease}',
        '#mobile-nav a:hover,#mobile-nav a.active{color:var(--text-primary,#f0f4f8);padding-left:0.5rem}',
        '#mobile-nav a:last-child{border-bottom:none}',

        '@media(max-width:768px){',
        '#hamburger{display:flex!important}',
        '.header-nav{display:none!important}',
        '}'
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

    var headerContainer = document.querySelector('.header-container');
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

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeMenu();
    });
})();
