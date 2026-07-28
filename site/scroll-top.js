/* Launch Forte: scroll-to-top arrow. Studio-styled, no sticky CTA bar. */
(function() {
    var btn = document.createElement('button');
    btn.id = 'scroll-top-btn';
    btn.setAttribute('aria-label', 'Scroll to top');
    btn.innerHTML = '↑';
    document.body.appendChild(btn);

    var style = document.createElement('style');
    style.textContent =
        '#scroll-top-btn{position:fixed;bottom:2rem;right:2rem;width:42px;height:42px;' +
        'border-radius:50%;border:1px solid rgba(0,0,0,0.14);background:#FFFFFF;color:#0A0A0A;' +
        'font-size:1rem;cursor:pointer;opacity:0;visibility:hidden;' +
        'transition:opacity 200ms ease,visibility 200ms ease,transform 180ms ease,' +
        'background 180ms ease,border-color 180ms ease,color 180ms ease,box-shadow 200ms ease;' +
        'z-index:1000;display:flex;align-items:center;justify-content:center;' +
        'box-shadow:0 4px 15px rgba(0,0,0,0.10)}' +
        '#scroll-top-btn.visible{opacity:1;visibility:visible}' +
        '#scroll-top-btn:hover{background:var(--accent,#0088DB);color:#fff;' +
        'border-color:var(--accent,#0088DB);transform:translateY(-2px);' +
        'box-shadow:0 6px 20px rgba(0,136,219,0.28)}' +
        '[data-theme="dark"] #scroll-top-btn{background:#171717;color:#FFFFFF;' +
        'border-color:rgba(255,255,255,0.18);box-shadow:0 4px 15px rgba(0,0,0,0.45)}' +
        '[data-theme="dark"] #scroll-top-btn:hover{background:var(--accent,#4AB5ED);color:#0A0A0A;' +
        'border-color:var(--accent,#4AB5ED)}' +
        '@media(max-width:480px){#scroll-top-btn{bottom:1.5rem;right:1.25rem;width:38px;height:38px;font-size:0.9rem}}';
    document.head.appendChild(style);

    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) btn.classList.add('visible');
        else btn.classList.remove('visible');
    }, { passive: true });

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
