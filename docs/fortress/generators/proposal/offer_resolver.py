"""Card 538: Python mirror of lib/gateway/offer-resolver.ts (rule technology-partner-offer, sections 4 and 8).
Held to the same cases in offer-resolver-cases.json. Never returns a price or wording."""

def _none(reason):
    return {"offer_plan": False, "variant": "none", "financing": False, "reason": reason}

def resolve_offer(i):
    if not i["rules_verified"]:
        return _none("The offer text could not be verified, so the plan is not added. The rest of the document is written without it.")
    if i["seth_opt_out"] or i["buyer_status"] == "opted_out":
        return _none("Seth opted this buyer out, so the plan is not offered.")
    if i["platform"] == "upwork":
        return _none("This buyer is on Upwork, so no off platform plan or price is offered.")
    if i["signed_agreement"] or i["buyer_status"] == "active_client":
        return _none("A signed agreement or current retainer is in force, so terms are not changed and the plan is a Seth decision.")
    if i["buyer_status"] == "unknown":
        return _none("Buyer eligibility is unknown, so the plan is not offered.")
    if i["doc_type"] in ("proposal", "quote"):
        if not i["scope_approved"]:
            return _none("The scope is not approved yet, so the plan is not added.")
        return {"offer_plan": True, "variant": "proposal_full", "financing": bool(i["financing_enabled"]),
                "reason": "Project first at its fixed price, then the optional plan."}
    if i["doc_type"] == "audit":
        return {"offer_plan": True, "variant": "audit_closing", "financing": False, "reason": "One short optional closing section tied to the findings."}
    return {"offer_plan": True, "variant": "mention_only", "financing": False, "reason": "Know the plan. Mention it only when triggered."}

def rules_verified(facts):
    """facts: the dict read from the canonical rule (offer_source), or None. Verified means ok, not stale, with a price and both rule shas."""
    return bool(facts and facts.get("ok") is True and facts.get("stale") is not True and isinstance(facts.get("plan_price_per_month"), int)
                and facts["plan_price_per_month"] > 0 and facts["plan_price_per_month"] != 750 and facts.get("offer_rule_sha12") and facts.get("pricing_rule_sha12"))
