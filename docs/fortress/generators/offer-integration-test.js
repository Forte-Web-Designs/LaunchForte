// Card 538: the Cockpit nodes take the plan price from $json.offer_rule (the canonical rule, via /api/offer/rule) and never type it.
// Run: node docs/fortress/generators/offer-integration-test.js
const fs = require("fs"), path = require("path"), assert = require("assert");
const dir = __dirname;
const pricingSrc = fs.readFileSync(path.join(dir, "cockpit-pricing-node.js"), "utf8");
const promptSrc = fs.readFileSync(path.join(dir, "cockpit-prompt-node.js"), "utf8");
const good = { ok: true, stale: false, plan_price_per_month: 500, member_discount_pct: 30, offer_rule_sha12: "6c16db653830", pricing_rule_sha12: "bf40e201ea00" };
const cases = [["live rule", good, 500], ["live rule with a changed price", { ...good, plan_price_per_month: 650 }, 650], ["rule failed", { ok: false, reason: "BRAIN down" }, null], ["stale rule", { ...good, stale: true }, null], ["retired price", { ...good, plan_price_per_month: 750 }, null], ["no rule at all", undefined, null]];
let n = 0;
for (const [name, rule, want] of cases) {
  const json = { evidence_shape: "system-sync", channel: "Direct", job_post: "Keep Shopify, HubSpot, QuickBooks, Airtable and Klaviyo in sync both ways. Six workflows in total." };
  if (rule !== undefined) json.offer_rule = rule;
  const out = new Function("$json", "$", pricingSrc)(json, () => { throw new Error("no node"); });
  const o = (Array.isArray(out) ? out[0].json : out) || {};
  if (want === null) { assert.equal(o.retainer_line, null, name + ": no plan line"); assert.equal(o.retainer_floor, null, name); assert.ok(/UNAVAILABLE/.test(o.offer_status), name); }
  else { assert.equal(o.retainer_floor, want, name); assert.ok(o.retainer_line.includes("$" + want.toLocaleString("en-US") + " a month"), name + ": " + o.retainer_line); assert.ok(/LIVE rule technology-partner-offer sha 6c16db653830/.test(o.offer_status), name); }
  assert.ok(!/750/.test(JSON.stringify({ l: o.retainer_line, f: o.retainer_floor })), name + ": never 750");
  console.log("ok pricing node: " + name); n++;
}
// The prompt node needs the whole workflow (template rows), so its plan sentence is lifted out and run on its own.
const defStart = promptSrc.indexOf("const __OFFER"), defEnd = promptSrc.indexOf("\n", defStart);
const lineStart = promptSrc.indexOf("(__OFFER ? '"), lineEnd = promptSrc.indexOf("\n", lineStart);
const offerDef = promptSrc.slice(defStart, defEnd), offerExpr = promptSrc.slice(lineStart, lineEnd).replace(/,\s*$/, "");
for (const [name, rule, want] of cases) {
  const w = rule === undefined ? {} : { offer_rule: rule };
  const text = new Function("$json", offerDef + "\nreturn " + offerExpr + ";")(w);
  if (want === null) assert.ok(/could not be read from the canonical rule/.test(text) && !/\$\d+ a month/.test(text) && !/750/.test(text), name);
  else { assert.ok(text.includes("$" + want + " a month, month to month, cancel anytime"), name); assert.ok(!/750/.test(text), name); }
  console.log("ok prompt node: " + name); n++;
}
console.log(n + " integration checks passed");
