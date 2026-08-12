# Client handoff — conversation Desktop to Fortress

Read [`START-HERE.md`](./START-HERE.md) first.

A project never starts in a Fortress chat. It starts as a client conversation on the
`seth@launchforte.com` Desktop. That chat holds the raw material — the Upwork thread,
the call transcript, the screenshots, everything the client said verbatim. Fortress
should never see all of that, and does not need to.

What crosses the gap is one paste, in the format below. It is written by the
conversation Desktop, reviewed by Seth, and pasted into a fresh Fortress chat as the
first message. Everything Fortress does downstream is derived from it.

---

## The paste

```
FORTRESS HANDOFF

CLIENT
  slug:            <lowercase-hyphenated, stable forever, e.g. top-shelf-logic>
  name:            <how Seth refers to them>
  contact route:   <upwork | email | both>  (Seth's channel — Fortress never uses it)

ENGAGEMENT
  id:              <SLUG-1, SLUG-2, ... one per signed scope>
  status:          <funded | unfunded | simulation>
  price:           <agreed total, or "audit-first $650">
  terms:           <half to start, half on delivery — or what was actually agreed>
  source posting:  <upwork job id, if there was one>

WHAT THEY ASKED FOR
  <the client's own words, trimmed to the ask. Nouns they used, not ours.>

WHAT WE AGREED TO BUILD
  <the scope as Seth signed it off. One line per deliverable.
   This is the contract. Fortress does not add to it or price it.>

THEIR ENVIRONMENT
  <every system the build reads or writes, and where it lives.
   Name the tenant/account explicitly for anything Fortress will touch.
   "Not connected yet" is a valid and important answer.>

CREDENTIALS AND ACCESS
  <what is already signed in on the runner's Chrome profile.
   what Seth still has to sign in to.
   what Fortress must NEVER touch.>

CONSTRAINTS FOR THIS JOB
  <anything on top of the standing constraints — a tenant to avoid,
   a naming convention, a client who must not see a draft, a date.>

OPEN QUESTIONS
  <what the client has not answered yet. Fortress must not guess these.>

BUILD IN
  <the tenant / repo / account this work happens in.
   For anything unfunded or simulated this is ALWAYS launchforte.app.n8n.cloud
   and the launchforte repo, with sample data only.>
```

Any section that is genuinely empty says `none`. A section that is missing entirely
means the handoff is incomplete — Fortress says so and stops rather than filling it in.

---

## What Fortress does with it

In this order, reporting back after step 4:

1. **`clients` row** — `slug`, `name`. If the slug already exists, reuse it; never
   create a second row for the same client.
2. **`engagements` row** — `id`, client slug, scope, price, funded flag.
3. **Cards.** One `build_queue` row per deliverable in WHAT WE AGREED TO BUILD, plus
   a run card for every tool-shaped deliverable (see below). Each card gets:
   - `job_class` from the closed set: `client_ui`, `doc_update`, `export`,
     `generator`, `site_pass`
   - `autonomy` — `green` unless the card touches a client's production system,
     which is `red` and gates on Seth
   - `criteria` written as observable facts, naming a file path wherever one exists,
     so a check card is auto-queued
   - `engagement` set to the engagement id
   - `prompt` opening with the instance confirmation and closing with the
     sample-data rule
4. **Report to Seth:** engagement id, the card list with job ids, and the OPEN
   QUESTIONS restated. Nothing is invented to close a gap.

**Every tool-shaped deliverable gets three cards, not one:** build it, check it, run
it. The build card writes the thing. The check card reads it and returns a verdict.
The run card executes it against sample data and pastes the actual output. A build and
a check can both pass on a workflow that is broken — that is exactly what happened on
`tsl-1`, where reading found nothing and running found two defects. The run recipe is
in `START-HERE.md` section 5.

---

## What never crosses the gap

- The client's verbatim messages. Fortress gets the agreed scope, not the thread.
- Real client data of any kind. Sample data only, invented names, `@example.com`.
- Anything that would let a runner contact the client. Fortress never talks to clients.
- Credentials. Access is a signed-in Chrome profile, never a value pasted into a chat.

---

## Closing an engagement

When the last card on an engagement is `done` and its check has returned
`VERDICT: PASS`, Fortress writes a close-out to `docs/fortress/engagements/<id>.md`:
what was built, where it lives, what was verified by running it, and what was left
open. That file is what the next chat reads if the client comes back six months later.
