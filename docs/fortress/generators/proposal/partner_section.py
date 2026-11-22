"""Technology Partner pages for proposals (template v13, editorial layout, v8).
Voice: Launch Forte as the subject (BRAIN rule:voice DOCUMENT VOICE), plain sentences (Voice Rules, Client Document Hard Rules, MCP reference 1960).
Honesty: only what the Nov 9 service status table supports. How much runs from month one depends on access and tools, and the page says so.
No pills, bars, icons, boxed feature cards, 'tier', 'real' as an intensifier, or 'AI' wording."""

import re
import offer_source

def _price():
    """The plan price, read from the verified canonical rule at render time. No verified rule means no page: fail closed, never a blank price."""
    p = offer_source.price_text()
    if not p:
        raise RuntimeError("The Technology Partner plan could not be read from the canonical rule, so the plan pages are not produced.")
    return p

UPWORK_BILLING = False   # set by the generator when the plan is offered to an Upwork buyer under Seth's written per client override

def _billing_note():
    # Seth, Nov 22 2026 2:40 PM CT: the plan pages never mention how the plan is billed (no "separate Upwork contract" line).
    return ""

def configure():
    pass   # kept for callers; the price is read at render time and rendering raises when the rule is not verified

CSS = """
.tp-lead{font-size:11pt;line-height:1.55;color:var(--n700);margin-bottom:8pt}
.tp-lead b,.tp-p b{color:var(--ink);font-weight:600}
.tp-p{font-size:9.8pt;line-height:1.55;color:var(--n600);margin-bottom:7pt}
.tp-price{border-top:1pt solid var(--ink);border-bottom:1pt solid var(--border-strong);padding:5pt 0 4pt 0;margin:2pt 0 8pt 0}
.tp-price:after{content:"";display:block;clear:both}
.tp-price .amt{float:left;width:150pt;font-family:var(--display);font-size:22pt;font-weight:500;letter-spacing:-.03em;line-height:1;color:var(--accent)}
.tp-price .amt span{display:inline;margin-left:4pt;font-size:8.6pt;letter-spacing:0;font-weight:400;color:var(--n500);margin-top:3pt}
.tp-price .txt{float:right;width:330pt;padding-top:6pt;font-size:9.6pt;line-height:1.55;color:var(--n600)}
.tp-price .txt b{color:var(--ink);font-weight:600}
.tp-h3{font-family:var(--display);font-size:13pt;font-weight:500;letter-spacing:-.015em;color:var(--ink);margin:2pt 0 5pt 0}
.tp-rows{margin:2pt 0 9pt 0}
.tp-row{display:table;width:100%;border-top:1pt solid var(--border);padding:0}
.tp-row .k{display:table-cell;width:132pt;padding:5pt 12pt 5pt 0;font-family:var(--display);font-size:9.6pt;font-weight:600;color:var(--ink);vertical-align:top}
.tp-row .v{display:table-cell;padding:5pt 0;font-size:9.2pt;line-height:1.55;color:var(--n600);vertical-align:top}
.tp-rows .tp-row:last-child{border-bottom:1pt solid var(--border)}
.tp-shot{border:1pt solid var(--border-strong);margin:6pt 0 4pt 0;width:330pt}
.tp-shot img{width:100%;display:block}
.tp-cap{font-size:7.8pt;line-height:1.5;color:var(--n500);margin-bottom:12pt;width:330pt}
.tp-terms{font-size:9.4pt;line-height:1.6;color:var(--n700);border-top:1pt solid var(--border-strong);padding-top:9pt;margin-top:6pt}
.tp-terms b{color:var(--ink);font-weight:600}
.tp-list{margin:4pt 0 12pt 14pt;padding:0}
.tp-list li{font-size:9.6pt;line-height:1.55;color:var(--n600);margin-bottom:5pt}
.tp-list li b{color:var(--ink);font-weight:600}
.tp-next{margin-top:14pt}
.tp-next ol{margin:3pt 0 0 14pt;font-size:9pt;line-height:1.55;color:var(--n600)}
"""


# Seth, Nov 22 2026 2:45 and 2:50 PM CT: the Technology Partner section is two pages in every proposal. Page A is the plan, page B
# the private client page with the demo screenshots. Page A keeps the value copy: the value heading and paragraph (word for word),
# the seven row monthly table, unlimited requests and "Your person for technology". Launch Forte is the subject except the
# opening paragraph and the accountability line. Backups say "running" only, never that restores work. No guessed savings.
VALUE_HEADING = "Know what's happening, and that it's working."
VALUE_PARA = ("New tools and automations get added faster than ever, and each one makes sense on its own. Together they make it easy to lose track "
              "of what actually needs to happen and whether it is happening. Meanwhile accounts stay open after people leave, backups go unchecked, "
              "subscriptions renew unnoticed, and small problems wait until they show up on the bottom line. This plan gives you one person accountable "
              "for all of it, and a page that shows, with dates, what was checked, what was handled and what needs your decision.")

SYSTEMS_ROW = ("Everything your business runs on, including your website, forms, automations and the software connected to them, is checked against a set "
               "list every month, and each result is recorded with a date. Anything that has stopped working gets caught early, before it reaches a customer.")
ACCESS_ROW = ("Former staff, shared logins, admin roles, old API keys, and the apps and AI tools connected to your accounts are reviewed. "
              "Anything that no longer needs a way in is flagged, with what should change.")
PERSON_LINE = ("One person who knows your systems end to end and answers for every change made and every result reported. "
               "Questions, fixes and decisions all go to the same place, so nothing falls between vendors.")
# Seth's own words, kept verbatim. The generic AI word list and the AI or API ban skip only these exact strings (Seth, Nov 22 2026 2:50 and 2:53 PM CT).
# The access row is backed by catalog checkpoints gen.access_users, gen.access_api_keys, gen.access_connected_apps and gen.access_ai_tools.
SETH_VERBATIM = [VALUE_PARA, SYSTEMS_ROW, ACCESS_ROW, PERSON_LINE]

# Seth, Nov 22 2026 2:53 PM CT: no out of scope or limitation wording anywhere in the Technology Partner section, and the access
# review stays a review with results (no threat detection, protection, bad actors or guarantee wording).
SECTION_BANNED = [r"out of scope", r"outside what the plan covers", r"outside the plan", r"not covered", r"\blimitations?\b",
                  r"bad actors?", r"\bthreats?\b", r"\battackers?\b", r"\bdetect(s|ion|ed)?\b"]

def section_problems(html_text):
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html_text))
    return ["wording not allowed in the Technology Partner section: %r" % m.group(0) for pat in SECTION_BANNED for m in re.finditer(pat, t, flags=re.I)]

def strip_verbatim(text):
    for v in SETH_VERBATIM:
        text = text.replace(v, " ")
    return text

def monthly():
    return [
        ("Your systems", SYSTEMS_ROW),
        ("Who and what has access", ACCESS_ROW),
        ("Backups", "Where a system supports it, Launch Forte confirms backups are running. Where it doesn't, you hear about it."),
        ("Subscriptions", "Overlaps and tools nobody uses are pointed out. No guessed savings."),
        ("Business review", "Risks, manual work that could go away and the next improvements worth making, with facts kept separate from opinions."),
        ("Improvements", "A short list you choose from. Launch Forte makes the changes you approve."),
        ("Monthly update", "What was checked, what was handled and what needs your decision. Happy to talk it through on a call."),
    ]

def page_a():
    rows = "".join(f'<div class="tp-row"><div class="k">{k}</div><div class="v">{v}</div></div>' for k, v in monthly())
    return f'''<h2 class="sec" style="margin-bottom:8pt">Your Technology Partner</h2>
<p class="tp-lead">After I build this, I would be happy to keep helping with the technology side of your business too. For {_price()} a month, I check the systems we agree to cover, review what is working and what needs attention, and look through your software for improvements worth making. You get a monthly update even if you have not asked me for anything new.</p>
<div class="tp-price"><div class="amt">{_price()}<span>a month</span></div><div class="txt">Month to month, cancel anytime, and your accounts stay yours.</div></div>
<div class="tp-h3">{VALUE_HEADING}</div>
<p class="tp-p">{VALUE_PARA}</p>
<div class="tp-h3">What Launch Forte takes care of each month</div>
<div class="tp-rows">{rows}</div>
<p class="tp-p"><b>Unlimited everyday requests.</b> Whenever you need an automation, an integration, a report, a fix or help figuring something out, send it over, as often as you like. Launch Forte works one request at a time so each one gets finished properly. New standalone projects like this one are quoted separately.</p>
<p class="tp-p"><b>Your person for technology.</b> {PERSON_LINE}</p>'''

def page_b_close():
    """Closes page B, under the screenshots. No billing line (Seth, Nov 22 2026 2:40 PM CT)."""
    return f'<div class="tp-terms"><b>{_price()} a month.</b>{_billing_note()} If you only want the project, that\'s completely fine too.</div>'

def next_steps(items):
    return '<div class="tp-next"><div class="label" style="margin-bottom:2pt">Next steps</div><ol>'+"".join(f"<li>{i}</li>" for i in items)+'</ol></div>'


def audit_closing(findings_ref="the findings above"):
    """Card 538: the short optional closing for an audit. Variant audit_closing of the offer resolver. No banner, no price table."""
    return (
        '<h3 class="tpc-h">If you want me around afterwards</h3>'
        '<p class="tpc-p">Everything in this audit stands on its own, and you can take it to any builder you like. '
        'If you would rather have one person check these systems and fix things as they come up, I offer that for %s a month. '
        'It is optional, month to month, and you can cancel anytime.</p>'
        '<p class="tpc-p">Each month Launch Forte checks the systems agreed in writing, reviews who has access, looks at what you are spending on software, '
        'and sends you a short note on what it found and what it would change. Everyday engineering requests are included on top, '
        'one active request at a time. Larger projects are quoted separately, like the ones recommended in %s.</p>'
        '<p class="tpc-p">I only report something as checked once I have checked it, and what I can cover depends on the access and tools your team gives me.</p>'
    ) % (offer_source.price_text(), findings_ref)
