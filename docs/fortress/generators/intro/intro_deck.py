"""Launch Forte intro deck ("Launch Forte - Seth Forte Intro.pdf"), the canonical generator (Seth, Nov 22 2026 3:16 PM CT).

This is the "Hi, I'm Seth Forte" page every Cockpit email attaches (public-assets/Launch-Forte-Intro.pdf) and the only
document that may name Upwork. Pages:
  01 Cover                 kept exactly from the Nov 2026 deck (kept-pages.pdf page 1)
  02 About Seth            kept exactly from the Nov 2026 deck (Seth, Nov 22 2026 3:25 PM CT: "keep the old version of page 2"), page count restamped
  03 How I work            rebuilt here: Launch Forte replaces "we", point 04 "Built to stay up"
  04 Past work             kept exactly (kept-pages.pdf page 3), only its page count is restamped
  05 Your Technology Partner  value heading and paragraph, seven condensed rows, one real client page screenshot
  06 Next step             testimonials kept, Audit, Build, Technology Partner and Reply here

Rules: the plan price comes only from the verified rule (offer_source, fail closed). The client page screenshot comes
only from product-assets/tp-page (tp_page.load, fail closed). The wording check fails we, us, our, an employer,
outside help, quietly, limitation and security protection wording on the generated pages (3, 5 and 6). Pages 1, 2 and 4
are Seth's own approved pages and are kept byte for byte.

Run: python3 intro_deck.py --rules rules.json --out ./out   (rules.json is the same rule readback the proposal uses)
"""
import argparse, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "..")
PROP = os.path.join(GEN, "proposal")
sys.path.insert(0, GEN)
sys.path.insert(0, PROP)
import tp_page, doc_voice  # noqa: E402

TOTAL = 6
OUT_NAME = "Launch Forte - Seth Forte Intro.pdf"

# Words this deck may never carry (Seth, Nov 22 2026): employer, the old plan, outside help, limitation, security claims.
BANNED = [
    (r"\b(bank|banking|national bank|wells fargo|employer|day job)\b", "employer"),
    (r"\bfull time\b", "full time claim"),
    (r"\b(we|We|us|Us|our|Our|ours)\b", "we, us or our"),
    (r"\bpartnership\b", "old plan name (use Technology Partner)"),
    (r"result you can read in dollars", "old plan promise"),
    (r"\b(monitor(s|ed|ing)?|alerting|protect(s|ed|ion)?|guarantee(s|d)?|24/7|secure)\b", "monitoring, protection or guarantee wording"),
    (r"out of scope|outside what the plan covers|outside the plan|not covered|\blimitations?\b", "limitation wording"),
    (r"\b(threats?|attackers?|bad actors?)\b", "threat wording"),
]

ROWS = [
    ("Your systems", "Checked against a set list every month, each result dated."),
    ("Who and what has access", "Former staff, shared logins, admin roles, old keys and connected apps reviewed."),
    ("Backups", "Confirmed running where a system supports it."),
    ("Subscriptions", "Overlaps and unused tools pointed out."),
    ("Business review", "Risks, manual work and the next improvements, facts kept separate from opinions."),
    ("Improvements", "A short list you choose from."),
    ("Monthly update", "What was checked, what was handled and what needs your decision."),
]


def wording_problems(text):
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text))
    t = re.sub(r"\bmy\.launchforte\.com\S*", " ", t)
    t = re.sub(r'"[^"]*"', " ", t)                 # client testimonials are their own words
    t = t.replace("my wife and our daughter", " ")  # Seth's family, in Off the clock
    out = []
    for pat, why in BANNED:
        flags = 0 if pat.startswith(r"\b(we|We") else re.I
        for m in re.finditer(pat, t, flags):
            out.append("%s: %r" % (why, m.group(0)))
    out += doc_voice.outside_help(t)
    return out


def css():
    tpl = open(os.path.join(PROP, "Launch-Forte-Proposal-Template-v13.html"), encoding="utf-8").read()
    base = tpl[tpl.index("<style>") + 7: tpl.index("</style>")]
    import partner_section
    return base + partner_section.CSS + tp_page.CSS + """
.wm{position:absolute;top:26pt;left:52pt;font-family:var(--display);font-size:8pt;font-weight:600;letter-spacing:.16em;color:var(--ink)}
.wm span{color:var(--accent)}
.lead2{font-family:var(--display);font-size:22pt;font-weight:500;letter-spacing:-.025em;line-height:1.14;color:var(--ink);margin-bottom:16pt;max-width:470pt}
.about{display:table;width:100%;margin-bottom:22pt}
.about .ph{display:table-cell;width:206pt;vertical-align:top}
.about .ph img{width:206pt;height:262pt;object-fit:cover;border-radius:7.5pt;border:1pt solid var(--border)}
.about .tx{display:table-cell;vertical-align:top;padding-left:22pt}
.about p,.prose p{font-size:9pt;line-height:1.72;color:var(--n700);margin-bottom:10pt}
.about p b,.prose p b{color:var(--ink);font-weight:600}
.pair{display:table;width:100%;margin-bottom:12pt}
.pair div{display:table-cell;width:50%;padding-right:9pt}
.pair div+div{padding:0 0 0 9pt}
.pair img{width:100%;height:170pt;object-fit:cover;border-radius:7.5pt;border:1pt solid var(--border)}
.lbl{font-family:var(--display);font-size:7pt;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--n500);margin:2pt 0 7pt}
.pts{border-top:1pt solid var(--border-strong);margin:4pt 0 16pt}
.pt{display:table;width:100%;border-bottom:1pt solid var(--border);padding:8pt 0}
.pt .n{display:table-cell;width:22pt;font-size:7pt;color:var(--accent);font-weight:600;vertical-align:top;padding-top:1pt}
.pt .k{display:table-cell;width:120pt;font-family:var(--display);font-size:9pt;font-weight:600;color:var(--ink);vertical-align:top;padding-right:10pt}
.pt .v{display:table-cell;font-size:8.4pt;line-height:1.55;color:var(--n600);vertical-align:top}
.who{border:1pt solid var(--border-strong);border-radius:10pt;padding:14pt 16pt;background:var(--paper-2)}
.who p{font-size:8.6pt;line-height:1.6;color:var(--n700)}
.who p b{color:var(--ink);font-weight:600}
.vh{font-family:var(--display);font-size:13pt;font-weight:500;letter-spacing:-.015em;color:var(--ink);margin:2pt 0 6pt}
.tpshot{margin:10pt 0 4pt}
.tpshot img{width:86%;margin:0 auto;border:1pt solid var(--border-strong);border-radius:6pt;display:block}
.tpcap{font-size:7.8pt;line-height:1.5;color:var(--n500);margin:5pt 0 10pt}
.tpcap a{color:var(--accent);text-decoration:none}
.q2 p{font-family:var(--display);font-size:13pt;font-weight:500;letter-spacing:-.015em;line-height:1.4;color:var(--ink);margin-bottom:5pt}
.q2 .a{font-size:7.8pt;color:var(--n600);margin-bottom:13pt}
.q2 .a b{color:var(--ink);font-weight:600}
.ap .apr{font-family:var(--display);font-size:8pt;font-weight:600;color:var(--accent-light);margin-top:5pt}
"""


def hdr(n, name):
    return '<div class="wm">LAUNCH FORTE<span>.</span></div><div class="hdr"><span class="ix"><b>%02d</b> / %s</span></div>' % (n, name)


def ftr(n, mid):
    return '<div class="ftr"><span class="l">Seth Forte / Launch Forte</span><span class="c">%s</span><span class="r">%02d / %02d</span></div>' % (mid, n, TOTAL)


def eyebrow(t, w):
    return '<div class="eyebrow"><div class="dot"></div><div class="t">%s</div><div class="rule" style="width:%dpt"></div></div>' % (t, w)


def page_work():
    pts = [
        ("01", "The bigger picture before the build", "Every engagement opens with a read of the whole operation and a number on what the problem is costing. The build is whatever that number points to, and it is scoped to fit the next one."),
        ("02", "Smallest win first", "One piece, shipped and checked, then the next. You pay for what moves the business, in the order it needs to move."),
        ("03", "A few clients at a time", "The roster stays short on purpose. The person who scopes your build is the one who builds it, tests it, and answers you."),
        ("04", "Built to stay up", "Every system ships with scheduled checks, written instructions and a dated record of what was checked, so problems surface early."),
        ("05", "Personalized approach", "Time up front to understand where you are trying to go, then a build shaped to that. Updates come often and read plain, so you never have to chase me or decode a status."),
    ]
    rows = "".join('<div class="pt"><div class="n">%s</div><div class="k">%s</div><div class="v">%s</div></div>' % p for p in pts)
    return ('<div class="page">' + hdr(3, "How I work") + eyebrow("What makes this different", 330)
            + '<div class="lead2">The whole business first. Then the smallest build that moves it.</div>'
            '<div class="prose"><p>Most of what gets posted is a task. I read it for the business underneath: how the money comes in, where it leaks, '
            'which tool is the bottleneck, what has to run clean before anything else can. The task is usually one piece of a bigger picture, and the '
            'bigger picture is what I am building toward. Launch Forte starts with the smallest piece worth taking, proves it on real data, and stacks '
            'the next one on it, so the system ends up running the business instead of becoming one more thing to manage.</p></div>'
            '<div class="pts">' + rows + '</div>'
            '<div class="who"><div class="lbl" style="margin-top:0">Who this is for</div><p>Owners doing real revenue who are still the bottleneck in their own '
            'operation, with tools already in place that do not talk to each other, who want the work off their plate for good. '
            '<b>Fixed price, tested on your data.</b></p></div>'
            + ftr(3, "Audit, then build, then Technology Partner.") + '</div>')


def page_tp(shots, rel):
    import partner_section
    shot = rel(shots["path"]["overview"]["desktop"])
    rows = "".join('<div class="tp-row"><div class="k">%s</div><div class="v">%s</div></div>' % r for r in ROWS)
    return ('<div class="page">' + hdr(5, "Technology Partner") + eyebrow("Your Technology Partner", 360)
            + '<div class="lead2" style="margin-bottom:8pt">Know what\'s happening, and that it\'s working.</div>'
            + '<p class="tp-p">%s</p>' % partner_section.VALUE_PARA
            + '<div class="tp-rows">' + rows + '</div>'
            '<div class="tpshot"><img src="%s"></div>' % shot
            + '<div class="tpcap">Your private client page, with everything checked, handled and waiting on you, dated. See the sample at '
            '<a href="%s">my.launchforte.com/demo</a>.</div>' % tp_page.DEMO_LINK
            + '<p class="tp-p"><b>Your person for technology.</b> %s</p>' % partner_section.PERSON_LINE
            + ftr(5, "Launch Forte stays on after launch.") + '</div>')


def page_next(price_text):
    quotes = [
        ("The process was smooth and stress free from start to finish. I would call it a ten out of ten, and I am already planning to come back for the next project.", "Chelsea Juels", "Founder and CEO, Six Months to Speech"),
        ("He stood out from the pack fast. We'll use him for any job we have.", "Matt Juels", "COO, Six Months to Speech"),
        ("He's enabled me to keep running my business with a lean, efficient team.", "Danielle Sandusky", "Modern Bungalow"),
    ]
    q = "".join('<div class="q2"><p>"%s"</p><div class="a"><b>%s</b>, %s</div></div>' % x for x in quotes)
    steps = (
        '<div class="ap"><div class="apn"></div><div class="apt">Audit</div><div class="aps">I find what is costing you customers and put a number on it. Credits toward the build.</div></div>'
        '<div class="ap"><div class="apn"></div><div class="apt">Build</div><div class="aps">The system the audit points to, built and tested on real data before it goes live.</div></div>'
        '<div class="ap"><div class="apn"></div><div class="apt">Technology Partner</div><div class="aps">Launch Forte stays on after launch. Your systems get checked every month, requests are unlimited, and your private page shows it all.</div><div class="apr">%s a month</div></div>'
        '<div class="ap last"><div class="apn"></div><div class="apt">Reply here</div><div class="aps">Everything before a contract happens in this Upwork thread. Send a message and a call gets set up.</div></div>'
    ) % price_text
    return ('<div class="page last">' + hdr(6, "Next step") + eyebrow("What happens next", 400)
            + '<div class="lead2">If this sounds like the way you want it done, the proposal is right below.</div>' + q
            + '<div class="approve"><div class="agrid gridfield on-dark"></div><div class="in"><div class="ae">Three ways in</div>'
            '<h2>Audit, build, or Technology Partner. Start wherever the problem is.</h2>'
            '<p class="intro">Most owners start with the <b>audit</b>: a short call, a written read of what is broken and what it is worth fixing, and a number on it. '
            'The audit fee credits toward the first build. If the job you posted already names the build, it goes straight to a fixed price proposal.</p>'
            '<div class="steps">' + steps + '</div>'
            '<div class="apfoot"><b>Reply here on Upwork.</b> I usually answer within a business day.</div></div></div>'
            + ftr(6, "Thanks for reading.") + '</div>')


def restamp(page, n):
    """Kept pages stay exactly as they are; only the footer count changes from NN / 05 to NN / 06."""
    from weasyprint import HTML
    import pypdf
    html = ("<html><head><style>@page{size:612pt 792pt;margin:0} body{margin:0}"
            ".m{position:absolute;left:532pt;top:757pt;width:31pt;height:13pt;background:#fff}"
            ".t{position:absolute;right:52pt;top:759.3pt;font-family:Inter;font-size:7.2pt;color:#737373;line-height:1}</style></head>"
            "<body><div class='m'></div><div class='t'>%02d / %02d</div></body></html>" % (n, TOTAL))
    stamp = pypdf.PdfReader(io.BytesIO(HTML(string=html).write_pdf())).pages[0]
    page.merge_page(stamp)
    return page


def build(rules_path, out_dir, dashboard_checkout=None):
    import rules_input, offer_source
    facts, _rates = rules_input.build(json.load(open(rules_path)))
    offer_source.configure(facts)
    if not offer_source.verified():
        raise SystemExit("REFUSED: the Technology Partner price could not be verified from the rules.")
    shots = tp_page.load(os.path.join(HERE, ".tp-page"), dashboard_checkout=dashboard_checkout)
    rel = lambda p: os.path.relpath(p, HERE)
    body = page_work() + page_tp(shots, rel) + page_next(offer_source.price_text())
    problems = wording_problems(body.replace("this Upwork thread", "").replace("Reply here on Upwork", ""))
    if problems:
        raise SystemExit("REFUSED, wording check:\n  " + "\n  ".join(problems))
    from weasyprint import HTML
    import pypdf
    html = "<html><head><meta charset='utf-8'><style>%s</style></head><body>%s</body></html>" % (css(), body)
    new = pypdf.PdfReader(io.BytesIO(HTML(string=html, base_url=HERE).write_pdf()))
    kept = pypdf.PdfReader(os.path.join(HERE, "kept-pages.pdf"))
    w = pypdf.PdfWriter()
    w.add_page(kept.pages[0])                 # 01 cover
    w.add_page(restamp(kept.pages[1], 2))     # 02 about Seth, kept exactly
    w.add_page(new.pages[0])                  # 03 how I work
    w.add_page(restamp(kept.pages[2], 4))     # 04 past work, kept exactly
    w.add_page(new.pages[1])                  # 05 Technology Partner
    w.add_page(new.pages[2])                  # 06 next step
    w.add_metadata({"/Title": "Launch Forte - Seth Forte Intro", "/Author": "Seth Forte / Launch Forte"})
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, OUT_NAME)
    w.write(out)
    m = shots["manifest"]
    report = {"pdf": OUT_NAME, "pages": len(w.pages), "plan_price": offer_source.price_text(), "rule_shas": offer_source.shas(),
              "tp_page": {"design_version": m.get("design_version"), "captured_at": m.get("captured_at"), "checked_against": shots["version_source"]},
              "wording_check": "CLEAN", "kept_exactly": ["01 cover", "02 about Seth (page count restamped)", "04 past work (page count restamped)"]}
    json.dump(report, open(os.path.join(out_dir, "intro_qa_report.json"), "w"), indent=1)
    print("RESULT: PASS | pages %d | plan %s | screenshots %s" % (len(w.pages), offer_source.price_text(), m.get("design_version")))
    return out


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--rules", required=True)
    a.add_argument("--out", default="out")
    a = a.parse_args()
    build(a.rules, a.out, os.environ.get("LF_DASHBOARD_CHECKOUT"))
