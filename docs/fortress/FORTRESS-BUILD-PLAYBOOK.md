# Fortress build playbook
A job posting lands. Find its pattern here. Everything you need is in the section:
the real ask, the pain, the product, the proof to send, how to build it, what will bite you,
and where the money is after the first invoice.

Cross-references: kit JSON in `fortress-kits.zip` · screenshots in `evidence-library/<shape>/`
· registry in `build-library.json` · method in `PRODUCT-KIT-STANDARD.md`

Every screenshot listed is a real file. Every ask quoted is a real posting from the
Command Center's live Upwork feed.

---

## Index

- **The Upsell Engine** — `storefront-upsell` — demand 599
- **The Reconciliation Build** — `books-reconciliation` — demand 246
- **The Booking System** — `scheduling` — demand 241
- **The Reporting Layer** — `reporting` — demand 181
- **The Sync Build** — `system-sync` — demand 147
- **The Rescue** — `stalled-deal-escalation` — demand named repeatedly in live postings
- **The Lead Router** — `lead-routing` — demand 127
- **The Intake System** — `data-collection` — demand 111
- **The Onboarding Build** — `client-onboarding` — demand 58
- **The Approval Router** — `approval-routing` — demand 22
- **The Voice Intake** — `voice-agent-intake` — demand 33
- **The Follow Up** — `quote-follow-up` — demand 127
- **The Win-Back** — `reactivation` — demand 58
- **The Watch** — `alerting` — demand 52
- **The Document Build** — `document-assembly` — demand 5
- **The Migration Build** — `platform-migration` — demand 29
- **The Takeover Build** — `production-takeover` — demand 10

---

## The Upsell Engine
`storefront-upsell` · demand **599** · 32 screenshots ready

**What they actually post**

> Bundle Creation on Shopify
> Shopify Developer Needed for Custom Product Bundles and Variant Selection
> Omnisend & Shopify Automation Expert
> Klaviyo Flow Builder & Shopify Plus Specialist

**The pain.** Every order that ships without its obvious companion is margin they already paid to acquire and then left on the table. At any real volume this is the single largest recoverable number in the business.

**How we build it.** Kit `storefront-upsell.json`. Order webhook lands, validate, dedupe on order_id (retries and re-sends are constant in storefront webhooks), rate-limit against the store API, read catalogue plus that customer's order history, then one honest companion or nothing. The restraint is the product: one suggestion, never a second.

**What will bite you.** Storefront platforms re-fire order webhooks on any edit, so dedupe on order_id is load-bearing, not decoration. Never suggest a product already in the cart or already owned — that single mistake reads as spam and is what makes merchants disable these.

**The upsell ladder** — what to walk them through after the first build:

1. post-purchase flow: the second email at day 14 when the consumable runs out
2. win-back for customers who lapsed past their own average reorder gap
3. bundle discovery: which pairs actually convert, fed back into the catalogue
4. inventory guard so we never upsell something about to go out of stock

**The line that lands.** *"I'd start with the companion-product logic because it pays for the build fastest. Here's the workflow that decides whether there's an honest upsell — and stays silent when there isn't."*

**Proof on hand** (`evidence-library/storefront-upsell/`):

- `storefront-upsell--n8n--canvas-ecommerce-order-ops.jpg`
- `storefront-upsell--n8n--kit-canvas-18-nodes.jpg`
- `storefront-upsell--n8n--kit-retry-config.jpg`
- `storefront-upsell--n8n--node-deduplicate-on-order_id.jpg`
- `storefront-upsell--n8n--node-v2-decision-if.jpg`
- `storefront-upsell--n8n--node-v2-gap-report.jpg`
- `storefront-upsell--n8n--node-v2-hold-the-rate-limit.jpg`
- `storefront-upsell--n8n--node-v2-log-the-run-both-paths.jpg`
- `storefront-upsell--n8n--node-validate-what-arrived.jpg`
- `storefront-upsell--shopify--admin-dashboard.jpg`
- `storefront-upsell--shopify--both-companion-mappings.jpg`
- `storefront-upsell--shopify--buy-x-get-y-reward.jpg`
- `storefront-upsell--shopify--buy-x-get-y-trigger.jpg`
- `storefront-upsell--shopify--checkout-settings.jpg`
- `storefront-upsell--shopify--collections-list.jpg`
- `storefront-upsell--shopify--complementary-and-related-config.jpg`
- `storefront-upsell--shopify--discounts-with-companion-upsell.jpg`
- `storefront-upsell--shopify--draft-orders-list.jpg`
- `storefront-upsell--shopify--flow-canvas-upsell-draft.jpg`
- `storefront-upsell--shopify--flow-list-inactive.jpg`
- `storefront-upsell--shopify--inventory-by-location.jpg`
- `storefront-upsell--shopify--order-with-companion-pair.jpg`
- `storefront-upsell--shopify--product-detail.jpg`
- `storefront-upsell--shopify--product-metafields-seo.jpg`
- `storefront-upsell--shopify--products-list-catalogue.jpg`
- `storefront-upsell--shopify--recommendation-performance.jpg`
- `storefront-upsell--shopify--recommendations-after-config.jpg`
- `storefront-upsell--shopify--recommendations-all-products.jpg`
- `storefront-upsell--shopify--rule-based-automated-collection.jpg`
- `storefront-upsell--shopify--saved-complementary-mapping.jpg`
- `storefront-upsell--shopify--search-discovery-settings.jpg`
- `storefront-upsell--shopify--variants-and-inventory.jpg`

---

## The Reconciliation Build
`books-reconciliation` · demand **246** · 49 screenshots ready

**What they actually post**

> AI Automation Developer for Invoice Reconciliation
> Multi-Entity Bookkeeping Cleanup for U.S. LLCs
> NetSuite Integration and Automation Specialist
> GTM Server Side Fix Session Attribution on GA4 (Stripe webhook reconciliation)

**The pain.** Someone is matching payouts to invoices by hand every week and the error only surfaces at month end, when it is expensive and slow to unwind.

**How we build it.** Kit `books-reconciliation.json`. Payout posts, validate, dedupe on payout_id, pull open invoices, match to the cent. Exact matches reconcile silently; anything else is flagged for a human with the delta attached. The scheduled leg reports what is still unreconciled and how old it is.

**What will bite you.** Never auto-reconcile a near-match. A cent of drift is usually a fee or an FX line and a human must rule on it once, after which it becomes a rule. Multi-entity work needs the entity on every row or the totals silently cross-contaminate.

**The upsell ladder** — what to walk them through after the first build:

1. the aged-discrepancy digest, so nothing quietly rots past 30 days
2. fee and FX rules learned from the human's first rulings
3. multi-entity split with per-entity reporting
4. a month-end close pack assembled automatically

**The line that lands.** *"The part that saves the most hours isn't the matching, it's the escalation: only the rows a human must actually judge ever reach a human. Here's that gate."*

**Proof on hand** (`evidence-library/books-reconciliation/`):

- `books-reconciliation--n8n--canvas-books-bridge.jpg`
- `books-reconciliation--n8n--kit-canvas-18-nodes.jpg`
- `books-reconciliation--n8n--kit-retry-config.jpg`
- `books-reconciliation--n8n--node-deduplicate-on-payout_id.jpg`
- `books-reconciliation--n8n--node-v2-decision-if.jpg`
- `books-reconciliation--n8n--node-v2-gap-report.jpg`
- `books-reconciliation--n8n--node-v2-hold-the-rate-limit.jpg`
- `books-reconciliation--n8n--node-v2-log-the-run-both-paths.jpg`
- `books-reconciliation--n8n--node-validate-what-arrived.jpg`
- `books-reconciliation--quickbooks--ar-aging-buckets.jpg`
- `books-reconciliation--quickbooks--ar-aging-summary.jpg`
- `books-reconciliation--quickbooks--ar-aging-total.jpg`
- `books-reconciliation--quickbooks--audit-log-traceability.jpg`
- `books-reconciliation--quickbooks--bank-register-reconcile-status.jpg`
- `books-reconciliation--quickbooks--bank-rule-builder-stripe.jpg`
- `books-reconciliation--quickbooks--bank-rule-saved-active.jpg`
- `books-reconciliation--quickbooks--bank-rules-screen.jpg`
- `books-reconciliation--quickbooks--bank-transactions-match-found.jpg`
- `books-reconciliation--quickbooks--categorize-actions-post-split-rule.jpg`
- `books-reconciliation--quickbooks--categorize-uncategorized-income.jpg`
- `books-reconciliation--quickbooks--chart-of-accounts-variance.jpg`
- `books-reconciliation--quickbooks--customers-open-balances.jpg`
- `books-reconciliation--quickbooks--customers-overdue-total.jpg`
- `books-reconciliation--quickbooks--dashboard-25-to-review.jpg`
- `books-reconciliation--quickbooks--for-review-queue-25-pending.jpg`
- `books-reconciliation--quickbooks--invoice-detail-line-items.jpg`
- `books-reconciliation--quickbooks--invoices-filtered-overdue.jpg`
- `books-reconciliation--quickbooks--invoices-overdue-total.jpg`
- `books-reconciliation--quickbooks--invoices-paid-vs-overdue.jpg`
- `books-reconciliation--quickbooks--journal-entry-debits-credits.jpg`
- `books-reconciliation--quickbooks--match-detail-open-balance.jpg`
- `books-reconciliation--quickbooks--match-proposals-suggested.jpg`
- `books-reconciliation--quickbooks--match-reasoning-panel.jpg`
- `books-reconciliation--quickbooks--match-vs-categorize-toggle.jpg`
- `books-reconciliation--quickbooks--qb-vs-bank-balance-variance.jpg`
- `books-reconciliation--quickbooks--reconcile-balance-form.jpg`
- `books-reconciliation--quickbooks--reconcile-blocked-categorize-first.jpg`
- `books-reconciliation--quickbooks--reconcile-books-to-bank.jpg`
- `books-reconciliation--quickbooks--reconcile-difference-closeup.jpg`
- `books-reconciliation--quickbooks--reconcile-workspace-difference.jpg`
- `books-reconciliation--quickbooks--unpaid-invoice-net30-duedate.jpg`
- `books-reconciliation--stripe--customer-detail-subscription-mrr.jpg`
- `books-reconciliation--stripe--invoice-partially-paid.jpg`
- `books-reconciliation--stripe--invoices-list-all-states.jpg`
- `books-reconciliation--stripe--payment-fee-breakdown-gross-net.jpg`
- `books-reconciliation--stripe--payments-list.jpg`
- `books-reconciliation--stripe--products-and-prices.jpg`
- `books-reconciliation--stripe--subscriptions-list.jpg`
- `books-reconciliation--stripe--unpaid-open-invoice.jpg`

---

## The Booking System
`scheduling` · demand **241** · 19 screenshots ready

**What they actually post**

> Automation Expert Needed – Must Have Experience with JaneApp + HighLevel
> AI Receptionist Developer (booking API integration, multi-location routing)
> Tracking a contact form from GoHighLevel (form and calendar workflow)

**The pain.** No-shows are paid-for demand that evaporates, and most booking setups do nothing between confirmation and the empty chair.

**How we build it.** Kit `scheduling.json` plus the GoHighLevel implementation. Booking lands, check for a real conflict, confirm, remind at 24h and again at 1h, and branch on attendance so a no-show enters recovery instead of disappearing.

**What will bite you.** In GoHighLevel a calendar cannot be created until at least one user is assigned to the sub-account — the error says 'at least one team member is required' and sends you hunting in the wrong place. Task due dates offer Days/Weeks/Months/Years only, no hours, so a same-day callback has to be worded as a one-day task.

**The upsell ladder** — what to walk them through after the first build:

1. no-show recovery with a one-tap rebook link
2. deposit capture on high-value bookings to make the slot cost something
3. multi-location and round-robin routing across staff
4. a weekly utilisation report showing which slots never fill

**The line that lands.** *"Confirmation is the easy half. The money is in the no-show branch — here's what fires when someone doesn't turn up, instead of the slot just being lost."*

**Proof on hand** (`evidence-library/scheduling/`):

- `scheduling--ghl--calendar-availability-mon-fri.jpg`
- `scheduling--ghl--calendar-booking-rules-notice-buffer.jpg`
- `scheduling--ghl--calendar-created-active.jpg`
- `scheduling--ghl--calendar-form-confirmation-consent.jpg`
- `scheduling--ghl--canvas-appointment-reminders-legible.jpg`
- `scheduling--ghl--canvas-appointment-reminders.jpg`
- `scheduling--ghl--wait-until-scheduled-date.jpg`
- `scheduling--google-sheets--trigger-config-time-driven.jpg`
- `scheduling--google-sheets--trigger-saved-list.jpg`
- `scheduling--n8n--canvas-booked-solid.jpg`
- `scheduling--n8n--kit-canvas-18-nodes.jpg`
- `scheduling--n8n--kit-retry-config.jpg`
- `scheduling--n8n--node-deduplicate-on-booking_id.jpg`
- `scheduling--n8n--node-v2-decision-if.jpg`
- `scheduling--n8n--node-v2-gap-report.jpg`
- `scheduling--n8n--node-v2-hold-the-rate-limit.jpg`
- `scheduling--n8n--node-v2-log-the-run-both-paths.jpg`
- `scheduling--n8n--node-validate-what-arrived.jpg`
- `scheduling--quickbooks--recurring-transactions.jpg`

---

## The Reporting Layer
`reporting` · demand **181** · 29 screenshots ready

**What they actually post**

> Build a Self-Hosted Marketing Attribution & Lead Tracking System
> GitHub Actions and Integrate.io Engineer (BigQuery)
> CRM, Data & AI Operations Specialist

**The pain.** The owner cannot answer three basic questions without opening four tools, so they stop asking and run the business on feel.

**How we build it.** Kit `reporting.json`. Gather from every source, and only publish a figure once there is enough data to be honest — below the threshold it prints COLLECTING rather than a zero that reads as fact.

**What will bite you.** A zero that means 'unknown' is the most expensive bug in reporting because it looks like data. Print UNREADABLE or COLLECTING and show the N beside every rate. If a source is down, say so on the page rather than quietly reporting a smaller number.

**The upsell ladder** — what to walk them through after the first build:

1. the daily one-pager into the inbox before coffee
2. trend layer: one immutable row per day, which is what every chart reads
3. anomaly alerts when a number moves more than its normal range
4. per-channel attribution once the trend layer has history

**The line that lands.** *"Every rate on here prints with its N, and nothing compares until there's enough data to mean something. That's the difference between a dashboard and a decoration."*

**Proof on hand** (`evidence-library/reporting/`):

- `reporting--activecampaign--deal-funnel-report.jpg`
- `reporting--airtable--cleaner-score-formula.jpg`
- `reporting--airtable--cleaner-scores-computed.jpg`
- `reporting--airtable--interface-dashboard-evaluations.jpg`
- `reporting--airtable--interface-dashboard.jpg`
- `reporting--airtable--monthly-evaluations-scores.jpg`
- `reporting--ghl--dashboard-opportunity-widgets.jpg`
- `reporting--google-sheets--bulk-order-populated-by-script.jpg`
- `reporting--google-sheets--grouping-and-sum-pass.jpg`
- `reporting--hubspot--dashboard-deals-created-vs-goal.jpg`
- `reporting--hubspot--dashboard-four-charts.jpg`
- `reporting--hubspot--dashboard-pipeline-health.jpg`
- `reporting--n8n--canvas-one-page-truth.jpg`
- `reporting--n8n--kit-canvas-18-nodes.jpg`
- `reporting--n8n--kit-retry-config.jpg`
- `reporting--n8n--node-deduplicate-on-period.jpg`
- `reporting--n8n--node-v2-decision-if.jpg`
- `reporting--n8n--node-v2-gap-report.jpg`
- `reporting--n8n--node-v2-hold-the-rate-limit.jpg`
- `reporting--n8n--node-v2-log-the-run-both-paths.jpg`
- `reporting--n8n--node-validate-what-arrived.jpg`
- `reporting--pipedrive--insights-pipeline-health.jpg`
- `reporting--quickbooks--balance-sheet.jpg`
- `reporting--quickbooks--profit-and-loss-2.jpg`
- `reporting--quickbooks--profit-and-loss.jpg`
- `reporting--quickbooks--standard-reports-list-2.jpg`
- `reporting--quickbooks--standard-reports-list.jpg`
- `reporting--shopify--shopify-analytics-dashboard.jpg`
- `reporting--stripe--billing-mrr-arr.jpg`

---

## The Sync Build
`system-sync` · demand **147** · 20 screenshots ready

**What they actually post**

> Need help with a Pipedrive/Wordpress Form Integration via Zapier
> Workflow Automation & API Integration Specialist (GoHighLevel, Zapier, Boulevard, Avochato)
> Encharge Automation Specialist Full Build + Thinkific/Zapier Integration
> Salesforce AI Integration Consultant

**The pain.** Two systems disagree about the same customer, so staff pick a side and the CRM slowly stops being trusted.

**How we build it.** Kit `system-sync.json`. Record changes, read the far side, and check whether this is our own write echoing back before writing anything. The echo gate is what separates a sync from an infinite loop.

**What will bite you.** Bidirectional sync without echo detection will loop, and it usually loops at 3am against a rate limit. Stamp every write with an origin marker and drop anything carrying your own. Queue rather than drop when the far side is unreachable.

**The upsell ladder** — what to walk them through after the first build:

1. conflict rules for when both sides changed since last sync
2. field-level mapping UI so the client can adjust without you
3. a drift report showing records that disagree anyway
4. a third and fourth system on the same spine

**The line that lands.** *"Here's the node that stops it looping — it checks whether the change coming back is our own write before it touches anything. That's the piece most of these builds are missing."*

**Proof on hand** (`evidence-library/system-sync/`):

- `system-sync--hubspot--connected-apps.jpg`
- `system-sync--hubspot--integrations-connected-apps.jpg`
- `system-sync--instantly--instantly-integrations-api-webhooks.jpg`
- `system-sync--n8n--canvas-two-way-bridge.jpg`
- `system-sync--n8n--kit-canvas-18-nodes.jpg`
- `system-sync--n8n--kit-retry-config.jpg`
- `system-sync--n8n--node-deduplicate-on-record_id.jpg`
- `system-sync--n8n--node-v2-decision-if.jpg`
- `system-sync--n8n--node-v2-gap-report.jpg`
- `system-sync--n8n--node-v2-hold-the-rate-limit.jpg`
- `system-sync--n8n--node-v2-log-the-run-both-paths.jpg`
- `system-sync--n8n--node-validate-what-arrived.jpg`
- `system-sync--quickbooks--integration-connectors.jpg`
- `system-sync--quickbooks--integration-transactions.jpg`
- `system-sync--shopify--shopify-apps-installed.jpg`
- `system-sync--stripe--api-keys-masked.jpg`
- `system-sync--stripe--webhooks.jpg`
- `system-sync--zapier--app-directory-9000-integrations.jpg`
- `system-sync--zapier--canvas-five-step-chain.jpg`
- `system-sync--zapier--canvas-sync-echo-guard.jpg`

---

## The Rescue
`stalled-deal-escalation` · demand **named repeatedly in live postings** · 46 screenshots ready

**What they actually post**

> Pipedrive Specialist needed for a CRM reorganization and improvement
> GoHighLevel Expert Needed – Update Existing Round Robin Assignment
> HubSpot Partner (Long-term, CRM + Ops)

**The pain.** Proposals go quiet and nobody notices for weeks. The deal was never lost on merit, it was lost to silence.

**How we build it.** Kit `approval-routing.json` for the on-hold routing, plus the GoHighLevel build 'SAMPLE - Stalled Deal Rescue: No Movement in 7 Days' — 9 nodes, 3 branches: idle 7 days, fork on stage, alert the owner, create a rescue task, wait 7 more, escalate, and an on-hold path that routes by reason.

**What will bite you.** In GoHighLevel the 'Pipeline stage changed' trigger carries no moved-to-stage filter, so put the stage intent in the workflow name and filter inside the flow. The on-hold path silently fails unless 'allow move to previous stage' is toggled ON in the Create/Update Opportunity action.

**The upsell ladder** — what to walk them through after the first build:

1. escalation ladder: owner at 7 days, manager at 14, principal at 21
2. on-hold reasons that each drive a different next step
3. reactivation campaign for anything dormant past 90 days
4. a stall-reason report showing which stage leaks worst

**The line that lands.** *"Your stalled-proposal problem is the one I'd fix first, because it's the one quietly costing you deals. Here's the workflow that catches an opportunity that hasn't moved in seven days and escalates it before it goes cold."*

**Proof on hand** (`evidence-library/stalled-deal-escalation/`):

- `stalled-deal-escalation--activecampaign--crm-pipeline-deal.jpg`
- `stalled-deal-escalation--ghl--canvas-bottom-escalation.jpg`
- `stalled-deal-escalation--ghl--canvas-top-three-way-fork.jpg`
- `stalled-deal-escalation--ghl--notification-merge-fields.jpg`
- `stalled-deal-escalation--ghl--on-hold-opportunity-update.jpg`
- `stalled-deal-escalation--ghl--opp-board-18-opportunities.jpg`
- `stalled-deal-escalation--ghl--opp-board-closed-won.jpg`
- `stalled-deal-escalation--ghl--opp-board-negotiation.jpg`
- `stalled-deal-escalation--ghl--opp-board-stages-1-5.jpg`
- `stalled-deal-escalation--ghl--opportunities-board-with-stalled-deal.jpg`
- `stalled-deal-escalation--ghl--pipeline-board.jpg`
- `stalled-deal-escalation--ghl--pipeline-stage-dropdown.jpg`
- `stalled-deal-escalation--ghl--pipelines-list-6-stages.jpg`
- `stalled-deal-escalation--ghl--trigger-idle-7-days.jpg`
- `stalled-deal-escalation--ghl--wait-7-days.jpg`
- `stalled-deal-escalation--hubspot--deal-all-properties-stall-reason.jpg`
- `stalled-deal-escalation--hubspot--deal-board-7-stages-12-deals.jpg`
- `stalled-deal-escalation--hubspot--deal-pipeline-board.jpg`
- `stalled-deal-escalation--hubspot--deal-record-stalled.jpg`
- `stalled-deal-escalation--hubspot--deal-table-stages-amounts.jpg`
- `stalled-deal-escalation--hubspot--pipeline-automate-tab.jpg`
- `stalled-deal-escalation--hubspot--pipeline-settings.jpg`
- `stalled-deal-escalation--hubspot--pipelines-overview-tier-cap.jpg`
- `stalled-deal-escalation--hubspot--stage-editor-7-stages-probabilities.jpg`
- `stalled-deal-escalation--hubspot--stage-editor-probabilities.jpg`
- `stalled-deal-escalation--n8n--canvas-ghl-deals-that-stopped-moving.jpg`
- `stalled-deal-escalation--n8n--kit-canvas-18-nodes.jpg`
- `stalled-deal-escalation--n8n--kit-retry-config.jpg`
- `stalled-deal-escalation--n8n--node-deduplicate-on-deal_id.jpg`
- `stalled-deal-escalation--n8n--node-v2-decision-if.jpg`
- `stalled-deal-escalation--n8n--node-v2-gap-report.jpg`
- `stalled-deal-escalation--n8n--node-v2-hold-the-rate-limit.jpg`
- `stalled-deal-escalation--n8n--node-v2-log-the-run-both-paths.jpg`
- `stalled-deal-escalation--n8n--node-validate-what-arrived.jpg`
- `stalled-deal-escalation--pipedrive--automation-canvas-stage-criteria.jpg`
- `stalled-deal-escalation--pipedrive--automation-canvas-time-based.jpg`
- `stalled-deal-escalation--pipedrive--automation-trigger-and-action.jpg`
- `stalled-deal-escalation--pipedrive--filter-applied-board.jpg`
- `stalled-deal-escalation--pipedrive--filter-applied-list.jpg`
- `stalled-deal-escalation--pipedrive--native-rotten-deals-filter.jpg`
- `stalled-deal-escalation--pipedrive--pipeline-board-stages.jpg`
- `stalled-deal-escalation--pipedrive--saved-filter-conditions.jpg`
- `stalled-deal-escalation--pipedrive--stage-rotting-days-per-stage.jpg`
- `stalled-deal-escalation--pipedrive--stage-rotting-saved.jpg`
- `stalled-deal-escalation--zapier--paths-branches-by-stall-reason.jpg`
- `stalled-deal-escalation--zapier--paths-canvas.jpg`

---

## The Lead Router
`lead-routing` · demand **127** · 43 screenshots ready

**What they actually post**

> Gmail Sender Reputation Recovery Specialist (inside GHL)
> ‎GoHighLevel Automation Expert / Smartlead.ai & Zapier Specialist
> AI Automation Specialist for Workflow (HubSpot)
> Need help with GHL and Whatsapp Integration

**The pain.** A lead that waits an hour is worth a fraction of one answered in five minutes, and most teams cannot tell you which of theirs waited.

**How we build it.** Kit workflows plus the GoHighLevel 'SAMPLE - Speed to Lead: 5 Minute Callback' — form submitted, branch on source, SMS with merge fields, wait, and escalate on silence. Round-robin distribution with an SLA timer sits alongside it.

**What will bite you.** GoHighLevel round-robin assignment cannot be configured at all until a user is assigned to the sub-account; the picker just shows 'No Data' and refuses to save. HubSpot's free tier has no branching workflows — the canvas is strictly linear with padlocks on every branch point.

**The upsell ladder** — what to walk them through after the first build:

1. SLA timer with reassignment when the first owner doesn't touch it
2. lead scoring so the best leads route to the best closer
3. WhatsApp or SMS as a first-touch channel alongside email
4. a speed-to-lead report by owner, which is the one that changes behaviour

**The line that lands.** *"Five minutes is the whole game. Here's the routing logic and the SLA timer that reassigns when the first owner doesn't pick it up."*

**Proof on hand** (`evidence-library/lead-routing/`):

- `lead-routing--activecampaign--segment-builder-compound.jpg`
- `lead-routing--activecampaign--segments-list-saved.jpg`
- `lead-routing--ghl--action-picker-contact.jpg`
- `lead-routing--ghl--action-picker-custom-objects.jpg`
- `lead-routing--ghl--assign-user-panel.jpg`
- `lead-routing--ghl--canvas-first-build.jpg`
- `lead-routing--ghl--canvas-round-robin-complete.jpg`
- `lead-routing--ghl--canvas-round-robin-sla.jpg`
- `lead-routing--ghl--canvas-speed-to-lead-full.jpg`
- `lead-routing--ghl--if-else-lead-source.jpg`
- `lead-routing--ghl--round-robin-assign-configured.jpg`
- `lead-routing--ghl--round-robin-assign-panel.jpg`
- `lead-routing--ghl--sms-action-merge-fields.jpg`
- `lead-routing--ghl--sms-body-merge-fields.jpg`
- `lead-routing--ghl--trigger-config-customer-replied.jpg`
- `lead-routing--ghl--trigger-picker-contact.jpg`
- `lead-routing--ghl--trigger-picker-events.jpg`
- `lead-routing--ghl--wait-action-types.jpg`
- `lead-routing--ghl--wait-config-period.jpg`
- `lead-routing--ghl--wait-five-minutes.jpg`
- `lead-routing--hubspot--property-dropdown-routing-tiers.jpg`
- `lead-routing--hubspot--sample-property-in-list.jpg`
- `lead-routing--hubspot--saved-segment-filters-members.jpg`
- `lead-routing--hubspot--segment-builder-compound-and-or.jpg`
- `lead-routing--hubspot--segment-filter-compound-logic.jpg`
- `lead-routing--hubspot--segment-object-picker.jpg`
- `lead-routing--hubspot--segment-review-save.jpg`
- `lead-routing--hubspot--segments-list-with-sample.jpg`
- `lead-routing--hubspot--workflow-send-email-tier-padlocks.jpg`
- `lead-routing--hubspot--workflow-trigger-node.jpg`
- `lead-routing--n8n--canvas-lf-demo-speed-to-lead-full.jpg`
- `lead-routing--n8n--canvas-lf-demo-speed-to-lead-left.png`
- `lead-routing--n8n--canvas-lf-demo-speed-to-lead-right.png`
- `lead-routing--n8n--canvas-speed-to-lead.jpg`
- `lead-routing--n8n--kit-canvas-18-nodes.jpg`
- `lead-routing--n8n--kit-retry-config.jpg`
- `lead-routing--n8n--node-deduplicate-on-lead_id.jpg`
- `lead-routing--n8n--node-v2-decision-if.jpg`
- `lead-routing--n8n--node-v2-gap-report.jpg`
- `lead-routing--n8n--node-v2-hold-the-rate-limit.jpg`
- `lead-routing--n8n--node-v2-log-the-run-both-paths.jpg`
- `lead-routing--n8n--node-validate-what-arrived.jpg`
- `lead-routing--zapier--filter-real-conditions.jpg`

---

## The Intake System
`data-collection` · demand **111** · 53 screenshots ready

**What they actually post**

> Job Fair Website Development
> Next.js + Supabase Portal & CRM
> LogicSheet – Customer Bug Investigation & Fix
> Hubspot Landing Page Specialist

**The pain.** Intake arrives as free text in six formats, so someone retypes it into the CRM and the errors start there.

**How we build it.** Kits `storefront-upsell`/`system-sync` share the intake spine: validate what arrived, refuse malformed input rather than guessing, dedupe, and write a clean record. Form builders in both GoHighLevel and HubSpot are built out with real field types.

**What will bite you.** Validate before you write, and refuse rather than guess — a half-record in the CRM is worse than no record because it looks complete. Dedupe on a stable key, never on name.

**The upsell ladder** — what to walk them through after the first build:

1. enrichment against a data provider on write
2. duplicate detection and merge on the existing base
3. conditional intake that asks fewer questions of better leads
4. a data-quality report on completeness by field

**The line that lands.** *"The validation gate is the part that matters — it refuses a malformed submission instead of writing half a record that looks complete."*

**Proof on hand** (`evidence-library/data-collection/`):

- `data-collection--activecampaign--contacts-sample.jpg`
- `data-collection--activecampaign--form-builder.jpg`
- `data-collection--airtable--dedupe-key-formula-editor.jpg`
- `data-collection--airtable--dedupe-keys-duplicates-visible.jpg`
- `data-collection--airtable--filtered-view-config.jpg`
- `data-collection--airtable--grouped-view-duplicate-pairs.jpg`
- `data-collection--airtable--incident-type-options.jpg`
- `data-collection--airtable--incidents-table-populated.jpg`
- `data-collection--ghl--contact-list-23-records.jpg`
- `data-collection--ghl--contact-list-sample-tags.jpg`
- `data-collection--ghl--contacts-bulk-actions-20-selected.jpg`
- `data-collection--ghl--contacts-smart-list.jpg`
- `data-collection--ghl--contacts-with-tags.jpg`
- `data-collection--ghl--form-builder-six-fields.jpg`
- `data-collection--ghl--form-builder.jpg`
- `data-collection--ghl--funnel-create-options-ai-templates.jpg`
- `data-collection--ghl--funnel-page-editor-builder.jpg`
- `data-collection--ghl--funnel-step-overview-split-test.jpg`
- `data-collection--ghl--funnel-steps-canvas.jpg`
- `data-collection--ghl--sites-funnels-websites-hub.jpg`
- `data-collection--google-sheets--apps-script-dedupe-function.jpg`
- `data-collection--google-sheets--data-validation-config.jpg`
- `data-collection--google-sheets--double-run-guard-lockservice.jpg`
- `data-collection--google-sheets--intake-sheet-populated.jpg`
- `data-collection--google-sheets--line-total-formula.jpg`
- `data-collection--google-sheets--status-dropdown-validation.jpg`
- `data-collection--google-sheets--validate-intake-function.jpg`
- `data-collection--google-sheets--validation-flagged-rows.jpg`
- `data-collection--google-sheets--validation-flagging-logic.jpg`
- `data-collection--hubspot--contacts-filtered-to-sample.jpg`
- `data-collection--hubspot--form-automation-entry.jpg`
- `data-collection--hubspot--form-builder-canvas.jpg`
- `data-collection--hubspot--form-builder-estimate-request.jpg`
- `data-collection--hubspot--form-field-connected-property.jpg`
- `data-collection--hubspot--form-template-gallery.jpg`
- `data-collection--instantly--bulk-insert-format.jpg`
- `data-collection--instantly--lead-import-methods.jpg`
- `data-collection--instantly--lead-list-with-variables.jpg`
- `data-collection--n8n--canvas-list-to-ledger.jpg`
- `data-collection--n8n--canvas-screening-desk.jpg`
- `data-collection--n8n--kit-canvas-18-nodes.jpg`
- `data-collection--n8n--kit-retry-config.jpg`
- `data-collection--n8n--node-deduplicate-on-submission-id.jpg`
- `data-collection--n8n--node-v2-decision-if.jpg`
- `data-collection--n8n--node-v2-gap-report.jpg`
- `data-collection--n8n--node-v2-hold-the-rate-limit.jpg`
- `data-collection--n8n--node-v2-log-the-run-both-paths.jpg`
- `data-collection--n8n--node-validate-what-arrived.jpg`
- `data-collection--shopify--shopify-customers-list.jpg`
- `data-collection--stripe--customers-list.jpg`
- `data-collection--zapier--formatter-clean-fields.jpg`
- `data-collection--zapier--trigger-config.jpg`
- `data-collection--zapier--webhook-trigger-url-masked.jpg`

---

## The Onboarding Build
`client-onboarding` · demand **58** · 23 screenshots ready

**What they actually post**

> ClickUp Expert Needed to Help Venture Studio
> Claude Code Specialist – Automate & Streamline Internal Systems

**The pain.** The first 48 hours set the tone for the engagement, and they are usually improvised.

**How we build it.** Kit `scheduling.json` patterns plus GoHighLevel 'SAMPLE - New Client Onboarding: First 48 Hours' — Won triggers a welcome, a checklist of tasks, a day-one intake reminder, and an owner notification if the intake hasn't come back by day two.

**What will bite you.** Trigger on the status flip to Won, not on stage movement — stage can be dragged back and forth and will re-fire. Make the checklist real tasks with owners, not a message listing steps.

**The upsell ladder** — what to walk them through after the first build:

1. a Day 1 brief assembled for the account owner
2. automatic review request when the engagement completes cleanly
3. client health flag when nobody has heard from them in 10 days
4. an onboarding-completion report

**The line that lands.** *"Here's what fires the moment a deal flips to Won — welcome, checklist, intake, and an escalation if the intake hasn't come back in 48 hours."*

**Proof on hand** (`evidence-library/client-onboarding/`):

- `client-onboarding--ghl--canvas-full-7-nodes.jpg`
- `client-onboarding--ghl--canvas-legible.jpg`
- `client-onboarding--ghl--canvas-review-request-legible.jpg`
- `client-onboarding--ghl--canvas-review-request.jpg`
- `client-onboarding--ghl--condition-named.jpg`
- `client-onboarding--ghl--if-else-expanded.jpg`
- `client-onboarding--ghl--intake-reminder-sms.jpg`
- `client-onboarding--ghl--reputation-reviews-ai-request-settings.jpg`
- `client-onboarding--ghl--trigger-moved-to-won.jpg`
- `client-onboarding--ghl--wait-for-reply-timeout.jpg`
- `client-onboarding--hubspot--landing-page-editor.jpg`
- `client-onboarding--hubspot--landing-page-gallery.jpg`
- `client-onboarding--hubspot--landing-pages-sample-draft.jpg`
- `client-onboarding--hubspot--marketing-email-builder.jpg`
- `client-onboarding--n8n--canvas-lifecycle-engine.jpg`
- `client-onboarding--n8n--kit-canvas-18-nodes.jpg`
- `client-onboarding--n8n--kit-retry-config.jpg`
- `client-onboarding--n8n--node-deduplicate-on-client-id.jpg`
- `client-onboarding--n8n--node-v2-decision-if.jpg`
- `client-onboarding--n8n--node-v2-gap-report.jpg`
- `client-onboarding--n8n--node-v2-hold-the-rate-limit.jpg`
- `client-onboarding--n8n--node-v2-log-the-run-both-paths.jpg`
- `client-onboarding--n8n--node-validate-what-arrived.jpg`

---

## The Approval Router
`approval-routing` · demand **22** · 17 screenshots ready

**What they actually post**

> Pipedrive Specialist (on-hold reasons and automated next steps)
> Twilio Campaign Approval Help

**The pain.** Approvals sit in an inbox with no ladder, so the bottleneck is invisible until someone asks why nothing shipped.

**How we build it.** Kit `approval-routing.json`. Look up the approver by rule, auto-approve inside a band with a recorded reason, route the rest to a named person, escalate on silence, and report weekly on what is still waiting and on whom.

**What will bite you.** Record who approved and why on every auto-approval or the band becomes unauditable and someone will eventually widen it quietly. Escalate on silence — an approval with no timeout is a queue with no exit.

**The upsell ladder** — what to walk them through after the first build:

1. approval bands by amount, category, or client tier
2. delegation and out-of-office fallback
3. a full audit trail export
4. a bottleneck report naming who is slowest

**The line that lands.** *"Every on-hold reason drives a different next step rather than dumping into one bucket. Here's the routing table and the escalation ladder behind it."*

**Proof on hand** (`evidence-library/approval-routing/`):

- `approval-routing--airtable--automation-approval-gate.jpg`
- `approval-routing--airtable--excused-vs-counts-field-config.jpg`
- `approval-routing--airtable--manager-review-queue-view.jpg`
- `approval-routing--airtable--rollup-manager-approval-gate.jpg`
- `approval-routing--n8n--kit-canvas-18-nodes.jpg`
- `approval-routing--n8n--kit-retry-config.jpg`
- `approval-routing--n8n--node-deduplicate-on-request-id.jpg`
- `approval-routing--n8n--node-v2-decision-if.jpg`
- `approval-routing--n8n--node-v2-gap-report.jpg`
- `approval-routing--n8n--node-v2-hold-the-rate-limit.jpg`
- `approval-routing--n8n--node-v2-log-the-run-both-paths.jpg`
- `approval-routing--n8n--node-validate-what-arrived.jpg`
- `approval-routing--pipedrive--automation-canvas-on-hold-branching.jpg`
- `approval-routing--pipedrive--condition-on-hold-reason-changed.jpg`
- `approval-routing--pipedrive--deal-detail-on-hold-activity.jpg`
- `approval-routing--pipedrive--else-branch-action.jpg`
- `approval-routing--pipedrive--on-hold-reason-field-options.jpg`

---

## The Voice Intake
`voice-agent-intake` · demand **33** · 23 screenshots ready

**What they actually post**

> AI Receptionist Developer
> Twilio Segment Developer for Tracking
> Add DNS records from Twilio send grid to our domain

**The pain.** Calls outside business hours go to voicemail, and voicemail is where leads go to die.

**How we build it.** n8n canvases 'Always On Desk' and 'After Hours Line'. Answer, capture intent, route or book, and hand a human the full context rather than a callback number.

**What will bite you.** The fail-safe matters more than the intelligence: when the model is unreachable the caller must get a human path, never silence and never a guess. Log both paths.

**The upsell ladder** — what to walk them through after the first build:

1. booking directly into the calendar from the call
2. multi-location routing by area code or stated location
3. call summary and sentiment into the CRM record
4. a missed-call text-back so no call ends at nothing

**The line that lands.** *"The part I'd point at is the fail-safe — when the model can't answer, the caller gets a human path instead of dead air."*

**Proof on hand** (`evidence-library/voice-agent-intake/`):

- `voice-agent-intake--ghl--voice-ai-actions-transfer-booking-workflow.jpg`
- `voice-agent-intake--ghl--voice-ai-agent-builder-prompt-persona.jpg`
- `voice-agent-intake--ghl--voice-ai-agent-list-not-deployed.jpg`
- `voice-agent-intake--ghl--voice-ai-call-handling-settings.jpg`
- `voice-agent-intake--ghl--voice-ai-create-agent-options.jpg`
- `voice-agent-intake--ghl--voice-ai-deploy-call-routing-hours.jpg`
- `voice-agent-intake--ghl--voice-ai-landing-create-agent.jpg`
- `voice-agent-intake--n8n--canvas-after-hours-line.jpg`
- `voice-agent-intake--n8n--canvas-always-on-desk.jpg`
- `voice-agent-intake--n8n--kit-canvas-18-nodes.jpg`
- `voice-agent-intake--n8n--kit-retry-config.jpg`
- `voice-agent-intake--n8n--node-deduplicate-on-call-id.jpg`
- `voice-agent-intake--n8n--node-v2-decision-if.jpg`
- `voice-agent-intake--n8n--node-v2-gap-report.jpg`
- `voice-agent-intake--n8n--node-v2-hold-the-rate-limit.jpg`
- `voice-agent-intake--n8n--node-v2-log-the-run-both-paths.jpg`
- `voice-agent-intake--n8n--node-validate-what-arrived.jpg`
- `voice-agent-intake--twilio--functions-twiml-runtime.jpg`
- `voice-agent-intake--twilio--messaging-services.jpg`
- `voice-agent-intake--twilio--phone-numbers.jpg`
- `voice-agent-intake--twilio--studio-flow-canvas.jpg`
- `voice-agent-intake--twilio--verify-services.jpg`
- `voice-agent-intake--twilio--widget-config-gather-input.jpg`

---

## The Follow Up
`quote-follow-up` · demand **127** · 15 screenshots ready

**What they actually post**

> Pipedrive Specialist (standard follow-up cadence for active proposals)
> Mailchimp Automation & Email Deliverability Specialist
> Encharge Automation Specialist Full Build

**The pain.** A quote goes out and then nothing happens, because following up is nobody's actual job and everybody assumes someone else did it.

**How we build it.** Kit `quote-follow-up.json` plus the GoHighLevel 'SAMPLE - Quote Follow Up Cadence' — day 2 email, day 5 SMS, day 9 call task, then nurture. The cadence checks for a reply before every touch and stops the moment one lands.

**What will bite you.** Stopping on reply is the whole thing. A cadence that keeps firing after someone answers is worse than no cadence — it actively damages the relationship and it is the single most common bug in these builds.

**The upsell ladder** — what to walk them through after the first build:

1. reply detection that stops the sequence and hands to the owner
2. channel escalation: email, then SMS, then a human call task
3. quote-aging report showing what is unanswered and how old
4. win/loss capture on close so the cadence tunes itself

**The line that lands.** *"Every touch checks for a reply first and the sequence stops dead the moment they answer. That one gate is what separates follow-up from nagging."*

**Proof on hand** (`evidence-library/quote-follow-up/`):

- `quote-follow-up--activecampaign--automation-canvas-branching.jpg`
- `quote-follow-up--activecampaign--reply-gate-condition.jpg`
- `quote-follow-up--ghl--canvas-quote-cadence-full.jpg`
- `quote-follow-up--ghl--canvas-quote-cadence-legible.jpg`
- `quote-follow-up--ghl--email-action-merge-chip.jpg`
- `quote-follow-up--n8n--kit-canvas-18-nodes.jpg`
- `quote-follow-up--n8n--kit-retry-config.jpg`
- `quote-follow-up--n8n--node-deduplicate-on-quote_id.jpg`
- `quote-follow-up--n8n--node-v2-decision-if.jpg`
- `quote-follow-up--n8n--node-v2-gap-report.jpg`
- `quote-follow-up--n8n--node-v2-hold-the-rate-limit.jpg`
- `quote-follow-up--n8n--node-v2-log-the-run-both-paths.jpg`
- `quote-follow-up--n8n--node-validate-what-arrived.jpg`
- `quote-follow-up--pipedrive--activities-list.jpg`
- `quote-follow-up--pipedrive--automation-action-call-in-2-days.jpg`

---

## The Win-Back
`reactivation` · demand **58** · 17 screenshots ready

**What they actually post**

> Klaviyo Flow Builder & Shopify Plus Specialist
> Omnisend & Shopify Automation Expert
> AI Automation Specialist for Workflow

**The pain.** Customers stop buying and nobody notices, because nothing is watching each customer's own normal rhythm.

**How we build it.** Kit `reactivation.json` plus the GoHighLevel 'SAMPLE - Reactivation: Dormant Lead 90 Days'. Work out that customer's normal gap, and only reach out when they are genuinely overdue by their own pattern — not by a blanket 90-day rule.

**What will bite you.** A fixed dormancy window is wrong for almost everyone. Someone who orders monthly is dormant at 60 days; someone who orders annually is not. Compute the gap per customer or the campaign reads as spam.

**The upsell ladder** — what to walk them through after the first build:

1. per-customer dormancy thresholds instead of one global rule
2. one honest win-back, never a series
3. churn-risk scoring before they go quiet at all
4. a recovered-revenue report to prove the build paid

**The line that lands.** *"It doesn't fire on a blanket 90 days. It works out each customer's own normal gap and only reaches out when they're genuinely overdue for them."*

**Proof on hand** (`evidence-library/reactivation/`):

- `reactivation--ghl--canvas-after-sms.jpg`
- `reactivation--ghl--canvas-full-8-nodes.jpg`
- `reactivation--ghl--canvas-legible.jpg`
- `reactivation--ghl--canvas-with-branch.jpg`
- `reactivation--ghl--condition-config.jpg`
- `reactivation--ghl--owner-notification-five-merge-fields.jpg`
- `reactivation--ghl--task-due-date-units.jpg`
- `reactivation--ghl--wait-three-day-timeout.jpg`
- `reactivation--ghl--win-back-sms-merge-field.jpg`
- `reactivation--n8n--kit-canvas-18-nodes.jpg`
- `reactivation--n8n--kit-retry-config.jpg`
- `reactivation--n8n--node-deduplicate-on-customer-id.jpg`
- `reactivation--n8n--node-v2-decision-if.jpg`
- `reactivation--n8n--node-v2-gap-report.jpg`
- `reactivation--n8n--node-v2-hold-the-rate-limit.jpg`
- `reactivation--n8n--node-v2-log-the-run-both-paths.jpg`
- `reactivation--n8n--node-validate-what-arrived.jpg`

---

## The Watch
`alerting` · demand **52** · 15 screenshots ready

**What they actually post**

> AI Agent Workflow Debugging — n8n Production Pipeline
> LogicSheet – Customer Bug Investigation & Fix

**The pain.** Something breaks silently and the business finds out from a customer, which is the most expensive way to learn it.

**How we build it.** Kit `alerting.json`. Watch for a stall, prove the alarm against a planted failure before it ever watches anything real, and put the exact fix inside the alert rather than just the fact of the failure.

**What will bite you.** Test the watchdog on a planted failure first. We have shipped a safety check that would have cried wolf on every single run forever, and only caught it because it was tested against a fake break before a real one. An alert nobody trusts is worse than no alert.

**The upsell ladder** — what to walk them through after the first build:

1. quiet hours with a morning rollup instead of 3am pages
2. the fix included in the alert, not just the symptom
3. escalation when the first alert goes unacknowledged
4. a reliability report showing how many alerts were real

**The line that lands.** *"I test the watchdog against a planted failure before it ever watches anything real, because an alert nobody trusts gets muted and then it may as well not exist."*

**Proof on hand** (`evidence-library/alerting/`):

- `alerting--airtable--automation-complaint-trigger.jpg`
- `alerting--google-sheets--apps-script-executions-log.jpg`
- `alerting--google-sheets--error-handling-try-catch-finally.jpg`
- `alerting--google-sheets--log-timestamped-entries.jpg`
- `alerting--google-sheets--logevent-disabled-email-hook.jpg`
- `alerting--n8n--canvas-watchtower.jpg`
- `alerting--n8n--kit-canvas-18-nodes.jpg`
- `alerting--n8n--kit-retry-config.jpg`
- `alerting--n8n--node-deduplicate-on-job-id.jpg`
- `alerting--n8n--node-v2-decision-if.jpg`
- `alerting--n8n--node-v2-gap-report.jpg`
- `alerting--n8n--node-v2-hold-the-rate-limit.jpg`
- `alerting--n8n--node-v2-log-the-run-both-paths.jpg`
- `alerting--n8n--node-validate-what-arrived.jpg`
- `alerting--zapier--zap-history-autoreplay.jpg`

---

## The Document Build
`document-assembly` · demand **5** · 9 screenshots ready

**What they actually post**

> Document/PDF automation with DocuSign
> Encharge Automation Specialist Full Build + training materials

**The pain.** Documents get assembled by hand from a template, and the one with a blank merge field goes out to a client.

**How we build it.** Kit `document-assembly.json`. Pull the record, assemble from the template, and verify every merge field resolved before anything sends. A document with a hole in it gets held and the missing field is named.

**What will bite you.** Never send a document with an unresolved merge field — check them all and hold the whole thing if one is missing. Binaries do not survive several n8n nodes: on cloud the data is stored by reference, so use getBinaryDataBuffer rather than reading item.binary.data.data, which is empty.

**The upsell ladder** — what to walk them through after the first build:

1. e-signature routing and countersign tracking
2. a version and audit trail per document
3. bulk assembly for onboarding packs
4. an expiry watcher for documents never signed

**The line that lands.** *"It won't send a document with an unresolved field. It holds it and tells you exactly which field is missing, which is the failure mode that actually embarrasses people."*

**Proof on hand** (`evidence-library/document-assembly/`):

- `document-assembly--n8n--canvas-paper-trail.jpg`
- `document-assembly--n8n--kit-canvas-18-nodes.jpg`
- `document-assembly--n8n--kit-retry-config.jpg`
- `document-assembly--n8n--node-deduplicate-on-record-id.jpg`
- `document-assembly--n8n--node-v2-decision-if.jpg`
- `document-assembly--n8n--node-v2-gap-report.jpg`
- `document-assembly--n8n--node-v2-hold-the-rate-limit.jpg`
- `document-assembly--n8n--node-v2-log-the-run-both-paths.jpg`
- `document-assembly--n8n--node-validate-what-arrived.jpg`

---

## The Migration Build
`platform-migration` · demand **29** · 13 screenshots ready

**What they actually post**

> NetSuite Integration and Automation Specialist
> Encharge Automation Specialist Full Build (account rebuild)

**The pain.** Migrations lose records quietly, and nobody finds out until the customer who was lost calls.

**How we build it.** Kit `platform-migration.json`. Reversible batches, counts reconciled exactly before anything commits, and a rollback that reports the delta rather than a partial write.

**What will bite you.** Never delete from the source until the destination count reconciles. Migrate in batches small enough to roll back inside a maintenance window.

**The upsell ladder** — what to walk them through after the first build:

1. a parallel-run period where both systems receive writes
2. field mapping documentation the client keeps
3. post-migration data-quality audit
4. decommission plan for the old system

**The line that lands.** *"Nothing commits until the counts reconcile exactly. If they don't, the batch rolls back and reports the delta instead of half-writing."*

**Proof on hand** (`evidence-library/platform-migration/`):

- `platform-migration--ghl--agency-create-snapshot-form.jpg`
- `platform-migration--ghl--agency-snapshots-list.jpg`
- `platform-migration--hubspot--import-column-mapping-automapped.jpg`
- `platform-migration--hubspot--import-details-step-4.jpg`
- `platform-migration--hubspot--import-summary-26-records-0-errors.jpg`
- `platform-migration--n8n--kit-canvas-18-nodes.jpg`
- `platform-migration--n8n--kit-retry-config.jpg`
- `platform-migration--n8n--node-deduplicate-on-batch-id.jpg`
- `platform-migration--n8n--node-v2-decision-if.jpg`
- `platform-migration--n8n--node-v2-gap-report.jpg`
- `platform-migration--n8n--node-v2-hold-the-rate-limit.jpg`
- `platform-migration--n8n--node-v2-log-the-run-both-paths.jpg`
- `platform-migration--n8n--node-validate-what-arrived.jpg`

---

## The Takeover Build
`production-takeover` · demand **10** · 8 screenshots ready

**What they actually post**

> AI Agent Workflow Debugging — n8n Production Pipeline
> Configuration updates/changes to a web based chat bot

**The pain.** Inheriting someone else's automation means inheriting undocumented behaviour, and the first change breaks something nobody knew depended on it.

**How we build it.** Kit `production-takeover.json`. Probe what the system actually does, compare against what the docs claim, record the surprises, and change nothing until the map is honest.

**What will bite you.** Watch before you touch. The first instinct is to fix the obvious thing, and the obvious thing is usually load-bearing for something undocumented.

**The upsell ladder** — what to walk them through after the first build:

1. full documentation of the inherited system
2. monitoring and alerting the previous build never had
3. a staged rebuild of the worst component
4. a retainer once you know where the bodies are

**The line that lands.** *"I don't change anything in week one. I map what it actually does versus what it's documented to do, and the gap between those two is the real scope."*

**Proof on hand** (`evidence-library/production-takeover/`):

- `production-takeover--n8n--kit-canvas-18-nodes.jpg`
- `production-takeover--n8n--kit-retry-config.jpg`
- `production-takeover--n8n--node-deduplicate-on-job-id.jpg`
- `production-takeover--n8n--node-v2-decision-if.jpg`
- `production-takeover--n8n--node-v2-gap-report.jpg`
- `production-takeover--n8n--node-v2-hold-the-rate-limit.jpg`
- `production-takeover--n8n--node-v2-log-the-run-both-paths.jpg`
- `production-takeover--n8n--node-validate-what-arrived.jpg`

---
