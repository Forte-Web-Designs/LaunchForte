# Confidence, and why it was meaningless — Aug 8, 2026

You were right. The label was measuring the wrong thing.

## What it was doing

```js
confidence = (top >= 12 && top >= second * 1.6) ? 'high' : (top >= 6) ? 'medium' : 'low';
```

Absolute thresholds on a raw keyword score. That is a measure of **how much the buyer
wrote**, not how clearly they said it. A 481-character posting that names one thing
precisely can never reach 12 points, so it could never be better than "medium" however
obvious it was. A rambling 4,000-character posting accumulates points and looks certain.

The real numbers from the five live runs:

| job | top vs runner-up | old label | why the old label was wrong |
|---|---|---|---|
| GHL funnel & automation | scheduling 8 · data-collection 7 | medium | a near-tie, should read as uncertain |
| UK accountancy (QuickBooks) | books-recon 5 · ai-research-agent 5 | low | a **dead tie** — right to be unsure, wrong reason |
| Shopify + Klaviyo | storefront-upsell 6 · messaging 4 | medium | clear winner, marked down for brevity |
| Attendance dashboard | reporting 6 · project-ops 3 | medium | twice the runner-up, not ambiguous at all |
| Make/Zapier/n8n/GHL | system-sync 6 · books-recon 1 | medium | six times the runner-up |

And it was costing you: `direction_note` fired on low **and** medium, so a clear match got
a letter opening "this is not a carbon copy of something I have shipped."

## What it does now

**Certainty is margin, not volume.** `top / runner_up`. If one pattern is well clear of the
field, the posting said which one it is. If two are neck and neck, it didn't, and length
changes nothing.

**Tool certainty is reported separately.** "They said QuickBooks and we hold QuickBooks" is
a fact — but it does not settle which *pattern* they want. Blending the two into one number
is what made the label useless. Now: `tool_certainty` is `named-and-covered` /
`named-not-covered` / `none`, and `match_confidence` is about the pattern alone.

**High needs evidence, not just margin.** A "part time bookkeeper wanted, must know
accounting" posting scores 5 against a runner-up of 0 — infinite margin on almost nothing,
and it is a staffing ad. So high requires margin **and** a real score behind it.

**The numbers ride along.** `match_scores: {top, runner_up, runner_up_shape, margin}`, so the
label can be checked instead of believed.

**Hedging only when it is earned** — a genuine near-tie, or a win on thin evidence. Never
because a posting was short.

## The deeper fix: not all keywords are worth the same

The accountancy tie was not really a tie. Books-reconciliation hit three concrete nouns —
**quickbooks, xero, accounting**. Ai-research-agent hit four generic AI words — **claude,
openai, "ai agent", "agents and"** — words that appear in half the AI-adjacent postings on
the market. Same score, completely different quality of evidence, because weight was based
on word *length* ("quickbooks" and "conversational" scored the same).

Weight is now based on how much a word **narrows the field**: a term claimed by more than one
pattern is halved, and a tool we actually hold shots of gets +1. Naming your stack is a fact;
saying "AI agent" is not.

## Result on the same five jobs

| job | now | scores |
|---|---|---|
| Shopify + Klaviyo | **high** | 6 vs 4, tool named and covered |
| Attendance dashboard | **high** | 6 vs 3 |
| Make/Zapier/n8n/GHL | **high** | 6 vs 1 — and it now stays **system-sync** |
| GHL funnel & automation | low | 8 vs 7, real near-tie, hedged |
| UK accountancy | low | 5 vs 5, dead tie, hedged |

Three unhedged, two honestly uncertain — and the two lows are uncertain about the *pattern*,
which is the only thing worth being uncertain about.

**One real bug fixed along the way.** The "vague request" fallback keyed off the same volume
threshold (`score < 8`), so the Make/Zapier/n8n/GoHighLevel posting — which scored system-sync
6 against a runner-up of 1, about as unambiguous as postings get — was being swapped to
lead-routing purely because it was concise. It keys off ambiguity now, and stays system-sync.

Regression-checked against the six-case scenario matrix and the nine-posting synthetic suite
across all four payload shapes. No shape changed except the one that was wrong.
