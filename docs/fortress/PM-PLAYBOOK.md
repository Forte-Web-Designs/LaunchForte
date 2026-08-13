# The PM playbook — what Seth does, and what any chat must tell him

Read [`START-HERE.md`](./START-HERE.md) first.

This exists because the operating loop kept living in one conversation. Seth asked the
right question — *"is the answer to come back to this chat and tell you?"* — and the
answer must not depend on which chat he opens. It is written here so every session
gives him the same answer.

---

## The loop

1. A card runs. A report email arrives.
2. He reads the top of it: **At a glance** (what passed, what failed) and
   **What to do next** (which of three situations this is).
3. He does the one thing that situation calls for.
4. Repeat.

That is the whole job. He is the PM: he decides, signs off, and unblocks. He does not
write the work and he does not chase the machine.

## The three situations, and only three

**1. It finished and passed.** The card's row is in `review`.
→ **Mark complete works.** Click it. That is the only state where the approve and
request-changes buttons can act, because `Process Approve` refuses any row that is not
in `review`.

**2. It stopped before finishing** — failed, refused, stuck, or out of budget. The row
is in `blocked`.
→ **The buttons cannot move it**, and clicking them does nothing visible. This needs a
**new card**. Seth tells Fortress what the report's *Did not pass* section said, and
Fortress cuts the next card from the surviving state.

**3. It is blocked on something only Seth can do** — a sign-in, a plan upgrade, a scope
call. The report carries a `SETUP NEEDED:` line or names the decision.
→ **No card can get past it.** He does the thing, then tells Fortress it is done.

## Cards are not resumed. They are re-cut.

A card is one session with one budget. There is no resume. The next card starts from
whatever survived, which the failed report states precisely.

Reading a failed report, in order:

| Question | Where the answer is |
|---|---|
| What actually exists now? | the PASS lines — a file, an id, a created object |
| What approach failed? | the FAIL lines. Re-queue the same approach and you buy the same failure twice |
| Is this mine to unblock? | a `SETUP NEEDED:` line, or a decision named in the open questions |

`re-1` is the worked example. It created the spreadsheet and its four tabs, then failed
trying to type data into the Google Sheets grid through a browser — `fill()` rejected,
paste silently lost, key-by-key too slow for the budget. The next card did not retry
typing: it took the spreadsheet id as given and wrote the same data **through the Sheets
API**, which is how the client's real system would do it anyway. Cost of the lesson:
$4.46 and one card.

## What Seth never has to do

- Fix a runner error. If cards are failing at setup, that is a Fortress problem to
  report and fix, not a thing to click through.
- Guess whether a report is telling the truth. If a report and the tool disagree,
  the tool wins and the disagreement is a defect worth naming.
- Enter a password, start a trial, accept terms or upgrade a plan **because a card asked
  him to**. Those are his decisions on his own initiative. A card may only surface them.

## What any chat owes him

When he asks "what do I do", answer in his terms, not the system's: which of the three
situations this is, and the single next action. Not a status dump.

When he reports a stuck loop — a button that does nothing, an email that repeats, a
board that will not update — treat it as a defect in the reporting layer until proven
otherwise. Every failure on Aug 12–13 was in that layer, not in the building.
