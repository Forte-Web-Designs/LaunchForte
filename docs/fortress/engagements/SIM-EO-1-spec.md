# SIM-EO-1 — HubSpot build specification (invented for rehearsal)

**This document is invented for a Fortress rehearsal. It is not the buyer's document.**
The buyer said on the posting that the real specification would be provided on hire.
We do not have it. Everything below — the company, its verticals, its property values,
its pipeline stages, its sequence copy — is a plausible stand-in written so later cards
in this simulation have a single, unambiguous source of truth to build against. No part
of it should be read as, or presented as, a real client's requirements.

**Every object name below is prefixed `LF SAMPLE - ` and every internal name starts
`lf_sample_`,** so the entire build can be found and removed later with one search.
Nothing described here is built by this card — this card only writes the spec. All
HubSpot object creation happens in later cards, as drafts/inactive, never turned on.

---

## The invented buyer

A certified women-owned business (WBE) selling premium branded merchandise and corporate
gifting programs. Customers: Fortune 500 companies, universities and their athletics/
alumni departments, professional and collegiate sports organizations, and large privately
held Florida companies. Portal is on **Sales Hub Professional** and **Marketing Hub
Professional**. They are standing up a **target-account (ABM-style) strategy** for the
first time — today they work reactively from inbound RFQs, and want tiered target
accounts, a defined outreach sequence, a pipeline that reflects a considered-purchase
gifting sales cycle, and reporting that shows pipeline and win rate by vertical.

---

## 1. Custom properties

### 1.1 Company properties (4)

#### Property 1 — Account Tier

| Field | Value |
|---|---|
| Internal name | `lf_sample_account_tier` |
| Label | `LF SAMPLE - Account Tier` |
| Field type | Dropdown select (single option) |
| Group | Company information |
| Description | Where this account sits in the target-account strategy. Set by the account owner after research, not by a form. |

Options, in order:
1. `Tier 1 - Strategic` — named target account, active outreach
2. `Tier 2 - Target` — fits the ideal customer profile, not yet in active outreach
3. `Tier 3 - Nurture` — qualified but not a near-term fit
4. `Unassigned` — default value, not yet reviewed

#### Property 2 — Vertical Segment

| Field | Value |
|---|---|
| Internal name | `lf_sample_vertical_segment` |
| Label | `LF SAMPLE - Vertical Segment` |
| Field type | Dropdown select (single option) |
| Group | Company information |
| Description | Which of the four named buyer segments this account belongs to. Drives sequence choice and reporting. |

Options, in order:
1. `Fortune 500`
2. `University / Higher Ed`
3. `Sports Organization`
4. `Private FL Company`

#### Property 3 — Estimated Annual Gifting Spend

| Field | Value |
|---|---|
| Internal name | `lf_sample_est_annual_gifting_spend` |
| Label | `LF SAMPLE - Estimated Annual Gifting Spend` |
| Field type | Dropdown select (single option) |
| Group | Company information |
| Description | Rough annual spend band on branded merch / gifting, estimated by the account owner from public signals (headcount, prior RFQs, event calendar) — not a hard number from the prospect. |

Options, in order:
1. `Under $10K`
2. `$10K - $50K`
3. `$50K - $150K`
4. `$150K - $500K`
5. `$500K+`

#### Property 4 — Supplier Diversity Requirement

| Field | Value |
|---|---|
| Internal name | `lf_sample_supplier_diversity_requirement` |
| Label | `LF SAMPLE - Supplier Diversity Requirement` |
| Field type | Dropdown select (single option) |
| Group | Company information |
| Description | Whether the buyer's own procurement process requires or prefers a certified diverse supplier — directly relevant since our invented seller is a certified WBE. |

Options, in order:
1. `Requires Certified WBE`
2. `Prefers Diverse Suppliers`
3. `No Stated Requirement`
4. `Unknown`

### 1.2 Deal property (1)

#### Property 5 — Gifting Occasion

| Field | Value |
|---|---|
| Internal name | `lf_sample_gifting_occasion` |
| Label | `LF SAMPLE - Gifting Occasion` |
| Field type | Dropdown select (single option) |
| Group | Deal information |
| Description | What the order is for. Set at deal creation; drives which catalogue/sample kit gets attached to the deal. |

Options, in order:
1. `Holiday Gifting`
2. `Client Onboarding Kit`
3. `Employee Recognition`
4. `Event / Conference Swag`
5. `New Hire Kit`
6. `Executive Gifting`

---

## 2. Active lists (4)

All four are **active** (dynamic, filter-based) lists, not static snapshots.

### List 1 — `LF SAMPLE - Target Accounts: Tier 1 Strategic`
- **Object:** Companies
- **Filter logic (AND):**
  1. `LF SAMPLE - Account Tier` **is equal to** `Tier 1 - Strategic`

### List 2 — `LF SAMPLE - Open Target Deals: Stalled 14+ Days`
- **Object:** Deals
- **Filter logic (AND):**
  1. `Pipeline` **is equal to** `LF SAMPLE - Corporate Gifting Pipeline`
  2. `Deal stage` **is not any of** `Closed Won`, `Closed Lost`
  3. `Last activity date` **is more than** `14 days ago`

### List 3 — `LF SAMPLE - MQL Contacts: University & Sports Vertical`
- **Object:** Contacts
- **Filter logic (AND):**
  1. `Lifecycle stage` **is equal to** `Marketing Qualified Lead`
  2. `Associated Company > LF SAMPLE - Vertical Segment` **is any of** `University / Higher Ed`, `Sports Organization`

### List 4 — `LF SAMPLE - Certified WBE Requirement Accounts`
- **Object:** Companies
- **Filter logic (AND):**
  1. `LF SAMPLE - Supplier Diversity Requirement` **is equal to** `Requires Certified WBE`
  2. `LF SAMPLE - Account Tier` **is any of** `Tier 1 - Strategic`, `Tier 2 - Target`

---

## 3. Deal pipeline

**Pipeline name:** `LF SAMPLE - Corporate Gifting Pipeline`

| # | Stage name | Probability |
|---|---|---|
| 1 | `Target Identified` | 5% |
| 2 | `Qualified / Discovery` | 15% |
| 3 | `Needs Analysis & Sample Kit Sent` | 35% |
| 4 | `Proposal / Quote Sent` | 55% |
| 5 | `Negotiation / Contract Review` | 75% |
| 6 | `Closed Won` | 100% |

Note: HubSpot requires every pipeline to also carry a closed-lost stage. That stage is
platform-required, not one of the six requested here — set it as `Closed Lost` at 0%
and leave the six above as the substantive stages of the sales process.

---

## 4. Sales sequence

**Sequence name:** `LF SAMPLE - Target Account Outreach - Corporate Gifting`
**Enrollment:** manual, one contact at a time, by the account owner — never automatic,
never a real contact in this simulation.

| Step | Day | Type | Copy |
|---|---|---|---|
| 1 | Day 0 | Email | **Subject:** A gifting partner your procurement team won't have to explain twice\n\nHi {{contact.firstname}},\n\nI work with organizations like {{company.name}} on branded merchandise and corporate gifting — onboarding kits, recognition programs, and event swag that actually get used instead of thrown away.\n\nWe're a certified women-owned supplier, which I know can matter for how a program gets approved internally. Worth 15 minutes to see if there's a fit for {{company.name}}?\n\n{{sender.firstname}} |
| 2 | Day 3 | Call task | **Task:** Call {{contact.firstname}} — reference the Day 0 email. Talking points: ask what gifting/merch they're currently running in-house vs. outsourcing, and whether procurement has a supplier-diversity requirement we can speak to. |
| 3 | Day 6 | Email | **Subject:** How a similar {{deal.lf_sample_gifting_occasion}} program came together\n\nHi {{contact.firstname}},\n\nFollowing up on my note last week — I wanted to share how we typically structure a program like this: a short catalogue review, a physical sample kit sent to your office, then a locked quote before anything ships.\n\nHappy to send a sample kit to {{company.name}} at no cost so your team can see the quality directly. Should I send one over?\n\n{{sender.firstname}} |
| 4 | Day 10 | LinkedIn task | **Task:** Send a LinkedIn connection request to {{contact.firstname}} with note: "Hi {{contact.firstname}} — following up on my note about corporate gifting for {{company.name}}. Would love to stay connected either way." |
| 5 | Day 15 | Email | **Subject:** Should I close the loop on this?\n\nHi {{contact.firstname}},\n\nI haven't heard back, so I'll assume gifting isn't a priority for {{company.name}} right now — totally understand if timing's off.\n\nIf that changes, or you'd like that sample kit down the road, just reply here and I'll pick it back up.\n\n{{sender.firstname}} |

---

## 5. Workflows (2)

Both are built as **drafts only** — `active: false` in every later build card. Neither
enrolls a real contact or company; enrollment is tested with sample records only.

### Workflow 1 — `LF SAMPLE - New Tier 1 Target Account Alert`

- **Object:** Company-based workflow
- **Trigger:** `LF SAMPLE - Account Tier` **is equal to** `Tier 1 - Strategic` (re-enrollment on property change: on)
- **Actions, in order:**
  1. Create task, assigned to the company owner: *"Confirm target account fit and build outreach plan for {{company.name}}"*, due 2 business days from enrollment.
  2. Send an internal email notification to the company owner summarizing the company name, vertical segment, and estimated annual gifting spend.
  3. Add the company to list `LF SAMPLE - Target Accounts: Tier 1 Strategic` (list membership is automatic given the filter, so this action is redundant by design and documents intent for whoever reviews the workflow later).

### Workflow 2 — `LF SAMPLE - Stalled Proposal Alert`

- **Object:** Deal-based workflow
- **Trigger:** Deal enters stage `Proposal / Quote Sent` in pipeline `LF SAMPLE - Corporate Gifting Pipeline`, **then** a time delay of 10 days, **then** a branch: continue only if `Deal stage` **is still equal to** `Proposal / Quote Sent`
- **Actions, in order:**
  1. Create task, assigned to the deal owner: *"Deal stalled in Proposal / Quote Sent for 10+ days — follow up or update the stage: {{deal.dealname}}"*, due the same day.
  2. Send an internal email notification to the deal owner and the deal owner's manager (property `Deal owner`'s manager, if set) with the deal name, amount, and days in stage.

---

## 6. Dashboard

**Dashboard name:** `LF SAMPLE - Target Account Pipeline Dashboard`

| # | Report name | Description |
|---|---|---|
| 1 | `LF SAMPLE - Pipeline by Stage (Target Accounts)` | Deal count and total deal amount by stage in `LF SAMPLE - Corporate Gifting Pipeline`, filtered to deals whose associated company has `LF SAMPLE - Account Tier` of `Tier 1 - Strategic` or `Tier 2 - Target`. Shows where target-account revenue is concentrated in the funnel. |
| 2 | `LF SAMPLE - New Target Companies by Vertical (Monthly)` | Count of companies created per month, broken down by `LF SAMPLE - Vertical Segment`, for companies with `LF SAMPLE - Account Tier` not equal to `Unassigned`. Shows which vertical the target-account motion is actually reaching. |
| 3 | `LF SAMPLE - Sequence Performance: Target Account Outreach` | Enrollment, open rate, reply rate and task-completion rate for sequence `LF SAMPLE - Target Account Outreach - Corporate Gifting`. Shows whether the 5-step cadence is generating replies before a deal is created. |
| 4 | `LF SAMPLE - Closed-Won Amount by Vertical & Gifting Occasion` | Total closed-won deal amount, grouped by the associated company's `LF SAMPLE - Vertical Segment` and the deal's `LF SAMPLE - Gifting Occasion`, for deals in `LF SAMPLE - Corporate Gifting Pipeline`. Shows which vertical/occasion combination is actually converting. |

---

## Open questions for whoever builds against this spec

- Real supplier-diversity certification body (WBENC vs. other) is unspecified — invented
  as generic "certified women-owned" since the buyer's posting didn't name one.
- Whether Marketing Hub Professional forms/landing pages are in scope for this
  simulation, or whether the target-account motion is sales-only — not addressed here
  because no later card in this simulation has asked for it yet.
