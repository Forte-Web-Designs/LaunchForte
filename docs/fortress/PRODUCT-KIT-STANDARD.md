# The Product Kit Standard
How Fortress builds, stores, and sells a repeatable build. Written 2026-08-06.

The goal: a job posting arrives, the Cockpit recognises the *pattern*, and answers with proof —
even when we have never touched that client's specific tool. This file is the recipe for making
that true, and for making the next one fast.

---

## 1. The unit of work is a PATTERN, not a tool

This is the whole idea, and everything else follows from it.

A buyer thinks they are hiring a Pipedrive specialist. What they are actually buying is a
*stalled-deal escalation system*. Pipedrive is the surface; the pattern is the product. We sell
the pattern and demonstrate it in whatever tool we happen to have built it in.

So the library is keyed by **shape**, and tool implementations hang off it:

```
shape: stalled-deal-escalation
  ├── canonical workflow ......... n8n canvas (the architecture, tool-neutral)
  ├── implementation: GoHighLevel . screenshots + sample data
  ├── implementation: HubSpot ..... screenshots + sample data
  ├── implementation: Pipedrive ... (none yet — falls back to the two above)
  ├── sample dataset .............. the fictional records that make it legible
  └── one-page architecture ....... how we think, without the method
```

A tool we have never opened costs us nothing as long as the shape is proven somewhere. That is
why shape coverage is worth more than tool coverage, and why the fallback is the product.

---

## 2. What "done" means — the kit checklist

A shape is SELLABLE when all six exist. Anything less is briefed, not proven, and must not be
cited in a proposal.

| # | Artifact | Why it exists | Fail state it prevents |
|---|---|---|---|
| 1 | **n8n canvas**, zoom-to-fit, every node legible | proves it is engineered, not clicked | "anyone can do this in Zapier" |
| 2 | **In-tool screenshot**, the pattern running in a real CRM | proves it lives where the buyer lives | "that's just a diagram" |
| 3 | **Config panel shots** — the conditions, filters, merge fields, wait logic | proves depth | "you built a two-step stub" |
| 4 | **Sample dataset** — fictional records that make the screen legible | an empty board proves nothing | "this is a blank demo account" |
| 5 | **One-page architecture doc** — how we think, no method given away | earns the technical buyer | "they can't explain their design" |
| 6 | **Build guide** — click path, field values, gotchas, timing | makes the next one fast | rediscovering the same wall twice |

Artifact 6 is the one that compounds. Everything else sells this deal; the build guide is what
makes the tenth build cost a fraction of the first.

---

## 3. The workflow standard (unchanged, restated because it is what buyers grade)

Canvases impress by showing what production actually requires, never by padding. A technical
buyer spots padding and it costs the deal. Every demo workflow carries:

input validation · deduplication · rate limiting · retry with `maxTries` on external calls ·
an error branch to an alert, never silent · a fail-safe response · logging on both paths ·
human escalation carrying context · **a second scheduled trigger** (weekly digest, gap report,
reconciliation)

That last one is the highest-value group for a buyer, because it proves the system keeps earning
after launch. Node names read as a story: "Refusal gate", "Model unreachable, alert us",
"Fail safe, never guess", "Weekly gap report to the owner".

A six-to-ten node chain with branching and a fail-safe is proof. A two-node stub is a liability —
it actively argues we are shallow.

---

## 4. The matching ladder — what the Cockpit does with a job posting

Four rungs, in order. Stop at the first that hits.

1. **Exact tool + exact shape.** Best case. Lead with it.
2. **Same shape, different tool.** Show it and *name the substitution out loud.* The line to use:
   "Here's the same system running in HubSpot — the tool changes, the architecture doesn't."
   Naming it reads as confidence. Hiding it reads as a bait-and-switch when they notice.
3. **Same shape, canonical n8n canvas only.** Sell the architecture. Weaker, still credible.
4. **No shape match.** Do not fake one. Fall back to the closest adjacent shape, say so plainly,
   and let the one-pager carry the weight.

Two rules that do not bend: never show a screenshot of a tool we cannot actually operate, and
never let the proposal imply the client's tool when the shot is another tool. Rung 2 must always
be spoken, never implied.

---

## 5. Worked example — the live Pipedrive posting

The posting: audit and redesign a Pipedrive proposal pipeline. Stage entry/exit criteria,
follow-up cadence, time-based reminders on proposals that have not progressed, escalation for
overdue items, on-hold handling with automated next steps, consistent won/lost/stalled/reactivated
treatment. Aug 17-28, daily EST check-ins.

**We do not have Pipedrive. We can still win this, and here is the exact assembly.**

Decompose into shapes we already own:

| What they asked for | Shape | Evidence we hold today |
|---|---|---|
| Stage entry/exit criteria, ownership per stage | pipeline-design | HubSpot stage editor — 7 stages with probabilities and stage IDs visible |
| Time-based reminders when a proposal stalls | stalled-deal-escalation | `LF DEMO: GoHighLevel deals that stopped moving` + GHL "SAMPLE - Stalled Deal Rescue" |
| Escalation / notification on overdue | alerting | n8n `Watchtower` canvas |
| Follow-up cadence on active proposals | quote-follow-up | GHL "SAMPLE - Quote Follow Up Cadence" |
| On-hold reasons driving next steps | approval-routing | **gap** — build it (see §7) |
| Won / lost / stalled / reactivated consistency | lifecycle | n8n `Lifecycle Engine` canvas |
| Reporting and data quality | reporting | n8n `One Page Truth` + HubSpot dashboard |
| Stage automation config | pipeline-design | HubSpot pipeline "Automate" tab |

Seven of eight covered, in tools that are not Pipedrive. That is a strong answer.

**The reply this produces** — this is the tone, and note it never pretends:

> Your stalled-proposal problem is the one I'd fix first, because it's the one quietly costing
> you deals. I've built exactly that escalation system twice — here's the workflow that watches
> for an opportunity that hasn't moved in seven days, escalates to the owner, and routes the
> on-hold reason to a different next step. [canvas]
>
> That build is in GoHighLevel and this one's in HubSpot [stage editor], because those are where
> my last two clients lived. The tool changes; the architecture doesn't — stage-entry criteria,
> a time-based watcher, an escalation path, and a fail-safe so nothing goes silent are the same
> four pieces in Pipedrive.
>
> On your Aug 17-28 window: the audit and the future-state design are week one, implementation
> week two. Here's how I'd document the stage criteria [one-pager].

Never says "I have done Pipedrive." Never needs to.

---

## 6. The repeatable recipe — how to build the next kit fast

Six steps. Target: under a day per shape once the pattern is known.

1. **Pick the shape by demand**, not by interest. The counts are in §7.
2. **Build the n8n canvas first** — tool-neutral, to the §3 standard. This is the reusable core.
3. **Seed the sample dataset** before touching the tool. An empty board wastes the screenshots.
   Reuse the standing cast so every kit looks like one shop: Dana Whitfield / Northside Plumbing,
   Marcus Reyes / Cedar Ridge Dental, Priya Anand / Lakeside Fitness, Tom Blackwell / Blackwell HVAC.
4. **Implement in ONE tool**, the highest-demand one we can actually operate.
5. **Capture on a fixed shot list**: full canvas → each config panel with real conditions →
   the resulting record/board → the settings screen. Same four shots every time, so the library
   is uniform and the Cockpit can rely on what it will find.
6. **Write the build guide as you go.** Not after — the gotchas are only remembered while hot.

Naming, so the machine can find things without a lookup table:
- workflows: `SAMPLE - <the story>` in-tool, `LF DEMO: <the story>` in n8n
- screenshots: `<shape>--<tool>--<view>.jpg` (e.g. `stalled-deal-escalation--ghl--canvas.jpg`)
- everything sample-facing carries the `SAMPLE` prefix so nothing is ever mistaken for client work

---

## 7. Build order

Shapes with no canvas yet — build these to close the library:

| Shape | Demand | Note |
|---|---|---|
| platform-migration | 29 | no canvas |
| approval-routing | 22 | no canvas — and the Pipedrive posting needs it |
| production-takeover | 10 | no canvas |

Tools with real demand and zero proof, in order:

| Tool | Mentions | First shape to build there |
|---|---|---|
| Shopify | 36 | storefront-upsell (599 — the largest shape we have) |
| Stripe | 24 | books-reconciliation / revenue-at-risk |
| Twilio | 21 | voice-agent-intake |
| Zapier | 19 | system-sync |
| Xero | 18 | books-reconciliation |
| QuickBooks | 16 | books-reconciliation |
| Pipedrive | 1 today | stalled-deal-escalation — build it when a deal justifies the seat |

Pipedrive is last on demand and first on opportunity. Do not buy a seat to chase one posting;
win it on the fallback, then build the kit on the client's own instance during delivery.

---

## 8. What has to be true in the Cockpit for any of this to pay

The library is inert without the matcher. Three requirements:

1. `Match Reference` resolves on **shape first, tool second** — tool is a ranking signal, never
   a filter. A tool-miss must never return empty.
2. When it falls back across tools, the assembled pack carries **both** the in-tool screenshot
   and the canonical n8n canvas. The canvas is what converts a substitution into a flex.
3. The substitution is **stated in the copy**, from a template — not left for the buyer to spot.

Verification discipline, because this has burned us: assert on something only true in the good
case. `evidence_pages: 1` was true both when the PDF held a real screenshot and when it held the
"no screenshot" fallback — it proved nothing. Check the run, never the response.
