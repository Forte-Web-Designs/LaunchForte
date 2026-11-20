/* One place for the live sample link (Seth, Nov 20 2026).
   Every "Try the live sample" link and every clickable screenshot carries
   data-demo-link="<source code>" and is pointed at DEMO_URL?r=<source code>.
   A screenshot can add data-demo-view="<page>" to open that page of the demo.
   The hrefs in the HTML already hold the production value, so links work
   even before this script runs. To test against a preview, set the DEMO_URL
   environment variable: the Netlify build rewrites the line below from it.
   Never commit a preview URL or a bypass value here. */
window.LF_DEMO_URL = 'https://my.launchforte.com/demo';
(function () {
    function apply() {
        var base = window.LF_DEMO_URL;
        document.querySelectorAll('a[data-demo-link]').forEach(function (a) {
            var u = new URL(base, location.href);
            u.searchParams.set('r', a.getAttribute('data-demo-link'));
            // Screenshots open the matching demo page: ?view=systems|requests|review|intelligence|documents
            if (a.hasAttribute('data-demo-view')) u.searchParams.set('view', a.getAttribute('data-demo-view'));
            a.href = u.toString();
            a.target = '_blank';
            a.rel = 'noopener';
        });
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', apply);
    else apply();
})();
