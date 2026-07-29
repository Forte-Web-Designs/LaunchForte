/* Cinematic hero — rotate through /media/hero-1.mp4 -> hero-2.mp4
   back-to-back. No-op if no #hero-video on page. Reduced motion honors the
   poster (which is nothing here) and skips rotation entirely. Same rotation
   pattern used sitewide so Seth appears framed the same on every page. */
(function(){
    var v = document.getElementById('hero-video');
    if (!v) return;
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var sources = [
        { src: '/media/hero-1.mp4', pos: 'center center' },
        { src: '/media/hero-2.mp4', pos: 'center 30%' }   // shift up so head stays in frame
    ];
    var i = 0;
    v.removeAttribute('loop');   // We rotate instead of looping a single file
    v.style.objectPosition = sources[0].pos;
    v.addEventListener('loadeddata', function(){ try { var _p = v.play(); if (_p && _p.catch) _p.catch(function(){}); } catch(_){} }, { once: true });
    try { var _p2 = v.play(); if (_p2 && _p2.catch) _p2.catch(function(){}); } catch(_){}

    function loadIndex(k){
        var s = sources[k];
        v.style.objectPosition = s.pos;
        v.src = s.src;
        try { var _p3 = v.play(); if (_p3 && _p3.catch) _p3.catch(function(){}); } catch(_){}
    }
    v.addEventListener('ended', function(){
        i = (i + 1) % sources.length;
        loadIndex(i);
    });
})();
