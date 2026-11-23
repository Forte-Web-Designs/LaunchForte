"""Card 538 / 629: Python mirror of lib/gateway/offer-resolver.ts (rule technology-partner-offer v3, sha 9f3961f5b8bf, sections 4 and 8; Seth Nov 23 2026 removed the Upwork exclusion).
Held to the same cases in offer-resolver-cases.json. Never returns a price or wording.

Inputs (section 8): doc_type, buyer_status, platform, upwork_first_contact_months, seth_override_on_card, signed_agreement,
kept_project_based, seth_opt_out, scope_approved, financing_enabled, rules_verified.
Variants: whats_next, mention_only, none. The retired variants proposal_full and audit_closing are read as whats_next."""

WHATS_NEXT_DOCS = ("proposal", "quote", "audit", "handoff", "architecture")
RETIRED_VARIANTS = {"proposal_full": "whats_next", "audit_closing": "whats_next"}

def normalize_variant(v):
    return RETIRED_VARIANTS.get(v, v)

def _none(reason):
    return {"offer_plan": False, "variant": "none", "financing": False, "reason": reason}

def resolve_offer(i):
    """Evaluated in the order of rule section 4. The first line that matches decides, and every NO fails closed."""
    if not i.get("rules_verified"):
        return _none("The offer text could not be verified, so the plan is not added. The rest of the document is written without it.")
    if i.get("seth_opt_out") or i.get("buyer_status") == "opted_out":
        return _none("Seth opted this buyer out, so the plan is not offered.")
    # v3 (Seth Nov 23 2026): the platform the buyer came through no longer decides the plan.
    if i.get("signed_agreement") or i.get("buyer_status") == "active_client":
        return _none("A signed agreement or current retainer is in force, so terms are not changed and the plan is a Seth decision.")
    if i.get("kept_project_based"):
        return _none("This client is kept project based, so the plan is not offered.")
    if i.get("buyer_status") in (None, "unknown", "unsuitable"):
        return _none("Buyer eligibility is unknown or unsuitable, so the plan is not offered.")
    dt = i.get("doc_type")
    if dt in ("proposal", "quote") and not i.get("scope_approved"):
        return _none("The scope is not approved yet, so the plan is not added.")
    if dt in WHATS_NEXT_DOCS:
        why = ""
        return {"offer_plan": True, "variant": "whats_next",
                "financing": bool(i.get("financing_enabled")) and dt in ("proposal", "quote") and i.get("platform") != "upwork",  # Pricing Standard 11.3(b)
                "reason": why + "Eligible, so the document ends with a tailored What's next section, last before any appendix."}
    return {"offer_plan": True, "variant": "mention_only", "financing": False, "reason": "Know the plan. Mention it only when the client, an outcome or Seth triggers it."}

def rules_verified(facts):
    """facts: the dict read from the canonical rule (offer_source), or None. Verified means ok, not stale, with a price and both rule shas."""
    return bool(facts and facts.get("ok") is True and facts.get("stale") is not True and isinstance(facts.get("plan_price_per_month"), int)
                and facts["plan_price_per_month"] > 0 and facts["plan_price_per_month"] != 750 and facts.get("offer_rule_sha12") and facts.get("pricing_rule_sha12"))
