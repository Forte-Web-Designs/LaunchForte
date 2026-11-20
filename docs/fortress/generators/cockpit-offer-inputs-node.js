/* Card 538 item A (Nov 19 2026). Builds the body for POST /api/offer/resolve. The decision itself is made by the dashboard resolver (rule technology-partner-offer v2), never here. */
const __safe = function (fn, d) { try { const v = fn(); return v == null ? d : v; } catch (e) { return d; } };
const __run = __safe(function () { return $('Make Run').first().json; }, {});
const __rule = $json || {};
const __valid = !!(__rule && __rule.ok === true && __rule.stale !== true && Number.isInteger(__rule.plan_price_per_month) && __rule.plan_price_per_month > 0 && __rule.plan_price_per_month !== 750 && __rule.offer_rule_sha12 && __rule.pricing_rule_sha12);
const __platform = String(__run.platform || __run.source || 'upwork').toLowerCase() === 'direct' ? 'direct' : 'upwork';
const __months = (typeof __run.upwork_first_contact_months === 'number' && isFinite(__run.upwork_first_contact_months)) ? __run.upwork_first_contact_months : null;
const body = {
  doc_type: String(__run.doc_type || 'proposal'),
  buyer_status: String(__run.buyer_status || (__platform === 'upwork' ? 'prospect' : 'unknown')),
  platform: __platform,
  upwork_first_contact_months: __months,
  seth_override_on_card: __run.seth_override_on_card === true,
  signed_agreement: __run.signed_agreement === true,
  kept_project_based: __run.kept_project_based === true,
  seth_opt_out: __run.seth_opt_out === true,
  scope_approved: __run.scope_approved === true,
  financing_enabled: __run.financing_enabled === true,
  rules_verified: __valid
};
return [{ json: { resolve_body: body, rule: __rule, rules_verified: __valid, platform: __platform } }];
