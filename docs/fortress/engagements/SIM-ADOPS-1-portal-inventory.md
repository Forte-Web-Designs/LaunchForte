# SIM-ADOPS-1 — HubSpot Portal Inventory (Quote-to-Cash Pipeline)

Rehearsal against the Upwork posting "HubSpot Expert Needed for Quote-to-Cash Pipeline
Implementation" (entertainment / ad-inventory business). Nobody contacted, nothing funded,
no client exists. Read directly off Seth's own Launch Forte HubSpot portal, portal ID
**51819426** (www.launchforte.com), logged in as Seth Forte. Confirmed via the HubSpot
account picker before touching anything else — the other portals visible on the account
(Another Source 6126385, FMI 14542748, SQFI 19578256) were never opened.

Tab: single browser tab, driven via the Playwright browser tool (the HubSpot MCP connector
requires interactive OAuth this session cannot perform, so the portal's own UI was driven
directly instead). No tab left open beyond the one used for this session; it was returned
to the Data Model manage screen at the end.

Nothing was created, activated, published, or sent. Where a screen offered "Activate
object," "Create," or "Set up payments," the option was read and screenshotted, never
clicked through to completion.

## Object / tool inventory

| Object | Status | Evidence |
|---|---|---|
| **Companies** | Present and usable | Native CRM object, activated, 438 live records, full record list at `/contacts/51819426/objects/0-2/...` |
| **Contacts** | Present and usable | Native CRM object, activated, 478 live records, full record list at `/contacts/51819426/objects/0-1/...` |
| **Deals** | Present and usable | Native CRM object, activated, 34 records, full record list at `/contacts/51819426/objects/0-3/...` |
| **Products** | Present and usable | Not listed as a schema row in Data Model (it isn't a discrete "CRM object" there — Line items is), but the Product Library tool itself (`/commerce-get-started/51819426/products`) is fully live: "Create a product" and "Import" both enabled, no gate |
| **Quotes** | Present but gated (by seat, not by object) | "Quotes" appears as its own row in the Data Model object list (confirmed present in the sidebar object list alongside Contracts, Invoices, etc.; exact record/property counts not captured). Legacy Quotes tool loads fully ("Build customized quotes to close deals faster"), but "Create a legacy quote" is disabled with tooltip **"Your permissions don't allow you to create quotes."** A newer "AI-powered CPQ" path is also offered alongside Legacy Quotes. This is a seat/permission gate on Seth's own user, not a plan-level lock message from HubSpot |
| **Contracts** | Present but gated — plan tier | Object exists in Data Model (Sales objects, 85 properties, 19 associated objects, object type ID **0-721**), but the get-started screen states in HubSpot's own words: **"Requires Revenue Hub Professional or Enterprise seat. No commitment or credit card required for trial."** A "Coming soon" sub-feature ("Create and edit contracts directly, without starting from a quote") is noted as **"No Revenue Hub seat required"** once shipped |
| **Invoices** | Present and usable | Object exists (Sales objects, object type 0-53). Get-started screen's "Create" button is live/enabled, no gate. Copy: "No hidden charges and only pay transaction fees to collect online payment" |
| **Payments and Payment Links** | Present, not yet configured (no gate found) | Settings → Revenue → Payments (`/commerce/51819426/zero-state`) shows "Payment processing with your CRM," "Process secure payments with HubSpot's tools — no code required," and a live "Set up payments" CTA. No tier-lock copy appeared on this screen. This screen also surfaced a notable rebrand banner: **"Commerce Hub is now Revenue Hub."** Payment Links specifically were not separately isolated before budget ran out — treat as present pending a follow-up pass |
| **Orders** | Present and usable | Object exists (CRM objects, object type **0-123**). Full record list loads live at `/contacts/51819426/objects/0-123/...` with an enabled "Add order" button and native Shopify / Microsoft Dynamics 365 / NetSuite sync tiles — this is the e-commerce Orders object, not a Commerce Hub checkout object |
| **Services** | Present but deactivated (no tier lock shown) | Native object exists (CRM objects, object type **0-162**, 45 properties, "Intangible offerings provided to customers, such as onboarding and consulting, repairs and maintenance, and personal care"). Object status filter shows it under "Deactivated objects." The row menu offers **"Activate object"** with no upgrade/paywall copy attached to that action |

## Custom objects

The "Create a new object" panel (Data Model → Add custom object) offers "Create with AI"
and "Create manually," the latter listing HubSpot-defined templates first (Appointments,
Courses, Listings, Projects, etc. — several of which are the same deactivated native
objects above, offered as one-click activations rather than true custom builds). The panel
did not surface an explicit numeric cap on this screen before the session's budget ran out,
so the exact custom-object allowance for this plan is **not confirmed** — that's the one
open item below.

## Commerce tools — do they appear at all?

Yes. The Commerce/Revenue Hub surface is fully present in the nav and settings (Settings →
Revenue → Billing / Payments / Tax), and most of its objects (Invoices, Orders, Products,
Payments setup) are usable with no plan-tier gate encountered. The one confirmed plan-tier
lock in the whole sweep was **Contracts**, gated behind "Revenue Hub Professional or
Enterprise seat."

## What surprised me

1. **HubSpot renamed Commerce Hub to Revenue Hub** mid-flight — the Payments zero-state
   page carries an active "Commerce Hub is now Revenue Hub" banner. Any proposal language
   should say "Revenue Hub," not "Commerce Hub."
2. **Quotes is blocked by a seat/permission message, not a plan message** — "Your
   permissions don't allow you to create quotes" — even on the portal owner's own login.
   That reads as a paid-seat requirement (a Sales Hub seat not assigned to this user) rather
   than a hard plan ceiling, which matters for scoping: the client may just need a seat
   assigned, not an upgrade.
3. **Contracts auto-generate from an accepted Quote** in the gated flow ("Contract records
   are automatically created when a quote is accepted, no manual work required") — the
   quote-to-contract-to-invoice chain the posting is asking about is a single connected
   Revenue Hub Professional/Enterprise feature, not three separate builds.
4. Several objects that read as obviously "core CRM" (Appointments, Courses, Listings,
   Services) ship **deactivated by default** and are one click from being turned on with no
   visible paywall — cheap wins if the client's data model needs any of them.

## Open question

Exact custom-object cap for this plan was not read off the UI before the session ended —
confirm on a follow-up pass (Data Model → Add custom object → scroll the "Create manually"
panel fully, or check Settings → Account & Billing → plan limits) before quoting a number
in the proposal.
