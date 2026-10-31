SPEC — INVENTED FOR REHEARSAL. This is not the buyer's document. The buyer said
their own specification would follow on hire; we do not have it. Everything below
is a plausible spec Fortress wrote itself so later cards in this simulation have a
single source of truth to build from. Every object name is prefixed
`LF SAMPLE - ` in its label; every internal name starts `lf_sample_`.

# SIM-EO-1 — HubSpot build spec

## Buyer profile (invented)

A certified women-owned premium branded merchandise and corporate gifting company.
Sells executive gifting programs, employee recognition kits, client onboarding
kits, event/conference swag, and milestone commemoratives to four buyer segments:
Fortune 500 companies, universities, sports organizations, and large privately
held Florida companies. Runs HubSpot **Sales Hub Professional** and **Marketing
Hub Professional**. Adopting a new **target-account (ABM) strategy** — sales and
marketing both need to see which accounts are in-strategy, at what tier, and
whether a program is in motion for them.

Portal for the real build phase of this simulation: Launch Forte HubSpot portal
`51819426`. This card does not open HubSpot — it only writes this spec.

---

## 1. Custom properties

### 1.1 Company properties (4)

**Property 1**
- Internal name: `lf_sample_target_account_tier`
- Label: `LF SAMPLE - Target Account Tier`
- Object: Company
- Field type: Dropdown select (single option)
- Options, in order:
  1. `Tier 1 - Strategic`
  2. `Tier 2 - Growth`
  3. `Tier 3 - Opportunistic`
  4. `Not Targeted`
- Group: Company information
- No default value (left unset until a rep or workflow sets it).

**Property 2**
- Internal name: `lf_sample_account_segment`
- Label: `LF SAMPLE - Account Segment`
- Object: Company
- Field type: Dropdown select (single option)
- Options, in order:
  1. `Fortune 500`
  2. `University`
  3. `Sports Organization`
  4. `Private Company - FL`
- Group: Company information

**Property 3**
- Internal name: `lf_sample_diversity_supplier_requirement`
- Label: `LF SAMPLE - Diversity Supplier Requirement`
- Object: Company
- Field type: Dropdown select (single option)
- Options, in order:
  1. `Yes - formal supplier diversity program`
  2. `No`
  3. `Unknown`
- Group: Company information
- Purpose: flags accounts whose procurement process requires or scores for a
  certified women-owned supplier, so it can be surfaced in proposals.

**Property 4**
- Internal name: `lf_sample_annual_gifting_budget_estimated`
- Label: `LF SAMPLE - Annual Gifting Budget (Estimated)`
- Object: Company
- Field type: Number (plain number, no currency formatting, no decimals)
- Group: Company information
- Purpose: rep's estimate of the account's total annual spend across all gifting
  programs, used to size and prioritize target accounts.

### 1.2 Deal property (1)

**Property 5**
- Internal name: `lf_sample_program_type`
- Label: `LF SAMPLE - Program Type`
- Object: Deal
- Field type: Dropdown select (single option)
- Options, in order:
  1. `Executive Gifting`
  2. `Employee Recognition`
  3. `Client Onboarding Kit`
  4. `Event/Conference Swag`
  5. `Championship/Milestone Commemorative`
  6. `New Hire Welcome Kit`
- Group: Deal information
- Required on the deal creation form used by this pipeline (see Section 3).

---

## 2. Active lists (4)

All four are **active** (dynamic, filter-based) lists, not static.

**List 1 — `LF SAMPLE - Target Accounts: Tier 1 Strategic`**
- Object type: Company-based list
- Filter logic (all conditions must match — AND):
  1. `LF SAMPLE - Target Account Tier` is equal to `Tier 1 - Strategic`

**List 2 — `LF SAMPLE - Target Accounts: Fortune 500 & Universities`**
- Object type: Company-based list
- Filter logic (AND of the two groups below):
  1. `LF SAMPLE - Account Segment` is any of `Fortune 500`, `University`
  2. `LF SAMPLE - Target Account Tier` is known (has any value)

**List 3 — `LF SAMPLE - Open Deals: Executive Gifting Program`**
- Object type: Deal-based list
- Filter logic (AND):
  1. `LF SAMPLE - Program Type` is equal to `Executive Gifting`
  2. `Deal stage` is not any of `Closed Won`, `Closed Lost` (pipeline:
     `LF SAMPLE - Target Account Gifting Pipeline`, see Section 3)

**List 4 — `LF SAMPLE - High-Value Targets, No Open Deal`**
- Object type: Company-based list
- Filter logic (AND):
  1. `LF SAMPLE - Annual Gifting Budget (Estimated)` is greater than or equal to
     `25000`
  2. `LF SAMPLE - Target Account Tier` is any of `Tier 1 - Strategic`,
     `Tier 2 - Growth`
  3. `Number of open deals` is equal to `0`
- Purpose: the account is worth pursuing and sized, but nothing is in motion yet
  — this is the prospecting worklist for the target-account strategy.

---

## 3. Deal pipeline

**Pipeline name:** `LF SAMPLE - Target Account Gifting Pipeline`

Six stages, in order, each with its probability:

| # | Stage name | Probability |
|---|---|---|
| 1 | Target Identified | 5% |
| 2 | Champion Engaged | 15% |
| 3 | Needs & Program Scoping | 35% |
| 4 | Proposal & Sample Kit Sent | 60% |
| 5 | Closed Won | 100% |
| 6 | Closed Lost | 0% |

Stage definitions (for the builder, not stored as a HubSpot field):
1. **Target Identified** — account matches the target-account criteria; no
   contact engaged yet.
2. **Champion Engaged** — a named contact at the account has responded or taken
   a meeting.
3. **Needs & Program Scoping** — program type, quantities, and budget range are
   being defined with the account.
4. **Proposal & Sample Kit Sent** — a written proposal and physical/digital
   sample kit have gone to the buyer.
5. **Closed Won** — contract signed.
6. **Closed Lost** — account passed or chose another vendor.

---

## 4. Sales sequence

**Sequence name:** `LF SAMPLE - Target Account Outreach Sequence`

Five steps. Cadence is measured in days after enrollment (Day 0 = enrollment day).

**Step 1 — Day 0 — Automated email**
- Subject: `Corporate gifting, done right for {{company.name}}`
- Body: `Hi {{contact.firstname}} — I work with organizations like {{company.name}} on executive gifting and recognition programs that actually reflect your brand, not a catalog page. We're a certified women-owned supplier, which I know matters for some procurement processes. Worth a 15-minute call to see if there's a fit for an upcoming program?`

**Step 2 — Day 2 — Manual task: call**
- Task title: `Call {{contact.firstname}} {{contact.lastname}} — target account outreach`
- Call script prompt: `Reference the email sent Day 0. Confirm the right buyer for gifting/recognition programs, ask what's currently in place, and ask about supplier diversity requirements in their procurement process.`

**Step 3 — Day 5 — Automated email**
- Subject: `A quick example — {{company.name}}`
- Body: `Hi {{contact.firstname}} — following up in case the last note got buried. I put together a short case study on a program we ran for an organization similar in size to {{company.name}}. Happy to send it over, or grab 15 minutes if that's easier.`

**Step 4 — Day 9 — Manual task: LinkedIn touch**
- Task title: `Connect with {{contact.firstname}} {{contact.lastname}} on LinkedIn`
- Note prompt: `Send a connection request with a short note referencing the two prior emails. No pitch in the note itself.`

**Step 5 — Day 14 — Automated email**
- Subject: `Should I close the loop, {{contact.firstname}}?`
- Body: `Hi {{contact.firstname}} — I don't want to keep filling your inbox. If corporate gifting or recognition programs aren't a priority right now, no worries at all — just let me know and I'll step back. If timing's just off, happy to check back in a quarter.`

---

## 5. Workflows (2)

**Workflow 1 — `LF SAMPLE - New Tier 1 Target Account Enrollment`**
- Object: Company-based workflow
- Trigger: `LF SAMPLE - Target Account Tier` changes to `Tier 1 - Strategic`
- Actions, in order:
  1. Create task, assigned to the company owner: `Build target account plan for {{company.name}}`, task type Todo, due 3 business days after enrollment.
  2. Set company property `LF SAMPLE - Account Segment` reminder — if the
     property is not yet set, create a second task assigned to the company
     owner: `Confirm account segment for {{company.name}}`, due 1 business day
     after enrollment.
  3. Send an internal notification email to the sales manager (a literal,
     hardcoded internal recipient — never the account's own contact) with the
     subject `New Tier 1 target account: {{company.name}}`.
- Stays in draft (`active: false`) — never turned on by any card in this
  simulation.

**Workflow 2 — `LF SAMPLE - Proposal Sent Follow-Up Reminder`**
- Object: Deal-based workflow, pipeline `LF SAMPLE - Target Account Gifting Pipeline`
- Trigger: Deal stage changes to `Proposal & Sample Kit Sent`
- Actions, in order:
  1. Create task, assigned to the deal owner: `Follow up on proposal + sample kit — {{deal.dealname}}`, due 5 days after the stage change.
  2. Wait 10 days.
  3. If the deal is still in stage `Proposal & Sample Kit Sent`, create a second
     task assigned to the deal owner: `Escalate stalled proposal — {{deal.dealname}}`, due immediately, and send an internal notification email to the sales manager (hardcoded internal recipient).
  4. If the deal has moved to any other stage, end the workflow for that
     enrollment with no further action.
- Stays in draft (`active: false`) — never turned on by any card in this
  simulation.

---

## 6. Dashboard

**Dashboard name:** `LF SAMPLE - Target Account Pipeline Dashboard`

Four reports:

1. **`LF SAMPLE - Target Accounts by Tier`**
   Description: Company count, broken out by `LF SAMPLE - Target Account Tier`
   (bar chart). Shows how many accounts sit in Tier 1, Tier 2, Tier 3, and Not
   Targeted at a glance.

2. **`LF SAMPLE - Pipeline by Program Type`**
   Description: Open deal count and total deal value in `LF SAMPLE - Target
   Account Gifting Pipeline`, broken out by `LF SAMPLE - Program Type` (stacked
   bar chart). Shows which gifting program types are driving the current
   pipeline.

3. **`LF SAMPLE - Deal Stage Funnel — Target Account Pipeline`**
   Description: Funnel report of deal count moving through the six stages of
   `LF SAMPLE - Target Account Gifting Pipeline`, from Target Identified through
   Closed Won, with stage-to-stage conversion rate.

4. **`LF SAMPLE - Sequence Performance — Target Account Outreach`**
   Description: Enrollment, open rate, reply rate, and meeting-booked rate for
   `LF SAMPLE - Target Account Outreach Sequence`, so the outreach cadence in
   Section 4 can be judged on results once it's run against sample data.

---

## Open questions (none block later cards)

- Whether the buyer wants `Closed Lost` reason codes as a separate property is
  left open — not specified here because the real buyer document may already
  define one.
- Whether universities and sports organizations need distinct pipelines from
  Fortune 500 / private-company deals (different procurement cycles) is left
  open; this spec assumes one shared pipeline for the rehearsal.
