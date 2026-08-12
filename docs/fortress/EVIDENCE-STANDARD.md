# Evidence standard — what "done" has to prove

Read [`START-HERE.md`](./START-HERE.md) first.

A card is not done because it says so. On Aug 12 a build card and its check card both
passed a workflow that would have held every lead in production, and a HubSpot build
reported itself complete with three defects in it. Every one was found by running the
thing. None was found by reading a report.

So: **a report that does not show its work is not a pass, it is unverified**, and the
Build Queue API now downgrades it to `stuck` rather than closing the card.

---

## Every build card ends with this block

```
EVIDENCE
- "<acceptance criterion, quoted from the card>" — PASS — <the artifact that proves it>
- "<next criterion>" — PASS — <artifact>
- "<criterion you could not satisfy>" — FAIL — <what is missing and why>

SCREENSHOTS
- docs/proof/<job_id>-<what-it-shows>.png — <one line on what a reader should see in it>
```

An artifact is a thing someone else can open, not a sentence. In order of preference:

| Claim | What proves it |
|---|---|
| A file exists | the path **and** the commit sha that added it |
| A workflow is a draft | `active: false` read back from `GET /rest/workflows/:id` after the last edit |
| It behaves correctly | the **execution id**, plus the literal values that execution returned |
| A record was written | the object id the API returned, and the field values on it |
| A screen looks right | a frame committed under `docs/proof/`, named in the report |

"Verified", "confirmed", "tested successfully" are not artifacts. Neither is a
description of what the output looked like. Paste the values.

## Screenshots

Required on every `client_ui`, `site_pass` and `generator` card — anything with a
surface a human would look at. Commit to `docs/proof/<job_id>-<what>.png`.

Sample data only in the frame. Never capture a sign-in screen, a billing screen, or
the n8n workflow list — that list carries real client names. Crop Slack sidebars at
x > 437.

A proof frame committed to an unpushed runner branch is invisible to Seth. Name the
exact path in the report so he can pull it out in one command:

```bash
git show <branch>:docs/proof/<file>.png > /tmp/proof.png && open /tmp/proof.png
```

## What a check card owes

A check card verifies behaviour by **producing** behaviour, not by reading. Re-run the
thing with the recipe in `RUN-A-WORKFLOW.md`, read `GET /rest/executions/<id>`, and
quote the actual values next to the expected ones. An empty executions list is not
evidence of anything — manual and partial runs do not reliably appear there, and a
checker that trusts that list will fail good work and pass bad work with equal
confidence. `check-tsl-3` failed a correct fix exactly this way.

The verdict line goes at the very end: `VERDICT: PASS` or `VERDICT: FAIL`.

## Why the cap mattered

`detail` was stored as 900 characters. The reviewer graded that slice, so a report that
proved everything got rejected for proving nothing — the evidence was cut out of the
middle before anyone read it. The column holds at least 8,400 characters; the cap is
now 8,000. If a report is ever cut again, that is a bug, not a formatting choice.
