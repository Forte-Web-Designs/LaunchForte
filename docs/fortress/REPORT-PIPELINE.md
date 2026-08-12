# What happens after a card finishes

Read [`START-HERE.md`](./START-HERE.md) first. The full generated map of every entry
point is [`SYSTEM-MAP.md`](./SYSTEM-MAP.md) — regenerate it with
`generators/system-map.js` before trusting any description of the plumbing, including
this one.

This page exists because the reporting path is where every failure on Aug 12 happened,
and none of it was written down.

---

## The chain, node for node

The runner POSTs its report to `POST /webhook/build-report-9f2ad4c7` on
`Ops: Build Queue API` (`nuNkZu0VqDVwtS9d`). What follows:

```
Report In
  → Build Update          grades the report, sets the status, writes the row
  → Verify Row            reads the row back — this is what the email renders from
  → Build Report Email    composes subject + html
  → Pretty Report         adds the DO THIS steps
  → Add CC Link           footer
  → Add CC Link Send Report Email
  → Shot List             finds docs/proof/*.png IN THE PUSHED COMMIT
  → Any Shots? ──no──→ Send Report Email (no proof)
       │yes
  → Fetch Shot            pulls each frame FROM GITHUB
  → Shot To JPEG
  → Make Proof PDF
  → Has Proof? ──no──→ Send Report Email (no proof)
       │yes
  → Send Report Email     attaches binary property `proof`
```

## The thing that catches everyone

**`Shot List` reads `Shape Diff`, and `Shape Diff` is built from a GitHub fetch of the
commit.** Not from the local worktree. Not from the report text. From GitHub.

So a card whose branch was never pushed has, as far as this pipeline is concerned, no
files and no screenshots. It falls through to `Send Report Email (no proof)` and Seth
gets a report with nothing attached — while the frame sits perfectly well on a local
branch nobody can see.

The same unpushed branch also defeats the reviewing agent, which verifies by looking
for the commit, and whose generated self-check tells Seth to run `git log` and expect a
sha that is not on `main`.

**Therefore: a card always pushes its own branch.** `git push origin runner/<job_id>-…`
is safe — Netlify publishes `main` only, so a branch push deploys nothing. Never tell a
card not to push. Never let a card push `main`, open a pull request, or merge; those are
Seth's, and the runner's permission set blocks a `main` push anyway.

## Status, and who assigns it

`Build Update` assigns the status, not the runner. See `START-HERE.md` for the full
table. The two that surprise people:

- `no_changes` is auto-promoted to `done` on tool-shaped work, because on an n8n build
  the diff is not the deliverable.
- `done` is downgraded to `stuck` when the report carries no `EVIDENCE` block, or when a
  `client_ui` / `site_pass` / `generator` card names no frame under `docs/proof/`.
  See [`EVIDENCE-STANDARD.md`](./EVIDENCE-STANDARD.md).

`detail` is capped at 8,000 characters and keeps the head and the tail. It was 900 for a
long time, which silently amputated the middle of every substantial report — and the
middle is where the evidence lives.

## The approve and request-changes buttons

`Process Approve` refuses anything whose row status is not exactly `review`:

```js
if (row.status !== 'review') → "already processed", change nothing
```

**Known defect, not yet fixed:** the reviewing agent sets a rejected row to `blocked`
*before* the email reaches Seth, so the Accept button it offers in that same email
cannot act. A rejection can only be overruled by editing the row directly. If Seth
clicks Mark Complete and nothing happens, this is why.

**Known defect, not yet fixed:** the rejection email includes a
`MESSAGE FOR THE CLIENT, COPY AND SEND` block on simulated, unfunded engagements with
no client on the other end. It should be gated on `funded = true`.
