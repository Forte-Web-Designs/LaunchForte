# The UI pass: what came off the page

**Aug 9, 2026. Phase 0.2. `site/command/index.html`, one file, no build step.**

The console-first ruling: the page is a chat with a dashboard behind it. One box
at the top, NEEDS ME beneath it, everything else collapsed to one summary row
each — expandable, never required to get anything done.

Reported as removals, not additions, because the point of the pass is what stops
demanding attention.

---

## Removed from the always-visible page

| what | was | now |
|---|---|---|
| **The board** | a full multi-column kanban, always rendered | one row: *"14 tasks across 6 clients."* |
| **Money** | a metric grid, always rendered | one row: *"Total cost $X."* |
| **Clients** | a search field, a Show-all button and 78 client cards, always rendered | one row: *"N clients shown."* Search and Show-all move inside |
| **The Client context collapse** | a Collapse ↑ control on the top box | removed — the paste box no longer collapses, because it is the one thing the page is for |
| **`wireClientContextToggle()`** | 331 characters of toggle wiring | deleted, not orphaned |

Four sections could not be collapsed before this pass; five already could. That
asymmetry was the mess — the ruling did not need a new mechanism, it needed the
existing one applied to the four that skipped it.

## Added — deliberately only one thing

**NEEDS ME**, directly beneath the paste box. It reuses `taskNeedsMe`, the signal
already computed per board card after the old NEEDS ME section was retired. So
this is a roll-up of an existing definition, not a second one: blocked task, reply
overdue seven days or more, a doorbell, or a report marked NEEDS YOU. Caps at 12
with a "N more on the board" line, and each row says *why* it needs him rather
than just that it does.

## Consolidated

Five hand-rolled toggle functions had the same body with different ids. The four
promoted sections share one `wireSection(name)` instead. The existing five were
left alone — rewriting working code to save duplication is a different change and
does not belong in a pass Seth has to sign off before living in it for a week.

## The resulting page, top to bottom

```
Client context     ALWAYS OPEN   the paste box
Needs me           ALWAYS OPEN   only what is waiting on him
Video script       collapsed
Cockpit            collapsed
Board              collapsed  <- promoted in this pass
Money              collapsed  <- promoted
Clients            collapsed  <- promoted
Reports            collapsed
Dispatch           collapsed
Demand             collapsed
```

Two things visible on load. Everything else one click away.

## Verified

- JS parses (`validate_cc.js`)
- Every static `$('id')` lookup in the script resolves against the markup — 66 lookups, 107 ids, **zero missing**. This is the check that catches a toggle wired to an element the markup no longer has, which is exactly the failure the removals could have introduced
- All four promoted sections have their full set: `Toggle`, `Flip`, `Collapsed`, `Body`

Not verified: how it looks. The page has not been rendered — that needs a deploy,
and it is the thing Seth is signing off.
