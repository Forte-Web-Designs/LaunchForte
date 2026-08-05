# /demo/blueprint/ build — proof status

**Commits:** `f750d3a` (relocate Ask Forte to /ask/) + `a63684b` (build Blueprint)

## Static verification that ran in-session

- File serves locally: `python3 -m http.server` on `site/`, `GET /demo/blueprint/` returned `HTTP 200`, 46,321 bytes.
- Title: `The Blueprint - see your operation on one page | Launch Forte`, distinct from Ask Forte's `Ask Forte: The Napkin Sketch of Your System | Launch Forte`.
- Canonical + og:url point at `https://launchforte.com/demo/blueprint/`.
- All 24 element IDs referenced by the script exist in the HTML (checked via `grep -c 'id="…"'`).
- xmllint XHTML parser warnings only on HTML5 elements it doesn't recognize (`<header>`, `<section>`, `<svg>`, `<nav>`) — normal for the site, not real errors.
- Balanced tags: 6 `<script>` / 6 `</script>`, 1 `<style>` / 1 `</style>`.

## Live browser proof — NOT COMPLETED

The runbook asks for two browser screenshots:
1. Top of the built page, before typing.
2. Result page after typing the sample sentence and pressing "Draw my blueprint".

Neither was captured in this session. **Tool status:** the connected agent tools in this session are `Bash`, `Read`, `Write`, `Edit`, and a set of workflow/agent tools — no browser-driving MCP tool (Playwright, Puppeteer, or equivalent) was available. Attempting to call `browser_navigate` / `browser_screenshot` would have failed with `no such tool` because those schemas are not registered here.

**What Seth or the next agent with a browser tool should do:**
1. Open `https://www.launchforte.com/demo/blueprint/` (once Netlify's next deploy is live).
2. Screenshot the top → save as `docs/proof/blueprint-top.png`.
3. Paste the runbook's exact sample sentence:
   > A lead fills in the form on our site, someone checks the inbox twice a day and copies it into HubSpot, then whoever is free calls them back.
4. Press **Draw my blueprint**.
5. Screenshot the rendered result → save as `docs/proof/blueprint-result.png`.

If the engine emits `[[NAPKIN]]` on that input, the page will render `/forte-draw`'s SVG plus the returned `scar` as a single-item gap list. If it doesn't, the page will show the runbook's honest empty line: *"Not enough to go on yet. Add a sentence about what happens after the lead arrives."* Either behavior is correct per the spec.

## Origin caveat (same as the cockpit page)

`launchforte.com` currently 301s to `www.launchforte.com`. The engine at `launchforte.app.n8n.cloud` must allow the `www` origin in its CORS config (Ask Forte already works from `www.launchforte.com/index.html`, so the same allowance covers this page).
