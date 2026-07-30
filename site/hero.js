/* Cinematic hero — rotates through the `sources` list back-to-back.
   Each source declares startAt (seconds — where playback begins) and
   optional endAt (seconds — where we cut to the next clip). If endAt
   is omitted, the clip plays to natural end. Cutting early keeps
   any per-frame gibberish from lingering long enough to read.
   No-op if no #hero-video on page. Reduced motion skips entirely. */
(function(){
    var v = document.getElementById('hero-video');
    if (!v) return;
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    var sources = [
        { src: '/media/hero-1.mp4?v=q1j', pos: 'center bottom', startAt: 6, endAt: 10 }
    ];
    var i = 0;

    /* We always rewind / swap ourselves, so native loop is off. */
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

    function advance() {
        var next = (i + 1) % sources.length;
        if (next === i) {
            /* single source — seek back to startAt and keep playing */
            seekToStart();
            play();
        } else {
            load(next);
        }
    }

    function load(k) {
        i = k;
        var s = sources[i];
        v.style.objectPosition = s.pos;
        if (!v.src.endsWith(s.src)) v.src = s.src;
        v.addEventListener('loadedmetadata', seekToStart, { once: true });
        v.addEventListener('loadeddata', play, { once: true });
        play();
    }

    /* endAt handling: on every timeupdate, if we've passed the endAt
       marker for the current source, advance. timeupdate fires ~4x/sec
       so a small margin is fine. */
    v.addEventListener('timeupdate', function(){
        var s = sources[i];
        if (s.endAt && v.currentTime >= s.endAt) advance();
    });

    /* Natural end still triggers advance (fallback if endAt omitted). */
    v.addEventListener('ended', advance);

    v.style.objectPosition = sources[0].pos;
    /* If the <source> tag already targets our first src, don't reload — seek + play. */
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
