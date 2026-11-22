"""One renderer for handoff, audit, architecture, proposal and quote in the layout of the Phase 2 handoff
sent on Nov 19 2026: full bleed dark cover with the detail strip, one page summary with
number tiles, the BOTTOM LINE box and the one line path, numbered SECTION headers with full tables and
figures numbered in reading order, Good to know (Your call, Know), What's next, Support, Appendix.
It calls lf_document and never types a price, plan item or pitch line."""
from __future__ import annotations
import base64, html, json, os, sys
from core import lf_document
from figures import caption

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import tp_page  # the shared Technology Partner closing section (Seth Nov 22 2026)
TPW_CSS = ":root{--n500:#86868b;--n600:#515154;--accent:#0088DB;--border-strong:rgba(0,0,0,0.12)} .tpw h2.sec{margin-top:0}" + tp_page.CSS
CSS = """
@page { size: Letter; margin: 0.6in 0.7in 0.75in; }
@page :first { margin: 0; }
* { box-sizing: border-box; }
body { font-family: Inter, 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 9.6pt; color: #1d1d1f; line-height: 1.5; margin: 0; }
.cover { background: radial-gradient(120% 80% at 70% 0%, #14324e 0%, #0b1220 55%, #070b14 100%); color: #fff; width: 8.5in; height: 11in; padding: 0.6in 0.65in; position: relative; page-break-after: always; overflow: hidden; }
.cover .brand { font-size: 13pt; font-weight: 600; } .cover .brand span { color: #4ab5ed; }
.cover .meta { position: absolute; top: 0.6in; right: 0.65in; text-align: right; font-size: 7.5pt; color: #c9d3e3; line-height: 1.5; }
.cover .kicker { margin-top: 3.1in; font-size: 7pt; letter-spacing: .12em; text-transform: uppercase; color: #c9d3e3; }
.cover .kicker:before { content: ""; display: inline-block; width: 6px; height: 6px; border-radius: 3px; background: #4ab5ed; margin-right: 6px; }
.cover h1 { font-size: 30pt; line-height: 1.12; margin: 10px 0 18px; font-weight: 600; letter-spacing: -0.02em; }
.cover .sub { color: #4ab5ed; font-size: 12.5pt; margin-bottom: 14px; }
.cover .intro { color: #b8c2d6; font-size: 9pt; max-width: 4.6in; }
.strip { position: absolute; left: 0.65in; right: 0.65in; bottom: 0.6in; border-top: 1px solid #2a3850; padding-top: 12px; display: flex; gap: 0.35in; }
.strip div { font-size: 7.5pt; color: #e6ecf5; } .strip b { display: block; font-size: 6.5pt; letter-spacing: .12em; text-transform: uppercase; color: #8796ad; font-weight: 500; margin-bottom: 4px; }
.page { page-break-before: always; }
.kick { font-size: 6.8pt; letter-spacing: .14em; text-transform: uppercase; color: #0088DB; font-weight: 600; margin: 0 0 2px; }
h2 { font-size: 17pt; margin: 0 0 10px; font-weight: 600; letter-spacing: -0.01em; }
h3 { font-size: 10.5pt; margin: 16px 0 6px; }
.tiles { display: flex; gap: 16px; margin: 16px 0 18px; } .tile { flex: 1; }
.tile .v { font-size: 22pt; color: #0088DB; font-weight: 600; line-height: 1.1; } .tile .l { font-size: 7.6pt; color: #3a3a3c; margin-top: 4px; }
.tile .s { font-size: 6.3pt; color: #86868b; margin-top: 3px; }
.box { background: #f5f7fa; border: 1px solid #e3e8ef; border-radius: 8px; padding: 14px 18px; margin: 10px 0; }
.box p { margin: 6px 0 8px; } .box .kick { color: #86868b; }
.oneline { font-size: 9pt; } .oneline .arrow { color: #0088DB; padding: 0 3px; }
table { border-collapse: collapse; width: 100%; margin: 6px 0 4px; font-size: 8.2pt; }
th { text-align: left; font-size: 6.6pt; letter-spacing: .08em; text-transform: uppercase; color: #6e6e73; font-weight: 600; padding: 5px 6px; border-bottom: 1px solid #d2d2d7; }
td { padding: 6px; border-bottom: 1px solid #ececf0; vertical-align: top; } tr { page-break-inside: avoid; }
td.num, th.num { text-align: right; } td.total { color: #0088DB; font-weight: 600; }
.tabhead { font-weight: 600; font-size: 8.6pt; margin: 12px 0 2px; }
.cap { font-size: 7pt; color: #6e6e73; margin: 4px 0 12px; }
.note { border-left: 3px solid #0088DB; padding: 2px 0 2px 10px; margin: 8px 0; color: #3a3a3c; }
.pair { display: flex; gap: 12px; page-break-inside: avoid; } .pair > div { flex: 1; } .pair img { width: 100%; border: 1px solid #e3e8ef; border-radius: 4px; }
.item { margin: 10px 0; page-break-inside: avoid; } .item .tag { font-size: 6.6pt; letter-spacing: .12em; text-transform: uppercase; font-weight: 700; color: #0088DB; margin-right: 6px; }
.item.know .tag { color: #6e6e73; } .item b { font-size: 9pt; } .item p { margin: 3px 0 0; }
.phase { border: 1px solid #d2d2d7; border-radius: 8px; padding: 12px 16px; margin: 10px 0; page-break-inside: avoid; }
.row { display: flex; justify-content: space-between; align-items: baseline; } .row .t { font-weight: 600; font-size: 10pt; } .row .p { color: #0088DB; font-weight: 600; font-size: 10pt; }
.rec { border: 1.5px solid #0088DB; border-radius: 8px; padding: 14px 18px; margin: 12px 0; page-break-inside: avoid; }
.rec ul { margin: 4px 0 8px 16px; padding: 0; } .rec li { margin: 5px 0; }
.quote { border-left: 3px solid #0088DB; padding: 4px 12px; margin: 8px 0; font-style: italic; }
.support { background: #0b1220; color: #e6ecf5; border-radius: 8px; padding: 14px 18px; margin: 16px 0; page-break-inside: avoid; }
.support .kick { color: #4ab5ed; }
.sign p { margin: 2px 0; }
"""


def esc(s):
    return html.escape(str(s))


def _is_num(s):
    v = str(s).replace(",", "").replace("$", "").strip()
    return v.isdigit() or v == "n/a"


def _table(tb, total_last=False):
    out = []
    if tb.get("heading"):
        out.append("<div class='tabhead'>%s</div>" % esc(tb["heading"]))
    cols, rows = tb["columns"], tb["rows"]
    numcol = [i > 0 and all(_is_num(r[i]) for r in rows) for i in range(len(cols))]
    out.append("<table><tr>%s</tr>" % "".join("<th%s>%s</th>" % (" class='num'" if numcol[i] else "", esc(c)) for i, c in enumerate(cols)))
    for r in rows:
        cells = []
        for i, c in enumerate(r):
            cls = (["num"] if numcol[i] else []) + (["total"] if total_last and i == len(r) - 1 and cols[-1].lower() == "total" else [])
            cells.append("<td%s>%s</td>" % (" class='%s'" % " ".join(cls) if cls else "", esc(c)))
        out.append("<tr>%s</tr>" % "".join(cells))
    out.append("</table>")
    return "".join(out)


def _img(path):
    p = path if os.path.isabs(path) else os.path.join(HERE, path)
    return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()


class Doc:
    """Holds the lf_document result and numbers figures in the order they are placed."""
    def __init__(self, record, snapshot, spec):
        self.doc = lf_document(record, spec["doc_type"], snapshot)
        self.m = self.doc["figures_manifest"]
        self.n, self.order = 0, []

    def fig(self, fid):
        f = self.m["figures"][fid]
        self.n += 1
        self.order.append(fid)
        return "".join(_table(t, True) for t in f.get("tables", [])) + "<div class='cap'>%s</div>" % esc(caption(self.n, f))

    def fig_pair(self, a, b):
        cells = []
        for fid in (a, b):
            f = self.m["figures"][fid]
            self.n += 1
            self.order.append(fid)
            cells.append("<div><img src='%s'/><div class='cap'>%s</div></div>" % (_img(f["image"]), esc(caption(self.n, f))))
        return "<div class='pair'>%s</div>" % "".join(cells)


def _whats_next(wn, num):
    h = ["<div class='page'><div class='kick'>Section %02d</div><h2>%s</h2>" % (num, esc(wn["title"]))]
    for b in wn["blocks"]:
        k = b["kind"]
        if k == "quote":
            h.append("<div class='quote'>\"%s\"<br><span style='font-style:normal;color:#6e6e73'>%s, on the first call</span></div>" % (esc(b["text"]), esc(b["who"])))
        elif k == "goals":
            if b.get("intro"):
                h.append("<p>%s</p>" % esc(b["intro"]))
            h.append(_table({"columns": b["columns"], "rows": b["rows"]}))
        elif k == "para":
            h.append("<p>%s</p>" % esc(b["text"]))
        elif k == "phase":
            h.append("<div class='phase'><div class='row'><span class='t'>%s</span><span class='p'>%s</span></div><p>%s</p></div>" % (esc(b["title"]), esc(b["price"]), esc(b["text"])))
        elif k == "recommend":
            r = ["<div class='rec'><div class='kick'>%s</div><div class='row'><span class='t'>%s</span><span class='p'>%s</span></div>" % (esc(b["kicker"]), esc(b["title"]), esc(b["price"])),
                 "<p>%s</p>" % esc(" ".join(b["intro"]))]
            if b["items"]:
                r.append("<p><b>%s</b></p><ul>%s</ul>" % (esc(b["list_intro"]), "".join("<li><b>%s</b> %s</li>" % (esc(i["title"]), esc(i["text"])) for i in b["items"])))
            if b["requests"]:
                r.append("<p><b>%s</b> %s</p>" % (esc(b["requests"][0]), esc(b["requests"][1])))
            if b["fit"]:
                r.append("<p><b>%s</b> %s %s</p>" % (esc(b["fit"][0]), esc(b["fit"][1]), esc(b["honesty"])))
            else:
                r.append("<p>%s</p>" % esc(b["honesty"]))
            r.append("</div>")
            h.append("".join(r))
    return "".join(h)


def build_html(spec: dict, record: dict, snapshot: dict | None) -> tuple[str, dict]:
    d = Doc(record, snapshot, spec)
    c = spec["cover"]
    h = ["<html><head><meta charset='utf-8'><style>%s%s</style></head><body>" % (CSS, TPW_CSS)]
    h.append("<div class='cover'><div class='brand'>Launch <span>Forte</span></div><div class='meta'>%s<br>%s<br>%s</div>"
             "<div class='kicker'>%s</div><h1>%s<br>%s</h1><div class='sub'>%s</div><div class='intro'>%s</div><div class='strip'>%s</div></div>"
             % (esc(spec["doc_label"]), esc(spec["doc_date"]), esc(spec["doc_where"]), esc(c["kicker"]), esc(c["client"]), esc(c["title"]),
                esc(c["subtitle"]), esc(c["intro"]), "".join("<div><b>%s</b>%s</div>" % (esc(l), "<br>".join(esc(x) for x in v)) for l, v in c["strip"])))
    s = spec["summary"]
    tiles = "".join("<div class='tile'><div class='v'>%s</div><div class='l'>%s</div><div class='s'>%s, read %s</div></div>"
                    % (esc(t["value"]), esc(t["label"]), esc(t["source"]), esc(t["read_at"])) for t in d.m["tiles"])
    h.append("<div><div class='kick'>Summary</div><h2>One page summary</h2><p>%s</p><div class='tiles'>%s</div>" % (esc(s["intro"]), tiles))
    if s.get("bottom_line"):
        h.append("<div class='box'><div class='kick'>Bottom line</div>%s</div>" % "".join("<p><b>%s</b> %s</p>" % (esc(a), esc(b)) for a, b in s["bottom_line"]))
    if s.get("one_line"):
        h.append("<h3>A new lead today, in one line</h3><div class='box oneline'>%s</div>" % "<span class='arrow'> to </span>".join(("<b>%s</b>" if i == 0 else "%s") % esc(x) for i, x in enumerate(s["one_line"])))
    h.append("</div>")
    num = 0
    if spec["doc_type"] in ("proposal", "quote"):
        pr = record["project"]
        num += 1
        lines = [[l["text"], "$%s" % f"{l['price']:,}"] for l in pr["lines"]] + [["Total, fixed price", "$%s" % f"{pr['fixed_price']:,}"]]
        h.append("<div class='page'><div class='kick'>Section %02d</div><h2>The project and its fixed price</h2><p>%s</p>%s<p>%s</p>"
                 % (num, esc(pr["name"]), _table({"columns": ["What you get", "Price by line"], "rows": lines}), esc(pr["payment"])))
        if d.m["baseline"]:
            h.append("<h3>Where things stand today</h3>" + _table({"columns": ["What", "Today", "Read from"], "rows": [[b["label"], b["value"], "%s, %s" % (b["source"], b["read_at"])] for b in d.m["baseline"]]}))
        elif d.m["week_one_measurements"]:
            h.append("<h3>What Launch Forte measures in week one</h3><p>Launch Forte does not have access to your accounts yet, so these are measured in the first week and reported before anything changes:</p><ul>%s</ul>" % "".join("<li>%s</li>" % esc(x) for x in d.m["week_one_measurements"]))
        h.append("</div>")
    for sec in spec.get("sections", []):
        num += 1
        h.append("<div class='page'><div class='kick'>Section %02d</div><h2>%s</h2>" % (num, esc(sec["title"])))
        if sec.get("subhead") and not sec.get("tables"):
            h.append("<h3>%s</h3>" % esc(sec["subhead"]))
        h += ["<p>%s</p>" % esc(p) for p in sec.get("paras", [])]
        h += ["<div class='note'>%s</div>" % esc(n) for n in sec.get("notes", []) if sec.get("figures") and sec["title"] != "Your pipelines"]
        for tb in sec.get("tables", []):
            h.append(_table(tb))
        h += ["<p class='cap'>%s</p>" % esc(p) for p in sec.get("after_tables", [])]
        if sec.get("subhead") and sec.get("tables"):
            h.append("<h3>%s</h3>" % esc(sec["subhead"]))
        for fid in sec.get("figures", []):
            h.append(d.fig(fid))
        if sec["title"] == "Your pipelines":
            h += ["<div class='note'>%s</div>" % esc(n) for n in sec.get("notes", [])]
        for t, body in sec.get("after", []):
            h.append("<h3>%s</h3>%s" % (esc(t), "<p>%s</p>" % esc(body) if body else ""))
        h += ["<div class='note'>%s</div>" % esc(n) for n in sec.get("notes_after", [])]
        if sec.get("figure_pair"):
            h.append(d.fig_pair(*sec["figure_pair"]))
        for tag, title, body in sec.get("items", []):
            h.append("<div class='item%s'><span class='tag'>%s</span><b>%s</b><p>%s</p></div>" % (" know" if tag == "Know" else "", esc(tag), esc(title), esc(body)))
        h.append("</div>")
    support = "<div class='support'><div class='kick'>Support</div>%s</div>" % esc(spec["support"]) if spec.get("support") else ""
    if d.doc["whats_next"]:
        num += 1
        h.append(_whats_next(d.doc["whats_next"], num) + support + "</div>")
        # Seth, Nov 22 2026 hard rule: every document that offers the Technology Partner plan closes with real screenshots of
        # the sample client portal from product-assets/tp-page. tp_page.load fails closed, so no document goes out with a
        # missing or out of date set.
        shots = tp_page.load(os.path.join(HERE, ".tp-page"), dashboard_checkout=os.environ.get("LF_DASHBOARD_CHECKOUT"))
        num += 1
        h.append("<div class='page tpw'><div class='kick'>Section %02d</div>%s</div>" % (num, tp_page.page_html(shots, rel=_img)))
        tm = shots["manifest"]
        d.doc["tp_page"] = {"design_version": tm.get("design_version"), "captured_at": tm.get("captured_at"), "checked_against": shots["version_source"]}
    elif support:
        h.append(support)
    ap = spec.get("appendix")
    if ap:
        h.append("<div class='page'><div class='kick'>Appendix</div><h2>%s</h2>%s<div class='sign'>%s</div></div>"
                 % (esc(ap.get("title", "Appendix")), _table({"columns": ["Item", "Detail"], "rows": ap["rows"]}) if ap.get("rows") else "",
                    "".join("<p>%s</p>" % esc(x) for x in ap.get("signoff", []))))
    h.append("</body></html>")
    d.doc["figure_order"] = d.order
    return "\n".join(h), d.doc


def to_pdf(html_text: str, out_pdf: str, footer_mid: str):
    from playwright.sync_api import sync_playwright
    foot = ("<div style='font-family:Helvetica,Arial;font-size:6.5px;color:#86868b;width:100%%;padding:0 0.7in;display:flex;justify-content:space-between'>"
            "<span>Seth Forte / Launch Forte</span><span>%s</span><span class='pageNumber'></span></div>" % html.escape(footer_mid))
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = b.new_page()
        pg.set_content(html_text, wait_until="load")
        pg.pdf(path=out_pdf, prefer_css_page_size=True, print_background=True, display_header_footer=True,
               header_template="<span></span>", footer_template=foot)
        b.close()


if __name__ == "__main__":
    spec_p, rec_p, snap, out = sys.argv[1:5]
    spec = json.load(open(spec_p))
    snapshot = None if snap == "UNAVAILABLE" else json.load(open(snap))
    text, doc = build_html(spec, json.load(open(rec_p)), snapshot)
    open(out.replace(".pdf", ".html"), "w").write(text)
    to_pdf(text, out, "%s · %s" % (spec["cover"]["client"], spec["doc_label"]))
    json.dump(doc, open(out.replace(".pdf", ".lf_document.json"), "w"), indent=1)
    print(out, doc["resolver"]["verdict"], doc["figures_manifest"]["status"], doc["figure_order"])
