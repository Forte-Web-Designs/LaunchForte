#!/usr/bin/env python3
"""Launch Forte proposal generator, the one approved entry point (card 535).

    python3 lf_proposal.py --spec spec.json --rules rules.json --out ./out

Fail closed. No price, rate, discount or plan fee is typed anywhere in a spec: every dollar figure is computed from the canonical
Pricing Standard text that the session read through the Launch Forte connector (rules.json, see rules_input.py).
Stops before anything is sent. Financing is refused (Pricing Standard section 11: off by default, not part of this rollout).
Exit codes: 0 built and every check passed; 2 refused or failed closed; 3 built but QA needs a person.
"""
import argparse, json, os, shutil, sys, io, contextlib, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rules_input, proposal_qa, offer_resolver


def refuse(msg, code=2):
    print("REFUSED:", msg)
    sys.exit(code)


def compute_blocks(spec_blocks, rates):
    blocks, total = [], 0
    for b in spec_blocks:
        parts = []
        for p in b["parts"]:
            kind = str(p["kind"]).lower()
            if "price" in p or "amount" in p:
                refuse("a part carries a typed price. Prices are computed from the rate card, never typed.")
            if kind == "included":
                parts.append((p["label"], "included", 0)); continue
            if kind == "extra system":
                refuse("extra system pieces are computed from the systems inventory (spec.systems), never entered by hand.")
            if kind not in rates:
                refuse("unknown piece kind %r" % kind)
            qty = int(p.get("qty", 1))
            if qty < 1:
                refuse("quantity must be at least 1")
            amt = rates[kind] * qty
            parts.append((p["label"], "%d x $%d %s" % (qty, rates[kind], kind), amt))
            total += amt
        blocks.append((b["name"], b.get("desc", ""), parts))
    return blocks, total


def systems_extra(spec):
    """Pricing Standard section 2: each genuinely distinct client system used after the first two, if touched by the scoped build.
    Middleware (n8n, Zapier, Make) does not count. The spec must list the distinct client systems the build touches."""
    sy = spec.get("systems")
    if not isinstance(sy, list) or not [s for s in sy if str(s).strip()]:
        refuse("the spec has no systems inventory. List every distinct client system the build touches (spec.systems); middleware goes in spec.middleware and is not counted.")
    names = [str(s).strip().lower() for s in sy if str(s).strip()]
    if len(set(names)) != len(names):
        refuse("spec.systems lists the same system twice.")
    mw = {"n8n", "zapier", "make", "make.com"}
    bad = [s for s in names if s in mw]
    if bad:
        refuse("middleware is not a client system and is not counted: %s. Move it to spec.middleware." % ", ".join(bad))
    return max(0, len(names) - 2), len(names)


def build_template(spec, src, dst):
    """Writes the template with unsupported defaults removed. Terms and proof come from approved sources named in the spec, never from the sample."""
    html = open(src, encoding="utf-8").read()
    def sub(old, new):
        nonlocal html
        if html.count(old) != 1:
            refuse("template changed: %r not found exactly once. Update lf_proposal.py before building." % old[:60])
        html = html.replace(old, new)
    if spec.get("engagement_terms"):
        refuse("engagement_terms is not supported. Payment terms are fixed by Pricing Standard section 4 and the contract is the applicable approved client agreement, confirmed outside this generator.")
    t = spec.get("testimonial")
    if t and all(t.get(k) for k in ("quote", "name", "title", "source_ref")):
        pass
    else:
        sub("Track record &middot; Before we start", "Before we start")
        sub('<h2 class="sec">Who has handed me this before</h2>', '<h2 class="sec">What I need to begin</h2>')
        sub("""  <div class="quote" style="margin:14pt 0 16pt 0">
    <p>[TESTIMONIAL QUOTE]</p>
    <div class="attr"><b>[TESTIMONIAL NAME]</b>, [TESTIMONIAL TITLE]</div>
  </div>

  <div class="label">What I need to begin</div>
""", "")
    open(dst, "w", encoding="utf-8").write(html)
    return True


UNSUPPORTED_TERMS = ["revision round", "business day window", "business days idle", "standard terms", "net-", "forms our agreement", "that written reply is the signature", "clause 01", "you own what", "is yours.", "everything delivered", "paid for stay"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--rules", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--allow-fixture", action="store_true", help="tests only")
    a = ap.parse_args(argv)

    try:
        spec = json.load(open(a.spec)); rules = json.load(open(a.rules))
    except Exception as e:
        refuse("could not read spec or rules: %s" % e)
    if spec.get("financing") or spec.get("purchase_choice"):
        refuse("financing is disabled by default and is not part of this rollout.")
    try:
        facts, rates = rules_input.build(rules, allow_fixture=a.allow_fixture)
    except rules_input.RulesRefused as e:
        refuse(str(e))

    import fill_proposal_v13 as g, offer_source
    os.chdir(HERE)
    offer_source.configure(facts)
    if not offer_source.verified():
        refuse("the plan fee could not be verified from the rules.")
    blocks, total = compute_blocks(spec["blocks"], rates)
    extra_n, n_sys = systems_extra(spec)
    if extra_n:
        first = blocks[0]
        blocks[0] = (first[0], first[1], list(first[2]) + [("each client system past the first two", "%d x $%d extra system" % (extra_n, rates["extra system"]), extra_n * rates["extra system"])])
        total += extra_n * rates["extra system"]
    if total <= 0 or total % 2:
        refuse("the computed investment %d cannot be split into two equal whole dollar milestones" % total)
    half = total // 2

    buyer = spec.get("buyer", {})
    if "scope_approved" not in buyer:
        refuse("buyer.scope_approved is missing. Unknown scope approval fails closed: no priced proposal is produced.")
    status = buyer.get("status", "unknown")
    platform = buyer.get("platform", "direct")
    # Fail closed on anything not recognised, then decide eligibility independently of the generator.
    if status not in ("prospect", "eligible", "active_client", "opted_out", "unknown", "unsuitable"):
        refuse("buyer.status %r is not recognised. Unknown eligibility fails closed; use prospect, eligible, active_client, opted_out, unknown or unsuitable." % status)
    if platform not in ("direct", "upwork"):
        refuse("buyer.platform %r is not recognised (direct or upwork). Unknown platform fails closed." % platform)
    unsuitable = status == "unsuitable" or bool(buyer.get("service_unsupported"))
    gen_status = "unknown" if unsuitable else status
    expected = offer_resolver.resolve_offer({"doc_type": "proposal", "buyer_status": gen_status, "platform": platform,
        "signed_agreement": bool(buyer.get("signed_agreement")), "seth_opt_out": bool(buyer.get("seth_opt_out")),
        "scope_approved": buyer.get("scope_approved") is True, "financing_enabled": False, "rules_verified": True})
    expected_offer = bool(expected["offer_plan"] and expected["variant"] == "proposal_full")
    if expected_offer:
        exc = None
    elif platform == "upwork": exc = "UPWORK_PLATFORM"
    elif buyer.get("signed_agreement") or status == "active_client": exc = "SIGNED_OR_ACTIVE_CLIENT"
    elif buyer.get("seth_opt_out") or status == "opted_out": exc = "OPT_OUT"
    elif unsuitable: exc = "UNSUITABLE_OR_SERVICE_UNSUPPORTED"
    elif status == "unknown": exc = "UNKNOWN_ELIGIBILITY"
    else: exc = "SCOPE_NOT_APPROVED"
    fill = dict(spec["fill"])
    if str(fill.get("[SUPPORT DAYS]", "30")).strip() != "30":
        refuse("included post launch support is the canonical 30 days. A spec cannot change it. An exception needs an approved, documented agreement.")
    for m in re.finditer(r"(\d+)\s+days of support", json.dumps(spec)):
        if m.group(1) != "30":
            refuse("included post launch support is the canonical 30 days. A spec cannot change it.")
    t = spec.get("testimonial") or {}
    fill["[TESTIMONIAL QUOTE]"] = t.get("quote", ""); fill["[TESTIMONIAL NAME]"] = t.get("name", ""); fill["[TESTIMONIAL TITLE]"] = t.get("title", "")
    missing = [k for k in g.FILL if k not in fill and k not in ("[AMOUNT]", "[SPLIT TO START]", "[SPLIT ON DELIVERY]", "[UPWORK NOTE]")]
    if missing:
        refuse("the spec does not supply: %s. Nothing from the sample is reused." % ", ".join(missing))
    for k in ("[AMOUNT]", "[SPLIT TO START]", "[SPLIT ON DELIVERY]"):
        if k in fill:
            refuse("%s is computed, not supplied." % k)
    fill["[AMOUNT]"] = f"{total:,}"
    fill["[SPLIT TO START]"] = fill["[SPLIT ON DELIVERY]"] = "$" + f"{half:,}"
    fill.setdefault("[UPWORK NOTE]", "Accepted and funded through Upwork." if platform == "upwork" else "")

    g.FILL = fill; g.BLOCKS = blocks
    g.UPWORK = (platform == "upwork")
    g.BUYER_STATUS = status
    g.SIGNED_AGREEMENT = bool(buyer.get("signed_agreement"))
    g.SETH_OPT_OUT = bool(buyer.get("seth_opt_out"))
    g.SCOPE_APPROVED = buyer.get("scope_approved") is True
    pc = spec.get("partner") or {}
    obs = pc.get("observations") or []
    if len(obs) > 2 or any(not (o.get("text") and o.get("source_ref")) for o in obs):
        refuse("partner.observations: at most two, each with text and a source_ref. Nothing is invented for the plan pages.")
    g.PARTNER_CONTEXT = {"systems": spec.get("systems", []), "observations": obs}
    g.BUYER_STATUS = gen_status
    g.WANTS_PLAN = False; g.ACTIVE_CLIENT = False; g.PURCHASE_CHOICE = None
    g.OFFER_PRESET = True
    g.SHOW_PARTNER = True
    os.makedirs(a.out, exist_ok=True)
    out = os.path.abspath(a.out)
    name = re.sub(r"[^A-Za-z0-9]+", "-", spec.get("file_name") or fill["[CLIENT NAME]"]).strip("-")
    g.OUT_HTML = os.path.join(HERE, ".proposal-%s.html" % name)
    g.OUT_PDF = os.path.join(out, "Launch-Forte-Proposal-%s.pdf" % name)
    g.OUT_WORKSHEET = os.path.join(out, "worksheet-%s-INTERNAL.txt" % name)
    tpl = os.path.join(HERE, ".tpl-%s.html" % name)
    build_template(spec, os.path.join(HERE, g.SRC), tpl)
    g.SRC = os.path.basename(tpl)
    buf = io.StringIO()
    code = 0
    with contextlib.redirect_stdout(buf):
        try:
            g.main()
        except SystemExit as e:
            code = e.code or 0
    log = buf.getvalue()
    for tmp in (g.OUT_HTML, tpl):
        try:
            os.remove(tmp)
        except OSError:
            pass
    print(log.strip())
    if code or not os.path.exists(g.OUT_PDF):
        refuse("the generator stopped: see the lines above.")

    pages = proposal_qa.pages_text(g.OUT_PDF)
    offered = bool(g.OFFER and g.OFFER["offer_plan"] and g.OFFER["variant"] == "proposal_full")
    hard, review = proposal_qa.word_check(pages, spec.get("word_check_allow", []))
    price_problems = proposal_qa.price_audit(pages, total, offer_source.price(), offered, half)
    presence = proposal_qa.offer_presence(pages, expected_offer, offer_source.price())
    if presence:
        report0 = {"result": "FAILED PREFLIGHT", "plan_expected": True, "problems": presence}
        for f in (g.OUT_PDF, g.OUT_WORKSHEET):
            try: os.remove(f)
            except OSError: pass
        json.dump(report0, open(os.path.join(out, "qa_report-%s.json" % name), "w"), indent=2)
        for p in presence: print("  preflight:", p)
        refuse("document preflight failed: this buyer is eligible for the Technology Partner option and the finished proposal does not show it. No PDF was kept.")
    overflow = proposal_qa.footer_overflow(g.OUT_PDF)
    left = re.findall(r"\[[A-Z][A-Z0-9 ]{1,28}\]", "\n".join(pages))
    imgs = proposal_qa.render(g.OUT_PDF, os.path.join(out, "pages-" + name))
    report = {"pdf": os.path.basename(g.OUT_PDF), "pages": len(pages), "investment": total, "milestones": [half, half],
              "plan_offered": offered, "plan_expected": expected_offer, "plan_exception": exc, "offer_reason": g.OFFER["reason"], "plan_price": offer_source.price() if offered else None,
              "rules": {"pricing_sha12": facts["pricing_rule_sha12"], "technology_partner_offer_sha12": facts["offer_rule_sha12"],
                        "client_document_hard_rules_sha12": rules.get("client_document_hard_rules", {}).get("sha12"),
                        "word_list_sha12": proposal_qa.WORDS_SHA12,
                        "voice_freshness": rules.get("voice", {}).get("freshness"), "voice_sha12": rules.get("voice", {}).get("sha12")},
              "word_check": {"hard_hits": hard, "review_hits": review},
              "price_problems": price_problems, "footer_overflow": overflow, "unfilled_tokens": left,
              "page_images": imgs, "financing": "disabled",
              "needs_visual_review": "Open every page image before handing the PDF to Seth."}
    flags = []
    full_text = "\n".join(pages)
    low = full_text.lower()
    flags += ["unsupported contract term present in the PDF: " + d for d in UNSUPPORTED_TERMS if d in low]
    if buyer.get("scope_approved") is not True:
        flags.append("DRAFT: scope is not approved, so the plan is omitted and this is not a final quote")
    report["unverified_defaults_and_flags"] = flags
    report["systems"] = {"distinct_client_systems": n_sys, "extra_systems_charged": extra_n}
    report["testimonial_source"] = (spec.get("testimonial") or {}).get("source_ref")
    ok = not (hard or review or price_problems or overflow or left or flags)
    report["result"] = "PASS" if ok else "NEEDS REVIEW"
    json.dump(report, open(os.path.join(out, "qa_report-%s.json" % name), "w"), indent=2)
    print("RESULT:", report["result"], "| pages", len(pages), "| investment $%s" % f"{total:,}", "| plan offered:", offered)
    for k in ("hard_hits", "review_hits"):
        for h in report["word_check"][k][:20]:
            print("  word check", k, h)
    for p in flags + price_problems + ["footer overflow page %d: %s" % o for o in overflow] + ["unfilled " + t for t in left]:
        print("  problem:", p)
    sys.exit(0 if ok else 3)


if __name__ == "__main__":
    main()
