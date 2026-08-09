# Simulation 1 — the handoff bridge, with real data

**Aug 9, 2026.** Purpose: get the loop into a testable state and run it before building
anything else. Input is a real handoff block built from the actual Modern Bungalow thread,
not an invented one.

---

## The input

This is what a Desktop chat should emit when Seth asks for a handoff. Every line is drawn
from the 489-turn log, so if Fortress mishandles it, it mishandles a real engagement.

```
HANDOFF — Modern Bungalow

STATUS   Inventory fix half-installed: the fulfillment decrement is live on
         "Fulfilled orders Xero" (42 nodes, Active) with its write node disabled, so
         real fulfilments produce free dry runs. PO staging change and fetch fix not
         installed.

SURFACE  n8n (modbung.app.n8n.cloud) — theirs — session live
SURFACE  Shopify admin (modern-bungalow-inc) — theirs — session live, Seth has admin
SURFACE  Xero (org "Modern Bungalow") — theirs — session none, Seth has no login
SURFACE  Twilio console — theirs — session none, Seth has no access

DONE     Seeded 697 rows into check-po-status; table reads 814; re-run found nothing
         left to seed, proving idempotence
DONE     Test product created: ZZ TEST - Inventory Automation, SKU ZZ-TEST-INV, Draft,
         zero stock

NEW      PO staging change — built, not installed
NEW      Fetch-window fix — identified, not built, not scoped

LANE     Install PO staging change with write node disabled — AMBER
LANE     Dry-run the decrement against a real past made-to-order fulfilment — AMBER
LANE     Enable either inventory write node — RED
LANE     Create the throwaway test PO in Xero — RED

RED      Enable either inventory write node — destructive (writes counts to her live
         store and books; not reversible from the report alone)
RED      Create the throwaway test PO in Xero — no session (Seth has no Xero login)

BLOCKED  M3 review texts — built and end-to-end tested, both workflows inactive.
         Unblock: her Twilio guy's new A2P campaign lands, then a messaging service
         SID swap and the consent-cutoff decision.

DECIDED  No automated backfill of missed POs — she applies all quantities then hand
         counts by vendor. Her call, on her own data.
DECIDED  Product sync moved from webhook to hourly schedule — the webhook churn was
         burning the n8n execution quota.

MONEY    $850 Shopify-to-Xero sync — delivered and paid (Feb, $200/$450/$200)
MONEY    $1,250 three-milestone contract — M1 and M2 delivered and live; M3 ($650)
         built, tested, not activated, not submitted
MONEY    $900 inventory fix — funded, not delivered
MONEY    Unbilled: quota-outage diagnosis and fixes, Made-to-Order email gate,
         reconciliation extract

PROMISED Video review link — she asked Jun 30 and said she'd leave a review. Still
         not sent.

RULE     Price fair — she is one of the earliest clients. Established shape is roughly
         a 30% relationship discount off normal rates.
RULE     No hourly contracts on Upwork, ever — fixed-price milestones only, because
         an hourly rate on the profile changes what every other client expects.

NEEDS ME Is the fetch-window fix inside the $900 or priced separately? It is a
         different defect from what she funded, and building her change without it
         means the gaps keep accumulating at ~10 missed POs a day.
NEEDS ME The reconciliation bonus amount is unstated — she offered, no number.

NEXT     Tuesday. She is away until Monday and her VA is mid-way through applying the
         inventory corrections, so nothing that writes inventory moves before then.
```

---

## What the simulation tests

Prerequisite: **publish the dedupe draft** in `Ops: Dashboard API` (draft `f894a8fa`,
active `aa2bc6cc`). Nothing below is meaningful until that is live.

Then paste the block above into the console at `/command/` and check:

**1. Does it file at all?** Does the console recognise a handoff block, or does it treat it
as an ordinary paste? If the latter, the console needs a parser and that is the first
build.

**2. Do the cards land with the right lane?** Four LANE lines, two AMBER, two RED. A RED
card that lands as GREEN is the most dangerous single failure in this system.

**3. Does each RED carry its reason?** `destructive` and `no session` are different
unblocks — one needs a decision, the other needs a sign-in. A RED without a reason is a
card that sits there.

**4. Paste the identical block a second time.** Nothing should duplicate. This is the
direct test of today's dedupe build, on a real payload, and it is the exact failure that
produced eight copies of one card.

**5. Does NEEDS ME populate** with both questions, and nothing else?

**6. Do PROMISED and RULE survive into the record** as retrievable facts, rather than being
dropped as prose? These are the two categories the brief test proved get lost.

**7. Do the four SURFACE lines land as a surface map**, including the two with no session?
Those two are why two cards are RED, and if the map does not record them, the lane
assignment has no basis.

---

## What passing means

If 1–7 pass, the bridge works and the next build is Phase 1 of the hardening run: a real
job, intake to delivery, with Seth as PM only.

If 1 fails, everything else is moot and the console parser is the build.

Grading is against this document, which was written before the run. Anything that passes
"if you squint" is a fail — the whole point of writing the expected result down first is
that it cannot be adjusted afterwards.

---

## Known gap this does not test

The block was written by me from a log I had already read. In real use a Desktop chat
writes it from its own context, and **whether it reliably emits the PROMISED and RULE
lines is untested**. Those are the two the summariser dropped when left to its own
judgement. The operating section gives them named slots specifically to force the issue,
but forcing is not the same as proving. That needs its own test, on a live thread, and it
is not this one.
