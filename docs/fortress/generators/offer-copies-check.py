#!/usr/bin/env python3
"""Card 538 drift guard. Every typed copy of the Technology Partner price in the Cockpit generators must equal
offer-constants.json, and the retired 750 dollar plan must not appear as a plan. Exit 1 on any disagreement."""
import json, os, re, sys
root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
c = json.load(open(os.path.join(root, "docs/fortress/generators/offer-constants.json")))
price = c["plan_price_per_month"]
bad, seen = [], 0
for rel in c["copies"]:
    text = open(os.path.join(root, rel), encoding="utf-8").read()
    for m in re.finditer(r"\$(\d[\d,]*) a month|retainer:\s*(\d+)", text):
        amt = int((m.group(1) or m.group(2)).replace(",", "")); seen += 1
        if amt != price: bad.append("%s: found %s, the pinned plan price is %s" % (rel, amt, price))
    if re.search(r"\$750 (a month|plan)|750 a month", text): bad.append(rel + ": mentions the retired $750 plan")
    if "technology-partner-offer" not in text and rel.endswith(("prompt-of-record.js", "cockpit-prompt-node.js")):
        bad.append(rel + ": no pointer to the canonical rule")
print("copies checked:", len(c["copies"]), "| price mentions:", seen, "| pinned price:", price)
for b in bad: print("DRIFT:", b)
print("FAIL" if bad else "PASS")
sys.exit(1 if bad else 0)
