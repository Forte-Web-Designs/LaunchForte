# Paper Trail — build notes

Live at `/demo/paper-trail/` (file: `site/demo/paper-trail/index.html`).

## What this demo claims, and what it deliberately does not

**Claims:** the product ("Paper Trail" — contracts and proposals generated, signed, and filed,
with a stamped audit trail) is only as good as the discipline of its record-keeping. This page
proves that discipline is checkable: paste what you generated/sent and what your signing system
actually recorded, and every document gets traced from sent, to signed, to filed, to stamped,
live, in the browser.

**Does not claim:**
- That this is the actual Paper Trail product. It is a standalone audit tool built to demonstrate
  the paper-trail-checking *concept* on pasted text.
- That it verifies contract terms, pricing, or legal enforceability. It is a mechanical checker:
  does a signature exist, was the signed copy filed, does the filing carry an audit stamp, and do
  the signed/filed timestamps even occur in the right order. It does not read contract language.
- That it connects to anything. There is no upload, no auth, no backend. Nothing pasted into the
  two boxes leaves the tab.

## The exact checks, in order

For every document listed in the "what you generated and sent" box, matched by `DOC:` id against
the "what your signing & filing system recorded" box:

1. **Does a filing record exist at all?** If the `DOC:` id from the sent log has no matching block
   in the filing log → **red, "No signing record."** It was sent, but the signing system has never
   heard of it — if the client denies ever agreeing to it, there is nothing to show them.
2. **Did the client decline or was it voided?** `STATUS: declined` → **red, "Client declined."**
   `STATUS: void`/`voided` → **red, "Voided."** Either way there is no live agreement, regardless
   of what the sent log says.
3. **Is there an actual signature?** Any status other than `signed`, or a `signed` status with no
   `SIGNED:` date, → **red, "Still unsigned."** A `pending` status with no signature is the most
   common real-world case: the document went out and nobody ever came back to it.
4. **Was the signed copy filed?** `signed` with a `SIGNED:` date but no `FILED:` date → **red,
   "Signed but never filed."** A signed PDF sitting in an inbox or a rep's downloads folder is not
   a filed contract.
5. **Does the filing carry an audit stamp?** Signed and filed, but no `STAMP:` value → **amber,
   "Filed without an audit stamp."** The document is in the system, but there's no tamper-evident
   record of when or how it got there.
6. **Do the timestamps make sense?** If `FILED:` is chronologically before `SIGNED:` → **amber,
   "Filing timestamp doesn't line up."** The record contradicts itself — either broken tooling or
   a backdated entry, and either way it would not survive a challenge.
7. Otherwise → **green, "Signed, filed, and stamped."** Live signature, filed copy, audit stamp,
   timestamps in the right order.

The hero figure is `(red count + amber count) / total`, rounded to a whole percent, always
rendered in the danger color, because the point is "how much of this can't you prove," not "how
good is your average case." The four counters below it are: total documents checked, green count,
amber count, and red count — deliberately exactly four, matching the convention used by the other
demos in this repo (`always-on-desk`, `books`, `leaks`). Cards are sorted red → amber → green so
the worst findings are on top.

## Where the sample data came from, and why those rows

Fictitious company: an outdoor construction/remodeling business (decks, patios, pergolas — high
dollar, contract-per-job work where a broken paper trail is expensive). Nine documents were chosen
to hit every branch of the checker at least once, so the demo is legible on the very first press
with zero edits:

- DOC-401, Bennett Residence, $42,300 → **green**, the control case: signed, filed same day, stamp
  present, timestamps consistent.
- DOC-402, Okafor Backyard Remodel, $8,750 → **red / still unsigned**, filing record exists but
  status is `pending` with no signature — the most common real failure mode.
- DOC-403, Whitmore Deck Rebuild, $27,900 → **red / no signing record**, sent but no filing block
  at all exists for this `DOC:` id anywhere in the second box.
- DOC-404, Castillo Patio Cover, $15,200 → **red / client declined**.
- DOC-405, Nguyen Outdoor Kitchen, $61,000 → **red / signed but never filed**, has a `SIGNED:` date
  and nothing else — the highest-dollar document in the set, deliberately, since this is the
  costliest version of the failure to have on a $61k job.
- DOC-406, Osei Fence Line, $6,400 → **amber / filed without an audit stamp**, signed and filed,
  no `STAMP:` field.
- DOC-407, Harmon Pergola Install, $22,750 → **amber / filing timestamp doesn't line up**, `FILED:
  2026-06-17` is one day before `SIGNED: 2026-06-18`.
- DOC-408, Delgado Pool Deck, $33,500 → **red / voided**.
- DOC-409, Faulkner Retaining Wall, $11,900 → **green**, a second clean case so the demo doesn't
  read as "nothing ever works," proving the checker isn't rigged to always fail.

Result with the stock data: 9 checked, 2 green, 2 amber, 5 red, hero figure 78%. Verified live
with Playwright — see "Proof" below.

## What this demo does NOT check (by design, not oversight)

- **Contract terms, scope, or pricing correctness.** Only the existence and integrity of the
  signing/filing/stamping chain is graded, never what the document actually says.
- **Whether the audit stamp itself is cryptographically valid.** The checker only confirms a
  `STAMP:` value is present and that `FILED:` is not before `SIGNED:`; it does not (and, running
  on pasted text with no backend, cannot) verify a hash against the actual document bytes.
- **Time elapsed since sending.** A `pending` status is flagged as unsigned regardless of how
  recently it was sent — this was a deliberate simplification to keep the demo deterministic (no
  dependency on "today's date," which would make the sample data's verdicts drift over time and
  make screenshots go stale). A real implementation would likely add an age threshold before
  flagging a pending document as overdue.

## Gotchas hit while building this, and the fix

- **Same input-format decision as `always-on-desk`.** Rather than a strict Q:/A:/CITED: line
  parser, this demo uses a generic `DOC: / KEY: value` block parser (`parseBlocks()`) that splits
  on blank lines and reads any `Key: value` line into a lowercase-keyed object. This tolerates
  fields appearing in any order and blocks with missing fields (e.g. a `pending` filing block that
  only has `DOC:` and `STATUS:`, no `SIGNED:`/`FILED:`/`STAMP:` lines at all) without extra
  special-casing. Confirmed this handles the DOC-402 and DOC-408 sample blocks correctly, which
  are deliberately the shortest blocks in the set (status-only, no other fields).
- **Literal `\n` in prefilled textareas.** Followed the existing house pattern exactly: built each
  sample as a JS array of lines and joined with `String.fromCharCode(10)` (see the `NL` constant
  at the top of the inline script), never a raw `\n` inside a templated string. Verified after the
  fact with `grep -n '\\n' index.html` — the only match is the regex literal `/\n\s*\n/` used to
  split blocks in `parseBlocks()`, which is code, not rendered text, so it's not a bug.
- **Closing `</script>` inside a JS string.** None of the sample data or copy contains the
  substring `</script>`, so the `String.fromCharCode(60) + "/script" + ...` workaround wasn't
  needed — worth re-checking if the sample data is ever edited to include HTML/code snippets.
- **Date comparisons without `Date` parsing.** `FILED:`/`SIGNED:` timestamp-order comparison
  (`DOC-407`) uses a plain string comparison (`String(filing.filed) < String(filing.signed)`)
  rather than `new Date(...)`, since all sample dates are `YYYY-MM-DD` ISO format, which sorts
  correctly as a plain string. Avoids timezone-parsing surprises entirely; if this is ever pointed
  at a real system with non-ISO date strings, this comparison would need a real date parser.
- **`animateCount()` reads are async**, same as `always-on-desk`. The hero figure and counters
  count up via `requestAnimationFrame` over ~700ms. When proving this with Playwright, clicking
  the button and immediately screenshotting shows `0%`/`0` — waited ~1.5s after the click before
  screenshotting so the counted-up values (`78%`, `9`/`2`/`2`/`5`) are actually on screen.
- **Sticky header can clip the hero figure in a screenshot.** After the button's
  `scrollIntoView({block:"start"})` runs, the results section top can land right under the sticky
  nav bar, cropping the top of the giant `78%` figure in a viewport screenshot. Fixed by scrolling
  up ~80px (`window.scrollBy(0, -80)`) before taking the "after" screenshot so the full figure is
  visible below the header. This is a screenshot-capture detail only — the on-page layout has no
  actual overlap bug, `scrollIntoView` just aligns the section edge exactly to the viewport top.

## What was tried and did NOT work / was not attempted

- **Did not copy `site/demo/books/index.html`'s CSV-upload + n8n-webhook interaction pattern.**
  That page (and `leaks`, `owner`, `watcher`, `signals`, `pipeline`, `blueprint`, `assurance`,
  `roofing`, `medspa`) all upload a file or POST to an n8n webhook
  (`https://launchforte.app.n8n.cloud/webhook/...`) and compute the result server-side. The brief
  for this demo explicitly requires in-browser-only checks with no server call, so — as with
  `always-on-desk` before it — the actual page furniture (header, nav, footer, section rhythm) and
  dark-everywhere CSS tokens were copied from `site/demo/always-on-desk/index.html` instead, since
  it already solved "two prefilled textareas → one button → in-browser scoring → hero figure +
  four counters + colored cards" for this exact brief shape. Nothing was copied from `books`
  directly beyond the general "how it works" 3-card section rhythm, which both pages already share.
- **Did not add a lead-capture form or an "Ask us anything" pill that POSTs anywhere.** Per the
  standing rule for this build (no writes to any live third-party system) and the brief's "no
  server call, nothing to authenticate against" requirement, the bottom CTA is a plain link to
  `/contact.html`, not a form submission — same choice `always-on-desk` made and for the same
  reason.
- **Did not add an elapsed-time-since-sent check for `pending` documents.** Considered flagging
  anything pending for more than N days as more urgent than a same-day pending, but this would
  require comparing against "today," which is either `Date.now()` (makes the demo's result drift
  day to day and stale screenshots misleading) or a hardcoded reference date (adds a second date
  concept purely for one edge case). Left out; noted above under "what this does NOT check."

## What would have to change to point this at a real client system

This page runs entirely in the browser against whatever text is pasted into it — there is nothing
to authenticate against, no live connection, no real contract or e-signature store. Turning it
into an actual working integration for a client would need, at minimum:

- **A DocuSign (or equivalent e-signature platform) integration.** This is the one piece a
  browser-only demo cannot fake. Real "was it signed, when, by whom" data lives in DocuSign's (or
  HelloSign's, or PandaDoc's) API, not in a pasted log — replacing the `filingInput` textarea with
  a live pull from that platform's envelope/status API is the core of turning this into a working
  product. Nobody should mistake this working browser demo for that integration already existing.
- **A real contract/proposal generation source** (CRM, quoting tool, or document-generation
  service) to replace the pasted `sentInput` textarea — wherever contracts and proposals actually
  get drafted and sent from today.
- **A real filing/document-of-record system** (Google Drive, a DMS, or the CRM itself) to confirm
  a signed document was actually filed, not just signed — today's `FILED:`/`STAMP:` fields are
  self-reported text; a real version would check for the document's actual presence and hash in
  that system.
- **Server-side storage and scheduling** if this needs to run continuously (checking every new
  contract as it's generated and signed, rather than a one-time paste-and-check), plus somewhere
  to persist findings so a client can see trend over time rather than a single snapshot.

## Proof

Screenshots taken with the Playwright MCP tools against a local `python3 -m http.server` serving
`site/` (no build step, so any static server works):
- `docs/products/paper-trail-before.png` — hero section on load, textareas prefilled, no typing.
- `docs/products/paper-trail-after.png` — after pressing "Audit this paper trail": hero figure
  `78%` in red, counters `9 / 2 / 2 / 5`, cards sorted red → amber → green, each with its reason.

No Playwright tool errors were hit during this build.
