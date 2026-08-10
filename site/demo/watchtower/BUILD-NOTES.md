# Watchtower — build notes

Live at `/demo/watchtower/` (file: `site/demo/watchtower/index.html`).

## What this demo claims, and what it deliberately does not

**Claims:** the product ("Watchtower" — a monitored scrape with a change log) catches the fields
that quietly moved between one snapshot of a site and the next, before a customer has to point
it out. This page proves the *diffing and verdict* concept is real and checkable: paste two
scrapes of the same business (a "yesterday" and a "today"), press one button, and every field is
compared, classified, and explained in one sentence, live, in the browser.

**Does not claim:**
- That this is the actual Watchtower product. It is a standalone diff tool built to demonstrate
  the change-log *concept* on two pasted snapshots.
- That it scrapes anything. There is no crawler, no scheduler, no real "yesterday" — both
  snapshots are pasted text the visitor controls.
- That it knows whether a change was authorized. It only knows that a value moved and how
  serious that category of field is if it moves without anyone saying so.
- That it connects to anything. There is no upload, no auth, no backend, no fetch call anywhere
  on this page. Nothing pasted into the two boxes leaves the tab.

## The exact checks, in order

1. **Parse both boxes.** Each non-blank line is split on its first `:` into a `label` and a
   `value`. Lines with no colon are silently skipped (tolerates stray blank lines or notes).
2. **Match fields by label**, case-insensitively, between the "yesterday" box and the "today"
   box. The union of labels from both boxes (yesterday's order first, then any label only present
   in today's box) becomes the list of rows in the change log — so a field that appears or
   disappears between scrapes still gets a row, not a silent gap.
3. **Compare values.** If a label exists in only one snapshot, that's treated as a change
   ("appeared since yesterday" / "gone from today's scrape"). Otherwise the trimmed string values
   are compared for exact equality.
4. **Classify severity** by field category, not by how big the text diff looks:
   - **Always fine (green), whether it changed or not:** footer copyright year, CSS bundle
     version, the internal "last updated" timestamp. These are supposed to move on every scrape;
     flagging them would train the reader to ignore the color.
   - **Critical (red) if changed:** header phone number, both starting-price fields, the booking
     button link, the contact form endpoint, SSL certificate status. These are the fields where a
     silent change costs a call, a quote, or a lead.
   - **Worth a look (amber) if changed:** page title, meta description, Saturday/Sunday hours,
     street address, Google Business Profile category, homepage hero headline. Discoverability
     and presentation — matters, rarely urgent.
   - **Unchanged → always green**, regardless of category.
   - **Fallback for edited/unrecognized labels:** if a visitor types their own field name, an
     unchanged value is green; a changed value matching `/phone|price|\$|booking|checkout|
     payment|link|url|endpoint|ssl|certificate/` in the label is red, everything else changed is
     amber. This keeps the tool from breaking (or defaulting to "fine") if someone pastes their
     own data instead of using the sample.
5. **Every row gets a plain-English reason**, not a code or a severity label alone — 13 of the 16
   known fields have a hand-written sentence keyed to that exact field (e.g. the phone number
   reason names what happens to calls, the booking-link reason names what a hijacked funnel looks
   like); the other 3 always-green fields get a "cosmetic, expected drift" sentence. Unrecognized
   fields fall through to a generic "changed with nothing logged about why" sentence.

The hero figure is the **count of critical (red) rows**, always rendered in the danger color
while it's greater than zero (falls back to a green "nothing critical moved" state if a visitor
edits the data down to zero critical changes — see gotchas below). The four counters are:
Critical — held, Worth a look, Fine, Fields watched. Cards are sorted red → amber → green so the
worst findings are on top, matching the convention used elsewhere in this repo (books, leaks,
always-on-desk).

## Where the sample data came from, and why those rows

Fictitious company: Bluebonnet Plumbing Co., Round Rock, TX. Sixteen fields were chosen to be a
realistic combined "scrape" of a small business's website header/footer plus its Google Business
Profile — the kind of thing an actual Watchtower crawl would pull nightly. The two snapshots
("Sunday night" baseline, "Monday morning" today) were built so the stock data exercises every
severity branch on the very first press, with zero edits:

- **4 critical:** header phone number ((512) 555-0142 → (512) 555-8890, a wrong-number scenario),
  drain-cleaning starting price ($89 → $59, every quote since is off), booking button link
  (domain quietly changed from `bluebonnetplumbing.com` to `bluebonnet-plumbing-tx.com` — a
  look-alike domain, the classic hijacked-funnel shape), SSL certificate status (Valid → Expired).
- **2 amber:** meta description (rewritten into keyword-stuffed spam text — reads like a CMS
  compromise, not a copy edit), Sunday hours (Closed → 10am–2pm, a real scheduling surprise for
  staff).
- **10 fine:** page title, Saturday hours, street address, water heater price, contact form
  endpoint, Google Business Profile category, homepage hero headline (all genuinely unchanged
  between the two scrapes — proof the tool doesn't cry wolf on stable fields), plus footer year,
  CSS bundle version, and the internal timestamp (these *do* change between the two boxes, on
  purpose, to prove the "always green" category actually suppresses noise instead of just never
  being exercised).

Result with the stock data: 16 fields watched, 4 critical, 2 worth a look, 10 fine. Verified by
running the page and reading `#heroFigure`, `#cRed`, `#cAmber`, `#cGreen`, `#cTotal` after the
count-up animation settles (see `docs/products/watchtower-after.png`).

## What this demo does NOT check (by design, not oversight)

- **Whether a change was authorized.** The tool has no concept of who made a change or whether it
  was approved — it only knows a value moved and how serious that category is. A real Watchtower
  would need a way to distinguish "the owner changed the price on purpose" from "someone else
  did," most likely an approval/changelog workflow layered on top of the diff, not a browser check.
- **Anything not expressed as a `label: value` line.** No screenshot diffing, no visual
  regression, no DOM structure comparison — this is a text-field diff, not a pixel diff.
- **Multi-day trends.** This is a two-point diff (yesterday vs. today), not a history. A field
  that drifts slowly over many small changes (a price nudged down a dollar a week) would show as
  "fine" every single day even though it's moved a lot over a month, because each individual diff
  is small. A real change log needs to compare against a longer baseline, not just T-1.

## Gotchas hit while building this, and the fix

- **No `docs/BUILD-GOTCHAS.md` existed yet** despite the brief instructing to read it first. This
  file is being created now (see repo root `docs/BUILD-GOTCHAS.md`) seeded with the gotchas
  supplied in the brief itself, plus the ones below, so the next build actually has something to
  read.
- **Prefilled textareas built via a JS array joined with `String.fromCharCode(10)`** (the `NL`
  constant), not embedded as literal multi-line text inside the `<textarea>` tags and not joined
  with a raw `\n` escape. Matches the convention already used in `site/demo/always-on-desk/`.
  Verified after the fact with `grep -c '\\n' index.html` returning `0`, and by reading
  `#snapA`/`#snapB` `.value.split(String.fromCharCode(10)).length` in a live page (both return
  16, confirming real newlines survived).
- **Matching two field sets by label is order- and case-sensitive by default** — the union-of-keys
  helper (`unionKeys`) lowercases for comparison but preserves the *first* snapshot's original
  casing/order, falling back to the second snapshot's label text only for fields that don't exist
  in the first. Without this, a field present only in "today" (simulating a newly-added or newly-
  removed field) would silently vanish from the change log instead of surfacing as a row.
  Also decided that a missing label on either side counts as "changed" for severity purposes,
  since a field disappearing entirely is at least as notable as its value moving — did not want
  the classifier to silently ignore fields that vanish between scrapes.
- **Deciding what happens to the hero figure if a visitor edits the sample data down to zero
  critical changes.** Always rendering "0" in the danger red would read as a false alarm (danger
  color on a good number). Added a `.zero` class that swaps the figure to green with a
  "nothing critical moved" caption when the critical count is exactly 0, so the color always
  matches what it's reporting. The stock sample data always ships with 4 critical changes, so a
  first-time visitor sees the red state described in the brief; the zero-state only appears if
  someone actively edits both boxes to remove every critical difference.
- **`animateCount()` (count-up) is `requestAnimationFrame`-based and async**, same as in
  `always-on-desk`. Testing with Playwright by clicking the button and immediately reading
  `textContent` gets the pre-animation `0`; a short `browser_wait_for` (or reading after
  `prefers-reduced-motion: reduce`, which skips the animation) is required before asserting on
  the rendered figure/counters. Confirmed final values via `browser_evaluate` after a 1.5s wait:
  hero `4`, `cRed 4`, `cAmber 2`, `cGreen 10`, `cTotal 16`, 16 `.finding` cards rendered.
- **`file://` navigation is blocked** in this environment's Playwright tool ("Access to file:
  protocol is blocked"). Worked around by serving `site/` with `python3 -m http.server` on a
  local port and navigating to `http://localhost:PORT/demo/watchtower/` instead. Killed the
  server process after taking screenshots.

## What was tried and did NOT work / was not attempted

- **Did not follow `site/demo/books/index.html`'s actual interaction pattern** (CSV upload → POST
  to an n8n webhook → redirect to a `/report/` page), even though the brief points at `books` as
  "the closest thing already in this repo" for page furniture. `books` and its siblings (leaks,
  watcher, owner, pipeline, blueprint, assurance, roofing, medspa, signals) all compute their
  result server-side. The brief for *this* demo explicitly requires the checks to run in the
  browser with no server call, no auth, no backend — which `books`'s mechanics don't satisfy. What
  was actually copied from `books` is limited to the shared "how it works" 3-card rhythm and
  overall page flow (hero → how it works → try it → results → CTA → footer). The interaction
  model, CSS tokens, and full-page dark styling were copied instead from
  `site/demo/always-on-desk/index.html`, which is the one existing demo that already matches this
  brief's spec exactly (textareas prefilled with messy sample data, in-browser-only diff logic,
  hero figure counting up in the danger color, four counters, color-coded cards with a reason
  sentence each, dark-everywhere styling, no ask-pill, plain `/contact.html` link instead of a
  webhook-backed CTA form).
- **Did not add an "Ask us anything" pill or a lead-capture form that POSTs to the n8n webhook**,
  unlike most sibling demos. The brief requires zero server calls on this page, and the standing
  rules for this build prohibit writing to a live third-party system. The bottom CTA is a plain
  link to `/contact.html`.
- **Did not attempt fuzzy/semantic field matching** (e.g. matching "Phone" to "Header phone
  number" via similarity). Exact-label matching (case-insensitive) was judged sufficient because
  the sample data uses consistent field names on both sides, as a real automated scraper would;
  a regex-based fallback classifier (see step 4 above) handles the case where a visitor types
  their own field names that don't exactly match the known list, without needing fuzzy matching.

## What would have to change to point this at a real client system

This page runs entirely in the browser against whatever text is pasted into the two boxes —
there is no crawler, no schedule, no storage, nothing to authenticate against. Turning it into an
actual working Watchtower for a client would need, at minimum:

- **A real scraper** that visits the client's actual site and Google Business Profile on a
  schedule (nightly, hourly, whatever the SLA is) and extracts the same kind of `label: value`
  fields this demo takes as pasted input — this is server-side infrastructure (a headless
  browser or HTTP fetch + parser), not something a static page can do.
- **Persistent storage of the prior snapshot**, so "yesterday" is a real stored value instead of
  a second textarea the visitor fills in by hand. This means a database or equivalent, and a
  server component that runs the diff on a schedule instead of on a button press.
- **A real alerting channel** (email, SMS, Slack) to push the change log to the client instead of
  rendering it inline on a demo page they have to be looking at.
- **An approval/acknowledgment concept**, so the tool can eventually distinguish "the client's own
  team changed this on purpose" from "this happened and nobody signed off" — right now every
  critical-category change is treated as equally alarming regardless of who made it, because
  there is no identity or audit trail behind a pasted textarea.
