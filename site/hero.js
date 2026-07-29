/* Cinematic hero — Seth 2026-07-29: play hero-1.mp4 ONLY for now.
   hero-2.mp4 stays in /media/ but doesn't rotate in. Single source
   just loops; when we want the second video back, add it to `sources`
   below and the rotation logic returns automatically.
   No-op if no #hero-video on page. Reduced motion skips entirely. */
(function(){
    var v = document.getElementById('hero-video');
    if (!v) return;
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var sources = [
        { src: '/media/hero-1.mp4', pos: 'center center' }
        // { src: '/media/hero-2.mp4', pos: 'center 30%' }   // paused
    ];
    var i = 0;
    if (sources.length > 1) {
        // Rotation mode: cycle back-to-back
        v.removeAttribute('loop');
    } else {
        // Single source: let the browser loop the one file natively
        v.setAttribute('loop', '');
    }
    v.style.objectPosition = sources[0].pos;
    // Ensure the first source matches (in case <source> tag already targets it)
    if (v.currentSrc !== sources[0].src && !v.src.endsWith(sources[0].src)) v.src = sources[0].src;
    v.addEventListener('loadeddata', function(){ try { var _p = v.play(); if (_p && _p.catch) _p.catch(function(){}); } catch(_){} }, { once: true });
    try { var _p2 = v.play(); if (_p2 && _p2.catch) _p2.catch(function(){}); } catch(_){}

    if (sources.length > 1) {
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
    }
})();
