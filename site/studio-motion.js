/* Launch Forte, Pass 8: Studio motion.
   Reveal-on-scroll (once per element) via IntersectionObserver.
   Honors prefers-reduced-motion. Vanilla JS, no framework.
   Anything with .studio-reveal fades and rises into place as it enters
   the viewport. Wrap a parent in .studio-reveal-stagger to cascade its
   children. */
(function () {
  if (typeof window === 'undefined') return;
  var motion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');
  if (motion && motion.matches) {
    document.querySelectorAll('.studio-reveal').forEach(function (el) { el.classList.add('is-visible'); });
    return;
  }
  if (!('IntersectionObserver' in window)) {
    document.querySelectorAll('.studio-reveal').forEach(function (el) { el.classList.add('is-visible'); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });

  function arm() {
    document.querySelectorAll('.studio-reveal:not(.is-visible)').forEach(function (el) { io.observe(el); });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', arm);
  } else {
    arm();
  }
})();
