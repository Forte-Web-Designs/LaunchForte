# Hardening Phase 0 — status and the STOP

**Aug 9, 2026. Engine work is closed. This is the parallel track.**

Per the runbook, Fortress does items 1–3 and stops. Seth does 4 and 5.

---

## Sequencing note

Runbook §1 says hardening does not start until the Cockpit is published. Seth
directed it to start in parallel. Both publishes are still outstanding (below), so
Phase 1 should not begin until they land — Phase 0 recon does not depend on them.

## PUBLISHES — neither has landed

| workflow | draft | published | state |
|---|---|---|---|
| Cockpit `Hl5zah3PZcHaEkuo` | `780cac4a` | `bc681d47` | **draft ahead** |
| Upwork: Job Engine `7MY8Bqj42haaFbPF` | `4f8967b4` | `a0f6d98a` | **draft ahead** |

What that means precisely:

- The Cockpit's published version `bc681d47` is one I deployed mid-session, so a
  publish did happen at some point. Everything after it is not live: **the role
  guard, the scope counter (v2 and the v2.1 correction), the derived phase split,
  and the narrowed guard.** The live Cockpit still prices with the counter that
  reads one workflow on 92% of postings.
- The Job Engine is running its **original** crons. `1-5` is still in the day
  field. **Weekend coverage is still dead.**

## Phase 0.1 — the four trial blockers

| blocker | status |
|---|---|
| Dashboard 9× duplication | **diagnosed, not fixed** — see below |
| Console image paste | not started |
| Real token minted | not started |
| Trial client pack seeded, returned as REVIEW | not started |

### The 9× duplication: it is a render join, not the seeder

The runbook says diagnose seeder duplication versus render join before styling.
It is the render side, which is the opposite of the first hypothesis:

- **`tasks`: 103 rows, 103 distinct `task_id`.** Zero duplicates.
- **`clients`: 78 rows, 78 distinct `slug`.** Zero duplicates.
- Every render function in the Command Center clears its host first
  (`host.innerHTML = ''` at lines 457, 475, 528, 548, 679). None append without clearing.
- `B6: Dashboard API` is a straight passthrough — 8 nodes, no merge nodes, no
  fan-in points.

So the seeder is clean and the client-side renderers are clean. The fan-out is in
whatever assembles the client/task snapshot between them, which I did not isolate
before stopping. `B6: Command Center Refresh` is a different surface (campaign
ops, 48 nodes).

**What I need to finish it:** the URL the Command Center calls for its
client/task snapshot, or confirmation of which workflow serves it. One `fetch` in
the browser console against that endpoint settles it in a minute — if the payload
carries 9 copies of each task, it is the snapshot builder; if it carries one, the
bug is already fixed and the screenshot is stale.

## Phase 0.2 — the UI simplification pass

**Not started.** The page is `site/command/eH2USoCjM4_Rwle4-JJ9sRPwuA5YMSXG/index.html`,
1,400 lines, one file, no build step. Current structure, in order:

```
clientcontext   collapsible
videoscript     collapsible
cockpit         collapsible
board           ALWAYS OPEN
money           ALWAYS OPEN
clients         ALWAYS OPEN
reports         collapsible
dispatch        ALWAYS OPEN
demand          collapsible
```

The console-first ruling wants: one box at the top, NEEDS ME strip beneath, and
everything else collapsed to one summary row each. So the pass is: promote
`clientcontext` to the single top box, add the NEEDS ME strip, and collapse
`board`, `money`, `clients` and `dispatch` — the four that cannot currently be
collapsed. The mechanism already exists and is used by five sections; this is
applying it consistently, not inventing it.

**Not done because it changes the page Seth is about to live in for a full run,
and the runbook has him sign off on the simplified page before Phase 1.** Doing it
before he has seen the plan risks a second pass. The removal list above is the
proposal; say go and it ships in one edit.

## Phase 0.3 — three candidate jobs

Criteria: judge A, shape resolves, buildable **entirely in house sandbox** with no
client tenant, 5–12 cards.

Pool: 56 judge-A postings met the access and shape filters; 51 landed inside the
card range. **13 survived excluding role-shaped titles** — for a simulation we need
a discrete project, not a seat, which is stricter than the bid guard.

**Candidate A — Programmatic SEO AI Build, Make Automation** · uid `2085835784613070905`
shape `ai-research-agent` · ~8 cards · derived $5,200 · 1.6 days old
Surfaces: Claude, Make, WordPress. **Access: none — house deliverable.**
*The strongest fit: nothing needs a client tenant, every surface is one we own, and it is the freshest of the three.*

**Candidate B — Build AI Client Intake Workflow (OpenAI, Stripe, Google Drive)** · uid `2082023975899034093`
shape `data-collection` · ~8 cards · derived $5,800 · 12.1 days old
Surfaces: Google Sheets, Google Drive, Stripe, Make. Access: one-time sign-in.
*Best shape fit — an intake workflow is exactly the loop Fortress should prove, and it exercises the sign-in doctrine once rather than repeatedly.*

**Candidate C — Backend Development (MVP) for Creator Platform, microsites** · uid `2082462044252330973`
shape `data-collection` · ~9 cards · derived $6,000 · 10.9 days old
Surfaces: Stripe, PostgreSQL, Python. Access: one-time sign-in.
*Buildable in house, but it is app development rather than automation — the weakest shape fit of the three and the least representative of real demand.*

Age does not disqualify B and C: nobody is bidding, the posting is a script.

**One thing the search surfaced:** at judge A and 5–12 cards, the pool skews
heavily to role-shaped postings — big enumerated descriptions tend to be job
descriptions rather than projects. Two of the first three candidates were
"Specialist … (Part-Time)". They pass the bid guard correctly because they carry
build signal, but they are wrong for a simulation.

## STOP

Waiting on Seth for:

1. **Both publishes.**
2. **Go on the UI removal list**, then it ships and he signs off on the page.
3. **The snapshot endpoint** so the 9× diagnosis closes.
4. **Pick a candidate** — A, B or C.

Nothing proceeds to Phase 1 until those land.
