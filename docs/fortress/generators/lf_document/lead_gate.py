"""Lead gate for generated client documents (work order 1, item 4). Deterministic, read only.
FAIL when: an eligible document is missing What's next; What's next appears where the resolver said
no; a plan item the service status table does not support; a figure without source and date; or a
client document word check hit (rule client-document-hard-rules) outside the allowed cases."""
from __future__ import annotations
import html, re
from core import CLIENT_WORDS, SHOWABLE, ITEM_TITLES

WORDS = ["Pricing Standard", "standard", "v2", "Config", "Judged", "Surface", "Risk", "Extra system", "ledger", "tier",
         "proven", "library", "lf_", "rate", "qty", "browser", "session", "endpoint", "401", "API", "Fortress", "Claude",
         "agent", "AI", "retainer", "package"]
PRONOUNS = ["we", "our", "us"]
ALLOWED_WE = ["when we first talked", "we can grab 15 minutes", "you and i", "our first call"]
PUNCT = {"—": "em dash", "–": "en dash", "--": "double hyphen", "~": "tilde", "→": "arrow", "e.g.": "e.g."}
CAPTION = re.compile(r"Figure (\d+)\. .+?, read from your accounts on [A-Z][a-z]+ \d{1,2}, \d{4}\. No contact details\.", re.S)


def _strip_quotes(t):
    return re.sub(r'"[^"]*"', '""', t)


def word_check(text: str) -> list[str]:
    hits = []
    body = text.replace("Seth Forte / Launch Forte", "")
    body = re.sub(r"Seth Forte\s+Launch Forte", "", body)  # the sign off
    for w in WORDS:
        pat = re.escape(w) if not w[0].isalnum() or w.endswith("_") else r"\b%s\b" % re.escape(w)
        for m in re.finditer(pat, body, flags=0 if w in ("AI", "API", "Risk", "Config", "Surface", "Judged") else re.I):
            hits.append("word '%s' near: %s" % (w, body[max(0, m.start() - 30):m.end() + 30].replace("\n", " ")))
    if re.search(r"\bSeth\b", body):
        hits.append("third person 'Seth' in body text")
    unq = _strip_quotes(body).lower()
    for a in ALLOWED_WE:
        unq = unq.replace(a, "")
    for p in PRONOUNS:
        for m in re.finditer(r"\b%s\b" % p, unq):
            hits.append("pronoun '%s' near: %s" % (p, unq[max(0, m.start() - 30):m.end() + 30]))
    for k, name in PUNCT.items():
        if k in text:
            hits.append(name)
    return hits


def to_text(t: str) -> str:
    """Gate reads what the client reads: tags stripped and entities decoded (HTML), or PDF text as is."""
    if "<html" in t:
        t = re.sub(r"<style.*?</style>", " ", t, flags=re.S)
        t = re.sub(r"<[^>]+>", " ", t)
        t = html.unescape(t)
    return re.sub(r"\s+", " ", t)


def check(text: str, doc: dict, snapshot: dict | None) -> dict:
    text = to_text(text)
    fails = []
    has_wn = "What's next" in text
    eligible = doc["resolver"]["variant"] == "whats_next"
    if eligible and not has_wn:
        fails.append("Eligible document is missing the What's next section.")
    if has_wn and not eligible:
        fails.append("What's next appears but the resolver said no: %s" % doc["resolver"]["reason"])
    st = {r["n"]: r["status"] for r in (snapshot or {}).get("service_status", {}).get("rows", []) if not r.get("internal")}
    supported = {k for k in CLIENT_WORDS if st.get(k) in SHOWABLE}
    # a plan item whose status row is not OPERATIONAL or PARTIAL must never appear
    for k, title in ITEM_TITLES.items():
        if k not in supported and title in text:
            fails.append("Plan item '%s' is not supported by the service status table but appears in the document." % title)
    if has_wn and eligible:
        rec = next(b for b in doc["whats_next"]["blocks"] if b["kind"] == "recommend")
        for i in rec["items"]:
            if i["key"] not in supported:
                fails.append("Plan item not supported by the service status table: %s" % i["title"])
            elif _norm(i["title"]) not in _norm(text):
                fails.append("Plan item missing from the rendered document: %s" % i["title"])
        if "Technology Partner" not in text or "What I'd recommend for you".upper().replace(" ", "") not in _norm(text).upper().replace(" ", ""):
            fails.append("What's next does not name and recommend Technology Partner.")
        wn_at = text.find("What's next")
        for later in ("Appendix", "APPENDIX"):
            at = text.find(later)
            if at != -1 and at < wn_at:
                fails.append("What's next is not the last section before the appendix.")
    for p in doc["figures_manifest"]["problems"]:
        fails.append("Figures: " + p)
    nums = [int(n) for n in re.findall(r"Figure (\d+)\.", text)]
    if nums != sorted(nums) or nums != list(range(1, len(nums) + 1)):
        fails.append("Figures are not numbered 1 to N in reading order: %s" % nums)
    for m in re.finditer(r"Figure (\d+)\.", text):
        if not CAPTION.match(text[m.start():m.start() + 300]):
            fails.append("Figure %s caption is not in the dated form or has no read date." % m.group(1))
    for t in doc["figures_manifest"]["tiles"]:
        if t["value"] not in text:
            fails.append("Summary tile missing: %s" % t["label"])
    if doc["doc_type"] in ("proposal", "quote") and has_wn:
        fp = text.find("fixed price")
        if fp == -1 or fp > text.find("What's next"):
            fails.append("Proposal does not show the project and its fixed price before What's next.")
    words = word_check(text)
    fails += ["Word check: " + w for w in words]
    return {"verdict": "PASS" if not fails else "FAIL", "failures": fails, "word_check": "CLEAN" if not words else "%d hits" % len(words)}


def _norm(t):
    return re.sub(r"\s+", " ", t)
