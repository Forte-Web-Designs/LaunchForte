(function() {
    var btn = document.createElement('button');
    btn.id = 'scroll-top-btn';
    btn.setAttribute('aria-label', 'Scroll to top');
    btn.innerHTML = '\u2191';
    document.body.appendChild(btn);

    var bar = document.createElement('div');
    bar.id = 'sticky-cta-bar';
    bar.innerHTML = '<a href="https://calendly.com/seth-fortewebdesigns/30min" target="_blank" rel="noopener" id="sticky-cta-link">Book a Call</a>';
    document.body.appendChild(bar);

    var style = document.createElement('style');
    style.textContent =
        '#scroll-top-btn{position:fixed;bottom:5rem;right:2rem;width:42px;height:42px;border-radius:50%;border:1px solid var(--border,#1e293b);background:var(--card-bg-solid,#111827);color:var(--text-muted,#64748b);font-size:1rem;cursor:pointer;opacity:0;visibility:hidden;transition:all 0.3s ease;z-index:1000;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 15px rgba(0,0,0,0.2);backdrop-filter:blur(10px)}' +
        '#scroll-top-btn.visible{opacity:1;visibility:visible}' +
        '#scroll-top-btn:hover{background:var(--accent,#0088DB);color:#fff;border-color:var(--accent,#0088DB);transform:translateY(-2px);box-shadow:0 6px 20px rgba(0,136,219,0.3)}' +
        '#sticky-cta-bar{position:fixed;bottom:0;left:0;right:0;background:var(--card-bg-solid,#111827);border-top:1px solid var(--border,#1e293b);padding:0.75rem 2rem;text-align:center;z-index:999;transform:translateY(100%);transition:transform 0.3s cubic-bezier(0.16,1,0.3,1);box-shadow:0 -4px 20px rgba(0,0,0,0.3);backdrop-filter:blur(20px)}' +
        '#sticky-cta-bar.visible{transform:translateY(0)}' +
        '#sticky-cta-link{display:inline-block;background:linear-gradient(135deg,#0088DB,#0099f0);color:#fff;padding:0.65rem 2rem;border-radius:8px;font-size:0.875rem;font-weight:600;font-family:"Inter",system-ui,sans-serif;text-decoration:none;transition:transform 0.2s ease,box-shadow 0.2s ease}' +
        '#sticky-cta-link:hover{transform:translateY(-1px);box-shadow:0 4px 15px rgba(0,136,219,0.35)}' +
        'body{padding-bottom:3.5rem}' +
        '@media(max-width:480px){#scroll-top-btn{bottom:4.5rem;right:1.25rem;width:38px;height:38px;font-size:0.9rem}#sticky-cta-bar{padding:0.6rem 1.25rem}#sticky-cta-link{padding:0.6rem 1.5rem;font-size:0.8125rem;width:100%;display:block}}';
    document.head.appendChild(style);

    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            btn.classList.add('visible');
            bar.classList.add('visible');
        } else {
            btn.classList.remove('visible');
            bar.classList.remove('visible');
        }
    });

    btn.addEventListener('click', function() {
        var start = window.scrollY;
        var duration = Math.min(1200, 400 + start * 0.3);
        var startTime = null;
        function step(ts) {
            if (!startTime) startTime = ts;
            var p = Math.min((ts - startTime) / duration, 1);
            window.scrollTo(0, start * (1 - (1 - Math.pow(1 - p, 3))));
            if (p < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
    });
})();
