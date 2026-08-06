# Always On Desk — build notes

Live at `/demo/always-on-desk/` (file: `site/demo/always-on-desk/index.html`).

## What this demo claims, and what it deliberately does not

**Claims:** the product ("Always On Desk" — an assistant that answers from a client's own
documents and shows where each answer came from) is only as good as the discipline of its
citations. This page proves that discipline is checkable: paste a knowledge base and a log of
the assistant's answers, and every citation gets verified against the real source text, live,
in the browser.

**Does not claim:**
- That this is the actual Always On Desk product. It is a standalone audit tool built to
  demonstrate the citation-checking *concept* on pasted text.
- That it understands language, contradictions, or intent. It is a mechanical checker: does a
  citation exist, does the cited document exist, do the numbers in the answer appear in that
  document's text, is the document marked current. It does not read for meaning beyond numbers.
- That it connects to anything. There is no upload, no auth, no backend. Nothing pasted into
  the two boxes leaves the tab.

## The exact checks, in order

For every `Q / A / CITED` entry in the answer log:

1. **Is there a citation at all?** If `CITED:` is blank → **red, "No source."** Nothing to check,
   nothing a customer could be shown.
2. **Does the cited document exist in the knowledge base?** If the `CITED:` id doesn't match any
   `[DOC-n]` block pasted into the knowledge base box → **red, "Invented source."** The assistant
   named a document that isn't real.
3. **Do the numbers in the answer appear in the cited document's text?** The answer is scanned
   for dollar amounts (`$49`, `$150`) and day/year counts (`14 days`, `90 days`, `1 year`). Each
   one is checked as a literal (whitespace-normalized) substring of the cited document's text.
   If any number in the answer is absent from the document → **red, "Source says otherwise."**
   The citation is real; the claim attached to it isn't backed by it.
   If the answer contains no checkable numbers (e.g. "yes, we service Flower Mound"), this step
   is skipped and the entry falls through to step 4 — see **What this demo does not check** below.
4. **Is the cited document current?** The knowledge base parser marks a document `outdated` if
   its header line contains the word "OUTDATED" (case-insensitive). If the document is outdated
   → **amber, "Outdated source."** The number is real, but the policy it came from has been
   replaced.
5. Otherwise → **green, "Verified."** Cited, current, and every checkable number matches.

The hero figure is `(red count + amber count) / total`, rounded to a whole percent, always
rendered in the danger color because the point is "how much of this can't you trust as-is,"
not "how good is your average case." The four counters below it are: total answers checked,
green count, amber count, and red count (the three tiers plus the total — deliberately exactly
four, per spec). Cards are sorted red → amber → green so the worst findings are on top,
matching the convention used in the other demo pages in this repo (books, leaks).

## Where the sample data came from, and why those rows

Fictitious company: Briarwood Appliance Repair. Six knowledge-base documents, two of which are
the same policy at two versions (`DOC-1` current, `DOC-2` outdated) — this is the single most
common real failure mode reported by clients: an assistant that still cites last year's return
policy because nobody removed it from the index. Eight logged answers were chosen to hit every
branch of the checker at least once, so the demo is legible on the very first press with zero
edits:

- Q1 (30-day return, cites DOC-1) → **green**, the control case.
- Q2 (14-day return, cites DOC-2) → **amber**, the outdated-but-technically-correct case.
- Q3 (satisfaction guarantee, cites DOC-9) → **red / invented**, DOC-9 was never defined.
- Q4 (same-day AC service, no citation) → **red / no source**.
- Q5 (diagnostic fee "$49", cites DOC-5 which says $89) → **red / mismatch**.
- Q6 (Flower Mound service area, cites DOC-4, no numbers to check) → **green**, exercises the
  "no checkable facts, falls through on citation + currency alone" path.
- Q7 (90-day labor warranty, cites DOC-3) → **green**.
- Q8 (after-hours fee "$99", cites DOC-5 which says $150) → **red / mismatch**, a second
  mismatch against the same document as Q5 to prove the checker isn't hardcoded to one number.

Result with the stock data: 8 checked, 3 green, 1 amber, 4 red, hero figure 63%.

## What this demo does NOT check (by design, not oversight)

- **Non-numeric factual contradictions.** A sample answer like "yes, we service Fort Worth"
  citing the service-area document (which explicitly says Fort Worth is *not* served) would not
  be caught, because the mismatch check only extracts dollar amounts and day/year counts. This
  was deliberately kept out of the sample data — including a case the checker silently gets
  wrong would undercut the demo's own premise. A real implementation would need semantic
  comparison (embeddings or an LLM-as-judge), not string matching, to catch this class of error.
  Said out loud in the "what would have to change" section below.
- **Tone, completeness, or whether the answer is actually helpful.** Only sourcing is graded.

## Gotchas hit while building this, and the fix

- **Literal `\n` in prefilled textareas.** Building the sample text as one long string with
  `\n` escapes risks it rendering as a literal backslash-n if the string ever gets
  double-escaped during generation. Fixed by building each sample as a JS array of lines and
  joining with `String.fromCharCode(10)` (see `NL` constant at the top of the inline script),
  never a raw `\n` inside a bigger templated string. Verified after the fact with
  `grep -n '\\n' index.html` returning zero matches.
- **Closing `</script>` inside a JS string.** None of the sample data or copy contains the
  substring `</script>`, so the `String.fromCharCode(60) + "/script" + ...` workaround wasn't
  needed here — but it's worth checking again if the sample data is ever edited to include HTML
  or code snippets.
- **The Q/A/CITED parser needs to tolerate blank lines between entries** (the sample data uses
  a blank line as a visual separator). The parser is state-machine based (new entry starts on
  any `Q:` line) rather than split-on-blank-line, so it doesn't break if someone pastes a log
  without blank-line separators, or with extra blank lines inside an entry.
- **Doc titles used inline in sentences read badly with their status still attached**, e.g.
  "cited Return & Refund Policy v1 (OUTDATED, superseded by DOC-1), but that document has been
  superseded" — redundant and clunky. Added a `cleanTitle()` helper that strips a trailing
  `(...)` parenthetical for use in prose sentences, while the full original title (with status)
  is still shown in the monospace evidence line under each card, so the detail isn't lost.
- **`animateCount()` reads are async.** The hero figure and counters count up via
  `requestAnimationFrame` over ~700ms. Testing with Playwright by clicking the button and
  immediately reading `textContent` returns the pre-animation value (`0%` / `0`) — you have to
  wait for the animation to finish (or check with `prefers-reduced-motion: reduce`, which skips
  the animation and sets the final value immediately) before asserting on the rendered numbers.

## What tried and did NOT work / was not attempted

- **Did not use any of the ten existing `/demo/*` pages' interaction pattern as-is.** All ten
  existing demos (books, leaks, watcher, owner, signals, pipeline, blueprint, assurance, roofing,
  medspa) either upload a CSV/file or submit a form to an n8n webhook
  (`https://launchforte.app.n8n.cloud/webhook/...`) to compute their result server-side, then
  redirect to a report page. None of them run the actual scoring logic client-side with zero
  network calls. The brief for this demo explicitly required in-browser-only checks with no
  server call, so the interaction model here (parse two textareas, score in JS, render inline)
  is new, not copied from a sibling. Page furniture (header, footer, section rhythm, "how it
  works" 3-card layout) was copied from `site/demo/books/index.html` as instructed; the CSS
  tokens and dark-everywhere styling were written fresh per the brief's explicit style spec
  ("background near black, panels a shade lighter"), since the existing demos are light-bodied
  with only a dark hero band, which contradicts the brief for this page.
- **Did not add an "Ask us anything" pill or a lead-capture form that POSTs to the n8n webhook**,
  unlike every sibling demo. Two reasons: the brief says no server call anywhere on this page,
  and per the standing rules for this build, nothing should write to a live third-party system.
  The bottom CTA is a plain link to `/contact.html` instead of a form submission.
- **Did not attempt semantic/LLM-based fact checking in-browser** — no model, no API key, and
  the brief requires zero backend. String-matching on extracted numbers was the deliberate
  scope boundary; see "what would have to change" below.

## What would have to change to point this at a real client system

This page runs entirely in the browser against whatever text is pasted into it — there is
nothing to authenticate against, no live connection, no real document store. Turning it into an
actual working integration for a client would need, at minimum:

- A real document index (the client's actual knowledge base — help docs, policies, PDFs)
  ingested somewhere queryable, replacing the pasted `[DOC-n]` text blocks.
- A live feed of the assistant's actual answers and the citations it produced, replacing the
  pasted `Q:/A:/CITED:` log — this means hooking into whatever is generating those answers.
- **An LLM to do the actual fact-matching.** The in-browser checker here only catches numeric
  mismatches via literal substring search. Real answers make claims that aren't reducible to a
  dollar figure or a day count ("we're open on weekends," "the warranty covers water damage").
  Verifying those against source text requires an LLM (or at minimum embeddings-based semantic
  similarity) doing the comparison, not string matching. **This means an OpenAI (or equivalent
  LLM provider) integration is required for a real version of this — that's the one piece this
  demo cannot fake, and nobody should mistake this working browser demo for that integration
  already existing.**
- Server-side storage and scheduling if this needs to run continuously (checking every new
  answer as it's generated, rather than a one-time paste-and-check).
