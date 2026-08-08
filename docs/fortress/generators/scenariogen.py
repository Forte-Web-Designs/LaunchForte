#!/usr/bin/env python3
"""
scenariogen.py — build the n8n workflow behind every scenario in the catalogue.

Why this exists.

The evidence library is 669 shots and 174 of them are n8n canvases, because the
canvas is the shot that does the most work: it is the only picture that shows
the whole cycle at once. A buyer looking at a Klaviyo flow sees Klaviyo. A buyer
looking at the canvas sees what happens when the API times out at 2am.

So every scenario in SCENARIO-CATALOGUE.md gets a workflow here, and every
workflow is built the same way — not because a template is quicker, but because
the parts that cost money are the same every time and a buyer should be able to
see them in the picture:

  validate      a malformed record refuses rather than becoming half a record
  dedupe        the same event arrives twice more often than anyone expects
  rate limit    the vendor ceiling is respected rather than discovered
  the branch    the actual decision the scenario is about
  retry         with an error path, so a failure alerts instead of failing quiet
  log both      the happy path and the sad path both get written down
  the sweep     a second scheduled trigger that keeps finding what nobody noticed

That last one is the difference between an automation and a system, and it is
the node most cheaper quotes leave out.

    python3 scenariogen.py            # write scenario-workflows.json
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "scenario-workflows.json")

# The businesses. One invented company per family, carried across every tool so
# the screenshots read as one estate rather than a pile of unrelated demos.
BIZ = {
    "planner":     "Meridian Paper Co.",
    "restoration": "Halden Restoration",
    "moving":      "Brightline Moving",
    "clinic":      "Cassia Health Group",
    "wholesale":   "Ordway Supply",
}

# scenario key -> (title, shape, business, trigger, the decision, the sweep)
SCENARIOS = [
    ("post-purchase-companion", "Post purchase companion offer", "storefront-upsell", "planner",
     "Order placed", "Does this order already contain the companion?",
     "Sweep: orders from yesterday with no companion offer sent"),

    ("abandoned-checkout", "Abandoned checkout recovery", "storefront-upsell", "planner",
     "Checkout started", "Did the order land within the window?",
     "Sweep: checkouts older than 24h with no order and no email"),

    ("winback-lapsed", "Winback for lapsed buyers", "reactivation", "planner",
     "Nightly at 07:00", "Lapsed past the threshold, and still reachable?",
     "Sweep: profiles that crossed 90 days since the last run"),

    ("welcome-series", "Welcome series with consent check", "client-onboarding", "planner",
     "Subscribed to list", "Did marketing consent actually travel with the profile?",
     "Sweep: profiles added in the last 24h with no consent recorded"),

    ("review-request", "Review request after delivery", "quote-follow-up", "planner",
     "Order fulfilled", "Delivered, and no review request already sent?",
     "Sweep: delivered orders older than 5 days with no request"),

    ("consent-reachability", "Consent and reachability audit", "messaging-compliance", "planner",
     "Weekly, Monday 06:00", "Is this profile on a list it can never be emailed from?",
     "Sweep: every profile, every week, reachable versus subscribed"),

    ("speed-to-lead", "Speed to lead, first touch inside five minutes", "lead-routing", "restoration",
     "New lead", "Is anyone actually assigned, and has the clock started?",
     "Sweep: leads older than 5 minutes with no first touch"),

    ("stalled-deal", "Stalled deal escalation", "stalled-deal-escalation", "restoration",
     "Nightly at 06:30", "Has this deal sat in the same stage past its limit?",
     "Sweep: every open deal, every night, against its stage clock"),

    ("quote-follow-up", "Quote follow up ladder", "quote-follow-up", "restoration",
     "Quote sent", "Has the quote been opened, and has the ladder run out?",
     "Sweep: quotes with no decision after the final step"),

    ("appointment-reminders", "Appointment reminders and confirmations", "scheduling", "clinic",
     "Appointment booked", "Confirmed, or is this heading for a no show?",
     "Sweep: tomorrow's appointments with no confirmation"),

    ("no-show-recovery", "No show recovery", "scheduling", "clinic",
     "Appointment ended", "Did they attend, and is a rebook offer owed?",
     "Sweep: yesterday's appointments with no outcome recorded"),

    ("intake-to-record", "Intake form to a clean record", "data-collection", "moving",
     "Form submitted", "Is this the same person under a different email?",
     "Sweep: records created today with a missing required field"),

    ("client-onboarding", "Client onboarding, kickoff to access", "client-onboarding", "moving",
     "Deal marked won", "Has every access item actually been received?",
     "Sweep: engagements past day three with access still outstanding"),

    ("review-ask-crew", "Review ask after the job closes", "reactivation", "moving",
     "Job closed", "Was the outcome good enough to ask?",
     "Sweep: jobs closed last week with no ask sent"),

    ("invoice-chasing", "Invoice chasing before it ages", "books-reconciliation", "wholesale",
     "Daily at 08:00", "How far past due, and who has already been asked?",
     "Sweep: every open invoice, every morning, by age bucket"),

    ("payment-reconciliation", "Payment matched to invoice", "books-reconciliation", "wholesale",
     "Payment received", "Does this payment match one invoice, or several?",
     "Sweep: unmatched payments older than 48h"),

    ("two-way-sync", "Two way sync with a conflict rule", "system-sync", "wholesale",
     "Record changed, either side", "Which side wrote last, and do they disagree?",
     "Sweep: records whose two sides drifted overnight"),

    ("dedupe-cleanup", "Deduplication with a merge rule", "data-model-architecture", "wholesale",
     "Nightly at 02:00", "Same person, or two people who share a surname?",
     "Sweep: every record pair above the match threshold"),

    ("approval-routing", "Approval routing with a timeout", "approval-routing", "wholesale",
     "Purchase request", "Over the threshold, and who owns the decision?",
     "Sweep: approvals with no answer inside the SLA"),

    ("alerting-watchtower", "Alerting when something goes quiet", "alerting", "wholesale",
     "Every 15 minutes", "Has this integration stopped writing, quietly?",
     "Sweep: every watched surface, every quarter hour"),

    ("reporting-rollup", "Reporting rollup the office can trust", "reporting", "restoration",
     "Daily at 05:00", "Do the two sources agree on the same number?",
     "Sweep: yesterday's figures re-read and compared"),

    ("knowledge-base-rag", "Answering from the knowledge base", "ai-research-agent", "clinic",
     "Question asked", "Is the answer actually in the documents, or is it guessing?",
     "Sweep: re-embed documents changed since the last run"),

    ("voice-intake", "Voice agent intake, write versus flag", "voice-agent-intake", "clinic",
     "Inbound call", "Is the agent allowed to WRITE this, or only flag it?",
     "Sweep: calls with a flagged outcome and no human follow up"),

    ("support-assistant", "Support assistant with a handoff rule", "ai-assistant", "moving",
     "Message received", "Confident enough to answer, or hand to a person?",
     "Sweep: conversations handed off with nobody assigned"),

    ("cold-outreach", "Cold outreach with a reply guard", "cold-outreach", "wholesale",
     "Sequence step due", "Has anyone replied, from any address on the domain?",
     "Sweep: sequences still sending to a domain that replied"),

    ("applicant-flow", "Applicant flow to a shortlist", "data-collection", "moving",
     "Application received", "Does this application clear the hard requirements?",
     "Sweep: applications sitting unreviewed past 48h"),

    ("document-assembly", "Document assembly and signature", "document-assembly", "restoration",
     "Scope approved", "Every field filled, or would this send with a blank?",
     "Sweep: documents sent for signature with no movement"),

    ("platform-migration", "Migration with a verified test batch", "platform-migration", "wholesale",
     "Batch released", "Did the batch come out the same size it went in?",
     "Sweep: batches whose counts do not reconcile"),

    ("inventory-sync", "Inventory and order status", "system-sync", "wholesale",
     "Stock level changed", "Would this oversell against what is really on hand?",
     "Sweep: SKUs whose two systems disagree"),

    ("project-ops", "Project ops, template to workload", "project-ops", "restoration",
     "Project created", "Is anyone over their limit before this is assigned?",
     "Sweep: tasks with no owner past the start date"),
]


def node(name, ntype, x, y, params=None, extra=None):
    n = {"parameters": params or {}, "id": name.lower().replace(" ", "-")[:36],
         "name": name, "type": ntype, "typeVersion": 1, "position": [x, y]}
    if extra:
        n.update(extra)
    return n


def code(name, x, y, body, notes=None):
    n = node(name, "n8n-nodes-base.code", x, y, {"jsCode": body})
    n["typeVersion"] = 2
    if notes:
        n["notes"] = notes
        n["notesInFlow"] = True
    return n


def build(key, title, shape, biz, trigger, decision, sweep):
    """One workflow, laid out left to right, with the sweep on a second row."""
    company = BIZ[biz]
    N, C = [], {}

    def link(a, b, out=0):
        C.setdefault(a, {"main": []})
        while len(C[a]["main"]) <= out:
            C[a]["main"].append([])
        C[a]["main"][out].append({"node": b, "type": "main", "index": 0})

    y0 = 300
    N.append(node(trigger, "n8n-nodes-base.webhook", -420, y0,
                  {"path": key, "options": {}},
                  {"webhookId": key, "notes": company, "notesInFlow": True}))

    N.append(code("Validate or refuse", -200, y0,
                  "// A malformed record must never become half a record.\n"
                  "const REQUIRED = ['id', 'email', 'occurred_at'];\n"
                  "const out = [];\n"
                  "for (const item of $input.all()) {\n"
                  "  const j = item.json || {};\n"
                  "  const missing = REQUIRED.filter(k => !j[k]);\n"
                  "  if (missing.length) {\n"
                  "    out.push({ json: { ...j, _refused: true, _why: 'missing ' + missing.join(', ') } });\n"
                  "    continue;\n"
                  "  }\n"
                  "  out.push({ json: { ...j, _refused: false } });\n"
                  "}\n"
                  "return out;",
                  "Refusals leave here labelled, they do not vanish"))

    N.append(node("Refused?", "n8n-nodes-base.if", 20, y0,
                  {"conditions": {"boolean": [{"value1": "={{ $json._refused }}", "value2": True}]}},
                  {"typeVersion": 2}))

    N.append(code("Seen this already?", 240, y0 - 120,
                  "// The same event arrives twice more often than anyone expects.\n"
                  "const staticData = $getWorkflowStaticData('global');\n"
                  "staticData.seen = staticData.seen || {};\n"
                  "const fresh = [];\n"
                  "for (const item of $input.all()) {\n"
                  "  const key = String(item.json.id) + ':' + String(item.json.occurred_at);\n"
                  "  if (staticData.seen[key]) continue;\n"
                  "  staticData.seen[key] = Date.now();\n"
                  "  fresh.push(item);\n"
                  "}\n"
                  "return fresh;",
                  "Idempotency key, not a timestamp guess"))

    N.append(code("Hold the rate limit", 460, y0 - 120,
                  "// The vendor ceiling is respected here rather than discovered in\n"
                  "// production at the worst possible moment.\n"
                  "const PER_MINUTE = 60;\n"
                  "const items = $input.all();\n"
                  "const batches = [];\n"
                  "for (let i = 0; i < items.length; i += PER_MINUTE) {\n"
                  "  batches.push({ json: { batch: i / PER_MINUTE, size: items.slice(i, i + PER_MINUTE).length,\n"
                  "                          rows: items.slice(i, i + PER_MINUTE).map(x => x.json) } });\n"
                  "}\n"
                  "return batches;"))

    N.append(node(decision[:60], "n8n-nodes-base.if", 700, y0 - 120,
                  {"conditions": {"boolean": [{"value1": "={{ $json.qualifies }}", "value2": True}]}},
                  {"typeVersion": 2, "notes": decision, "notesInFlow": True}))

    N.append(node("Do the thing", "n8n-nodes-base.httpRequest", 940, y0 - 220,
                  {"method": "POST", "url": "https://api.example.com/v1/" + key,
                   "options": {"timeout": 15000}},
                  {"typeVersion": 4, "retryOnFail": True, "maxTries": 3,
                   "waitBetweenTries": 3000, "onError": "continueErrorOutput",
                   "notes": "3 tries, then the error branch", "notesInFlow": True}))

    N.append(code("Write it back", 1180, y0 - 220,
                  "// What was written, onto the record, in the client's own words.\n"
                  "return $input.all().map(i => ({ json: { ...i.json,\n"
                  "  note: 'Automation wrote: ' + (i.json.outcome || 'no change') + ' at ' + new Date().toISOString(),\n"
                  "  written_by: 'n8n', written_at: new Date().toISOString() } }));"))

    N.append(code("Flag, do not write", 940, y0 - 20,
                  "// The decision that shapes the whole build: what the automation is\n"
                  "// allowed to WRITE versus what it may only flag for a person.\n"
                  "return $input.all().map(i => ({ json: { ...i.json,\n"
                  "  flagged: true, reason: i.json.why || 'below the confidence floor',\n"
                  "  assigned_to: 'ops queue' } }));",
                  "An agent that writes with no read back will eventually write something wrong"))

    N.append(code("Log the run, both paths", 1420, y0 - 120,
                  "// Both paths get written down. A run nobody logged is a run nobody\n"
                  "// can explain three weeks later.\n"
                  "return $input.all().map(i => ({ json: {\n"
                  "  run_id: $execution.id, workflow: $workflow.name,\n"
                  "  path: i.json.flagged ? 'flagged' : (i.json.error ? 'error' : 'written'),\n"
                  "  record: i.json.id, at: new Date().toISOString() } }));"))

    N.append(node("Tell somebody", "n8n-nodes-base.httpRequest", 1180, y0 + 140,
                  {"method": "POST", "url": "https://hooks.example.com/alert", "options": {}},
                  {"typeVersion": 4, "notes": "Failure alerts, it does not fail quietly",
                   "notesInFlow": True}))

    N.append(code("Park the refusal", 240, y0 + 160,
                  "// A refused record is parked with its reason, never dropped.\n"
                  "return $input.all().map(i => ({ json: { ...i.json,\n"
                  "  parked_at: new Date().toISOString(), needs: i.json._why } }));"))

    # ---- the second trigger: the sweep -------------------------------------
    N.append(node("Sweep, on a schedule", "n8n-nodes-base.scheduleTrigger", -420, y0 + 380,
                  {"rule": {"interval": [{"field": "hours", "hoursInterval": 1}]}},
                  {"typeVersion": 1, "notes": sweep, "notesInFlow": True}))

    N.append(code("What did nobody notice?", -160, y0 + 380,
                  "// The node most cheaper quotes leave out. The first trigger catches\n"
                  "// what happens; this one catches what did not.\n"
                  "// " + sweep + "\n"
                  "const rows = $input.all().map(i => i.json);\n"
                  "const missed = rows.filter(r => !r.handled_at);\n"
                  "return missed.map(r => ({ json: { ...r, found_by: 'sweep', qualifies: true } }));"))

    link(trigger, "Validate or refuse")
    link("Validate or refuse", "Refused?")
    link("Refused?", "Park the refusal", 0)
    link("Refused?", "Seen this already?", 1)
    link("Seen this already?", "Hold the rate limit")
    link("Hold the rate limit", decision[:60])
    link(decision[:60], "Do the thing", 0)
    link(decision[:60], "Flag, do not write", 1)
    link("Do the thing", "Write it back", 0)
    link("Do the thing", "Tell somebody", 1)
    link("Write it back", "Log the run, both paths")
    link("Flag, do not write", "Log the run, both paths")
    link("Sweep, on a schedule", "What did nobody notice?")
    link("What did nobody notice?", decision[:60])

    return {"name": "LF · " + title + " · " + company,
            "nodes": N, "connections": C,
            "settings": {"executionOrder": "v1"},
            "_meta": {"key": key, "shape": shape, "title": title, "company": company}}


def main():
    out = [build(*s) for s in SCENARIOS]
    json.dump(out, open(OUT, "w"), indent=1)
    shapes = sorted(set(w["_meta"]["shape"] for w in out))
    print("wrote %s: %d workflows, %d nodes each, %d shapes"
          % (os.path.basename(OUT), len(out), len(out[0]["nodes"]), len(shapes)))
    for s in shapes:
        n = [w["_meta"]["title"] for w in out if w["_meta"]["shape"] == s]
        print("  %-28s %d  %s" % (s, len(n), "; ".join(n)[:70]))
    return 0


sys.exit(main())
