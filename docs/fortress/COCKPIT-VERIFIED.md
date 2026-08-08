# Cockpit evidence matching — verified against real postings
2026-08-07. This is the answer to "would it respond appropriately if it received one of these jobs?"

## How it was tested
`run-dryrun.py` builds a harness from the **live** node file (never a snapshot — that was the bug)
and executes the node's actual code against 12 real Upwork postings. No browser, no email sent.
Re-run it any time: `python3 run-dryrun.py`

## Result: 10 of 12 postings answer in the client's OWN tool

| Posting | Resolved pattern | Tool shown |
|---|---|---|
| Pipedrive — CRM reorganization | stalled-deal-escalation | **Pipedrive** |
| HubSpot — attribution & pipeline | reporting | **HubSpot** |
| GoHighLevel — Med Spa AI booking | scheduling | **GoHighLevel** |
| GoHighLevel — CRM Architect (AI+SaaS) | scheduling | **GoHighLevel** |
| Monday.com — marketing ops | project-ops | **Monday.com** |
| n8n — supplier lead processing | data-collection | **n8n** |
| GoHighLevel — 10DLC / multi-brand | messaging-compliance | **GoHighLevel** |
| Zapier — automation tasks | system-sync | **Zapier** |
| GoHighLevel — FieldRoutes integration | quote-follow-up | **GoHighLevel** |
| Home service — AI automation | books-reconciliation | **QuickBooks** |
| Instantly.ai — AI agents | ai-assistant | GoHighLevel + **GAP RAISED** |
| Airtable — cleaner performance | data-collection | GoHighLevel + **GAP RAISED** |

The last two are correct behaviour, not failures: we do not have Instantly or Airtable, so it
substitutes, states the substitution out loud, and emits `gap_notice` for the
"email Seth and queue that build" branch.

## The bug this caught, and why it mattered
v2 baked four fixed screenshots per pattern at generation time. The morning after we built the
whole pattern **in Pipedrive**, a Pipedrive posting still reported "not covered" and substituted
GoHighLevel — because the node held a snapshot. v3 embeds the library grouped by shape *and tool*
and picks at run time.

**The rule that follows: regenerate the node whenever the library changes.**
`python3 buildnode.py` then redeploy. The harness will tell you immediately if it went stale.

## Known weak spots
- `project-ops` returns only 2 attachments — it has no n8n canvas yet. Build a project-ops kit.
- `ai-assistant` has no n8n kit canvas either, so an Instantly/chatbot job gets 3 not 4.
- The draft is deployed but **UNPUBLISHED**. Nothing reaches production until Publish is clicked.

---

## Update — reading their pain, not just their tool

The node now mirrors the buyer's own language back. It extracts the phrases THEY used and pairs
each with how that thing is handled, so the reply quotes them rather than us. Buyers describe the
same handful of systems in very different packaging; this is what sees through the packaging.

Real output against the Pipedrive posting:

| They said | We answer |
|---|---|
| "not progressed" | a watcher on time-in-stage, so a quiet deal surfaces before it goes cold |
| "on hold" | each on-hold reason routed to its own next step, not one dead bucket |
| "stage-entry" | entry and exit criteria enforced by the system, so a stage cannot sit empty |
| "escalation" | an escalation ladder: owner, then manager, then principal |
| "overdue" | overdue items named and owned rather than reported in aggregate |

Against the Monday.com posting: "board-relation" → relations audited so widgets stop silently
dropping items · "template" → a template system, so a launch is not rebuilt from scratch ·
"subitem" → a standardised subitem structure · "workload" → a workload view that makes capacity
visible · "native" → native automations only, no external middleware to maintain.

### When it is NOT an exact match
Every result carries `match_confidence` (high / medium / low). Below high, it emits a
`direction_note` instead of overclaiming:

> "This is not a carbon copy of something I have shipped. Read against what you have described,
> it is a **{product}** — {the one-line thesis}. Here is the direction I would take it, and what
> that looks like already built."

That is the honest version of "we have thought through your problem" — it names the pattern,
explains why the screenshots relate, and never pretends the build was theirs.

### Current spread across the 12 postings
10 of 12 answer in the client's own tool · 3 high-confidence · 2 raise a build-gap notice
(Instantly, Airtable — tools we genuinely do not hold).

### Weakest matches, honestly
- **GoHighLevel CRM Architect** resolves to The Booking System at low confidence. That posting is
  a whole-account architecture build; booking is one limb of it. The direction note carries it,
  but a `crm-architecture` pattern would answer it properly.
- **Zapier / n8n generalist postings** resolve on thin keyword evidence. They are genuinely vague
  posts, so low confidence is the correct reading rather than a bug.

### Wording
The lines above are placeholders in the right shape. They can be re-voiced from the existing Loom
script, proposal generator and cover letter so everything sounds like one person. The matching
logic does not change when the wording does — `PAIN` in `buildnode.py` is just a phrase table.
