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

---

# Follow-up, Aug 9 — and a finding that invalidates the price basis

## 1. `seth_minute_cost` is now derived, not estimated
Set to **$2.50/min**, from the catalogue's own $150/hr specialist band floor.
`delivery_floor_source` flips to `DERIVED`. Per-input provenance is emitted:
`upwork_fee` and `connect_cost` are Upwork's published rates; `connects_per_bid`
(6) remains the one unmeasured assumption.

Delivery floors move from $25–$290 to **$30–$365, median $155**.

## 2. ⚠️ SELECTION BIAS CHECK — the basis is broken, in the opposite direction

The hypothesis was that single-component postings with stated budgets are the
cheapest sub-population by construction, so their medians run low. The check says
something worse.

**Median posted budget barely moves with scope at all:**

| components asked for | median posted | median description |
|---|---|---|
| 0 | $50 | 771 chars |
| 1 | $75 | 1,064 |
| 2 | $100 | 1,334 |
| 3 | $125 | 2,188 |
| 4 | $120 | 1,660 |
| 5 | $125 | 2,213 |
| 6 | $75 | 3,319 |

A posting asking for **six** things is budgeted the same as one asking for
**one**. Description length rises monotonically across the same bands, so the
component count is measuring real scope — the budget field simply is not
responding to it.

**So the single-ask medians are not "where that ask clears." They are what people
type in the budget box, which is $50–$150 regardless of what is being asked for.**
It is the placeholder finding generalised: not merely that *some* budgets are
placeholders, but that the budget column carries almost no scope information.

**The multi-component estimator is worse, not better.** It divides an already
scope-flat number by the component count, so every allocation collapses toward
$25. Applying "where they diverge more than 2×, the multi-component figure
governs" would have driven the entire tier to $25 — the opposite of the rule's
intent, which assumed a downward bias in the single-ask figure.

Both columns are reported side by side in the sweep. **The >2× substitution rule
was NOT applied**, because the estimator it promotes is contaminated by the same
defect it was meant to correct, and a rule that fires on 100% of clusters is not
correcting a bias — it is replacing one bad number with a worse one.

**What this leaves standing:** the taxonomy, the demand ranking, the four rails,
and the cost-to-deliver floor — which is now the only figure in Class 0 derived
from arithmetic rather than from the budget field. Every component price above
should be read as a demand-ranked placeholder awaiting real closed amounts.

## 3. The flat $200 lane bid is deleted
The lane bids the **derived component price with cost-to-deliver as the hard
minimum**. Triage no longer emits a bid figure at all — it names the rule and
lets pricing derive the number, asserted in `triage_rules_ok`. A single flat
number priced a $600 ticket-routing build and a $50 zap identically.

## 4. Quotes under the delivery floor: none. The floor binds.
**0 of 1,493 Class 0 quotes emit below their own floor.** The `$25` figures in
the previous report were *component sums before the floor applied*, not quotes;
357 (24%) were raised to the floor. No jobs need routing to no-bid on this basis.

## 5. Re-run, all four applied
```
delivery floor        $30 - $365, median $155     (source: DERIVED)
class 0 quotes        1,493
class 0 range         $30 - $1,900, median $300
raised to the floor   357 (24%)
under their floor     0
consistency gate      holds on all 1,493

all quotes            priced 1,883 · no number 138 · distinct totals 78
MODE                  $155 x273 (14.5%)
still at $2,500       186   (was 776)
```

---

# Archive / bid pool split (same deploy)

`age_days` and `bid_eligible` are **computed at read time, never stored** — a
stored freshness flag is wrong within a day and would quietly authorise bidding
on dead postings. Archived rows stay in the table: the buyer-spend column, the
component prices and the pricing anchors all came from postings older than seven
days.

```
bid_eligible (<= 7 days)   3,392  (49.9%)
archive (> 7 days)         3,408
no posted_at               4       (fails closed — not bid on)

arrivals                   597/day mean over 11 full days
table spans                13 days (Jul 26 - Aug 8)
```

**The real weekly supply:** of 2,021 full-package jobs, **985 are still fresh**,
767 of them carrying a price. Against 10 proposals a week that is roughly **99×
oversupply** — the constraint is not finding work, it is choosing.

**Two gaps in the ingest worth knowing:** Aug 2 has zero rows and Aug 1 has nine,
and nothing has arrived for Aug 9. The sweep now prints a warning when the newest
posting is more than 1.5 days old.
