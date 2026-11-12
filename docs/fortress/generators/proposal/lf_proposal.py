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
import rules_input, proposal_qa


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
    if total <= 0 or total % 100:
        refuse("the computed investment %d cannot be split into two equal milestones" % total)
    half = total // 2

    buyer = spec.get("buyer", {})
    status = buyer.get("status", "unknown")
    platform = buyer.get("platform", "direct")
    fill = dict(spec["fill"])
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
    g.SCOPE_APPROVED = bool(buyer.get("scope_approved", True))
    g.WANTS_PLAN = False; g.ACTIVE_CLIENT = False; g.PURCHASE_CHOICE = None
    g.OFFER_PRESET = True
    g.SHOW_PARTNER = True
    os.makedirs(a.out, exist_ok=True)
    out = os.path.abspath(a.out)
    name = re.sub(r"[^A-Za-z0-9]+", "-", spec.get("file_name") or fill["[CLIENT NAME]"]).strip("-")
    g.OUT_HTML = os.path.join(HERE, ".proposal-%s.html" % name)
    g.OUT_PDF = os.path.join(out, "Launch-Forte-Proposal-%s.pdf" % name)
    g.OUT_WORKSHEET = os.path.join(out, "worksheet-%s-INTERNAL.txt" % name)
    buf = io.StringIO()
    code = 0
    with contextlib.redirect_stdout(buf):
        try:
            g.main()
        except SystemExit as e:
            code = e.code or 0
    log = buf.getvalue()
    try:
        os.remove(g.OUT_HTML)
    except OSError:
        pass
    print(log.strip())
    if code or not os.path.exists(g.OUT_PDF):
        refuse("the generator stopped: see the lines above.")

    pages = proposal_qa.pages_text(g.OUT_PDF)
    offered = bool(g.OFFER and g.OFFER["offer_plan"] and g.OFFER["variant"] == "proposal_full")
    hard, review = proposal_qa.word_check(pages, spec.get("word_check_allow", []))
    price_problems = proposal_qa.price_audit(pages, total, offer_source.price(), offered, half)
    overflow = proposal_qa.footer_overflow(g.OUT_PDF)
    left = re.findall(r"\[[A-Z][A-Z0-9 ]{1,28}\]", "\n".join(pages))
    imgs = proposal_qa.render(g.OUT_PDF, os.path.join(out, "pages-" + name))
    report = {"pdf": os.path.basename(g.OUT_PDF), "pages": len(pages), "investment": total, "milestones": [half, half],
              "plan_offered": offered, "offer_reason": g.OFFER["reason"], "plan_price": offer_source.price() if offered else None,
              "rules": {"pricing_sha12": facts["pricing_rule_sha12"], "technology_partner_offer_sha12": facts["offer_rule_sha12"],
                        "client_document_hard_rules_sha12": rules.get("client_document_hard_rules", {}).get("sha12"),
                        "word_list_sha12": proposal_qa.WORDS_SHA12},
              "word_check": {"hard_hits": hard, "review_hits": review},
              "price_problems": price_problems, "footer_overflow": overflow, "unfilled_tokens": left,
              "page_images": imgs, "financing": "disabled",
              "needs_visual_review": "Open every page image before handing the PDF to Seth."}
    ok = not (hard or review or price_problems or overflow or left)
    report["result"] = "PASS" if ok else "NEEDS REVIEW"
    json.dump(report, open(os.path.join(out, "qa_report-%s.json" % name), "w"), indent=2)
    print("RESULT:", report["result"], "| pages", len(pages), "| investment $%s" % f"{total:,}", "| plan offered:", offered)
    for k in ("hard_hits", "review_hits"):
        for h in report["word_check"][k][:20]:
            print("  word check", k, h)
    for p in price_problems + ["footer overflow page %d: %s" % o for o in overflow] + ["unfilled " + t for t in left]:
        print("  problem:", p)
    sys.exit(0 if ok else 3)


if __name__ == "__main__":
    main()
