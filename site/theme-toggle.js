(function() {
    var lightCSS = ':root[data-theme="light"]{' +
        '--text-primary:#0f172a;--text-secondary:#475569;--text-muted:#94a3b8;' +
        '--accent:#4f46e5;--accent-hover:#6366f1;--accent-subtle:rgba(79,70,229,0.06);' +
        '--accent-glow:rgba(79,70,229,0.12);--accent-2:#0891b2;--accent-3:#7c3aed;' +
        '--background:#f8fafc;--background-alt:#f1f5f9;' +
        '--surface:#ffffff;--surface-hover:#f8fafc;' +
        '--border:rgba(0,0,0,0.06);--border-light:rgba(0,0,0,0.1)}' +
        '[data-theme="light"] body::before{background:radial-gradient(ellipse at 20% 0%,rgba(79,70,229,0.04) 0%,transparent 50%),radial-gradient(ellipse at 80% 100%,rgba(8,145,178,0.03) 0%,transparent 50%),radial-gradient(circle at 50% 50%,rgba(79,70,229,0.01) 0%,transparent 70%)}' +
        '[data-theme="light"] body{background-image:radial-gradient(ellipse at 20% 0%,rgba(79,70,229,0.04) 0%,transparent 50%),radial-gradient(ellipse at 80% 100%,rgba(8,145,178,0.03) 0%,transparent 50%)}' +
        '[data-theme="light"] .site-header{background:rgba(248,250,252,0.85)}' +
        '[data-theme="light"] .site-header::after{opacity:0.3}' +
        '[data-theme="light"] .grid-bg{background-image:linear-gradient(rgba(0,0,0,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(0,0,0,0.03) 1px,transparent 1px)}' +
        '[data-theme="light"] .header-nav a:hover{background:rgba(0,0,0,0.04)}' +
        '[data-theme="light"] .header-nav a.active{background:rgba(79,70,229,0.08)}' +
        '[data-theme="light"] .hero-badge{background:rgba(79,70,229,0.06);border-color:rgba(79,70,229,0.15)}' +
        '[data-theme="light"] .btn-primary{background:#4f46e5}' +
        '[data-theme="light"] .btn-primary:hover{background:#6366f1;box-shadow:0 8px 30px rgba(79,70,229,0.2)}' +
        '[data-theme="light"] .btn-secondary{border-color:rgba(0,0,0,0.12);color:#475569}' +
        '[data-theme="light"] .btn-secondary:hover{border-color:rgba(0,0,0,0.2);background:rgba(0,0,0,0.02);color:#0f172a}' +
        '[data-theme="light"] .cap-card,[data-theme="light"] .case-study,[data-theme="light"] .review-card,[data-theme="light"] .stage-card,[data-theme="light"] .result-card,[data-theme="light"] .process-step,[data-theme="light"] .tier-card,[data-theme="light"] .industry-card,[data-theme="light"] .layer-item{background:#ffffff;border-color:rgba(0,0,0,0.06)}' +
        '[data-theme="light"] .cap-card:hover,[data-theme="light"] .case-study:hover,[data-theme="light"] .review-card:hover,[data-theme="light"] .stage-card:hover,[data-theme="light"] .result-card:hover,[data-theme="light"] .tier-card:hover,[data-theme="light"] .industry-card:hover,[data-theme="light"] .layer-item:hover{background:#f8fafc;border-color:rgba(79,70,229,0.2)}' +
        '[data-theme="light"] .cta-block,[data-theme="light"] .cta-section{background:#ffffff;border-color:rgba(0,0,0,0.06)}' +
        '[data-theme="light"] .stat-item{background:#ffffff;border-color:rgba(0,0,0,0.06)}' +
        '[data-theme="light"] .callout{background:#ffffff;border-color:rgba(0,0,0,0.06);border-left-color:#4f46e5}' +
        '[data-theme="light"] .tech-tag{background:#f5f5f7;border-color:rgba(0,0,0,0.06);color:#6e6e73}' +
        '[data-theme="light"] .cs-tag{background:#f5f5f7;border-color:rgba(0,0,0,0.06);color:#6e6e73}' +
        '[data-theme="light"] .review-tag{background:#f5f5f7;border-color:rgba(0,0,0,0.06);color:#6e6e73}' +
        '[data-theme="light"] .calendly-wrap{background:#ffffff;border-color:rgba(0,0,0,0.06)}' +
        '[data-theme="light"] .product-callout{background:linear-gradient(135deg,rgba(79,70,229,0.04),rgba(8,145,178,0.03));border-color:rgba(79,70,229,0.15)}' +
        '[data-theme="light"] .metrics-bar{background:rgba(0,0,0,0.03)}' +
        '[data-theme="light"] .metric-item{background:#ffffff}' +
        '[data-theme="light"] .metric-item:hover{background:#f8fafc}' +
        '[data-theme="light"] #scroll-top-btn{background:#fff;border-color:rgba(0,0,0,0.1);color:#94a3b8;box-shadow:0 2px 12px rgba(0,0,0,0.08)}' +
        '[data-theme="light"] #scroll-top-btn:hover{background:#4f46e5;color:#fff;border-color:#4f46e5}' +
        '[data-theme="light"] #sticky-cta-bar{background:rgba(248,250,252,0.9);border-top-color:rgba(0,0,0,0.06);box-shadow:0 -2px 12px rgba(0,0,0,0.06)}' +
        '[data-theme="light"] #sticky-cta-link{background:#4f46e5}' +
        '[data-theme="light"] #sticky-cta-link:hover{background:#6366f1}' +
        '[data-theme="light"] .review-quote::before{color:#4f46e5}' +
        '[data-theme="light"] .about-avatar{border-color:rgba(0,0,0,0.06);box-shadow:0 0 20px rgba(79,70,229,0.1)}' +
        '[data-theme="light"] .site-video{box-shadow:0 8px 30px rgba(0,0,0,0.1)}' +
        '[data-theme="light"] .hamburger-overlay{background:rgba(255,255,255,0.98)}' +
        '[data-theme="light"] .hamburger-overlay a{color:#1d1d1f}' +
        '[data-theme="light"] .hamburger-overlay a:hover{color:#4f46e5}' +
        '[data-theme="light"] .gradient-text{background:linear-gradient(135deg,#4f46e5,#0891b2,#7c3aed);-webkit-background-clip:text;background-clip:text}' +
        '[data-theme="light"] .result-stat{background:linear-gradient(135deg,#4f46e5,#0891b2);-webkit-background-clip:text;background-clip:text}' +
        '[data-theme="light"] .stage-foundation .cap-card{border-top-color:rgba(138,133,120,0.2)}' +
        '[data-theme="light"] .stage-launch-section .cap-card{border-top-color:rgba(79,70,229,0.2)}' +
        '[data-theme="light"] .stage-growth-section .cap-card{border-top-color:rgba(16,185,129,0.2)}' +
        '[data-theme="light"] .stage-scale-section .cap-card{border-top-color:rgba(8,145,178,0.2)}';

    var toggleCSS = '#theme-toggle{width:40px;height:40px;border-radius:50%;border:1px solid var(--border);background:var(--surface);color:var(--text-muted);font-size:0.95rem;cursor:pointer;z-index:1001;display:flex;align-items:center;justify-content:center;transition:all 0.25s ease;box-shadow:0 2px 8px rgba(0,0,0,0.15);line-height:1;flex-shrink:0;margin-left:0.75rem;backdrop-filter:blur(10px)}' +
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

    applyTheme('dark');

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
