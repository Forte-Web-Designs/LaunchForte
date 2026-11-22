"""The Technology Partner closing section for every document that goes out (Seth, Nov 22 2026 hard rule).

Proposals, audits, handoff guides, architecture documents and every other client document end with the Technology Partner
section, and that section shows what the client page really looks like: the canonical screenshots of the Northline sample
page, captured by code after every production deploy (dashboard scripts/product-assets/tp-page-shots.py) and stored in
product-assets/tp-page/current/. Generators read only those files. Nothing here draws a mockup.

Fail closed: if the set is missing, incomplete, altered, or older than the design version the live site states
(https://my.launchforte.com/design-version.json), TpPageUnavailable is raised and no document is written.

    import tp_page
    shots = tp_page.load("/tmp/build")          # downloads and checks the set, returns local paths
    html = tp_page.page_html(shots)             # "Your private client portal"
    problems = tp_page.lint(text)               # captions and plan copy against the BRAIN wording rules
"""
import hashlib
import json
import os
import re
import subprocess
import urllib.request

STORE = "https://xndccqxgqobezzfuadni.supabase.co/storage/v1/object/public/product-assets/tp-page/current/"
LIVE_VERSION = "https://my.launchforte.com/design-version.json"
DEMO_LINK = "https://my.launchforte.com/demo"
SAMPLE_LABEL = "Sample page for a fictional business."
VIEWS = ["overview", "handled", "systems", "edition", "documents", "requests"]
DEVICES = ["desktop", "phone"]

# One line each, plain words (Seth Nov 22 2026 item 3).
CAPTIONS = {
    "overview": "Everything I checked this month, with dates",
    "handled": "What I handled, each with the day it was done",
    "systems": "Each of your systems and when I last looked at it",
    "edition": "News from your industry and what it means for you",
    "documents": "Every document I have sent you, in one place",
    "requests": "What you asked for and where each one stands",
}

# Captions and plan copy are checked like any client claim (Seth Nov 22 2026 item 6, BRAIN client-page-truth and the Client
# Document Hard Rules): no monitoring, protection or guarantee wording, no security status, nothing AI related.
BANNED = [
    (r"\bmonitor(s|ed|ing)?\b", "monitoring wording"),
    (r"\bprotect(s|ed|ing|ion)?\b", "protection wording"),
    (r"\bguarantee(s|d)?\b", "guarantee wording"),
    (r"\b24/7\b|\baround the clock\b", "always on wording"),
    (r"\b(secure|safe from|fully secure)\b", "security claim"),
    (r"\bverified healthy\b|\bcritical, act now\b|\ball clear\b", "status words the page does not use"),
    (r"\bAI\b|\bartificial intelligence\b", "AI wording"),
    (r";", "semicolon"),
    (u"[–—]", "dash"),
]


class TpPageUnavailable(RuntimeError):
    pass


def _get(url, timeout=30):
    req = urllib.request.Request(url, headers={"user-agent": "LaunchForteGenerator/1.0", "cache-control": "no-cache"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def current_design_version(dashboard_checkout=None):
    """The design version the live client page is built from. The live file first; a dashboard checkout only when the live
    file is not deployed yet, and then only from the checked out code, never typed."""
    try:
        v = json.loads(_get(LIVE_VERSION)).get("design_version", "")
        if re.fullmatch(r"[0-9a-f]{12}", v or ""):
            return v, "live " + LIVE_VERSION
    except Exception:
        pass
    if dashboard_checkout:
        v = subprocess.check_output(["node", "scripts/design-version.mjs", "--print"], cwd=dashboard_checkout).decode().strip()
        head = subprocess.check_output(["git", "rev-parse", "--short=12", "HEAD"], cwd=dashboard_checkout).decode().strip()
        if re.fullmatch(r"[0-9a-f]{12}", v):
            return v, "dashboard checkout at " + head + " (the live design-version.json is not deployed yet)"
    raise TpPageUnavailable("The current design version could not be read (" + LIVE_VERSION + "), so the page screenshots cannot be checked. No document is written.")


def load(dest, dashboard_checkout=None):
    """Download the canonical set into dest and check it. Returns {"manifest", "version_source", "path": {view: {device: file}}}."""
    os.makedirs(dest, exist_ok=True)
    fx = os.environ.get("LF_TP_PAGE_FIXTURE")
    if fx and os.environ.get("LF_TEST") == "1":
        # Tests only: blank images with a manifest, never a client document (the QA report names the source FIXTURE).
        m = json.load(open(os.path.join(fx, "manifest.json")))
        out = {v: {} for v in VIEWS}
        for f in m["files"]:
            src = os.path.join(fx, f["file"])
            data = open(src, "rb").read()
            if hashlib.sha256(data).hexdigest() != f["sha256"]:
                raise TpPageUnavailable("fixture file does not match its manifest: " + f["file"])
            p = os.path.join(dest, "tp-" + f["file"])
            open(p, "wb").write(data)
            out[f["view"]][f["device"]] = p
        return {"manifest": m, "version_source": "FIXTURE (tests only)", "path": out}
    try:
        m = json.loads(_get(STORE + "manifest.json"))
    except Exception as e:
        raise TpPageUnavailable("The page screenshots are missing from product-assets/tp-page/current (" + str(e)[:80] + "). No document is written.")
    want, source = current_design_version(dashboard_checkout)
    if m.get("design_version") != want:
        raise TpPageUnavailable("The page screenshots are from design %s but the page is now %s. Capture a new set (dashboard tp-page-shots) before any document is written." % (m.get("design_version"), want))
    need = {v + "-" + d + ".png" for v in VIEWS for d in DEVICES}
    listed = {f["file"] for f in m.get("files", [])}
    if listed != need:
        raise TpPageUnavailable("The screenshot set is incomplete: " + ", ".join(sorted(need - listed)) or "unexpected files")
    out = {v: {} for v in VIEWS}
    for f in m["files"]:
        data = _get(STORE + f["file"], timeout=60)
        if hashlib.sha256(data).hexdigest() != f["sha256"]:
            raise TpPageUnavailable("Screenshot " + f["file"] + " does not match its manifest. No document is written.")
        p = os.path.join(dest, "tp-" + f["file"])
        open(p, "wb").write(data)
        out[f["view"]][f["device"]] = p
    return {"manifest": m, "version_source": source, "path": out}


def lint(text):
    """Problems in captions or plan copy, empty when clean."""
    hits = []
    for pat, why in BANNED:
        for mm in re.finditer(pat, text, flags=re.I if why != "AI wording" else 0):
            hits.append(why + ": " + text[max(0, mm.start() - 30): mm.end() + 30].replace("\n", " "))
    return hits


def page_html(shots, demo_link=DEMO_LINK, rel=os.path.basename):
    """One page, "Your private client portal" (Seth Nov 22 2026 2:25 PM CT named it): desktop Overview large with the phone Overview beside it, then Your systems and
    the edition small, each with a one line caption. The sample label is inside every shot. rel maps a local path to the src
    the renderer uses (the file name by default, for documents rendered from the same folder)."""
    p = shots["path"]
    for k in ("overview", "systems", "edition"):
        problems = lint(CAPTIONS[k])
        if problems:
            raise TpPageUnavailable("Caption fails the wording check: " + "; ".join(problems))
    cap = lambda k: '<div class="tpw-cap">%s</div>' % CAPTIONS[k]
    return (
        '<h2 class="sec" style="margin-bottom:6pt">Your private client portal</h2>'
        '<p class="tpw-lead">Every client on the plan signs in to a private portal like this one. It shows what I checked, what I handled and what needs you, each with a date, and it is where you send me requests.</p>'
        '<div class="tpw-row">'
        '<div class="tpw-desk"><img src="%s" alt="Overview on a computer">%s</div>'
        '<div class="tpw-phone"><img src="%s" alt="Overview on a phone"></div>'
        '</div>'
        '<div class="tpw-row tpw-small">'
        '<div class="tpw-half"><img src="%s" alt="Your systems">%s</div>'
        '<div class="tpw-half"><img src="%s" alt="Forte Intelligence edition">%s</div>'
        '</div>'
        '<p class="tpw-note">Open the sample yourself at <a href="%s">%s</a>.</p>'
    ) % (rel(p["overview"]["desktop"]), cap("overview"), rel(p["overview"]["phone"]),
         rel(p["systems"]["desktop"]), cap("systems"), rel(p["edition"]["desktop"]), cap("edition"),
         demo_link + "?r=document", demo_link.replace("https://", ""))


CSS = """
.tpw-lead{font-size:10pt;line-height:1.55;color:var(--n600);margin:0 0 10pt 0}
.tpw-row{display:table;width:100%;table-layout:fixed;margin:0 0 8pt 0}
.tpw-desk{display:table-cell;width:76%;padding-right:10pt;vertical-align:top}
.tpw-phone{display:table-cell;width:24%;vertical-align:top}
.tpw-half{display:table-cell;width:50%;vertical-align:top;padding-right:8pt}
.tpw-small .tpw-half:last-child{padding-right:0;padding-left:8pt}
.tpw-row img{width:100%;display:block;border:1pt solid var(--border-strong);border-radius:4pt}
.tpw-cap{font-size:7.8pt;line-height:1.4;color:var(--n500);margin-top:3pt}
.tpw-note{font-size:8.2pt;line-height:1.5;color:var(--n500);margin-top:4pt}
.tpw-note a{color:var(--accent);text-decoration:none}
"""
