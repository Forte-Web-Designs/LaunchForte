# TRELLO CARD WRITER

**Paste this whole file into any chat, along with the client detail, and that chat can create and
update Trello cards on its own. It does not need another chat to do it. Every call it needs is in
here.**

Written Aug 14 2026. Everything below is verified against the live system on that date.

---

## 0. What this is for

Launch Forte runs on Trello. The board is the record of what is happening. Google Drive holds the
long form client documents, which are written *from* the cards, never the other way round.

There is one board per client. A card is one piece of work with a defined finish. Nine n8n
workflows read and write those boards on a schedule. Two email digests are built from them.

You do not need to understand any of that. You need to write a correctly shaped block and POST it
to one endpoint. The endpoint does the routing, the field writing, the checklist, the estimate and
the placement.

---

## 1. The one call that does everything

```
POST https://launchforte.app.n8n.cloud/webhook/trello-intake
Content-Type: application/json

{ "block": "CARD\nclient: ...\n..." }
```

The value of `block` is the entire card block as plain text, including the word `CARD` on the
first line. Newlines are real newlines. That is the whole API.

It responds with JSON that tells you exactly what happened:

```json
{
  "ok": true,
  "ref": "modern-bungalow-a3f9x2",
  "action": "created",
  "card": "Correct the ten items left reading high after the switchover",
  "url": "https://trello.com/c/xxxxxxxx",
  "board": "Modern Bungalow",
  "routed_ok": true,
  "list": "Ready",
  "list_note": "placed by the gate",
  "complete": true,
  "gaps": [],
  "fields_written": ["Client or company", "Initiative", "..."],
  "fields_failed": [],
  "fields_unresolved": [],
  "criteria_added": 7,
  "unknowns": ["..."]
}
```

**Read the response. Do not assume it worked.** The three fields that matter:

- `complete: false` with a populated `gaps` array means the card was created in **Needs detail**
  and cannot be worked. Fix the named gaps and send the block again.
- `fields_unresolved` names any field that could not be written and says why. Most often a number
  field that got prose.
- `routed_ok: false` means the client name did not match a board and the card landed on TRIAGE.

**Sending the same block twice is safe.** Matching is by `ref`, and by exact title as a fallback.
A second send updates the existing card in place rather than making a duplicate.

### If the POST returns HTTP 500

Two transient 500s were seen on large blocks containing raw email addresses. If it happens,
rewrite `someone@example.com` as `someone at example.com` and resend. The card reads the same and
the block goes through. Same for raw `https://` URLs inside criteria — describe the endpoint in
words instead. This is a workaround, not a rule; try the block as written first.

---

## 2. The card block

```
CARD
client:         Modern Bungalow
initiative:     Xero inventory flow fix
phase:          Post launch
milestone:      Switch on verification
priority:       high
cadence:        daily
lane:           red
piece:          risk
quoted:         within the $900 fixed inventory fix, already funded
tools:          Shopify, n8n
client-visible: yes

title:          Correct the ten items left reading high after the switchover
intent-client:  Fix the small number of items whose counts read high because they shipped before
                the last piece was switched on.
intent-build:   Zero out the ten SKUs carrying a one time overstatement from the transition
                window, and confirm the corrected values hold.
context:        [everything a person who has never seen this needs, in prose]
access:         [what logins or grants exist, who holds them, what is written to]
where-repo:     NONE
where-path:     NONE
where-branch:   NONE
where-account:  Shopify store modern-bungalow-inc, inventory location 29448837
where-env:      production
where-output:   Shopify on hand quantities for the ten named SKUs
where-evidence: Before and after on hand values per SKU
criteria:
- One checkable step per line.
- A wrapped line is joined to the bullet above it, so you can format for width freely.
client-line:    Sending over the ten items that read high from the switchover.
unknown:
- One open question per line, phrased as the question it actually is.
```

### Header fields

| Field | Required | Notes |
|---|---|---|
| `client` | yes | Must match a board name. See §6. |
| `initiative` | yes | The project this card belongs to. |
| `phase` | yes | Free text. Use the client's own words — `Phase 2`, `Discovery`, `Post launch`. |
| `milestone` | yes | Free text. |
| `priority` | yes | `high` / `normal` / `low` |
| `cadence` | yes | `daily` / `every other day` / `weekly` / `paused` / `on change` |
| `lane` | yes | `green` / `yellow` / `red` |
| `piece` | yes | `config` / `connection` / `judged` / `surface` / `risk` / `follow-up` |
| `quoted` | yes* | Prose is fine. Exempt for `follow-up`. |
| `tools` | yes | Comma separated. |
| `client-visible` | yes | `yes` / `no` |
| `target-date` | **no** | See §4. Only when Seth named a date. |
| `forecast-date` | no | Your own estimate of when it lands. |
| `chase-sent` | follow-up only | Date of the last thing sent. Required if `piece: follow-up`. |
| `chase-every` | no | Business days between chases. Defaults to 5. |
| `ref` | no | Generated for you. Only set it to force a match. |
| `seth-minutes` | **no. Never set this.** | See §3. |

### Body sections

All of `intent-client`, `intent-build`, `context`, `access`, `where-*`, `where-evidence`,
`client-line` are required and must each carry more than three characters. `criteria` must have at
least one entry, and every entry must be at least eight characters.

`intent-client` may be the literal word `NONE` on an internal card. Nothing else may be blank.

**A secret never appears on a card.** Name the location of the credential, never the credential.
"The DebtWave bearer token, stored inside step 3 of the Zap" is right. The token itself is not.

---

## 3. The estimate is not yours to ask for, and not Seth's to fill

**Never put `seth-minutes` in a block. Never ask Seth how long something takes.**

If the field is absent, the system prices the card off its own contents and writes
`Estimate by: Fortress, unconfirmed` on it. The rates live in the n8n data table
`seth_minute_rates` and the estimate is built from:

- a baseline for the piece kind
- an addition for the lane
- an addition per criterion that names Seth by name
- an addition per criterion that hands an activation decision back
- an addition per criterion that waits on a third party
- an addition per open question, up to three
- an addition when the card runs to nine or more criteria
- capped at 90 minutes

It counts confirmation steps. Seth prices build scale. Measured against his own eight Kevin Daleen
cards the totals matched exactly, 180 against 180, but per card the error ran plus or minus 20
minutes. **Treat it as a floor, not a forecast.** It exists so a card is never blank in the
capacity line, because a blank reads as zero and makes the day look empty.

Seth can overwrite any estimate on the card itself. The field then reads `Estimate by: Seth` and
nothing overwrites it again.

**What this means for how you write a card:** the size of a card is set by how many criteria it
carries, so keep cards small enough to finish and large enough to matter. Milestone sized, not
task sized. Six to ten criteria is the healthy range. If you are writing fifteen, it is two cards.

### A wait is never a criterion. It is its own card.

This is the rule that matters most and it was learned the hard way.

A criterion like *"Confirm with Seth that Kevin has told the crew to stop building costing sheets
by hand"* is not a step in the work. It is a **wait on another human**, and burying it inside a
build card is what let three cards sit in Ready with dates on them while none of them could
actually start. The completeness gate proved they were fully specified. Nothing proved they were
startable.

So: **if a step depends on somebody outside answering, it comes out and becomes its own card**,
written as `piece: follow-up` with a `chase-kind`, so the timer chases it and the build card is
honestly blocked behind it rather than pretending to be ready.

Signs a line should be its own card rather than a criterion:

- it starts with *wait for*, *confirm with*, *ask*, *chase*, *once they*
- it contains *has told*, *has confirmed*, *has replied*, *has approved*, *has signed off*
- it names a person outside Launch Forte who has to do something first

One card per actionable thing. If one email covers two waits for the same client, that is one
chase card naming both — not two cards and not a line inside a build card.

The digest enforces this from the other side: it reads the first unticked step of every card in
Ready, and if that step reads as a wait rather than work, it pulls the card out of TODAY, TOMORROW
and the week and lists it under YOUR MOVE as *cannot start yet*.

---

## 4. Dates

`target-date` is a **commitment**, and only Seth makes commitments. Set it only when he has said a
date out loud, in his own words, and quote where it came from in `context`.

`forecast-date` is your read on when it will land. Set that freely.

A proposal or a quote that has gone out gets a `forecast-date` and no `target-date`. That was
ruled explicitly.

---

## 5. Follow-ups: proposals, pricing, anything waiting on a reply

A card that is "we sent something and are waiting to hear back" is not build work and must not
spend capacity. It gets `piece: follow-up`.

```
CARD
client:        Effective Students
initiative:    Audit and rebuild
phase:         Proposal
milestone:     Audit acceptance
priority:      normal
cadence:       weekly
lane:          green
piece:         follow-up
chase-sent:    2026-08-12
chase-every:   5
tools:         Upwork
client-visible: yes

title:         Chase the Effective Students audit contract until Rachael answers either way
...
```

**What the system then does on its own:**

- Estimates it at **5 minutes flat**, regardless of criteria count.
- **Leaves it out of the capacity line entirely** — today's line, the week ahead total, the free
  day maths and the at risk run all skip it. A day full of chases is not a full day of work.
- Puts it in its own **Follow-ups** block in the morning and evening digests, split into *Send
  today*, *On the clock*, and *Three chases spent, your call now*.
- Runs `Ops: Follow Up Timer` every weekday at 7:45am Chicago, which computes
  `Chase next = Chase sent + Chase every business days`, writes it to the card, and when it comes
  due moves the card to **Ready** and comments on it.

**The loop, once it is running:**

1. Card sits in **Blocked on client** with a `Chase next` date.
2. On that date the timer moves it to **Ready** and comments that chase N of 3 is due.
3. Seth sends the chase and drags the card to **Done**.
4. The card-event webhook sees that, increments `Chase count`, restamps `Chase sent` to today,
   recomputes `Chase next`, and puts the card back in **Blocked on client**.
5. On the third chase it stops. The timer is cleared, the card parks in **Blocked on client**, and
   it comments that three messages on a rhythm have not produced an answer so a fourth will not
   either — change the channel, call, or close it out.

If the client replies before the timer fires, Seth moves the card out of Blocked himself and it
stops asking.

`chase-every` defaults to 5 business days. Set it explicitly when the situation says otherwise —
the Another Source card runs at 4 because Seth's own note said call by Aug 19 against a send date
of Aug 13.

**Fields, if you ever need to read or set them directly:** `Chase sent` (date), `Chase every`
(number), `Chase count` (number), `Chase next` (date, written by the timer, do not set it by hand).

---

## 6. Boards and routing

The `client` field resolves the board by name, case and punctuation insensitive. An unrecognised
client goes to **TRIAGE - Unrouted Cards** in Needs detail rather than silently creating a board.

| Client | Board id |
|---|---|
| Another Source | `6a7fceaaa9cab629b17821e5` |
| Effective Students | `6a7fd90340692b41a758da96` |
| FaithWorks Financial | `6a7fcead8ec7a8250f698c42` |
| Kevin Daleen | `6a7f9dbe240236f3ba6500ed` |
| Modern Bungalow | `6a7fceaf3a536a085eaa0dfe` |
| MyElite Health Meds | `6a7fceb5f76e566618e6a54e` |
| The Josephine Collective | `6a7fceb3a8ce06f5641186b1` |
| Vanguard Academy Jiu-Jitsu | `6a7fceb1dc611a30e0777575` |
| TRIAGE - Unrouted Cards | `6a7f85c29e1cd6c0e3501408` |
| TEMPLATE - Client Board | `6a7f48c75afb77197cde25f6` |
| Launch Forte (executive) | `69cf2115a57380c935bcecc9` |

**Never write to the Launch Forte board.** It is Seth's own view of his week, organised by when,
not a Fortress queue. Fortress pulls only from client boards.

### New client, new board

```
POST https://launchforte.app.n8n.cloud/webhook/new-client
{ "client": "Their Company Name" }
```

Copies the template, creates all 25 custom fields with their dropdown options, registers the
webhook so card moves are seen, and files the board under the *Clients - active* collection.
Idempotent — running it against an existing board repairs anything missing rather than duplicating.

**Fire these one at a time.** Six at once hit Trello rate limits and two boards came out with
missing dropdown options and no webhook. Sequential is slower and correct.

### Client board lists

`Needs detail` · `Ready` · `In progress` · `Blocked on client` · `Blocked on Seth` · `In review` · `Done`

---

## 7. The gate: complete, or Needs detail

Validation runs **before** the card is created, so a card is either born complete in `Ready` or
born in `Needs detail` with the gaps named on it. It never lands in Ready half formed.

A card goes to Needs detail if any of these are true:

- any required header field is blank
- any body section is missing or under three characters
- there are no acceptance criteria, or any criterion is under eight characters
- `where` names a repo but gives no local path
- `where` names a platform (HubSpot, GoHighLevel, Trello, n8n, QuickBooks) but gives no account
  id, portal id, tenant hostname or long resource id
- `lane: red` but neither ACCESS nor WHERE says what actually gets written
- `piece: follow-up` but no `chase-sent` date

The seven MyElite Health Meds cards are sitting in Needs detail right now on
`header field missing: cadence`, which is the gate working — Seth's own source document lists
cadence as never having been set for that client. Only he can answer it.

---

## 8. Updating a card that already exists

Send the block again. That is the whole procedure.

What happens on an update:

- Matched by `ref`, falling back to an exact title match on that board.
- Title, description, labels and all custom fields are rewritten from the block.
- **The list is left alone.** If Seth moved the card to In progress, or Done, or Blocked, it stays
  there and the response says `"list_note": "left where you put it"`. The two exceptions: if the
  gate now fails it is pulled to Needs detail, and if it was parked in Needs detail and now passes
  it is released to Ready.
- The checklist is reconciled rather than rebuilt. A criterion that matches exactly is left with
  its tick intact. A stored criterion that is a strict prefix of the new one is **renamed in
  place**, keeping its tick. Anything new is added. **Nothing is ever deleted**, so if you reword
  a criterion substantially you will get both versions and should tell Seth.

---

## 9. Writing findings back to a card mid-work

For posting what you found while working, without re-sending the whole block:

```
POST https://launchforte.app.n8n.cloud/webhook/card-write
{
  "card": "<card id or short link>",
  "comment": "What you found, in full. No length limit that matters.",
  "tick": ["exact text of a criterion to mark complete"],
  "list": "In progress",
  "fields": { "Seth minutes actual": "45" }
}
```

Every field is optional. What lands on the card also syncs to that client's Google Doc, so the
client record stays complete without a second write.

**The RED lane gate.** If the card is `lane: red`, this endpoint refuses unless a comment
containing the word `CONFIRM` exists on the card, posted by a human, and newer than the last
Fortress action on that card. One CONFIRM authorises one write. The refusal message tells you
exactly what to do. Do not try to route around it.

Fortress comments identify themselves. They are prefixed `Fortress ·` so the client document can
tell them apart from Seth's own notes — every API call carries his token, so without the prefix
everything reads as him.

---

## 10. Reading the board

```
POST https://launchforte.app.n8n.cloud/webhook/board-status
{}
```

Emails Seth the current state immediately. Use it when he asks where things stand.

The two digests run themselves: **07:45** the follow-up timer, **08:00** the morning digest,
**17:30** the evening digest, weekdays, America/Chicago. They are drafted into Gmail, never sent —
Seth walks the drafts. The evening one answers tomorrow and whether a day can be kept clear.

---

## 11. Direct Trello calls, for anything the endpoints do not cover

Only reach for these when there is no endpoint. Authentication is the stored n8n credential
*Launch FOrte Trello*, so these run from inside an n8n workflow, not from a chat.

```
GET    /1/boards/{boardId}/cards/open?customFieldItems=true&fields=name,idList,shortUrl
GET    /1/boards/{boardId}/customFields
GET    /1/boards/{boardId}/lists?fields=name
PUT    /1/cards/{cardId}                          body {"idList": "..."}
PUT    /1/cards/{cardId}/customField/{fieldId}/item   body {"value":{"date":"2026-08-19T12:00:00.000Z"}}
PUT    /1/cards/{cardId}/checkItem/{itemId}       body {"name":"corrected text"}
POST   /1/cards/{cardId}/actions/comments         body {"text":"..."}
POST   /1/checklists/{checklistId}/checkItems     body {"name":"...","checked":false,"pos":"bottom"}
POST   /1/customFields                            body {"idModel":"<boardId>","modelType":"board","name":"...","type":"date","pos":"bottom"}
POST   /1/customFields/{fieldId}/options          body {"value":{"text":"..."},"pos":"bottom"}
```

Custom field value bodies by type: `{"value":{"text":"..."}}`, `{"value":{"number":"25"}}`,
`{"value":{"date":"...Z"}}`, `{"value":{"checked":"true"}}`, dropdown `{"idValue":"<optionId>"}`,
and `{"value":""}` clears a field.

### Things that have already cost a day, so do not relearn them

- **Nested JSON must go in the body, not the query.** An n8n HTTP node with
  `sendQuery + specifyQuery: json` silently drops nested objects and still returns 200. Twenty-nine
  successful calls created twenty-nine empty dropdowns. Use `sendBody + specifyBody: json`.
- **Rapid option writes race each other.** Thirty POSTs, thirty successes, nine options actually
  present. Batch at 1.6 seconds.
- **`fullResponse: true` on a GET stops n8n splitting the array**, which is how you keep a
  per board response paired with the board it came from. It also means you read `$json.body`.
- **Returning zero items from a mid chain node kills the rest of the chain** with "No item to
  return was found", and everything downstream is silently skipped. Always emit a sentinel item.
  This caused a RED lane gate to report a pass while doing nothing.
- **`executeOnce: true` limits `$input` to the first item.** Use `$('NodeName').all()`. This bug
  recurred four times.
- **Two branches feeding one node** run that node as soon as the first branch lands. Chain reads
  in series instead.
- **Copying a board does not copy custom fields and does not copy webhooks.** The provisioning
  workflow creates them explicitly. Never assume a copied board is watched.
- **Stripping non digits from a money string corrupts it.** `within M1, $1,300` became `11300`.
  Take the money token or take nothing.
- **The n8n run log is not evidence.** Every real diagnosis on this system came from reading the
  other side — Trello, Drive, Gmail, the raw flatted execution data. Runs report success while
  doing nothing. Verify against the thing you were writing to.

---

## 11b. The board cleans itself

`Ops: Auto Archive Sweep` runs weekdays at 07:30 Chicago and does two things.

**Cards.** Any card sitting in `Done` and untouched for **14 days** is archived off the board.
Trello archive is reversible and the card keeps its full history, so nothing is lost — it just
stops crowding the list. Applies to client boards and to the executive board.

**Boards.** A client board with **no open cards outside Done** and **no activity for 30 days**
moves from the *Clients - active* collection to *Clients - dormant*. The board itself is never
closed and never deleted.

That board move is gated on one interlock: **the client's Google Doc must exist** in the client
pack folder, matched on the board name. If there is no doc, the board is left exactly where it is
and the run reports why. The doc is the durable record — cards, findings, comments and payment
detail all sync into it as work happens — so the board is only allowed to go quiet once that
record is confirmed to be there.

To change the thresholds, edit `DONE_DAYS` and `DORMANT_DAYS` at the top of the `Plan` node.

## 12. Standing rules

- **Nothing goes live.** Every artefact stays draft or inactive unless Seth says otherwise.
- **Never delete.** Archive. This applies to boards, cards, workflows and lists alike.
- **A secret never appears on a card**, only the location of the session.
- **Never write to the Launch Forte executive board.**
- **Never publish a `record_url`.**
- **Account creation, payment, plan upgrades and accepting terms are Seth's**, always. Never enter
  a password or a token into a field. Never click Upgrade or start a trial. Do not buy anything.
- **Confirm the HubSpot instance (portal 51819426) as the first action of any card that touches
  HubSpot.** Another Source 6126385, FMI 14542748 and SQFI 19578256 belong to other people.
- **Launch Forte only.** Never touch another organisation's data.
- **Never drive upwork.com with browser automation.**
- During an audit: never request an admin seat or a shared password, never change anything in a
  client system, and never total findings into one headline number.

---

## 13. How to check your own work

After sending a block:

1. Read the response. `complete`, `gaps`, `fields_unresolved`, `routed_ok`, `criteria_added`.
2. If anything is off, fix the block and send it again. It is idempotent.
3. If you want to see the card as Seth will see it, open the `url` from the response.

After a batch, read the boards back rather than trusting the responses:

```
GET /1/boards/{boardId}/cards/open?customFieldItems=true&checklists=all&fields=name,idList
```

and confirm the cards are on the right board, in the right list, with estimates populated and
checklists matching what you sent. That readback has caught every real defect in this system. The
run log has caught none of them.
