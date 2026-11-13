#!/usr/bin/env python3
"""
Fills Launch-Forte-Proposal-Template-v13.html (five pages) and writes a PDF.

v12 (Nov 8 2026): the client PDF shows OUTCOME BLOCKS WITH ONE PRICE EACH.
v12.1 (Nov 9 2026): Pricing Standard v2.5. The ongoing plan is Launch Forte
Technology Partner, $500 a month, month to month, cancel anytime. The retired
$750 plan wording is blocked from client copy.

Each block below also carries its internal parts (kind and unit price per the
Pricing Standard). Those parts are written ONLY to worksheet.txt, the internal
PRICING ESTIMATE (INTERNAL, NOT A QUOTE) for the Trello card. They never enter
the HTML or the PDF. The script refuses to write the PDF when:
  - block prices plus credits do not equal [AMOUNT]
  - a block price does not equal the sum of its internal parts
  - the splits do not equal [AMOUNT]
  - any piece kind or unit rate appears in the client text
  - the retired plan wording, a second plan, a quota or a request credit appears
  - an active client proposal lacks the $500 Technology Partner line
  - a prospect proposal carries the plan line without WANTS_PLAN

Kinds and unit prices, off the published card (internal only):
    config $250 / connection $400 / judged $700 / surface $600
    risk $800 / extra system $300

    python3 fill_proposal_v13.py
"""
import re
import sys
from purchase_choice import Quote, calculate, refusal_reason
import choice_section, partner_section
from offer_resolver import resolve_offer, rules_verified
import offer_source
from weasyprint import HTML

SRC = "Launch-Forte-Proposal-Template-v13.html"
OUT_HTML = "proposal-filled.html"
OUT_PDF = "Launch-Forte-Proposal.pdf"
OUT_WORKSHEET = "worksheet.txt"

CHOICE_RESULT = None
UPWORK = True
# --- v13 (Pricing Standard v2.6, section 11): controlled experiment, OFF by default ---
SHOW_PARTNER = True    # direct prospects see the optional Technology Partner pages (the $500 plan, month to month). Off for Upwork contracts and active clients.
PURCHASE_CHOICE = None  # None = fixed price only. Set to a purchase_choice.Quote to show Build & Own and Build & Partner.
ACTIVE_CLIENT = False   # True: the Technology Partner plan line is required (every active client proposal)
# --- card 538: the offer resolver decides whether the $500 plan appears (rule technology-partner-offer, sections 4 and 8) ---
BUYER_STATUS = "prospect"    # prospect | eligible | active_client | unknown | opted_out
SIGNED_AGREEMENT = False
SETH_OPT_OUT = False
SCOPE_APPROVED = True
DOC_TYPE = "proposal"
OFFER_PRESET = False   # True only in tests that configure offer_source themselves. Otherwise main() reads the canonical rule through offer_source.load() (needs LF_WORK_KEY); no verified rule means no plan.
OFFER = None       # filled in by main() from the resolver
PARTNER_CONTEXT = None   # buyer specific systems and sourced observations for the partner pages, from the approved spec
POINTER = "I would also be glad to be your ongoing Technology Partner after launch. It is optional and separate from this project, and the next pages explain how it works."
WANTS_PLAN = False      # New prospect: True only when the client wants monitoring or support after the 30 days

# ---------------------------------------------------------------------------
# (outcome name, one or two line plain description, [ (internal part, kind, price) ])
# The client sees: name, description, and ONE price (the sum of the parts).
# A part price of 0 means included. A negative price is a credit (shown as a
# credit block). All-zero blocks render as Included with the part labels as
# plain bullet lines.
# ---------------------------------------------------------------------------
BLOCKS = [
    ("Four Platforms, One Repository",
     "Every order from TikTok, Amazon, Walmart, and Shopify lands in one repository, tagged by channel the moment it arrives.",
     [
        ("TikTok, Amazon, Walmart, and Shopify order feeds into the repository", "4 connections x $400", 1600),
        ("Walmart and Shopify, each a system past the first two", "2 extra systems x $300", 600),
     ]),
    ("The Segment Foundation",
     "Survey data, zip codes, and interest segments beside the sales data, one source for both layers.",
     [("repository holding survey, zip code, and interest segments", "config", 250)]),
    ("AI Content Variations, On Schedule",
     "Variations generate and post on schedule across all four platforms, nothing built by hand.",
     [("content variation system and its posting schedule", "config", 250)]),
    ("Soft Conversions And The Retargeting Pool",
     "Almost buyers on TikTok and Shopify get retargeted with content that already proved it converts. Amazon and Walmart are excluded, neither exposes this signal to a seller.",
     [
        ("TikTok and Shopify add to cart and page view events into the repository", "2 connections x $400", 800),
        ("retargeting pool logic, matching proven content to soft converters", "judged", 700),
        ("soft conversion pool into a retargeting audience", "connection", 400),
     ]),
    ("The Reporting Layer",
     "Which variations, segments, and channels actually convert, replacing survey guesswork with real numbers.",
     [("one dashboard across all four channels", "surface", 600)]),
    ("Handover And Support Window",
     "",
     [
        ("Testing against your real data rather than a sandbox", "included", 0),
        ("Handover documentation, so you can run what was built", "included", 0),
        ("One recorded walkthrough call", "included", 0),
        ("30 days of support after go live", "included", 0),
     ]),
]

# The plan line comes from the canonical rule (Pricing Standard section 10, via offer_source), never typed here.
SUPPORT_PLAN_ACTIVE_T = ("Launch Forte Technology Partner, {P} a month: your business technology handled, "
                       "including everyday engineering requests, monitoring, fixes, and review of anything "
                       "you build or change on your own. Month to month, cancel anytime, optional.")
SUPPORT_PLAN_PROSPECT_T = "If you want ongoing help after that, Launch Forte Technology Partner is {P} a month, month to month, cancel anytime."
SUPPORT_PLAN_ACTIVE = SUPPORT_PLAN_PROSPECT = ""   # filled in by main() from the verified canonical rule (offer_source); empty when the rule is unavailable
SUPPORT_PLAN_NONE = ""   # a prospect who has not asked for monitoring or support sees no plan line

FILL = {
    "[REF]": "LF-2608-COL",
    "[SEND DATE]": "August 20, 2026",
    "[PHASE LABEL]": "Phase One",
    "[CLIENT NAME]": "Cool Cases LLC",
    "[ENGAGEMENT NAME]": "CAC Tracking, Content Engine, and Soft Conversion Retargeting",
    "[COVER SUBTITLE]": "Every sale tagged to its channel, and proven content retargeted to the people closest to buying.",
    "[CONTACT NAME AND TITLE]": "Shelby Adams, Founder",
    "[ENGAGEMENT TYPE]": "Fixed Price, Milestone Funded",
    "[DELIVERY WINDOW]": "4 Weeks",
    "[AMOUNT]": "5,200",

    "[SITUATION TITLE]": "The Discount That Broke The Data",
    "[SITUATION LEAD]":
        "The last launch moved fast, and a marketer discounted eight hundred units along the way, so "
        "those sales cannot tell you what a real customer costs. A survey since then gave you a range, "
        "not a measurement.",
    "[SITUATION DETAIL]":
        "New sizes land this winter, with affiliates and influencers ready to push traffic the moment "
        "stock allows it. <b>Nothing tags a sale back to its channel, segment, or content right now</b>, "
        "and no one who almost buys gets a second chance at content that already works.",
    "[STAGE 1 NAME]": "A customer buys",   "[STAGE 1 NOTE]": "TikTok, Amazon, Walmart, or Shopify",
    "[STAGE 2 NAME]": "The order lands",   "[STAGE 2 NOTE]": "In each platform, separately",
    "[STAGE 3 NAME]": "Source untracked",  "[STAGE 3 NOTE]": "No link back to channel or content",
    "[STAGE 4 NAME]": "Almost buyers lost", "[STAGE 4 NOTE]": "No pool, no path back to them",
    "[STAGE 5 NAME]": "Content unproven",  "[STAGE 5 NOTE]": "No signal on what is converting",
    "[COST LINE 1]": "The survey puts customer acquisition cost between $9 and $32, wide enough that ad spend is still a guess.",
    "[COST LINE 2]": "Affiliates and influencers are ready to push traffic this winter, and everyone who almost buys and does not just disappears, with no way to bring proven content back to them.",
    "[COST LINE 3]": "",
    "[AFTER TITLE]": "Every sale, and every near miss, knows what to do next",
    "[AFTER BODY]":
        "A sale on any of the four platforms gets tagged to its channel and segment the moment it lands. "
        "Add to cart and page view events that never convert on TikTok and Shopify build a pool of near "
        "buyers, and proven content goes back out to them automatically.",

    "[SCOPE TITLE]": "What Gets Built",
    "[SCOPE INTRO]":
        "Four platforms feed one repository instead of four separate dashboards. <b>The tagging has to "
        "exist before traffic starts</b>, so the foundation goes in first and the retargeting loop runs "
        "on top of it.",
    "[VALID THROUGH]": "September 3, 2026",
    "[SPLIT TO START]": "$2,600",
    "[SPLIT ON DELIVERY]": "$2,600",

    "[WEEK 1 SUMMARY]": "TikTok and Amazon order feeds live in the repository, survey and zip code data loaded.",
    "[WEEK 2 SUMMARY]": "Walmart and Shopify feeds connected, all four platforms tagging sales by channel.",
    "[WEEK 3 SUMMARY]": "Content variation system posting on schedule, soft conversion capture and the retargeting pool live on TikTok and Shopify.",
    "[WEEK 4 SUMMARY]": "Reporting layer live, handover walkthrough recorded, support window opens.",
    "[SUPPORT DAYS]": "30",
    "[UPWORK NOTE]": "Accepted and funded through Upwork.",

    "[TESTIMONIAL QUOTE]": "Smooth from start to finish. Already planning to come back for the next project.",
    "[TESTIMONIAL NAME]": "Chelsea",
    "[TESTIMONIAL TITLE]": "Founder, 6 Months to Speech",
}

UPWORK_SWAPS = [
    ("Confirming takes one email", "Confirming takes one reply"),
    ("To seth@launchforte.com.",
     "Reply here on Upwork."),
    ("grab a time at <b>calendly.com/seth-launchforte</b>. Everything else, including questions on scope or terms, is handled over email.",
     "send a message here and a time gets set up. Everything else, including questions on scope or terms, is handled in this thread."),
]

# Strings that must never reach client copy (internal pricing math).
LEAK_PATTERNS = [
    r"\bconnections?\b\s*(&middot;|x|×|\$)",
    r"\b(config|judged|surface|extra systems?|added systems?)\b\s*(&middot;|x|×|\$)",
    r"\$(250|300|400|700|800)\b",      # unit rates (a block price may equal one of these, so see check_leaks)
    r"\bper piece\b", r"\bunit (price|rate)\b", r"\brate card\b",
]

# Pricing Standard v2.5: retired plan wording, second plans, quotas and credits are never client copy.
RETIRED_PLAN_PATTERNS = [
    r"\$\s?750\s*(a|per|/)\s*month", r"\$\s?750\s*/\s*mo\b", r"\bsupport plan\b",
    r"\bplan\s+(tier|a|b)\b", r"\btiers?\b", r"\brequest credits?\b",
    r"\b\d+\s*(hours?|hrs?)\s*(a|per|/)\s*month\b", r"\bhour(ly)? quota\b",
]


def money(n):
    return "$%s" % f"{n:,.0f}"


def block_total(parts):
    return sum(p for _, _, p in parts)


def build_blocks(blocks):
    out = []
    for i, (name, desc, parts) in enumerate(blocks, 1):
        total = block_total(parts)
        if total < 0:
            cls, bn = "blk credit", "&minus;%s" % money(-total)
        elif total == 0:
            cls, bn = "blk inc", "Included"
        else:
            cls, bn = "blk", money(total)
        out.append('    <div class="%s">' % cls)
        out.append('      <div class="bh"><span class="num">%02d</span><span class="name">%s</span><span class="bn">%s</span></div>'
                   % (i, name, bn))
        if desc:
            out.append('      <div class="bd">%s</div>' % desc)
        if total == 0:
            for label, _, _ in parts:
                out.append('      <div class="bi">%s</div>' % label)
        out.append('    </div>')
    return "\n".join(out)


def worksheet(blocks, fill):
    lines = ["PRICING ESTIMATE (INTERNAL, NOT A QUOTE)  Pricing Standard v2.6 worksheet",
             "Never shown to a client. Paste on the Trello card as a dated comment.", ""]
    grand = 0
    for i, (name, _, parts) in enumerate(blocks, 1):
        lines.append("%02d %s   client price %s" % (i, name, money(block_total(parts))))
        for label, kind, price in parts:
            lines.append("      %-9s %-24s %s   %s" % ("", kind, money(price), label))
        grand += block_total(parts)
    lines += ["", "TOTAL %s   status PROVISIONAL until reviewed" % money(grand)]
    return "\n".join(lines) + "\n"


def money_val(s):
    return float(s.replace("$", "").replace(",", ""))


def check(blocks, fill):
    problems = []
    total = money_val(fill["[AMOUNT]"])
    rows = sum(block_total(p) for _, _, p in blocks)
    if rows != total:
        problems.append("block prices add to %s, [AMOUNT] says %s" % (f"{rows:,.0f}", f"{total:,.0f}"))
    split = money_val(fill["[SPLIT TO START]"]) + money_val(fill["[SPLIT ON DELIVERY]"])
    if split != total:
        problems.append("splits add to %s, [AMOUNT] says %s" % (f"{split:,.0f}", f"{total:,.0f}"))
    return problems


def client_body(client_html):
    body = client_html.split("-->", 1)[-1]
    return re.sub(r'<style>.*?</style>', "", body, flags=re.S)


def check_leaks(client_html):
    """Remove the visible block prices and the amount lines, then look for rate math."""
    body = client_body(client_html)
    body = re.sub(r'<span class="bn">[^<]*</span>', "", body)
    body = re.sub(r'\$[\d,]+', "$N", body)  # prices of blocks, amounts, splits, plan line
    bad = []
    for pat in LEAK_PATTERNS[:2] + LEAK_PATTERNS[3:]:
        for m in re.finditer(pat, body, flags=re.I):
            bad.append(m.group(0))
    return bad


def check_plan(client_html, active=None, wants=None):
    """Pricing Standard v2.5 plan rules. Returns a list of problems (empty means pass)."""
    active = ACTIVE_CLIENT if active is None else active
    wants = WANTS_PLAN if wants is None else wants
    body = client_body(client_html)
    problems = []
    tp_segs = re.findall(r"<!--TP-->.*?<!--/TP-->", body, flags=re.S)
    pc_segs = re.findall(r"<!--PC-->.*?<!--/PC-->", body, flags=re.S)
    for seg in tp_segs + pc_segs:
        body = body.replace(seg, "")
    if tp_segs:
        tp = " ".join(tp_segs)
        tptext = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", tp))
        for need in (re.escape(offer_source.plan_text()), r"month to month", r"cancel anytime", r"one active request at a time", r"Unlimited everyday engineering requests",
                     r"quoted separately", r"stay yours", r"will not call anything healthy that I have not checked", r"depends on the access and tools"):
            if not re.search(need, tptext, flags=re.I):
                problems.append("technology partner pages missing required wording: %s" % need)
        banned = (r"24/7", r"around the clock", r"guarantee", r"\bSOC\b", r"\btiers?\b", r"valued at", r"\bsaves? you\b", r"\bhourly\b",
                  r"\b(leverage|streamline|robust|seamless|transformative|compelling|crucial|innovative|foster|cultivate|delve|elevate|harness|navigate|unlock|catalyst|cornerstone|paradigm|synergy|quietly|silently)\b",
                  r"[\u2013\u2014]|--|->|\u2192|~", r"\breal\b", r"\bflag(s|ging)?\b", r"\bour\b", r"\bus\b", r"\bAI\b", r"\b(ledger|proven|browser|session|endpoint|agent|Fortress|Claude)\b",
                  r"\bPricing Standard\b", r"\bdelivered now\b", r"\bset up in your first month\b", r"\bon my own\b", r"\bnothing waits\b", r"\bqueue\b", r"e\.g\.")
        for pat in banned:
            for m in re.finditer(pat, tptext, flags=re.I if pat not in (r"\bAI\b", r"\bSOC\b") else 0):
                problems.append("wording not allowed on partner pages: %r" % m.group(0))
        for pat in RETIRED_PLAN_PATTERNS:
            for m in re.finditer(pat, tptext, flags=re.I):
                problems.append("retired or forbidden wording on partner pages: %r" % m.group(0))
    if pc_segs:
        seg = " ".join(pc_segs)
        if "Build &amp; Own" not in seg or "Build &amp; Partner" not in seg:
            problems.append("choice page must show both options")
        if len(re.findall(re.escape(offer_source.price_text()), seg)) < 2:
            problems.append("choice page must show the plan fee separately and in the combined line")
        for pat in RETIRED_PLAN_PATTERNS:
            for m in re.finditer(pat, seg, flags=re.I):
                problems.append("retired or forbidden wording on choice page: %r" % m.group(0))
        for pat in (r"24/7", r"around the clock", r"guarantee", r"\bSOC\b", r"\bunlimited\b"):
            for m in re.finditer(pat, seg, flags=re.I):
                problems.append("claim beyond the service status table on choice page: %r" % m.group(0))
    for pat in RETIRED_PLAN_PATTERNS:
        for m in re.finditer(pat, body, flags=re.I):
            problems.append("retired or forbidden plan wording: %r" % m.group(0))
    count = len(re.findall(r"\$\d[\d,]* a month", body))
    if (active or wants) and not tp_segs and offer_source.verified() and count != 1:
        problems.append("the Technology Partner plan line must appear exactly once, found %d" % count)
    if tp_segs and count != 0:
        problems.append("the plan price line must live only on the partner pages, found %d outside" % count)
    elif not (active or wants) and count != 0:
        problems.append("a prospect who has not asked for monitoring or support must not see the plan line, found %d" % count)
    return problems


def main():
    issues = check(BLOCKS, FILL)
    if issues:
        print("STOPPED, the numbers do not agree:")
        for i in issues:
            print("   -", i)
        sys.exit(1)

    global SUPPORT_PLAN_ACTIVE, SUPPORT_PLAN_PROSPECT
    if not OFFER_PRESET:
        offer_source.load()
    partner_section.configure(PARTNER_CONTEXT)
    SUPPORT_PLAN_ACTIVE = SUPPORT_PLAN_ACTIVE_T.replace("{P}", offer_source.price_text()) if offer_source.verified() else ""
    SUPPORT_PLAN_PROSPECT = SUPPORT_PLAN_PROSPECT_T.replace("{P}", offer_source.price_text()) if offer_source.verified() else ""
    mapping = dict(FILL)
    mapping["[BUILD BLOCKS]"] = build_blocks(BLOCKS)
    if ACTIVE_CLIENT:
        mapping["[SUPPORT PLAN LINE]"] = SUPPORT_PLAN_ACTIVE
    elif WANTS_PLAN:
        mapping["[SUPPORT PLAN LINE]"] = SUPPORT_PLAN_PROSPECT
    else:
        mapping["[SUPPORT PLAN LINE]"] = SUPPORT_PLAN_NONE

    html = open(SRC, encoding="utf-8").read()
    for token, value in mapping.items():
        html = html.replace(token, value)
    if UPWORK:
        for old, new in UPWORK_SWAPS:
            if html.count(old) != 1:
                print("STOPPED, upwork swap not found exactly once:", old[:50])
                sys.exit(1)
            html = html.replace(old, new)
    html = re.sub(r'\s*<div class="line">\s*</div>', "", html)

    # v13: purchase choice page, only when explicitly enabled and the calculator says both options are allowed
    global CHOICE_RESULT
    CHOICE_RESULT = None
    if PURCHASE_CHOICE is not None and not offer_source.verified():
        print("FAIL CLOSED: the plan fee could not be read from the canonical rule, so no purchase choice is calculated.")
    elif PURCHASE_CHOICE is not None:
        if PURCHASE_CHOICE.approved_total_cents != int(round(money_val(FILL["[AMOUNT]"]) * 100)):
            print("STOPPED, the purchase choice quote does not equal [AMOUNT]")
            sys.exit(1)
        CHOICE_RESULT = calculate(PURCHASE_CHOICE)
        if not CHOICE_RESULT["offer_both"]:
            print("PURCHASE CHOICE REFUSED, fixed price only:", CHOICE_RESULT["refusal"])
    # v13: optional pages inserted before Schedule: the Technology Partner spread (default on for direct prospects) and, only when enabled, the payment choice
    global OFFER
    OFFER = resolve_offer({"doc_type": DOC_TYPE, "buyer_status": "active_client" if ACTIVE_CLIENT else BUYER_STATUS,
                           "platform": "upwork" if UPWORK else "direct", "signed_agreement": SIGNED_AGREEMENT,
                           "seth_opt_out": SETH_OPT_OUT, "scope_approved": SCOPE_APPROVED,
                           "financing_enabled": PURCHASE_CHOICE is not None, "rules_verified": offer_source.verified()})
    show_partner = SHOW_PARTNER and OFFER["offer_plan"] and OFFER["variant"] == "proposal_full"
    print("OFFER RESOLVER:", OFFER["variant"], "| financing:", OFFER["financing"], "|", OFFER["reason"])
    if not offer_source.verified():
        print("FAIL CLOSED: the offer rules were not verified. The document is written without the Technology Partner plan.")
    if CHOICE_RESULT and not OFFER["financing"]:
        CHOICE_RESULT = None  # financing is shown only when the resolver allows it
    if show_partner:
        html = html.replace(SUPPORT_PLAN_PROSPECT, "")  # the partner pages carry the $500 line exactly once
        anchor = 'agreed in writing before any work happens.</div>\n  </div>'
        assert html.count(anchor) == 1, "investment box anchor changed"
        html = html.replace(anchor, anchor + '\n  <div class="tp-notice">' + POINTER + "</div>")  # no price here, only the notice that the option exists
    extra = []
    if show_partner:
        extra.append("tpa"); extra.append("tpb")
    if CHOICE_RESULT and CHOICE_RESULT["offer_both"]:
        extra.append("pc")
    k = len(extra)
    if k:
        total = 5 + k
        pages, no = "", 4
        for kind in extra:
            lab = {"tpa": "Technology Partner", "tpb": "Technology Partner", "pc": "Payment choice"}[kind]
            if kind == "tpa":
                inner = '<div class="eyebrow"><div class="dot"></div><div class="t">Optional <b>&middot; After the project</b></div><div class="rule" style="width:292pt"></div></div>' + partner_section.page_a()
            elif kind == "tpb":
                inner = '<div class="eyebrow"><div class="dot"></div><div class="t">Optional <b>&middot; Every month</b></div><div class="rule" style="width:292pt"></div></div>' + partner_section.page_b().replace("{SHOT}", "portal-sample-top.png")
            else:
                inner = '<div class="eyebrow"><div class="dot"></div><div class="t">Optional <b>&middot; Same project</b></div><div class="rule" style="width:292pt"></div></div>' + choice_section.body(CHOICE_RESULT)
            seg = '<div class="page"><div class="hdr"><img src="launch-forte-dark.png"><span class="ix"><b>%02d</b> / %s</span></div>%s<div class="ftr"><span class="l">Seth Forte / Launch Forte</span><span class="c">Reply to confirm. First milestone initiates work.</span><span class="r">%02d / %02d</span></div></div>\n' % (no, lab, inner, no, total)
            tag = "TP" if kind in ("tpa", "tpb") else "PC"
            pages += "<!--%s-->%s<!--/%s-->\n" % (tag, seg, tag)
            no += 1
        marker = "<!-- ============ 04 SCHEDULE AND TERMS ============ -->"
        assert html.count(marker) == 1
        html = html.replace(marker, pages + marker)
        html = html.replace('<b>04</b> / Schedule', '<b>%02d</b> / Schedule' % (4 + k)).replace('<b>05</b> / Acceptance', '<b>%02d</b> / Acceptance' % (5 + k))
        for old, new_ in (("04 / 05</span>", "%02d / %02d</span>" % (4 + k, total)), ("05 / 05</span>", "%02d / %02d</span>" % (5 + k, total)),
                          ("01 / 05</span>", "01 / %02d</span>" % total), ("02 / 05</span>", "02 / %02d</span>" % total), ("03 / 05</span>", "03 / %02d</span>" % total)):
            html = html.replace(old, new_, 1) if old.startswith(("04", "05")) else html.replace(old, new_)
        html = html.replace('</style>', partner_section.CSS + choice_section.CSS + '</style>', 1)

    plan_problems = check_plan(html)
    if plan_problems:
        print("STOPPED, the plan line breaks Pricing Standard v2.5:")
        for p in plan_problems:
            print("   -", p)
        sys.exit(1)
    leaks = check_leaks(html)
    if leaks:
        print("STOPPED, internal piece math reached client copy:", leaks)
        sys.exit(1)

    open(OUT_HTML, "w", encoding="utf-8").write(html)
    open(OUT_WORKSHEET, "w", encoding="utf-8").write(worksheet(BLOCKS, FILL))
    HTML(OUT_HTML).write_pdf(OUT_PDF)

    body = html.split("-->", 1)[-1]
    left = sorted(set(re.findall(r"\[[A-Z][A-Z0-9 ]{1,28}\]", body)))
    print("wrote", OUT_PDF, "and", OUT_WORKSHEET)
    print("total $%s from %d outcome blocks" % (FILL["[AMOUNT]"], len(BLOCKS)))
    print("unfilled tokens:", left or "none")


if __name__ == "__main__":
    main()
