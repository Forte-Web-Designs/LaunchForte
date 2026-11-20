// Card 538 item A. Tests the two Cockpit offer nodes (Offer Inputs, Offer Decision) around the ONE resolver,
// POST /api/offer/resolve. The decision itself is tested in launchforte-dashboard (lib/gateway/offer-resolver.test); here a stub
// answers with the shared case's expected output, so this proves the nodes pass the right inputs and never add a plan or price
// on their own. Usage: node cockpit-offer-decision-test.js [path to offer-resolver-cases.json]
const fs = require('fs'), path = require('path');
const inSrc = fs.readFileSync(path.join(__dirname, 'cockpit-offer-inputs-node.js'), 'utf8');
const decSrc = fs.readFileSync(path.join(__dirname, 'cockpit-offer-decision-node.js'), 'utf8');
const casesPath = process.argv[2] || process.env.OFFER_CASES || '/home/claude/launchforte-dashboard/lib/gateway/offer-resolver-cases.json';
const cases = JSON.parse(fs.readFileSync(casesPath, 'utf8'));
const good = { ok: true, stale: false, plan_price_per_month: 500, member_discount_pct: 30, offer_rule_sha12: 'fe21a96233cf', pricing_rule_sha12: 'bf40e201ea00' };
const mk = (m) => ({ first: () => ({ json: m }) });
function run(src, json, nodes) { return new Function('$json', '$', src)(json, (n) => mk(nodes[n]))[0].json; }
function pipe(rule, make, gate, resp) {
  const nodes = { 'Make Run': make, 'Price Gate': gate };
  const a = run(inSrc, rule, nodes); nodes['Offer Inputs'] = a;
  return { body: a.resolve_body, out: run(decSrc, resp, nodes) };
}
let bad = 0;
function check(n, c, d) { console.log((c ? 'PASS ' : 'FAIL ') + n + (d ? '  ' + d : '')); if (!c) bad++; }
cases.forEach((c) => {
  const r = pipe(c.in.rules_verified ? good : { ok: false, reason: 'rule missing' }, c.in, { quote_total: 4900 }, Object.assign({ ok: true }, c.out));
  const o = r.out.offer;
  check('shared case: ' + c.name, o.offer_plan === c.out.offer_plan && o.variant === (c.out.offer_plan || !c.in.rules_verified ? c.out.variant : c.out.variant) && o.financing === c.out.financing && r.body.doc_type === c.in.doc_type && r.body.platform === c.in.platform);
});
const direct = { platform: 'direct', buyer_status: 'prospect', scope_approved: true };
const yes = { ok: true, offer_plan: true, variant: 'whats_next', financing: false, reason: 'ok' };
let r = pipe(good, direct, { quote_total: 4900 }, yes);
check('plan offered only with a valid rule and a yes from the resolver, price read from the rule', r.out.offer.offer_plan && r.out.offer.plan_price_per_month === 500 && r.out.quote_total === 4900);
check('Upwork months and override are forwarded', (b => b.upwork_first_contact_months === 8 && b.seth_override_on_card === true)(pipe(good, Object.assign({}, direct, { platform: 'upwork', upwork_first_contact_months: 8, seth_override_on_card: true }), {}, yes).body));
check('resolver unreachable (empty body): no plan, no price', (o => !o.offer_plan && o.plan_price_per_month === null)(pipe(good, direct, {}, {}).out.offer));
check('resolver 401 body: no plan', !pipe(good, direct, {}, { ok: false, offer_plan: false, variant: 'none', reason: 'Unauthorized' }).out.offer.offer_plan);
check('stale rule even when resolver says yes: no plan', !pipe(Object.assign({}, good, { stale: true }), direct, {}, yes).out.offer.offer_plan);
check('retired 750 plan in the rule: no plan', !pipe(Object.assign({}, good, { plan_price_per_month: 750 }), direct, {}, yes).out.offer.offer_plan);
check('rule read failed (error object): no plan, no sha', (o => !o.offer_plan && o.offer_rule_sha12 === null)(pipe({ error: { message: 'ETIMEDOUT' } }, direct, {}, yes).out.offer));
console.log(bad ? bad + ' FAILED' : 'ALL PASS'); process.exit(bad ? 1 : 0);
