import json, sys
from offer_resolver import resolve_offer
cases = json.load(open("offer-resolver-cases.json"))
bad = 0
for c in cases:
    r = resolve_offer(c["in"])
    ok = all(r[k] == v for k, v in c["out"].items())
    bad += (not ok)
    print(("PASS " if ok else "FAIL ") + c["name"])
import json
from offer_resolver import rules_verified
good = json.load(open("offer_facts_fixture.json"))
checks = [("live facts", rules_verified(good), True), ("none", rules_verified(None), False), ("failed read", rules_verified({"ok": False, "reason": "x"}), False),
          ("stale", rules_verified(dict(good, stale=True)), False), ("retired 750", rules_verified(dict(good, plan_price_per_month=750)), False),
          ("no sha", rules_verified(dict(good, offer_rule_sha12="")), False)]
for n, got, want in checks:
    ok = got == want; bad += (not ok); print(("PASS " if ok else "FAIL ") + "rules_verified " + n)
print(len(cases), "shared cases +", len(checks), "fact checks;", "FAILURES:", bad)
sys.exit(1 if bad else 0)
