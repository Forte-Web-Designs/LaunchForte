"""Rules input for the proposal generator (card 535).

A session reads the canonical rules through the Launch Forte connector (lf_rules) and writes the evidence into a small rules.json.
Nothing here carries a price, a rate or a discount of its own: the plan price and the six rates are parsed out of the verbatim
Pricing Standard text the session read, and the run fails closed when that text, its sha or its freshness is missing or wrong.

rules.json shape (all strings come from the lf_rules readback, verbatim):
{
  "read_at": "2026-11-12T18:40:00Z",                       # when the session read the rules (must be under 24 hours old)
  "pricing":  {"sha12": "bf40e201ea00", "freshness": "VERIFIED", "version": "v2.6",
               "section_2":  "<the rate card table rows, verbatim>",
               "section_10": "<section 10 text from '## 10.' through the Plan paragraph, verbatim>"},
  "technology_partner_offer": {"sha12": "6c16db653830", "freshness": "LIVE"},
  "client_document_hard_rules": {"sha12": "ee99703ddff9", "freshness": "LIVE"},
  "voice": {"freshness": "LIVE"}
}
"""
import re, datetime

OK_FRESH = ("LIVE", "VERIFIED")
KINDS = {"config": "Config", "connection": "Connection", "judged": "Judged", "surface": "Surface", "risk": "Risk", "extra system": "Extra system"}


class RulesRefused(Exception):
    pass


def _fresh(block, name):
    f = str((block or {}).get("freshness", "")).upper()
    if f not in OK_FRESH:
        raise RulesRefused("%s is %s, not LIVE or VERIFIED, so the proposal is not built." % (name, f or "missing"))


def _age_ok(read_at, max_hours=24, now=None):
    try:
        t = datetime.datetime.fromisoformat(str(read_at).replace("Z", "+00:00"))
    except Exception:
        raise RulesRefused("rules.json has no valid read_at time.")
    now = now or datetime.datetime.now(datetime.timezone.utc)
    if (now - t).total_seconds() > max_hours * 3600:
        raise RulesRefused("The rules were read more than %d hours ago. Read them again." % max_hours)


def parse_rates(section_2):
    rates = {}
    for line in (section_2 or "").splitlines():
        m = re.match(r"\|\s*\*\*(Config|Connection|Judged|Surface|Risk|Extra system)\*\*\s*\|.*\|\s*\*\*\$(\d[\d,]*)\*\*\s*\|", line.strip())
        if m:
            rates[m.group(1).lower()] = int(m.group(2).replace(",", ""))
    missing = [k for k in KINDS if k not in rates]
    if missing:
        raise RulesRefused("The rate card text is missing: %s." % ", ".join(missing))
    return rates


def parse_plan_price(section_10):
    m = re.search(r"\*\*Plan\.\*\*[^\n]*?\*\*\$(\d[\d,]*) a month\*\*", section_10 or "")
    if not m:
        raise RulesRefused("Pricing section 10 text does not state the plan price.")
    price = int(m.group(1).replace(",", ""))
    if price <= 0 or price == 750:
        raise RulesRefused("The plan price read from the rule is not valid.")
    return price


def build(rules, now=None, allow_fixture=False):
    """Returns (facts for offer_source, rates). Raises RulesRefused on anything unverified."""
    if not isinstance(rules, dict) or not rules:
        raise RulesRefused("No rules were supplied (rules.json is empty or missing), so nothing is priced.")
    if str(rules.get("pricing", {}).get("freshness", "")).upper() == "FIXTURE":
        if not allow_fixture:
            raise RulesRefused("These rules are a test fixture, not a live readback.")
    else:
        _age_ok(rules.get("read_at"), now=now)
        _fresh(rules.get("pricing"), "The Pricing Standard")
        _fresh(rules.get("technology_partner_offer"), "The Technology Partner offer rule")
        _fresh(rules.get("client_document_hard_rules"), "The Client Document Hard Rules")
        _fresh(rules.get("voice"), "The Voice Rules")
    p = rules["pricing"]
    for k in ("sha12", "section_2", "section_10"):
        if not p.get(k):
            raise RulesRefused("rules.json pricing.%s is missing." % k)
    offer_sha = (rules.get("technology_partner_offer") or {}).get("sha12")
    if not offer_sha:
        raise RulesRefused("rules.json technology_partner_offer.sha12 is missing.")
    rates = parse_rates(p["section_2"])
    price = parse_plan_price(p["section_10"])
    facts = {"ok": True, "stale": False, "plan_price_per_month": price, "offer_rule_sha12": offer_sha, "pricing_rule_sha12": p["sha12"],
             "pricing_section_10": p["section_10"]}
    return facts, rates
