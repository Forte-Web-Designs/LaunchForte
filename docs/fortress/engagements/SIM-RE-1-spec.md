# SIM-RE-1 — build spec (client-supplied, simulated)

Simulated rehearsal of Upwork posting `2083114668777115157`, "Automation Developer —
AI-Powered CRM & Marketing Bot for Real Estate Agents". Nobody has been contacted and
nothing is funded. In the real posting the buyer supplies this document; here it stands
in for theirs, so what the rehearsal proves is **clean execution of a written spec**.

Everything is built in `launchforte.app.n8n.cloud`. Every workflow stays a DRAFT with
`active: false`. Every name is prefixed `SIM RE:`. Sample data only — invented agents,
invented buyers, invented addresses, `@example.com`.

## The interface

The buyer's suite is Telegram-driven. Unless a Telegram connection already exists in
n8n, build the trigger as a **webhook** carrying the same fields a chat command would,
and say plainly in the report which you used. Do not create a Telegram connection.

## Shared store — one Google Sheet

One spreadsheet named `SIM RE - Agent Suite`, four tabs:

| Tab | Columns |
|---|---|
| `buyers` | buyer_id, name, phone, email, budget_min, budget_max, beds, area, notes, created_at |
| `listings` | listing_id, address, area, price, beds, status, owner_name, owner_phone |
| `visits` | visit_id, buyer_id, listing_id, visit_date, slot_start, slot_end, status |
| `documents` | listing_id, doc_name, required, present, verified_by, verified_at |

Seed `listings` with 6 invented properties across 3 areas, and `documents` with the
checklist rows for one of them.

## 1. `SIM RE: Buyer Requirement CRM`

Trigger carries: name, phone, email, budget_min, budget_max, beds, area, notes.

- Read the incoming fields off `($json.body || $json)` once, in a first node.
- Append the buyer to the `buyers` tab with a generated `buyer_id` and `created_at`.
- Read `listings`, and cross-match: same `area`, `price` within budget, `beds` at least
  the requested number, `status` not `sold`.
- Emit a summary naming the buyer and every matched listing_id with its address and price.
- If nothing matches, say so explicitly rather than emitting an empty success.

## 2. `SIM RE: Document Checklist Generator`

Trigger carries a `listing_id`.

- Read `documents` for that listing.
- Produce the sale-side checklist: every required document, whether it is present, and
  what verification step is outstanding.
- Emit a readable checklist plus a count of what is missing.
- An unknown `listing_id` returns a clear "no such listing" result, not a crash.

## 3. `SIM RE: Visit Scheduler`

Trigger carries: buyer_id, a list of listing_ids, a visit_date, and a day window
(default 10:00–18:00).

- Read existing `visits` for that date.
- Build a day-wise schedule in 45-minute slots with 15 minutes between visits.
- **Never double-book**: skip any slot that overlaps an existing visit for that buyer or
  that listing, and report which listings could not be placed and why.
- Append the placed visits to the `visits` tab.

## 4. `SIM RE: Marketing Post Generator`

Trigger carries a `listing_id`.

- Read the listing.
- Ask Claude for ready-to-post marketing copy: one portal listing description (about 120
  words) and one short social caption with 3–5 hashtags.
- Return strict JSON with keys `portal_copy` and `social_caption`, parsed defensively —
  on unparseable output, return the raw text and a flag rather than failing.
- Write nothing to the sheet. This one only produces copy.

## Hard limits

Drafts only, `active: false`, nothing published or scheduled. Nothing is emailed, posted
or sent anywhere. No Telegram connection is created. Nothing existing in the Google
account is modified — the spreadsheet is new and named as above. Nothing is ever deleted.

## Open questions, deliberately not invented

- Whether the buyer wants visit slots confirmed back to the agent, or just written down.
- Whether listings come from a portal feed later, rather than a sheet.
