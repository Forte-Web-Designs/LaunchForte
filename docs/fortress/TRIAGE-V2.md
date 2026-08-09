# Triage v2, as built

**Built Aug 9, 2026. Revised the same day — see "The revision" below, which
supersedes the floor rule entirely.**
Source of record: `generators/cockpit-triage-node.js`. Deployed as the n8n node
**"Route the job"** in the Cockpit (`Hl5zah3PZcHaEkuo`), between
`Read Shapes (Cockpit)` and `Read Specs C`, behind three data-table reads.

---

## The revision: the floor is dead as a gate

The first cut refused any posting whose stated fixed budget sat under $200. It
looked disciplined and it was wrong, and the corpus says exactly how wrong.

**The largest buyer that rule would have silently binned had spent $1,854,701 on
Upwork.** Fifty-one of the buyers it killed average $1,000 or more per hire. One
posted "$30" against a $7,633 per-hire average. They were not offering $30 for
the work — they were typing a number into a required field.

So the rule now is: **the posted budget is a signal and never a gate.** Nothing
is refused for being cheap on its face. The number is compared against what the
buyer actually pays, and the comparison decides what the number *means*.

### The placeholder test

Runs on every posting with a stated **fixed** budget. Hourly is excluded on
purpose: comparing $40/hr against an $800 per-hire average is a category error,
so an hourly post routes exactly like one with no budget stated.

| Verdict | Condition | What happens |
|---|---|---|
| `placeholder_budget` | posted ÷ average **< 0.5** | the number is ignored **entirely**. Routes on judge grade and shape, identically to a job with no budget stated. |
| `cheap_room_confirmed` | ratio ≥ 0.5 **and** average < $500 | the posted number and the buyer's history agree the room is thin. Short reply. |
| `budget_confirmed` | ratio ≥ 0.5 **and** average ≥ $500 | the number is real and so is the buyer. |
| `no_spend_history` | a number posted, no buyer history | nothing to test it against. Judge grade alone. |
| `no_budget_stated` / `hourly_no_fixed_budget` | no fixed number | judge grade and shape. |

Every job emits `budget_test`, `budget_test_why`, `posted_vs_avg_ratio` and
`posted_budget_amount`, so which test fired is always on the record.

Joel is the calibration case in both directions: $100 posted against a $132
average is `cheap_room_confirmed` — believed, and given the short reply, not
silence. Seth's example is the other pole: $50 against $800 is `placeholder_budget`
and the number is thrown away.

**`room_below_floor` still gets emitted, and it now routes nothing.** It is kept
purely so the weekly report can count the thin end of the auction.

### The invariants that hold this in place
Asserted on every job in `triage_rules_ok`, not checked once:

- no `no_bid` may come from any route except the listing lane — a posted number can never end a job
- a `placeholder_budget` job may only reach `short_reply` if the judge graded it C or U, i.e. only for a reason that would have applied with no budget at all
- `cheap_room_confirmed` requires the buyer's own history to agree (`avg < $500`)
- `placeholder_budget` and `cheap_room_confirmed` can never both be true
- every job logs which test fired

`triage-check.js` proves the first of those directly: it runs the placeholder
fixture twice, once with the $50 budget and once with `not stated`, and asserts
the route and action are identical.

---

## The data fix that had to come first

**`client_hires` was 0 on all 6,800 rows, so `buyer_avg_per_hire` could not
compute anywhere and the placeholder test had nothing to test against.** So were
`client_avg_rate` and `application_cost` — three dead columns.

The hires number was never actually missing. It was stored under a different
name:

- `client_reviews` is populated on 3,933 rows and is the contract count
- `avg_per_contract` is populated on 3,838 rows and equals `client_spend ÷ client_reviews` (verified: 95.5% match within 2%, the rest is rounding on small numbers)

So the ingest has been computing the per-hire average all along and writing zero
into the field triage reads.

**Backfill, done Aug 9:** `client_hires = client_reviews` where reviews > 0.
3,933 rows updated via 415 grouped PATCHes, zero failures. Derived entirely from
data already owned — no Upwork access, ever.

```
buyer_avg_per_hire computable:   0  ->  3,902 of 6,800  (57.4%)
```

**The honest caveat:** reviews ≤ hires, because not every completed contract
leaves feedback. So this *understates* hires and therefore *overstates* the
per-hire average. That bias pushes postings toward `placeholder_budget`, which
routes on judge grade — meaning the error direction is "consider more work",
never "refuse work". That is the safe way to be wrong here.

### Still to fix at the source
No n8n workflow writes `upwork_jobs` — checked all 100, zero matches — and the
ingest code is not in this repo either. It lives in Apify plus the Console.
Whoever owns that mapping needs to:

1. capture **hires** from the buyer panel as its own field (Upwork shows hires
   and reviews separately; they are not the same number)
2. stop writing `0` into `client_avg_rate` and `application_cost`, or drop the
   columns
3. keep writing `avg_per_contract` — it is the one buyer-math field that has
   always worked

Until 1 lands, every fresh scrape arrives with `client_hires = 0` and the
backfill has to be re-run. `triage-sweep.js` can carry it.

---

## The design decision everything else follows from

**Every certification check fails closed.** A missing record is a failed check,
not a skipped one. If the builds registry is not upstream, check 1 fails. If the
rehearsal timestamp is empty, check 6 fails. The gate opens only as real records
appear and can never open by accident of plumbing.

Note the asymmetry, which is deliberate: **the gate fails closed, the budget
fails open.** Doubt about our own capability costs us the cheap lane; doubt about
a buyer's number costs them nothing. Those are the correct directions.

---

## What ships

### Fields computed on every job
`psm_estimate` · `psm_parts` · `buyer_avg_per_hire` · `room` · `budget_test` ·
`budget_test_why` · `placeholder_budget` · `cheap_room_confirmed` ·
`posted_vs_avg_ratio` · `posted_budget_amount` · `room_below_floor` (reporting
only) · `route` · `certified` · `certified_failed_check` · `listing_candidate` ·
`triage_action` · `triage_judge_score`

`room` is now read **only** from the buyer's per-hire average (`auction` under
$500, `value` at or above, null with no history). A posted number can no longer
make a room thin.

### The four routes
`hands_free_house` (volume lane) · `hands_free_shape_client_access` (listing
lane, no bid) · `assisted` (ladder) · `heavy` (calls, scoping, migrations).

The one budget-shaped condition left on routing is that an **hourly** post cannot
reach the volume lane — a mechanism, not a price: the tracker screenshots the
working screen.

### The six-check certification gate
proven kit · known path per surface · zero open walls · no client-account access
· no call · green rehearsal inside 14 days.

### The volume lane ships OFF
`LANE.enabled = false`, `connects_budget_monthly = null`. `LANE.bid` ($200) is
now only what a certified lane job *bids* — it gates nothing.

---

## Pricing is unchanged, and that is verified not assumed

The pricing node reads the posting text and the resolved shape. **It never reads
the posted budget** — grepped and confirmed. The only ceiling in it is Launch
Forte's own $3,500 first-engagement platform ceiling, which triggers a phase
split, never a discount.

Two prohibitions now sit in the Prompt of Record:

- when `placeholder_budget` fires, the letter is told the posted number is a
  placeholder and must not bid it, reference it, work toward it, apologise for
  exceeding it, or let it shape the scope
- unconditionally: **a posted budget is never a ceiling on the derivation.** If
  the derived figure lands above what they posted, the phase split carries it —
  never a discount, never a quietly trimmed scope, never a remark about their
  budget

---

## What 6,800 real postings do now

Zero errors. `triage_rules_ok` true on all 6,800.

```
BUDGET TEST   hourly 2,880 · no budget stated 1,611 · no spend history 820
              cheap_room_confirmed 708 · placeholder_budget 649 · budget_confirmed 132

ACTION        short_reply 4,779 · full_package 2,021 · no_bid 0
ROUTE         assisted 6,552 · heavy 248
ROOM          auction 1,980 · value 1,953 · unknown 2,867
```

### Before and after
| | old floor rule | placeholder test |
|---|---|---|
| jobs refused outright | 1,331 | **0** |
| full packages | 1,346 | **2,021** |
| quotes produced | 1,058 | **1,601** |

### The 1,331 the old rule would have killed
```
458  cheap_room_confirmed -> short reply     (the rule was right about these)
332  placeholder_budget   -> short reply     (judge said C/U, not the budget)
284  no_spend_history     -> short reply
152  placeholder_budget   -> FULL PACKAGE
105  no_spend_history     -> FULL PACKAGE
```
257 of them now earn a full package. 207 produce a real derived quote, worth
**$429,200** of pipeline the floor rule was throwing in the bin — including a
$1.85M buyer who posted $20.

### The flatness is still there
Mode is **$2,500 on 48.5% of quotes** (776 of 1,601), essentially unchanged from
the 49.2% before this revision. Triage decides *whether* to quote; it has never
touched *what* the number is. The scope counter still reads one workflow on most
postings and that rework remains unshipped — it is still the largest single lever
on revenue in the estate.

**420 jobs that earned a full package produced no price at all** (up from 288,
because the population grew) because no shape resolved. Those fail silently.

---

## Files

| File | What it is |
|---|---|
| `generators/cockpit-triage-node.js` | source of record for the deployed node |
| `generators/triage-check.js` | the runbook's jobs as fixtures plus the placeholder cases, the invariants, the negative controls |
| `generators/triage-sweep.js` | browser sweep: runs the **deployed** node over the corpus, prints the opportunities line, files `listing_candidate` rows behind a `WRITE` flag |

`triage-sweep.js` reads the node source out of the live workflow rather than
carrying its own copy. No posting text is in this repo.

---

## Still open

1. **Fix hires at the ingest**, so the backfill stops being a recurring chore.
2. **One proven kit, one rehearsal** — the only thing standing between the estate and a working volume lane. Nothing certifies today: 0 of 6,800.
3. **File the Margaret walls** in `blockers`. Check 3 passes vacuously until they exist, which is worse than failing.
4. **The scope counter rework.** Half of every quote is still $2,500.
5. **Two numbers** to open the lane: the bid and the monthly connects budget.
6. **`triage_stop` is emitted but not wired to a hard halt** — deliberate, since the Cockpit is fired by hand.
