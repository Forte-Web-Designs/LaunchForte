# Importing cards onto the Trello board

How work gets from a Claude Desktop conversation onto a board in a shape Fortress can start from.
Written 14 Aug 2026, proved on the first eight real client cards.

---

## 1. Add the client first

One call, and it is safe to run twice.

```
POST https://launchforte.app.n8n.cloud/webhook/new-client
{ "client": "Kevin Daleen" }
```

It copies the template board, recreates all custom fields with their dropdown options, registers
the Trello board watch, and files the board under `Clients - active`. Running it again on a client
that already exists changes nothing and says so.

**Copying a board in Trello carries lists and labels and nothing else.** No custom fields, no
webhook. That is why this exists rather than a right click and Copy.

**The board is named exactly what the client is called**, because the intake resolves the board
from the client field by name, and the Drive client record is matched on the same string. Rename a
board and you split its history. If a client name has to change, the Drive doc gets renamed in the
same breath.

Skip this and the cards still land, on the triage board in Needs detail, with the reason printed.
Nothing is lost, but it is rework.

## 2. Send the card

```
POST https://launchforte.app.n8n.cloud/webhook/trello-intake
{ "block": "<the whole CARD block, verbatim>" }
```

Optionally `"overrides": { "target_date": "", "forecast_date": "2026-08-18" }`, which is how a
proposed date lands as a forecast rather than a promise.

The block goes in exactly as written. Continuation lines, indentation, `NONE` as a real answer,
all of it survives.

```
CARD
client / initiative / phase / milestone / priority / cadence / lane /
piece / quoted / tools / target-date / seth-minutes / client-visible

title:         action first, written so the client could read it
intent-client: what the client gets, one sentence, their language
intent-build:  what the build actually does
context:       what is already true, what came before
access:        per system, login URL and session location, never a secret
where-repo / where-path / where-branch / where-account / where-env /
where-output / where-evidence
criteria:      one imperative line each, as - bullets
client-line:   one sentence for the update email
unknown:       anything the conversation could not answer, as - bullets
```

## 3. What the gate checks before anything is created

A card is either born complete in **Ready** or born in **Needs detail** with its gaps named. It
never lands in Ready half formed.

**Header must all be present:** client, initiative, phase, milestone, priority, cadence, lane,
piece, quoted, tools.

**Body must all be present and not thin:** intent, context, access, where, evidence, client line.

**At least one acceptance criterion**, each an executable step rather than a desired state.

**Two checks that are easy to fudge and are not:** a WHERE that names a repo and gives no local
path fails. A WHERE that names a platform and gives no account id, tenant hostname or long
resource id fails. A RED lane card whose ACCESS and WHERE never say what gets written fails.

## 4. Things that will bite you, learned the hard way

**Put a dollar sign on money.** `within M1, $1,300, already funded` parses to 1300. A quoted line
with no `$` and no clean number comes back as unresolved rather than being guessed at. An earlier
version stripped every non digit and turned that same line into **11300**.

**`phase` is free text** and takes `Phase 2`. **`Work stage`** is the separate plain English word
that shows up in client updates: Scoping, Ready to build, Building, Testing, Live, Maintaining.

**`cadence`** takes daily, every other day, weekly, paused, on change.

**`lane`** takes green, yellow, red. It becomes a label so the gate is visible on the card face.

**Do not send `seth-minutes` at all.** Leave the line out and the card is priced off its own
contents, marked `Estimate by: Fortress, unconfirmed`, with the arithmetic posted as a comment.
Correct the number on the card whenever you disagree and it becomes yours. Sending a number makes
it yours immediately, which is wrong when it came out of a chat rather than out of your head.

The estimate is a floor rather than a forecast. Measured against eight cards Seth priced himself
it lands within about twenty minutes either way, so it exists to stop a blank reading as zero, not
to be believed.

**`target-date` is a promise.** Anything not personally committed belongs in `forecast-date` or
under `unknown`.

## 4b. Writing the cards in the first place

`TRELLO-CARD-WRITER.md`, beside this file, is the one to paste into a chat that already holds a
client's details. It carries the block format, the gate rules, the fixed field values, the voice
rules and the granularity rules, and it tells that chat to omit `seth-minutes` and any uncommitted
target date. This file is the operator side. That one is the author side.

## 5. Resending

Send the same card again and it **updates** rather than duplicating. Matching is on a `ref`, a
client slug plus a hash of the title, minted on first send and returned in the response. Change a
title and the ref changes, so there is a second match on exact title that catches it and rewrites
the ref onto the card that already exists.

A resend does not make a second acceptance criteria checklist.

Answering a gap and resending is the intended way to move a card out of Needs detail.

## 6. What happens on its own once the card exists

Move it and the event is written to the ledger. Move it to **Done** and the `Done date` is stamped
and any unticked acceptance criteria are named in a comment. Every comment, every move to Done, In
review or either Blocked list appends to that client's Google Doc record.

The morning digest reads every open board in the workspace except TEMPLATE, TRIAGE and anything
parked in `Clients - dormant`. Nothing has to be registered with it.

## 7. Writing to a card as work happens

```
POST https://launchforte.app.n8n.cloud/webhook/card-write
{ "card": "<id or shortLink>", "note": "the finding", "evidence": ["..."],
  "tick": ["exact criterion text"], "list": "In review",
  "fields": { "Work stage": "Testing", "Forecast date": "2026-08-20" } }
```

Lists, fields and dropdown options resolve by name on that card's own board. Anything unresolved
comes back named with the valid options listed.

**A RED lane card refuses every write unless the card carries a comment containing CONFIRM**, and
a confirm already spent by an earlier Fortress action does not count twice.

## 8. The endpoints, in one place

| what | where |
|---|---|
| add a client | `POST /webhook/new-client` |
| send a card | `POST /webhook/trello-intake` |
| write to a card | `POST /webhook/card-write` |
| board status now | `POST /webhook/board-status` |
| card events in | `POST /webhook/trello-card-event` (Trello calls this, not you) |

All on `https://launchforte.app.n8n.cloud`.

## 9. The tables you can edit without touching a workflow

| table | what it holds |
|---|---|
| `capacity` | daily minutes, by default, weekday or exact date |
| `seth_minute_rates` | what each kind of involvement is worth when a card is estimated |
| `card_events` | the append only history of every board event |
| `audit_checkpoints` | the 45 point standard, one row per checkpoint |
