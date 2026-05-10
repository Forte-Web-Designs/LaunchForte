(function() {
    var s = document.createElement('style');
    s.textContent = '.reveal,.animate-fade-up,.animate-fade-in,.animate-delay-1,.animate-delay-2,.animate-delay-3,.animate-delay-4{opacity:1!important;transform:none!important;animation:none!important}';
    (document.head || document.documentElement).appendChild(s);
    var els = document.querySelectorAll('.reveal');
    for (var i = 0; i < els.length; i++) {
        els[i].classList.add('revealed');
    }
})();
