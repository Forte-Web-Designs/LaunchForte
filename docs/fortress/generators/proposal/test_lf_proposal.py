"""Tests for the spec-driven proposal entry (card 535). Synthetic rule text with FIXTURE-style values: these prove behavior, they are not a source of prices."""
import subprocess, re, os, json, os, subprocess, sys, tempfile, unittest, copy, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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

    def test_support_days_cannot_change(self):
        s = copy.deepcopy(SPEC); s["fill"]["[SUPPORT DAYS]"] = "60"
        c, o, _ = self.go(s); self.assertEqual(c, 2); self.assertIn("30 days", o)

    def test_engagement_terms_input_is_refused(self):
        s = copy.deepcopy(SPEC); s["engagement_terms"] = {"net_days": 10, "standard_terms_attached": True, "source_ref": "x"}
        c, o, _ = self.go(s); self.assertEqual(c, 2); self.assertIn("engagement_terms", o)

    def test_unapproved_scope_is_a_draft_without_plan(self):
        s = copy.deepcopy(SPEC); s["buyer"]["scope_approved"] = False
        c, o, out = self.go(s); self.assertEqual(c, 3)
        rep = json.load(open([os.path.join(out, f) for f in os.listdir(out) if f.startswith("qa_report")][0]))
        self.assertFalse(rep["plan_offered"]); self.assertTrue(any("DRAFT" in x for x in rep["unverified_defaults_and_flags"]))


class T5(unittest.TestCase):
    """Universal Technology Partner option (Seth, Nov 13 2026): eligible proposals always show it, exceptions are explicit, preflight fails closed."""
    def go(self, spec, rl=None):
        return run(spec, rl or rules(), tempfile.mkdtemp())

    def rep(self, out):
        return json.load(open([os.path.join(out, f) for f in os.listdir(out) if f.startswith("qa_report")][0]))

    def text(self, out):
        pdf = [os.path.join(out, f) for f in os.listdir(out) if f.endswith(".pdf")][0]
        return " ".join(subprocess.run(["pdftotext", pdf, "-"], capture_output=True, text=True).stdout.split())

    def test_fresh_prospect_shows_option_notice_pages_and_value(self):
        for status in ("prospect", "eligible"):
            s = copy.deepcopy(SPEC); s["buyer"]["status"] = status
            c, o, out = self.go(s); self.assertIn(c, (0, 3), o)
            r = self.rep(out); self.assertTrue(r["plan_expected"] and r["plan_offered"]); self.assertIsNone(r["plan_exception"])
            t = self.text(out)
            for need in ("ongoing Technology Partner after launch", "$500 a month", "Unlimited everyday engineering requests", "Monthly Technology Review", "Forte Intelligence", "new automations and integrations", "month to month", "cancel anytime"):
                self.assertIn(need.lower(), t.lower(), need)
            self.assertLess(t.index("$3,500"), t.index("$500 a month"))   # project price first

    def test_option_is_tailored_to_the_buyers_own_systems_only(self):
        s = copy.deepcopy(SPEC); s["systems"] = ["Shopify", "QuickBooks", "Slack", "Gmail"]
        c, o, out = self.go(s); t = self.text(out)
        self.assertIn("beginning with Shopify and QuickBooks", t)
        self.assertNotIn("Slack and Gmail and", t)
        s = copy.deepcopy(SPEC); s["partner"] = {"observations": [{"text": "An invented claim.", "source_ref": ""}]}
        self.assertEqual(self.go(s)[0], 2)
        s = copy.deepcopy(SPEC); s["partner"] = {"observations": [{"text": "a", "source_ref": "x"}] * 3}
        self.assertEqual(self.go(s)[0], 2)

    def test_exceptions_are_explicit_and_show_nothing(self):
        cases = [({"status": "prospect", "platform": "upwork"}, "UPWORK_PLATFORM"), ({"status": "active_client", "platform": "direct"}, "SIGNED_OR_ACTIVE_CLIENT"),
                 ({"status": "prospect", "platform": "direct", "signed_agreement": True}, "SIGNED_OR_ACTIVE_CLIENT"),
                 ({"status": "opted_out", "platform": "direct"}, "OPT_OUT"), ({"status": "prospect", "platform": "direct", "seth_opt_out": True}, "OPT_OUT"),
                 ({"status": "unsuitable", "platform": "direct"}, "UNSUITABLE_OR_SERVICE_UNSUPPORTED"),
                 ({"status": "prospect", "platform": "direct", "service_unsupported": True}, "UNSUITABLE_OR_SERVICE_UNSUPPORTED"),
                 ({"status": "unknown", "platform": "direct"}, "UNKNOWN_ELIGIBILITY")]
        for b, exc in cases:
            s = copy.deepcopy(SPEC); s["buyer"] = dict(b, scope_approved=True)
            c, o, out = self.go(s); r = self.rep(out)
            self.assertFalse(r["plan_expected"], b); self.assertFalse(r["plan_offered"], b); self.assertEqual(r["plan_exception"], exc, b)
            t = self.text(out)
            for bad in ("Technology Partner", "$500", "Forte Intelligence"):
                self.assertNotIn(bad, t, (b, bad))

    def test_unrecognised_status_or_platform_fails_closed(self):
        for b in ({"status": "maybe", "platform": "direct"}, {"status": "prospect", "platform": "carrier pigeon"}):
            s = copy.deepcopy(SPEC); s["buyer"] = dict(b, scope_approved=True)
            c, o, _ = self.go(s); self.assertEqual(c, 2, b); self.assertIn("fails closed", o)

    def test_financing_disabled_still_shows_the_standalone_option(self):
        s = copy.deepcopy(SPEC)
        c, o, out = self.go(s); r = self.rep(out)
        self.assertEqual(r["financing"], "disabled"); self.assertTrue(r["plan_offered"])
        t = self.text(out); self.assertNotIn("Build & Partner", t); self.assertNotRegex(t, r"(?i)installment")
        s["financing"] = True
        self.assertEqual(self.go(s)[0], 2)   # financing stays refused, and nothing hides the option in the default run

    def test_preflight_fails_when_an_eligible_proposal_loses_the_option(self):
        """A regression that drops the plan pages (here: the page body is emptied) must fail preflight and keep no PDF."""
        tmp = tempfile.mkdtemp(); sp, rp, out = [os.path.join(tmp, n) for n in ("spec.json", "rules.json", "out")]
        json.dump(copy.deepcopy(SPEC), open(sp, "w")); json.dump(rules(), open(rp, "w"))
        code = ("import sys; sys.path.insert(0, %r); import partner_section as P; P.page_a = lambda: '<p>x</p>'; P.page_b = lambda next_html='': '<p>y</p>'; "
                "import lf_proposal; lf_proposal.main(['--spec', %r, '--rules', %r, '--out', %r])" % (HERE, sp, rp, out))
        p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        self.assertIn(p.returncode, (1, 2), p.stdout + p.stderr)
        self.assertEqual([f for f in (os.listdir(out) if os.path.exists(out) else []) if f.endswith(".pdf")], [])


class T6(unittest.TestCase):
    """Independent review defects D1 to D5 (Nov 13 2026)."""
    def go(self, spec): return run(spec, rules(), tempfile.mkdtemp())

    def test_text_flags_and_missing_platform_fail_closed(self):
        for flag in ("signed_agreement", "seth_opt_out", "service_unsupported"):
            for val in ("false", "no", "true", 0, None):
                s = copy.deepcopy(SPEC); s["buyer"][flag] = val
                c, o, _ = self.go(s); self.assertEqual(c, 2, (flag, val, o)); self.assertIn("true or false", o)
        s = copy.deepcopy(SPEC); del s["buyer"]["platform"]
        c, o, _ = self.go(s); self.assertEqual(c, 2); self.assertIn("platform is missing", o)

    def test_observation_limits_and_claims(self):
        long = "word " * 60
        bad = ["You will save $5,000 a year.", "This cuts costs 40 percent.", "This keeps you secure and prevents any breach.", "It never fails.", long]
        for text in bad:
            s = copy.deepcopy(SPEC); s["partner"] = {"observations": [{"text": text, "source_ref": "x"}]}
            self.assertEqual(self.go(s)[0], 2, text)
        s = copy.deepcopy(SPEC); s["partner"] = {"observations": [{"text": "ok", "source_ref": "   "}]}
        self.assertEqual(self.go(s)[0], 2)

    def test_malformed_partner_is_refused_not_a_crash(self):
        for p in ("x", {"observations": [None]}, {"observations": "x"}, {"observations": [{"text": 1, "source_ref": 2}]}):
            s = copy.deepcopy(SPEC); s["partner"] = p
            self.assertEqual(self.go(s)[0], 2, p)

    def test_page_count_check_catches_an_overflow(self):
        import proposal_qa as Q
        self.assertIsNone(Q.page_count_problem(["a\n04 / 07", "b\n07 / 07"] + ["x"] * 5 if False else ["p%d\n%02d / 03" % (i, i + 1) for i in range(3)]))
        self.assertIn("overflowed", Q.page_count_problem(["p\n01 / 03", "p\n02 / 03", "p\n03 / 03", "spill"]))

class T7(unittest.TestCase):
    """Final corrections (Seth, Nov 13 2026)."""
    def test_final_corrections_in_the_pdf(self):
        c, o, out = run(SPEC, rules(), tempfile.mkdtemp())
        self.assertEqual(c, 0, o)
        pdf = [f for f in os.listdir(out) if f.endswith(".pdf")][0]
        txt = subprocess.run(["pdftotext", "-layout", os.path.join(out, pdf), "-"], capture_output=True, text=True).stdout
        flat = re.sub(r"\s+", " ", txt)
        for must in ("30 days of support included with the project", "unless we agree on an earlier start in writing",
                     "detailed written review", "substantial illustrated magazine", "30% off a later qualifying larger project",
                     "not this one, a financed project or the plan fee", "proactive ownership", "once access is authorized and verified",
                     "Sample layouts of both, with a fictional company and made up figures", "Fixed Price, Two Milestones"):
            self.assertIn(must, flat)
        for banned in ("ignore it", "same day", "Milestone Funded", "accountable for all of it", "keep watching", "keep them working", "short written review", "short illustrated magazine"):
            self.assertNotIn(banned, flat)

    def test_preview_images_are_generic_and_hold_no_client_data(self):
        import partner_section as P
        self.assertIn("{SHOT_BOTH}", P.page_b())
        src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "make_previews.py")).read()
        for client in ("FaithWorks", "Debttrakker", "GoHighLevel"):
            self.assertNotIn(client, src)

    def test_member_benefit_is_not_a_discount_on_this_quote(self):
        import partner_section as P
        b = P._benefit()
        self.assertIn("later", b); self.assertIn("not this one", b); self.assertIn("financed project", b)

if __name__ == "__main__":
    unittest.main()
