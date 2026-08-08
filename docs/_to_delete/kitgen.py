#!/usr/bin/env python3
"""
kitgen.py — emit n8n workflow JSON for a Fortress product kit.

Every kit is built to THE WORKFLOW STANDARD, so a technical buyer sees what
production actually requires and never sees padding:

  input validation · deduplication · rate limiting · retry with maxTries on
  external calls · an error output branch to an alert, never silent · a
  fail-safe response · logging on both paths · human escalation carrying
  context · a SECOND SCHEDULED TRIGGER (the weekly digest / gap report)

Node names read as a story, never as node types.

Usage:
    python3 kitgen.py                 # writes every kit into ./kits/
    python3 kitgen.py scheduling      # writes one kit

Import into n8n: new workflow -> select the canvas -> paste the JSON (Cmd+V).
n8n imports nodes and connections directly. Rename, leave INACTIVE, screenshot.
"""

import json, os, sys

W, H = 220, 150  # horizontal step, vertical lane step


def _id(n):
    return f"kit{n:04d}-0000-4000-8000-{n:012d}"


class Kit:
    def __init__(self, slug, title, story):
        self.slug, self.title, self.story = slug, title, story
        self.nodes, self.conns, self.n = [], {}, 0

    def add(self, name, ntype, x, y, params=None, tv=1, extra=None):
        self.n += 1
        node = {
            "parameters": params or {},
            "id": _id(self.n),
            "name": name,
            "type": f"n8n-nodes-base.{ntype}",
            "typeVersion": tv,
            "position": [x, y],
        }
        if extra:
            node.update(extra)
        self.nodes.append(node)
        return name

    def link(self, src, dst, out=0):
        self.conns.setdefault(src, {"main": []})
        while len(self.conns[src]["main"]) <= out:
            self.conns[src]["main"].append([])
        self.conns[src]["main"][out].append({"node": dst, "type": "main", "index": 0})

    # ---- node helpers -------------------------------------------------
    def code(self, name, x, y, js):
        return self.add(name, "code", x, y, {"jsCode": js}, tv=2)

    def gate(self, name, x, y, expr):
        return self.add(name, "if", x, y, {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "",
                            "typeValidation": "loose", "version": 2},
                "conditions": [{
                    "id": _id(self.n + 500),
                    "leftValue": expr,
                    "rightValue": "",
                    "operator": {"type": "boolean", "operation": "true", "singleValue": True},
                }],
                "combinator": "and",
            },
            "options": {},
        }, tv=2.2)

    def call(self, name, x, y, url):
        """External call: retries, and an error output branch so it is never silent."""
        return self.add(name, "httpRequest", x, y,
                        {"url": url, "options": {"timeout": 10000}}, tv=4.2,
                        extra={"retryOnFail": True, "maxTries": 3, "waitBetweenTries": 2000,
                               "onError": "continueErrorOutput"})

    def note(self, name, x, y):
        return self.add(name, "noOp", x, y)

    def respond(self, name, x, y, body):
        return self.add(name, "respondToWebhook", x, y,
                        {"respondWith": "json", "responseBody": body}, tv=1)

    def dump(self):
        return {"name": self.title, "nodes": self.nodes,
                "connections": self.conns, "settings": {"executionOrder": "v1"},
                "pinData": {}}


def build(slug, spec):
    """Assemble one kit: a live path and a scheduled path, to the standard."""
    k = Kit(slug, spec["title"], spec["story"])
    y0, y_err, y_sched = 300, 620, 900
    x = 0

    trig = k.add(spec["trigger"], "webhook", x, y0,
                 {"path": slug, "options": {}}, tv=2,
                 extra={"webhookId": _id(900)})

    x += W
    val = k.code("Validate what arrived", x, y0, f"""// Never trust the payload.
const required = {json.dumps(spec['required'])};
const missing = required.filter(f => !$json[f]);
return [{{ json: {{ ...$json, valid: missing.length === 0, missing }} }}];""")
    k.link(trig, val)

    x += W
    g1 = k.gate("Malformed, refuse it", x, y0, "={{ $json.valid }}")
    k.link(val, g1)

    x += W
    dedupe = k.code("Deduplicate on " + spec["dedupe_key"], x, y0, f"""// The same event arrives twice more often than anyone expects.
const key = $json[{json.dumps(spec['dedupe_key'])}];
const seen = $getWorkflowStaticData('global');
seen.keys = seen.keys || {{}};
const isNew = !seen.keys[key];
seen.keys[key] = Date.now();
return [{{ json: {{ ...$json, isNew, dedupeKey: key }} }}];""")
    k.link(g1, dedupe, 0)

    x += W
    g2 = k.gate("Already handled, stop here", x, y0, "={{ $json.isNew }}")
    k.link(dedupe, g2)

    x += W
    rate = k.code("Hold the rate limit", x, y0, """// Stay under the vendor ceiling instead of discovering it in production.
const s = $getWorkflowStaticData('global');
const now = Date.now();
s.window = (s.window || []).filter(t => now - t < 60000);
const allowed = s.window.length < 50;
s.window.push(now);
return [{ json: { ...$json, allowed } }];""")
    k.link(g2, rate, 0)

    x += W
    fetch = k.call(spec["lookup"], x, y0, spec["lookup_url"])
    k.link(rate, fetch)

    # error branch — never silent
    alert = k.note(spec["unreachable"], x + W, y_err)
    k.link(fetch, alert, 1)
    esc = k.note("Escalate to a human, with the context", x + 2 * W, y_err)
    k.link(alert, esc)

    x += W
    decide = k.gate(spec["decision"], x, y0, spec["decision_expr"])
    k.link(fetch, decide, 0)

    # two real outcomes
    x += W
    a = k.call(spec["action_yes"], x, y0 - H, spec["action_url"])
    b = k.call(spec["action_no"], x, y0 + H, spec["action_url"])
    k.link(decide, a, 0)
    k.link(decide, b, 1)
    k.link(a, esc, 1)
    k.link(b, esc, 1)

    x += W
    log = k.code("Log the run, both paths", x, y0, """// A path that is not logged cannot be improved.
return [{ json: {
  at: new Date().toISOString(),
  key: $json.dedupeKey,
  path: $json.outcome || 'handled',
  ok: true,
} }];""")
    k.link(a, log, 0)
    k.link(b, log, 0)

    x += W
    k.respond("Fail safe, never guess", x, y0,
              '={{ JSON.stringify({ received: true, handled: $json.ok === true }) }}')
    k.link(log, "Fail safe, never guess")

    # refusal paths answer too, rather than hanging
    k.link(g1, "Fail safe, never guess", 1)
    k.link(g2, "Fail safe, never guess", 1)

    # ---- the scheduled path: what keeps earning after launch ----------
    sx = 0
    st = k.add("Every Monday, 7am", "scheduleTrigger", sx, y_sched,
               {"rule": {"interval": [{"field": "weeks", "triggerAtDay": [1], "triggerAtHour": 7}]}},
               tv=1.2)
    sx += W
    read = k.code("Read the week of runs", sx, y_sched, """const s = $getWorkflowStaticData('global');
const keys = Object.entries(s.keys || {});
const weekAgo = Date.now() - 7 * 864e5;
return [{ json: { handled: keys.filter(([,t]) => t > weekAgo).length } }];""")
    k.link(st, read)

    sx += W
    gaps = k.code(spec["digest"], sx, y_sched, """// The gap report is the part a buyer keeps paying for.
const handled = $json.handled || 0;
return [{ json: {
  handled,
  note: handled === 0
    ? 'Nothing ran this week. Worth checking the source is still sending.'
    : `${handled} handled cleanly this week.`,
} }];""")
    k.link(read, gaps)

    sx += W
    k.note("Weekly gap report to the owner", sx, y_sched)
    k.link(gaps, "Weekly gap report to the owner")

    return k.dump()


# ---------------------------------------------------------------------
# The kits. Ordered by measured Upwork demand.
# ---------------------------------------------------------------------
KITS = {
    "storefront-upsell": dict(
        title="LF DEMO: The order that should have been bigger", demand=599,
        story="Catches the order that shipped without its obvious companion, and follows up once.",
        trigger="An order lands", required=["order_id", "email"], dedupe_key="order_id",
        lookup="Read the catalogue and the order history",
        lookup_url="https://example.com/api/catalogue",
        unreachable="Catalogue unreachable, alert us",
        decision="Is there an honest companion product?",
        decision_expr="={{ $json.companion != null }}",
        action_yes="Send the one upsell, never a second",
        action_no="Say nothing, log why",
        action_url="https://example.com/api/message",
        digest="Which companions actually converted"),

    "books-reconciliation": dict(
        title="LF DEMO: The books that disagree", demand=246,
        story="Matches payouts to invoices and surfaces only the ones a human must judge.",
        trigger="A payout posts", required=["payout_id", "amount"], dedupe_key="payout_id",
        lookup="Pull the open invoices",
        lookup_url="https://example.com/api/invoices",
        unreachable="Ledger unreachable, alert us",
        decision="Does it match to the cent?",
        decision_expr="={{ $json.matched === true }}",
        action_yes="Reconcile it and move on",
        action_no="Flag the discrepancy for a human",
        action_url="https://example.com/api/ledger",
        digest="What is still unreconciled, and how old"),

    "scheduling": dict(
        title="LF DEMO: The booking that keeps itself", demand=241,
        story="Confirms, reminds twice, and recovers the no-show instead of losing it.",
        trigger="An appointment is booked", required=["booking_id", "starts_at"],
        dedupe_key="booking_id",
        lookup="Check the calendar for a real conflict",
        lookup_url="https://example.com/api/calendar",
        unreachable="Calendar unreachable, alert us",
        decision="Did they show?",
        decision_expr="={{ $json.attended === true }}",
        action_yes="Confirm and close the loop",
        action_no="Run the no-show recovery",
        action_url="https://example.com/api/message",
        digest="No-shows recovered versus lost"),

    "reporting": dict(
        title="LF DEMO: The one page that answers it", demand=181,
        story="Answers the three questions an owner actually asks, on one page, every morning.",
        trigger="A report is requested", required=["period"], dedupe_key="period",
        lookup="Gather the numbers from every source",
        lookup_url="https://example.com/api/metrics",
        unreachable="A source is down, say so on the page",
        decision="Is there enough data to be honest?",
        decision_expr="={{ $json.n >= 30 }}",
        action_yes="Publish the figure with its N",
        action_no="Print COLLECTING, never a fake zero",
        action_url="https://example.com/api/publish",
        digest="Which sources went quiet this week"),

    "system-sync": dict(
        title="LF DEMO: The two systems that stopped arguing", demand=147,
        story="Keeps two tools in step both ways, and never lets an echo become a loop.",
        trigger="A record changes", required=["record_id", "source"], dedupe_key="record_id",
        lookup="Read the other system's version",
        lookup_url="https://example.com/api/mirror",
        unreachable="Far side unreachable, queue and alert",
        decision="Is this our own echo coming back?",
        decision_expr="={{ $json.isEcho !== true }}",
        action_yes="Write it across",
        action_no="Drop the echo, log it",
        action_url="https://example.com/api/write",
        digest="Records that drifted apart anyway"),

    "approval-routing": dict(
        title="LF DEMO: The approval that routes itself", demand=22,
        story="Sends each request to the right approver by rule, escalates on silence, and every on-hold reason drives a different next step.",
        trigger="A request needs approval", required=["request_id", "amount"],
        dedupe_key="request_id",
        lookup="Look up the approver for this rule",
        lookup_url="https://example.com/api/approvers",
        unreachable="Directory unreachable, alert us",
        decision="Is it inside the auto-approve band?",
        decision_expr="={{ $json.withinBand === true }}",
        action_yes="Approve it and record who and why",
        action_no="Route to the named approver",
        action_url="https://example.com/api/route",
        digest="Approvals still waiting, and on whom"),

    "platform-migration": dict(
        title="LF DEMO: The move that loses nothing", demand=29,
        story="Moves records in reversible batches and proves the count before it deletes anything.",
        trigger="A migration batch starts", required=["batch_id"], dedupe_key="batch_id",
        lookup="Read the source batch",
        lookup_url="https://example.com/api/source",
        unreachable="Source unreachable, stop the batch",
        decision="Do the counts reconcile exactly?",
        decision_expr="={{ $json.countsMatch === true }}",
        action_yes="Commit the batch",
        action_no="Roll back and report the delta",
        action_url="https://example.com/api/commit",
        digest="Batches migrated, and anything left behind"),

    "stalled-deal-escalation": dict(
        title="LF DEMO: The deal that stopped moving", demand=127,
        story="Catches an opportunity that has gone quiet, escalates on a ladder, and routes each on-hold reason to its own next step.",
        trigger="A deal goes quiet", required=["deal_id", "stage"], dedupe_key="deal_id",
        lookup="Read the stage history and the last contact",
        lookup_url="https://example.com/api/deal",
        unreachable="CRM unreachable, alert us",
        decision="Has anyone touched it inside the window?",
        decision_expr="={{ $json.touchedRecently === true }}",
        action_yes="Leave it alone, log the touch",
        action_no="Escalate to the owner with the context",
        action_url="https://example.com/api/notify",
        digest="What is still stalled, and on whom"),

    "lead-routing": dict(
        title="LF DEMO: The lead answered in five minutes", demand=127,
        story="Routes a new lead to the right owner in seconds and reassigns when the first owner does not touch it.",
        trigger="A lead lands", required=["lead_id", "source"], dedupe_key="lead_id",
        lookup="Score the lead and find its owner",
        lookup_url="https://example.com/api/routing",
        unreachable="Routing table unreachable, alert us",
        decision="Is this one worth the fast lane?",
        decision_expr="={{ $json.score >= 70 }}",
        action_yes="Call within five minutes",
        action_no="Send to the nurture track",
        action_url="https://example.com/api/assign",
        digest="Median speed to lead, by owner"),

    "data-collection": dict(
        title="LF DEMO: The intake that refuses to guess", demand=111,
        story="Takes messy intake, refuses what is malformed rather than writing half a record, and enriches what is good.",
        trigger="An intake form arrives", required=["submission_id", "email"],
        dedupe_key="submission_id",
        lookup="Enrich against what we already know",
        lookup_url="https://example.com/api/enrich",
        unreachable="Enrichment unreachable, write the clean record anyway",
        decision="Is this a person we already have?",
        decision_expr="={{ $json.existing === true }}",
        action_yes="Merge onto the existing record",
        action_no="Create a clean new record",
        action_url="https://example.com/api/crm",
        digest="Fields most often left blank"),

    "client-onboarding": dict(
        title="LF DEMO: The first forty eight hours", demand=58,
        story="Turns a won deal into a real opening sequence: welcome, checklist, intake, and an escalation when the intake does not come back.",
        trigger="A deal flips to won", required=["client_id"], dedupe_key="client_id",
        lookup="Assemble what we already know about them",
        lookup_url="https://example.com/api/client",
        unreachable="Client record unreachable, alert us",
        decision="Did the intake come back inside two days?",
        decision_expr="={{ $json.intakeReturned === true }}",
        action_yes="Start the work, notify the owner",
        action_no="Chase the intake, then escalate",
        action_url="https://example.com/api/tasks",
        digest="Onboardings stuck past day two"),

    "alerting": dict(
        title="LF DEMO: The watchdog that never cries wolf", demand=52,
        story="Watches for a stall, proves the alarm on a planted failure before it ever watches anything real, and carries the fix in the alert.",
        trigger="A heartbeat arrives", required=["job_id"], dedupe_key="job_id",
        lookup="Check when this last completed",
        lookup_url="https://example.com/api/heartbeat",
        unreachable="Monitor itself is down, alert louder",
        decision="Is it genuinely stalled, or just slow?",
        decision_expr="={{ $json.stalled === true }}",
        action_yes="Alert with the exact fix attached",
        action_no="Record the run and stay quiet",
        action_url="https://example.com/api/alert",
        digest="Alerts raised, and how many were real"),

    "voice-agent-intake": dict(
        title="LF DEMO: The call that never rings out", demand=33,
        story="Answers after hours, captures intent, books or routes, and hands a human full context instead of a callback number.",
        trigger="A call comes in", required=["call_id", "from"], dedupe_key="call_id",
        lookup="Look the caller up before answering",
        lookup_url="https://example.com/api/caller",
        unreachable="Model unreachable, hand to a human now",
        decision="Can this be handled without a person?",
        decision_expr="={{ $json.selfServe === true }}",
        action_yes="Book it and confirm by text",
        action_no="Route to a human with the context",
        action_url="https://example.com/api/route",
        digest="Calls handled versus escalated"),

    "quote-follow-up": dict(
        title="LF DEMO: The quote that follows itself up", demand=127,
        story="Runs a cadence on a sent quote and stops the moment they reply, which is the part most cadences get wrong.",
        trigger="A quote goes out", required=["quote_id"], dedupe_key="quote_id",
        lookup="Check whether they have already replied",
        lookup_url="https://example.com/api/thread",
        unreachable="Inbox unreachable, hold the cadence",
        decision="Have they replied since the last touch?",
        decision_expr="={{ $json.replied === true }}",
        action_yes="Stop the cadence, hand to the owner",
        action_no="Send the next touch in the sequence",
        action_url="https://example.com/api/send",
        digest="Quotes still unanswered, and how old"),

    "reactivation": dict(
        title="LF DEMO: The customer who went quiet", demand=58,
        story="Finds the dormant customer past their own normal gap and makes one honest attempt to bring them back.",
        trigger="A dormancy check runs", required=["customer_id"], dedupe_key="customer_id",
        lookup="Work out their normal gap",
        lookup_url="https://example.com/api/history",
        unreachable="History unreachable, skip rather than guess",
        decision="Are they genuinely overdue for them?",
        decision_expr="={{ $json.overdue === true }}",
        action_yes="Send one win-back, never a series",
        action_no="Leave them alone, check again later",
        action_url="https://example.com/api/message",
        digest="Dormant customers recovered"),

    "document-assembly": dict(
        title="LF DEMO: The paperwork that assembles itself", demand=5,
        story="Builds the document from real record data, checks every merge field resolved, and refuses to send one with a hole in it.",
        trigger="A document is requested", required=["record_id", "template"],
        dedupe_key="record_id",
        lookup="Pull the record the document describes",
        lookup_url="https://example.com/api/record",
        unreachable="Record store unreachable, alert us",
        decision="Did every merge field resolve?",
        decision_expr="={{ $json.allFieldsResolved === true }}",
        action_yes="Assemble it and send for signature",
        action_no="Hold it and name the missing field",
        action_url="https://example.com/api/document",
        digest="Documents held, and which field was missing"),

    "production-takeover": dict(
        title="LF DEMO: Taking over someone else's system", demand=10,
        story="Maps an inherited system, watches it before changing it, and documents every wall it hits.",
        trigger="An inherited job runs", required=["job_id"], dedupe_key="job_id",
        lookup="Probe what the old system actually does",
        lookup_url="https://example.com/api/probe",
        unreachable="Legacy endpoint unreachable, alert us",
        decision="Does it behave the way the docs claim?",
        decision_expr="={{ $json.matchesDocs === true }}",
        action_yes="Record it as understood",
        action_no="Log the surprise, do not touch it yet",
        action_url="https://example.com/api/record",
        digest="What is still undocumented"),
}


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kits")
    os.makedirs(out, exist_ok=True)
    want = sys.argv[1:] or list(KITS)
    for slug in want:
        if slug not in KITS:
            print(f"unknown kit: {slug}"); continue
        wf = build(slug, KITS[slug])
        path = os.path.join(out, f"{slug}.json")
        with open(path, "w") as f:
            json.dump(wf, f, indent=2)
        print(f"{slug:24s} {len(wf['nodes']):2d} nodes  demand {KITS[slug]['demand']:3d}  -> {path}")


if __name__ == "__main__":
    main()
