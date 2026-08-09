# Standing rule: never conclude "not found" from an unpaged read

**Filed Aug 9, 2026, after the third instance.**

## The rule

**No exhaustive claim may be made from a single API read.** Any statement of the
form "not found", "zero matches", "all N checked", or a count used to support a
conclusion must first page to the reported total, and must state the page count
and the total it reached.

Wrong: *"No n8n workflow writes upwork_jobs — all 100 checked."*
Right: *"No workflow writes upwork_jobs — 374 of 374 checked across 4 pages."*

If the total is unknown or unbounded, the claim is not "not found". It is
**"not found in the first N of an unknown total"**, and it cannot carry a
decision.

## Known caps in this estate

| Endpoint | Behaviour |
|---|---|
| `/rest/workflows` | returns **100** regardless of `take`. Page with `skip`. The response `count` field carries the real total (374 at time of writing). |
| `/rest/projects/{p}/data-tables/{id}/rows` | returns **250** max regardless of `take`. Page with `skip`; `count` carries the total. |
| `/rest/data-tables-global` and `/rest/projects/{p}/data-tables` | default **10**. Nearly caused a duplicate `ideas` table in July because an existing table did not appear in the first page. |

Assume every list endpoint caps. Check `count` against `data.length` on every
read and page until they agree.

## The three instances

1. **July — the data-tables list defaulted to 10.** An existing `ideas` table was
   not in the first page, so it read as absent. A duplicate table was nearly
   created.
2. **Earlier — data-table rows capped at 250.** Caught, and the paging helper
   `pull()` exists because of it.
3. **Aug 9 — `/rest/workflows` capped at 100.** Produced the confident claim that
   no n8n workflow writes `upwork_jobs`, and a recommendation to migrate the
   ingest to Apify to fix a "trigger living on the Mac mini". The real cause was
   `Upwork: Job Engine` with `1-5` in its cron day field, sitting on page two.
   The diagnosis was wrong, the proposed fix was aimed at the wrong system, and
   the actual repair was a one-line cron edit.

The pattern is identical each time: **an unpaged read produced a confident
negative, and the negative drove a decision.** A partial read is not evidence of
absence, and the failure is silent — the API returns 200 with a plausible-looking
list.

## The check, in code

```js
const pull = async (url) => {
  const first = await get(url + '?take=250&skip=0');
  let rows = first.data.slice();
  while (rows.length < first.count) {
    const next = await get(url + '?take=250&skip=' + rows.length);
    if (!next.data.length) break;          // guard against a cap that lies
    rows = rows.concat(next.data);
  }
  if (rows.length < first.count) throw new Error('paged ' + rows.length + ' of ' + first.count);
  return rows;
};
```

Any audit that reports a negative should print `checked N of M` alongside the
finding, so an unpaged read is visible in the output rather than hidden in it.

---

# The sibling failure: an aggregate over a field that was never there

**Added Aug 9, the same night, after the second instance.**

## What happened

Auditing the Command Center's snapshot endpoint, I counted distinct `task_id`
across the returned tasks and reported **"103 rows, 1 distinct task_id — 103×
fan-out, the bug is the snapshot builder."**

The payload keys tasks on **`id`**, not `task_id`. Every row returned `undefined`.
"One distinct value" was one distinct `undefined`. Checked on the real key:
**103 rows, 103 distinct ids, 103 distinct objects. Completely clean.**

The wrong conclusion then survived four more queries, because each one took the
fan-out as established and went looking for its cause — a merge node, a `.first()`
versus `.all()`, a closure shadowing bug. All of it was archaeology on a bug that
did not exist, and it nearly ended in a fix to a working node.

## The rule

**Before any `count`, `distinct`, `filter`, `group` or `map` over a named field,
print one raw record and confirm the field exists.**

One line, before the aggregate:

```js
console.log('field check:', Object.keys(rows[0]));
// or, cheaper and self-asserting:
if (!(FIELD in rows[0])) throw new Error(FIELD + ' is not on these records: ' + Object.keys(rows[0]));
```

An aggregate over a missing field does not throw. `undefined` is a legal value, a
`Set` of them has size 1, and `filter(x => x.missing === y)` returns `[]`. Every
one of those is a plausible-looking answer.

## The shared root

Both instances have the same shape, and it is worth naming because it will
recur in a third form:

> **A confident conclusion drawn from an unverified assumption that returned a
> plausible result instead of an error.**

- The unpaged read returned a valid list — just not the whole one.
- The aggregate returned a valid number — just not over a real field.

Neither failed loudly. Both produced output that looked exactly like a correct
answer, which is why neither got a second look. The defence is the same in both
cases: **assert the precondition before trusting the result**, and make the
assertion part of the output so a reader can see it held.

`checked N of M` for paging. `field check: [...]` for aggregates. If the audit
cannot show its precondition, the audit is a guess with a number attached.
