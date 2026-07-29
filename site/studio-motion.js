/* Launch Forte, Pass 8: Studio motion.
   Reveal-on-scroll (once per element) via IntersectionObserver.
   Honors prefers-reduced-motion. Vanilla JS, no framework.
   Anything with .studio-reveal fades and rises into place as it enters
   the viewport. Wrap a parent in .studio-reveal-stagger to cascade its
   children.
   Also handles the legacy .reveal class (adds .revealed) so shell-swapped
   pages get the same animation without changing their body markup. */
(function () {
  if (typeof window === 'undefined') return;
  var SELECTOR = '.studio-reveal, .reveal';
  function mark(el) {
    el.classList.add('is-visible');
    if (el.classList.contains('reveal')) el.classList.add('revealed');
  }
  var motion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');
  if (motion && motion.matches) {
    document.querySelectorAll(SELECTOR).forEach(mark);
    return;
  }
  if (!('IntersectionObserver' in window)) {
    document.querySelectorAll(SELECTOR).forEach(mark);
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        mark(entry.target);
        io.unobserve(entry.target);
      }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });

  function arm() {
    document.querySelectorAll(SELECTOR).forEach(function (el) {
      if (el.classList.contains('is-visible') || el.classList.contains('revealed')) return;
      io.observe(el);
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', arm);
  } else {
    arm();
  }
})();
