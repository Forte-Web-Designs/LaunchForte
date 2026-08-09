# Triage v2, as built

**Built Aug 9, 2026, against `upwork_triage_system_runbook.md` (Aug 8).**
Source of record: `generators/cockpit-triage-node.js`. Deployed as the n8n node
**"Route the job"** in the Cockpit (`Hl5zah3PZcHaEkuo`), between
`Read Shapes (Cockpit)` and `Read Specs C`, behind three new data-table reads.

---

## The one design decision everything else follows from

**Every check fails closed.**

A missing record is a failed check, not a skipped one. If the builds registry is
not upstream, check 1 fails. If a tool has no row in the known-path library,
check 2 fails. If the rehearsal timestamp is empty, check 6 fails. If none of the
registries are readable at all, the gate closes completely.

This is the prime rule in code. Underpaid work is permitted only where Fortress
*provably* handles the job end to end, and a gate that opens when a record is
absent is a gate that opens on optimism. When in doubt, the doubt decides.

The consequence, which is the honest headline of this build:

> **Nothing in the estate certifies today. Zero of 6,800 postings.**

That is not a bug in the gate. It is the gate reporting the state of the records,
and the records are thin in four specific, nameable places. See "What is actually
blocking the lane" below.

---

## What ships

### Fields computed on every job
| Field | What it is |
|---|---|
| `psm_estimate` | projected Seth-minutes, the primary router |
| `psm_parts` | the minutes broken out, so the number can be argued with |
| `buyer_avg_per_hire` | client spend ÷ hires; falls back to `avg_per_contract`; null when unknown |
| `room` | `auction` when the posted budget sits at or under the $500 fix floor or the average is under $500; else `value`; null when nothing is known |
| `room_below_floor` | posted FIXED budget under the $200 lane floor |
| `route` | one of the four lanes |
| `certified` | the six-check gate |
| `certified_failed_check` | never false without naming the check |
| `listing_candidate` | feeds the Project Catalog shelf |
| `triage_action` | what actually happens: `no_bid`, `lane_bid`, `lane_held`, `short_reply`, `full_package` |

Buyer math **never gates**. Missing stats leave `room` null and routing proceeds.

### The four routes
- `hands_free_house` — the volume lane. Certified, fixed-price, at or above the floor.
- `hands_free_shape_client_access` — the listing lane. No bid; files a shelf candidate.
- `assisted` — the ladder. Real Seth-minutes, catalogue pricing, buyer math sets position in range.
- `heavy` — full treatment. Calls, scoping, migrations.

### The six-check certification gate
1. **proven kit** in the builds registry — status proven/built/delivered, `proven_minutes > 0`, and not stubbed "estimated only, nothing built"
2. **known path** on every resolved surface — a working API route (`endpoint_status` = answered 2xx) or exact clicks on file with a credential
3. **zero open walls** in the blockers ledger on those surfaces
4. **no client-account access** — read from the shape record's `access_list`, with a deliberately broad posting-text fallback
5. **no call**
6. **freshness** — a green rehearsal inside 14 days (`session_last_verified`)

### The volume lane ships OFF
`LANE.enabled = false`, `connects_budget_monthly = null`. A certified job is still
routed and still reported; it emits `lane_held` instead of `lane_bid`. The lane
cannot bid while either of those is unset, and that is asserted in
`triage_rules_ok` on every single job, not checked once at startup.

**To open it, Seth confirms two numbers:** the $200 floor (or his own), and the
monthly connects budget. Nothing else is blocking the code.

---

## What is actually blocking the lane

Read from the live tables on Aug 9, not assumed:

| Check | State of the records today | Effect |
|---|---|---|
| 1. proven kit | `builds` has **19 rows, all `status=briefed`**, `proven_minutes=0` on every one, `stubs = "estimated only, nothing built"` on every one | fails on **6,800 / 6,800** |
| 2. known path | `tools_kb` has 177 rows; `login_state` is null on **all 177**; only 38 answered 2xx; 17 have a credential | fails on 6,110 |
| 3. open walls | `blockers` has 14 rows — every `kind` is `api_key`, `shell`, `reconnect`, `quota`, `question`, `fix` or `scope`. **Not one UI or surface wall is filed.** The Margaret walls named in the runbook (the coordinate-bug day, the extension dropping the tab three times, the sequences inbox) **are not in this ledger.** | fails on 626 — and would fail on more if the real walls were filed |
| 4. client account | **All 32 shapes have a populated `access_list`.** Every known shape needs their tenant. | fails on 558 |
| 5. call | posting text | fails on 248 |
| 6. freshness | `session_last_verified` is **empty on all 177 tool rows**. Nothing has ever been rehearsed. | fails on **6,800 / 6,800** |

Two of these — the proven kit and the rehearsal — fail on *every posting in the
corpus*, which means they are the binding constraints and the other four are
currently decorative. The order of work is therefore fixed by arithmetic rather
than preference:

1. **Prove one kit end to end** and record it in `builds` with real
   `proven_minutes`. One is enough to open one lane.
2. **Run the first rehearsal** and stamp `session_last_verified`. Check 6 is a
   schedule, not a build.
3. **File the Margaret walls** in `blockers`. Check 3 is vacuously passing right
   now, which is worse than failing: it is a gate reporting green on a ledger
   nobody has written to.
4. Then checks 2 and 4 become the real conversation, and check 4 is what the
   listing lane exists to answer.

---

## What 6,800 real postings do

Run Aug 9 through the deployed node, every posting in `upwork_jobs`, zero errors,
`triage_rules_ok` true on all 6,800.

```
ROUTE    assisted 6,552   heavy 248
ACTION   short_reply 4,123   full_package 1,346   no_bid 1,331

no_bid             1,331  (19.6%)
room_below_floor   1,331  (19.6%)
listing_candidate    519  (7.6%)
certified              0
```

**One posting in five now costs zero seconds.** That is the Joel volume: 1,331
postings whose stated fixed budget sits under the floor, which previously each
had at least a judge score spent on them and sometimes a full sketch package.

**No C-scored or U-scored job ever reaches a full package.** An early cut of this
node promoted 2,646 C-scored postings to `full_package` because their buyers were
rich, which is the pricing-flatness bug wearing a different hat. Triage adds lanes
*below* the judge; it does not overrule it. Heavy runs through the same test —
"full treatment: value rooms only" — because needing a call in a thin room is the
most expensive combination there is, not a reason to spend more.

### The shelf menu that falls out of it
519 listing candidates, aggregated by surface (threshold 8):

```
gohighlevel 64 · hubspot 55 · google sheets 48 · shopify 44 · quickbooks 40
stripe 30 · make 28 · n8n 25 · slack 19 · claude 16 · google drive 11
twilio 10 · zoho crm 9
```

This is the Project Catalog menu, derived from real demand rather than guessed.
Every one of these is a shape that *could* run hands-free and is blocked only by
needing the buyer's account — exactly the tier §3.2 says to serve on a shelf
instead of in an auction.

---

## The seven jobs from section 7

`generators/triage-check.js` runs them as fixtures. All seven produce the route
and the response the runbook states. Job 2 is run twice: once against today's
registries (assisted, because no kit is proven) and once against a stubbed
registry carrying the proven kit and a fresh rehearsal — where it certifies and
returns `lane_held`. That second run is the proof that the closed door is a
record problem and not a code bug.

Four negative controls, each of which must trip and does: remove the proven kit,
age the rehearsal past 14 days, open a wall on a resolved surface, remove the
registries entirely.

```
node generators/triage-check.js      # exits non-zero on any regression
```

---

## Files

| File | What it is |
|---|---|
| `generators/cockpit-triage-node.js` | source of record for the deployed node |
| `generators/triage-check.js` | the seven fixtures, the invariants, the negative controls |
| `generators/triage-sweep.js` | browser-console sweep: runs the **deployed** node over the corpus, prints the opportunities line, files the `listing_candidate` ideas rows behind a `WRITE` flag |

`triage-sweep.js` reads the node source out of the live workflow rather than
carrying its own copy. A second implementation of the routing arithmetic is
exactly the bug that was fixed in pricing, and it is not being reintroduced here.

No posting text is in this repo. The sweep runs inside the n8n tab and only counts
come back.

---

## The weekly report's opportunities line

There is no weekly-report workflow in n8n to patch — the internal report is not an
n8n artefact. The line is therefore defined here and produced by the sweep:

```
listing_candidate 519   room_below_floor 1331
shelf menu (>= 8): gohighlevel x64, hubspot x55, google sheets x48, ...
certified today: 0
```

`triage-sweep.js` prints exactly this. It files ideas rows with
`tag: 'listing_candidate'`, `shape: 'upwork:<surface>:listing_candidate'`,
`source: 'upwork_triage'` — the same discipline the judge already uses for
`product_gap`. **It is shipped dry-run.** Flipping `WRITE = true` files 14 rows.

---

## Still open

1. **The floor and the connects budget.** Two numbers from Seth, then the lane
   can open — for whatever certifies, which today is nothing.
2. **The ingest-side auto-route.** Acceptance §9 says a Joel-shaped job produces
   zero output "except two logged tags". Triage is currently deployed inside the
   Cockpit, which Seth fires deliberately, so today it *informs* a run rather than
   preventing one. There is no Upwork ingest/scoring workflow in n8n to attach it
   to — the Apify ingest and the A/B/C judge live outside it. The node is written
   to run anywhere (it falls back to `$json` when `Merge Context` is absent), so
   this is a placement question, not a rewrite.
3. **The Margaret walls are unfiled.** Check 3 cannot mean anything until they
   are in `blockers` with `kind` naming the surface class.
4. **`triage_stop` is emitted but not wired to a hard halt.** Deliberate: an
   automatic halt on a workflow Seth fires by hand could kill a run he wanted.
   One IF node turns it on once he has seen the numbers land.
