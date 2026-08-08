#!/usr/bin/env python3
"""
matcher-test.py — prove the matcher discriminates, and prove it under contamination.

Two runs against the SAME postings:
  CLEAN        the posting arrives alone, the way it does locally
  CONTAMINATED the posting arrives with a large constant riding in another field,
               which is what a real Cockpit execution looks like

The old node passes CLEAN and collapses under CONTAMINATED — every job resolving
to one shape. That collapse is the bug in the handoff. A fix is only a fix if
both columns match.

Always reads the CURRENT node file. Never a snapshot.
"""
import json, subprocess, sys, os

NODE = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/cockpit-evidence-node.js"

# The constant. In production this is our own text riding in a payload field:
# the assembled prompt, the playbook, a previous run's output. It names every
# pattern and every tool we hold, which is exactly why it wins on raw count.
BLOB = open("/home/claude/fortress/SEND-THIS.md").read()

JOBS = [
    dict(id="ghl-10dlc", expect="messaging-compliance", tool="gohighlevel",
         title="A2P 10DLC registration and SMS deliverability in GoHighLevel",
         post="Our GoHighLevel sub-accounts keep getting SMS blocked by carriers. We need "
              "A2P 10DLC brand and campaign registration done properly, opt-out handling "
              "that actually records consent, and our sending domain set up with SPF, DKIM "
              "and DMARC so email stops landing in spam. TCPA compliance matters to us."),
    dict(id="pipedrive-stall", expect="stalled-deal-escalation", tool="pipedrive",
         title="Pipedrive deals sitting in a stage with no movement",
         post="Deals go into our Pipedrive proposal pipeline and just sit there. Nobody "
              "notices a deal has not progressed in three weeks. We want stage-entry rules, "
              "an escalation when something is overdue, and an on hold reason captured so a "
              "stalled deal is visible instead of quietly rotting."),
    dict(id="airtable-model", expect="data-model-architecture", tool="airtable",
         title="Airtable base restructure — our schema is a mess",
         post="Our Airtable base grew organically and the data model is now a problem. "
              "Duplicate custom fields everywhere, no field standard, data quality is bad. "
              "We need someone to design a proper schema, define each object and property, "
              "and migrate what we have into it."),
    dict(id="telehealth-sms", expect="messaging-compliance", tool=None,
         title="Telehealth SMS reminders keep getting filtered",
         post="We run a telehealth practice and our appointment SMS is getting blocked. "
              "Need A2P 10DLC sorted, carrier registration, opt-out compliance and our "
              "sending domain warmed with SPF DKIM DMARC so deliverability recovers."),
    dict(id="hubspot-qbo", expect="books-reconciliation", tool="hubspot",
         title="HubSpot and QuickBooks invoice reconciliation",
         post="When a deal closes in HubSpot somebody retypes it into QuickBooks. We want "
              "the invoice created automatically, payouts reconciled against the ledger, and "
              "an aging report so invoices get chased. Month end currently takes four days."),
    dict(id="ghl-chatbot", expect="conversation-design", tool="gohighlevel",
         title="Chatbot copywriter to review our GoHighLevel bot conversation flow",
         post="We have a bot live in GHL and the conversation design is weak. Looking for a "
              "chatbot copywriter to review the conversation flow, fix the fallback message, "
              "define the intents properly and design the escalation to human. Reviewing the "
              "dialogue and the bot persona is the job."),
    dict(id="claude-research", expect="ai-research-agent", tool=None,
         title="Claude and Perplexity research agent with citations",
         post="Want a deep research agent using Claude and Perplexity that produces a market "
              "research brief with a citation on every claim. Retrieval and grounding matter — "
              "no hallucinated sources. Setting up agents scoped to one job each."),
    dict(id="shopify-bundle", expect="storefront-upsell", tool="shopify",
         title="Shopify post-purchase upsell and product bundles",
         post="Shopify store, want a cross-sell on the cart and a post purchase upsell when an "
              "order is placed. Klaviyo is our email tool. Product bundle logic by variant."),
    dict(id="restaurant-menu", expect=None, tool=None,
         title="Restaurant menu design, PDF deliverable",
         post="Looking for a graphic designer to lay out a new dinner menu for our restaurant. "
              "Final deliverable as a print-ready pdf. Two pages, our brand colours."),
]

def build_harness(node_src, payloads):
    # $ is the n8n node accessor. Payloads may carry an "upstream" map naming
    # what each referenced node would return, so the recovery path is exercised
    # exactly as it runs in production.
    return ("function runNode($json, $){\n%s\n}\nconst P=%s;\nconst out=P.map(p=>{"
            "const $=(n)=>{const u=(p.upstream||{})[n]; if(!u) throw new Error('no node '+n);"
            "return {first:()=>({json:u})};};"
            "try{const o=runNode(p.payload, $)[0].json;return{id:p.id,shape:o.evidence_shape,"
            "tool:o.client_tool,count:o.evidence_count,skip:!!o.should_skip,"
            "conf:o.match_confidence,files:(o.evidence||[]).map(e=>e.file),"
            "override:o.shape_override||null,unverified:!!o.shape_unverified,"
            "trace:o.evidence_input||null};}"
            "catch(e){return{id:p.id,error:String(e)};}});"
            "console.log(JSON.stringify(out));"
            % (node_src, json.dumps(payloads)))

def run(payloads):
    src = open(NODE).read()
    open("/home/claude/_h.js", "w").write(build_harness(src, payloads))
    r = subprocess.run(["node", "/home/claude/_h.js"], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[:3000]); sys.exit(1)
    return {o["id"]: o for o in json.loads(r.stdout)}

clean = run([dict(id=j["id"], payload=dict(jobTitle=j["title"], jobPost=j["post"])) for j in JOBS])
# The contaminated shape: the posting is present AND our own text rides along in
# the fields the old node concatenated.
dirty = run([dict(id=j["id"], payload=dict(
    jobTitle=j["title"], jobPost=j["post"],
    notes=BLOB, summary=BLOB[:20000], reason="scored 82 on the demand model",
    angle="automation retainer", category="Automation & Integration",
    skills="n8n, Zapier, Make.com, API integration, GoHighLevel, HubSpot",
)) for j in JOBS])

# The worst realistic case, and the one that actually explains three unrelated
# jobs coming back with the same four shots: the posting arrives under a field
# name nobody wrote down, there is no title to lean on, and a constant is
# sitting in the fields the old node concatenated. With no title the old node
# has nothing but the constant, so the constant elects the shape — every time,
# for every job.
blind = run([dict(id=j["id"], payload=dict(
    description=j["post"],
    notes=BLOB, summary=BLOB[:20000],
    skills="n8n, Zapier, Make.com, API integration, GoHighLevel, HubSpot",
    category="Automation & Integration",
)) for j in JOBS])

# The shape a REAL execution actually has, dumped from run 25938. "Match Product"
# joins the run against a stored shapes table and does not carry $json through,
# so the posting is gone by the time it reaches this node and a `shape` from a
# record written days earlier rides in its place. Every job resolved to that
# stored shape. This column proves the node now walks back to Ground Match for
# the posting and scores it on its own words.
production = run([dict(id=j["id"], payload=dict(
    id=7, label="dental-expansion-probe-two-uqok", shape="voice-agent-intake",
    status="raw", seen_count=3, matchedCount=0, briefWordCount=5,
    questions_raw="Walk me through what your front desk does on a booking call, "
                  "start to finish, including the part where nobody picks up. " * 12,
    access_list="Twilio account admin access (or a subaccount) with the existing numbers visible",
    prior_art="dental-shape-probe-iysb | dental-expansion-probe-two-uqok",
), upstream={"Ground Match": dict(
    jobTitle=j["title"], jobPost=j["post"],
    notes="", reason="scored 82 on the demand model", angle="automation retainer",
    skills="n8n, Zapier, Make.com, API integration, GoHighLevel, HubSpot",
    category="Automation & Integration", toolsSeen=j["tool"] or "",
)}) for j in JOBS])

W = 22
def label(o, expect):
    if o.get("error"): return "ERROR"
    if o.get("skip"):  return "(refused)"
    return o.get("shape") or "-"

def ok(o, expect):
    if o.get("error"): return False
    if expect is None: return bool(o.get("skip"))
    return (not o.get("skip")) and o.get("shape") == expect

print(f"{'job':<18}{'expected':<25}{'clean':<25}{'contaminated':<25}{'blind+contam':<25}{'production payload':<25}")
print("-" * 143)
fails = []
for j in JOBS:
    c, d, b, pr = clean[j["id"]], dirty[j["id"]], blind[j["id"]], production[j["id"]]
    exp = j["expect"] or "(refuse)"
    good = all(ok(x, j["expect"]) for x in (c, d, b, pr))
    if not good: fails.append(j["id"])
    print(f"{j['id']:<18}{exp:<25}{label(c,exp):<25}{label(d,exp):<25}{label(b,exp):<25}"
          f"{label(pr,exp):<25}{'  ok' if good else '  FAIL'}")

recovered = sum(1 for j in JOBS if (production[j["id"]].get("trace") or {}).get("posting_recovered_upstream"))
overrode  = sum(1 for j in JOBS if production[j["id"]].get("override"))
print()
print(f"production payload: posting recovered from an upstream node in {recovered}/{len(JOBS)} runs; "
      f"the stored shape was overruled in {overrode}")

print()
nd = lambda r: len({r[j["id"]].get("shape") for j in JOBS})
print(f"distinct shapes   clean {nd(clean)}   contaminated {nd(dirty)}   blind+contam {nd(blind)}"
      f"    (total collapse would read 1)")

# The attachment check the handoff insists on: same shape must not mean same files.
live = [j for j in JOBS if j["expect"]]
stable = [j["id"] for j in live
          if clean[j["id"]].get("files")
          and clean[j["id"]]["files"] == dirty[j["id"]].get("files")
          and clean[j["id"]]["files"] == blind[j["id"]].get("files")]
print(f"attachments unchanged by contamination: {len(stable)}/{len(live)} "
      f"(the files a buyer opens must not depend on what else rode in the payload)")
allfiles = {tuple(clean[j["id"]].get("files") or []) for j in live}
print(f"distinct attachment sets across {len(live)} live jobs: {len(allfiles)} "
      f"(the reported bug was 1)")

t = blind["ghl-10dlc"].get("trace")
if t:
    print("\ninput trace, blind+contaminated run (ghl-10dlc):")
    print("  post read from :", t.get("post_field"), f"({t.get('post_chars')} chars)")
    print("  dropped as ours:", ", ".join(t.get("dropped_as_ours") or []) or "none")
    for f in t.get("fields_seen", []):
        print(f"    {f['field']:<12}{f['chars']:>7} chars  ours={f['ours']}  used={f['used']}")

print()
print("RESULT:", "PASS" if not fails else "FAIL " + ", ".join(fails))
sys.exit(1 if fails else 0)
