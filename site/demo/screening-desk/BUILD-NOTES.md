# Screening Desk — build notes

Live at `/demo/screening-desk/` (file: `site/demo/screening-desk/index.html`).

## What this demo claims, and what it deliberately does not

**Claims:** the product ("Screening Desk" — applicant ranking with the reason for the ranking
written down) is checkable on the spot: paste what you're actually screening for and a stack of
applications, and every applicant gets ranked against your own bar, live, in the browser, with a
plain-English sentence for why they landed where they did.

**Does not claim:**
- That this is the actual Screening Desk product wired to an ATS or inbox. It is a standalone
  ranking tool built to demonstrate the "ranked with a reason" concept on pasted text.
- That it understands a resume the way a hiring manager does. It is a mechanical checker: does the
  years-of-experience number clear the bar, is the commute distance inside the radius, did the
  applicant explicitly rule out the required shift, did they explicitly say they have no license,
  does their stated pay ask exceed the budget, and do any of the preferred extras show up in what
  they wrote. It does not read for tone, honesty, or whether the resume is well written.
- That it verifies anything. Every number it scores comes straight from the pasted text with no
  outside lookup — a resume that lies about its own numbers scores exactly as if it were true.
- That it connects to anything. There is no upload, no ATS integration, no auth, no backend.
  Nothing pasted into the two boxes leaves the tab.

## The exact checks, in order

Requirements are parsed from labelled lines (`MIN EXPERIENCE:`, `MAX COMMUTE:`, `SHIFT:`,
`REQUIRED:`, `PAY RANGE:`, `PREFERRED:`); applicants are parsed from labelled blocks
(`APPLICANT:`, `EXPERIENCE:`, `AVAILABILITY:`, `LOCATION:`, `LICENSE:`, `SOFTWARE:`, `PAY:`,
`NOTES:`). For every applicant, in this order:

1. **Years of relevant experience.** Extracted from the `EXPERIENCE:` line (a `"N years"` or
   `"N months"` pattern; months convert to a fraction of a year). If it's below the posting's
   `MIN EXPERIENCE`, that's a hard fail: *"8 months of experience — this role wants 2+ years."*
2. **Commute distance.** Extracted from `LOCATION:` (a `"N miles"` pattern). If it's over the
   posting's `MAX COMMUTE`, that's a hard fail: *"42 miles from the shop — the cutoff is 25."*
3. **Shift availability.** If the posting's `SHIFT:` mentions Saturday and the applicant's
   `AVAILABILITY:` explicitly rules out weekends (a small set of phrases like "will not work
   weekends," "no weekends, ever," "not available for weekends"), that's a hard fail. An applicant
   who just doesn't mention Saturday, or who hedges ("prefers not to, but flexible if needed"),
   is **not** flagged — only an explicit refusal counts, on purpose, because ambiguity in a
   pasted note isn't the same as a stated dealbreaker.
4. **Driver's license.** If the posting's `REQUIRED:` line mentions a driver's license and the
   applicant's `LICENSE:` line explicitly says they don't have one, that's a hard fail.
5. **Pay ask vs. budget.** The first dollar figure in the applicant's `PAY:` line is read as their
   minimum ask. If it's above the top of the posting's `PAY RANGE:`, that's a hard fail, even if
   the applicant is otherwise the strongest candidate in the stack — *"wants $26/hr minimum — the
   role tops out at $22."*
6. **If any of the above failed**, the applicant is **Held** (red), and the reason sentence lists
   every failed check that applied, not just the first one — an applicant who's both under-
   experienced and too far away gets both sentences, so the reason is complete, not a coin flip
   of which check happened to run first.
7. **If all hard checks pass**, the posting's `PREFERRED:` lines are checked against everything
   the applicant wrote (`SOFTWARE:`, `NOTES:`, `EXPERIENCE:` combined). Each `PREFERRED:` line is
   split into candidate phrases (on commas, `/`, and `" or "`) and counted as a hit if any phrase
   appears as a substring of what the applicant wrote. Zero hits → **Worth a look** (amber): every
   must-have is cleared but nothing extra stands out. One or more hits → **Fine** (green), and the
   reason names exactly which extras were found.

The hero figure is the percent of applicants who are **Held**: `red / total`, rounded to a whole
percent, in the danger color, because that's the number a business owner reacts to — how much of
this pile can be set aside without reading it. The four counters below it are: applicants ranked,
Fine, Worth a look, and Held — the exact three tiers named in the style brief plus the total.
Cards are sorted Held → Worth a look → Fine, worst first, matching the convention already used by
`books`, `leaks`, and `always-on-desk`.

## Where the sample data came from, and why those rows

Fictitious company: Copper Creek HVAC & Air, hiring a Customer Service Rep / Dispatcher in Denton,
TX. Ten applicants were written to hit every branch of the checker at least once, so the demo is
legible on the very first press with zero edits:

- **Jordan T.** → **Fine.** Clears everything, brings ServiceTitan experience and picked-up
  Spanish — the two-extras case.
- **Maria R.** → **Worth a look.** Clears every hard requirement (including a hedge on weekends
  that deliberately does *not* trip the "no weekends" rule) but her software (Dentrix) and
  background (dental office) don't match any preferred line.
- **DeShawn K.** → **Held.** Only 8 months of experience against a 2-year minimum — exercises the
  months-to-years conversion and the single-reason-fail case.
- **Priya S.** → **Held.** Everything else about her is strong (5 years dispatching, ServiceTitan
  power user) but she's 42 miles out against a 25-mile cutoff — proves a hard fail overrides an
  otherwise excellent fit.
- **Kevin O.** → **Held.** Explicitly states he will not work weekends under any circumstance,
  against a posting that requires rotating Saturdays.
- **Angela F.** → **Held.** The strongest resume in the stack on paper (6 years, HVAC background,
  ServiceTitan, bilingual) but asks for $26/hr against a $22 ceiling — proves pay is a hard
  ceiling with no exception for an otherwise ideal candidate.
- **Trevor B.** → **Held.** No driver's license, stated plainly, against a posting that requires
  one.
- **Sam W.** → **Fine.** Clears everything, brings ServiceTitan and direct HVAC-industry
  background — the second clean pass, with a different pair of extras than Jordan's.
- **Lena H.** → **Worth a look.** Exactly 2 years of experience (the boundary case — passes with
  nothing to spare) and no preferred extras.
- **Marcus D.** → **Held.** Fails two checks at once (1 year of experience *and* 30 miles out) —
  exercises the multi-reason-fail sentence, which lists both failures instead of stopping at the
  first.

Result with the stock data: 10 ranked, 2 Fine, 2 Worth a look, 6 Held, hero figure 60%. Verified
independently with a Node dry run of the extracted parsing/scoring functions (see gotchas below)
before ever opening a browser, then confirmed again in Playwright.

## What this demo does NOT check (by design, not oversight)

- **Whether anything an applicant wrote is true.** There's no reference check, no ID verification,
  no way to confirm the "6 years" or "valid license" claims. A real integration would need to sit
  downstream of however references or background checks already get handled, not replace them.
- **Soft fit — tone, professionalism, culture fit, writing quality.** Only the five stated
  requirements are graded. A beautifully written resume from someone who's 40 miles away still
  gets Held; a terse, typo-ridden one from someone who clears every bar still gets Fine or better.
- **Anything not phrased as one of the recognized fields.** An applicant who buries their years of
  experience in a paragraph instead of an `EXPERIENCE:` line, or a posting that states a
  requirement in prose instead of a labelled line, won't be picked up by the regex-based parser.
  This is a deliberate scope boundary for a paste-and-score demo, not a claim that real resumes
  arrive this well-labelled — see "what would have to change" below.

## Gotchas hit while building this, and the fix

All of the general demo-page gotchas (never a literal `</script>` in a JS string, real newlines
via `String.fromCharCode(10)` instead of `\n`, no `localStorage`, animation timing, sticky-header
screenshot clipping) are documented in `docs/BUILD-GOTCHAS.md`, which did not exist yet on this
branch and was recreated there — see that file for the full list and the two new entries added
while building this page (a Node-based dry run technique for sanity-checking the scoring logic
before opening a browser, and where `browser_take_screenshot`'s `filename` actually resolves to).
Specific to this page:

- **The "no weekends" and "no license" checks needed to be phrase-based, not keyword-based**, or
  they'd misfire on hedged language. An early draft used a loose pattern like `/not.*weekends/i`,
  which would have wrongly flagged Maria R.'s "prefers not to work weekends but says she's
  flexible if truly needed" as a hard refusal. Switched to a short list of specific refusal
  phrases (`"will not work weekends"`, `"no weekends, ever"`, etc.) so only an unambiguous
  statement trips the rule.
- **The preferred-skills matcher needed to split each `PREFERRED:` line into separate candidate
  phrases**, not just check the whole line as one string. A line like `"bilingual, English/Spanish"`
  as a single substring would never match an applicant who only wrote "Spanish." Splitting on
  commas, `/`, and `" or "` into `["bilingual", "English", "Spanish"]` and matching if *any* token
  hits fixed this, and kept the matcher generic — it works off whatever the requirements text
  says, not a hardcoded skills list.

## What tried and did NOT work / was not attempted

- **Did not use the file-upload/webhook pattern from the ten original `/demo/*` pages.** Per the
  brief, this page runs the checks in the browser with no server call and nothing to authenticate
  against, so it copies `always-on-desk`'s furniture and script structure (two prefilled
  textareas, client-side parse + score, inline render) rather than the CSV-upload-plus-n8n-webhook
  pattern used by `books`, `leaks`, `owner`, etc.
- **Did not add a lead-capture form or an "Ask us anything" pill that POSTs anywhere.** Nothing on
  this page writes to a live third-party system, per the standing rules for this build. The bottom
  CTA is a plain link to `/contact.html`.
- **Did not attempt semantic resume parsing (extracting years/skills from unstructured prose).**
  The parser only reads labelled fields (`EXPERIENCE:`, `LOCATION:`, etc.). Real resumes don't
  arrive pre-labelled like this — see below for what that actually requires.

## What would have to change to point this at a real client system

This page runs entirely in the browser against whatever text is pasted into it. Turning it into an
actual working screen for a client would need, at minimum:

- **A real intake source** — an ATS export, a job-board API, or a shared inbox — replacing the
  pasted `APPLICANT:` blocks. Real applications arrive as PDFs, free-form emails, or web-form
  submissions, not pre-labelled text blocks.
- **An LLM or a dedicated resume-parsing service to extract structured fields from unstructured
  text.** This demo's parser only reads labelled lines; it does not understand a resume written in
  paragraphs. Pulling "years of relevant experience," "commute-relevant location," and "stated pay
  expectation" out of a real resume reliably is the one piece this demo cannot fake, and nobody
  should mistake this working browser demo for that extraction already existing.
- **A persistent requirements definition per job posting**, rather than one pasted textarea, if a
  client is running more than one open role at a time.
- **Storage and a real ranking view** (a shared dashboard the whole hiring team can see) if this
  needs to run continuously as new applications come in, rather than a one-time paste-and-rank.
