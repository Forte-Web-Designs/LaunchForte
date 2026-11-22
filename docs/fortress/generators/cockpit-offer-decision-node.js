/* Card 538 item A (Nov 19 2026). The decision comes from the dashboard resolver (POST /api/offer/resolve, rule technology-partner-offer v2) through "Resolve Offer". This node only merges it with the rule facts read this run and the Price Gate output. It never decides and never types a price: the plan price is carried only when the rule read was valid AND the resolver said offer_plan. Any bad, missing or non-200 answer means no plan (rule section 7). */
const __safe = function (fn, d) { try { const v = fn(); return v == null ? d : v; } catch (e) { return d; } };
const __gate = __safe(function () { return $('Price Gate').first().json; }, {});
const __in = __safe(function () { return $('Offer Inputs').first().json; }, {});
const __rule = __in.rule || {};
const __res = $json || {};
const __answered = __res && __res.ok === true && typeof __res.offer_plan === 'boolean' && typeof __res.variant === 'string';
const __ok = !!__in.rules_verified && __answered;
const __plan = __ok && __res.offer_plan === true;
const offer = {
  offer_plan: __plan,
  variant: __ok ? __res.variant : 'none',
  financing: __ok ? !!__res.financing : false,
  reason: __answered ? String(__res.reason || '') : 'The offer resolver did not answer, so the plan is not added. The rest of the document is written without it.',
  rules_verified: !!__in.rules_verified,
  plan_price_per_month: __plan ? __rule.plan_price_per_month : null,
  offer_rule_sha12: __in.rules_verified ? __rule.offer_rule_sha12 : null,
  pricing_rule_sha12: __in.rules_verified ? __rule.pricing_rule_sha12 : null,
  platform: __in.platform || 'upwork'
};
return [{ json: Object.assign({}, __gate, { offer: offer }) }];
