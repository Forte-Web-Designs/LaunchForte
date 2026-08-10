# Profile Persistence Probe B — Result

## Action
Navigated to `https://launchforte.com` and read back the `lf_persist_probe` marker via `browser_evaluate`.

## Script run
```js
() => ({ marker: localStorage.getItem('lf_persist_probe'), origin: location.origin, keys: Object.keys(localStorage).length })
```

## Returned object (verbatim)
```json
{
  "marker": "lfprobebwneaive",
  "origin": "https://launchforte.com",
  "keys": 2
}
```

## Comparison to earlier job
An earlier job on branch `runner/profile-persist-a2-write-a-marker-into-the` (see
`docs/proof/profile-persistence-a.md` on that branch) wrote:

```js
() => { localStorage.setItem('lf_persist_probe', 'lfprobebwneaive'); ... }
```

The marker value read back in this session, `lfprobebwneaive`, is an exact match
for the value written by that earlier job.

## Browser tools used
- `mcp__playwright__browser_navigate`
- `mcp__playwright__browser_evaluate`

## Conclusion
**Yes** — the browser profile persists between jobs. The `lf_persist_probe` marker
written by an earlier job (`profile-persist-a2`) was still present, unchanged, in
this brand-new session's `localStorage` for `https://launchforte.com`.
