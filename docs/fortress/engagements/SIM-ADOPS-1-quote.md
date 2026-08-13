# SIM-ADOPS-1 — Quote assembled from the Products catalog (rehearsal)

Simulated rehearsal against the Upwork posting "HubSpot Expert Needed for Quote-to-Cash
Pipeline Implementation" (entertainment business selling ad inventory). Nobody has been
contacted, nothing is funded, no client exists. All data below is invented demo content,
built in **Seth's own Launch Forte HubSpot portal, portal ID 51819426**
(www.launchforte.com). No real advertiser, contact, or rate.

## Portal confirmation

Confirmed via the HubSpot Accounts Dashboard (`app.hubspot.com/myaccounts`) before
touching anything: four portals are visible on this login (Another Source 6126385,
FMI 14542748, Launch Forte 51819426, SQFI 19578256). Navigated explicitly into
**Launch Forte, portal 51819426**, confirmed by the account switcher label ("Launch
Forte") in the top-right of every screen worked in. No other portal was opened or
touched.

## Tab

Work was done in one browser tab, opened fresh for this session (the only other tab
open was the browser extension's own "Welcome" tab, present before this session
started and never touched). A second tab opened briefly by clicking "Explore
AI-powered quotes" (it landed on a Sales Hub Professional pricing/upgrade page) was
closed immediately without interacting with it further. The work tab was closed at
the end of this session.

## What was built live

**Deal** — `Nightfall Gaming Studios — Fall Campaign (SIM-ADOPS-1)`, record ID
`63837161559`, on the portal's only pipeline ("Sales Pipeline"), stage
"Presentation Scheduled" (closest fit to "we've put a quote in front of them"),
amount $8,450 (matches the line-item design total below).

**Associations**, confirmed live on the Deal record and in the screenshot below:
- Company: `Nightfall Gaming Studios (SIM-ADOPS-1)` (pre-existing, created by card
  adops-4/4a), marked Primary
- Contact: `Jordan Voss`, Head of Growth Marketing (SIM-ADOPS-1),
  jordan.voss@example.com (pre-existing, created by card adops-4a)

## Status: the Quote object itself was NOT created — blocked

Two independent routes to creating a Quote were tried, in this portal, on Seth's own
login, and both were blocked before any quote content could be entered:

1. **Legacy Quotes** (`app.hubspot.com/commerce-get-started/51819426/quotes`, then
   `app.hubspot.com/quotes/51819426`) — the page loads fully ("Build customized
   quotes to close deals faster"), but the "Create a legacy quote" button is
   disabled with the tooltip, quoted verbatim:
   > **"Your permissions don't allow you to create quotes"**
   Screenshot: `docs/proof/SIM-ADOPS-5-quotes-permission-gate.png`.
2. **AI-powered CPQ** ("Explore AI-powered quotes" button on the same screen) does
   not open a quote builder at all — it redirects straight to a Sales Hub
   Professional upgrade/pricing page
   (`/pricing/51819426/upgrade/hub-professional?upgradeSource=legacy-quotes-zero-state`,
   titled "Go from quote-to-close faster with AI-powered CPQ"). That tab was closed
   without touching anything on it — no click on Upgrade, no trial started, no
   billing page interacted with.

A third check was made from the natural in-context entry point: the Deal record
itself. Its association sidebar offers only Contacts, Companies, Tickets, Payments,
and Attachments — there is no Quotes card and no Line Items card in this deal's
layout, and the record's "Actions" menu has no "Create quote" or "Add line item"
action either. This matches the seat/permission read: Quotes is not surfaced as an
option anywhere in this seat's UI, not merely disabled on one screen.

This reads as a **seat/permission gate, not a hard plan-tier lock** — the wording is
"your permissions," and the object itself is present in the portal's Data Model
(confirmed by an earlier card in this series, adops-1). Per house rules, no attempt
was made to route around it: no click on "Upgrade," no trial started, no billing
screen touched beyond landing on it involuntarily via the CPQ button (immediately
closed).

## The Quote, designed on paper

Below is the exact Quote that would be created the moment a Sales Hub seat is
assigned to this login — detailed enough that a paid-seat operator could execute it
directly, no further design work needed.

**Quote name:** Nightfall Gaming Studios — Fall Campaign Proposal (SIM-ADOPS-1)
**Associated Deal:** Nightfall Gaming Studios — Fall Campaign (SIM-ADOPS-1) — `63837161559` (built live, see above)
**Associated Company:** Nightfall Gaming Studios (SIM-ADOPS-1)
**Associated Contact:** Jordan Voss (jordan.voss@example.com)
**Status:** Draft — never sent, no signature collected, no payment step attached

**Line items** — all three pulled from the 8-product catalog built in card adops-2
(`docs/fortress/engagements/SIM-ADOPS-1-products.md`), spanning three asset types
(exceeds the two-asset-type minimum):

| # | SKU | Product | Asset Type | Unit Price | Qty | Line Total |
|---|-----|---------|-----------|-----------:|----:|-----------:|
| 1 | NL-AW-FULL | Afterglow Weekly — Featured Newsletter Sponsorship | Newsletter sponsorship | $4,500.00 | 1 | $4,500.00 |
| 2 | MN-BP-60 | Backstage Pass — Host-Read Mention (:60) | Mention | $2,200.00 | 1 | $2,200.00 |
| 3 | AR-GR-PRE30 | The Green Room — Pre-Roll Ad Read (:30) | Ad read in show | $1,750.00 | 1 | $1,750.00 |
| | | | | | **Total** | **$8,450.00** |

Every line here is a pointer to an existing Product record (by SKU) in the catalog —
none of it is free-typed. This is the point the posting is actually testing: the
quote's numbers live in the Product Library, not retyped per-quote, so a price change
on a product (say, Backstage Pass mid-roll goes to $3,700) propagates the next time a
quote references it rather than needing to be hunted down across every draft quote
that used the old number. The Deal's `amount` ($8,450, set live above) already
matches this line-item total, so the moment the Quote is created and its Deal
association is set, the numbers reconcile with no manual entry.

## PASS note for this criterion

**"Create one Quote... assembled from line items taken from the Products catalog"**
— blocked by plan/seat gate, design documented above, gate photographed and quoted
verbatim. See EVIDENCE block in the session report for the full per-criterion verdict.
