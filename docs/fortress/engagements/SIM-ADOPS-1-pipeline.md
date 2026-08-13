# SIM-ADOPS-1 — Ad Sales deal pipeline (simulated rehearsal)

Simulated rehearsal against a real Upwork posting, "HubSpot Expert Needed for
Quote-to-Cash Pipeline Implementation" (an entertainment business selling ad
inventory). Nobody has been contacted, nothing is funded, no client exists.
This was built in **Seth's own Launch Forte HubSpot portal** (portalId
`51819426`), never anywhere else.

## Status: pipeline stages were NOT created — blocked by plan limit

This portal's HubSpot plan allows exactly one Deal pipeline
("Pipelines used: 1 of 1", Create pipeline greyed out and lock-icon gated —
see `docs/proof/SIM-ADOPS-1-pipeline-limit-blocked.png`). Creating a second
pipeline needs a Sales Hub upgrade, which is a billing decision, not a build
step, so it wasn't taken. The existing "Sales Pipeline" (7 stages, internal
ID `default`) was left untouched — not modified, not deleted, not used as a
host for the new stages.

Everything below is the design that would have been built: five stages in
order, each with a probability and a stated source of truth, so the reasoning
this posting is actually asking for is on record even though the pipeline
object itself could not be created live.

## The real point of the posting

The posting's harder ask isn't "make a pipeline" — it's "how do the stages
relate to Quote, Contract and Order state instead of re-stating it." A Deal
stage should be a **projection** of state that already lives on another
object, moved by that object's real-world event, not a second, manually
maintained copy of it.

## Stages, probabilities, and source of truth

| # | Stage | Probability | Real-world event that moves the deal here | Object that holds the truth |
|---|---|---|---|---|
| 1 | Lead | 10% | An advertiser inquiry is qualified (budget, flight window, target show/audience confirmed as real) | The Deal itself — no Quote/Contract/Order exists yet, so there's nothing to duplicate |
| 2 | Negotiating | 30% | A Quote is created and sent to the advertiser for the ad package/rate card | **Quote** — status `Draft`/`Sent`. The deal advances when the Quote is created and sent, not when someone remembers to drag the card |
| 3 | Signed | 70% | The advertiser executes the insertion order — the Quote converts to a signed Contract (or the Quote itself is marked signed if no separate Contract object is in play) | **Contract** — status `Signed`. This is an e-signature event, not a sales rep's opinion that the deal "feels done" |
| 4 | Fulfilling | 90% | The ad campaign goes into flight — spots/impressions are actively being delivered against the signed terms | **Order** — status `In fulfillment`, campaign flight dates active. This is where ad ops, not sales, owns the state |
| 5 | Paid | 100% | The advertiser's payment clears in full against the invoice | **Payment** — status `Paid` (via the Invoice it's applied to). Not "invoice sent," which is a Fulfilling-stage event at best |

Probabilities step up in a way that matches how much of the quote-to-cash
chain is already locked in by that point: Lead and Negotiating are still
speculative (10/30%), Signed is a real commitment (70%), Fulfilling is
already-delivering revenue (90%), and Paid is realized (100%).

## Where duplication is most tempting, and what to do instead

The tempting spot is **Deal-level custom properties that shadow the source
objects** — e.g. a `contract_signed_date` or `amount_paid` property sitting
directly on the Deal so a sales dashboard can show one flat row per deal
without joining to Quote/Contract/Order/Payment. It's tempting because
reporting tools want a denormalized table, and hand-adding a few fields to
the Deal is the path of least resistance.

The problem: those fields become a second, manually-entered copy of state
that already exists elsewhere. They drift — someone updates the Payment
record and forgets the Deal property, or updates the Deal property without
a Payment record to back it up, and now the CRM disagrees with itself about
whether the advertiser actually paid.

What to do instead: use HubSpot's native **associations plus calculated /
rollup properties** that read live off the associated Quote, Contract, Order
and Payment records, and drive stage changes with **workflows triggered on
the source object's status change** (Quote sent → move to Negotiating;
Contract signed → move to Signed; Order fulfillment status → Fulfilling;
Payment paid → Paid) rather than a rep dragging the card by feel. If a truly
flat field is still needed for a dashboard, it should be read-only and
computed from the source object, never a second editable field a human can
set out of sync with reality.
