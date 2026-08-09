# Class 0 — Components

**Built Aug 9, 2026, from `upwork_jobs` (6,800 postings). Deployed in the n8n
node "Price the build".**

---

## The gap

The catalogue's lowest rungs were $500 (fix) and $800 (single workflow). A large
share of real postings ask for one small discrete thing — a form, a payment
element wired, a tag rule, a page, a field mapping — which is neither a repair
nor a full workflow. Those either inflated to $800 or fell out of pricing
entirely (420 of them a sweep).

**Components detected in 3,977 of 6,800 postings.** 1,949 postings ask for
exactly one.

---

## How the prices were derived

Each price is the **median stated budget across postings whose ENTIRE ask was
that one component**, rounded to $25. Not a catalogue fraction. Where that exact
ask actually clears.

**Read this before trusting any single number:** only 689 of 6,800 postings are
single-component *and* carry a fixed budget. Six clusters have ≥30 priced solo
asks; 29 have fewer than 10. Every cluster under 30 is marked `thin` in the code
and in the line's own `why` text. These are directional, not settled, and they
are posted asks — not closed prices, which do not exist anywhere in our records.

### The published SKUs
| component | price | n | postings | evidence |
|---|---|---|---|---|
| write or fix a single API call | $100 | 86 | 780 | solid |
| build a dashboard or report view | $100 | 36 | 717 | solid |
| build a landing page | $150 | 60 | 599 | solid |
| set up tracking or conversion pixels | $400 | 69 | 573 | solid |
| set up support ticket routing | $600 | 20 | 288 | thin |
| set up a new zap or scenario | $50 | 16 | 257 | thin |
| scrape or build a lead list | $50 | 46 | 239 | solid |
| build a document or PDF generator | $150 | 37 | 232 | solid |
| build a chatbot flow | $100 | 12 | 226 | thin |
| configure recurring billing | $250 | 11 | 208 | thin |
| set up file upload or storage | $325 | 27 | 190 | thin |
| build a checkout or cart page | $25 | 26 | 178 | thin |
| build a referral or affiliate flow | $150 | 13 | 173 | thin |
| build a board or project view | $500 | 17 | 171 | thin |
| inject a custom code snippet | $50 | 20 | 166 | thin |

18 further components carry internal prices without a published SKU (demand
under 140 postings or fewer than 10 priced asks). 33 clusters priced in total.

---

## The four rails

A sub-floor number only ever emits when all four hold.

**1. The tier only reduces.** If components sum at or above the class floor,
Class 0 declines and the normal derivation governs. This tier prices small things
small; it never inflates a job past its class.

**2. Uncertified small jobs are not cheap jobs.** Without proven autonomy the
component prices are not authorised at all — no proven kit, open walls, repeated
account access or a call, and the job routes to short reply or listing candidate
exactly as before. The prime rule is untouched: **price drops only as far as
proven autonomy rises.**

**3. Nothing goes under the cost to deliver.** On certified work this replaces
the catalogue floor, because the catalogue floor is a positioning number and this
one is arithmetic:

```
floor = (connects + Seth-minutes × his minute cost) ÷ (1 − Upwork's fee)
```

**4. The consistency gate.** No quote emits that its own lines cannot rebuild.
Asserted per quote, and it held on all 1,493 Class 0 quotes in the cross-check.

### The fix floor bends
It used to apply to any repair. It now applies only to a repair spanning several
components. A single-component job is never dragged up to $500 by it.

### Matching the posted number
Permitted — but only where the buyer's own history already confirmed the number
is real (`cheap_room_confirmed`) **and** it clears the delivery floor. In a
placeholder room the posted figure is not an offer, and matching it would be
bidding against a typo.

---

## ⚠️ The one number nobody has set

`seth_minute_cost` is defaulted to **$2.00/min ($120/hr) and is unconfirmed.**
It is the single biggest lever on the whole tier: it sets the delivery floor,
which decides how many component quotes get raised off their derived price.

An early cross-check run left `psm_estimate` at its uncertified value (~235 min)
and produced a **$525** delivery floor, which swallowed 67% of the tier. With a
coherent certified psm (median 55 min) the floors land at **$25–$290**. Same
code, same corpus — a factor of four, entirely from one unmeasured input.

Every emitted figure carries `delivery_floor_source: 'ESTIMATED'` until Seth sets
it. Read the floors as a shape, not a number.

---

## Cross-check: 6,800 postings

### Live today
Class 0 authorises **nothing**, because certification still fails on every
posting (checks 1 and 6 — no proven kit anywhere, no rehearsal ever run). The
tier is built, deployed and dormant, exactly like the volume lane.

```
packages 2,021 · priced 1,601 · no number 420 · class 0 quotes 0
component tier declined: 1,211 "not certified hands-free", 4 "summed at or above the class floor"
```

### With certification granted (same corpus, psm recomputed accordingly)
```
priced              1,601  ->  1,883
no number             420  ->    138      (282 previously-unpriced jobs resolve)
class 0 quotes                  1,493     (79.3% of all quotes)
class 0 range                $25 - $1,900, median $300
raised to the delivery floor      249     (17%)
distinct totals          53  ->     79

MODE   $2,500 × 776 (48.5%)  ->  $125 × 197 (10.5%)
jobs off the $2,500 mode          590
consistency gate                  holds on all 1,493
```

**This is the first thing that has moved the flatness.** The scope-counter rework
is still unshipped and still the largest lever on the top end, but Class 0 takes
590 jobs off the $2,500 pile on its own.

---

## Known dead path

`component_matched_posted` fired **0 times**. Not a bug — a routing consequence
worth seeing:

- `cheap_room_confirmed` rooms route to **short reply**, and only `full_package`
  reaches the pricing node
- certified jobs route to **`lane_held`** while the volume lane ships OFF, and
  also never reach pricing

So the match-the-posted-number rule cannot fire until the volume lane opens.
When it does, there is a design question waiting: the lane currently bids a flat
`LANE.bid` ($200), but the addendum's logic says the **derived component price
should govern**, floored at cost-to-deliver. That is Seth's dial and it was set
by hand, so it has been left alone rather than silently rewired.

---

## Check 4 amendment (same deploy)

A one-time sign-in no longer fails certification. Signing in once at the start and
running unattended after is acceptable on certified work; needing him back inside
their account mid-delivery is not. Read off the shape record's `access_list`: a
request for a credential is a handover, a request for collaborator/admin/sub-
account presence is a residency.

```
jobs needing their account        4,372
  one-time sign-in (now passes)   3,360
  repeated access (still fails)   1,012
check 4 failures  4,372  ->  1,012
```

**A correction on the earlier number:** this file previously reported 558 check-4
failures. That run had no shape resolved, so the access test fell back to a
posting regex that under-detected badly. With shapes resolved the true
pre-amendment figure is 4,372. The amendment frees 3,360 jobs.

Certified is still 0 — checks 1 and 6 fail on all 6,800 regardless.

**RED confirms are unchanged and unconditional.** Every write to a client's
production system still gates on Seth's recorded confirm, cheap job or not,
certified or not, and still counts toward `psm_estimate`. The component tier buys
no exemption from the rollback law.

**NEEDS SIGN-IN is called out by name.** 4,372 jobs carry
`needs_sign_in_flag` naming the account and whether it is once or repeated. A
sign-in dependency is never silent — asserted in `triage_rules_ok`.

---

## PSM constants: instrumented, not yet measured

`signin_assist` (15 min) and `red_confirm` (30 min) are **unmeasured guesses**
and now say so: every job emits `psm_constants_source: 'estimated'` and
`psm_constants: {signin_assist, red_confirm, measured_n: 0}`.

The measurement cannot be faked from the corpus — it needs ten real jobs carrying
each part, with actual elapsed Seth-time logged. Until then, be aware a wrong
constant suppresses jobs silently: psm feeds routing, and the counterfactual above
showed a 4× swing in the delivery floor from psm alone.

Contract for the next ten jobs: log elapsed minutes per part into the existing
`tasks` table, then replace each constant with the measured median and re-run the
sweep to report the before/after eligibility counts. No new tables.
