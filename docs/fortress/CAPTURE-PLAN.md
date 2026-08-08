# The next round of tools

What to sign into, in what order, and what gets shot once you have.

Nothing here is a guess about what buyers want. It is 6,800 real Upwork
postings out of `upwork_jobs`, counted by which tool they name, then weighted by
whether the judge graded them A or B — because a tool that only ever shows up on
C-graded staffing gigs is not worth an afternoon.

The library today is 669 shots across 25 shapes and 15 tools. The gaps below are
tools that appear in the demand and nowhere in the library.

---

## Tier 1 — free forever, no card, do these first

| # | Tool | Jobs naming it | A or B | What it fills |
|---|------|---------------:|-------:|---------------|
| 1 | **Klaviyo** | 159 | 68 | `storefront-upsell` has Shopify and nothing else. 1,588 postings name Shopify and Klaviyo is what sits next to it. This is the exact gap that made a letter describe a Klaviyo screenshot that was not in the PDF. |
| 2 | **Supabase** | 167 | **123** | The best ratio in the whole set — three quarters of the jobs naming it are worth bidding. `ai-research-agent` has 3 shots total and `data-model-architecture` has no database in it at all. |
| 3 | **Zoho CRM + Books** | 196 | 104 | A second CRM for `lead-routing` and `stalled-deal-escalation`, and a second ledger for `books-reconciliation`, which today is QuickBooks or nothing. |
| 4 | **Salesforce** (Developer Edition) | 176 | 69 | Free forever, full Lightning UI, and it is the org type meant for exactly this. Buyers naming Salesforce are the largest ones in the flow. |
| 5 | **Slack** | 328 | 79 | Twenty minutes of work. `alerting` and `approval-routing` currently end in a Google Sheet, which reads as unfinished. |
| 6 | **Notion** | 225 | 44 | `project-ops` is Monday and nothing else. |
| 7 | **Calendly** | 91 | 33 | `scheduling` is GoHighLevel and n8n. Calendly is what people who are not on a CRM actually use. |
| 8 | **ElevenLabs + Retell + Vapi** | 145 | **98** | Small counts, excellent grades. `voice-agent-intake` has n8n, GHL and Twilio — no actual agent UI. ElevenLabs is free; Retell gives $10 credit with no card; Vapi's dashboard is free to open. |
| 9 | **Looker Studio** | 43 | 21 | Free with the Google account you already have. `reporting` has no BI tool in it. |

Every one of these is a free account with no credit card. Slack, Notion,
Calendly, Looker Studio and ElevenLabs are five minutes each.

## Tier 2 — clock starts when you sign up, so do these in one sitting

Do not open these until we are ready to shoot the same week.

| Tool | Window | Note |
|------|--------|------|
| **Xero** | 30 days | Comes with a **demo company** already full of sample data — better than anything we would invent. |
| **DocuSign** | unlimited | Use the free **developer sandbox**, not the 30-day trial. `document-assembly` is n8n only. |
| **Smartlead** | 14 days | No card. `cold-outreach` is Instantly and nothing else. |
| **WooCommerce** | none | Free, but needs somewhere to run. A local install is fine and covers the non-Shopify half of 515 WordPress postings. |

## Skipping, and why

- **Acuity** — no free tier at all, seven days. Calendly covers the shape.
- **Gorgias** — no free tier, has to be wired to a real store, and its own docs
  disagree about whether the trial is 7 or 30 days.
- **Power BI** — Desktop is Windows only and you are on a Mac. Looker Studio
  gets us the same shape for nothing.

---

## What gets shot, per tool

Four shots per tool per shape, matching the beats the Cockpit already writes to:
the system, the thinking, their world, the result.

**Klaviyo** → `storefront-upsell`, `reactivation`
- Flow builder canvas with the post-purchase branch and the exclusion split
- The profile view showing consent state and why a suppressed profile is skipped
- Segment editor for buyers with one order and no companion product
- The flow's own analytics, one row per step, showing where it stops

**Supabase** → `ai-research-agent`, `data-model-architecture`, `system-sync`
- Table editor with the schema and the foreign keys visible
- SQL editor with the dedupe query that stops the same record landing twice
- Auth users list with row level security policy shown
- Logs, the run that failed and the run that retried

**Zoho** → `lead-routing`, `stalled-deal-escalation`, `books-reconciliation`
- Blueprint / workflow rule builder with the escalation condition
- Deal list filtered to stalled, sorted by days since last touch
- Books: invoice matched to payment, showing the reconciliation
- Books: aging report

**Salesforce** → `lead-routing`, `data-model-architecture`
- Flow Builder canvas with the assignment decision element
- Object Manager showing a custom object and its relationships
- List view of leads with the routing field populated
- Debug log of a flow run

**Slack** → `alerting`, `approval-routing`
- Workflow builder with the approval step
- The channel showing the alert as it arrives, with the fields laid out
- The approve/reject interaction and what it wrote back
- The audit trail message after the decision

**Voice (ElevenLabs / Retell / Vapi)** → `voice-agent-intake`
- Agent config: the prompt, the tools it may call, and what it may only flag
- The transcript view with the turn where it handed off
- The call log with duration, outcome and cost per call
- What it wrote onto the record afterwards

**Notion** → `project-ops`, `client-onboarding`
- Database with the properties and the rollup that drives status
- Board view by stage with the WIP limit visible
- Template button and what it stamps out
- Automation panel

**Calendly** → `scheduling`
- Event type config with buffers and the availability rules
- Routing form that sends different answers to different event types
- Booked calendar with the reminder cadence shown
- Workflow panel: the no-show follow-up

**Looker Studio** → `reporting`
- The report itself, executive layout
- Data source panel showing the blend
- A calculated field with the definition open
- Scheduled delivery config

---

## The rules that still apply to every shot

- Sample data only. Invented names, `@example.com` addresses. Nothing real,
  nothing Upwork-related anywhere in frame.
- Never a credential, never a billing page, never an account list.
- Sample data gets built from the actual postings in `upwork_jobs`, so the
  fixtures read like the businesses that are actually hiring — a planner brand,
  a moving company, a restoration contractor — not like a tutorial.
