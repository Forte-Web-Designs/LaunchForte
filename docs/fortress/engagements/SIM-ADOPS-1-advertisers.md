# SIM-ADOPS-1 — Advertiser demo companies and contacts

Rehearsal data only, HubSpot portal 51819426 (Launch Forte). Nothing here is a real
client, contact, or transaction. All records tagged `(SIM-ADOPS-1)`. This is a
read-only write-up — no company, contact, or association was created, edited, or
deleted while producing it. Values below were read directly off the portal on
2026-08-13, not copied from an earlier draft.

## Companies (6)

All six were present and unchanged in the portal at write-up time.

| Company | Record ID |
|---|---|
| Bluecrest Motors (SIM-ADOPS-1) | 57441996317 |
| Solstice Retail Co (SIM-ADOPS-1) | 57441996322 |
| Ember & Oak QSR Group (SIM-ADOPS-1) | 57446602589 |
| Meridian Trust Financial (SIM-ADOPS-1) | 57442119816 |
| Nightfall Gaming Studios (SIM-ADOPS-1) | 57441996340 |
| Cobalt Peak Airlines (SIM-ADOPS-1) | 57442183237 |

Proof: `docs/proof/sim-adops-1-advertisers-companies.png` — all six visible together
in the Companies list, filtered to `SIM-ADOPS-1`.

## Contacts (6)

All six were present and unchanged in the portal at write-up time.

| Contact | Email | Intended company |
|---|---|---|
| Simone Achterberg | simone.achterberg@example.com | Cobalt Peak Airlines (SIM-ADOPS-1) |
| Jordan Voss | jordan.voss@example.com | Nightfall Gaming Studios (SIM-ADOPS-1) |
| Elena Kowalski | elena.kowalski@example.com | Meridian Trust Financial (SIM-ADOPS-1) |
| Marcus Delgado | marcus.delgado@example.com | Ember & Oak QSR Group (SIM-ADOPS-1) |
| Priya Nandakumar | priya.nandakumar@example.com | Solstice Retail Co (SIM-ADOPS-1) |
| Derek Hallowell | derek.hallowell@example.com | Bluecrest Motors (SIM-ADOPS-1) |

Proof: `docs/proof/sim-adops-1-advertisers-contacts.png` — all six visible together
in the Contacts list, filtered by last name to this set.

## Actual company associations, read from each contact record

Checked live via each contact's inline "Associated Companies" panel — not assumed
from the table above.

| Contact | Associated company on the portal right now |
|---|---|
| Simone Achterberg | **Cobalt Peak Airlines (SIM-ADOPS-1)** — correct, sole association |
| Derek Hallowell | **Bluecrest Motors (SIM-ADOPS-1)** — correct, plus the auto-matched "example.com" company below |
| Jordan Voss | Only the auto-matched "example.com" company (record 57220742702) — **not** associated to Nightfall Gaming Studios |
| Elena Kowalski | Only the auto-matched "example.com" company (record 57220742702) — **not** associated to Meridian Trust Financial |
| Marcus Delgado | Only the auto-matched "example.com" company (record 57220742702) — **not** associated to Ember & Oak QSR Group |
| Priya Nandakumar | Only the auto-matched "example.com" company (record 57220742702) — **not** associated to Solstice Retail Co |

The "example.com" company (record 57220742702, no name) is HubSpot's own automatic
domain-matching artifact, created because every demo contact shares the
`@example.com` domain. It is cosmetic noise, not a duplicate advertiser. It has been
removed from Simone Achterberg's record but is still attached to the other five.

This confirms, unchanged, the incomplete state left by the card that built these
records (`runner/adops-4a-finish-the-advertiser-re`, commit `6d73c452`): it ran out
of budget after associating only Simone Achterberg and Derek Hallowell to their real
companies. A follow-up card can finish the remaining four by opening each contact's
Companies panel, using "Add" to attach the correct company from the table above, and
optionally removing the "example.com" chicklet on all five to clean up the noise.
That work is out of scope for this write-up card, which is read-only.
