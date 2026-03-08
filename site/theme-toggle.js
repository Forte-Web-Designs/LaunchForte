(function() {
    var lightCSS = ':root[data-theme="light"]{' +
        '--text-primary:#1a202c;--text-secondary:#4a5568;--text-muted:#718096;' +
        '--accent:#0070b8;--accent-hover:#005a96;--accent-warm:#0099f0;--background:#f7f9fc;' +
        '--background-alt:#edf2f7;--border:#e2e8f0;--border-light:#cbd5e0;--card-bg:rgba(255,255,255,0.8);' +
        '--card-bg-solid:#fff;--card-hover:rgba(237,242,247,0.5)}' +
        '[data-theme="light"] body::before{background:radial-gradient(ellipse at 20% 0%,rgba(0,112,184,0.04) 0%,transparent 50%),radial-gradient(ellipse at 80% 100%,rgba(0,136,219,0.03) 0%,transparent 50%),radial-gradient(circle at 50% 50%,rgba(0,136,219,0.01) 0%,transparent 70%)}' +
        '[data-theme="light"] .site-header{background:rgba(247,249,252,0.85);border-bottom-color:var(--border)}' +
        '[data-theme="light"] .header-nav a:hover{background:rgba(0,0,0,0.04)}' +
        '[data-theme="light"] .header-nav a.active{background:rgba(0,112,184,0.08)}' +
        '[data-theme="light"] .hero-badge{background:rgba(0,112,184,0.06);border-color:rgba(0,112,184,0.15)}' +
        '[data-theme="light"] .capability-icon{background:rgba(0,112,184,0.08);border-color:rgba(0,112,184,0.15)}' +
        '[data-theme="light"] .btn-primary{background:linear-gradient(135deg,#0070b8,#005a96)}' +
        '[data-theme="light"] .btn-primary:hover{box-shadow:0 8px 30px rgba(0,112,184,0.3)}' +
        '[data-theme="light"] #scroll-top-btn{background:#fff;border-color:var(--border);color:#718096;box-shadow:0 2px 12px rgba(0,0,0,0.08)}' +
        '[data-theme="light"] #scroll-top-btn:hover{background:#0070b8;color:#fff;border-color:#0070b8}' +
        '[data-theme="light"] #sticky-cta-bar{background:#fff;border-top-color:var(--border);box-shadow:0 -2px 12px rgba(0,0,0,0.06)}' +
        '[data-theme="light"] #sticky-cta-link{background:linear-gradient(135deg,#0070b8,#005a96)}' +
        '[data-theme="light"] .review-quote::before{color:#0070b8}' +
        '[data-theme="light"] .about-avatar{border-color:var(--border);box-shadow:0 0 20px rgba(0,112,184,0.1)}' +
        '[data-theme="light"] .site-video{box-shadow:0 8px 30px rgba(0,0,0,0.1)}';

    var toggleCSS = '#theme-toggle{width:40px;height:40px;border-radius:50%;border:1px solid var(--border);background:var(--card-bg-solid);color:var(--text-muted);font-size:0.95rem;cursor:pointer;z-index:1001;display:flex;align-items:center;justify-content:center;transition:all 0.25s ease;box-shadow:0 2px 8px rgba(0,0,0,0.15);line-height:1;flex-shrink:0;margin-left:0.75rem;backdrop-filter:blur(10px)}' +
        '#theme-toggle.scrolled{position:fixed;top:auto;bottom:8.5rem;right:2rem;margin-left:0}' +
        '#theme-toggle:hover{background:var(--accent);color:#fff;border-color:var(--accent);transform:scale(1.05)}' +
        '@media(max-width:768px){#theme-toggle{width:38px;height:38px;font-size:0.9rem}#theme-toggle.scrolled{right:1.25rem;bottom:8rem}}';

    var style = document.createElement('style');
    style.textContent = lightCSS + toggleCSS;
    document.head.appendChild(style);

    var toggle = document.createElement('button');
    toggle.id = 'theme-toggle';
    toggle.setAttribute('aria-label', 'Toggle light/dark mode');

    var headerContainer = document.querySelector('.header-container');
    if (headerContainer) {
        headerContainer.appendChild(toggle);
    } else {
        document.body.appendChild(toggle);
    }

    var saved = localStorage.getItem('theme');
    applyTheme(saved || 'dark');

    function applyTheme(t) {
        document.documentElement.setAttribute('data-theme', t);
        toggle.innerHTML = t === 'dark' ? '\u263C' : '\u263D';
        localStorage.setItem('theme', t);
    }

    toggle.addEventListener('click', function() {
        var current = document.documentElement.getAttribute('data-theme');
        applyTheme(current === 'dark' ? 'light' : 'dark');
    });

    var isScrolled = false;
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            if (!isScrolled) {
                isScrolled = true;
                toggle.classList.add('scrolled');
                document.body.appendChild(toggle);
            }
        } else {
            if (isScrolled) {
                isScrolled = false;
                toggle.classList.remove('scrolled');
                if (headerContainer) headerContainer.appendChild(toggle);
            }
        }
    });

    // Active nav link
    var path = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.header-nav a').forEach(function(a) {
        var href = a.getAttribute('href').split('/').pop() || 'index.html';
        if (href === path) a.classList.add('active');
    });
})();
