#!/usr/bin/env python3
"""
heroes.py — emit SEND-THIS.md

The library is a reservoir: every shot we hold, so that ANY scenario has something.
This picks the 3-4 to actually attach for each pattern, in order, with the
line to say. Nobody sends 40 images to an Upwork client.

The send order is always the same four beats, because it is the argument:
  1. THE SYSTEM      — the n8n canvas. Proves it is engineered, not clicked.
  2. THE THINKING    — one node close-up. Proves depth behind the diagram.
  3. THEIR WORLD     — the same pattern inside a real CRM/store/ledger.
  4. THE RESULT      — the board, the record, the number. Proves it lands.
"""
import os, json, re

LIB = "/home/claude/evidence-library"

# per shape: the product name, the opening line, and how to introduce each beat
SHAPES = {
"stalled-deal-escalation": dict(
  product="The Rescue",
  open="Your stalled-proposal problem is the one I'd fix first, because it's the one quietly costing you deals.",
  beats=["Here's the system that watches for a deal that hasn't moved and escalates before it goes cold.",
         "This is the gate underneath it — it checks whether anyone actually touched the deal, not just whether time passed.",
         "The same pattern inside the CRM itself — the escalation branch, with the owner and the manager step both wired.",
         "And this is what it looks like once it's running — every stage worked, and the stalled one flagged rather than forgotten."]),
"lead-routing": dict(
  product="The Lead Router",
  open="Five minutes is the whole game. A lead that waits an hour is worth a fraction of one answered fast.",
  beats=["Here's the routing system end to end — score, assign, contact, and escalate on silence.",
         "The part most builds miss is the SLA timer: this reassigns when the first owner doesn't touch it.",
         "Same pattern running inside a real CRM, with the merge fields and the branch on lead source.",
         "And the segmentation behind it, so the right leads reach the right closer."]),
"books-reconciliation": dict(
  beat2="report",
  product="The Reconciliation Build",
  open="The hours don't go into the matching. They go into the handful of rows a human has to judge.",
  beats=["Here's the system: payouts in, matched to the cent, and only the exceptions reach a person.",
         "This is what it reports weekly — what's still unreconciled and how old, because that's the number that turns into a month-end problem.",
         "The same logic inside QuickBooks — a rule that encodes the ruling once instead of every week.",
         "And the variance it's built to close: the ledger and the bank disagreeing, in one frame."]),
"storefront-upsell": dict(
  product="The Upsell Engine",
  open="Every order that ships without its obvious companion is margin you already paid to acquire.",
  beats=["Here's the system that decides whether there's an honest companion — and stays silent when there isn't.",
         "The restraint is the product: one suggestion, never a second, and never something they already own.",
         "Running inside Shopify, with the companion mapping configured against the real catalogue.",
         "And the cross-sell rule firing on the order itself."]),
"scheduling": dict(
  product="The Booking System",
  open="Confirmation is the easy half. The money is in what happens when someone doesn't turn up.",
  beats=["Here's the full sequence — confirm, remind twice, and branch on attendance.",
         "This is the no-show recovery path, which is the part that pays for the build.",
         "The same pattern inside a real booking system, with availability and buffers configured.",
         "And the reminder cadence timed against the appointment rather than a fixed delay."]),
"reporting": dict(
  product="The Reporting Layer",
  open="Most dashboards lie by omission. A zero that means 'unknown' looks exactly like a zero that means zero.",
  beats=["Here's the system that gathers from every source and only publishes once there's enough data to be honest.",
         "Below the threshold it prints COLLECTING rather than a number that reads as fact.",
         "The reporting layer running live on real records.",
         "And the same layer on a second stack — the numbers move, the structure does not."]),
"system-sync": dict(
  product="The Sync Build",
  open="Two systems disagreeing about the same customer is how a CRM quietly stops being trusted.",
  beats=["Here's the two-way sync, with the echo gate that stops it looping at 3am.",
         "This is the node that checks whether the change coming back is our own write. Most builds are missing it.",
         "The integration layer in place on a live stack.",
         "And the connectors it reconciles across."]),
"client-onboarding": dict(
  product="The Onboarding Build",
  open="The first 48 hours set the tone for the whole engagement, and they're usually improvised.",
  beats=["Here's what fires the moment a deal flips to Won — welcome, checklist, intake, escalation.",
         "It escalates if the intake hasn't come back by day two, rather than waiting for someone to notice.",
         "Running in the CRM, triggered on the status change rather than a stage drag.",
         "And the onboarding assets it assembles."]),
"data-collection": dict(
  product="The Intake System",
  open="A half-record in the CRM is worse than no record, because it looks complete.",
  beats=["Here's the intake spine: validate, refuse what's malformed, dedupe, then write a clean record.",
         "The validation gate is the part that matters — it refuses rather than guessing.",
         "The intake form itself, with real field types bound to CRM properties.",
         "And the records it produces, clean and deduplicated."]),
"quote-follow-up": dict(
  product="The Follow Up",
  open="Following up on a quote is nobody's actual job, so it quietly becomes nobody's.",
  beats=["Here's the cadence — day 2, day 5, day 9, then nurture.",
         "Every touch checks for a reply first and stops dead the moment they answer. That gate is what separates follow-up from nagging.",
         "The same cadence inside the CRM, with the real message copy.",
         "And what it reports: which quotes are unanswered and how old."]),
"reactivation": dict(
  product="The Win-Back",
  open="Customers stop buying and nobody notices, because nothing is watching their own rhythm.",
  beats=["Here's the win-back, keyed on each customer's normal gap rather than a blanket 90 days.",
         "One honest message, never a series — that's what keeps it out of the spam folder.",
         "Running in the CRM against real dormancy signals.",
         "And the branch that stops the moment someone replies."]),
"approval-routing": dict(
  product="The Approval Router",
  open="Approvals sit in an inbox with no ladder, so the bottleneck is invisible until someone asks why nothing shipped.",
  beats=["Here's the router: auto-approve inside a band, route the rest by rule, escalate on silence.",
         "Every auto-approval records who and why, or the band becomes unauditable.",
         "The stage and approval configuration inside a real CRM.",
         "And the weekly report naming who's actually holding things up."]),
"alerting": dict(
  product="The Watch",
  open="Something breaks silently and the business hears it from a customer. That's the most expensive way to find out.",
  beats=["Here's the watchdog, with the exact fix carried inside the alert rather than just the symptom.",
         "It's tested against a planted failure before it ever watches anything real — an alert nobody trusts gets muted.",
         "The alerting path in the CRM, escalating with context.",
         "And the precision check: how many alerts were actually real."]),
"platform-migration": dict(
  product="The Migration Build",
  open="Migrations lose records quietly. Nobody finds out until the customer who was lost calls.",
  beats=["Here's the migration: reversible batches, counts reconciled before anything commits.",
         "If the counts don't match, the batch rolls back and reports the delta instead of half-writing.",
         "A real import with the field mapping resolved.",
         "And the result — records in, associations intact, zero errors."]),
"production-takeover": dict(
  product="The Takeover Build",
  open="I don't change anything in week one. I map what it actually does versus what it's documented to do.",
  beats=["Here's the probe: watch the inherited system, record every surprise, change nothing yet.",
         "The gap between documented and observed behaviour is the real scope.",
         "Every external call retries on its own terms rather than inheriting one blanket rule — an inherited system tells you which calls it can survive being hit twice.",
         "And both paths get logged, the good one and the failed one, because week one is worth nothing if the evidence isn't written down."]),
"voice-agent-intake": dict(
  product="The Voice Intake",
  open="Calls outside business hours go to voicemail, and voicemail is where leads go to die.",
  beats=["Here's the after-hours desk — answer, capture intent, book or route.",
         "The fail-safe matters more than the intelligence: when the model can't answer, the caller gets a human, never dead air.",
         "The agent itself inside the tool — persona, prompt, and what it's allowed to say.",
         "And the deployment side: which number it answers, which hours, and where the call goes when it hands over."]),
"document-assembly": dict(
  product="The Document Build",
  open="The document with a blank merge field is the one that goes out to a client.",
  beats=["Here's the assembly, which verifies every merge field resolved before anything sends.",
         "If one is missing it holds the document and names the field, rather than sending a hole.",
         "The paper trail that goes with it — every document generated is traceable back to the record it came from.",
         "And the retry configuration on the generation call, so a slow storage API delays a document instead of losing one."]),
 "ai-assistant": dict(product="The Straight Answer Desk",
   open="An assistant that guesses is worse than no assistant, because people stop trusting the answers and go back to phoning you.",
   beats=["Here's the assistant — it answers from a real knowledge base and refuses when it doesn't know.",
          "The refusal gate is the product. It hands to a human with the context attached rather than inventing something.",
          "Running inside the tool, with the knowledge source it's actually trained on.",
          "And the behaviour settings — how long it waits, when it stops, when a person takes over."]),
 "cold-outreach": dict(product="The Outreach Engine",
   open="Volume isn't the problem. Deliverability and reply handling are, and they're what nobody sets up properly.",
   beats=["Here's the sending architecture — validated list, deduplicated, rate-limited to protect the domain.",
          "The reply gate stops the sequence the moment someone answers.",
          "Running in the tool, with the sending and consent configuration visible.",
          "And the report: what's landing, what's bouncing, what replied."]),
 "project-ops": dict(product="The Operations Board",
   open="Most board problems are architecture problems: relations pointing at dead boards, no templates, and no way to see who is drowning.",
   beats=["Here's the system that keeps the boards honest — it checks the structure on every change rather than waiting for someone to notice a broken column.",
          "This is the gate underneath it: a relation pointing at a board that no longer exists gets flagged, not silently dropped. Silently dropped is how boards rot.",
          "The standardised subitem structure, so every launch starts the same way instead of from scratch.",
          "And the workload view, which is the answer to 'we can't see who's overloaded'."]),
 "messaging-compliance": dict(product="The Deliverability Build",
   open="Messaging that isn't registered and authenticated doesn't get delivered, and nobody tells you — it just quietly stops arriving.",
   beats=["Here's the system — nothing leaves until the sending identity has been checked against the registry.",
          "This is the gate: registered, and throughput left on the number. 10DLC filtering is silent, so if you don't check here you find out from the reply rate weeks later rather than from an error.",
          "Here's the A2P 10DLC registration path, including the status screen where rejections actually surface.",
          "And the sending-domain setup — SPF, DKIM and DMARC — which is what keeps email out of spam."]),
"ai-research-agent": dict(
  product="The Research Desk",
  open="An agent that researches is easy. An agent that can show you where every sentence came from is the one you can actually put in front of a client.",
  beats=["Here's the research pass — question in, live sources fetched, brief out, and the sources kept.",
         "This is the gate that makes it usable: if a claim is not backed by something it actually fetched, it does not go in the brief. It says what it does not know instead.",
         "The whole pass end to end — search, then the gate, then the brief, with an escalation route when the search itself is down.",
         "And the weekly scorecard: how many answers needed a human, and how thin the sourcing was when they did. Depth measured in sources actually read, not in output length."]),
"conversation-design": dict(
  product="The Conversation Architecture",
  open="Most chatbot projects are copywriting projects wearing an AI costume. The bot fails on the turn nobody scripted, not on the greeting everybody polished.",
  beats=["Here's the shape underneath a conversation — intents, the escalation path, and what happens on the turn nobody planned for.",
         "The refusal and handoff rules are the architecture. A bot that guesses once is a bot nobody trusts twice.",
         "The agent in the tool itself — persona, prompt, and the goals it is actually allowed to pursue.",
         "And the knowledge it answers from, because a conversation is only as honest as its source."]),
"data-model-architecture": dict(
  product="The Data Layer",
  open="Most CRM problems are data-model problems wearing a workflow costume.",
  beats=["Here's the system that enforces it — a record only gets written once every field maps to a property that exists.",
         "This is the gate that keeps the model clean: every field has to map to a property that exists, or the record is quarantined rather than guessed at. Guessing is how you end up with three fields meaning the same thing.",
         "Here's the object model on a real portal — objects, properties, and how they associate.",
         "And the property architecture underneath it, with fill rates so you can see what's actually used."]),
}

TOOLS_INTOOL = ("ghl", "hubspot", "shopify", "stripe", "quickbooks")

# Where the generic picker cannot know which shot the LINE is describing, pin it.
# (beat 3 = their world, beat 4 = the result)
HINT = {
 "storefront-upsell":       ("both-companion-mappings", "buy-x-get-y-reward"),
 "books-reconciliation":    ("bank-rule-builder-stripe", "qb-vs-bank-balance-variance"),
 "scheduling":              ("calendar-availability-mon-fri", "wait-until-scheduled-date"),
 "reporting":               ("dashboard-pipeline-health", "dashboard-four-charts"),
 "system-sync":             ("connected-apps", "integration-connectors"),
 "client-onboarding":       ("trigger-moved-to-won", "canvas-full-7-nodes"),
 "data-collection":         ("form-builder-six-fields", "contact-list-sample-tags"),
 "quote-follow-up":         ("email-action-merge-chip", "canvas-quote-cadence-full"),
 "reactivation":            ("win-back-sms-merge-field", "canvas-full-8-nodes"),
 "approval-routing":        ("stage-editor-7-stages-probabilities", "pipeline-automate-tab"),
 "alerting":                ("notification-merge-fields", "canvas-bottom-escalation"),
 "lead-routing":            ("canvas-speed-to-lead-full", "segment-filter-compound-logic"),
 "stalled-deal-escalation": ("canvas-bottom-escalation", "opp-board-18-opportunities"),
 "platform-migration":      ("import-column-mapping-automapped", "import-summary-26-records-0-errors"),
 "data-model-architecture": ("data-model-graph-view", "contact-properties-fill-rate"),
 "project-ops":             ("subitems-expanded", "dashboard-workload-widget"),
 "production-takeover":     ("kit-retry-config", "node-v2-log-the-run-both-paths"),
 "document-assembly":       ("canvas-paper-trail", "kit-retry-config"),
 "voice-agent-intake":      ("voice-ai-agent-builder-prompt-persona", "voice-ai-deploy-call-routing-hours"),
 "conversation-design":     ("conversation-ai-bot-goals-prompt-personality", "conversation-ai-bot-training-knowledge-base-triggers"),
 "system-sync":             ("deals-table-source-system-external-id", "sync-log-echo-skipped"),
 "ai-research-agent":       ("kit-canvas-18-nodes", "node-v2-gap-report"),
 "messaging-compliance":    ("a2p-10dlc-registration-wizard-steps",
                             "email-deliverability-dedicated-sending-domain-spf-dkim-dmarc"),
}


def pick(files, *patterns):
    for p in patterns:
        for f in files:
            if p in f:
                return f
    return None


def main():
    man = json.load(open(os.path.join(LIB, "manifest.json")))
    by_shape = {}
    for i in man["images"]:
        by_shape.setdefault(i["shape"], []).append(i["file"])

    TOTAL = sum(len(v) for k, v in by_shape.items() if k != "_rejects")

    L = []
    w = L.append
    w("# SEND THIS")
    w("Which screenshots to attach for which ask, and the line to say with each.\n")
    w(f"**Never attach more than four.** The library has {TOTAL} shots so that any scenario is covered;")
    w("a proposal that sends forty reads as a data dump, not as proof. Four is the argument:")
    w("the system, the thinking, their world, the result.\n")
    w("Full inventory per pattern lives in `evidence-library/manifest.json`. This file is the send list.\n")
    w("---\n")

    for shape, spec in SHAPES.items():
        files = sorted(by_shape.get(shape, []))
        if not files:
            continue
        canvas = pick(files, "kit-canvas-18-nodes", "--n8n--canvas")
        # beat 2 is "the thinking" — the decision gate, unless this shape's line
        # explicitly describes the weekly report instead
        order = (["node-v2-gap-report", "node-v2-decision-if"]
                 if spec.get("beat2") == "report"
                 else ["node-v2-decision-if", "node-v2-gap-report"])
        node = pick(files, *order, "node-validate-what-arrived", "node-v2-hold-the-rate-limit")
        # prefer a full in-tool canvas over a partial or an early build
        intool = pick(files, *[f"--{t}--canvas-{s}" for t in TOOLS_INTOOL
                               for s in ("speed-to-lead-full", "full", "bottom", "top")]) or \
                 pick(files, *[f"--{t}--canvas" for t in TOOLS_INTOOL]) or \
                 pick(files, *[f"--{t}--" for t in TOOLS_INTOOL])
        h3, h4 = HINT.get(shape, (None, None))
        if h3:
            intool = pick(files, h3) or intool
        # ONE TOOL ONLY. A send that mixes two CRMs asks the buyer to do the
        # translating. Beat 4 must come from the same tool as beat 3; n8n is the
        # architecture layer and is the one permitted companion.
        same_tool = None
        if intool:
            m = re.search(r"--([a-z0-9]+)--", os.path.basename(intool))
            same_tool = m.group(1) if m else None
        pool = [f for f in files if f not in (canvas, node, intool)]
        if same_tool:
            pool = [f for f in pool if f"--{same_tool}--" in os.path.basename(f)]
        result = (pick(pool, h4) if h4 else None) or \
                 pick(pool, "board", "list", "record", "dashboard", "saved", "detail",
                      "variance", "summary", "report") or (pool[0] if pool else None)

        picks = [(canvas, spec["beats"][0]), (node, spec["beats"][1]),
                 (intool, spec["beats"][2]), (result, spec["beats"][3])]
        picks = [(f, line) for f, line in picks if f and line]

        w(f"## {spec['product']}  ·  `{shape}`")
        w(f"*{len(files)} in the library, send these {len(picks)}.*\n")
        w(f"**Open with:** {spec['open']}\n")
        for n, (f, line) in enumerate(picks, 1):
            w(f"{n}. `{f}`")
            w(f"   > {line}\n")
        w("---\n")

    w("## When their tool isn't in the folder\n")
    w("Send the same four. Swap beat 3 for whichever tool you do have, and say the substitution")
    w("out loud — never let the proposal imply it's their tool:\n")
    w("> *\"That build is in GoHighLevel and this one's in HubSpot, because that's where my last")
    w("> two clients lived. The tool changes; the architecture doesn't — stage criteria, a")
    w("> time-based watcher, an escalation path and a fail-safe are the same four pieces in yours.\"*\n")
    w("Naming it reads as confidence. Hiding it reads as a bait-and-switch the moment they notice.\n")
    w("On Upwork, **attach the files** — do not link to launchforte.com. Links risk reading as circumvention.\n")

    out = "/home/claude/SEND-THIS.md"
    open(out, "w").write("\n".join(L))
    total = sum(1 for s in SHAPES if by_shape.get(s))
    print(f"wrote {out}: send lists for {total} products")

    # --- machine-readable twin, for the Cockpit ---
    send = {}
    for shape, spec in SHAPES.items():
        files = sorted(by_shape.get(shape, []))
        if not files:
            continue
        canvas = pick(files, "kit-canvas-18-nodes", "--n8n--canvas")
        order = (["node-v2-gap-report", "node-v2-decision-if"]
                 if spec.get("beat2") == "report"
                 else ["node-v2-decision-if", "node-v2-gap-report"])
        node = pick(files, *order, "node-validate-what-arrived")
        h3, h4 = HINT.get(shape, (None, None))
        intool = (pick(files, h3) if h3 else None) or \
                 pick(files, *[f"--{t}--canvas" for t in TOOLS_INTOOL]) or \
                 pick(files, *[f"--{t}--" for t in TOOLS_INTOOL])
        rest = [f for f in files if f not in (canvas, node, intool)]
        result = (pick(rest, h4) if h4 else None) or \
                 pick(rest, "board", "list", "record", "dashboard", "detail", "variance", "summary")
        attach = [{"file": f, "line": l, "beat": b}
                  for f, l, b in zip([canvas, node, intool, result], spec["beats"],
                                     ["system", "thinking", "their-world", "result"])
                  if f and l]
        tools = sorted({re.search(r"--([a-z0-9]+)--", os.path.basename(f)).group(1)
                        for f in files if re.search(r"--([a-z0-9]+)--", os.path.basename(f))})
        send[shape] = {"product": spec["product"], "open": spec["open"],
                       "attach": attach, "tools_with_proof": tools,
                       "library_total": len(files)}
    json.dump({"max_attachments": 4,
               "substitution_line": ("That build is in {have} rather than {want}, because that's "
                                     "where my last two clients lived. The tool changes; the "
                                     "architecture doesn't."),
               "rule": ("Attach at most 4. Resolve on SHAPE first, tool second. If the client's "
                        "tool is not in tools_with_proof, still attach the same 4 and state the "
                        "substitution out loud — never imply it is their tool."),
               "shapes": send},
              open("/home/claude/send-list.json", "w"), indent=2)
    print(f"wrote /home/claude/send-list.json: {len(send)} shapes, "
          f"{sum(len(v['attach']) for v in send.values())} attachments")


main()
