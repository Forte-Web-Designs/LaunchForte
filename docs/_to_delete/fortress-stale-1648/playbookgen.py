#!/usr/bin/env python3
"""
playbookgen.py — emit FORTRESS-BUILD-PLAYBOOK.md

One section per product. Each section ties together, for a single pattern:
  the real Upwork ask -> the pain -> the product -> the proof we can show today
  -> how to build it -> the gotchas -> the upsell ladder -> the words to say.

This is the file Fortress reads when a job posting lands. Everything cross-links:
kit JSON (fortress-kits.zip), screenshots (evidence-library/<shape>/), registry
(build-library.json).
"""
import json, os, glob

LIB = "/home/claude/evidence-library"

P = [
dict(shape="storefront-upsell", product="The Upsell Engine", demand=599,
 asks=["Bundle Creation on Shopify",
       "Shopify Developer Needed for Custom Product Bundles and Variant Selection",
       "Omnisend & Shopify Automation Expert",
       "Klaviyo Flow Builder & Shopify Plus Specialist"],
 pain="Every order that ships without its obvious companion is margin they already paid to acquire and then left on the table. At any real volume this is the single largest recoverable number in the business.",
 build="Kit `storefront-upsell.json`. Order webhook lands, validate, dedupe on order_id (retries and re-sends are constant in storefront webhooks), rate-limit against the store API, read catalogue plus that customer's order history, then one honest companion or nothing. The restraint is the product: one suggestion, never a second.",
 gotchas="Storefront platforms re-fire order webhooks on any edit, so dedupe on order_id is load-bearing, not decoration. Never suggest a product already in the cart or already owned — that single mistake reads as spam and is what makes merchants disable these.",
 upsell=["post-purchase flow: the second email at day 14 when the consumable runs out",
         "win-back for customers who lapsed past their own average reorder gap",
         "bundle discovery: which pairs actually convert, fed back into the catalogue",
         "inventory guard so we never upsell something about to go out of stock"],
 say="I'd start with the companion-product logic because it pays for the build fastest. Here's the workflow that decides whether there's an honest upsell — and stays silent when there isn't."),

dict(shape="books-reconciliation", product="The Reconciliation Build", demand=246,
 asks=["AI Automation Developer for Invoice Reconciliation",
       "Multi-Entity Bookkeeping Cleanup for U.S. LLCs",
       "NetSuite Integration and Automation Specialist",
       "GTM Server Side Fix Session Attribution on GA4 (Stripe webhook reconciliation)"],
 pain="Someone is matching payouts to invoices by hand every week and the error only surfaces at month end, when it is expensive and slow to unwind.",
 build="Kit `books-reconciliation.json`. Payout posts, validate, dedupe on payout_id, pull open invoices, match to the cent. Exact matches reconcile silently; anything else is flagged for a human with the delta attached. The scheduled leg reports what is still unreconciled and how old it is.",
 gotchas="Never auto-reconcile a near-match. A cent of drift is usually a fee or an FX line and a human must rule on it once, after which it becomes a rule. Multi-entity work needs the entity on every row or the totals silently cross-contaminate.",
 upsell=["the aged-discrepancy digest, so nothing quietly rots past 30 days",
         "fee and FX rules learned from the human's first rulings",
         "multi-entity split with per-entity reporting",
         "a month-end close pack assembled automatically"],
 say="The part that saves the most hours isn't the matching, it's the escalation: only the rows a human must actually judge ever reach a human. Here's that gate."),

dict(shape="scheduling", product="The Booking System", demand=241,
 asks=["Automation Expert Needed – Must Have Experience with JaneApp + HighLevel",
       "AI Receptionist Developer (booking API integration, multi-location routing)",
       "Tracking a contact form from GoHighLevel (form and calendar workflow)"],
 pain="No-shows are paid-for demand that evaporates, and most booking setups do nothing between confirmation and the empty chair.",
 build="Kit `scheduling.json` plus the GoHighLevel implementation. Booking lands, check for a real conflict, confirm, remind at 24h and again at 1h, and branch on attendance so a no-show enters recovery instead of disappearing.",
 gotchas="In GoHighLevel a calendar cannot be created until at least one user is assigned to the sub-account — the error says 'at least one team member is required' and sends you hunting in the wrong place. Task due dates offer Days/Weeks/Months/Years only, no hours, so a same-day callback has to be worded as a one-day task.",
 upsell=["no-show recovery with a one-tap rebook link",
         "deposit capture on high-value bookings to make the slot cost something",
         "multi-location and round-robin routing across staff",
         "a weekly utilisation report showing which slots never fill"],
 say="Confirmation is the easy half. The money is in the no-show branch — here's what fires when someone doesn't turn up, instead of the slot just being lost."),

dict(shape="reporting", product="The Reporting Layer", demand=181,
 asks=["Build a Self-Hosted Marketing Attribution & Lead Tracking System",
       "GitHub Actions and Integrate.io Engineer (BigQuery)",
       "CRM, Data & AI Operations Specialist"],
 pain="The owner cannot answer three basic questions without opening four tools, so they stop asking and run the business on feel.",
 build="Kit `reporting.json`. Gather from every source, and only publish a figure once there is enough data to be honest — below the threshold it prints COLLECTING rather than a zero that reads as fact.",
 gotchas="A zero that means 'unknown' is the most expensive bug in reporting because it looks like data. Print UNREADABLE or COLLECTING and show the N beside every rate. If a source is down, say so on the page rather than quietly reporting a smaller number.",
 upsell=["the daily one-pager into the inbox before coffee",
         "trend layer: one immutable row per day, which is what every chart reads",
         "anomaly alerts when a number moves more than its normal range",
         "per-channel attribution once the trend layer has history"],
 say="Every rate on here prints with its N, and nothing compares until there's enough data to mean something. That's the difference between a dashboard and a decoration."),

dict(shape="system-sync", product="The Sync Build", demand=147,
 asks=["Need help with a Pipedrive/Wordpress Form Integration via Zapier",
       "Workflow Automation & API Integration Specialist (GoHighLevel, Zapier, Boulevard, Avochato)",
       "Encharge Automation Specialist Full Build + Thinkific/Zapier Integration",
       "Salesforce AI Integration Consultant"],
 pain="Two systems disagree about the same customer, so staff pick a side and the CRM slowly stops being trusted.",
 build="Kit `system-sync.json`. Record changes, read the far side, and check whether this is our own write echoing back before writing anything. The echo gate is what separates a sync from an infinite loop.",
 gotchas="Bidirectional sync without echo detection will loop, and it usually loops at 3am against a rate limit. Stamp every write with an origin marker and drop anything carrying your own. Queue rather than drop when the far side is unreachable.",
 upsell=["conflict rules for when both sides changed since last sync",
         "field-level mapping UI so the client can adjust without you",
         "a drift report showing records that disagree anyway",
         "a third and fourth system on the same spine"],
 say="Here's the node that stops it looping — it checks whether the change coming back is our own write before it touches anything. That's the piece most of these builds are missing."),

dict(shape="stalled-deal-escalation", product="The Rescue", demand="named repeatedly in live postings",
 asks=["Pipedrive Specialist needed for a CRM reorganization and improvement",
       "GoHighLevel Expert Needed – Update Existing Round Robin Assignment",
       "HubSpot Partner (Long-term, CRM + Ops)"],
 pain="Proposals go quiet and nobody notices for weeks. The deal was never lost on merit, it was lost to silence.",
 build="Kit `approval-routing.json` for the on-hold routing, plus the GoHighLevel build 'SAMPLE - Stalled Deal Rescue: No Movement in 7 Days' — 9 nodes, 3 branches: idle 7 days, fork on stage, alert the owner, create a rescue task, wait 7 more, escalate, and an on-hold path that routes by reason.",
 gotchas="In GoHighLevel the 'Pipeline stage changed' trigger carries no moved-to-stage filter, so put the stage intent in the workflow name and filter inside the flow. The on-hold path silently fails unless 'allow move to previous stage' is toggled ON in the Create/Update Opportunity action.",
 upsell=["escalation ladder: owner at 7 days, manager at 14, principal at 21",
         "on-hold reasons that each drive a different next step",
         "reactivation campaign for anything dormant past 90 days",
         "a stall-reason report showing which stage leaks worst"],
 say="Your stalled-proposal problem is the one I'd fix first, because it's the one quietly costing you deals. Here's the workflow that catches an opportunity that hasn't moved in seven days and escalates it before it goes cold."),

dict(shape="lead-routing", product="The Lead Router", demand=127,
 asks=["Gmail Sender Reputation Recovery Specialist (inside GHL)",
       "‎GoHighLevel Automation Expert / Smartlead.ai & Zapier Specialist",
       "AI Automation Specialist for Workflow (HubSpot)",
       "Need help with GHL and Whatsapp Integration"],
 pain="A lead that waits an hour is worth a fraction of one answered in five minutes, and most teams cannot tell you which of theirs waited.",
 build="Kit workflows plus the GoHighLevel 'SAMPLE - Speed to Lead: 5 Minute Callback' — form submitted, branch on source, SMS with merge fields, wait, and escalate on silence. Round-robin distribution with an SLA timer sits alongside it.",
 gotchas="GoHighLevel round-robin assignment cannot be configured at all until a user is assigned to the sub-account; the picker just shows 'No Data' and refuses to save. HubSpot's free tier has no branching workflows — the canvas is strictly linear with padlocks on every branch point.",
 upsell=["SLA timer with reassignment when the first owner doesn't touch it",
         "lead scoring so the best leads route to the best closer",
         "WhatsApp or SMS as a first-touch channel alongside email",
         "a speed-to-lead report by owner, which is the one that changes behaviour"],
 say="Five minutes is the whole game. Here's the routing logic and the SLA timer that reassigns when the first owner doesn't pick it up."),

dict(shape="data-collection", product="The Intake System", demand=111,
 asks=["Job Fair Website Development", "Next.js + Supabase Portal & CRM",
       "LogicSheet – Customer Bug Investigation & Fix", "Hubspot Landing Page Specialist"],
 pain="Intake arrives as free text in six formats, so someone retypes it into the CRM and the errors start there.",
 build="Kits `storefront-upsell`/`system-sync` share the intake spine: validate what arrived, refuse malformed input rather than guessing, dedupe, and write a clean record. Form builders in both GoHighLevel and HubSpot are built out with real field types.",
 gotchas="Validate before you write, and refuse rather than guess — a half-record in the CRM is worse than no record because it looks complete. Dedupe on a stable key, never on name.",
 upsell=["enrichment against a data provider on write",
         "duplicate detection and merge on the existing base",
         "conditional intake that asks fewer questions of better leads",
         "a data-quality report on completeness by field"],
 say="The validation gate is the part that matters — it refuses a malformed submission instead of writing half a record that looks complete."),

dict(shape="client-onboarding", product="The Onboarding Build", demand=58,
 asks=["ClickUp Expert Needed to Help Venture Studio",
       "Claude Code Specialist – Automate & Streamline Internal Systems"],
 pain="The first 48 hours set the tone for the engagement, and they are usually improvised.",
 build="Kit `scheduling.json` patterns plus GoHighLevel 'SAMPLE - New Client Onboarding: First 48 Hours' — Won triggers a welcome, a checklist of tasks, a day-one intake reminder, and an owner notification if the intake hasn't come back by day two.",
 gotchas="Trigger on the status flip to Won, not on stage movement — stage can be dragged back and forth and will re-fire. Make the checklist real tasks with owners, not a message listing steps.",
 upsell=["a Day 1 brief assembled for the account owner",
         "automatic review request when the engagement completes cleanly",
         "client health flag when nobody has heard from them in 10 days",
         "an onboarding-completion report"],
 say="Here's what fires the moment a deal flips to Won — welcome, checklist, intake, and an escalation if the intake hasn't come back in 48 hours."),

dict(shape="approval-routing", product="The Approval Router", demand=22,
 asks=["Pipedrive Specialist (on-hold reasons and automated next steps)",
       "Twilio Campaign Approval Help"],
 pain="Approvals sit in an inbox with no ladder, so the bottleneck is invisible until someone asks why nothing shipped.",
 build="Kit `approval-routing.json`. Look up the approver by rule, auto-approve inside a band with a recorded reason, route the rest to a named person, escalate on silence, and report weekly on what is still waiting and on whom.",
 gotchas="Record who approved and why on every auto-approval or the band becomes unauditable and someone will eventually widen it quietly. Escalate on silence — an approval with no timeout is a queue with no exit.",
 upsell=["approval bands by amount, category, or client tier",
         "delegation and out-of-office fallback",
         "a full audit trail export",
         "a bottleneck report naming who is slowest"],
 say="Every on-hold reason drives a different next step rather than dumping into one bucket. Here's the routing table and the escalation ladder behind it."),

dict(shape="voice-agent-intake", product="The Voice Intake", demand=33,
 asks=["AI Receptionist Developer", "Twilio Segment Developer for Tracking",
       "Add DNS records from Twilio send grid to our domain"],
 pain="Calls outside business hours go to voicemail, and voicemail is where leads go to die.",
 build="n8n canvases 'Always On Desk' and 'After Hours Line'. Answer, capture intent, route or book, and hand a human the full context rather than a callback number.",
 gotchas="The fail-safe matters more than the intelligence: when the model is unreachable the caller must get a human path, never silence and never a guess. Log both paths.",
 upsell=["booking directly into the calendar from the call",
         "multi-location routing by area code or stated location",
         "call summary and sentiment into the CRM record",
         "a missed-call text-back so no call ends at nothing"],
 say="The part I'd point at is the fail-safe — when the model can't answer, the caller gets a human path instead of dead air."),

dict(shape="quote-follow-up", product="The Follow Up", demand=127,
 asks=["Pipedrive Specialist (standard follow-up cadence for active proposals)",
       "Mailchimp Automation & Email Deliverability Specialist",
       "Encharge Automation Specialist Full Build"],
 pain="A quote goes out and then nothing happens, because following up is nobody's actual job and everybody assumes someone else did it.",
 build="Kit `quote-follow-up.json` plus the GoHighLevel 'SAMPLE - Quote Follow Up Cadence' — day 2 email, day 5 SMS, day 9 call task, then nurture. The cadence checks for a reply before every touch and stops the moment one lands.",
 gotchas="Stopping on reply is the whole thing. A cadence that keeps firing after someone answers is worse than no cadence — it actively damages the relationship and it is the single most common bug in these builds.",
 upsell=["reply detection that stops the sequence and hands to the owner",
         "channel escalation: email, then SMS, then a human call task",
         "quote-aging report showing what is unanswered and how old",
         "win/loss capture on close so the cadence tunes itself"],
 say="Every touch checks for a reply first and the sequence stops dead the moment they answer. That one gate is what separates follow-up from nagging."),

dict(shape="reactivation", product="The Win-Back", demand=58,
 asks=["Klaviyo Flow Builder & Shopify Plus Specialist",
       "Omnisend & Shopify Automation Expert",
       "AI Automation Specialist for Workflow"],
 pain="Customers stop buying and nobody notices, because nothing is watching each customer's own normal rhythm.",
 build="Kit `reactivation.json` plus the GoHighLevel 'SAMPLE - Reactivation: Dormant Lead 90 Days'. Work out that customer's normal gap, and only reach out when they are genuinely overdue by their own pattern — not by a blanket 90-day rule.",
 gotchas="A fixed dormancy window is wrong for almost everyone. Someone who orders monthly is dormant at 60 days; someone who orders annually is not. Compute the gap per customer or the campaign reads as spam.",
 upsell=["per-customer dormancy thresholds instead of one global rule",
         "one honest win-back, never a series",
         "churn-risk scoring before they go quiet at all",
         "a recovered-revenue report to prove the build paid"],
 say="It doesn't fire on a blanket 90 days. It works out each customer's own normal gap and only reaches out when they're genuinely overdue for them."),

dict(shape="alerting", product="The Watch", demand=52,
 asks=["AI Agent Workflow Debugging — n8n Production Pipeline",
       "LogicSheet – Customer Bug Investigation & Fix"],
 pain="Something breaks silently and the business finds out from a customer, which is the most expensive way to learn it.",
 build="Kit `alerting.json`. Watch for a stall, prove the alarm against a planted failure before it ever watches anything real, and put the exact fix inside the alert rather than just the fact of the failure.",
 gotchas="Test the watchdog on a planted failure first. We have shipped a safety check that would have cried wolf on every single run forever, and only caught it because it was tested against a fake break before a real one. An alert nobody trusts is worse than no alert.",
 upsell=["quiet hours with a morning rollup instead of 3am pages",
         "the fix included in the alert, not just the symptom",
         "escalation when the first alert goes unacknowledged",
         "a reliability report showing how many alerts were real"],
 say="I test the watchdog against a planted failure before it ever watches anything real, because an alert nobody trusts gets muted and then it may as well not exist."),

dict(shape="document-assembly", product="The Document Build", demand=5,
 asks=["Document/PDF automation with DocuSign",
       "Encharge Automation Specialist Full Build + training materials"],
 pain="Documents get assembled by hand from a template, and the one with a blank merge field goes out to a client.",
 build="Kit `document-assembly.json`. Pull the record, assemble from the template, and verify every merge field resolved before anything sends. A document with a hole in it gets held and the missing field is named.",
 gotchas="Never send a document with an unresolved merge field — check them all and hold the whole thing if one is missing. Binaries do not survive several n8n nodes: on cloud the data is stored by reference, so use getBinaryDataBuffer rather than reading item.binary.data.data, which is empty.",
 upsell=["e-signature routing and countersign tracking",
         "a version and audit trail per document",
         "bulk assembly for onboarding packs",
         "an expiry watcher for documents never signed"],
 say="It won't send a document with an unresolved field. It holds it and tells you exactly which field is missing, which is the failure mode that actually embarrasses people."),

dict(shape="platform-migration", product="The Migration Build", demand=29,
 asks=["NetSuite Integration and Automation Specialist",
       "Encharge Automation Specialist Full Build (account rebuild)"],
 pain="Migrations lose records quietly, and nobody finds out until the customer who was lost calls.",
 build="Kit `platform-migration.json`. Reversible batches, counts reconciled exactly before anything commits, and a rollback that reports the delta rather than a partial write.",
 gotchas="Never delete from the source until the destination count reconciles. Migrate in batches small enough to roll back inside a maintenance window.",
 upsell=["a parallel-run period where both systems receive writes",
         "field mapping documentation the client keeps",
         "post-migration data-quality audit",
         "decommission plan for the old system"],
 say="Nothing commits until the counts reconcile exactly. If they don't, the batch rolls back and reports the delta instead of half-writing."),

dict(shape="production-takeover", product="The Takeover Build", demand=10,
 asks=["AI Agent Workflow Debugging — n8n Production Pipeline",
       "Configuration updates/changes to a web based chat bot"],
 pain="Inheriting someone else's automation means inheriting undocumented behaviour, and the first change breaks something nobody knew depended on it.",
 build="Kit `production-takeover.json`. Probe what the system actually does, compare against what the docs claim, record the surprises, and change nothing until the map is honest.",
 gotchas="Watch before you touch. The first instinct is to fix the obvious thing, and the obvious thing is usually load-bearing for something undocumented.",
 upsell=["full documentation of the inherited system",
         "monitoring and alerting the previous build never had",
         "a staged rebuild of the worst component",
         "a retainer once you know where the bodies are"],
 say="I don't change anything in week one. I map what it actually does versus what it's documented to do, and the gap between those two is the real scope."),
]


def shots(shape):
    d = os.path.join(LIB, shape)
    if not os.path.isdir(d):
        return []
    return sorted(os.path.basename(f) for f in glob.glob(d + "/*") )


def main():
    L = []
    w = L.append
    w("# Fortress build playbook")
    w("A job posting lands. Find its pattern here. Everything you need is in the section:")
    w("the real ask, the pain, the product, the proof to send, how to build it, what will bite you,")
    w("and where the money is after the first invoice.\n")
    w("Cross-references: kit JSON in `fortress-kits.zip` · screenshots in `evidence-library/<shape>/`")
    w("· registry in `build-library.json` · method in `PRODUCT-KIT-STANDARD.md`\n")
    w("Every screenshot listed is a real file. Every ask quoted is a real posting from the")
    w("Command Center's live Upwork feed.\n")
    w("---\n")
    w("## Index\n")
    for p in P:
        w(f"- **{p['product']}** — `{p['shape']}` — demand {p['demand']}")
    w("\n---\n")

    for p in P:
        s = shots(p["shape"])
        w(f"## {p['product']}")
        w(f"`{p['shape']}` · demand **{p['demand']}** · {len(s)} screenshots ready\n")
        w("**What they actually post**\n")
        for a in p["asks"]:
            w(f"> {a}")
        w("")
        w(f"**The pain.** {p['pain']}\n")
        w(f"**How we build it.** {p['build']}\n")
        w(f"**What will bite you.** {p['gotchas']}\n")
        w("**The upsell ladder** — what to walk them through after the first build:\n")
        for i, u in enumerate(p["upsell"], 1):
            w(f"{i}. {u}")
        w("")
        w(f"**The line that lands.** *\"{p['say']}\"*\n")
        if s:
            w("**Proof on hand** (`evidence-library/" + p["shape"] + "/`):\n")
            for f in s:
                w(f"- `{f}`")
        else:
            w("**Proof on hand:** none yet — this shape still needs capture.")
        w("\n---\n")

    out = "/home/claude/FORTRESS-BUILD-PLAYBOOK.md"
    open(out, "w").write("\n".join(L))
    total = sum(len(shots(p["shape"])) for p in P)
    print(f"wrote {out}: {len(P)} products, {total} screenshots referenced")


main()
