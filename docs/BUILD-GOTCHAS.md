# Build gotchas

Running list of traps that have already cost time on this project: how to reach records in each
vendor tool, which clicks do not work, which prompts get refused, and n8n behaviours that fail
silently. If you hit something new while building, add it here in the same shape before you
finish — a one- or two-line description plus the fix, grouped by area.

## Static demo pages (`site/demo/*`)

- **Never write the literal closing `</script>` tag inside a JS string.** It ends the surrounding
  `<script>` block early and the page dies silently. Build it from
  `String.fromCharCode(60) + "/script" + String.fromCharCode(62)` if you ever need the literal
  text inside a string.
- **Join prefilled textarea sample lines with a real newline** — build the sample as a JS array of
  lines and `.join(String.fromCharCode(10))`, never a `\n` escape inside a bigger templated
  string. Getting this wrong renders a literal backslash-n in the box and looks broken. Before
  committing, `grep -n '\\n' index.html` and confirm any hits are regex literals (code), not data
  destined for a textarea's prefilled value.
- **Do not use `localStorage` anywhere** on these pages.
- **Every clickable thing needs `cursor:pointer` and a real handler.** A lying affordance (looks
  clickable, does nothing) is worse than no affordance.
- **Two demo interaction patterns exist in this repo — pick the one the brief actually asks for.**
  Ten of the original demos (`books`, `leaks`, `owner`, `watcher`, `signals`, `pipeline`,
  `blueprint`, `assurance`, `roofing`, `medspa`) upload a file or POST to an n8n webhook
  (`https://launchforte.app.n8n.cloud/webhook/...`) and redirect to a report page — server-side
  scoring. `always-on-desk` and `paper-trail` instead parse two prefilled textareas and score
  entirely client-side with zero network calls, per an explicit "no server call, nothing to
  authenticate against" brief requirement. If a new brief says "run the checks in the browser, no
  backend," copy `site/demo/always-on-desk/index.html`'s furniture and script structure, not the
  webhook-upload pattern — they look similar but are fundamentally different builds.
- **`animateCount()`-style counting animations are async** (`requestAnimationFrame` over ~700ms).
  When proving a page with Playwright, clicking the run button and immediately screenshotting or
  reading `textContent` captures the pre-animation `0`/`0%` value. Wait ~1.5s after the click (or
  rely on `prefers-reduced-motion: reduce`, which several of these pages check and skip the
  animation for) before asserting on or screenshotting the rendered numbers.
- **A sticky header can clip a full-viewport-width hero figure right after `scrollIntoView`.**
  If the result section calls `scrollIntoView({block:"start"})` on reveal, its top edge lands
  flush against the sticky nav, which can crop a large heading/figure directly under it in a
  screenshot. Scroll up ~80px (`window.scrollBy(0, -80)`) before capturing an "after" screenshot
  so nothing important is hidden behind the header. This is a screenshot-framing issue only, not
  a real layout bug.
- **Prefer plain ISO (`YYYY-MM-DD`) string comparison over `new Date()` parsing** for simple
  date-order checks on pasted sample data (e.g. "is the filed date before the signed date").
  String comparison sorts ISO dates correctly with zero timezone-parsing surprises; only reach for
  a real date parser if the input format won't be ISO in practice.

## Playwright MCP tool usage

- **`browser_click`'s `target` parameter does not accept an accessibility-snapshot ref directly**
  (e.g. passing `ref=e70` as `target` throws `Unknown engine "ref"`). Use a CSS selector (`#id`,
  `.class`) as `target` instead, alongside a human-readable `element` description.

## Where `docs/BUILD-GOTCHAS.md` itself has been

This file did not exist anywhere in git history before it was created during the `paper-trail`
demo build (searched with `git log --all -- docs/BUILD-GOTCHAS.md`, no hits on any branch). If a
future task brief references this file as already containing prior entries and it looks thin,
that's why — it started here. Keep appending, don't replace.
