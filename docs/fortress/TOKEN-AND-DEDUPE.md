# Two changes to `Ops: Dashboard API`

**Aug 9, 2026.** Part A is yours, five minutes in the n8n UI. Part B is mine, and Part A
is what makes it possible.

---

# PART A — move the token onto the webhook

## Why

The token is currently a string constant on line 7 of the `Code in JavaScript` node. That
puts a secret inside the workflow JSON, and the practical consequence is that I can't read
any code node in that workflow any more — every attempt comes back `[BLOCKED]`. The
snapshot node, `Dupe Gate`, `Criteria Guard`, all of them. I can read node *parameters*
fine, which is how I found the dedupe bug, but I can't safely edit code I can't see.

Three things are stuck behind this:

1. the tasks-table dedupe (Part B)
2. the run epoch for **Money** — `total_cost_usd` is computed server-side over every row,
   which is why the page still says $155 with an honest label on it
3. **Reports** and **queue depth**, same reason

n8n's webhook nodes have Header Auth built in. Moving the token there puts it in the
credential store instead of the workflow body, and unauthorised requests get rejected by
n8n before a single line of your code runs — which is strictly better than a guard that
executes first and returns 401 second.

## Steps

**First, copy the current token somewhere temporary.** It's in `Ops: Dashboard API` →
`Code in JavaScript` → line 7, between the quotes. You'll paste it in step 2, and you'll
keep using the same value, so nothing you've already entered on `/command/` breaks.

1. n8n → **Credentials** → **Add credential** → search **Header Auth** → Create
   - **Name:** `Dashboard Token`
   - **Header Name:** `X-Dashboard-Token`
   - **Header Value:** the token you just copied
   - Save

2. Open **`Ops: Dashboard API`** → double-click the **`Snapshot In`** webhook node
   - **Authentication:** `Header Auth`
   - **Credential:** `Dashboard Token`
   - Close the node

3. **Save**, then **Publish**.

4. Reload `/command/`. It should still work with no re-entry — the page already sends that
   header, and the guard block is still in the code, so both checks pass. That overlap is
   deliberate: no window where the endpoint is open or the page is locked out.

Then tell me it's done and I'll take the guard block out.

## Already shipped for this

The page now treats **403 as an auth failure alongside 401**. n8n's Header Auth rejects
with 403; the guard node answers 401. Without this, flipping the switch would make a bad
token surface as a generic "cannot reach n8n" banner instead of the token form. It had to
land before you touch the webhook, so it's in this push.

---

# PART B — the dedupe fix

## What's actually wrong

`Check Dupe` runs `rowExists` against **`build_queue`, matching on `job_id`**. That is a
correct guard against replaying the *same job*. It is not a guard against writing the same
*card* twice, because nothing anywhere checks the tasks table.

So: re-run an enqueue with a fresh `job_id` and the same title, and you get another task
row. Every time. That is exactly what the data shows — one title exists **8 times**, with
8 distinct `task_id`s, 8 distinct row ids, the same client and the same engagement, all
written inside a four-hour window. Five titles duplicated, 18 rows involved.

This is the Phase 0 blocker "diagnose seeder duplication versus render join." **Seeder
duplication**, definitively — a render join would have shown one row id repeated, not eight
distinct ones.

## The current chain

```
Enqueue In → Enqueue Guard → Enqueue Guard If ─true→ Check Dupe → Dupe Gate → Dupe Gate If
                                    │                                              │
                                    └─false→ Enqueue Body                     true ─┤
                                                                                    ↓
                        Write Queue ← Write Task ← Criteria Guard ← Draft Criteria ─┘
```

## The change

Insert the tasks-table check between `Criteria Guard` and `Write Task`:

```
Criteria Guard → Task Dupe Check → Task Dupe If ─true (exists)──→ Write Queue
                                             └─false (new card)─→ Write Task → Write Queue
```

**Node 1 — `Task Dupe Check`**, type `n8n-nodes-base.dataTable`, typeVersion 1

- Operation: **Row Exists**
- Data table: `tasks` (`F5vZVMEHiMIBLgeN`)
- Conditions:
  - `client_slug` = `={{ $('Criteria Guard').first().json.job.client_slug || '' }}`
  - `title` = `={{ $('Criteria Guard').first().json.job.title }}`

**Node 2 — `Task Dupe If`**, type `n8n-nodes-base.if`, typeVersion 2.2

- Boolean condition: `={{ $json.exists }}` **is true**
- true → `Write Queue`   (the queue row is still written; the card is not duplicated)
- false → `Write Task`

**And one rewrite that is easy to miss.** `Write Task` currently reads nine of its twelve
columns off `$json` — `task_id`, `title`, `ask_verbatim`, `acceptance_criteria`,
`client_slug`, `engagement_id`, `task_type`, `created_ts`, `updated_ts`. Once two nodes sit
between it and `Criteria Guard`, `$json` is the Row Exists output, not the job payload, and
every one of those columns silently goes empty. They all become:

```
$('Criteria Guard').first().json.…
```

`Write Queue` already uses that form for all ten of its columns, which is why it needs no
change — and is a good sign that form is the house style here.

## Verify before trusting it

The Row Exists node's output field name — I've written `$json.exists` from the node's
documented shape, not from a live run of yours. Fire one enqueue and read the actual output
before relying on the If. If the field is named something else, only that one expression
changes.

## What this deliberately does not do

It dedupes on **exact title within a client**. Phase 1 drafts 5–12 distinct cards, so no
false positives are expected, and a re-run of intake gets caught — which is the case that
produced the 8 copies. Two cards intentionally sharing a title would be blocked; the
enqueue still returns a normal response rather than an error, so that shows up as a missing
card at sign-off rather than a failure, and the fix is to give it a distinct title.

## Who does it

I can build all of it once Part A lands — it's parameters only, no code node edits, so it's
inside what I can author safely. If you'd rather not do Part A, say so and I'll write it as
a click-by-click for you instead; the spec above is complete either way.
