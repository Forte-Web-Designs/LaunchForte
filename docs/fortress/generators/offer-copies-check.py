#!/usr/bin/env python3
"""Card 538 drift guard. The Cockpit generators must carry NO typed Technology Partner price: every plan price comes from the
canonical rule via offer_rule (GET /api/offer/rule). Fails on any typed price per month, a typed retainer amount, the retired
750 plan, or a node that does not read offer_rule. Exit 1 on any finding."""
import json, os, re, sys
root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
c = json.load(open(os.path.join(root, "docs/fortress/generators/offer-constants.json")))
bad = []
for rel in c["copies"]:
    text = open(os.path.join(root, rel), encoding="utf-8").read()
    for m in re.finditer(r"\$\d[\d,]* a month|retainer:\s*\d+|retainer\s*=\s*\d+", text):
        bad.append("%s: typed plan price %r" % (rel, m.group(0)))
    if re.search(r"750 a month|\$750 plan", text): bad.append(rel + ": mentions the retired 750 plan")
    needs = rel.endswith(("pricing.py", "cockpit-pricing-node.js", "prompt-of-record.js", "cockpit-prompt-node.js"))
    if needs and "offer_rule" not in text: bad.append(rel + ": does not read offer_rule from the canonical rule")
print("files checked:", len(c["copies"]))
for b in bad: print("DRIFT:", b)
print("FAIL" if bad else "PASS")
sys.exit(1 if bad else 0)
