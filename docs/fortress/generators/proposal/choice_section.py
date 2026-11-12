"""Renders the 'Choose how to start' page for proposals (template v13). Numbers come ONLY from purchase_choice.calculate()."""
from purchase_choice import usd

CSS = """
.pc { width:100%; }
.pc:after { content:""; display:block; clear:both; }
.pcc { float:left; width:246pt; border:1pt solid var(--border-strong); border-radius:6pt; padding:12pt 15pt 11pt 15pt; height:280pt; background:var(--paper); }
.pcc.r { float:right; }
.pcc .pt { font-family:var(--display); font-size:7pt; font-weight:600; letter-spacing:.14em; text-transform:uppercase; color:var(--accent); margin-bottom:4pt; }
.pcc .pn { font-family:var(--display); font-size:14pt; font-weight:600; letter-spacing:-.015em; color:var(--ink); margin-bottom:3pt; }
.pcc .ps { font-size:8.3pt; line-height:1.45; color:var(--n600); margin-bottom:6pt; min-height:33pt; }
.pcc .pb { font-family:var(--display); font-size:24pt; font-weight:500; letter-spacing:-.025em; color:var(--ink); line-height:1.05; }
.pcc .pbs { font-size:8pt; color:var(--n500); margin:2pt 0 9pt 0; }
.pcc .rw { display:table; width:100%; border-top:1pt solid var(--border); padding:3.6pt 0; }
.pcc .rw .k { display:table-cell; font-size:8pt; color:var(--n600); }
.pcc .rw .v { display:table-cell; text-align:right; font-family:var(--display); font-size:8.6pt; font-weight:600; color:var(--ink); width:92pt; }
.pcc .rw.tot .k, .pcc .rw.tot .v { color:var(--ink); font-weight:600; }
.pcn { font-size:8pt; line-height:1.5; color:var(--n600); margin-top:7pt; }
.pcn b { color:var(--ink); font-weight:600; }
.same { border-top:1pt solid var(--border-strong); padding:8pt 0 0 0; margin-top:12pt; font-size:8.8pt; line-height:1.55; color:var(--n600); }
.same b { color:var(--ink); font-weight:600; }
.pwhy { margin-top:11pt; }
.pwhy .gi { float:left; width:236pt; border-top:1pt solid var(--border-strong); padding:4pt 0 3.5pt 0; }
.pwhy .gi.r { float:right; }
.pwhy .gi p { font-size:7.9pt; line-height:1.4; color:var(--n600); }
.pwhy .gi p b { color:var(--ink); font-weight:600; }
.pwhy:after { content:""; display:block; clear:both; }
"""

def body(calc):
    """Inner HTML of the optional payment choice. The standalone $500 service is shown as its own line, never folded into the hero figure."""
    assert calc["offer_both"], "choice page rendered without an approved calculation"
    o, b = calc["build_and_own"], calc["build_and_partner"]
    n = b["installments"]
    prem = ("" if b["premium_cents"] == 0 else
            f'<div class="rw"><span class="k">Additional cost of spreading the payments</span><span class="v">{usd(b["premium_cents"])}</span></div>')
    return f'''<h2 class="sec" style="margin-bottom:8pt">Optional: spread the project payment</h2>
<p class="lead" style="margin-bottom:9pt;font-size:9.6pt;line-height:1.5">The usual way to buy is the fixed price above. If you would rather spread the project cost, you can. This choice is only about how you pay for the project. The Technology Partner service is separate, and you can say yes or no to it either way.</p>
<div class="pc">
  <div class="pcc">
    <div class="pt">Fixed price</div><div class="pn">Build &amp; Own</div>
    <div class="ps">Pay the fixed project price and own the finished work.</div>
    <div class="pb">{usd(o["project_cents"])}</div><div class="pbs">fixed project price</div>
    <div class="rw"><span class="k">Payment</span><span class="v">50% to start, 50% on delivery</span></div>
    <div class="rw"><span class="k">Monthly commitment</span><span class="v">None</span></div>
    <div class="rw tot"><span class="k">Total project cost</span><span class="v">{usd(o["project_cents"])}</span></div>
    <div class="pcn"><b>Technology Partner:</b> optional, {usd(b["service_monthly_cents"])} a month, added whenever you want it. Month to month, cancel anytime.</div>
  </div>
  <div class="pcc r">
    <div class="pt">Optional</div><div class="pn">Build &amp; Partner</div>
    <div class="ps">The same project, paid over {n} monthly installments.</div>
    <div class="pb">{usd(b["installment_cents"])}<span style="font-size:10pt;font-weight:500"> a month</span></div><div class="pbs">project installment, for {n} months</div>
    <div class="rw"><span class="k">Installments</span><span class="v">{n} x {usd(b["installment_cents"])}</span></div>
    {prem}
    <div class="rw tot"><span class="k">Total project cost</span><span class="v">{usd(b["project_total_cents"])}</span></div>
    <div class="rw"><span class="k">After the last installment</span><span class="v">Project paid off</span></div>
    <div class="pcn"><b>The commitment:</b> the {n} installments are owed on the written schedule and can be prepaid any time at no penalty. Cancelling the Technology Partner service does not cancel the project balance.</div>
  </div>
</div>
<div class="same"><b>Spreading the payments costs more.</b> The fixed price is {usd(o["project_cents"])}. Paying over {n} months adds {usd(b["premium_cents"])}, so the project totals {usd(b["project_total_cents"])}. You can pay the remaining balance early at no penalty.</div>
<div class="same" style="margin-top:7pt"><b>If you also add the Technology Partner service</b> ({usd(b["service_monthly_cents"])} a month, month to month, cancel anytime), your monthly total during the {n} installments is {usd(b["combined_monthly_cents"])}: {usd(b["installment_cents"])} for the project plus {usd(b["service_monthly_cents"])} for the service. After the last installment the project is paid off and the service continues at {usd(b["service_monthly_cents"])} a month, or stops if you cancel it.</div>
<div class="same" style="margin-top:7pt"><b>Identical in both:</b> every outcome in this proposal, the scope, testing, handover documentation, one walkthrough, 30 days of support, and ownership of everything delivered and paid for. Third party tool costs stay yours. No member discount applies to a financed project.</div>'''

def render(calc, page_no, total_pages, project_label="the same scoped project"):
    return f'''
<div class="page">
  <div class="hdr"><img src="launch-forte-dark.png"><span class="ix"><b>{page_no}</b> / Payment choice</span></div>
  <div class="eyebrow"><div class="dot"></div><div class="t">Optional <b>&middot; Same project</b></div><div class="rule" style="width:292pt"></div></div>
  {body(calc)}
  <div class="ftr"><span class="l">Seth Forte / Launch Forte</span><span class="c">Accept by reply. First milestone initiates work.</span><span class="r">{page_no} / {total_pages}</span></div>
</div>
'''
