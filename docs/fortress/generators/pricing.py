#!/usr/bin/env python3
"""
pricing.py — emit the Cockpit's "Price the build" Code node.

The pricing catalogue is the system of record. This turns it into arithmetic the
Cockpit can run and a client can rebuild. Rules taken straight from the catalogue
and enforced here rather than trusted to a prompt:

  - the derived number STANDS. A sum landing at 3,550 is quoted at 3,550.
  - charm endings banned (no 2,997).
  - no hourly anything client-facing. Hours exist only in internal arithmetic,
    and none appear in this node's output at all.
  - buyer spend calibrates WHO the buyer is. It never reaches the client.
  - ceiling discipline: a first Upwork engagement lands at or under ~3,000-3,500,
    and when the derived total exceeds it we SPLIT BY PHASE rather than inflate
    or discount.
  - generosity removes LINES, never shaves a total.
"""
import json, re

# shape -> (class, floor, typical_low, typical_high, note)
CLASS = {
# class 1 — single-workflow builds
"quote-follow-up":        (1, 800, 800, 1800, ""),
"reactivation":           (1, 800, 800, 1800, ""),
"alerting":               (1, 800, 800, 1800, ""),
"approval-routing":       (1, 1200, 1200, 1800, "judged class: branching plus an approval step"),
"stalled-deal-escalation":(1, 1200, 1200, 1800, "judged class: it decides, so it is not the simple floor"),
"client-onboarding":      (1, 1200, 1200, 1800, "judged class: fans out into task creation"),
# class 2 — system builds
"lead-routing":           (2, 2500, 2500, 5000, ""),
"data-collection":        (2, 2500, 2500, 5000, ""),
"scheduling":             (2, 2500, 2500, 5000, ""),
"system-sync":            (2, 2500, 2500, 5000, ""),
"books-reconciliation":   (2, 2500, 2500, 5000, ""),
"reporting":              (2, 2500, 2500, 5000, ""),
"storefront-upsell":      (2, 2500, 2500, 5000, ""),
"project-ops":            (2, 2500, 2500, 5000, ""),
"data-model-architecture":(2, 2500, 2500, 5000, ""),
"cold-outreach":          (2, 2500, 2500, 5000, ""),
"messaging-compliance":   (2, 1200, 1200, 2500, "sold alone it prices by BRAND count: registrations are per-brand, so brands are the surface unit"),
# class 3 — AI conversation builds
"ai-assistant":           (3, 2500, 2500, 4500, "knowledge-base population is its own named line: the KB must exist before go-live, so it is scope, never an assumption"),
"conversation-design":    (3,  650,  650, 2500, "audit-shaped: 650 transcript audit first, 1,200-2,500 rebuild. Never quoted without twenty real transcripts in hand"),
"ai-research-agent":      (3, 2500, 2500, 4500, "the model-spend cap is a named line; the weekly scorecard is the retainer hook"),
"voice-agent-intake":     (3, 1500, 1500, 2500, "PILOT-PRICED, then 500-1,200 per additional location"),
# class 4 — risk-priced builds
"platform-migration":     (4, 2500, 2500, 5000, "the parallel-run window is a priced line: reversible batches and count reconciliation are the difference between a migration and a data loss"),
"production-takeover":    (4,  650,  650,  650, "the 650 audit IS week one and is mandatory. Nothing changes in week one except the map; the rebuild quotes after"),
"document-assembly":      (4, 2500, 2500, 4500, "e-signature routing is a surface line"),
}

ANCHOR = {
1: "Published 2026 freelancer bands put a single workflow at $1,000 to $6,000. The floor sits under that, with testing and documentation inside it.",
2: "Published 2026 benchmarks put a build this shape at $2,000 to $8,000 for three to ten workflows with APIs.",
3: "Custom bots run $1,000 to $5,000 bare and $10,000 to $30,000 at an agency. This lands between them.",
4: "Complex multi-system work runs $8,000 to $20,000+ at the top of the published bands. Phase one is scoped to land well under that.",
}

# What a cheaper quote leaves out. Each maps to a node a buyer can SEE in the pack.
SKIPPED = [
 ("Input validation and a refusal path", "malformed data gets refused instead of written, so the CRM never fills with half-records"),
 ("Deduplication", "the same event arrives twice more often than anyone expects, and twice-processed is worse than not processed"),
 ("Rate limiting", "the vendor ceiling gets respected instead of discovered in production"),
 ("Retries with an error branch", "a failed call alerts instead of failing silently, which is the difference between a bug and a mystery"),
 ("Logging on both paths", "the successful runs and the failed ones, because a path nobody logs cannot be improved"),
 ("A fail-safe response", "the system answers even when the answer is 'held', so nothing hangs"),
 ("A second scheduled trigger", "the weekly report that keeps finding the thing nobody noticed"),
]

def main():
    js = ("""// Price the build.
//
// The pricing catalogue, as arithmetic. Every number here derives from parts the
// client can point at, which is the whole defence: remove a line and the number
// drops with it. That is the negotiation.
//
// Rules enforced in code rather than trusted to a prompt:
//   - the derived number STANDS. No smoothing, no charm endings.
//   - no hourly anything reaches the client.
//   - buyer spend calibrates who the buyer is; it NEVER goes in the quote.
//   - ceiling discipline on a first Upwork engagement: split by phase, never inflate.
//   - generosity removes LINES, never shaves a total.

const CLASS   = @@CLASS@@;
const ANCHOR  = @@ANCHOR@@;
const SKIPPED = @@SKIPPED@@;

const RATE = {
  audit: 650,
  simpleWorkflow: 800,
  judgedWorkflow: 1200,
  systemBase: 2500,       // covers the first two workflows across the first two systems
  surfaceLow: 300,        // each system past the first two
  surfaceHigh: 500,
  docsLow: 250,
  docsHigh: 500,
  testPct: 0.15,          // 15-20% of the build subtotal
  retainer: 750,
  upworkCeiling: 3500
};

const input = $json || {};
let ev = null;
try { ev = $('Pick the evidence to attach').first().json; } catch (e) { ev = null; }
const shape = (ev && ev.evidence_shape) || input.evidence_shape || null;
const spec  = shape ? CLASS[shape] : null;

if (!spec) {
  return [{ json: Object.assign({}, input, {
    priced: false,
    pricing_reason: 'No pattern resolved, so there is nothing to derive a number from. Quote nothing.'
  })}];
}

const [klass, floor, typLow, typHigh, note] = spec;

// ---- count the scope from the posting -------------------------------------
// The payload reaching this node has usually lost the posting: "Match Product"
// joins the run against a stored table and does not carry $json through, so
// job_post and text are both absent and every quote silently counted one
// workflow. Walk back to the node that still has the posting, the same way the
// evidence node does. A quote derived from an empty string is not a quote.
const POST_SOURCES = ['Ground Match', 'Merge Context', 'Read Job Row', 'Cockpit Form'];
const POSTING_KEYS = ['jobPost', 'job_post', 'jobDescription', 'description', 'text', 'body', 'post'];
const carriesPosting = function (o) {
  return !!o && POSTING_KEYS.some(function (f) {
    return typeof o[f] === 'string' && o[f].trim().length > 40; });
};
let src = input, postSource = '$json';
if (!carriesPosting(input)) {
  for (const nm of POST_SOURCES) {
    try { const j = $(nm).first().json;
      if (carriesPosting(j)) { src = Object.assign({}, j, input); postSource = nm; break; }
    } catch (e) { /* not in this branch */ }
  }
}
const postText = POSTING_KEYS.map(function (f) { return src[f]; })
  .filter(function (v) { return typeof v === 'string'; })
  .sort(function (a, b) { return b.length - a.length; })[0] || '';
const hay = String(postText + ' ' + (src.jobTitle || src.title || '')).toLowerCase();

// how many workflows are they describing?
let workflows = 1;
const wfWords = hay.match(/(\\d+)\\s*(?:automation|workflow|sequence|zap|scenario)/);
if (wfWords) { workflows = Math.min(parseInt(wfWords[1], 10) || 1, 12); }
else {
  const listed = (hay.match(/\\bnurture\\b|\\brecovery\\b|\\bonboarding\\b|\\bretention\\b|\\bchurn\\b|\\breferral\\b|\\breminder\\b|\\bfollow[- ]?up\\b/g) || []).length;
  if (listed > 1) { workflows = Math.min(listed, 12); }
}

// how many systems does it touch?
const TOOLS = ['gohighlevel','ghl','hubspot','pipedrive','salesforce','zoho','shopify','stripe',
  'quickbooks','xero','airtable','monday','clickup','notion','twilio','slack','zapier','make',
  'n8n','instantly','klaviyo','activecampaign','calendly','wordpress','google sheets','hyros'];
const named = TOOLS.filter(function (t) { return hay.indexOf(t) !== -1; });
const systems = Math.max(named.length, (ev && (ev.client_tools || []).length) || 1, 1);

// ---- derive ----------------------------------------------------------------
const lines = [];
let subtotal = 0;
const add = function (label, amount, why) {
  lines.push({ label: label, amount: amount, why: why });
  subtotal += amount;
};

if (klass === 4 && shape === 'production-takeover') {
  add('Audit, week one', RATE.audit, 'Nothing changes in week one except the map. The rebuild quotes after it exists.');
} else if (klass === 3 && shape === 'conversation-design') {
  add('Transcript audit', RATE.audit, 'Twenty real transcripts in, the three failure turns named. No rebuild is quoted before this.');
} else if (klass === 1) {
  const isJudged = floor >= RATE.judgedWorkflow;
  add((isJudged ? 'Workflow, judged build' : 'Workflow, simple build'), floor,
      isJudged ? 'It makes a decision, so it carries the judged rate.' : 'One trigger, one system, one outcome.');
  for (let i = 1; i < workflows; i++) {
    add('Additional workflow', RATE.simpleWorkflow, 'Rides the same records as the first.');
  }
} else {
  add('Full system base', RATE.systemBase, 'Covers the first two workflows across the first two systems.');
  for (let i = 2; i < workflows; i++) {
    add('Additional workflow', RATE.simpleWorkflow, 'Beyond the two the base covers.');
  }
}

const extraSurfaces = Math.max(systems - 2, 0);
for (let i = 0; i < extraSurfaces; i++) {
  add('Integration surface', RATE.surfaceLow, 'Each system past the first two, priced by API quality.');
}

const buildSubtotal = subtotal;
const testing = Math.round(buildSubtotal * RATE.testPct);
const docs = RATE.docsLow;

// CHANNEL RULE: itemised on direct, included inside the floors on gig channels.
const channel = String(input.channel || 'Upwork');
const isGig = /upwork|gig/i.test(channel);

if (!isGig) {
  add('Testing and hardening on real data', testing, 'Your data, not a sandbox, with every path verified.');
  add('Documentation and handoff', docs, 'You own the whole thing when I am gone.');
}
add('Warranty, 30 days, fix anything we built', 0, 'Included. It is on the sheet so you can see it.');

const total = subtotal;

// ---- ceiling discipline ----------------------------------------------------
// The platform ceiling is SEPARATE from the value ceiling. A buyer willing to
// pay $5,000 for the business value will not pay it on a gig platform where
// they are comparing bids in the same window. When honest scope exceeds the
// ceiling the move is SPLIT, never inflate and never discount — phase one now,
// phase two named and non-binding. MFLG settled at $2,950 after five rounds of
// exactly this reasoning; that is the calibration point, not a floor.
let phased = null;
if (isGig && total > RATE.upworkCeiling) {
  const phaseOne = Math.min(RATE.systemBase + (extraSurfaces ? RATE.surfaceLow : 0), RATE.upworkCeiling);
  phased = {
    phase_one: phaseOne,
    phase_two: total - phaseOne,
    why: 'A first engagement lands at or under about $3,500 here. The scope is split by phase rather than inflated or discounted — the same total, delivered in two commitments.'
  };
}

// ---- the words -------------------------------------------------------------
const money = function (n) { return '$' + n.toLocaleString('en-US'); };
const partsSentence = lines.filter(function (l) { return l.amount > 0; })
  .map(function (l) { return l.label.toLowerCase() + ' at ' + money(l.amount); }).join(', ');

const threeLine = [
  'The parts: this is ' + workflows + ' workflow' + (workflows === 1 ? '' : 's') +
    ' touching ' + systems + ' system' + (systems === 1 ? '' : 's') + ' — ' + partsSentence + '.',
  'The anchor: ' + ANCHOR[klass],
  'The flag: every line walks back to a component. Remove a line and the number drops with it. That is the whole negotiation.'
].join(' ');

const whatItTakes =
  'What you are paying for is the part that is invisible until it fails. ' +
  SKIPPED.slice(0, 4).map(function (s) { return s[0].toLowerCase() + ' — ' + s[1]; }).join('; ') + '. ' +
  'Those are lines a cheaper quote skips, and you will not find out which ones until something breaks quietly. ' +
  'They are in the attached build, node by node, so you can check rather than take my word for it.';

// ---- MANDATORY BLOCK 1: the phase split, stated either way -----------------
// This used to be emitted only when a split happened, which meant the prompt
// had nothing to say in the ordinary case and quietly said nothing in the
// exceptional one too when a field came back null. It is now always a sentence.
// A quote that exceeds the ceiling and does not visibly split reads as a
// number somebody pulled out of the air.
const phaseSplitParagraph = phased
  ? ('This is scoped in two phases. Phase one is ' + money(phased.phase_one) +
     ' and is the whole of what you would sign for now: the system standing up, running on your ' +
     'data, with the paths that fail handled. Phase two is ' + money(phased.phase_two) +
     ' and is named here so you can see the shape of it, not so you commit to it — it is a ' +
     'separate decision made after phase one has proved itself. The split is not a discount ' +
     'and the total does not change. A first engagement on this channel lands at or under ' +
     'about ' + money(RATE.upworkCeiling) + ', so the scope gets divided rather than the price ' +
     'inflated to cover everything at once or shaved to fit.')
  : ('No phase split is needed here. The derived total of ' + money(total) + ' already sits ' +
     (total <= RATE.upworkCeiling ? 'at or under' : 'inside') +
     ' the range a first engagement should land in, so the whole scope is one commitment. ' +
     'If you want it smaller, the way to get there is to remove a line from the list above — ' +
     'the number moves with it. That is the only lever, and it is yours.');

// ---- MANDATORY BLOCK 2: why it costs this ----------------------------------
// Derived from the lines ACTUALLY quoted, not a fixed blurb. If the arithmetic
// changes, this paragraph changes with it, which is the whole point: a client
// can rebuild the number from the words.
const paidLines = lines.filter(function (l) { return l.amount > 0; });
// Four identical "additional workflow" lines read as padding even when the
// arithmetic is honest. Collapse repeats into a count so the buyer sees the
// unit and the multiplier, which is what they would check anyway.
const grouped = [];
paidLines.forEach(function (l) {
  const prev = grouped[grouped.length - 1];
  if (prev && prev.label === l.label && prev.amount === l.amount) { prev.n += 1; return; }
  grouped.push({ label: l.label, amount: l.amount, why: l.why, n: 1 });
});
const whyItCostsThis = [
  'Why it costs this, in the order the number is built.',
  grouped.map(function (g) {
    return (g.n > 1 ? g.n + ' \\u00d7 ' + money(g.amount) + ' (' + money(g.amount * g.n) + ') for '
                    : money(g.amount) + ' for ') +
           g.label.toLowerCase() + (g.n > 1 ? 's' : '') + ' — ' + g.why;
  }).join(' '),
  'That comes to ' + money(total) + '. Not a range, not a rounded number, and not a ' +
    'figure ending in a nine to look smaller than it is: it is the sum of the parts above, ' +
    'and every part is something you can point at in the attached build.',
  ANCHOR[klass],
  'The rest of what you are paying for is the part that is invisible until it fails: ' +
    SKIPPED.slice(0, 3).map(function (s) { return s[0].toLowerCase(); }).join(', ') +
    '. A cheaper quote leaves those out and you find out which ones eight weeks later.'
].join(' ');

return [{ json: Object.assign({}, input, {
  priced: true,
  pricing_class: klass,
  pricing_shape: shape,
  workflows_counted: workflows,
  systems_counted: systems,
  quote_lines: lines,
  quote_total: total,
  quote_total_text: money(total),
  quote_typical_band: money(typLow) + ' to ' + money(typHigh),
  quote_phased: phased,
  quote_channel: channel,
  quote_note: note || null,
  retainer_floor: RATE.retainer,
  retainer_line: 'Run retainer from ' + money(RATE.retainer) +
    ' a month: drift maintenance, optimisation and the weekly report. Not availability.',
  retainer_defense: '43% of businesses using freelancers for automation hit at least one critical ' +
    'workflow failure from lack of ongoing support (Zapier, State of Business Automation).',
  pricing_three_line: threeLine,
  pricing_what_it_takes: whatItTakes,
  pricing_anchor: ANCHOR[klass],
  pricing_post_source: postSource,
  pricing_post_chars: postText.length,
  // The two blocks the letter must carry. Named here so the Prompt of Record
  // asserts their presence rather than hoping the model included them.
  pricing_phase_split: phaseSplitParagraph,
  pricing_why_it_costs_this: whyItCostsThis,
  pricing_mandatory_blocks: ['pricing_why_it_costs_this', 'pricing_phase_split'],
  // guardrails, asserted not assumed
  pricing_rules_ok: (total % 5 === 0)
    && String(total).slice(-3) !== '997'
    && !!phaseSplitParagraph && !!whyItCostsThis
    && !/\\bper hour\\b|\\bhourly\\b|\\ban hour\\b|\\b\\/hr\\b/i.test(whyItCostsThis + ' ' + phaseSplitParagraph + ' ' + threeLine)
}) }];
""".replace('@@CLASS@@', json.dumps(CLASS, separators=(',', ':')))
        .replace('@@ANCHOR@@', json.dumps(ANCHOR, separators=(',', ':')))
        .replace('@@SKIPPED@@', json.dumps(SKIPPED, separators=(',', ':'))))
    open('cockpit-pricing-node.js','w').write(js)
    print(f"wrote cockpit-pricing-node.js: {len(js)} chars | {len(CLASS)} patterns priced")

main()
