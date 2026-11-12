/* Card 535 (Nov 12 2026). n8n Code node "Offer Decision", placed after "Read Offer Rule" (GET /api/offer/rule) and before "Prompt of Record".
   One resolver decision per run, from the canonical rule read this run. It never types a price: a plan price is carried only when the rule
   read is valid AND the resolver says offer_plan. A bad, stale or missing read means rules_verified false and the plan is never added
   (rule technology-partner-offer, section 7). The resolver below mirrors lib/gateway/offer-resolver.ts and is held to the same shared cases. */
const __none = function (reason) { return { offer_plan: false, variant: 'none', financing: false, reason: reason }; };
const __resolve = function (i) {
  if (!i.rules_verified) return __none('The offer text could not be verified, so the plan is not added. The rest of the document is written without it.');
  if (i.seth_opt_out || i.buyer_status === 'opted_out') return __none('Seth opted this buyer out, so the plan is not offered.');
  if (i.platform === 'upwork') return __none('This buyer is on Upwork, so no off platform plan or price is offered.');
  if (i.signed_agreement || i.buyer_status === 'active_client') return __none('A signed agreement or current retainer is in force, so terms are not changed and the plan is a Seth decision.');
  if (i.buyer_status === 'unknown') return __none('Buyer eligibility is unknown, so the plan is not offered.');
  if (i.doc_type === 'proposal' || i.doc_type === 'quote') {
    if (!i.scope_approved) return __none('The scope is not approved yet, so the plan is not added.');
    return { offer_plan: true, variant: 'proposal_full', financing: !!i.financing_enabled, reason: i.financing_enabled ? 'Project first at its fixed price, then the optional plan. Financing is on for this proposal and sits beside the plan, never in place of it.' : 'Project first at its fixed price, then the optional plan. Financing is off, which does not hide the plan.' };
  }
  if (i.doc_type === 'audit') return { offer_plan: true, variant: 'audit_closing', financing: false, reason: 'One short optional closing section tied to the findings. No sales banner.' };
  return { offer_plan: true, variant: 'mention_only', financing: false, reason: 'Know the plan. Mention it only when the client\'s request, an outcome or Seth\'s direction triggers it. Nothing sends automatically.' };
};
const __valid = function (r) {
  return !!(r && r.ok === true && r.stale !== true && Number.isInteger(r.plan_price_per_month) && r.plan_price_per_month > 0
    && r.plan_price_per_month !== 750 && r.offer_rule_sha12 && r.pricing_rule_sha12);
};
const __safe = function (fn, d) { try { const v = fn(); return v == null ? d : v; } catch (e) { return d; } };
const __gate = __safe(function () { return $('Price Gate').first().json; }, {});
const __run = __safe(function () { return $('Make Run').first().json; }, {});
const __rule = $json || {};
const __ok = __valid(__rule);
/* This pipeline answers Upwork postings (the job row is read from upwork_jobs by uid). A run that says otherwise is resolved as it says. */
const __platform = String(__run.platform || __run.source || 'upwork').toLowerCase() === 'direct' ? 'direct' : 'upwork';
const __input = {
  doc_type: String(__run.doc_type || 'proposal'),
  buyer_status: String(__run.buyer_status || (__platform === 'upwork' ? 'prospect' : 'unknown')),
  platform: __platform,
  signed_agreement: __run.signed_agreement === true,
  seth_opt_out: __run.seth_opt_out === true,
  scope_approved: __run.scope_approved === true,
  financing_enabled: __run.financing_enabled === true,
  rules_verified: __ok
};
const __res = __resolve(__input);
const offer = {
  offer_plan: __res.offer_plan, variant: __res.variant, financing: __res.financing, reason: __res.reason,
  rules_verified: __ok,
  plan_price_per_month: (__ok && __res.offer_plan) ? __rule.plan_price_per_month : null,
  offer_rule_sha12: __ok ? __rule.offer_rule_sha12 : null,
  pricing_rule_sha12: __ok ? __rule.pricing_rule_sha12 : null,
  platform: __platform
};
return [{ json: Object.assign({}, __gate, { offer: offer }) }];
