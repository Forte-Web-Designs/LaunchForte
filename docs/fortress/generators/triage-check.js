#!/usr/bin/env node
// Triage v2 regression.
//
// The seven worked examples in section 7 of the runbook are the acceptance test.
// Each one states the route and the response the system must produce, so each one
// is a fixture with an expected answer rather than a story.
//
// Two of them are run TWICE: once against the registries as they exist today, and
// once against a stubbed registry that contains the proven kit, the paths and the
// fresh rehearsal the runbook assumes. The first run proves the gate is honest
// about today. The second proves the gate opens when the records arrive, which is
// the only way to know the closed door is a record problem and not a code bug.
//
// Usage:  node triage-check.js
// Exit 0 = every assertion holds.

const fs = require('fs');
const path = require('path');

const SRC = fs.readFileSync(path.join(__dirname, 'cockpit-triage-node.js'), 'utf8');

// --- the n8n code-node harness --------------------------------------------
function runNode(job, upstream) {
  const nodes = upstream || {};
  const $ = function (name) {
    if (!(name in nodes)) { const e = new Error('no node ' + name); throw e; }
    const rows = nodes[name];
    return { all: function () { return rows.map(function (r) { return { json: r }; }); },
             first: function () { return { json: rows[0] }; } };
  };
  const fn = new Function('$json', '$', '"use strict";' + SRC);
  return fn(job, $)[0].json;
}

// --- registries, as they actually are today (read from n8n Aug 9) ---------
const TODAY = {
  'Read Shapes (Cockpit)': [
    { shape: 'lead-routing', access_list: 'Netlify team/site collaborator access (or repo access plus deploy rights)' },
    { shape: 'books-reconciliation', access_list: 'Stripe restricted API key, read-only on payouts, balance transactions, charges' },
    { shape: 'system-sync', access_list: 'HubSpot super admin to create a private app with crm.objects.deals, line_items' },
    { shape: 'voice-agent-intake', access_list: 'Twilio account admin access (or a subaccount) with the existing numbers visible' },
    { shape: 'data-collection', access_list: 'Read access to the source system' },
    { shape: 'client-onboarding', access_list: 'GoHighLevel sub-account admin' }
  ],
  // 19 rows, every one status=briefed, proven_minutes=0, stubs="estimated only, nothing built"
  'Read Builds G': [
    { slug: 'dental-voice-brief-0zj6', status: 'briefed', shape_class: 'twilio+voice+sms', proven_minutes: 0, stubs: 'estimated only, nothing built' },
    { slug: 'client-says-we-need-it-3y0c', status: 'briefed', shape_class: 'n8n+quickbooks', proven_minutes: 0, stubs: 'estimated only, nothing built' }
  ],
  // 177 rows; login_state null on all of them, session_last_verified empty on all of them
  'Read Tools KB': [
    { tool: 'hubspot', endpoint_status: 'answered 200', have_credential: 'no', session_last_verified: '', notes: '' },
    { tool: 'quickbooks', endpoint_status: 'exists, requires a key (401)', have_credential: 'no', session_last_verified: '', notes: '' },
    { tool: 'zapier', endpoint_status: '404, the documented endpoint does not exist', have_credential: 'no', session_last_verified: '', notes: '' },
    { tool: 'vapi', endpoint_status: 'answered 200', have_credential: 'no', session_last_verified: '', notes: '' },
    { tool: 'gohighlevel', endpoint_status: 'exists, requires a key (401)', have_credential: 'no', session_last_verified: '', notes: '' },
    { tool: 'apollo', endpoint_status: 'answered 200', have_credential: 'yes', session_last_verified: '', notes: '' }
  ],
  // 14 rows, 4 open + 1 sent; every kind is api_key / shell / reconnect / quota / question / fix / scope
  'Read Blockers': [
    { blocker_id: 'blk-msghap3y-vapi', status: 'open', kind: 'api_key', subject: 'vapi' },
    { blocker_id: 'blk-msghap3y-lookerstudio', status: 'sent', kind: 'api_key', subject: 'looker studio' },
    { blocker_id: 'blk-msghap3y-instantly', status: 'done', kind: 'api_key', subject: 'instantly' }
  ]
};

// --- the same registries, with the lead-list kit actually proven ----------
const fresh = new Date(Date.now() - 3 * 86400000).toISOString();
const PROVEN = JSON.parse(JSON.stringify(TODAY));
PROVEN['Read Shapes (Cockpit)'].push({ shape: 'data-collection-house', access_list: '' });
PROVEN['Read Builds G'].push({
  slug: 'leads-verified-list-house', status: 'proven', shape_class: 'data-collection-house',
  proven_minutes: 12, stubs: 'built end to end, 4 deliveries'
});
PROVEN['Read Tools KB'].push(
  { tool: 'apify', endpoint_status: 'answered 200', have_credential: 'yes', session_last_verified: fresh, notes: '' },
  { tool: 'neverbounce', endpoint_status: 'answered 200', have_credential: 'yes', session_last_verified: fresh, notes: '' }
);

// --- the seven jobs from section 7 ----------------------------------------
const JOBS = [
  { id: 1, label: 'Joel: GHL sponsor signup form with payment',
    job: { title: 'GHL sponsor signup form with payment', job_type: 'FIXED', budget: '100 USD',
      description: 'Need a sponsor signup form built in our GoHighLevel sub-account with payment collection wired to the existing pipeline.',
      skills: 'gohighlevel', client_spend: 1320, client_hires: 10 },
    shape: 'client-onboarding',
    // REVISED Aug 9: the floor is dead. $100 posted against a $132 average is a
    // number the buyer's own history agrees with, so it is believed — short
    // reply, not silence. It still files as a listing candidate.
    expect: { budget_test: 'cheap_room_confirmed', action: 'short_reply', listing_candidate: true, certified: false } },

  { id: '1b', label: 'THE PLACEHOLDER: $50 posted by a buyer who averages $800',
    job: { title: 'Need a HubSpot to Xero invoice sync built', job_type: 'FIXED', budget: '50 USD',
      description: 'We need our hubspot deals to create invoices in xero automatically. About 400 deals a month, needs line items and a reconciliation report.',
      skills: 'hubspot, xero', client_spend: 40000, client_hires: 50, score: 'A' },
    shape: 'system-sync',
    // 50 / 800 = 6% of what they actually pay. That is a required field being
    // filled in. The number is ignored entirely and judge grade carries it.
    expect: { budget_test: 'placeholder_budget', placeholder_budget: true, action: 'full_package', certified: false } },

  { id: '1c', label: 'NO HISTORY: $75 posted by a buyer with no spend at all',
    job: { title: 'Automate our lead handoff', job_type: 'FIXED', budget: '75 USD',
      description: 'We want leads from our forms to route to the right rep automatically with a slack alert. Roughly 200 leads a month.',
      skills: 'slack', client_spend: 0, client_hires: 0, score: 'B' },
    shape: 'lead-routing',
    // Nothing to test the number against. Judge grade alone decides, and B earns
    // the package. A cheap-looking post is never refused on its face.
    expect: { budget_test: 'no_spend_history', action: 'full_package', certified: false } },

  { id: 2, label: 'Verified lead list, 100 leads',
    job: { title: 'Need a verified lead list for my niche, 100 leads', job_type: 'FIXED', budget: '350 USD',
      description: 'I need 100 verified leads in my niche, delivered as a spreadsheet with emails verified. Built from apify scraping and neverbounce verification. No access to anything of mine is needed, just deliver the file.',
      skills: 'lead generation, apify, neverbounce', client_spend: 4200, client_hires: 6 },
    shape: 'data-collection-house',
    expect: { route: 'assisted', certified: false },
    expectProven: { route: 'hands_free_house', certified: true, action: 'lane_held' } },

  { id: 3, label: 'Fix my broken Zapier zap',
    job: { title: 'Fix my broken Zapier zap, it stopped firing', job_type: 'FIXED', budget: '300 USD',
      description: 'Our zapier zap stopped firing last week. Need someone to get into our account and fix it. About 3 steps.',
      skills: 'zapier', client_spend: 900, client_hires: 4 },
    shape: 'alerting',
    expect: { route: 'assisted', action: 'short_reply', budget_test: 'cheap_room_confirmed', room: 'auction', certified: false } },

  { id: 4, label: 'HubSpot expert, hourly',
    job: { title: 'HubSpot expert needed', job_type: 'HOURLY', budget: '30-50/hr',
      description: 'Looking for an ongoing hubspot expert to help with workflows, lists and reporting inside our portal. 10 hours a week.',
      skills: 'hubspot', client_spend: 48000, client_hires: 12 },
    shape: 'system-sync',
    expect: { route: 'assisted', hourly_convert: true, certified: false } },

  { id: 5, label: 'QuickBooks / HubSpot invoice reconciliation',
    job: { title: "Our invoices in QuickBooks don't match what we billed in HubSpot", job_type: 'FIXED', budget: '2000 USD',
      description: 'We have about 400 invoices in quickbooks that do not match the deals we billed in hubspot. Need a reconciliation built so this stops happening every month.',
      skills: 'quickbooks, hubspot', client_spend: 9000, client_hires: 6 },
    shape: 'books-reconciliation',
    expect: { route: 'assisted', action: 'full_package', room: 'value', certified: false } },

  { id: 6, label: 'AI voice agent for after-hours calls',
    job: { title: "Build an AI voice agent for our clinic's after-hours calls", job_type: 'FIXED', budget: '5000 USD',
      description: 'We want an ai voice agent to handle our after-hours calls, book appointments into our system, and escalate emergencies. Established practice, 3 locations.',
      skills: 'vapi, twilio', client_spend: 62000, client_hires: 18 },
    shape: 'voice-agent-intake',
    expect: { route: 'heavy', action: 'full_package', certified: false } },

  { id: 7, label: 'Margaret: invited HubSpot campaign work',
    job: { title: 'HubSpot campaign work for our association', job_type: 'FIXED', budget: '4000 USD',
      description: 'We would love to set up a quick intro call to walk through the campaign work we need in our hubspot portal for the association members.',
      skills: 'hubspot', client_spend: 31000, client_hires: 9, invite: true },
    shape: 'system-sync',
    expect: { route: 'heavy', action: 'full_package', certified: false } }
];

// --- run -------------------------------------------------------------------
let failures = 0;
const eq = (label, got, want) => {
  if (want === undefined) return;
  const ok = got === want;
  if (!ok) { failures++; console.log('    FAIL  ' + label + ': got ' + JSON.stringify(got) + ', wanted ' + JSON.stringify(want)); }
  else { console.log('    ok    ' + label + ' = ' + JSON.stringify(got)); }
};

const MAP = { action: 'triage_action', hourly_convert: 'triage_hourly_convert' };
const showBudget = (o) => '    budget_test=' + o.budget_test + '  posted=' + o.posted_budget_amount +
  '  avg=' + o.buyer_avg_per_hire + '  ratio=' + o.posted_vs_avg_ratio;
const check = (out, expect) => {
  Object.keys(expect).forEach(k => eq(k, out[MAP[k] || k], expect[k]));
  if (out.triage_rules_ok !== true) { failures++; console.log('    FAIL  triage_rules_ok is not true'); }
};

console.log('TRIAGE v2 — the seven jobs, against the registries AS THEY ARE TODAY\n');
JOBS.forEach(j => {
  const out = runNode(Object.assign({ evidence_shape: j.shape }, j.job), TODAY);
  console.log('  Job ' + j.id + ': ' + j.label);
  console.log('    route=' + out.route + '  action=' + out.triage_action + '  psm=' + out.psm_estimate +
              '  room=' + out.room + '  avg=' + out.buyer_avg_per_hire + '  certified=' + out.certified);
  console.log(showBudget(out));
  console.log('    failing checks: ' + (out.certified_failed_check || 'none'));
  check(out, j.expect);
  console.log('');
});

console.log('\nTHE GATE OPENS WHEN THE RECORDS ARRIVE (same code, stubbed proven registry)\n');
JOBS.filter(j => j.expectProven).forEach(j => {
  const out = runNode(Object.assign({ evidence_shape: j.shape }, j.job), PROVEN);
  console.log('  Job ' + j.id + ': ' + j.label);
  console.log('    route=' + out.route + '  action=' + out.triage_action + '  certified=' + out.certified +
              '  bid=' + out.triage_bid + '  lane_enabled=' + out.lane_enabled);
  check(out, j.expectProven);
  console.log('');
});

// --- the invariants that must hold no matter what the corpus contains ------
console.log('\nINVARIANTS\n');
const inv = (label, ok, detail) => {
  if (!ok) failures++;
  console.log('  ' + (ok ? 'ok  ' : 'FAIL') + '  ' + label + (detail ? '  — ' + detail : ''));
};

// A certified job can never need a call or their account.
const all = JOBS.map(j => runNode(Object.assign({ evidence_shape: j.shape }, j.job), PROVEN));
inv('no certified job needs a call or a client account',
  all.every(o => !(o.certified && (o.triage_needs_call || o.triage_needs_client_account))));
inv('the lane never bids while it ships OFF',
  all.every(o => o.triage_action !== 'lane_bid'));
// THE FLOOR IS DEAD. The old invariant said the opposite of this one; it is
// replaced rather than deleted, because the reversal is the point.
inv('no posted number, however small, ever ends a job on its own',
  JOBS.map(j => runNode(Object.assign({ evidence_shape: j.shape }, j.job), TODAY))
      .every(o => o.triage_action !== 'no_bid' || o.route === 'hands_free_shape_client_access'));
// A placeholder job may still get a short reply — but only for a reason that
// would have applied with no budget stated at all. The number itself never costs
// it anything.
inv('a placeholder budget never reduces the treatment on its own',
  JOBS.map(j => runNode(Object.assign({ evidence_shape: j.shape }, j.job), TODAY))
      .every(o => !o.placeholder_budget || o.triage_action !== 'short_reply' || o.triage_judge_score === 'C' || o.triage_judge_score === 'U'));
// The proof, run directly: strip the budget off the placeholder fixture and the
// answer must not move.
(() => {
  const ph = JOBS.find(j => j.id === '1b');
  const withBudget = runNode(Object.assign({ evidence_shape: ph.shape }, ph.job), TODAY);
  const without = runNode(Object.assign({ evidence_shape: ph.shape }, ph.job, { budget: 'not stated' }), TODAY);
  inv('a placeholder routes identically to the same job with no budget stated',
    withBudget.triage_action === without.triage_action && withBudget.route === without.route,
    'with=' + withBudget.triage_action + ' without=' + without.triage_action);
})();
inv('cheap_room_confirmed requires the buyer history to agree',
  JOBS.map(j => runNode(Object.assign({ evidence_shape: j.shape }, j.job), TODAY))
      .every(o => !o.cheap_room_confirmed || (o.buyer_avg_per_hire != null && o.buyer_avg_per_hire < 500)));
inv('every job logs which budget test fired',
  JOBS.map(j => runNode(Object.assign({ evidence_shape: j.shape }, j.job), TODAY)).every(o => !!o.budget_test));
inv('certified false always names a check',
  all.every(o => o.certified || !!o.certified_failed_check));
inv('an hourly post can never reach the volume lane',
  runNode(Object.assign({ evidence_shape: 'data-collection-house' }, JOBS[1].job, { job_type: 'HOURLY', budget: '25-40/hr' }), PROVEN).route !== 'hands_free_house');

// The negative controls: each assertion must be capable of failing.
console.log('\nNEGATIVE CONTROLS (each must trip)\n');
const noKit = JSON.parse(JSON.stringify(PROVEN));
noKit['Read Builds G'] = noKit['Read Builds G'].filter(b => b.status !== 'proven');
inv('removing the proven kit closes the gate',
  runNode(Object.assign({ evidence_shape: 'data-collection-house' }, JOBS[1].job), noKit).certified === false);

const stale = JSON.parse(JSON.stringify(PROVEN));
stale['Read Tools KB'].forEach(t => { if (t.session_last_verified) t.session_last_verified = new Date(Date.now() - 20 * 86400000).toISOString(); });
inv('a rehearsal older than 14 days closes the gate',
  runNode(Object.assign({ evidence_shape: 'data-collection-house' }, JOBS[1].job), stale).certified === false);

const walled = JSON.parse(JSON.stringify(PROVEN));
walled['Read Blockers'].push({ blocker_id: 'blk-test', status: 'open', kind: 'ui', subject: 'apify' });
inv('an open wall on a resolved surface closes the gate',
  runNode(Object.assign({ evidence_shape: 'data-collection-house' }, JOBS[1].job), walled).certified === false);

inv('no upstream registries at all closes the gate',
  runNode(Object.assign({ evidence_shape: 'data-collection-house' }, JOBS[1].job), {}).certified === false);

console.log('\n' + (failures === 0 ? 'PASS — every assertion holds.' : 'FAIL — ' + failures + ' assertion(s) broke.'));
process.exit(failures === 0 ? 0 : 1);
