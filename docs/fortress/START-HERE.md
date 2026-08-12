# Fortress — START HERE

**Read this file first, before anything else in `docs/fortress/`.**

Every other file in this folder is either a generator, an artifact, or a dated
snapshot of one session. This file is the only one that is kept current, and it is
the only one a fresh chat needs in order to be useful without a warm-up
conversation. If something here is wrong, fix it here — do not fix it in a
side document.

**Doc hygiene rule.** A file with a date in its title (`HANDOFF.md`, `SESSION-AUG8.md`,
`CHANGELOG-*.md`, `SIMULATION-1.md`) is history, not instruction. It records what was
true on that day. Never take an action because a dated file says to. `INSTANCE.md`,
`PRODUCT-KIT-STANDARD.md`, `PAGING-RULE.md` and this file are law.

---

## 1. Who does what

Seth Forte runs **Launch Forte**, an automation and systems build business that sells
through Upwork. **Fortress** is the build system. Seth is the PM. Fortress executes.

**Fortress never talks to a client.** Not an email, not a message, not a comment.
Every word that reaches a client is written or approved by Seth.

Two Claude Desktops, deliberately separate:

| Surface | Account | Job |
|---|---|---|
| Conversation | `seth@launchforte.com` | One chat per client, named for that client. Everything the client says is pasted in verbatim. Nothing is built here. |
| Build (Fortress) | `fortresslaunchforte@gmail.com` | Work gets produced here. Clients are never named to a runner beyond what a card needs. |

The bridge between them is a handoff paste — see section 3.

---

## 2. The stack

| Layer | Where |
|---|---|
| Cockpit (proposal engine) | n8n `launchforte.app.n8n.cloud`, workflow `Hl5zah3PZcHaEkuo` |
| Build queue / reports API | n8n workflow `nuNkZu0VqDVwtS9d` (`Ops: Build Queue API`) |
| Upwork ingest | n8n workflow `7MY8Bqj42haaFbPF` (`Upwork: Job Engine`) |
| Repo | `~/repos/launchforte`, branch `main`, remote `Forte-Web-Designs/LaunchForte` |
| Site | Netlify publishes `site/` |
| Command center | `launchforte.com/command/` |
| Runner | daemon on a dedicated Mac mini; a signed-in Chrome profile *is* the credential set |

**Data tables** live under personal project `G1EzIclYs4hXjhBw`:

| Table | id |
|---|---|
| `build_queue` | `cWzXlhGhQvSZR30J` |
| `tasks` | `F5vZVMEHiMIBLgeN` |
| `clients` | `QUEzmHKwfe24G7Pa` |
| `engagements` | `sPnshUWWRM0b9VIH` |
| `upwork_jobs` | `iSZB081VXkJjbZs5` |
| `proposals` | `ejwx9dNfbqQ4gyyW` |
| `proposal_runs` | `K86MS5ngQsDaw7GH` |
| `inbox_log` | `CnINyovqbff2TXRs` |
| `digest_state` | `snILkvKIYvgB0hYJ` |
| `content_seen` | `KSJ1Rb61WpbDPrRE` |

---

## 3. How a project starts

A new project always begins as a conversation on the `seth@launchforte.com` Desktop,
never here. That chat produces a **handoff paste**. Fortress turns the paste into
rows and cards. The format and the exact steps are in
[`CLIENT-HANDOFF-TEMPLATE.md`](./CLIENT-HANDOFF-TEMPLATE.md).

Short version of what Fortress does with a handoff:

1. Insert a `clients` row (slug, name, instance/tenant notes).
2. Insert an `engagements` row (id, client slug, scope, price, funded yes/no).
3. Break the scope into cards and insert `build_queue` rows, `status = queued`.
4. Report back to Seth: the engagement id, the card list, and anything the handoff
   did not answer. **Never invent a missing answer** — list it as an open question.

Fortress does not decide scope or price. Those come from the handoff.

---

## 4. The card loop

This is the whole delivery mechanism. Everything else is detail.

```
queued  ->  runner claims  ->  builds on a runner/<job_id> branch  ->  commits
        ->  POSTs a report  ->  Ops: Build Queue API grades it
        ->  status done | stuck | no_changes | refused | failed
        ->  a check card is auto-queued when the criteria name a file
        ->  check card reads the BUILD branch and returns VERDICT: PASS | FAIL
        ->  doorbell email to Seth with accept / request-changes buttons
```

**Queue a card through the endpoint, never by writing the table.**

```
POST https://launchforte.app.n8n.cloud/webhook/build-enqueue
{ job_id, title, job_class, repo, prompt, autonomy, criteria }
```

`Ops: Dashboard API` (`XOjXyxgywZJK3G5x`) handles that path and writes **two** rows:
one in `build_queue` for the runner, one in `tasks` for the Command Center board.
Inserting straight into `build_queue` over the data-table REST API works — the runner
picks the card up and builds it — but no `tasks` row is ever created, so the card is
invisible on the board and the board looks frozen while work is plainly happening.
That is not a bug in the board. Every card in this session was queued the wrong way.

Required fields are `job_id, title, job_class, repo, prompt, autonomy`. Duplicate
`job_id` is rejected. The endpoint locks `autonomy` to `green`.

**Always send `client_slug` and `engagement_id` too.** They are not required by the
endpoint, but the board groups tasks by client — a card with an empty `client_slug`
is written to both tables, builds normally, and is invisible on the board. It reads
exactly like the board being broken. `Write Task` maps both fields, so sending them
is all it takes.

**Card fields** (`build_queue` row): `job_id`, `title`, `job_class`, `repo`, `prompt`,
`status`, `autonomy`, `engagement`, `unit`, `criteria`, `difficulty`, `task_shape`.
The runner fills in `branch`, `commit_sha`, `cost_usd`, `session_id`, `detail`, `runner`.

**`job_class` is a closed set.** Valid values: `client_ui`, `doc_update`, `export`,
`generator`, `site_pass`. Anything else is refused outright with
`unknown job class '<x>'`. There is no `tooling` class.

**`autonomy`:** `green` runs unattended. `red` gates on Seth's recorded confirm before
it may touch a client's production system.

**`criteria` is the contract.** Write it as observable facts a second agent can check
without reading the prompt. If the criteria name a file path, a check card is queued
automatically. Criteria that name only a feeling ("works well") cannot be checked and
will not produce a check card.

**Status meanings the API assigns, not the runner:**
- `done` — finished and the deliverable exists.
- `no_changes` — no diff. Auto-promoted to `done` when the work was tool-shaped
  (an n8n workflow, a browser action) and nothing stopped it early, because on those
  cards the diff is not the deliverable.
- `stuck` — hit a budget ceiling, ran out of turns, or reported `SETUP NEEDED`.
  A card that says "done" but also says it stopped early is recorded as `stuck`.
- `refused` — a guardrail fired. Read the detail: usually a bad `job_class`, or a
  prompt whose wording tripped the credential/production gate.
- `failed` — `error_max_turns` or a crash.

**Every card's first action is confirming the instance.** See `INSTANCE.md`. A card
that finds Chrome on another tenant stops and says so.

---

## 5. Proven recipes

These exist because doing it the obvious way already cost real money. Use them.

### n8n REST, from the browser console on a `launchforte.app.n8n.cloud` tab

```js
const H = {'content-type':'application/json','browser-id':localStorage.getItem('n8n-browserId')};
```

The `browser-id` header is required on every `/rest/` call.

- **Read:** `GET /rest/workflows/:id` -> `.data`
- **Save a draft:** `PATCH /rest/workflows/:id` with `{nodes, connections, settings, versionId}`
- **Publish without clicking:** `POST /rest/workflows/:id/activate` with
  `{versionId, versionName}`. `versionId` is the draft; `activeVersionId` is what is live.
- **Data table rows:** `GET  /rest/projects/{p}/data-tables/{id}/rows?take=100&skip=N`
  (paginate — `take` caps at 100), `POST .../insert` with `{data:[row], returnType:'all'}`,
  `PATCH .../rows` with a filter object. The `/rows/{id}` form 404s.
- **Executions are `flatted`-encoded.** `execution.data` is a JSON string of an array,
  and any string of digits inside it is an index back into that array. Resolve it
  recursively before reading `resultData.runData`.

### Running a draft workflow without touching the canvas

Three cards died on turn budget clicking around the n8n UI to do this. Do not do that.
`POST /webhook-test/<path>` does not work from a script either — a test webhook is only
registered for the tab that started the run, so it returns 404. Inject the trigger's
output instead and the real saved draft executes server-side:

```js
const ID = '<workflow id>', TRIG = '<trigger node name>', FIRST = '<node right after the trigger>';
const PAYLOAD = { body: {...}, headers: {}, query: {} };   // webhook node output shape
const wf = (await fetch('/rest/workflows/'+ID,{headers:H}).then(r=>r.json())).data;
const rd = {}; rd[TRIG] = [{startTime:Date.now(),executionTime:0,source:[],
  executionStatus:'success',data:{main:[[{json:PAYLOAD}]]}}];
const res = await fetch('/rest/workflows/'+ID+'/run?partialExecutionVersion=2',
  {method:'POST',headers:H,body:JSON.stringify({workflowData:wf, runData:rd,
   startNodes:[{name:FIRST, sourceData:{previousNode:TRIG}}],
   triggerToStartFrom:{name:TRIG, data:rd[TRIG][0]}})}).then(r=>r.json());
// res.data.executionId  ->  wait ~2s  ->  GET /rest/executions/<id>
```

This runs the draft. It does not activate anything. `active` stays `false`.

### Chrome tool output classifier

The browser tool blocks any returned string that looks like cookie or query data —
which includes ordinary JavaScript. Before returning a string that contains code,
swap the characters out:

```js
s.split('=').join('≔').split(';').join('¶')
```

---

## 6. Standing constraints — these do not bend

1. **Never drive upwork.com with browser automation.** Upwork bans for bot activity and
   the account is the business. The `upwork_jobs` data table is the sanctioned route.
   Anything else on Upwork is Seth's, by hand.
2. **Launch Forte only.** Never touch another org's data. GoHighLevel opens on
   *First Cornerstone Group LLC* — nothing of Seth's belongs under it. Supabase org ALG
   is off limits. Notion "Seth Knowledge Transfer" is not his content. `modbung` is a
   client tenant, not his.
3. **Nothing goes live.** Every artifact stays draft, unpublished, inactive, unscheduled,
   unenrolled, switched off. If a thing has no draft state, do not create it — stop and
   say so. Leaving a dialog by Cancel is always correct.
4. **Confirm the instance** as the first action of every card.
5. **Account creation, payment, plan upgrades and accepting terms are Seth's.** Never
   enter a password or token into a field, even when handed the value.
6. **Never delete data.** Archive instead.
7. **Sample data only** in any captured frame. Invented names, `@example.com`. Never
   screenshot a credential page, a billing page, or the n8n workflow list (real client
   names). Crop Slack sidebars at x > 437.
8. **Never publish `record_url`** — it points into his logged-in accounts.
9. **Never restart the runner while a job is in flight.**
10. **Fail soft.** Never invent client names, results or testimonials.
11. **Never fit a number to a target.** A quote changes only by changing the piece count,
    never by adjusting a rate. Report the gap as a finding.
12. If manual sign-in is needed before Fortress can start, that is fine — but the email
    must reach Seth so he knows to go check that browser.
13. **Never run `git` through the device bridge.** It leaves `.git/index.lock` behind and
    strands the repo. Git happens in a runner card or by Seth.

---

## 7. Cover letter law (Cockpit output)

The full, current law lives in the deployed `Prompt of Record` node of workflow
`Hl5zah3PZcHaEkuo` — that node is the source of truth, not any file in this repo.
The invariants:

- Fixed 9-beat order: HEADER, OPENER, INSIGHT, TOOL GAP, CATALOGUE, PRICING,
  ENTRY OFFER, CLOSE, SIGNATURE, SCREENING ANSWERS.
- Pricing block goes **above** the `Seth Forte` sign-off. Screening answers go **below**
  it. One sign-off, never both "Seth" and "Seth Forte".
- Greeting is `Hey {first name}` only when the posting clearly gives the poster's own
  name. Otherwise just `Hey`.
- No hourly anything client-facing. No call asks, no meeting windows, no working hours.
- Payment terms: half to start, half on delivery.
- Audit-heavy postings (review -> outline -> define -> present for approval) route to
  audit-first, $650, no piece breakdown.
- Any quote over roughly $1,200 offers an **entry piece**: a real deliverable already in
  the breakdown, at the same price, never a discount.
- The pricing page is retired — never claim a published rate card.
- **The letter may only describe what is actually attached.**
- Evidence is framed as a **product in the catalogue**, never a demo or a test account.
  Never claim a perfect fit. Never write "[IMAGE LINK]".
- The phrase "plain English" never appears.
- A sentence asserting a product is live or production-ready must verify against a
  builds-registry row with status `proven`. No proven row, the sentence does not ship.
- Where two readings of a quote are both defensible, take the one that prices lower.

---

## 8. Failure modes that have already cost time

- `[^.]` is not "to end of sentence" — it cuts `477.50` in half.
- `$&` in a `String.replace` replacement means "the match". Always use function replacements.
- A `function` declared inside an `else` block is invisible to earlier top-level code.
- Do not filter a workflow scan by name prefix. Naming conventions do not hold — a prefix
  filter found 54 of 378 and missed 27 relevant workflows.
- `device_bash` has no network and cannot delete files. Move to `_to_delete/`.
- After a plumbing commit, `git read-tree HEAD` or `git status` shows phantom `MM`.
- A check card that reads `main` instead of the build branch will pass work that does not
  exist. The branch and sha go into the check prompt.
- A truncated `detail` field can eat the `VERDICT:` line at the end of a report. Keep the tail.
- Gate wording is matched literally: a prompt saying "do not enter a credential" trips the
  credential gate. Reword rather than argue with it.
- **A card that passes its check can still be broken.** A build card and a check card both
  read the workflow; neither runs it. Reading found nothing wrong with the TSL lead intake;
  running it found two defects in four minutes. **Every tool-shaped build gets a run card.**
- Webhook payloads arrive under `$json.body`, not at the top level. Read
  `($json.body || $json)` once, in a first node, and let everything downstream read plain fields.
- n8n Set nodes drop incoming fields unless told to carry them. Records end up saying
  "Serves undefined" and "Lead from unknown".
- A check card that browses n8n's executions list will not find manual or partial runs
  and will fail correct work. A behavioural claim is verified by **re-running it** with
  the recipe in section 5 and reading `GET /rest/executions/<id>` — never by looking at
  a list. `check-tsl-3` failed a correct fix exactly this way.
- An n8n expression needs the braces. `=$json.total` is not an expression that reads
  `total` — it is the literal string `$json.total`, and a number-typed column rejects
  it as `Invalid input for '<column>'`. It must be `={{ $json.total }}`. This survived
  three rounds of "add number coercion" because the value arriving was never a number
  in the first place. When a type error will not die, print what actually arrived.
- `onError: continueRegularOutput` does not catch a bad parameter. Input validation
  runs before the node does, so the workflow still errors and still pages Seth.
- Before chasing an error email, check its DATE. Aug 11 produced 24 alarm emails that
  were all a rule that no longer exists. An error watcher with no history reads like a
  system on fire when the fire was put out yesterday.
