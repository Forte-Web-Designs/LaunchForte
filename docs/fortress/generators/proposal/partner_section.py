"""Technology Partner pages for proposals (template v13, editorial layout, v8).
Voice: Launch Forte as the subject (BRAIN rule:voice DOCUMENT VOICE), plain sentences (Voice Rules, Client Document Hard Rules, MCP reference 1960).
Honesty: only what the Nov 9 service status table supports. How much runs from month one depends on access and tools, and the page says so.
No pills, bars, icons, boxed feature cards, 'tier', 'real' as an intensifier, or 'AI' wording."""

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
.tp-lead{font-size:11pt;line-height:1.6;color:var(--n700);margin-bottom:12pt}
.tp-lead b,.tp-p b{color:var(--ink);font-weight:600}
.tp-p{font-size:9.8pt;line-height:1.6;color:var(--n600);margin-bottom:9pt}
.tp-price{border-top:1pt solid var(--ink);border-bottom:1pt solid var(--border-strong);padding:11pt 0 10pt 0;margin:4pt 0 16pt 0}
.tp-price:after{content:"";display:block;clear:both}
.tp-price .amt{float:left;width:150pt;font-family:var(--display);font-size:34pt;font-weight:500;letter-spacing:-.03em;line-height:1;color:var(--accent)}
.tp-price .amt span{display:block;font-size:8.6pt;letter-spacing:0;font-weight:400;color:var(--n500);margin-top:3pt}
.tp-price .txt{float:right;width:330pt;font-size:9.6pt;line-height:1.55;color:var(--n600)}
.tp-price .txt b{color:var(--ink);font-weight:600}
.tp-h3{font-family:var(--display);font-size:13pt;font-weight:500;letter-spacing:-.015em;color:var(--ink);margin:2pt 0 5pt 0}
.tp-rows{margin:2pt 0 12pt 0}
.tp-row{display:table;width:100%;border-top:1pt solid var(--border);padding:0}
.tp-row .k{display:table-cell;width:132pt;padding:8pt 12pt 8pt 0;font-family:var(--display);font-size:9.6pt;font-weight:600;color:var(--ink);vertical-align:top}
.tp-row .v{display:table-cell;padding:8pt 0;font-size:9.2pt;line-height:1.55;color:var(--n600);vertical-align:top}
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

SYSTEMS_PHRASE = "the systems built in this project"   # set by the generator from spec["tp_systems_phrase"], ex: "the QuickBooks setup from this project"

# Seth, Nov 22 2026 2:45 PM CT: the Technology Partner section is two scannable pages in every proposal. Page A is the plan,
# page B the private client page with the demo screenshots. Launch Forte is the subject except the opening paragraph and the
# accountability line. Removed for good: "Software tends to pile up", the business review row, the coverage disclaimer
# paragraph, the specialist line and any dollar savings claim. Backups only "confirms they are running", never that restores work.
def monthly():
    return [
        ("Checks your systems.", "The website, forms, automations and %s are checked, and each result is recorded with a date." % SYSTEMS_PHRASE),
        ("Reviews access.", "You get a list of who can get into what, with former staff and old accounts marked."),
        ("Checks backups.", "Where a system supports backups, Launch Forte confirms they are running. Where it doesn't, the update says so."),
        ("Reviews subscriptions.", "You get a list of what you pay for, with overlaps and unused tools marked."),
        ("Keeps an improvement list.", "You approve an item and Launch Forte makes the change."),
        ("Sends the monthly update.", "It covers what was checked, what was handled and what needs your decision."),
    ]

ACCOUNTABILITY = "I answer for the changes I make and for what I report, and I tell you plainly when something is outside what the plan covers."

def page_a():
    items = "".join('<li><b>%s</b> %s</li>' % (k, v) for k, v in monthly())
    return f'''<h2 class="sec" style="margin-bottom:10pt">Your Technology Partner</h2>
<p class="tp-lead">After I build this, I would be happy to keep helping with the technology side of your business too. For {_price()} a month, I check the systems we agree to cover, review what is working and what needs attention, and look through your software for improvements worth making. You get a monthly update even if you have not asked me for anything new.</p>
<div class="tp-price"><div class="amt">{_price()}<span>a month</span></div><div class="txt">Month to month. Cancel anytime. Your accounts stay yours.</div></div>
<div class="tp-h3">Every month, Launch Forte:</div>
<ul class="tp-list">{items}</ul>
<p class="tp-p"><b>Unlimited everyday requests.</b> Send any automation, integration, report, fix or question, with no limit on how many. Launch Forte works one active request at a time and finishes each before the next. New standalone projects like this one are quoted separately.</p>
<p class="tp-p"><b>Accountability.</b> {ACCOUNTABILITY}</p>'''

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
