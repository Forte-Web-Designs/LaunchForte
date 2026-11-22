"""Technology Partner pages for proposals (template v13, editorial layout, v8).
Voice: Seth, first person singular, plain sentences (Voice Rules, Client Document Hard Rules, MCP reference 1960).
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
.tp-next{margin-top:14pt}
.tp-next ol{margin:3pt 0 0 14pt;font-size:9pt;line-height:1.55;color:var(--n600)}
"""

MONTHLY = [
 ("Checking your systems", "Launch Forte checks that the systems on the plan are working, such as your website, forms and automations, and writes down what it finds."),
 ("Who has access", "Launch Forte goes through who can get into what, and points out former staff or old accounts that still have a way in, with what it would change."),
 ("Backups", "Where a system supports it, Launch Forte checks that it is being backed up and that a restore would work. Where it does not, Launch Forte tells you."),
 ("Software and subscriptions", "Launch Forte looks through what you are paying for, points out overlaps and things nobody uses, and tells you what it would change. It does not guess at savings."),
 ("Business and technology review", "Launch Forte looks at how the business runs and the systems around it, and tells you what it sees: risks, manual work that could go away and the next improvements worth making. What was observed and what is opinion stay separate, and no dollar figure goes on anything that cannot be shown."),
 ("Routine improvements", "Launch Forte keeps a short list of things worth improving. You decide which ones go ahead, and Launch Forte handles the changes you approve."),
 ("The monthly update", "Each month Launch Forte sends a short written update covering what was checked, what was handled, what needs a decision from you and what it recommends next. A call to talk it through is there if you would like one."),
]

def page_a():
    rows = "".join(f'<div class="tp-row"><div class="k">{k}</div><div class="v">{v}</div></div>' for k, v in MONTHLY)
    return f'''<h2 class="sec" style="margin-bottom:10pt">Your Technology Partner</h2>
<p class="tp-lead">After I build this, I would be happy to keep helping with the technology side of your business too. For {_price()} a month, I check the systems we agree to cover, review what is working and what needs attention, and look through your software for improvements worth making. You get a monthly update even if you have not asked me for anything new.</p>
<div class="tp-price"><div class="amt">{_price()}<span>a month</span></div><div class="txt"><b>Optional, and separate from the project.</b> It is month to month, you can cancel anytime, and your accounts stay yours.</div></div>
<p class="tp-p">Software tends to pile up. Accounts stay open after people leave, backups go unchecked, subscriptions renew unnoticed and small problems wait until they are expensive. With this plan, one person is accountable for all of it, and what Launch Forte builds in this project gets looked after instead of left alone.</p>
<div class="tp-h3">What Launch Forte takes care of each month</div>
<div class="tp-rows">{rows}</div>'''

def page_b(next_html=""):
    return f'''<h2 class="sec" style="margin-bottom:10pt">Unlimited everyday engineering requests</h2>
<p class="tp-lead">Whenever you need an automation, an integration, a report, a fix or help figuring something out, send it to Launch Forte. There is no limit on how many you send.</p>
<p class="tp-p">Launch Forte works on one active request at a time, so each one is finished properly before the next begins. A larger standalone project, like the one in this proposal, is quoted separately.</p>
<div class="tp-h3" style="margin-top:14pt">What Launch Forte takes responsibility for</div>
<p class="tp-p">Launch Forte would be your partner for the technology side of the business: the software you use, everyday IT questions, integrations, troubleshooting and the decisions that come with all of it. You can send a question directly and Launch Forte works out what needs doing. I answer for the changes I make and for what I report, and I tell you plainly when something is outside what the plan covers. Launch Forte's monthly checks cover the systems we agree on and connect.</p>
<p class="tp-p">How much of this runs from the first month depends on the access and tools your accounts allow. Launch Forte tells you which systems are covered and which are not yet. I will not call anything healthy that I have not checked.</p>
<p class="tp-p">Each month you get a short written update, and your private portal shows what Launch Forte checked, what was handled and what needs your decision, each with a date. The next page shows that portal.</p>
<div class="tp-terms"><b>{_price()} a month.</b> Month to month, cancel anytime.{_billing_note()} If you only want the project, that is completely fine too.</div>
{next_html}'''

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
