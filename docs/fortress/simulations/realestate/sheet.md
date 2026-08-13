# SIM RE - Agent Suite — shared store

Spreadsheet id: `1oLQS6-T_pGE_-sin2WFmIdygDHY2wdpiJmSA-jJKOO4`
URL: https://docs.google.com/spreadsheets/d/1oLQS6-T_pGE_-sin2WFmIdygDHY2wdpiJmSA-jJKOO4/edit

Created under the house sim account (fortresslaunchforte@gmail.com), private, not shared,
not published to the web. Four tabs created: `buyers`, `listings`, `visits`, `documents`,
matching the tab order and names in the SIM-RE-1 spec.

## Status: INCOMPLETE — stopped on budget exhaustion

Tab creation and naming is done. Column headers and seed data (6 listings, one listing's
document checklist) were **not** reliably entered before the session's budget ran out.
The `buyers` tab currently has a single comma-joined string sitting in cell A1 rather than
split into its ten header columns — that row needs to be fixed, not trusted as-is.

Root cause: this browser session's Google Sheets grid does not accept Playwright's
`fill()` on cell edit boxes, embedded `\t`/`\n` characters typed via `pressSequentially`
land inconsistently (sometimes committed as literal text, sometimes as real Tab/Enter
key events — verified both outcomes on the same input during this session), and
clipboard-based paste (`navigator.clipboard.writeText` + `Ctrl+V`) did not deliver text
into the grid even though the write call itself resolved without error. Reliable entry
required one real keypress-driven `type` + `Tab` cycle per cell, which is correct but
too slow to finish four tabs' worth of headers and seed rows inside the session budget.

## Next steps for whoever resumes this card

- Re-open the spreadsheet at the id above.
- Clear cell A1 on `buyers` (it holds a stray comma-joined string, not real headers).
- Enter headers and seed data one real cell-edit + Tab keypress at a time (confirmed
  reliable in this session), or find a faster input path this account's Sheets session
  actually accepts (e.g. importing a small CSV file per tab via File > Import, if that
  menu proves reachable) before falling back to cell-by-cell typing.
- Column orders per the spec:
  - `buyers`: buyer_id, name, phone, email, budget_min, budget_max, beds, area, notes, created_at
  - `listings`: listing_id, address, area, price, beds, status, owner_name, owner_phone
  - `visits`: visit_id, buyer_id, listing_id, visit_date, slot_start, slot_end, status
  - `documents`: listing_id, doc_name, required, present, verified_by, verified_at
