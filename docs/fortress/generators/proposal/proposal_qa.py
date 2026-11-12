"""Quality checks for a generated proposal PDF (card 535). Reads the PDF only. No prices or rules live here except the
Client Document Hard Rules word list, which is stamped with the sha it was copied from so a stale copy is visible."""
import re, subprocess, json, os

WORDS_SHA12 = "ee99703ddff9"   # client-document-hard-rules, required check list. If the live rule sha differs, update this list first.
HARD = [r"Pricing Standard", r"\bv2(\.\d+)?\b", r"\bConfig\b", r"\bJudged\b", r"\bExtra system", r"\bledger\b", r"\btiers?\b", r"\bproven\b",
        r"\blibrary\b", r"\blf_", r"\bqty\b", r"\bbrowser\b", r"\bsessions?\b", r"\bendpoint\b", r"\b401\b", r"\bAPI\b", r"\bFortress\b",
        r"\bClaude\b", r"\bagents?\b", r"\bAI\b"]
REVIEW = [r"\bstandard\b", r"\bConnection\b", r"\bSurface\b", r"\bRisk\b", r"\brate\b", r"\bwe\b", r"\bour\b", r"\bus\b", r"\bSeth\b"]


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def pages_text(pdf):
    t = run(["pdftotext", "-layout", pdf, "-"])
    return [p for p in t.split("\f") if p.strip()]


CASE_SENSITIVE = {r"\bAI\b", r"\bAPI\b", r"\bConfig\b", r"\bJudged\b", r"\bConnection\b", r"\bSurface\b", r"\bRisk\b", r"\bSeth\b", r"\bFortress\b", r"\bClaude\b"}


def _hit(pat, line):
    return re.search(pat, line, 0 if pat in CASE_SENSITIVE else re.I)


def word_check(pages, allow=()):
    """HARD hits always fail. REVIEW hits fail unless the line contains an allowed snippet the spec lists
    (for example 'once we agree'); the running footer Seth Forte / Launch Forte is allowed."""
    hard, review = [], []
    allow = [a.lower() for a in allow]
    for n, p in enumerate(pages, 1):
        for line in p.splitlines():
            line = line.replace("Seth Forte / Launch Forte", "")
            for pat in HARD:
                if _hit(pat, line):
                    hard.append((n, pat, line.strip()))
            if any(a in line.lower() for a in allow):
                continue
            for pat in REVIEW:
                if _hit(pat, line):
                    review.append((n, pat, line.strip()))
    return hard, review


def footer_overflow(pdf, page_h_margin=40):
    """Flags text boxes that sit on top of the footer band (page content running into the footer)."""
    out = run(["pdftotext", "-bbox-layout", pdf, "-"])
    problems = []
    for pm in re.finditer(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', out, re.S):
        h = float(pm.group(2)); body = pm.group(3)
        n = len(problems) + 1
        pg = [m for m in re.finditer(r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</line>', body, re.S)]
        ys = []
        for l in pg:
            words = re.findall(r">([^<]+)</word>", l.group(5))
            ys.append((float(l.group(2)), float(l.group(4)), " ".join(words)))
        foot = [y for y in ys if "Seth Forte / Launch Forte" in y[2]]
        if foot:
            top = min(y[0] for y in foot)
            for y in ys:
                if "Launch Forte" in y[2] and "Seth Forte" in y[2]: continue
                if y[1] > top - 2 and y[0] < top + 1 and not re.search(r"Accept by reply|^\d\d / \d\d", y[2]):
                    problems.append((len(problems) + 1, y[2][:60]))
    return problems


def render(pdf, outdir, dpi=70):
    os.makedirs(outdir, exist_ok=True)
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", pdf, os.path.join(outdir, "page")], check=True)
    return sorted(f for f in os.listdir(outdir) if f.endswith(".png"))


def money_list(text):
    return [int(m.replace(",", "")) for m in re.findall(r"\$(\d[\d,]*)", text)]


def price_audit(pages, amount, plan_price, offered, split):
    """amount: fixed project investment (int). plan_price: int or None. offered: whether the partner pages should exist."""
    prob = []
    full = "\n".join(pages)
    if full.count("$%s" % f"{amount:,}") < 1:
        prob.append("the project investment is not printed")
    # order: cover has no monthly plan price, plan price only after the investment page
    first_amt = next((i for i, p in enumerate(pages) if "$%s" % f"{amount:,}" in p and "Investment" in p.title() or ("$%s" % f"{amount:,}" in p and i > 0)), None)
    tp_pages = [i for i, p in enumerate(pages) if "Technology Partner" in p and "a month" in p]
    if offered:
        if plan_price is None:
            prob.append("partner offered but no verified plan price")
        else:
            token = "$%d" % plan_price
            plan_pages = [i for i, p in enumerate(pages) if token + " a month" in p]
            if not plan_pages:
                prob.append("the plan price is not printed on any page")
            if any(i == 0 for i in plan_pages):
                prob.append("the plan price is on the cover")
            if first_amt is not None and plan_pages and min(plan_pages) < first_amt:
                prob.append("the plan price appears before the project investment")
            if re.search(r"(?<![\d,])\$750\b", full):
                prob.append("retired 750 figure present")
    else:
        if tp_pages or re.search(r"Technology Partner", full):
            prob.append("partner offer present although the buyer is not eligible")
        if plan_price and ("$%d a month" % plan_price) in full:
            prob.append("plan price present although not offered")
    half = f"${split:,}"
    if full.count(half) < 2:
        prob.append("the two milestone amounts %s are not both printed" % half)
    if re.search(r"financ|payment plan|installment|buy now", full, re.I) and not offered is None:
        if re.search(r"Build (&|and) Partner", full):
            prob.append("financing wording present; financing is off by default")
    return prob
