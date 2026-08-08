# Fix notes — Aug 8, 2026

Picks up from `HANDOFF.md`. Everything here is regenerated, never hand-edited.

---

## 1. The real bug was not the one in the handoff

The handoff's hypothesis was that `Pick the evidence to attach` built a haystack
from too many payload fields, and something large and constant was drowning the
posting. Reasonable, and the hardening was worth doing — but it is not what was
happening.

I dumped `$json` as it actually exists in a real execution (run 25938). What the
node receives:

```
access_list, briefWordCount, createdAt, id, label, matchedCount, matchedProducts,
prior_art, questions_confirmed, questions_raw, referenceBuilds, referenceCount,
seen_count, shape, status, ts, updatedAt
```

**Seventeen fields, and not one of them is the job posting.** Not `jobPost`, not
`jobTitle`, not any of the twenty names the node reads. `id: 7`,
`label: "dental-expansion-probe-two-uqok"`, `ts: 2026-07-30` — this is a row
from a stored shapes table, written eleven days earlier.

`Match Product` scores the posting, then emits that table row **without carrying
`$json` through**. Everything downstream of it — the evidence node, the Prompt
of Record, pricing — sees the row instead of the job.

And the row carries `shape: "voice-agent-intake"`. The evidence node's first
line of shape resolution was `input.shape || input.build_shape || ...`, so it
took that value and skipped its own matching entirely. `match_confidence` came
back **`"given"`** on every run — meaning nothing was ever scored.

That is the whole bug. Three unrelated postings returned the same four
voice-agent-intake shots because none of them were ever read. **The matcher was
not wrong. It was never consulted.**

Confirmed across five consecutive real executions — all five previously resolved
`voice-agent-intake`, confidence `given`, four voice-agent-intake shots each.

---

## 2. What changed in the evidence node

**It walks back for the posting.** If `$json` carries no posting, the node now
reads it from `Ground Match` (falling back to `Merge Context`, `Read Job Row`,
`Cockpit Form`). Wrapped in try/catch, read-only, degrades silently to the old
behaviour if none resolve. `evidence_input.post_source` reports which node the
posting came from on every run.

**A handed-in shape is a hint, not a verdict.** The node now scores the posting
on its own words whenever it has them, and only falls back to the upstream
`shape` when it has nothing of its own to say. When its own reading disagrees,
`shape_override` records both — a disagreement means the upstream table has
drifted and somebody should see it. When a shape is handed in and there is no
posting to check it against, `shape_unverified` is set: that is exactly the
state that shipped four voice-agent-intake shots to a Pipedrive job.

**One posting field, not twenty glued together.** Primary fields first
(`jobPost`, `job_post`, `jobDescription`, `posting`, `post`, `description`),
secondary only if no primary arrived, capped at 12,000 chars. This is the
handoff's hypothesis, fixed anyway — it was a real hazard even if it was not the
active one.

**Fields carrying our own text are dropped.** Anything containing `launchforte`,
`built-with/shots`, `prompt of record`, or three or more of our own pattern
slugs is us echoed back, not a buyer describing a problem. Named in the trace.

**Tools split into two tiers.** A tool the buyer named in their posting can
vouch for a fit. A tool sitting in a `skills` list or `category` tag cannot —
those are marketplace labels, often our own stack reflected at us. Hint-tier
tools are read only when the posting named none, and can never clear the refusal
floor or trigger the vague-tool fallback. This had teeth: a restaurant-menu job
with `skills: "n8n, Zapier, GoHighLevel"` cleared the floor and came back with
lead-routing screenshots. It refuses now.

**Every execution carries its own diagnostic.** `evidence_input` on all three
return paths including the refusals: which field the posting was read from, from
which node, how long each candidate was, which were dropped as ours, where the
tool came from. No separate diagnostic run needed next time.

---

## 3. Five real postings, before and after

Replayed the five most recent real executions through the deployed node, using
each run's actual payload and its actual upstream nodes.

| execution | posting, in short | was | now | tool shown | confidence |
|---|---|---|---|---|---|
| 25938 | GoHighLevel build for a GLP-1 telehealth platform | voice-agent-intake | **messaging-compliance** | GoHighLevel | medium |
| 25843 | leads answered fast, estimates chased, invoices chased, daily reports | voice-agent-intake | **books-reconciliation** | QuickBooks | low |
| 25842 | Instantly.ai AI agents, setup and maintenance | voice-agent-intake | **cold-outreach** | Instantly.ai | low |
| 25841 | cleaner performance tracking in one Airtable system | voice-agent-intake | **reporting** | Airtable | low |
| 25839 | audit and redesign Pipedrive proposal pipeline, stage-entry criteria | voice-agent-intake | **stalled-deal-escalation** | Pipedrive | high |

Five jobs, five patterns, five tools — and in every case the tool shown is one
the buyer named themselves. `shape_override` fired on all five, naming the
stored shape it overruled.

Two of these are honest low-confidence calls rather than obvious wins. 25843 is
a four-ask posting (speed to lead, quote follow-up, invoicing, reporting) and
books-reconciliation is one defensible reading of it, not the only one. The
`low` confidence label is the node telling the truth about that, and the
direction note in the letter softens the claim accordingly. Worth watching.

The synthetic suite also passes: nine postings across four payload shapes —
clean, contaminated, posting-under-an-unregistered-field-name, and a replica of
the real production payload. All correct, including the restaurant-menu job
refusing in every column. `matcher-test.py` runs it.

---

## 4. Deployed

| | before | now |
|---|---|---|
| active version | `902fb7b3` | `7c4a3bb9` |
| Prompt of Record | 21,946 (good) — with a **58,296-char corrupted draft** one Publish click away | 21,946, draft discarded |
| Pick the evidence to attach | 112,077 (stale) | 124,525 |

The corrupted draft is gone: draft and active are the same version, so there is
nothing corrupt left to publish by accident. Payload went in gzipped and
base64-chunked with per-chunk hashes and a full-payload SHA-256 verified in the
page before writing — the channel has silently truncated before.

One correction to the handoff: `return __walk(__out)` count is **0 on the good
version too**, so it does not discriminate. The signals that do are the char
count (21,946 vs 58,296) and the `__walk` mention count (4 vs 12).

---

## 5. Pricing

`pricing.py` restored from your copy, with both refinements redone in the
generator rather than patched into the live node:

**Mandatory phase-split wording.** `pricing_phase_split` is now always a
paragraph. Over the ceiling it names phase one, phase two, and says the split is
not a discount and the total does not change. Under it, it says so and points at
the only lever: remove a line and the number moves with it.

**Mandatory "why it costs this".** `pricing_why_it_costs_this` derives from the
lines actually quoted — change the arithmetic and the paragraph changes with it.
Repeated lines collapse to a count (`4 × $800 ($3,200) for additional
workflows`), because four identical lines read as padding even when the
arithmetic is honest.

Both are named in `pricing_mandatory_blocks` so the Prompt of Record can assert
their presence rather than hope. `pricing_rules_ok` now also fails if either
block is empty or if hourly language reaches any client-facing string.

**Also fixed, from the same root cause:** the pricing node read `job_post ||
text`, which are both absent by the time it runs — so every quote counted one
workflow. It now walks back to `Ground Match` the same way the evidence node
does, and reports `pricing_post_source` and `pricing_post_chars` so a quote
built on an empty string is visible instead of silent.

`pricing-check.py` asserts eleven cases: divisible by five, no charm endings, no
hourly language, no buyer spend in the output, gig channel over the ceiling
always splits, phases always sum back to the total, both mandatory blocks
present. All pass.

**Still unverified:** the closed book — MFLG $2,950, Daleen phase two $3,900,
Drew $950. Those are settled historical numbers and the original postings are
not on disk, so they cannot be re-derived. `pricing-check.py` prints UNVERIFIED
rather than pretending. Paste the three postings into its `CLOSED_BOOK` list and
it will check them.

---

## 6. What is left

1. **`Match Product` still drops the payload.** The evidence node and the
   pricing node now work around it, but the Prompt of Record and everything else
   downstream still see a stale table row instead of the job. The fix belongs in
   that node — spread `$json` through it — and it is yours to make, since it
   touches how products are matched, not just how evidence is picked.
2. **Deploy `cockpit-pricing-node.js`.** There is no pricing node in the Cockpit
   yet; adding one means wiring connections, so I left it for you.
3. **Open an attachment.** Everything above is verified at the node level on real
   payloads. Nobody has yet opened the PDF a buyer would receive. That is the
   check the handoff insists on, and it is the one still outstanding.
4. Paste the three closed-book postings into `pricing-check.py`.
5. Then OpenAI and Anthropic Console.
