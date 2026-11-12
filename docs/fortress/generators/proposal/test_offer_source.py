import json, threading, http.server, os, sys
import offer_source
good = json.load(open("offer_facts_fixture.json"))
state = {"status": 200, "body": good, "seen_key": None, "seen_url": None}
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        state["seen_key"] = self.headers.get("x-work-key"); state["seen_url"] = self.path
        b = json.dumps(state["body"]).encode(); self.send_response(state["status"]); self.send_header("content-type", "application/json"); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass
srv = http.server.HTTPServer(("127.0.0.1", 0), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
url = "http://127.0.0.1:%d/api/offer/rule" % srv.server_port
bad = 0
def check(name, cond):
    global bad
    print(("PASS " if cond else "FAIL ") + name); bad += (not cond)
if os.path.exists(offer_source.CACHE): os.remove(offer_source.CACHE)
check("good rule loads, key sent in the header only", offer_source.load("k-123", url, use_cache=False) and state["seen_key"] == "k-123" and "k-123" not in state["seen_url"])
check("price and shas come from the rule", offer_source.price_text() == "$500" and offer_source.plan_text() == "$500 a month" and offer_source.service_cents() == 50000 and offer_source.shas()["pricing"] == "bf40e201ea00")
state["body"] = dict(good, plan_price_per_month=650); offer_source.load("k-123", url, use_cache=False)
check("a changed price in the rule changes the next run", offer_source.price_text() == "$650")
state["status"] = 503; state["body"] = {"ok": False, "reason": "rule missing"}
check("503 fails closed (no price, no plan)", not offer_source.load("k-123", url, use_cache=False) and offer_source.price_text() == "" and offer_source.service_cents() is None)
state["status"] = 200; state["body"] = dict(good, stale=True)
check("stale rule fails closed", not offer_source.load("k-123", url, use_cache=False))
state["body"] = dict(good, plan_price_per_month=750)
check("retired 750 plan fails closed", not offer_source.load("k-123", url, use_cache=False))
state["body"] = good
check("no key fails closed without calling the service", not offer_source.load("", url, use_cache=False))
srv.shutdown()
check("service unreachable fails closed", not offer_source.load("k-123", url, use_cache=False, timeout=2))
if os.path.exists(offer_source.CACHE): os.remove(offer_source.CACHE)
print("FAILURES:", bad); sys.exit(1 if bad else 0)
