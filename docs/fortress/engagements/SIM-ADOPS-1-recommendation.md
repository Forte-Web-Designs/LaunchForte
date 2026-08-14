# SIM-ADOPS-1 — Object mapping recommendation (Quote-to-Cash Pipeline)

Rehearsal deliverable for the Upwork posting "HubSpot Expert Needed for Quote-to-Cash
Pipeline Implementation" (entertainment business selling ad inventory). Nobody has been
contacted, nothing is funded, no client exists. This is a documentation-only card — no
system was touched and no browser was opened to produce it. Every claim below traces to
one of the five files earlier cards wrote in this series, all read from Seth's own Launch
Forte HubSpot portal, portal ID **51819426**:

- `docs/fortress/engagements/SIM-ADOPS-1-portal-inventory.md` (adops-1, commit `d56a1e82`) — cited as **[inventory]**
- `docs/fortress/engagements/SIM-ADOPS-1-products.md` (adops-2b, commit `7682b545`) — cited as **[products]**
- `docs/fortress/engagements/SIM-ADOPS-1-pipeline.md` (adops-3, commit `d71415c7`) — cited as **[pipeline]**
- `docs/fortress/engagements/SIM-ADOPS-1-advertisers.md` (adops-4a2, commit `21b3a6ff`) — cited as **[advertisers]**
- `docs/fortress/engagements/SIM-ADOPS-1-quote.md` (adops-5, commit `8bd039c7`) — cited as **[quote]**

These five files currently live on separate `runner/adops-*` branches, not on this branch —
they were read via `git show <branch>:<path>` rather than assumed from memory. Where the
inventory did not establish a fact, this document says so instead of filling the gap with
general HubSpot knowledge.

---

## 1. Object by object — native or custom

The posting names nine objects for the quote-to-cash chain. **All nine are native HubSpot
objects on this portal — none required, or would require, a custom object build.** [inventory]

| # | Object | Native or custom | Evidence |
|---|---|---|---|
| 1 | Companies | Native | "Native CRM object, activated, 438 live records" [inventory] |
| 2 | Contacts | Native | "Native CRM object, activated, 478 live records" [inventory] |
| 3 | Deals | Native | "Native CRM object, activated, 34 records" [inventory] |
| 4 | Products | Native | Not a schema row in Data Model (Line Items is the schema object), but "the Product Library tool itself... is fully live" [inventory]; the 8 live product records were read directly off this tool [products] |
| 5 | Quotes | Native | "appears as its own row in the Data Model object list" [inventory]; the Legacy Quotes tool loads fully with real copy ("Build customized quotes to close deals faster") [inventory] [quote] |
| 6 | Contracts | Native | "Object exists in Data Model (Sales objects, 85 properties, 19 associated objects, object type ID 0-721)" [inventory] |
| 7 | Invoices | Native | "Object exists (Sales objects, object type 0-53)" [inventory] |
| 8 | Payments (incl. Payment Links) | Native | Settings → Revenue → Payments zero-state is live with a "Set up payments" CTA [inventory] |
| 9 | Orders | Native | "Object exists (CRM objects, object type 0-123)... full record list loads live... with an enabled 'Add order' button" [inventory] |

One caveat the inventory flagged directly: the native **Orders** object (0-123) ships with
"native Shopify / Microsoft Dynamics 365 / NetSuite sync tiles" — it reads as the
e-commerce Orders object, not a bespoke ad-fulfillment order object [inventory]. Before
building against it, confirm with the client whether "Order" in their quote-to-cash
process means an ad insertion order or an e-commerce order — the label is native, but the
semantics may not match an ad-sales workflow out of the box. This is a scoping flag, not a
tier gate.

A tenth object, **Services**, turned up in the same inventory sweep but is not one of the
nine the posting names — it's native, exists, and is simply deactivated with no paywall on
reactivation [inventory]. Noted here for completeness, not counted above.

---

## 2. Tier and add-on requirements, quoted from the portal

| Object | What this plan requires | Portal's own wording |
|---|---|---|
| Companies, Contacts, Deals | Included on this plan, already in use | — (no gate encountered) [inventory] |
| Products | Included, no add-on | "'Create a product' and 'Import' both enabled, no gate" [inventory] |
| **Quotes** | Blocked on this seat, not a plan ceiling — reads as needing a Sales Hub seat assignment for Legacy Quotes, or **Sales Hub Professional** for the AI-CPQ path | Legacy Quotes button tooltip: **"Your permissions don't allow you to create quotes"** [inventory] [quote]. The "Explore AI-powered quotes" button redirects to `/pricing/51819426/upgrade/hub-professional?upgradeSource=legacy-quotes-zero-state`, titled **"Go from quote-to-close faster with AI-powered CPQ"** [quote] |
| **Contracts** | **Revenue Hub Professional or Enterprise seat** | Get-started screen: **"Requires Revenue Hub Professional or Enterprise seat. No commitment or credit card required for trial."** [inventory] |
| Invoices | Included, no add-on found | "'Create' button is live/enabled, no gate... 'No hidden charges and only pay transaction fees to collect online payment'" [inventory] |
| Payments / Payment Links | Included, present but **not configured** — no tier-lock copy seen | "No tier-lock copy appeared on this screen" [inventory]. Payment Links specifically were not isolated as a separate check before the inventory card's budget ran out — treat as unconfirmed, not as gated |
| Orders | Included, no add-on found | "Full record list loads live... with an enabled 'Add order' button" [inventory] |
| Deal pipelines (second pipeline) | **Sales Hub upgrade** to go past this plan's one-pipeline ceiling | "Pipelines used: 1 of 1", Create pipeline greyed out and lock-icon gated [pipeline] |
| Custom objects | **Not established** — see gap list | "did not surface an explicit numeric cap on this screen before the session's budget ran out" [inventory] |

Two gates were found in this whole sweep, and they are different in kind:

- **Contracts** is a genuine plan-tier lock — the portal's own copy names the required tier
  by name (Revenue Hub Professional or Enterprise). [inventory]
- **Quotes** reads as a seat/permission gate, not a plan-tier lock: the tooltip says "your
  permissions," not "your plan," and the object itself is fully present in Data Model
  [inventory]. That distinction matters for scoping the client engagement — it may mean
  assigning an existing paid seat to the right user rather than buying a new tier. This
  reading was not confirmed by actually assigning a seat (that's a billing action, out of
  scope for this rehearsal), so treat it as the most likely explanation, not a proven one.

One connected-chain finding worth carrying into the proposal: once a Revenue Hub seat is in
place, Contracts are not a separate manual build — "Contract records are automatically
created when a quote is accepted, no manual work required" [inventory]. The
quote→contract→invoice chain the posting asks about is one connected Revenue Hub feature on
this plan, not three independent objects to wire together by hand.

---

## 3. How Deal stages should relate to Quote, Contract, and Order state

Carried directly from the pipeline design [pipeline], which was built on paper after the
live build was blocked by the one-pipeline ceiling (Section 2). The core principle: **a
Deal stage is a projection of state that already lives on another object, moved by that
object's real event — never a second, manually-maintained copy of it.**

| # | Stage | Probability | What moves the deal here | Object holding the truth |
|---|---|---|---|---|
| 1 | Lead | 10% | Advertiser inquiry qualified (budget, flight window, target show/audience confirmed) | The Deal itself — nothing to duplicate yet |
| 2 | Negotiating | 30% | A Quote is created and sent | **Quote** — status Draft/Sent |
| 3 | Signed | 70% | The Quote converts to a signed Contract | **Contract** — status Signed |
| 4 | Fulfilling | 90% | The ad campaign goes into flight | **Order** — status In fulfillment, flight dates active |
| 5 | Paid | 100% | Payment clears in full | **Payment**, via the Invoice it's applied to — status Paid |

[pipeline] flags the most tempting mistake directly: adding Deal-level custom properties
(e.g. `contract_signed_date`, `amount_paid`) that shadow the Quote/Contract/Order/Payment
records so a flat sales dashboard doesn't need to join across objects. That drifts —
someone updates the Payment and forgets the Deal property, or vice versa, and the CRM
disagrees with itself.

The recommended build, per [pipeline]: native **associations plus calculated/rollup
properties** that read live off the associated records, with **workflows triggered on the
source object's status change** driving stage moves (Quote sent → Negotiating; Contract
signed → Signed; Order fulfillment status → Fulfilling; Payment paid → Paid) instead of a
rep dragging the card by feel. Any flat field still needed for a dashboard should be
read-only and computed, never a second editable field a human can desync from reality.

---

## 4. The QuickBooks approach for invoicing and payments

**No card in this series opened, tested, or even referenced a QuickBooks connection in
this portal.** None of the five source files mention QuickBooks. This section cannot
responsibly describe a sync direction or failure mode as portal-verified fact, because
nothing was verified — doing so would be general HubSpot product knowledge dressed up as a
finding, which the brief for this card explicitly rules out.

What portal evidence *does* establish, and what it implies for scoping this work:

- **Invoices is a native, usable HubSpot object with no gate found** — "'Create' button is
  live/enabled, no gate" [inventory]. This is the object a QuickBooks sync would need to
  read from or write to; it already exists and is not blocked on this plan.
- **Payments/Revenue Hub is present but not configured** — the "Set up payments" CTA is
  live but nothing has been set up [inventory]. Any invoicing-and-payments recommendation
  is downstream of a decision the client hasn't made yet: process payments inside HubSpot's
  own Revenue Hub, route them through QuickBooks, or both. That decision was not made in
  this rehearsal and can't be inferred from what the portal showed.
- **Contracts requires Revenue Hub Professional or Enterprise** [inventory] (Section 2)
  — if the intended flow is Quote → Contract → Invoice → QuickBooks, the Contract step
  alone already carries a named tier requirement, independent of whatever QuickBooks needs.

Recommendation for the actual engagement, stated plainly as unverified: before proposing a
specific sync direction (HubSpot invoices → QuickBooks, or QuickBooks as the invoicing
system of record with HubSpot read-only), connect a real QuickBooks Online sandbox to a
test portal and read what HubSpot's own setup screen says it will and won't sync — the same
"read the portal's own wording, don't assume" method used for every other object in this
report. Doing that is out of scope for this documentation-only card.

---

## 5. What could not be proven on this plan

Listed plainly, per source:

1. **Exact custom-object cap for this plan.** The "Create a new object" panel didn't
   surface a numeric ceiling before the inventory card's session budget ran out [inventory].
2. **Whether the Quotes gate actually clears by assigning a Sales Hub seat.** The wording
   ("your permissions don't allow you to create quotes") reads as a seat gate rather than a
   plan gate, but this was never tested by actually assigning a seat — that's a billing
   action and out of scope for a rehearsal [inventory] [quote].
3. **Payment Links, isolated from Payments generally.** The inventory card flagged this as
   unfinished: "Payment Links specifically were not separately isolated before budget ran
   out — treat as present pending a follow-up pass" [inventory].
4. **The Quote object's actual field/line-item behavior, live.** Two separate attempts to
   create a Quote were both blocked before any quote content could be entered — Legacy
   Quotes by the permission tooltip, AI-CPQ by a redirect to an upgrade page [quote]. The
   line-item design in that file (three products, $8,450 total) was built on paper against
   the real Product catalog [products], not exercised in a live Quote record.
5. **Deal record layout for Quotes/Line Items.** The one live Deal built for this rehearsal
   has an association sidebar with "only Contacts, Companies, Tickets, Payments, and
   Attachments — there is no Quotes card and no Line Items card," and no "Create quote"
   action on the record [quote]. Whether that's seat-driven (same root cause as #2) or a
   separate layout gap was not determined.
6. **The Deal pipeline design (Section 3) has never been created in HubSpot.** It exists
   only on paper — blocked by "Pipelines used: 1 of 1" with Create pipeline locked
   [pipeline]. The stage names, probabilities, and workflow triggers are a design a
   paid-plan operator could execute directly, not a built-and-verified pipeline.
7. **QuickBooks, entirely.** See Section 4 — nothing in this series touched it.
8. **Whether "Order" in the client's actual process means the native e-commerce Orders
   object found here (with Shopify/Dynamics/NetSuite sync tiles) or an ad-insertion-order
   concept the client will describe differently** [inventory]. This is a scoping question
   for the real engagement, not a plan limitation.

Everything else in this report — the native/custom call for all nine objects, the two named
tier gates (Contracts: Revenue Hub Professional/Enterprise; second pipeline: Sales Hub), and
the Deal-stage-to-Quote/Contract/Order design — traces to portal wording quoted above, not
to memory of how HubSpot generally works.
