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
