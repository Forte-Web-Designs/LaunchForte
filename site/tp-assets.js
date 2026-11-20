/* Technology Partner screenshots and video come from Fortress as real files
   under /technology-partner/. Any slot marked [data-asset] whose image or
   video fails to load is removed, so a missing file never shows as a
   placeholder or a broken image; the surrounding layout falls back to text. */
(function () {
    function drop(el) {
        var slot = el.closest('[data-asset]');
        if (!slot) return;
        var row = slot.closest('[data-asset-row]');
        slot.remove();
        if (row) row.classList.add('no-asset');
    }
    function watch() {
        document.querySelectorAll('[data-asset] img').forEach(function (img) {
            if (img.complete && img.naturalWidth === 0 && img.getAttribute('src')) { drop(img); return; }
            img.addEventListener('error', function () { drop(img); }, { once: true });
        });
        // A missing loop video drops only the video; the poster image beside it
        // takes over. If the poster is missing too, its img error drops the slot.
        document.querySelectorAll('[data-asset] video').forEach(function (v) {
            var src = v.querySelector('source');
            (src || v).addEventListener('error', function () { v.remove(); }, { once: true });
        });
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', watch);
    else watch();
})();
