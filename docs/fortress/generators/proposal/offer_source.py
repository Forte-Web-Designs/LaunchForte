"""Card 538 (Seth ruling Nov 12): the proposal generator reads the Technology Partner plan from the canonical rule, never from typed text.
Source: GET <dashboard>/api/offer/rule with the x-work-key header (the key n8n already holds; never in a URL, never logged).
Fail closed: any error, a stale source, a missing price or the retired 750 plan means NO plan text and NO price is produced.
A small cache (default 300 seconds) avoids hammering the service; a cached copy is never used past its age and never after a failure."""
import json, os, time, urllib.request

URL = "https://dashboard.launchforte.com/api/offer/rule"
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".offer_rule_cache.json")
FACTS = None   # the verified facts for this run, or None (unavailable)

def _valid(f):
    return bool(f and f.get("ok") is True and f.get("stale") is not True and isinstance(f.get("plan_price_per_month"), int)
                and f["plan_price_per_month"] > 0 and f["plan_price_per_month"] != 750 and f.get("offer_rule_sha12") and f.get("pricing_rule_sha12"))

def configure(facts):
    """Set (or clear, with None) the facts used by every section. Invalid facts clear it: fail closed."""
    global FACTS
    FACTS = facts if _valid(facts) else None
    return FACTS is not None

def load(key=None, url=URL, ttl=300, use_cache=True, timeout=15):
    key = key or os.environ.get("LF_WORK_KEY", "")
    if use_cache and os.path.exists(CACHE):
        try:
            c = json.load(open(CACHE))
            if time.time() - c["at"] < ttl and _valid(c["facts"]):
                return configure(c["facts"])
        except Exception:
            pass
    if not key:
        return configure(None)
    try:
        req = urllib.request.Request(url, headers={"x-work-key": key, "accept": "application/json"})
        facts = json.load(urllib.request.urlopen(req, timeout=timeout))
    except Exception:
        return configure(None)
    ok = configure(facts)
    if ok:
        try: json.dump({"at": time.time(), "facts": facts}, open(CACHE, "w"))
        except Exception: pass
    return ok

def verified(): return FACTS is not None
def price(): return FACTS["plan_price_per_month"] if FACTS else None
def price_text(): return "$%d" % FACTS["plan_price_per_month"] if FACTS else ""
def plan_text(): return price_text() + " a month" if FACTS else ""
def service_cents(): return FACTS["plan_price_per_month"] * 100 if FACTS else None
def shas(): return {"technology-partner-offer": FACTS["offer_rule_sha12"], "pricing": FACTS["pricing_rule_sha12"]} if FACTS else None
