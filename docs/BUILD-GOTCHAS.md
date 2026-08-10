# Build gotchas

A running list of traps that have already cost time on this project: how to reach records in
each vendor tool, which clicks do not work, which prompts get refused, and vendor-tool behaviors
that fail silently. If you hit something new while building, add it here in the same shape
before you finish — that's part of the job, not an extra.

This file did not exist before the Watchtower demo build (2026-08-10); it's being created now,
seeded with the gotchas that were already being handed out verbatim in build briefs (so they
were clearly known, just not written down) plus what came up during that build.

## Static demo pages (`site/demo/*/index.html`)

- **Never write the literal closing script tag inside a JS string.** Build it from
  `String.fromCharCode(60) + "/script" + String.fromCharCode(62)` if you ever need the literal
  text `</script>` inside a string — writing it directly closes the surrounding `<script>` block
  early and the rest silently doesn't run. Only matters if sample data or copy ever needs to
  contain that substring; check with `grep -n '</script' index.html` and confirm every hit is a
  real tag, not one inside a string, before shipping.
- **Join prefilled textarea lines with a real newline, not a backslash-n.** Build the sample as a
  JS array of line strings and join with `String.fromCharCode(10)` (conventionally named `NL`),
  never with a raw `\n` escape inside a bigger templated string — getting this wrong renders a
  literal backslash-n in the box and looks broken. This also plays it safe against the string
  ever getting double-escaped during generation. Verify with `grep -c '\n' index.html` (excluding
  the `String.fromCharCode` and `.forEach`-style false positives) returning `0` before shipping,
  and by checking `document.getElementById(id).value.split(String.fromCharCode(10)).length` in a
  live page matches the expected line count.
- **Do not use `localStorage` anywhere** on these pages.
- **Every clickable thing needs `cursor:pointer` and a real handler.** A lying affordance (looks
  clickable, does nothing, or isn't wired to a listener) is worse than no affordance.
- **Check your own output before committing:** grep the built page for stray literal
  `\n` sequences in the rendered HTML/JS, and click through the actual interaction (not just eyeball
  the source) to confirm pressing the button produces a visible result, not a silent no-op.
- **`file://` navigation is blocked in the Playwright browser tool available in this environment**
  ("Access to file: protocol is blocked"). To screenshot or interact with a static page before
  it's deployed, serve the `site/` directory locally first — `python3 -m http.server <port>` from
  inside `site/` works — and navigate to `http://localhost:<port>/demo/<name>/` instead. Remember
  to kill the server process afterward (`pkill -f "http.server <port>"`).
- **`requestAnimationFrame`-driven count-up animations (hero figures, counters) are async.**
  Clicking the run button and immediately reading `textContent` via Playwright's `browser_evaluate`
  captures the pre-animation value (usually `0`). Either wait (`browser_wait_for` with a short
  `time`, ~1–1.5s covers a ~700ms animation) before reading the final numbers, or check under
  `prefers-reduced-motion: reduce`, which these pages already skip the animation for and set the
  final value immediately.
- **Not all `site/demo/*` pages follow the same interaction pattern**, despite briefs sometimes
  implying they do. Two families exist as of 2026-08: (1) CSV-upload pages that POST to an n8n
  webhook and redirect to a `/report/` page (`books`, `leaks`, `watcher`, `owner`, `pipeline`,
  `blueprint`, `assurance`, `roofing`, `medspa`, `signals`) — these need a live backend and are
  light-bodied with only a dark hero band; (2) fully in-browser pages with prefilled textareas,
  zero network calls, a hero figure that counts up in the danger color, four counters, and
  color-coded finding cards with a plain-English reason each, styled dark end-to-end
  (`always-on-desk`, `watchtower`). If a brief says "no server call, everything must work from a
  static page," copy family (2)'s CSS tokens and JS structure (`site/demo/always-on-desk/index.html`
  is the reference), not family (1)'s — even if the brief points at a family-(1) page like `books`
  for "page furniture." In that case only the page *rhythm* (hero → how it works → try it →
  results → CTA → footer) carries over, not the upload/webhook mechanics.
- **A brief may point you to a `docs/BUILD-GOTCHAS.md` that doesn't exist yet.** If so, create it
  (this file) rather than skipping the step — the instruction to read-and-append is itself the
  signal that the file is expected to exist going forward, not evidence it's optional.
