(function() {
    var els = document.querySelectorAll('.reveal');
    if (!els.length) return;
    var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(e) {
            if (e.isIntersecting) {
                e.target.classList.add('revealed');
                observer.unobserve(e.target);
            }
        });
    }, { threshold: 0.02 });
    els.forEach(function(el) { observer.observe(el); });
})();
