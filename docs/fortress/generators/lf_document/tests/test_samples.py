"""lf_document sample tests (synthetic data only, per repo rule). The client fixture tests live in the
Fortress 2 project folder lf_document/tests. Run from this folder: python3 -m pytest -q tests"""
import copy, json, os, sys
# The client portal screenshots come from a blank test fixture here, never the live set (tp_page.load).
os.environ.setdefault("LF_TEST", "1")
os.environ.setdefault("LF_TP_PAGE_FIXTURE", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tp_page_fixture"))
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from core import lf_document, plan_price, CLIENT_WORDS
from render import build_html
from lead_gate import check, word_check, to_text

def J(p): return json.load(open(os.path.join(HERE, p)))
SNAP = J("sources/rules_snapshot_2026-11-19.json")
SIGNED, UP8, PROS = J("accounts/signed_retainer_sample.json"), J("accounts/upwork_8mo_sample.json"), J("accounts/direct_prospect_sample.json")
PSPEC = J("specs_proposal_sample.json")
def rec(r, s=SNAP): return next(b for b in lf_document(r, "proposal", s)["whats_next"]["blocks"] if b["kind"] == "recommend")

def test_signed_no_plan_and_upwork_gets_plan():
    assert lf_document(SIGNED, "handoff", SNAP)["resolver"]["verdict"] == "NO PLAN"
    # technology-partner-offer v3 (Seth Nov 23 2026): the Upwork exclusion is removed
    assert lf_document(UP8, "handoff", SNAP)["resolver"]["verdict"] == "OFFER"
    u = copy.deepcopy(UP8); u["resolver_inputs"]["upwork_first_contact_months"] = None
    assert lf_document(u, "handoff", SNAP)["resolver"]["verdict"] == "OFFER"

def test_rules_unavailable_still_renders():
    for snap in (None, dict(SNAP, offer_rule={"sha12": "old"})):
        html, d = build_html(PSPEC, PROS, snap)
        t = to_text(html)
        assert d["resolver"]["verdict"] == "NO PLAN" and "Technology Partner" not in t and "Terms" in t

def test_price_discount_live_and_750_refused():
    s = copy.deepcopy(SNAP); s["pricing_rule"]["section_10_text"] = s["pricing_rule"]["section_10_text"].replace("$500", "$525")
    assert rec(PROS, s)["price"] == "$525 a month"
    s["pricing_rule"]["section_10_text"] = s["pricing_rule"]["section_10_text"].replace("$525", "$750")
    assert plan_price(s["pricing_rule"]["section_10_text"]) is None

def test_operational_rows_lead_with_no_code_change():
    s = copy.deepcopy(SNAP)
    assert [i["key"] for i in rec(PROS)["items"]] == [5, 8, 6]
    next(r for r in s["service_status"]["rows"] if r["n"] == 9)["status"] = "OPERATIONAL"
    assert [i["key"] for i in rec(PROS, s)["items"]][0] == 9

def test_proposal_shape_and_gate():
    html, d = build_html(PSPEC, PROS, SNAP)
    t = to_text(html)
    assert t.find("fixed price") < t.find("What's next") < t.find("Terms")
    assert '"We miss calls when the techs are out, and those people just call the next guy."' in t
    assert "What Launch Forte measures in week one" in t and "Technology Partner" in t
    assert check(html, d, SNAP)["verdict"] == "PASS"

def test_gate_failures():
    html, d = build_html(PSPEC, PROS, SNAP)
    assert any("resolver said no" in f for f in check(html, lf_document(SIGNED, "proposal", SNAP), SNAP)["failures"])
    bad = html.replace("</ul>", "<li><b>%s</b> %s</li></ul>" % CLIENT_WORDS[9], 1)
    assert any("not supported" in f for f in check(bad, d, SNAP)["failures"])
    p = copy.deepcopy(PROS); p["figures"]["week_one_measurements"] = []
    assert lf_document(p, "proposal", SNAP)["figures_manifest"]["status"] == "FAIL"
    assert word_check("We used an AI agent — tier one.")


def test_portal_page_closes_an_eligible_document():
    """Seth Nov 22 2026: the Technology Partner section ends every document that offers the plan, with real portal screenshots."""
    text, doc = build_html(PSPEC, PROS, SNAP)
    if doc["whats_next"]:
        assert "Your private client page" in text
        assert text.index("Your private client page") > text.index("<h2>" + __import__("render").esc(doc["whats_next"]["title"]))
        assert "portal-sample-top" not in text and doc["tp_page"]["checked_against"].startswith("FIXTURE")
    else:
        assert "Your private client page" not in text
