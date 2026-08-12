# Pricer, 11 Aug — the composite ask, and which two systems

Workflow `Hl5zah3PZcHaEkuo`, node `Price the build`.
Draft saved as `66eadece-4689-45d7-a969-836ac8cd4ac2`. **Live is still
`dd6251c4-555c-41ad-9cb8-7cf99c77c370`** — nothing published, awaiting Seth.

Handoff items 1 and 2. Both changes are in the node only; the repo copy
`generators/cockpit-pricing-node.js` is the Aug 9 pricer and is now two
generations stale. It was not touched.

## What changed

**1. The composite ask (`IMPLIED`).** Rule 4 of the pricing package says the
systematic error is collapsing many rules into one piece. Some asks are
composite by definition: reconciliation is a matching rule AND a path for what
does not match — without the second half nothing is reconciled, it is only
compared. Four families carry an implied second decision: reconciliation,
identity across systems, deduplication, migration.

Conservative by construction. An extra fires only when the naming ask was
already counted as a clause of its own, and never when the posting spells the
second half out itself (that clause is already a piece). Each extra is named,
so it prints in the parenthetical and the client can remove it.

**2. Which two systems (`PAIR_DIR`, `sysHits`).** A connection line now says
`Shopify into Slack`, not `connecting the two systems`. The pair is read from
the clause the piece was found in. Where the whole job names exactly two
systems, the pair is those two — with only two systems there is no third thing
a connection could join, so that is reading the posting, not guessing. Three or
more systems and the label stays clause-local; a guess that names a system is
worse than a generic phrase. Unresolvable pairs fall back to the old shortName.

## Measured, 240 real postings out of `upwork_jobs`

Old node vs draft, run offline with stubbed inputs. No posting text left the
machine.

| | old | draft |
|---|---|---|
| held by an assert | 41 | 41 |
| Decisions pieces, total | 73 | 79 |
| quotes whose count moved | — | 6 |
| book value, 199 priced | $171,400 | $175,600 |
| lines with no name | 17 | 17 |
| connection lines naming a pair | 1 of 49 | 7 of 49 |

No assert fires that did not fire before, and none stopped firing.

## The finding, and it is bigger than either fix

**118 of 169 build-mode quotes carry zero Decisions.** 42 of those postings
contain plain rule language — if / when / route / score / exclude / reconcile /
threshold / flag — and still price no decision at all. At $700 a decision that
is the largest number on this page.

Instrumenting the judged loop over those 42 postings, 1,523 clause units in:

- **987 rejected by `RULEVERB`** — no rule verb matched
- **370 rejected for want of a name** — clause passes every gate, matches no
  judged row in `ASKS`, so it has no `say` and is dropped
- 78 rejected as bidder-directed, 5 as goal language, ~83 as too short

The 370 are the honest half of the hole: rules the engine recognised as rules
and then discarded because it could not label them. Fixing that means either
widening the judged rows in `ASKS` or giving an unmatched rule clause a name
from `conceptOf`. It moves money in the direction the document warns about, so
it wants its own card and its own corpus run — not a patch bolted onto this one.

The pair labels have a data ceiling worth knowing before more work goes in:
**109 of 199 postings name exactly one system and 56 name none.** Only 34 name
two or more, so most connections cannot be named by pair from the posting alone,
however good the detector gets.
