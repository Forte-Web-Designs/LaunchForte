# Launch Forte, website redesign handoff

Say "reference the redesign md" in a new chat and start from here. This documents the
"tool-page" restyle so it can be rolled across the rest of the site.

Last updated: 2026-07-21. Homepage is done and live.

---

## 1. The goal

Make the marketing pages look like the interactive tool/demo pages (dark gradient hero,
plain kicker eyebrow (no badge/pill), gradient accent word, gradient CTA, one product visual on the right)
while keeping the rest of the page clean and Apple-esque (light sections, refined cards).

Reference pages that set the look (already live):
- https://launchforte.com/grade  (landing)
- https://launchforte.com/demo/leaks , /demo/books , /demo/roofing , /demo/medspa
- The homepage now uses this system too: https://launchforte.com/

Brand accent is the site blue **#0088DB** (with #4AB5ED as the lighter tone). The dark
hero/band navy is **#0A1220 -> #0E1729**.

---

## 2. Deploy mechanics (important, do this exactly)

- Static site, **no build step**. `netlify.toml` publishes the `site/` directory as-is.
- Deploys from **git, branch `main`, to Netlify**. Push to `main` = production deploy. NOT Cloudflare.
- Clean URLs: `site/foo/index.html` serves at `/foo`. `site/bar.html` serves at `/bar`.
- Workflow every time: edit files in `site/`, `git add`, commit, `git push origin main`, then
  verify live with curl (Netlify takes ~30-90s to propagate; CDN may serve a cached copy briefly).
- `gh` is NOT authenticated in these sessions, so PRs/deploy-previews can't be opened here.
  We push straight to `main` (that has been the established flow all along).
- Verify pattern (poll then check):
  ```bash
  for i in $(seq 1 8); do curl -s -L https://launchforte.com/PAGE | grep -q MARKER && break;
    curl -s -o /dev/null --retry 1 --retry-delay 12 --retry-connrefused http://127.0.0.1:9 2>/dev/null; done
  ```

### House rules
- Each page is self-contained: all CSS in one `<style>` in the head, all JS inline. No external CSS files, no frameworks, no npm.
- Island/demo pages carry `<meta name="robots" content="noindex">` and are byte-identical deliverables when handed over.
- Preview trick used for the homepage: build the restyle as a `noindex` copy at `/preview/`,
  eyeball it, then "promote" (copy over the real file, restore real title/canonical, drop noindex).
  `/preview/index.html` currently still exists as a stale noindex duplicate of the homepage. Delete it or reuse it.

---

## 3. What is done

- **Homepage (`site/index.html`)**: fully converted and live.
  - Dark `lf-hero` with rotating accent word ("A System" -> "Using The Right Data" -> ...), gradient CTA, `lf-hero-visual` product card on the right (currently the connected-system SVG).
  - Site-wide skin applied (plain kicker eyebrows, no badge/pill, gradient accent headings, premium buttons/cards, enriched dark bands + trusted strip).
  - Dark-mode overrides so hero text stays white (the CTA is an `<a>`, so the site's dark-mode `a{color:#4ab5ed}` was bleeding in).
  - Removed the duplicated "One Connected System" model-diagram section (that visual now lives in the hero).

Everything below the hero on the homepage stays light. Content sections were NOT flipped to dark
(flipping requires re-coloring all inner text and breaks things). Rhythm comes from: dark hero ->
light -> dark accent bands (the existing `.section.dark`) -> dark footer.

---

## 4. The design system (copy-paste)

Paste this whole block into the target page's head `<style>`, just before `</style>`.
It is scoped to the shared class names the site already uses (`.eyebrow`, `.section.white/tinted/dark`,
`.btn-primary`, `.service-card`, `.step-card`, `.capability-row`, `.review-card`), plus new `.lf-*` hero classes.

```css
/* ===== Tool-page style hero ===== */
.lf-hero{position:relative;overflow:hidden;background:linear-gradient(180deg,#0A1220 0%,#0E1729 55%,#0A1220 100%);color:#E7EDF5;padding:96px 0 104px}
.lf-hero::before{content:"";position:absolute;inset:0;background:radial-gradient(ellipse 900px 520px at 30% 0%,rgba(0,136,219,.26),transparent 60%);pointer-events:none}
.lf-hero::after{content:"";position:absolute;inset:0;background:radial-gradient(ellipse 700px 420px at 85% 100%,rgba(74,181,237,.14),transparent 55%);pointer-events:none}
.lf-hero-grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:56px 56px;-webkit-mask-image:radial-gradient(ellipse at 40% 30%,#000 30%,transparent 72%);mask-image:radial-gradient(ellipse at 40% 30%,#000 30%,transparent 72%);pointer-events:none}
.lf-hero-inner{position:relative;max-width:1120px;margin:0 auto;padding:0 24px;display:grid;grid-template-columns:1.05fr .95fr;gap:56px;align-items:center}
/* Eyebrow is plain kicker text, NOT a badge/pill. Do not add a background,
   border, padding, border-radius, or a glowing .dot to eyebrows. */
.lf-eyebrow{display:inline-flex;align-items:center;gap:8px;font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#7EC9F1}
.lf-h1{font-size:clamp(38px,5.4vw,58px);line-height:1.05;letter-spacing:-.028em;font-weight:800;color:#fff;margin:22px 0 18px}
.lf-h1 .lf-accent{background:linear-gradient(180deg,#4AB5ED 0%,#0088DB 100%);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.lf-sub{font-size:19px;line-height:1.55;color:#B7C4D6;max-width:40ch;margin:0 0 28px}
.lf-ctas{display:flex;flex-wrap:wrap;gap:14px;align-items:center}
.lf-cta{display:inline-flex;align-items:center;gap:10px;background:linear-gradient(180deg,#0088DB 0%,#0077C4 100%);color:#fff;font-weight:700;border:0;border-radius:12px;padding:15px 26px;font-size:16px;text-decoration:none;box-shadow:0 10px 28px rgba(0,136,219,.4);transition:transform .18s ease,box-shadow .25s}
.lf-cta:hover{transform:translateY(-1px);box-shadow:0 14px 34px rgba(0,136,219,.5);color:#fff}
.lf-cta-ghost{display:inline-flex;align-items:center;gap:8px;color:#B7C4D6;font-weight:600;font-size:15px;text-decoration:none;padding:14px 4px}
.lf-cta-ghost:hover{color:#fff}
.lf-hero-visual{background:#fff;border:1px solid rgba(255,255,255,.14);border-radius:20px;padding:20px;box-shadow:0 30px 70px rgba(0,0,0,.45)}
.lf-hero-visual img{width:100%;height:auto;display:block}
@media(max-width:900px){.lf-hero{padding:60px 0 68px}.lf-hero-inner{grid-template-columns:1fr;gap:36px}.lf-hero-visual{order:-1}}

/* ===== Tool-page system across the whole page ===== */
.section.white{background:#FFFFFF}
.section.tinted{background:#F5F7FA}
/* Plain kicker text, no badge/pill. No background/border/padding/border-radius. */
.eyebrow{display:block;background:none;border:0;padding:0;border-radius:0;color:#0088DB !important;font-size:12px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;line-height:1.3}
.section.dark .eyebrow{color:#B7DBF3 !important}
h1 span[style*="var(--accent)"], h2 span[style*="var(--accent)"], h2 span[style*="--accent-warm"]{
  background:linear-gradient(180deg,#4AB5ED 0%,#0088DB 100%);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent !important;color:#0088DB}
.section.dark h2 span[style*="var(--accent)"], .section.dark h2 span[style*="--accent-warm"]{
  background:linear-gradient(180deg,#7EC9F1 0%,#4AB5ED 100%);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent !important}
.btn-primary{background:linear-gradient(180deg,#0088DB 0%,#0077C4 100%) !important;border-radius:12px !important;box-shadow:0 8px 22px rgba(0,136,219,.26);transition:transform .18s ease,box-shadow .25s}
.btn-primary:hover{box-shadow:0 12px 30px rgba(0,136,219,.4);transform:translateY(-1px)}
.btn-secondary{border-radius:12px}
.service-card,.step-card,.capability-row,.review-card,.stat-card,.card{border-radius:16px;transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}
.service-card:hover,.step-card:hover,.review-card:hover,.stat-card:hover{transform:translateY(-2px);box-shadow:0 18px 40px rgba(20,25,34,.10);border-color:rgba(0,136,219,.30)}
.capability-row:hover{background:rgba(0,136,219,.04);border-color:rgba(0,136,219,.22)}
.section.dark{position:relative;overflow:hidden;background:linear-gradient(180deg,#0A1220 0%,#0E1729 55%,#0A1220 100%)}
.section.dark::before{content:"";position:absolute;inset:0;background:radial-gradient(ellipse 820px 460px at 50% -10%,rgba(0,136,219,.22),transparent 60%);pointer-events:none}
.section.dark .section-inner{position:relative;z-index:1}

/* ===== Hero: stay light-on-dark in dark mode too ===== */
[data-theme="dark"] .lf-hero .lf-h1{color:#fff}
[data-theme="dark"] .lf-sub{color:#B7C4D6}
[data-theme="dark"] .lf-eyebrow{color:#B7DBF3 !important}
[data-theme="dark"] .lf-cta{color:#fff !important}
[data-theme="dark"] .lf-cta-ghost{color:#B7C4D6 !important}
[data-theme="dark"] .lf-cta-ghost:hover{color:#fff !important}
```

Notes:
- The gradient-heading rule works by targeting the site's existing inline accent spans:
  `<h2>Word <span style="color:var(--accent)">accent</span>.</h2>`. Keep writing headings that way and they auto-gradient.
- `.section.dark` bands need their inner content wrapped in `.section-inner` (they already are on the homepage) so the glow sits behind the text.
- Class names per page vary. The verticals use `.coaches-*`, `.tools-*`, `.vertical-diagram`, `.faq-item`, etc. Check each page and extend the card selector list if a page uses a card class not covered above.

---

## 5. Hero markup pattern

Replace the page's existing hero `<section>` with this shape:

```html
<!-- HERO -->
<section class="lf-hero">
  <div class="lf-hero-grid" aria-hidden="true"></div>
  <div class="lf-hero-inner">
    <div>
      <span class="lf-eyebrow">EYEBROW TEXT</span>
      <h1 class="lf-h1">Headline with an <span class="lf-accent">accent word</span>.</h1>
      <p class="lf-sub">One-line positioning subhead.</p>
      <div class="lf-ctas">
        <a href="CALENDLY_OR_ANCHOR" class="lf-cta">Book a Call</a>
        <a href="#anchor" class="lf-cta-ghost">See how it works</a>
      </div>
    </div>
    <div class="lf-hero-visual">
      <img src="/images/SOME-VISUAL.svg" alt="..." width="960" height="540" loading="eager">
    </div>
  </div>
</section>
```

- For a **rotating** accent word (homepage only), add class `rotating-word` to the accent span and keep the existing rotating-word JS at the bottom of the page. Other pages use a static `.lf-accent` word.
- Keep whatever hero CTA the page already had (audit / Book a call / etc.).

---

## 6. Recipe to convert a new page

1. Read the page, note its hero markup and its card class names.
2. Paste the CSS block from section 4 into the head `<style>` (before `</style>`).
3. Swap the hero `<section>` for the `lf-hero` pattern (section 5). Pick a right-side visual:
   the verticals already have `/images/launchforte-diagram-*.svg`, `-crm-*.svg`, `-workflow-*.svg`.
   NOTE: those diagram SVGs have transparent backgrounds with dark text, so on the DARK hero put them
   inside the white `.lf-hero-visual` card (as we did on the homepage), OR build a dark-native visual.
4. If the page uses a card class not in the selector list, add it to the `.service-card,...` lines.
5. Commit, push to `main`, verify live.
6. Optional: build it as `/preview/<page>` noindex first if you want to compare before promoting.

Keep it low-risk: dark hero + refined light sections + the existing dark bands. Do NOT flip light content sections to dark.

---

## 7. Pages still to convert

Priority order (most valuable first):
1. `/one-connected-system` (`site/one-connected-system.html`) - flagship offer page.
2. Verticals: `/coaches`, `/home-services`, `/financial-firms`, `/medspa`, `/real-estate`.
3. `/medspa/reactivation` (campaign page), `/what-we-build`, `/lead-systems`, `/results`, `/about`, `/partnership`, `/contact`, `/faq`.
4. Legal (`/privacy`, `/terms`) - minimal, maybe just the header/eyebrow polish.

Header + footer are shared blocks (`.site-header`, `.site-footer`) already consistent across pages; leave them.

---

## 8. Known issues / open decisions

- **Hero visual is the weak spot.** The connected-system SVG on a white card reads a bit flat.
  Better: build a dark-native hero diagram (light strokes on dark, like the /demo/leaks and /demo/books
  hero SVGs) per page, or use a higher-contrast product board. Revisit before rolling site-wide.
- **Rotating word width jump.** On the left-aligned hero, the rotating homepage word changes width each
  cycle and nudges the layout. If it bugs you: reserve a min-width on `.rotating-word`, or trim the word list
  (JS array in index.html: `['A System','Using The Right Data','A Framework','A Process','Repeatable']`).
- **Light sticky header over dark hero.** Works, but a translucent-dark header that fades to light on scroll
  would feel more premium. Not done.
- **`/preview/index.html`** is a leftover noindex duplicate of the homepage. Delete or reuse.
- The island/demo pages were repainted from an original green (#123B33) to the site blue (#0088DB) in a
  prior "Repaint 8 island pages" commit. They are already blue.

---

## 9. Copy voice rules (still apply to any new copy)

- No em dashes, en dashes, double hyphens, arrows, tildes, emojis. Use commas, periods, parentheses. Write "ex:" not "e.g."
- Space compound words: follow up, front desk, speed to lead, end to end, no show.
- No rule-of-three lists (use two, or four+). No "not X but Y" contrast framing.
- "Fixed scope, fixed price, fixed timeline" is an approved signature line.
- Business location reads as **Dallas, Texas** / Dallas Fort Worth (not Grapevine) in site copy, though some
  island/demo footers say Grapevine - leave those as delivered unless asked.

---

## 10. Escape-sequence gotcha (for byte-identical deliverables)

When writing delivered HTML that contains JS unicode escapes (`À-ɏ`, `’`, `·`), the Write
tool converts them to literal characters and breaks the md5. Fix after writing with a Python replace back to
the escape form, then re-check md5. (Only relevant for byte-identical island installs, not the redesign.)
