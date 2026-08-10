# What changed on 2026-08-10

### One day, one session. The runner, its config, the browser binding and five n8n
### workflows. Written so a Wednesday oddity is traceable to a specific change rather
### than re-derived from scratch. Every failed attempt is here too, because the
### corrections are the part worth reading.

Backups are timestamped siblings of every file touched
(`runner.py.bak.20260810145141` and so on). Every n8n change is published; each
workflow's version history holds the prior version.

---

## 1. THE BROWSER BINDING — this is the one that unlocked the day

`~/assembly-line-runner/playwright-mcp.json`

**Was:** `--isolated`, which keeps the browser profile in memory and throws it away.
Every job started in a blank browser with no cookies and no logins.

**Why it mattered:** every successful browser job to date had been on a public page.
The five `fmi-hubspot-read-*` jobs that hung to a 3000s timeout were sitting on a
login wall in an empty profile with no instruction to stop. The sign-in doctrine —
"the persisted Chrome session IS the credential" — was written down and never wired
to the runner.

**Now:** extension mode, bound to a dedicated Fortress Chrome profile, with
`PLAYWRIGHT_MCP_EXTENSION_TOKEN` set so connections need no per-job approval.

**Deliberate deviation from the capability runbook:** §5.1 prescribes `--extension`
against Seth's own Chrome. That profile carries a live GoHighLevel session for
First Cornerstone Group LLC, a former client. Binding an unattended runner to it was
not acceptable. An intermediate step used `--user-data-dir` with a dedicated profile;
extension mode replaced it once Seth wanted to watch and intervene.

**Also corrected:** the runbook's `--caps=network,storage,testing,vision,pdf,devtools`
is wrong. `--caps` accepts only `vision,pdf,devtools`. The original config was right
on that point.

**Two scripts left behind:** `use-extension-mode.sh <TOKEN>` and `use-profile-mode.sh`
switch between them in one command. `playwright-mcp.profile.json` and
`playwright-mcp.extension.json` hold each shape.

---

## 2. `runner.py`

### 2.1 The refusal gate could not tell a prohibition from an instruction

`DEFAULT_REFUSE_PATTERNS` matched the whole prompt with no notion of negation, so
`Do not publish, activate, edit or delete any other workflow` scored identically to
`Publish the client workflow`. A card was refused for a line written to constrain it.

**Added:** `refusal_hit()`, `NEGATION`, `FALSE_NEGATION`, `SENTENCE_SPLIT`. A match is
skipped only when a negation governs it in the same sentence. `do not forget to
publish` is explicitly not a negation.

**Failed attempt worth keeping:** the first split rule was `(?<=[.\n])\s*`, which
splits on *every* period — fragmenting `.env`, version numbers and URLs, and hiding
real matches in the debris. Caught by a test case (`Read the values out of .env`)
that passed before the change and failed after. Tightened to `(?<=[.!?])\s+|\n+`.

Result: 18/18 on the gate battery, 4/4 on URL and path edge cases, acceptance 30/30.

### 2.2 Branch names collided, so no retry could ever run

`branch_name()` used `slugify(job_id, 24)`. `lf-hubspot-lead-capture-b` and
`lf-hubspot-lead-capture-b2` both truncate to `lf-hubspot-lead-capture` — the
distinguishing suffix is exactly what got cut. **Every retry of any job with an id
longer than 24 characters died before it started**, on `fatal: a branch named ... already exists`.

**Added:** `slug_id()`, which keeps a 6-char hash of the full id when truncating.
`hashlib` imported.

### 2.3 HOUSE_RULES, rule 4, rewritten twice

**Was:** *"Never send email, publish, deploy, activate, or write to any live third
party system."* That forbids the exact work Fortress exists to do. Every session
carried a standing instruction not to act in any live system.

**First rewrite** made it lane-aware: may act inside a Launch Forte house account.

**Second rewrite, after Seth's correction, is the one that stands:** `NOTHING GOES
LIVE`. Work inside any system the task names, including a client's. Never make
anything take effect. Leave every artifact draft, unpublished, inactive, unscheduled
or switched off. If a thing has no draft state, do not create it — stop and say so.
Leaving a dialog by Cancel or Escape is always correct.

This is a loosening relative to the original, recorded as such.

### 2.4 SETUP NEEDED rule

Sessions now stop at a sign-in page, consent screen or 2FA prompt and emit
`SETUP NEEDED: <surface> | <url> | <what a human must do> | <phone code likely?>`.
`setup_needed()` lifts those lines to the top of the job detail so they reach the
digest instead of dying in a report.

**Measured effect:** the HubSpot wall that consumed 3000s five times now costs
**36 seconds and $0.32** and returns the exact URL and available sign-in options.

**Known cost:** it is tuned to stop early, so it produces false positives. It fired
once on HubSpot's `/myaccounts` picker, which means signed in with more than one
portal, not signed out. Filed as a known path.

### 2.5 The identity rule for screenshots

A proof shot shipped with `From: Seth Forte (seth@launchforte.com)` in the frame while
the session reported no real person was visible. Every card said "no real person's
name" and every worker read that as "no contact records."

**Added:** `WHOSE NAME IS IN THE FRAME`, a named list rather than a principle — the
signed-in user chip, From/Sender/Reply-to lines, the workspace owner, any email
address including the operator's own, profile names, notification toasts, record
lists. *"The sender is a real person just as much as the recipient is."*

### 2.6 The reach-around rule

A card set an email body by writing `innerHTML` and dispatching synthetic events. It
worked, and it verified honestly by reloading from the server — but it skips the
application's own validation and autosave, so the screen can agree while the server
does not.

**Added:** `DRIVE THE INTERFACE, DO NOT REACH AROUND IT`. Permitted only when a card
names it as allowed on a house account, and the report must say it happened and why
the normal route failed.

---

## 3. `runner.config.json`

### 3.1 The running config had drifted five days from disk

The process started 2026-08-05 16:43:57. The config was written at 17:23 — thirty-nine
minutes later. **It ran a stale config for five days and nothing surfaced it.** The
first symptom was a `doc_update` job getting no browser tools when disk said it had them.

### 3.2 Restarting would have silently removed 13 tools

The on-disk `client_ui` allow-list was *narrower* than the running one. A restart would
have dropped `browser_file_upload`, `browser_handle_dialog`, `browser_drag`/`drop`,
`browser_network_request` and every `mouse_*_xy` tool — **rungs 5 and 6 of the control
ladder**, the escape hatches for iframes and canvas editors.

**Merged** both lists before any restart. `client_ui` is now 40 tools.

### 3.3 `max_parallel` 2 → 1

Correct when every job launched a throwaway browser. Wrong the moment extension mode
made all jobs share one Chrome window: two browser jobs would drive the same tabs
against each other. Nothing had hit it yet, by luck.

---

## 4. `Proposal: Cockpit` — `Hl5zah3PZcHaEkuo`

### 4.1 Pack section 5 was empty because of schema drift, not a rendering fault

`Build Pack` read `P.sketch.flow.steps`, `P.sketch.zeroRisk`, `P.sketch.disclaimer`.
The model emits `{title, mainIdea, archetype, nodes, decisionIndex, edgeNodes, glyph,
reframe}`. All three resolved undefined, so the section printed headings over nothing.
Rewritten against the shape that actually arrives.

### 4.2 Render Sketch now records what it drew

The sketch's wording is picked per run from banks, so no two clients read the same
words and nothing recorded which words *this* client read. `__DRAWN` captures every
string drawn; `printedText` carries them into the pack verbatim.

### 4.3 CONFIRM THE INSTANCE shipped into the pack

Previously a rule in a document. A rule that only exists in a document does not run.

### 4.4 Product naming, three iterations

The letter said *"mirrors my The Reporting Layer"* — an internal catalogue name on a
sales-pipeline posting, with the buyer left to work out the connection.

1. First attempt dropped the name and led with the function. **Wrong** — loses the
   established, premium read that a named product carries.
2. Second added name plus gloss, then repeated "product in my catalogue" twice
   because the lead already said it. Caught before publishing.
3. **Stands:** the article is stripped and the possessive kept, so it reads
   *"yours closely mirrors my Reporting Layer, which handles HubSpot pipeline
   automation with workflows and nurturing."* A final sweep stops any path putting
   "The" back in front.

### 4.5 Forge paused

`Fire Forge`, `Forge Gate`, `Read Forge Queue`, `Read Builds G` disabled. Killed at
the source rather than muting the two emails, because the emails are the cheap part —
the analysis LLM call inside `Forge: Intake` runs before either of them.

### 4.6 `Price the build` rewritten — 45,873 chars to 12,946

Class floors, shape minimums, `floorUpPrice` and `__classFloor` are retired per
`HOW_TO_PRICE.md`. Five piece kinds, two prices each, systems past the first two,
cost to deliver as the only floor, and a do-not-price rule that emits no number when
no piece can be named.

**Failed attempt, caught in test before publishing:** every stem pattern was written
`/\bnurtur\b/`. **A trailing `\b` after a stem can never match the inflected word** —
`nurtur` cannot match "nurturing", `qualif` cannot match "qualification". Ten stems,
all silently dead, all producing confident low numbers. Joel's form derived $800
instead of $1,750.

**Blast radius: zero.** Verified against the workflow version history — the buggy
code was never patched in. No quote was drafted or sent from it. The old class engine
did not carry the bug either; it used `integrat\w*`, the correct form.

**The defence that should be automatic:** every extraction pattern gets a fixture
asserting it matches a real inflected example. A pattern matching nothing in its own
fixture fails the build. Same failure class as the paging rule and the field rule —
a confident wrong result that never throws.

Verified against the doc's worked examples: Joel's form **$1,750**, a single form
**$250**, a staffing role **no number**. Job 122 derives **$2,250**, which is what the
posting names; the doc's $3,150 includes stalled-deal escalation and three systems the
posting never mentions.

**Ruling recorded:** price what the posting NAMES, never what the shape implies, with
a guard line naming likely additions without pricing them.

---

## 5. `Ops: Build Queue API` — `nuNkZu0VqDVwtS9d`

### 5.1 Screenshots now attach as a PDF

`Shot List → Any Shots? → Fetch Shot → Shot To JPEG → Make Proof PDF → Send Report Email`.
Up to 12 images, fetched from the runner branch through the GitHub credential,
converted to JPEG (a PNG cannot embed in a PDF without decoding), assembled as one
page per shot.

**Broke your emails for about twenty minutes.** The Gmail node *requires* the binary
once an attachment is configured, so the no-screenshot path threw instead of sending.
Two reports were lost. **Fixed** with a twin `Send Report Email (no proof)` node and a
`Has Proof?` gate — every path now reaches an email. Classic one-sided gate: the happy
path built, the other left to fall over.

### 5.2 The inline images were pointed at a branch that does not have them

Built against `LaunchForte/main/docs/proof/...`. Those files only exist on the runner
branch, which is never merged. Every image rendered broken, which is why the filename
appeared twice — broken image alt text, then caption. Now rewritten to the real branch.
Cap raised 3 → 12.

### 5.3 A rejected job displayed a green tick

`tone` was inferred by matching words in the subject and body, neither of which carries
the verdict. **A job the verifier rejected rendered as ✅ VERIFIED.** The single most
dangerous defect of the day — it is how a rejected result reaches a client. Now reads
the verdict directly and renders ⛔ REJECTED.

### 5.4 Failed verifications sent nothing at all

`Lead: Fail Update Row` emitted zero items, so the chain stopped and no email was sent.
You only ever heard about work that succeeded. `alwaysOutputData` set.

### 5.5 WHAT WAS ASKED / WHY THIS ANSWERS IT

`Ask Prompt → Summarise Ask → Parse Ask`, written from the card's `ask_verbatim` rather
than paraphrasing the acceptance criteria. Fail-open: a missing summary never costs an
email.

### 5.6 `Shape Task Row` had `client_slug: ''` hardcoded

**No piece of work could ever attach to a client.** This is the root cause of three
separate symptoms: the Command Center board showing nothing, the 8pm update engine
having nothing to draft for six days, and per-job cost never rolling up. Now carried
from the card's `engagement` field as `client-slug` or `client-slug|engagement-id`.

### 5.7 Recording a cost destroyed commercial data

`Update Engagement Spend` wrote `work_order_version: 0, price_charged: 0,
touch_time_hours: 0, infra_cost_usd: 0, current_phase: 0` alongside the spend. **Every
cost update zeroed the price charged, the hours and the phase.** Now writes only
`api_spend_usd`.

---

## 6. `Ops: Task Watch` — `ww2RC1BLSZr0Jffi`

`Email Stuck` disabled. Twelve cards, twelve false positives, every one a job that had
already finished — the email said so itself: *"this is a reporting gap rather than a
stalled job."* The orphan reaper is untouched and still runs; only the nagging stopped.

Separately, `Ops: Build Watch` correctly caught a genuinely dead job
(`session-setup-round-2`, killed by a runner restart mid-flight). That row was cleared
by hand with the real cause written on it. That alarm stays on — it tells the truth.

---

## 7. `Ops: Update Draft Engine` — `V7jzsfGoEU2YCxbd`

Schedule moved 08:00 → 17:30 → **20:00 America/Chicago, weekdays**. Drafts are written
from the day's work and signed off at end of day, so the loop closes the same evening
rather than describing work that is already stale.

---

## 8. `Ops: Update Approval API` — `EHou1qXYVwMrBJzw`

**Reverted change, recorded because the reasoning matters.** Approve was briefly made
to hold the draft with no scheduled send. Seth's intent was the opposite: approve
means scheduled. Restored, and `Send Window Jitter` added — `Math.random() * 60`
minutes after the 08:00 trigger, so the batch lands somewhere between 8 and 9 and reads
like a person clearing their morning rather than a machine at the top of the hour.

The draft is sent by draft id, so **editing the Gmail draft before approving carries
the edits**. That is the correction path, not a feature request.

---

## 9. The blockers ledger went from 14 rows to 20

For the first time it carries UI surface classes and winning rungs, which the
capability doc flagged as missing — the certification gate had been passing off an
empty ledger.

- **15 `ui_no_session`** — closed. The `--isolated` finding, with the fix and why
  `--extension` against Seth's own Chrome was rejected.
- **16 `ui_login_hang`** — closed. The five HubSpot 3000s timeouts, cause and cure.
- **17 `dispatcher_gate`** — open. The polarity-blind gate, with the 13-case result.
- **18 `known_path`** — the n8n version-naming path, with selectors.
- **19 `known_path`** — **the Margaret wall beaten.** A real cross-origin iframe
  (`51819426.hubspotpreview-na1.com` inside `app.hubspot.com`) entered with a frame
  locator on the first attempt, no coordinates. Rung 4 wins; rung 6 was never needed.
- **20 `plan_locked`** — open. HubSpot Workflows and Campaigns locked on portal
  51819426.
- Plus `kp-hs-clickcatcher` — a click-catcher overlay inside the canvas iframe defeats
  locator clicks; rung 4 to enter, rung 6 to click.
- Plus `kp-hs-picker` — `app.hubspot.com/` redirects to an account picker when the
  login sees several portals. That means signed IN, not out.
- Plus `blk-autosave` — open, and worth reading. **Opening a HubSpot editor panel fires
  the platform's own autosave.** Under an explicit change-nothing instruction, the
  draft's timestamp still moved. A read-only guarantee cannot honestly be promised on
  that surface.

---

## 10. What was NOT changed, and why

- **The catalog price bands.** Repricing from pieces puts every product below its band —
  Booked Solid at $1,350 against $6k–$12k. A 5x gap points at a thin spec rather than a
  fivefold overprice. Bands stay published until three are hand-read.
- **The evidence matching logic.** It picked The Reporting Layer, then Stuck Deal
  Detection for a pipeline job. Choosing on substance is the hard part and it is
  working. Only the presentation was wrong.
- **239 of 250 catalog rows.** They have a one-line promise and no spec, and returned
  $0 correctly. They cannot be priced, sold or built. That is a content problem, not a
  pricing one.

---

## 11. Restarts required, in order

`launchctl kickstart -k gui/$(id -u)/com.launchforte.assembly-runner`

Everything in sections 2 and 3 needs it. **Never restart while a job is in flight** —
that is how `session-setup-round-2` died, and `fmi-hubspot-read-5` before it.
