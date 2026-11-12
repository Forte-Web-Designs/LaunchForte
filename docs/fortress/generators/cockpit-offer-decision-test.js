const fs = require('fs'), path = require('path');
const src = fs.readFileSync(path.join(__dirname, 'cockpit-offer-decision-node.js'), 'utf8');
const cases = JSON.parse(fs.readFileSync('/home/claude/launchforte-dashboard/lib/gateway/offer-resolver-cases.json', 'utf8'));
const good = { ok: true, stale: false, plan_price_per_month: 500, member_discount_pct: 30, offer_rule_sha12: '6c16db653830', pricing_rule_sha12: 'bf40e201ea00', read_at: 'x' };
function run(rule, make, gate) {
  const $ = function (n) { return { first: function () { return { json: n === 'Make Run' ? make : gate }; } }; };
  const f = new Function('$json', '$', src);
  return f(rule, $)[0].json;
}
let bad = 0; const rows = [];
function check(n, c, detail) { rows.push((c ? 'PASS ' : 'FAIL ') + n + (detail ? '  ' + detail : '')); if (!c) bad++; }
// the 15 shared resolver cases, through the node
cases.forEach(function (c) {
  const make = Object.assign({}, c.in, { platform: c.in.platform });
  const o = run(c.in.rules_verified ? good : { ok: false, reason: 'rule missing' }, make, { quote_total: 4900 }).offer;
  check('shared case: ' + c.name, o.offer_plan === c.out.offer_plan && o.variant === c.out.variant && o.financing === c.out.financing);
});
// Cockpit specific
let o = run(good, { uid: 'u1' }, { quote_total: 4900 });
check('default Upwork run with a valid rule: no plan, price absent', o.offer.offer_plan === false && o.offer.plan_price_per_month === null && o.offer.reason.indexOf('Upwork') >= 0, o.offer.reason);
check('Price Gate output passes through untouched', o.quote_total === 4900);
o = run(good, { platform: 'direct', buyer_status: 'prospect', scope_approved: true }, {});
check('direct approved prospect, financing off: plan offered at the price from the rule', o.offer.offer_plan && o.offer.plan_price_per_month === 500 && o.offer.financing === false && o.offer.offer_rule_sha12 === '6c16db653830');
o = run(good, { platform: 'direct', buyer_status: 'prospect', scope_approved: true, financing_enabled: true }, {});
check('financing on keeps the plan beside it', o.offer.offer_plan && o.offer.financing === true);
check('rule read failed (HTTP error object): no plan, no price, no sha', (o = run({ error: { message: 'connect ETIMEDOUT' } }, { platform: 'direct', buyer_status: 'prospect', scope_approved: true }, {})).offer.offer_plan === false && o.offer.plan_price_per_month === null && o.offer.rules_verified === false);
check('401 or 503 body (ok false): no plan', run({ ok: false, reason: 'rule missing' }, { platform: 'direct', buyer_status: 'prospect', scope_approved: true }, {}).offer.offer_plan === false);
check('stale rule: no plan', run(Object.assign({}, good, { stale: true }), { platform: 'direct', buyer_status: 'prospect', scope_approved: true }, {}).offer.offer_plan === false);
check('retired 750 plan in the rule: no plan', run(Object.assign({}, good, { plan_price_per_month: 750 }), { platform: 'direct', buyer_status: 'prospect', scope_approved: true }, {}).offer.offer_plan === false);
check('empty response: no plan', run({}, { platform: 'direct', buyer_status: 'prospect', scope_approved: true }, {}).offer.offer_plan === false);
check('active client with signed agreement: no plan', run(good, { platform: 'direct', buyer_status: 'active_client', signed_agreement: true, scope_approved: true }, {}).offer.offer_plan === false);
check('opt out: no plan', run(good, { platform: 'direct', buyer_status: 'prospect', seth_opt_out: true, scope_approved: true }, {}).offer.offer_plan === false);
check('unknown eligibility: no plan', run(good, { platform: 'direct', buyer_status: 'unknown', scope_approved: true }, {}).offer.offer_plan === false);
check('unapproved scope: no plan', run(good, { platform: 'direct', buyer_status: 'prospect', scope_approved: false }, {}).offer.offer_plan === false);
const leak = JSON.stringify(run(good, { platform: 'direct', buyer_status: 'prospect', scope_approved: true }, {}).offer);
check('output carries no key, token or customer text', !/x-work-key|CRON|secret|Bearer|@/i.test(leak));
const __code = src.replace(/\/\*[\s\S]*?\*\//g, '').replace(/plan_price_per_month !== 750/, '');
check('node source types no plan price or discount value', !/\b500\b|\b750\b|\b30\b|\$\s?\d/.test(__code));
console.log(rows.join('\n')); console.log('FAILURES: ' + bad); process.exit(bad ? 1 : 0);
