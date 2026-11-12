"""Launch Forte purchase choice calculator (Pricing Standard v2.6).
Deterministic. Every number derives from the approved quote. Fails closed.
All money is integer cents; no float arithmetic on money."""
from dataclasses import dataclass, field

import offer_source

def _service_cents():
    """The plan fee comes from the canonical rule (offer_source), never typed. No verified rule means no calculation."""
    c = offer_source.service_cents()
    if c is None:
        raise RuntimeError("The Technology Partner plan could not be read from the canonical rule, so no purchase choice is calculated.")
    return c
MEMBER_DISCOUNT_PCT = 30
DISCOUNT_AFTER_PAID_MONTHS = 3
ALLOWED_TERMS = (6, 9, 12, 18, 24)
MAX_PREMIUM_PCT = 15           # financing premium cap, shown explicitly to buyer

class Refusal(Exception):
    """Plain-words reason Build & Partner cannot be offered. Fixed price stays."""

@dataclass
class Quote:
    approved_total_cents: int
    scope_approved: bool = False
    platform: str = "direct"            # "direct" | "upwork" | "unknown"
    agreement_reviewed: bool = False    # installment terms reviewed by Seth/counsel
    experiment_enabled: bool = False    # Seth enabled for this proposal
    buyer_status: str = "unknown"       # "prospect" | "active_signed" | "opted_out" | "unknown"
    third_party_cents: int = 0          # pass-through, never financed or marked up
    premium_pct: int = 0                # explicit, shown to buyer
    installments: int = 12
    existing_discount_applied: bool = False

def refusal_reason(q: Quote):
    if not q.scope_approved: return "Scope is not approved, so no installment price can exist."
    if q.approved_total_cents <= 0: return "No approved project price."
    if q.platform == "upwork": return "Upwork contract: billing stays on platform milestones. No installment offer."
    if q.platform != "direct": return "Platform unknown. Fixed price only."
    if q.buyer_status == "unknown": return "Buyer eligibility unknown. Fixed price only."
    if q.buyer_status == "active_signed": return "Signed agreement in force. Existing terms are unchanged; no installment offer."
    if q.buyer_status == "opted_out": return "Buyer opted out of the Technology Partner service."
    if not q.agreement_reviewed: return "Installment agreement terms are not reviewed. Fixed price only."
    if not q.experiment_enabled: return "Build & Partner is not enabled for this proposal."
    if q.installments not in ALLOWED_TERMS: return "Installment count is not an approved term."
    if not 0 <= q.premium_pct <= MAX_PREMIUM_PCT: return "Financing premium outside the approved range."
    if q.existing_discount_applied: return "Member discount already applied; it cannot apply to a financed project."
    return None

def _round_up_cents(n, d):  # ceiling division
    return -(-n // d)

def calculate(q: Quote):
    r = refusal_reason(q)
    own = {"label": "Build & Own", "project_cents": q.approved_total_cents,
           "third_party_cents": q.third_party_cents,
           "total_cents": q.approved_total_cents + q.third_party_cents}
    if r:
        return {"offer_both": False, "refusal": r, "build_and_own": own}
    base = q.approved_total_cents
    financed_total = base + _round_up_cents(base * q.premium_pct, 100)
    inst = _round_up_cents(financed_total, q.installments)
    project_total = inst * q.installments          # exact sum of payments
    combined = inst + _service_cents()
    return {"offer_both": True, "refusal": None, "build_and_own": own,
        "build_and_partner": {"label": "Build & Partner",
            "installment_cents": inst, "installments": q.installments,
            "project_total_cents": project_total,
            "premium_cents": project_total - base,
            "service_monthly_cents": _service_cents(),
            "combined_monthly_cents": combined,
            "term_total_cents": project_total + _service_cents() * q.installments,
            "service_total_over_term_cents": _service_cents() * q.installments,
            "third_party_cents": q.third_party_cents,
            "member_discount_applies": False,
            "after_payoff": "Installments end. Service continues at %s/month, or stops; month to month, cancel anytime." % offer_source.price_text(),
            }}

def member_discount(price_cents, completed_paid_months, financed=False, already_applied=False, new_fixed_quote=True):
    """30% member discount: only a NEW fixed price quote, only after 3 completed paid months,
    never on a financed project, never twice."""
    if financed: raise Refusal("Member discount cannot apply to a financed project.")
    if already_applied: raise Refusal("Member discount already applied to this project.")
    if not new_fixed_quote: raise Refusal("Discount applies only to a new fixed price quote.")
    if completed_paid_months < DISCOUNT_AFTER_PAID_MONTHS:
        raise Refusal("Member discount starts after 3 completed paid months.")
    return price_cents - price_cents * MEMBER_DISCOUNT_PCT // 100

def cancel_after(q: Quote, month: int):
    """Buyer cancels the $500 service in `month`. Project installments are a project
    obligation, not service MRR: they continue (or are paid off per agreement)."""
    res = calculate(q)
    if not res["offer_both"]: return res
    b = res["build_and_partner"]
    n = min(month, b["installments"])
    paid_proj = b["installment_cents"] * n
    return {"service_paid_cents": _service_cents() * month, "project_paid_cents": paid_proj,
            "project_remaining_cents": b["project_total_cents"] - paid_proj,
            "note": "Service cancels without penalty. Remaining project balance is still owed per the written schedule; it can be prepaid at any time with no penalty."}

def after_final(q: Quote, month: int):
    res = calculate(q)
    if not res["offer_both"]: return res
    b = res["build_and_partner"]
    due_project = b["installment_cents"] if month <= b["installments"] else 0
    return {"project_due_cents": due_project, "service_due_cents": _service_cents(), "total_due_cents": due_project + _service_cents()}

def usd(c): return f"${c/100:,.0f}" if c % 100 == 0 else f"${c/100:,.2f}"
