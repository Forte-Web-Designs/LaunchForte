"""Tests for the spec-driven proposal entry (card 535). Synthetic rule text with FIXTURE-style values: these prove behavior, they are not a source of prices."""
import json, os, subprocess, sys, tempfile, unittest, copy, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = json.load(open(os.path.join(HERE, "examples", "ridgeline-spec.json")))

S2 = """## 2. The only rate card
| **Config** | x | **$250** |
| **Connection** | x | **$400** |
| **Judged** | x | **$700** |
| **Surface** | x | **$600** |
| **Risk** | x | **$800** |
| **Extra system** | x | **$300** |
## 3. next"""
S10 = "## 10. Technology Partner\n**Plan.** One plan, **$500 a month**, month to month.\n## 11. next"

def rules(**over):
    r = {"read_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
         "pricing": {"sha12": "bf40e201ea00", "freshness": "VERIFIED", "section_2": S2, "section_10": S10},
         "technology_partner_offer": {"sha12": "6c16db653830", "freshness": "LIVE"},
         "client_document_hard_rules": {"sha12": "ee99703ddff9", "freshness": "LIVE"}, "voice": {"freshness": "LIVE"}}
    r.update(over); return r

def run(spec, rl, tmp):
    sp, rp, out = [os.path.join(tmp, n) for n in ("spec.json", "rules.json", "out")]
    with open(sp, "w") as f: json.dump(spec, f)
    with open(rp, "w") as f: json.dump(rl, f)
    p = subprocess.run([sys.executable, os.path.join(HERE, "lf_proposal.py"), "--spec", sp, "--rules", rp, "--out", out], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr, out

class T(unittest.TestCase):
    def go(self, spec=None, rl=None):
        self.tmp = tempfile.mkdtemp(); return run(spec or copy.deepcopy(SPEC), rl if rl is not None else rules(), self.tmp)

    def test_eligible_prospect_builds_priced_from_rules(self):
        c, o, out = self.go()
        self.assertIn(c, (0, 3), o)
        rep = json.load(open([os.path.join(out, f) for f in os.listdir(out) if f.startswith("qa_report")][0]))
        self.assertEqual(rep["investment"], 3 * 400 + 700 + 400 + 600 + 2 * 300)   # 3500, four client systems means two extra
        self.assertEqual(rep["milestones"], [1750, 1750])
        self.assertTrue(rep["plan_offered"]); self.assertEqual(rep["plan_price"], 500)
        self.assertEqual(rep["price_problems"], []); self.assertEqual(rep["word_check"]["hard_hits"], [])
        self.assertEqual(rep["financing"], "disabled")

    def test_ineligible_buyers_get_no_plan(self):
        for b in ({"status": "prospect", "platform": "upwork"}, {"status": "active_client", "platform": "direct"},
                  {"status": "prospect", "platform": "direct", "signed_agreement": True}, {"status": "opted_out", "platform": "direct"},
                  {"status": "unknown", "platform": "direct"}):
            s = copy.deepcopy(SPEC); s["buyer"] = dict(b, scope_approved=True)
            c, o, out = self.go(s)
            rep = json.load(open([os.path.join(out, f) for f in os.listdir(out) if f.startswith("qa_report")][0]))
            self.assertFalse(rep["plan_offered"], b); self.assertEqual(rep["price_problems"], [], (b, rep["price_problems"]))

    def test_missing_rules_fail_closed(self):
        for bad in ({}, {"pricing": {"sha12": "x", "freshness": "STALE", "section_2": S2, "section_10": S10}},
                    {"pricing": {"sha12": "x", "freshness": "LIVE", "section_2": S2, "section_10": "no plan here"}},
                    {"technology_partner_offer": {"sha12": "", "freshness": "LIVE"}},
                    {"read_at": "2020-01-01T00:00:00Z"}):
            rl = rules(**bad)
            if bad == {}: rl = {}
            c, o, _ = self.go(rl=rl)
            self.assertEqual(c, 2, (bad, o)); self.assertIn("REFUSED", o)

    def test_retired_plan_price_refused(self):
        rl = rules(); rl["pricing"]["section_10"] = S10.replace("$500", "$750")
        c, o, _ = self.go(rl=rl); self.assertEqual(c, 2, o)

    def test_typed_price_or_financing_or_missing_fact_refused(self):
        s = copy.deepcopy(SPEC); s["blocks"][0]["parts"][0]["price"] = 1
        self.assertEqual(self.go(s)[0], 2)
        s = copy.deepcopy(SPEC); s["financing"] = True
        self.assertEqual(self.go(s)[0], 2)
        s = copy.deepcopy(SPEC); del s["fill"]["[SITUATION TITLE]"]
        c, o, _ = self.go(s); self.assertEqual(c, 2); self.assertIn("SITUATION TITLE", o)

class T2(unittest.TestCase):
    def test_split_of_2750_and_unverified_voice_refuses_with_no_override(self):
        s = copy.deepcopy(SPEC); s["blocks"][1]["parts"][0] = {"label": "follow-up sequence", "kind": "config", "qty": 1}
        s["blocks"][1]["parts"].pop(1)   # 3 connections 1200 + config 250 + surface 600 = 2050? keep explicit below
        s["blocks"][1]["parts"].append({"label": "urgent rule", "kind": "judged", "qty": 1})   # 1200+250+700+600 = 2750
        s["systems"] = ["one", "two"]   # two systems, no extras
        rl = rules(); rl["voice"] = {"sha12": "e6110d3a755a", "freshness": "UNVERIFIED"}
        tmp = tempfile.mkdtemp(); c, o, _ = run(s, rl, tmp)
        self.assertEqual(c, 2); self.assertIn("Voice Rules is UNVERIFIED", o)
        self.assertFalse(os.path.exists(os.path.join(tmp, 'out')))

class T4(unittest.TestCase):
    def test_2750_total_splits_and_is_not_flagged_as_750(self):
        s = copy.deepcopy(SPEC); s["blocks"][1]["parts"] = [{"label": "follow-up sequence", "kind": "config", "qty": 1}, {"label": "urgent rule", "kind": "judged", "qty": 1}]
        s["systems"] = ["one", "two"]
        c, o, out = run(s, rules(), tempfile.mkdtemp())
        rep = json.load(open([os.path.join(out, f) for f in os.listdir(out) if f.startswith("qa_report")][0]))
        self.assertEqual((rep["investment"], rep["milestones"]), (2750, [1375, 1375]))
        self.assertEqual(rep["price_problems"], [])

class T3(unittest.TestCase):
    def go(self, spec):
        return run(spec, rules(), tempfile.mkdtemp())

    def test_missing_inventory_scope_or_typed_extra_refused(self):
        s = copy.deepcopy(SPEC); del s["systems"]
        c, o, _ = self.go(s); self.assertEqual(c, 2); self.assertIn("systems inventory", o)
        s = copy.deepcopy(SPEC); del s["buyer"]["scope_approved"]
        c, o, _ = self.go(s); self.assertEqual(c, 2); self.assertIn("scope_approved", o)
        s = copy.deepcopy(SPEC); s["blocks"][0]["parts"].append({"label": "x", "kind": "extra system", "qty": 1})
        c, o, _ = self.go(s); self.assertEqual(c, 2)
        s = copy.deepcopy(SPEC); s["systems"] = ["a", "n8n", "b"]
        c, o, _ = self.go(s); self.assertEqual(c, 2); self.assertIn("middleware", o)

    def test_five_systems_charge_three_extras(self):
        s = copy.deepcopy(SPEC); s["systems"] = ["a", "b", "c", "d", "e"]
        c, o, out = self.go(s)
        rep = json.load(open([os.path.join(out, f) for f in os.listdir(out) if f.startswith("qa_report")][0]))
        self.assertEqual(rep["systems"], {"distinct_client_systems": 5, "extra_systems_charged": 3})
        self.assertEqual(rep["investment"], 2900 + 900)

    def test_no_unsupported_terms_in_default_pdf(self):
        c, o, out = self.go(copy.deepcopy(SPEC))
        pdf = [os.path.join(out, f) for f in os.listdir(out) if f.endswith(".pdf")][0]
        txt = subprocess.run(["pdftotext", pdf, "-"], capture_output=True, text=True).stdout
        for bad in ("Chelsea", "6 Months to Speech", "net-15", "Standard Terms", "revision round", "10 business day", "7 business days", "is the signature", "Clause 01", "Who has handed me this before"):
            self.assertNotIn(bad, txt)
        self.assertIn("half to start and half on delivery", txt)
        self.assertIn("applicable Launch Forte client", " ".join(txt.split()))
        rep = json.load(open([os.path.join(out, f) for f in os.listdir(out) if f.startswith("qa_report")][0]))
        self.assertEqual(rep["unverified_defaults_and_flags"], [])

    def test_approved_testimonial_is_used(self):
        s = copy.deepcopy(SPEC)
        s["testimonial"] = {"quote": "Fictional test quote.", "name": "A Tester", "title": "Owner, Test Co", "source_ref": "test fixture"}
        c, o, out = self.go(s)
        pdf = [os.path.join(out, f) for f in os.listdir(out) if f.endswith(".pdf")][0]
        txt = subprocess.run(["pdftotext", pdf, "-"], capture_output=True, text=True).stdout
        self.assertIn("Fictional test quote.", txt)

    def test_engagement_terms_input_is_refused(self):
        s = copy.deepcopy(SPEC); s["engagement_terms"] = {"net_days": 10, "standard_terms_attached": True, "source_ref": "x"}
        c, o, _ = self.go(s); self.assertEqual(c, 2); self.assertIn("engagement_terms", o)

    def test_unapproved_scope_is_a_draft_without_plan(self):
        s = copy.deepcopy(SPEC); s["buyer"]["scope_approved"] = False
        c, o, out = self.go(s); self.assertEqual(c, 3)
        rep = json.load(open([os.path.join(out, f) for f in os.listdir(out) if f.startswith("qa_report")][0]))
        self.assertFalse(rep["plan_offered"]); self.assertTrue(any("DRAFT" in x for x in rep["unverified_defaults_and_flags"]))

if __name__ == "__main__":
    unittest.main()
