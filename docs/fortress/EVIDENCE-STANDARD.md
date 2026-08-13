# Evidence standard — what "done" has to prove

Read [`START-HERE.md`](./START-HERE.md) first.

A card is not done because it says so. On Aug 12 a build card and its check card both
passed a workflow that would have held every lead in production, and a HubSpot build
reported itself complete with three defects in it. Every one was found by running the
thing. None was found by reading a report.

So: **a report that does not show its work is not a pass, it is unverified**, and the
Build Queue API now downgrades it to `stuck` rather than closing the card.

---

## The report's last two sections, in this order

A report ends with **EVIDENCE, then SCREENSHOTS**. Nothing after them.

That order is the rule, and a card prompt must never say "end with an EVIDENCE block"
while also asking for a screenshots section — on Aug 12 that exact contradiction got a
correct frame rejected for putting SCREENSHOTS last, which is the only place it can go.
Say: *include an EVIDENCE block, followed by a SCREENSHOTS section, and nothing after.*

An open question or a flagged judgment call goes **inside** the EVIDENCE block as its own
line, not appended after the sections. Workers surface good ones — one cropped a personal
address out of a frame and asked whether that was over-cautious — and they must have a
home that does not break the ordering rule.

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

## Screenshots — a pack, not a frame

**One picture is almost never enough.** A single canvas shot proves a thing was drawn.
It does not prove the thing works, and it is not something Seth can send a client to
show the job is done. That is the actual purpose of the frames: a client-shareable
proof that the work is complete.

So the default is a **pack**, ordered so a stranger can follow it:

| Frame | What it proves |
|---|---|
| 1. the build | the thing exists, in the tool, in the state promised (draft/inactive) |
| 2. the run | it executed — the execution view with real output visible, not an empty canvas |
| 3. the result | what it produced, *inside the tool the client actually opens* — the CRM record, the draft, the label, the message |

Add frames when a deliverable has more surfaces than that. A workflow that writes to
three places owes a frame per place. **One frame is acceptable only when there is
genuinely one surface to photograph, and the report must say why.**

Name them so the order is obvious and a stranger can tell what they are looking at:

```
docs/proof/<job_id>-1-<what-it-shows>.png
docs/proof/<job_id>-2-<what-it-shows>.png
```

Every frame is client-shareable or it does not ship: sample data only, no account chip,
no billing or settings screen, no sign-in page, no workflow list (it carries real client
names), no other client's record anywhere in shot. Crop rather than explain.

The report names each frame and says in one line what a reader should see in it. A frame
nobody can interpret is not evidence.

## Screenshots — the rules that always apply

Required on every `client_ui`, `site_pass` and `generator` card — anything with a
surface a human would look at. Commit to `docs/proof/<job_id>-<what>.png`.

Sample data only in the frame. Never capture a sign-in screen, a billing screen, or
the n8n workflow list — that list carries real client names. Crop Slack sidebars at
x > 437.

**A card pushes its own branch. Never tell a card not to push.**

`git push origin runner/<job_id>-...` is the normal path and it is safe: Netlify
publishes `main` only, so a branch push deploys nothing. Pushing is what makes the
work checkable — the reviewing agent verifies the commit exists, Seth can open the
proof frame on GitHub, and the branch is ready for a pull request. The digest line
"Branches are pushed but not merged. Open a pull request to ship." describes the
intended flow.

On Aug 12 three cards in a row — `hs-1b`, `hs-2`, `hs-3` — were told "do not push".
All three built correctly. All three were rejected or failed, because the reviewer
was sent to look for a commit that existed nowhere it could reach, and its own
self-check instructions told Seth to run `git log` and expect a sha that is not on
`main`. `hs-3` was rejected while the same email's rationale block said the work
answered the ask. The instruction caused the rejection, not the work.

What a card must still never do: push `main`, open a pull request, or merge. Those
are Seth's. The runner's permission set blocks a `main` push anyway.

If a frame ever does sit on an unpushed branch, name the exact path so it can be
pulled out in one command:

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
