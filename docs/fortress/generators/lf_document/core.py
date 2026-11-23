"""lf_document (Fortress work order 1, Seth Nov 19 2026; revised 15:07 CT to match the Phase 2
handoff sent on Nov 19).

One call: account record + doc_type + live sources -> resolver verdict and reason, the drafted
"What's next" (rule technology-partner-offer v2 section 6, in the shape of the Phase 2 handoff Seth sent on Nov 19),
and the figures manifest for the doc type (rule client-document-figures). Read scope only.

Nothing here types a price, discount or plan item that could drift:
  * plan price, member discount and positioning are parsed from Pricing Standard section 10 at run time,
  * the monthly list is built from the service status table at run time. OPERATIONAL and PARTIAL rows
    are shown, NOT BUILT rows never are, and rows are ordered by MONTHLY_ORDER so the monthly review,
    the private page and the industry briefing lead automatically the day their rows go OPERATIONAL,
  * client facts (business goals, next phase, covered systems) come from the record with their refs.
"""
from __future__ import annotations
import re

BUILT_FROM = {"technology-partner-offer": "9f3961f5b8bf", "pricing": "bf40e201ea00"}
DOC_TYPES = ("handoff", "audit", "architecture", "proposal", "quote")
MENTION_ONLY = ("client_update", "sop", "email", "reply", "upwork_reply", "status")
RETIRED_PRICES = {750}
SHOWABLE = ("OPERATIONAL", "PARTIAL")

# Every month, even with no requests. Order is the client's order of value; a row that is not
# OPERATIONAL or PARTIAL in the live status table is skipped. "private_page" and "industry_briefing"
# have no status row yet, so they stay out until the other builds add their rows.
MONTHLY_ORDER = [9, "private_page", "industry_briefing", 5, 8, 6, 3, 7, 4, 2]

# Each item: a bold title and one concrete sentence. {covered} and {where} come from the record.
CLIENT_WORDS = {
    9: ("Your monthly Technology and Opportunities Review.",
        "A short report: what Launch Forte checked across {where}, what was fixed, how your numbers moved against last month, and the one or two improvements worth making next."),
    "private_page": ("Your client portal.",
                     "One place to see what Launch Forte took care of this month: checks done, issues fixed, improvements shipped and anything waiting on your decision."),
    "industry_briefing": ("What's changing that matters to you.",
                          "Anything changing in your tools or your industry that affects you, in plain words."),
    5: ("Launch Forte checks what it built for you.",
        "{covered}. If something breaks, Launch Forte fixes it."),
    8: ("The next worthwhile improvement.",
        "Launch Forte looks across {where} for what's worth fixing or building next, and tells you what it found and where it came from."),
    6: ("A second look at anything new.",
        "If you or your team build or change something, Launch Forte reviews it before it causes trouble."),
    3: ("Logins and access.",
        "A regular look at who has access to your accounts, so old logins get closed."),
    7: ("The software you pay for.",
        "A regular look at your subscriptions and renewals, so you aren't paying for tools nobody uses."),
    4: ("Your backups.",
        "Checking that your important data is backed up and that a restore would work."),
    2: ("Everyday IT help.",
        "Email, calendars, app accounts and shared files."),
}
# Titles a Lead must never see in a document while their row is not supported.
ITEM_TITLES = {k: v[0].rstrip(".") for k, v in CLIENT_WORDS.items()}


class SourcesUnavailable(Exception):
    pass


# ---------------------------------------------------------------- live source readers

def plan_price(sec10: str | None) -> int | None:
    m = re.search(r"One plan, \*\*\$(\d[\d,]*) a month\*\*", sec10 or "")
    if not m:
        return None
    p = int(m.group(1).replace(",", ""))
    return None if p <= 0 or p in RETIRED_PRICES else p


def member_discount(sec10: str | None) -> int | None:
    m = re.search(r"receives a (\d+)% member discount", sec10 or "")
    return int(m.group(1)) if m else None


def positioning(sec10: str | None) -> str | None:
    m = re.search(r"Positioning: ([^.]+)\.", sec10 or "")
    return m.group(1).strip() if m else None


def rules_verified(snapshot: dict | None) -> tuple[bool, str]:
    if not snapshot:
        return False, "The rule store could not be read."
    o, p = snapshot.get("offer_rule") or {}, snapshot.get("pricing_rule") or {}
    if o.get("sha12") != BUILT_FROM["technology-partner-offer"]:
        return False, "The offer rule on hand is not the version this generator was built from."
    if p.get("sha12") != BUILT_FROM["pricing"]:
        return False, "The pricing rule on hand is not the version this generator was built from."
    if plan_price(p.get("section_10_text")) is None:
        return False, "The plan price could not be read from the pricing rule."
    if not (snapshot.get("service_status") or {}).get("rows"):
        return False, "The service status table could not be read."
    return True, "Rules read and matched."


def seth_override(comments: list[dict], client_name: str) -> dict | None:
    """Seth's written override on the client's card: names the client and a date (rule v2, 4.3)."""
    for c in comments or []:
        t = c.get("text", "")
        if "SETH OVERRIDE" in t and "Upwork" in t and client_name.lower() in t.lower():
            d = re.search(r"Date:\s*(\d{4}-\d{2}-\d{2})", t)
            if d:
                return {"date": d.group(1), "ref": c.get("ref")}
    return None


# ---------------------------------------------------------------- resolver v2 (rule sections 4 and 8)

def _no(reason, variant="none"):
    return {"offer_plan": False, "variant": variant, "financing": False, "reason": reason, "verdict": "NO PLAN"}


def resolve(i: dict) -> dict:
    """Mirror of lib/gateway/technology-partner.ts v2 (branch fortress/538-v2-whats-next). Never returns a price."""
    if not i.get("rules_verified"):
        return _no("The offer text could not be verified, so the plan is not added. The rest of the document is written without it.")
    if i.get("seth_opt_out") or i.get("buyer_status") == "opted_out":
        return _no("Seth opted this buyer out, so the plan is not offered.")
    # v3 (Seth Nov 23 2026): the Upwork exclusion is removed; the platform no longer decides the plan.
    if i.get("signed_agreement"):
        return _no("A signed agreement or current retainer is in force, so terms are not changed and the plan is a Seth decision.")
    if i.get("kept_project_based"):
        return _no("This client is kept project based, so the plan is not offered.")
    if i.get("buyer_status") in (None, "unknown", "unsuitable"):
        return _no("Buyer eligibility is unknown or unsuitable, so it fails closed and the plan is not offered.")
    dt = i.get("doc_type")
    if dt in MENTION_ONLY:
        return _no("Know the plan. Mention it only when the client, an outcome or Seth triggers it.", "mention_only")
    if dt not in DOC_TYPES:
        return _no("Unknown document type, so it fails closed.")
    if dt in ("proposal", "quote") and not i.get("scope_approved"):
        return _no("The scope is not approved yet, so the plan is not added.")
    why = ""
    return {"offer_plan": True, "variant": "whats_next", "verdict": "OFFER",
            "financing": bool(i.get("financing_enabled")) and dt in ("proposal", "quote") and i.get("platform") != "upwork",  # Pricing Standard 11.3(b)
            "reason": why + "Eligible %s, so it ends with a tailored What's next section, last before support and the appendix." % dt}


# ---------------------------------------------------------------- What's next

def status_map(rows):
    return {r["n"]: r["status"] for r in rows if not r.get("internal")}


def monthly_items(status_rows: list[dict], record: dict) -> list[dict]:
    st = status_map(status_rows)
    fill = {"covered": record.get("covered_systems", "The systems on the plan"),
            "where": record.get("where", "your accounts")}
    out = []
    for key in MONTHLY_ORDER:
        if st.get(key) in SHOWABLE:
            title, text = CLIENT_WORDS[key]
            out.append({"key": key, "status": st[key], "title": title, "text": text.format(**fill)})
    return out


def _join(items):
    items = [i.rstrip(".") for i in items]
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def draft_whats_next(record: dict, sec10: str, status_rows: list[dict]) -> dict:
    """Shape of section 07 of the Phase 2 handoff sent Nov 19. Every client fact carries its ref."""
    price, disc, pos = plan_price(sec10), member_discount(sec10), positioning(sec10)
    st = status_map(status_rows)
    goals = record.get("business_goals") or []
    also = record.get("also_open") or []
    nxt = record.get("next_phase")
    blocks = []

    # 1. The client's own business goals and where each stands (never housekeeping)
    if record.get("goals_intro"):
        blocks.append({"kind": "para", "text": record["goals_intro"], "refs": [g["ref"] for g in goals]})
    for q in record.get("client_quotes") or []:
        if q.get("full_sentence"):  # a client is quoted only as a whole sentence in their own words
            blocks.append({"kind": "quote", "text": q["text"], "who": q["who"], "ref": q["ref"]})
    if goals:
        blocks.append({"kind": "goals", "intro": None, "columns": record.get("goals_columns", ["What you named", "Where it stands"]),
                       "rows": [[g["goal"], g["status"]] for g in goals], "refs": [g["ref"] for g in goals]})
    if also:
        blocks.append({"kind": "para", "text": "Also open from the first call: %s." % _join([a["text"] for a in also]),
                       "refs": [a["ref"] for a in also]})

    # 2. Next fixed price phase first, only if on record
    if nxt and nxt.get("price") and nxt.get("ref"):
        blocks.append({"kind": "para", "text": "There are two ways to keep going."})
        blocks.append({"kind": "phase", "title": nxt["name"], "price": "$%s" % f"{nxt['price']:,}",
                       "text": nxt.get("description", ""), "ref": nxt["ref"]})

    # 3. The recommendation
    items = monthly_items(status_rows, record)
    rec = {"kind": "recommend", "kicker": "What Launch Forte recommends for you",
           "title": "Technology Partner" + (": " + pos.replace("your business technology", "your technology") if pos else ""),
           "price": "$%s a month" % f"{price:,}",
           "intro": ["After I build this, I would be happy to keep helping with the technology side of your business too.",
                     "Month to month, cancel anytime, and you keep everything Launch Forte builds. Instead of you noticing a problem and hiring Launch Forte for a project, Launch Forte is already in your accounts every month, keeping what it built working and building the next thing."],
           "list_intro": "Every month, even if you never send a request:" if items else None,
           "items": items, "requests": None, "fit": None, "honesty": None,
           "refs": ["pricing section 10", "service status table"]}
    if st.get(1) in SHOWABLE:
        direct = " one at a time, and you can ask directly" if st.get(10) in SHOWABLE else " one at a time"
        bigger = "Bigger builds are still quoted separately"
        if disc:
            bigger += ", and after three paid months they come with %d%% off" % disc
        rec["requests"] = ("And on top of that, as many everyday requests as you want.",
                           "New automations, fixes, reports, integrations, a new staff member who needs set up, or a quick question. Launch Forte works through them%s. %s." % (direct, bigger))
    # 4. Why it fits: the open business goals, never chores
    layer = record.get("next_layer")
    if layer:
        rec["fit"] = ("Why it fits %s." % record.get("client_short", record["client_name"]),
                      "Your next layer is exactly this kind of work: %s. Launch Forte already knows %s inside and out, so there's no ramp up and nothing to explain twice."
                      % (layer.rstrip("."), record.get("accounts_phrase", "your accounts")))
    # 5. Honesty line
    rec["honesty"] = "One person who knows your systems end to end and answers for every change made and every result reported. Questions, fixes and decisions all go to the same place, so nothing falls between vendors."  # Seth Nov 22 2026 2:53 PM CT, no limitation wording in the TP section
    blocks.append(rec)
    # 6. Close
    blocks.append({"kind": "para", "text": "If %s sounds good, reply to the email or book 15 minutes to set it up." % ("either" if nxt else "it")})
    return {"title": "What's next", "blocks": blocks, "price": price, "discount": disc,
            "monthly_keys": [i["key"] for i in items]}


# ---------------------------------------------------------------- the one call

def lf_document(record: dict, doc_type: str, snapshot: dict | None) -> dict:
    ok, why = rules_verified(snapshot)
    inputs = dict(record.get("resolver_inputs") or {})
    inputs.update(doc_type=doc_type, rules_verified=ok)
    if inputs.get("platform") == "upwork":
        inputs["seth_override_on_card"] = bool(seth_override(record.get("card_comments"), record["client_name"]))
    verdict = resolve(inputs)
    if not ok:
        verdict["reason"] = why + " " + verdict["reason"]
    out = {"account": record["client_name"], "doc_type": doc_type, "resolver": verdict,
           "rules": {"verified": ok, "detail": why, "built_from": BUILT_FROM,
                     "on_hand": None if not snapshot else {
                         "technology-partner-offer": (snapshot.get("offer_rule") or {}).get("sha12"),
                         "pricing": (snapshot.get("pricing_rule") or {}).get("sha12")}},
           "whats_next": None}
    if verdict["variant"] == "whats_next":
        out["whats_next"] = draft_whats_next(record, snapshot["pricing_rule"]["section_10_text"], snapshot["service_status"]["rows"])
    from figures import manifest_for
    out["figures_manifest"] = manifest_for(doc_type, record)
    return out
