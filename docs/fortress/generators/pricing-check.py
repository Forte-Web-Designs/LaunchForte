#!/usr/bin/env python3
"""
pricing-check.py — assert the pricing rules against the LIVE generated node.

The rules in the catalogue are only rules if something fails when they are
broken. This runs the node over a spread of shapes and channels and asserts:

  - the derived number stands: divisible by 5, no charm ending
  - no hourly anything reaches any client-facing string
  - buyer spend never appears in the output
  - gig channel over the ceiling ALWAYS produces a phase split, and the two
    phases always sum back to the total
  - both mandatory blocks are present and non-empty on every priced result

Reads cockpit-pricing-node.js as it is on disk. Never a snapshot.
"""
import json, subprocess, sys, re

NODE = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/fortress/generators/cockpit-pricing-node.js"

CASES = [
    ("class1-simple",   "alerting",                "Upwork",
     "We need one alert when a workflow fails. Slack notification, that is it."),
    ("class1-judged",   "client-onboarding",       "Upwork",
     "New client onboarding checklist with kickoff tasks and a welcome sequence."),
    ("class2-2sys",     "books-reconciliation",    "Upwork",
     "HubSpot deals need to create QuickBooks invoices without retyping."),
    ("class2-5sys",     "system-sync",             "Upwork",
     "Keep Shopify, HubSpot, QuickBooks, Airtable and Klaviyo in sync both ways. "
     "Six workflows in total."),
    ("class2-5sys-dir", "system-sync",             "Direct",
     "Keep Shopify, HubSpot, QuickBooks, Airtable and Klaviyo in sync both ways. "
     "Six workflows in total."),
    ("class3-ai",       "ai-assistant",            "Upwork",
     "AI chatbot on our site with a knowledge base and human handoff."),
    ("class3-convo",    "conversation-design",     "Upwork",
     "Review our bot conversation design and rewrite the flow."),
    ("class4-takeover", "production-takeover",     "Upwork",
     "Take over an undocumented existing system and tell us what it does."),
    ("class4-migrate",  "platform-migration",      "Upwork",
     "Migrate from Zapier to n8n and Make, four systems, ten scenarios."),
    ("gig-over-ceiling","system-sync",             "Upwork",
     "Keep Shopify, HubSpot, QuickBooks, Airtable and Klaviyo in sync both ways. "
     "6 workflows in total, two-way, and it has to stay in sync."),
    ("no-shape",        None,                      "Upwork",
     "Something we could not resolve."),
    # The shape says class 2. The posting says take over an undocumented system,
    # which is a class 4 audit. The posting has to win, or a shape that resolved
    # badly becomes a confidently wrong number.
    ("class-disagrees",  "system-sync",            "Upwork",
     "We inherited an undocumented setup from a previous contractor and nobody here knows "
     "what it does. We need someone to take over, review the whole thing and tell us what "
     "is actually running before anything is touched or rebuilt."),
]

src = open(NODE).read()
payloads = [dict(id=c[0], payload=dict(evidence_shape=c[1], channel=c[2], job_post=c[3]))
            for c in CASES]
harness = ("function runNode($json, $){\n%s\n}\nconst P=%s;"
           "console.log(JSON.stringify(P.map(p=>{try{"
           "return {id:p.id, out: runNode(p.payload, ()=>{throw new Error('no node')})[0].json};"
           "}catch(e){return {id:p.id, error:String(e)};}})));"
           % (src, json.dumps(payloads)))
open("/home/claude/_p.js", "w").write(harness)
r = subprocess.run(["node", "/home/claude/_p.js"], capture_output=True, text=True)
if r.returncode:
    print(r.stderr[:3000]); sys.exit(1)
results = json.loads(r.stdout)

HOURLY = re.compile(r"\bper hour\b|\bhourly\b|\ban hour\b|\b/hr\b|\bhours\b", re.I)
SPEND  = re.compile(r"buyer[_ ]spend|spend on upwork|has spent", re.I)

failures = []
print(f"{'case':<18}{'total':>9}  {'split':<18}{'rules':<7}checks")
print("-" * 88)
for res in results:
    cid = res["id"]
    if res.get("error"):
        failures.append(f"{cid}: {res['error']}"); print(f"{cid:<18}  ERROR {res['error'][:50]}"); continue
    o = res["out"]
    if not o.get("priced"):
        print(f"{cid:<18}{'-':>9}  {'(not priced)':<18}{'n/a':<7}refused, as intended")
        continue

    total = o["quote_total"]
    phased = o.get("quote_phased")
    problems = []

    if total % 5: problems.append("total not divisible by 5")
    if str(total).endswith(("97", "99")): problems.append("charm ending")
    if not o.get("pricing_why_it_costs_this"): problems.append("missing why-it-costs-this")
    if not o.get("pricing_phase_split"): problems.append("missing phase-split wording")

    client_text = " ".join(str(o.get(k) or "") for k in
                           ("pricing_three_line", "pricing_what_it_takes", "pricing_anchor",
                            "pricing_phase_split", "pricing_why_it_costs_this", "retainer_line"))
    if HOURLY.search(client_text): problems.append("hourly language in client-facing text")
    if SPEND.search(json.dumps(o)):  problems.append("buyer spend reached the output")

    if o["quote_channel"].lower().startswith("upwork") and total > 3500 and not phased:
        problems.append("over the ceiling with no phase split")
    if phased and phased["phase_one"] + phased["phase_two"] != total:
        problems.append("phases do not sum to the total")
    if phased and phased["phase_one"] > 3500:
        problems.append("phase one over the ceiling")
    if not o.get("pricing_rules_ok"):
        problems.append("node's own guardrail says not ok")

    split = f"{phased['phase_one']}+{phased['phase_two']}" if phased else "none"
    mark = "ok" if not problems else "FAIL"
    print(f"{cid:<18}{total:>9}  {split:<18}{str(o.get('pricing_rules_ok')):<7}{mark}"
          + ("  " + "; ".join(problems) if problems else ""))
    if problems: failures.append(f"{cid}: {'; '.join(problems)}")

print()
# The closed book. These are settled historical numbers, not outputs of this
# arithmetic — they calibrate it. Asserting them needs the original postings,
# which are not on disk here, so this reports honestly rather than pretending.
CLOSED_BOOK = [("MFLG", 2950, None), ("Daleen phase two", 3900, None), ("Drew", 950, None)]
print("closed book:")
for name, amount, post in CLOSED_BOOK:
    if post is None:
        print(f"  {name:<20} ${amount:,}   UNVERIFIED — the original posting text is not on disk, "
              f"so this cannot be re-derived. Paste it into CLOSED_BOOK to check it.")
    else:
        print(f"  {name:<20} ${amount:,}")
print()
print("  Searched 9 Aug 2026: not in the repo, and not in the Cockpit's `proposals` data")
print("  table under any of the three names or the three amounts.")
print()
print("  The proposals table WAS evaluated as a replacement closed book and rejected.")
print("  53 of its rows carry a real posting and a number. Re-deriving all 53 against the")
print("  live node put the median at -22% with a long tail of +525% — because most of those")
print("  numbers are the BUYER'S posted budget ($100, $400), not a price we settled on.")
print("  Comparing our arithmetic against a buyer's budget field measures nothing. A")
print("  regression built on it would go green while being meaningless, which is worse")
print("  than the honest gap. The three numbers still need Seth to paste the postings.")

print()
print("RESULT:", "PASS" if not failures else "FAIL")
for f in failures: print("  -", f)
sys.exit(1 if failures else 0)
