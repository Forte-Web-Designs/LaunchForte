# Ingest root cause, the floor-up reprice, and the priority board

**Aug 9, 2026.**

---

## 1. The ingest gaps are weekends. All of them.

Not a failed run. A schedule that only covers part of the week.

```
date         dow   rows   hours UTC   lanes
2026-07-26   Sun       0   —          NOTHING RAN
2026-07-27   Mon     815   01-23      instant 181  sweep 516  net 118
2026-07-28   Tue     647   12-22      instant 149  sweep 498  net 0
2026-07-29   Wed     654   12-23      instant 142  sweep 413  net 99
2026-07-30   Thu     691   12-23      instant 141  sweep 446  net 104
2026-07-31   Fri     588   12-23      instant 108  sweep 378  net 102
2026-08-01   Sat       9   12-12      instant 9    sweep 0    net 0
2026-08-02   Sun       0   —          NOTHING RAN
2026-08-03   Mon     492   16-23      instant 115  sweep 377  net 0
2026-08-04   Tue     709   12-23      all three
2026-08-05   Wed     734   12-23      all three
2026-08-06   Thu     678   12-23      all three
2026-08-07   Fri     631   12-23      all three
2026-08-08   Sat     152   01,13,19   net 150 only
2026-08-09   Sun       0   —          NOTHING RAN
```

**Weekday mean 664/day across 10 days. All four weekend days together: 161 rows.**

Three things fall straight out of that table:

**The window is 12:00–23:00 UTC** on every healthy day — 08:00 to 19:00 Eastern.
A workday. Nothing runs 00:00–11:00 UTC, ever. Combined with the weekend
blackout, the ingest is awake for roughly a third of the week.

**Monday does not backfill.** Rows scraped on a Monday, grouped by the date they
were *posted*: Jul 27 → 740 posted Jul 27; Aug 3 → 492 posted Aug 3. The only
exception is the very first run (Jul 27 picked up 75 posted Jul 26), which was
the initial backfill. **The weekend's postings are never captured, not even
late.** The lanes fetch the recent page, and by Monday the weekend has scrolled
off it.

**The `net` lane is separately flaky** — it produced nothing on Jul 28 and Aug 3,
2 of the 10 weekdays with data. Roughly 100 postings each time.

### What it costs
At ~664/weekday and Upwork weekend volume running lower but not zero, the
blackout is on the order of **700–900 postings a week, permanently**, plus ~100
per missed `net` day. Not the ~1,200 lost once on Aug 1–2: ~1,200 lost *every
weekend*, and it has happened every weekend the table has existed.

### Where it is not
**No n8n workflow writes `upwork_jobs`** — all 100 checked, zero matches — and
the ingest code is not in this repo. So n8n execution logs have nothing to say
about it. The ingest is Apify actors triggered from outside n8n, and the
08:00–19:00-Eastern-weekdays-only shape is the signature of a trigger that lives
on the Mac mini and stops when the machine sleeps.

### The fix
The repair is a schedule that does not depend on a desk being occupied:

1. **Move the trigger into Apify's own scheduler**, which runs in Apify's cloud
   7×24 regardless of the Mac. This is the actual fix and it costs nothing —
   Apify is already owned and already running the actors.
2. Failing that, an n8n Cloud Schedule trigger calling the Apify run endpoint.
   Same property: not on the Mac.
3. Either way, extend to 7 days and widen past the 12:00–23:00 window.
4. Add a **`net`-lane liveness check** — it fails silently and independently.

The 1.5-day staleness warning already in `triage-sweep.js` stays as the detector.
It is not the repair and was never meant to be.

---

## 2. Class 0, repriced from the floor up

Component prices no longer come from budget medians. Those are now **ordering
evidence only** — they rank demand, they do not set a price.

```
delivery = component Seth-minutes x $2.50
warranty = delivery x 15%                    reserve for rework
connects = 6 x $0.15 / WIN RATE              the losing bids
tooling  = $400/mo / 3.5 wins per month
price    = (delivery + warranty + connects + tooling) / (1 - 10% Upwork fee)
```

**Assumed win rate: 8%** → $11.25 of connects per win. **Every one of those four
inputs except the minute cost and the Upwork fee is an assumption**, and they are
named in `component_price_assumptions` on every quote. `tool_spend` is all zeros,
so the $400/month is stated, not measured.

### The honest limit, found while building it
`psm_estimate` takes only **two distinct values** across the whole corpus — 10
and 55 minutes — because it measures Seth's *hands* (sign-in, RED confirms,
thread) and not build effort. So floor-up produces a **two-tier component list**:
$175 for the quick ones, $325 for the rest. Per-component *build* minutes do not
exist anywhere and would be needed for a graded list.

**But components sum, and at job level that recovers the grading:** 27 distinct
prices from **$175 to $3,275, median $650**, across 736 priced bid-pool jobs.

The flat component list never under-prices, which the budget-derived one did — a
$25 checkout page was the old list's answer.

---

## 3. The priority board

**922 bid-eligible, priced, full-package jobs. Ten proposals a week.** Choosing
is the entire constraint, and nothing was ranking.

```
score = (derived quote ÷ psm_estimate) × judge × buyer × freshness
```

Return per Seth-minute is the spine, because his minutes are the only input that
does not scale. Judge grade (A 1.30, B 1.00, C 0.70), buyer history (≥$1,000/hire
1.25, ≥$500 1.10, thin 0.90, unknown 1.00) and age (1.00 fresh decaying to 0.55
at the seven-day edge) are adjustments, never gates.

### What ranking is worth
```
              mean quote   mean psm   return per Seth-minute
top 15            $2,733     10 min                    $273
whole board         $679     46 min                     $24
```

**11× on return per Seth-minute, from choosing well.** The top 15 are all judge A
or B, all between 1.4 and 5.6 days old, 8 of 15 with real buyer history.

Score spread across the board: p10 2.4 · median 9.5 · p90 49.3 · max 384.8. The
distribution is wide enough that ranking is worth doing — if it were flat, the
board would be theatre.

`generators/priority-board.js`, dry-run by default. `WRITE_RANKS = true` stamps
`priority_rank` and `quoted_price` onto the proposals rows so **the board can be
scored later**: did the jobs it ranked first actually win? A ranking that cannot
be wrong out loud is not worth keeping.

---

## 4. Outcome capture

Nothing in the estate recorded whether a bid won. Worse: all 61 rows in
`proposals` are `status: "draft, tokens missing"` — **not one proposal has ever
been recorded as sent.**

Seven columns added to the existing `proposals` table. No new tables:

| column | what it holds |
|---|---|
| `outcome` | won / lost / no_response / withdrawn |
| `proposal_sent_ts` | when it actually went out, not when the draft was made |
| `quoted_price` | what we asked |
| `actual_price` | **what the client agreed to** — the number missing from every pricing decision this month |
| `actual_seth_minutes` | measured, to replace the psm guesses |
| `priority_rank` | where the board put it, so the ranking can be scored |
| `outcome_ts`, `outcome_note` | |

`actual_price` is the one that unblocks the most. Component prices, the $2,500
mode, the win rate behind the connects term and the psm constants are all waiting
on the same thing: five to ten real outcomes.
