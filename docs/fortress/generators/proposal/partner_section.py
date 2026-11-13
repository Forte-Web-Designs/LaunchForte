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

CONTEXT = {"systems": [], "observations": []}   # buyer specific facts from the approved spec (never invented here)

def configure(context=None):
    """The price is read at render time and rendering raises when the rule is not verified.
    context: {"systems": [names of the client systems this project touches], "observations": [{"text", "source_ref"}]}"""
    global CONTEXT
    CONTEXT = {"systems": list((context or {}).get("systems", [])), "observations": list((context or {}).get("observations", []))}

def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def tailored():
    """One or two sentences that tie the plan to this buyer's own systems and, when approved, a sourced observation.
    Lists never run to exactly three names (Voice Rules): at most two systems are named, the rest are covered by the count."""
    sy = [s for s in CONTEXT["systems"] if str(s).strip()]
    out = ""
    if len(sy) >= 2:
        out += f"<p class=\"tp-p\">For you, I would start with the systems this project connects, beginning with {_esc(sy[0])} and {_esc(sy[1])}. I would keep watching how they work together and keep them working as your business changes.</p>"
    elif len(sy) == 1:
        out += f"<p class=\"tp-p\">For you, I would start with the system this project builds on, {_esc(sy[0])}, and keep it working as your business changes.</p>"
    for o in CONTEXT["observations"][:2]:
        if o.get("text") and o.get("source_ref"):
            out += f"<p class=\"tp-p\">{_esc(o['text'])}</p>"
    return out

CSS = """
.tp-notice{margin-top:14pt;padding-top:9pt;border-top:1pt solid var(--border-strong);font-size:10pt;line-height:1.55;color:var(--ink)}

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
.tp-shot{border:1pt solid var(--border-strong);margin:6pt 0 4pt 0;width:260pt}
.tp-shot img{width:100%;display:block}
.tp-cap{font-size:7.8pt;line-height:1.5;color:var(--n500);margin-bottom:10pt;width:300pt}
.tp-terms{font-size:9.4pt;line-height:1.6;color:var(--n700);border-top:1pt solid var(--border-strong);padding-top:9pt;margin-top:6pt}
.tp-terms b{color:var(--ink);font-weight:600}
.tp-next{margin-top:14pt}
.tp-next ol{margin:3pt 0 0 14pt;font-size:9pt;line-height:1.55;color:var(--n600)}
"""

MONTHLY = [
 ("Checking your systems", "I check that the systems we agree to cover are working, such as your website, forms and automations, and I write down what I find."),
 ("Who has access", "I go through who can get into what, and point out former staff or old accounts that still have a way in, with what I would change."),
 ("Backups", "Where a system supports it, I check that it is being backed up and that a restore would work. Where it does not, I tell you."),
 ("Software and subscriptions", "I look through what you are paying for, point out overlaps and things nobody uses, and tell you what I would change. I do not guess at savings."),
 ("Business and technology review", "I look at how the business runs and the systems around it, and tell you what I see: risks, manual work that could go away and the next improvements worth making. What I observed and what I think stay separate, and I put no dollar figure on anything I cannot show."),
 ("Routine improvements", "I keep a short list of things worth improving. You decide which ones I go ahead with, and I handle the changes we agree on."),
]

ARRIVES = [
 ("Monthly Technology Review", "Each month I send a short written review covering what I checked, what I handled, what needs a decision from you and what I would recommend next. We can talk it through on a call if you would like."),
 ("Forte Intelligence", "Each month I also send a short illustrated magazine about your industry and the software and rules around it, with examples from your industry and ideas you may want to try. It is written for your business, and you can ignore it whenever you like."),
]

def page_a():
    rows = "".join(f'<div class="tp-row"><div class="k">{k}</div><div class="v">{v}</div></div>' for k, v in MONTHLY)
    return f'''<h2 class="sec" style="margin-bottom:10pt">Your Technology Partner</h2>
<p class="tp-lead">After I build this, I would be happy to keep helping with the technology side of your business too. For {_price()} a month, I build new automations and integrations when you ask, give you advice on your software and what is worth adopting, keep an eye on the systems we agree to cover and bring you what I find along the way. You get a monthly Technology Review and a copy of Forte Intelligence even if you have not asked me for anything new.</p>
<div class="tp-price"><div class="amt">{_price()}<span>a month</span></div><div class="txt"><b>Optional, and separate from the project.</b> It is month to month, you can cancel anytime, and your accounts stay yours.</div></div>
<p class="tp-p">Software tends to pile up. Accounts stay open after people leave, backups go unchecked, subscriptions renew unnoticed and small problems wait until they are expensive. With this plan, one person is accountable for all of it, and what I build in this project gets looked after instead of left alone.</p>
{tailored()}
<div class="tp-h3">What I take care of each month</div>
<div class="tp-rows">{rows}</div>'''

def page_b(next_html=""):
    return f'''<h2 class="sec" style="margin-bottom:10pt">Unlimited everyday engineering requests</h2>
<p class="tp-lead">Whenever you need an automation, an integration, a report, a fix or help figuring something out, send it my way. There is no limit on how many you send.</p>
<p class="tp-p">I work on one active request at a time, so I can finish it properly before moving on. A larger standalone project, like the one in this proposal, is quoted separately.</p>
<div class="tp-h3" style="margin-top:14pt">What I take responsibility for</div>
<p class="tp-p">I would be your person for the technology side of the business: the software you use, everyday IT questions, integrations, troubleshooting and the decisions that come with all of it. You can reach me directly with a question and I work out what needs doing. I answer for the changes I make and for what I reported, I tell you plainly when something is outside what I cover, and I bring in a specialist when the work calls for one. Monitoring covers the systems we agree on and set up for it.</p>
<p class="tp-p">How much of this runs from the first month depends on the access and tools your accounts allow. I tell you which systems are covered and which are not yet, and I will not call anything healthy that I have not checked.</p>
<div class="tp-h3" style="margin-top:14pt">What arrives every month</div>
<div class="tp-rows">{"".join(f'<div class="tp-row"><div class="k">{k}</div><div class="v">{v}</div></div>' for k, v in ARRIVES)}</div>
<div class="tp-h3" style="margin-top:12pt">What the monthly review looks like</div>
<div class="tp-shot"><img src="{{SHOT}}"></div>
<div class="tp-cap">A sample, with made up information for a fictional business. The update lists what I checked, what I handled and what needs your decision, each with a date.</div>
<div class="tp-terms"><b>{_price()} a month.</b> Month to month, cancel anytime. If you only want the project, that is completely fine too.</div>
{next_html}'''

def next_steps(items):
    return '<div class="tp-next"><div class="label" style="margin-bottom:2pt">Next steps</div><ol>'+"".join(f"<li>{i}</li>" for i in items)+'</ol></div>'


def audit_closing(findings_ref="the findings above"):
    """Card 538: the short optional closing for an audit. Variant audit_closing of the offer resolver. No banner, no price table."""
    return (
        '<h3 class="tpc-h">If you want me around afterwards</h3>'
        '<p class="tpc-p">Everything in this audit stands on its own, and you can take it to any builder you like. '
        'If you would rather have one person keep an eye on these systems and fix things as they come up, I offer that for %s a month. '
        'It is optional, month to month, and you can cancel anytime.</p>'
        '<p class="tpc-p">Each month I check the systems we agreed to cover, review who has access, look at what you are spending on software, '
        'and send you a short note on what I found and what I would change. Everyday engineering requests are included on top, '
        'one active request at a time. Larger projects are quoted separately, like the ones recommended in %s.</p>'
        '<p class="tpc-p">I only report something as checked once I have checked it, and what I can cover depends on the access and tools your team gives me.</p>'
    ) % (offer_source.price_text(), findings_ref)
