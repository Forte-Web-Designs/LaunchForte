(function() {
    var darkCSS = ':root[data-theme="dark"]{' +
        '--text-primary:#f5f5f7;' +
        '--text-secondary:#a1a1a6;' +
        '--text-muted:#86868b;' +
        '--accent:#4ab5ed;' +
        '--accent-hover:#0088DB;' +
        '--accent-warm:#0088DB;' +
        '--accent-subtle:rgba(74,181,237,0.12);' +
        '--accent-glow:rgba(74,181,237,0.12);' +
        '--accent-tint:rgba(74,181,237,0.14);' +
        '--accent-2:#0088DB;' +
        '--accent-3:#4ab5ed;' +
        '--background:#1d1d1f;' +
        '--background-alt:#000000;' +
        '--background-dark:#000000;' +
        '--surface:#2a2a2c;' +
        '--surface-hover:#3a3a3c;' +
        '--card-bg:#2a2a2c;' +
        '--border:rgba(255,255,255,0.10);' +
        '--border-light:rgba(255,255,255,0.16)}' +
        '[data-theme="dark"] body{background:#1d1d1f;color:#f5f5f7}' +
        '[data-theme="dark"] .site-header{background:rgba(29,29,31,0.85)!important;border-bottom:0.5px solid rgba(255,255,255,0.10)}' +
        '[data-theme="dark"] .header-nav a,[data-theme="dark"] .nav-link{color:#f5f5f7;opacity:0.85}' +
        '[data-theme="dark"] .header-nav a:hover,[data-theme="dark"] .nav-link:hover,[data-theme="dark"] .header-nav a.active,[data-theme="dark"] .nav-link.active{color:#f5f5f7;opacity:1}' +
        '[data-theme="dark"] .header-logo{color:#f5f5f7}' +
        '[data-theme="dark"] .stage-card,[data-theme="dark"] .result-card,[data-theme="dark"] .review-card,[data-theme="dark"] .capability-card,[data-theme="dark"] .step-card,[data-theme="dark"] .case-study-card,[data-theme="dark"] .case-study,[data-theme="dark"] .featured-card,[data-theme="dark"] .video-quote-card,[data-theme="dark"] .feature-block,[data-theme="dark"] .service-card,[data-theme="dark"] .featured-case,[data-theme="dark"] .audit-section,[data-theme="dark"] .stat-card,[data-theme="dark"] .stat-item,[data-theme="dark"] .metric-item,[data-theme="dark"] .cta-block,[data-theme="dark"] .cta-section,[data-theme="dark"] .next-step,[data-theme="dark"] .engagement-block,[data-theme="dark"] .product-card,[data-theme="dark"] .credibility-card,[data-theme="dark"] .cap-card,[data-theme="dark"] .pricing-card,[data-theme="dark"] .results-card,[data-theme="dark"] .about-block,[data-theme="dark"] .industry-card,[data-theme="dark"] .calendly-wrap,[data-theme="dark"] .faq-item-card{background:#2a2a2c;border-color:rgba(255,255,255,0.10);color:#f5f5f7}' +
        '[data-theme="dark"] .stage-card:hover,[data-theme="dark"] .result-card:hover,[data-theme="dark"] .review-card:hover,[data-theme="dark"] .capability-card:hover,[data-theme="dark"] .step-card:hover,[data-theme="dark"] .case-study-card:hover,[data-theme="dark"] .case-study:hover,[data-theme="dark"] .featured-card:hover,[data-theme="dark"] .video-quote-card:hover,[data-theme="dark"] .product-card:hover,[data-theme="dark"] .credibility-card:hover,[data-theme="dark"] .results-card:hover{background:#3a3a3c;border-color:rgba(255,255,255,0.16)}' +
        '[data-theme="dark"] h1,[data-theme="dark"] h2,[data-theme="dark"] h3,[data-theme="dark"] h4,[data-theme="dark"] .page-title,[data-theme="dark"] .section-heading,[data-theme="dark"] .hero-headline,[data-theme="dark"] .hero h1{color:#f5f5f7}' +
        '[data-theme="dark"] p,[data-theme="dark"] .body-text,[data-theme="dark"] .about-text,[data-theme="dark"] .sub,[data-theme="dark"] .hero-sub,[data-theme="dark"] .page-subtitle,[data-theme="dark"] .hero-subtitle,[data-theme="dark"] .section-sub{color:#a1a1a6}' +
        '[data-theme="dark"] .review-text,[data-theme="dark"] .video-quote-text,[data-theme="dark"] .review-quote{color:#a1a1a6}' +
        '[data-theme="dark"] .review-name,[data-theme="dark"] .video-quote-name,[data-theme="dark"] .review-author,[data-theme="dark"] .featured-case-client,[data-theme="dark"] .about-name{color:#f5f5f7}' +
        '[data-theme="dark"] .review-project,[data-theme="dark"] .video-quote-project,[data-theme="dark"] .case-study-meta,[data-theme="dark"] .stage-tagline,[data-theme="dark"] .cs-meta,[data-theme="dark"] .price-line{color:#86868b}' +
        '[data-theme="dark"] .price-line{color:#f5f5f7}' +
        '[data-theme="dark"] .btn-primary{background:#4ab5ed;color:#1d1d1f!important}' +
        '[data-theme="dark"] .btn-primary:hover{background:#0088DB;color:#ffffff!important}' +
        '[data-theme="dark"] .btn-ghost,[data-theme="dark"] .btn-secondary{color:#4ab5ed;border-color:rgba(255,255,255,0.16)}' +
        '[data-theme="dark"] .btn-ghost:hover,[data-theme="dark"] .btn-secondary:hover{background:rgba(74,181,237,0.12);color:#4ab5ed}' +
        '[data-theme="dark"] .btn-link{color:#4ab5ed!important}' +
        '[data-theme="dark"] .btn-link:hover{color:#7ec9f1!important}' +
        '[data-theme="dark"] a{color:#4ab5ed}' +
        '[data-theme="dark"] .section-label,[data-theme="dark"] .eyebrow{color:#4ab5ed}' +
        '[data-theme="dark"] .result-stat,[data-theme="dark"] .case-study-stat,[data-theme="dark"] .featured-stat,[data-theme="dark"] .stat-card .stat,[data-theme="dark"] .feature-block .stat,[data-theme="dark"] .metric-value,[data-theme="dark"] .stat,[data-theme="dark"] .gradient-text,[data-theme="dark"] .credibility-stat,[data-theme="dark"] .stat-item .stat,[data-theme="dark"] .cs-metric-num,[data-theme="dark"] .results-big-number,[data-theme="dark"] .rotating-word{color:#4ab5ed!important;-webkit-text-fill-color:#4ab5ed!important;background:none!important;-webkit-background-clip:unset!important;background-clip:unset!important}' +
        '[data-theme="dark"] .footer-section,[data-theme="dark"] .site-footer{background:#000000;color:#86868b}' +
        '[data-theme="dark"] .footer-col h4{color:#ffffff}' +
        '[data-theme="dark"] .footer-col a{color:#86868b}' +
        '[data-theme="dark"] .footer-col a:hover{color:#ffffff}' +
        '[data-theme="dark"] .footer-email-main,[data-theme="dark"] .footer-email-main a{color:#ffffff!important}' +
        '[data-theme="dark"] .footer-bottom p,[data-theme="dark"] .footer-status,[data-theme="dark"] .footer-location,[data-theme="dark"] .copyright{color:#86868b!important}' +
        '[data-theme="dark"] .tech-tag,[data-theme="dark"] .case-study-tags span,[data-theme="dark"] .review-tag,[data-theme="dark"] .cs-tag{background:rgba(74,181,237,0.14);color:#4ab5ed;border-color:rgba(74,181,237,0.20)}' +
        '[data-theme="dark"] .carousel-item{color:#a1a1a6}' +
        '[data-theme="dark"] .metric-label,[data-theme="dark"] .trust-label,[data-theme="dark"] .featured-label,[data-theme="dark"] .stage-number,[data-theme="dark"] .step-number,[data-theme="dark"] .case-label,[data-theme="dark"] .credibility-label,[data-theme="dark"] .trusted-label,[data-theme="dark"] .cs-metric-label{color:#86868b}' +
        '[data-theme="dark"] .featured-in,[data-theme="dark"] .featured-in a{color:#a1a1a6}' +
        '[data-theme="dark"] hr,[data-theme="dark"] .section-divider{border-color:rgba(255,255,255,0.10)}' +
        '[data-theme="dark"] .results-summary li{color:#a1a1a6}' +
        '[data-theme="dark"] .results-summary li strong{color:#f5f5f7}' +
        '[data-theme="dark"] .hamburger-overlay{background:rgba(29,29,31,0.98)}' +
        '[data-theme="dark"] .hamburger-overlay a{color:#f5f5f7}' +
        '[data-theme="dark"] .hamburger-overlay a:hover{color:#4ab5ed}' +
        '[data-theme="dark"] #scroll-top-btn{background:#2a2a2c;border-color:rgba(255,255,255,0.10);color:#a1a1a6}' +
        '[data-theme="dark"] #scroll-top-btn:hover{color:#4ab5ed;border-color:rgba(74,181,237,0.40)}' +
        '[data-theme="dark"] #sticky-cta-bar{background:rgba(29,29,31,0.95);border-top-color:rgba(255,255,255,0.10)}' +
        '[data-theme="dark"] #sticky-cta-link{background:#4ab5ed;color:#1d1d1f}' +
        '[data-theme="dark"] #sticky-cta-link:hover{background:#0088DB;color:#ffffff}' +
        '[data-theme="dark"] .section.tinted{background:#1d1d1f}' +
        '[data-theme="dark"] .section.white{background:#2a2a2c}' +
        '[data-theme="dark"] .section.dark{background:#000000}' +
        '[data-theme="dark"] .trusted-strip{background:#1d1d1f}' +
        '[data-theme="dark"] .marquee-track span{color:#a1a1a6}' +
        '[data-theme="dark"] .logo-img-light{display:none}' +
        '[data-theme="dark"] .logo-img-dark{display:block;filter:brightness(0) invert(1)}' +
        '[data-theme="dark"] .capability-row{border-bottom-color:rgba(255,255,255,0.10)}' +
        '[data-theme="dark"] .capability-list{border-top-color:rgba(255,255,255,0.10)}' +
        '[data-theme="dark"] .capability-row:hover{background:rgba(255,255,255,0.04)}' +
        '[data-theme="dark"] .faq-item{border-bottom-color:rgba(255,255,255,0.10)}';

    var toggleCSS = '#theme-toggle{width:36px;height:36px;border-radius:50%;border:1px solid var(--border);background:transparent;color:var(--text-muted);font-size:1rem;cursor:pointer;z-index:1001;display:flex;align-items:center;justify-content:center;transition:color 0.3s ease,border-color 0.3s ease,background 0.3s ease;line-height:1;flex-shrink:0;margin-left:0.75rem}' +
        '#theme-toggle.scrolled{position:fixed;top:auto;bottom:8.5rem;right:2rem;margin-left:0;background:var(--background);border:1px solid var(--border-light)}' +
        '#theme-toggle:hover{color:var(--text-primary);border-color:var(--border-light)}' +
        '[data-theme="dark"] #theme-toggle{background:rgba(255,255,255,0.08);border-color:rgba(255,255,255,0.20);color:#f5f5f7}' +
        '[data-theme="dark"] #theme-toggle:hover{background:rgba(255,255,255,0.14);border-color:rgba(255,255,255,0.30);color:#ffffff}' +
        '@media(max-width:768px){#theme-toggle{width:34px;height:34px;font-size:0.95rem;margin-left:0;margin-right:0.5rem;background:transparent}[data-theme="dark"] #theme-toggle{background:rgba(255,255,255,0.08)}#theme-toggle.scrolled{position:fixed;top:auto;bottom:8rem;right:1.25rem;margin:0;background:var(--background);border:1px solid var(--border-light)}}';

    var style = document.createElement('style');
    style.textContent = darkCSS + toggleCSS;
    document.head.appendChild(style);

    var toggle = document.createElement('button');
    toggle.id = 'theme-toggle';
    toggle.setAttribute('aria-label', 'Toggle light/dark mode');

    var isMobile = window.innerWidth <= 768;
    var headerContainer = document.querySelector('.header-container');

    function placeToggle() {
        if (!headerContainer) {
            document.body.appendChild(toggle);
            return;
        }
        var hamburger = document.getElementById('hamburger');
        if (hamburger && hamburger.parentNode === headerContainer) {
            // Insert toggle before the hamburger so it doesn't overlap
            headerContainer.insertBefore(toggle, hamburger);
        } else {
            headerContainer.appendChild(toggle);
        }
    }

    // The hamburger script also runs on load — wait a tick so it's in the DOM
    if (document.getElementById('hamburger')) {
        placeToggle();
    } else {
        setTimeout(placeToggle, 0);
    }

    // Versioned theme key. Bumping the version invalidates any previously saved
    // preference and forces all visitors back to the light default. Bump when
    // the default theme intent changes.
    var THEME_KEY = 'theme_v2';
    var saved = null;
    try {
        saved = localStorage.getItem(THEME_KEY);
        // Clear the legacy key so it doesn't leak back in.
        localStorage.removeItem('theme');
    } catch (e) {}
    var theme = saved === 'dark' ? 'dark' : 'light';
    applyTheme(theme);

    function applyTheme(t) {
        document.documentElement.setAttribute('data-theme', t);
        toggle.innerHTML = t === 'dark' ? '☼' : '☽';
        try { localStorage.setItem(THEME_KEY, t); } catch (e) {}
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
                if (!isMobile && headerContainer && toggle.parentNode === headerContainer) {
                    document.body.appendChild(toggle);
                }
            }
        } else {
            if (isScrolled) {
                isScrolled = false;
                toggle.classList.remove('scrolled');
                if (!isMobile && headerContainer) {
                    toggle.style.position = '';
                    toggle.style.top = '';
                    toggle.style.right = '';
                    headerContainer.appendChild(toggle);
                }
            }
        }
    });
})();
