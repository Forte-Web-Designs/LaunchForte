/* Cinematic hero — rotates through the `sources` list back-to-back.
   Each source declares an optional `startAt` (seconds) so the video
   starts inside the clip rather than at frame 0 — used to skip the
   first few seconds of ramp-up. We handle the loop ourselves (native
   `loop` would rewind to 0, not `startAt`).
   No-op if no #hero-video on page. Reduced motion skips entirely. */
(function(){
    var v = document.getElementById('hero-video');
    if (!v) return;
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    var sources = [
        { src: '/media/hero-1.mp4?v=p9y', pos: 'center center', startAt: 3 }
    ];
    var i = 0;

    /* We're always seeking to startAt on wrap, so native loop is off. */
    v.removeAttribute('loop');

    function seekToStart() {
        var s = sources[i];
        var t = s.startAt || 0;
        if (t > 0 && v.duration && t < v.duration) {
            try { v.currentTime = t; } catch (_) {}
        }
    }

    function play() {
        try { var p = v.play(); if (p && p.catch) p.catch(function(){}); } catch (_) {}
    }

    function load(k) {
        i = k;
        var s = sources[i];
        v.style.objectPosition = s.pos;
        if (!v.src.endsWith(s.src)) v.src = s.src;
        /* loadedmetadata fires as soon as duration is known — safe to seek */
        v.addEventListener('loadedmetadata', seekToStart, { once: true });
        /* loadeddata fires after the first frame is decoded — safe to play */
        v.addEventListener('loadeddata', play, { once: true });
        play();
    }

    v.addEventListener('ended', function(){
        var next = (i + 1) % sources.length;
        if (next === i) {
            /* single source — seek back to startAt and keep playing */
            seekToStart();
            play();
        } else {
            load(next);
        }
    });

    v.style.objectPosition = sources[0].pos;
    /* If the <source> tag already targets our first src, don't reload it,
       just seek + play. Otherwise `load(0)` will point src at it. */
    if (v.src && v.src.endsWith(sources[0].src)) {
        if (v.readyState >= 1) {
            seekToStart();
        } else {
            v.addEventListener('loadedmetadata', seekToStart, { once: true });
        }
        play();
    } else {
        load(0);
    }
})();
