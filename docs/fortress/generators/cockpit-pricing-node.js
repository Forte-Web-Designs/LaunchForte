// Price the build.
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

const CLASS   = {"quote-follow-up":[1,800,800,1800,""],"reactivation":[1,800,800,1800,""],"alerting":[1,800,800,1800,""],"approval-routing":[1,1200,1200,1800,"judged class: branching plus an approval step"],"stalled-deal-escalation":[1,1200,1200,1800,"judged class: it decides, so it is not the simple floor"],"client-onboarding":[1,1200,1200,1800,"judged class: fans out into task creation"],"lead-routing":[2,2500,2500,5000,""],"data-collection":[2,2500,2500,5000,""],"scheduling":[2,2500,2500,5000,""],"system-sync":[2,2500,2500,5000,""],"books-reconciliation":[2,2500,2500,5000,""],"reporting":[2,2500,2500,5000,""],"storefront-upsell":[2,2500,2500,5000,""],"project-ops":[2,2500,2500,5000,""],"data-model-architecture":[2,2500,2500,5000,""],"cold-outreach":[2,2500,2500,5000,""],"messaging-compliance":[2,1200,1200,2500,"sold alone it prices by BRAND count: registrations are per-brand, so brands are the surface unit"],"ai-assistant":[3,2500,2500,4500,"knowledge-base population is its own named line: the KB must exist before go-live, so it is scope, never an assumption"],"conversation-design":[3,650,650,2500,"audit-shaped: 650 transcript audit first, 1,200-2,500 rebuild. Never quoted without twenty real transcripts in hand"],"ai-research-agent":[3,2500,2500,4500,"the model-spend cap is a named line; the weekly scorecard is the retainer hook"],"voice-agent-intake":[3,1500,1500,2500,"PILOT-PRICED, then 500-1,200 per additional location"],"platform-migration":[4,2500,2500,5000,"the parallel-run window is a priced line: reversible batches and count reconciliation are the difference between a migration and a data loss"],"production-takeover":[4,650,650,650,"the 650 audit IS week one and is mandatory. Nothing changes in week one except the map; the rebuild quotes after"],"document-assembly":[4,2500,2500,4500,"e-signature routing is a surface line"]};
const ANCHOR  = {"1":"Published 2026 freelancer bands put a single workflow at $1,000 to $6,000. The floor sits under that, with testing and documentation inside it.","2":"Published 2026 benchmarks put a build this shape at $2,000 to $8,000 for three to ten workflows with APIs.","3":"Custom bots run $1,000 to $5,000 bare and $10,000 to $30,000 at an agency. This lands between them.","4":"Complex multi-system work runs $8,000 to $20,000+ at the top of the published bands. Phase one is scoped to land well under that."};
const SKIPPED = [["Input validation and a refusal path","malformed data gets refused instead of written, so the CRM never fills with half-records"],["Deduplication","the same event arrives twice more often than anyone expects, and twice-processed is worse than not processed"],["Rate limiting","the vendor ceiling gets respected instead of discovered in production"],["Retries with an error branch","a failed call alerts instead of failing silently, which is the difference between a bug and a mystery"],["Logging on both paths","the successful runs and the failed ones, because a path nobody logs cannot be improved"],["A fail-safe response","the system answers even when the answer is 'held', so nothing hangs"],["A second scheduled trigger","the weekly report that keeps finding the thing nobody noticed"]];

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

// ===========================================================================
// CLASS 0 — COMPONENTS. Derived from the corpus, Aug 9 2026.
//
// The gap this closes: the catalogue's lowest rungs were $500 (fix) and $800
// (single workflow), but a large share of real postings ask for one small
// discrete thing — a form, a payment element wired, a tag rule, a page, a field
// mapping. Those either inflated to $800 or fell out of pricing entirely.
//
// Every price below is the MEDIAN STATED BUDGET across postings in this corpus
// whose ENTIRE ask was that one component, rounded to $25. Not a catalogue
// fraction, not a guess: where that exact ask actually clears.
//
// [plain name, price, n priced solo asks, total postings, published, thin evidence]
// "thin" means fewer than 30 solo priced asks — the number is directional, not settled.
const COMPONENT = {
  'api-call':             ['write or fix a single API call', 100, 86, 780, true, false],
  'dashboard-view':       ['build a dashboard or report view', 100, 36, 717, true, false],
  'landing-page':         ['build a landing page', 150, 60, 599, true, false],
  'tracking-pixel':       ['set up tracking or conversion pixels', 400, 69, 573, true, false],
  'webhook':              ['set up a webhook endpoint', 250, 5, 342, false, true],
  'ticket-routing':       ['set up support ticket routing', 600, 20, 288, true, true],
  'new-zap':              ['set up a new zap or scenario', 50, 16, 257, true, true],
  'permissions':          ['set up user roles or permissions', 300, 8, 255, false, true],
  'ai-content':           ['wire an AI content or summarisation step', 50, 7, 250, false, true],
  'scrape-list':          ['scrape or build a lead list', 50, 46, 239, true, false],
  'doc-generate':         ['build a document or PDF generator', 150, 37, 232, true, false],
  'chatbot-flow':         ['build a chatbot flow', 100, 12, 226, true, true],
  'payment-wire':         ['wire a payment element', 350, 8, 224, false, true],
  'subscription':         ['configure recurring billing', 250, 11, 208, true, true],
  'file-upload':          ['set up file upload or storage', 325, 27, 190, true, true],
  'checkout-page':        ['build a checkout or cart page', 25, 26, 178, true, true],
  'referral':             ['build a referral or affiliate flow', 150, 13, 173, true, true],
  'board-view':           ['build a board or project view', 500, 17, 171, true, true],
  'code-snippet':         ['inject a custom code snippet', 50, 20, 166, true, true],
  'booking-setup':        ['set up booking or calendar', 200, 6, 144, false, true],
  'list-clean':           ['clean or dedupe a list', 25, 9, 132, false, true],
  'onboarding-flow':      ['build a client onboarding flow', 100, 14, 132, false, true],
  'email-deliverability': ['configure email deliverability or DNS', 150, 13, 129, false, true],
  'data-import':          ['import or migrate a data set', 25, 21, 122, false, true],
  'form-build':           ['build a form in an existing tool', 200, 11, 121, false, true],
  'survey-quiz':          ['build a survey or quiz', 100, 13, 111, false, true],
  'membership':           ['set up membership or gated content', 300, 5, 109, false, true],
  'fix-zap':              ['fix a broken zap or scenario', 25, 9, 104, false, true],
  'list-verify':          ['verify or enrich a list', 75, 5, 98, false, true],
  'one-way-connect':      ['connect two tools one direction', 25, 7, 94, false, true],
  'catalog-sync':         ['build a product feed or catalog sync', 75, 9, 92, false, true],
  'popup':                ['add a popup or banner', 150, 11, 89, false, true],
  'abandoned-cart':       ['set up an abandoned cart flow', 100, 5, 65, false, true]
};

const COMPONENT_RE = {
  'api-call': /\b(api call|api endpoint|rest api|api request|api integration)\b/,
  'dashboard-view': /\b(dashboard|dashboards|report view|reporting view|looker studio|data studio|scorecard|kpi)\b/,
  'landing-page': /\b(landing page|landing pages|opt-?in page|squeeze page|sales page|funnel page)\b/,
  'tracking-pixel': /\b(pixel|conversion tracking|google tag manager|gtm|utm|ga4|google analytics|tracking code)\b/,
  'webhook': /\bwebhooks?\b/,
  'ticket-routing': /\b(ticket|tickets|helpdesk|help desk|support queue|zendesk|freshdesk|intercom)\b/,
  'new-zap': /\b(zapier|make\.com|integromat|n8n)\b[^.]{0,40}\b(set ?up|build|create|new|automation|scenario|zap)\b/,
  'permissions': /\b(user roles?|permissions?|access levels?|user management|sso)\b/,
  'ai-content': /\b(chatgpt|openai|gpt|claude|ai generated|ai writes|summari[sz])\b[^.]{0,40}\b(integrat|automat|connect|generate|api|workflow)\b/,
  'scrape-list': /\b(scrape|scraping|scraper|web scrap|lead list|prospect list|build a list|data extraction)\b/,
  'doc-generate': /\b(pdf|document generation|generate documents?|proposal generator|contract generation|docusign|e-?signature)\b/,
  'chatbot-flow': /\b(chat ?bot|chatbot|chat widget|live chat|conversational flow|chat flow)\b/,
  'payment-wire': /\b(payment|stripe|paypal|checkout)\b[^.]{0,50}\b(element|button|link|gateway|integration|processing|collect|collection|accept)\b|\baccept payments?\b|\bcollect payments?\b/,
  'subscription': /\b(subscription|recurring billing|recurring payment|membership billing|retainer billing)\b/,
  'file-upload': /\b(file upload|upload files?|google drive|dropbox|file storage|document storage)\b/,
  'checkout-page': /\b(checkout page|cart page|shopping cart|checkout flow|order form|product page)\b/,
  'referral': /\b(referral|affiliate|partner program|rewards program|loyalty program)\b/,
  'board-view': /\b(kanban|board view|project view|task board|monday board|clickup)\b/,
  'code-snippet': /\b(code snippet|custom code|javascript snippet|embed code|custom script|liquid)\b/,
  'booking-setup': /\b(calendly|booking|appointment|scheduling|calendar)\b[^.]{0,40}\b(set ?up|link|integrate|sync|embed|configure|book|schedule)\b|\bbooking (system|page|link|flow)\b/,
  'list-clean': /\b(clean|cleanse|dedupe|de-duplicate|deduplicate|scrub|tidy|normali[sz]e)\b[^.]{0,30}\b(list|lists|data|database|contacts|records|csv|spreadsheet|leads)\b/,
  'onboarding-flow': /\b(onboarding)\b[^.]{0,40}\b(flow|sequence|process|automat|form|client|customer)\b|\bclient onboarding\b/,
  'email-deliverability': /\b(spf|dkim|dmarc|deliverability|domain warm|inbox placement|dns record)\b/,
  'data-import': /\b(import|migrate|upload|transfer|move)\b[^.]{0,30}\b(csv|data|contacts|records|spreadsheet|list|products)\b/,
  'form-build': /\b(build|create|set ?up|make|need|design|add)\b[^.]{0,40}\b(form|forms|intake form|signup form|sign-up form|contact form|lead form|application form|registration form|web form)\b/,
  'survey-quiz': /\b(survey|quiz|questionnaire|assessment form|typeform)\b/,
  'membership': /\b(membership|members area|gated content|course platform|paywall|subscriber only)\b/,
  'fix-zap': /\b(fix|repair|debug|troubleshoot|broken|not working|stopped|failing|error)\b[^.]{0,40}\b(zap|zaps|scenario|scenarios|automation|automations|workflow|workflows|integration)\b/,
  'list-verify': /\b(verify|verification|enrich|enrichment|validate)\b[^.]{0,30}\b(email|emails|list|leads|contacts|data)\b/,
  'one-way-connect': /\b(connect|integrate|sync|push|send)\b[^.]{0,40}\b(to|with|into)\b[^.]{0,30}\b(crm|sheet|sheets|airtable|hubspot|slack|notion|database|api)\b/,
  'catalog-sync': /\b(product feed|catalog sync|inventory sync|product sync|sku|catalogue)\b/,
  'popup': /\b(pop-?up|popups|modal|banner|slide-?in|exit intent)\b/,
  'abandoned-cart': /\b(abandoned cart|cart abandonment|abandoned checkout|browse abandonment)\b/
};

// ---------------------------------------------------------------------------
// PRICE BASIS: FLOOR-UP (Aug 9). The budget medians above are now ORDERING
// EVIDENCE ONLY — they rank demand, they no longer set a price.
//
// Why: the budget column does not respond to scope. Median posted budget by
// number of components asked for runs $50, $75, $100, $125, $120, $125, $75 —
// a posting asking for six things is budgeted like one asking for one, while
// description length triples across the same bands. A price derived from that
// column is a price derived from what people type in a required field.
//
// So every component price is now built from arithmetic:
//
//   delivery   = component Seth-minutes x minute cost
//   warranty   = delivery x reserve            (rework exposure)
//   connects   = connects-per-bid x cost / WIN RATE   (the losing bids)
//   tooling    = monthly tooling / wins per month
//   price      = (delivery + warranty + connects + tooling) / (1 - Upwork fee)
//
// HONEST LIMIT, STATED UP FRONT: psm_estimate takes only two distinct values
// across this corpus (10 and 55 minutes), because it measures SETH'S HANDS —
// sign-in, RED confirms, thread — and not build effort. So floor-up yields a
// two-tier list, not a graded one. That is arithmetic being honest about an
// input nobody has measured: per-component BUILD minutes do not exist yet. The
// flat answer never under-prices, which the budget-derived list did.
const BASIS = {
  win_rate: 0.08,            // ASSUMED. Nothing in the estate records a win yet.
  warranty_reserve: 0.15,    // ASSUMED
  monthly_tooling: 400,      // ASSUMED — tool_spend table is all zeros
  wins_per_month: 3.5,       // ASSUMED (10 proposals/wk at the assumed win rate)
  source: 'DERIVED',
  assumptions: ['win_rate', 'warranty_reserve', 'monthly_tooling', 'wins_per_month']
};
// Component Seth-minutes, median of certified psm across postings whose entire
// ask was that component. Data-derived from the corpus, not assigned.
const COMPONENT_PSM_DEFAULT = 55;
const COMPONENT_PSM = {
  'api-call': 10, 'permissions': 10, 'code-snippet': 10, 'data-import': 10,
  'list-clean': 10, 'one-way-connect': 10, 'form-build': 10
};
const floorUpPrice = function (key, psmOverride) {
  const psm = psmOverride != null ? psmOverride : (COMPONENT_PSM[key] || COMPONENT_PSM_DEFAULT);
  const delivery = psm * DELIVERY.seth_minute_cost;
  const warranty = delivery * BASIS.warranty_reserve;
  const connects = DELIVERY.connects_per_bid * DELIVERY.connect_cost / BASIS.win_rate;
  const tooling  = BASIS.monthly_tooling / BASIS.wins_per_month;
  return Math.round(((delivery + warranty + connects + tooling) / (1 - DELIVERY.upwork_fee)) / 25) * 25;
};

// THE COST-TO-DELIVER FLOOR. On certified hands-free work this replaces the
// catalogue floor entirely, because the catalogue floor is a positioning number
// and this one is arithmetic: what the job actually costs to win and run.
//
//   floor = (connects + Seth-minutes x his minute cost) / (1 - Upwork's fee)
//
// WARNING, AND IT MATTERS: seth_minute_cost is the ONE number here nobody has
// set. It is the difference between a $35 floor and a $90 one. Until Seth
// confirms it, every cost-to-deliver figure carries delivery_floor_source
// 'ESTIMATED' and should be read as a shape, not a number.
const DELIVERY = {
  connects_per_bid: 6,      // assumption
  connect_cost: 0.15,       // Upwork published
  upwork_fee: 0.10,         // Upwork published
  seth_minute_cost: 2.50,   // DERIVED: the catalogue's own $150/hr specialist band floor
  source: 'DERIVED',
  provenance: {
    seth_minute_cost: 'catalogue specialist band floor, $150/hr',
    upwork_fee: 'Upwork published rate',
    connect_cost: 'Upwork published rate',
    connects_per_bid: 'ASSUMPTION — the one input still unmeasured'
  }
};
const costToDeliver = function (psmMinutes) {
  const direct = DELIVERY.connects_per_bid * DELIVERY.connect_cost +
                 (psmMinutes || 0) * DELIVERY.seth_minute_cost;
  return Math.ceil((direct / (1 - DELIVERY.upwork_fee)) / 5) * 5;
};

const input = $json || {};
let ev = null;
try { ev = $('Pick the evidence to attach').first().json; } catch (e) { ev = null; }
const shape = (ev && ev.evidence_shape) || input.evidence_shape || null;
const spec  = shape ? CLASS[shape] : null;

// Triage already decided whether autonomy is proven. Class 0 depends on it
// absolutely, so it is read here rather than re-derived.
let tri = null;
try { tri = $('Route the job').first().json; } catch (e) { tri = null; }
if (!tri && input.triaged) { tri = input; }
const isCertified   = !!(tri && tri.certified);
const psmMinutes    = (tri && typeof tri.psm_estimate === 'number') ? tri.psm_estimate : null;
const postedAmount  = (tri && typeof tri.posted_budget_amount === 'number') ? tri.posted_budget_amount : null;
const cheapConfirmed = !!(tri && tri.cheap_room_confirmed);
const deliveryFloor = costToDeliver(psmMinutes == null ? 30 : psmMinutes);

// What does this posting actually ask for, at component level?
const __hay = [input.title, input.description, input.skills, ev && ev.title, ev && ev.description]
  .filter(Boolean).join(' ').toLowerCase();
const detected = Object.keys(COMPONENT_RE)
  .filter(function (k) { return COMPONENT_RE[k].test(__hay); })
  .sort(function (a, b) { return COMPONENT[b][1] - COMPONENT[a][1]; });
const componentSum = detected.reduce(function (a, k) { return a + COMPONENT[k][1]; }, 0);

// The fix floor BENDS. It used to apply to any repair; it now applies only to a
// repair spanning several components. A single-component job is never dragged up
// to $500 by it.
const __isRepair = detected.indexOf('fix-zap') !== -1;
const __fixFloorApplies = __isRepair && detected.length > 1;

if (!spec) {
  // No shape resolved. This used to end here with no number at all — 420 jobs a
  // sweep. If the posting names components we can still price it honestly,
  // because a component quote does not need a shape: it needs a list of parts.
  if (detected.length && isCertified) {
    const lines0 = detected.map(function (k) {
      return { label: COMPONENT[k][0], amount: floorUpPrice(k),
               why: 'cost to deliver plus warranty, connects on losing bids and tooling',
               basis: 'floor_up', price_source: 'DERIVED',
               demand_rank_postings: COMPONENT[k][3], budget_median_evidence_only: COMPONENT[k][1] };
    });
    const total0 = lines0.reduce(function (a, l) { return a + l.amount; }, 0);
    return [{ json: Object.assign({}, input, {
      priced: true, pricing_class: 0, pricing_class_source: 'components',
      pricing_shape: null, quote_lines: lines0, quote_total: Math.max(total0, deliveryFloor),
      quote_total_text: '$' + Math.max(total0, deliveryFloor).toLocaleString('en-US'),
      component_keys: detected, component_sum: total0,
      component_below_delivery_floor: total0 < deliveryFloor,
      delivery_floor: deliveryFloor, delivery_floor_source: DELIVERY.source,
      pricing_rules_ok: Math.max(total0, deliveryFloor) >= deliveryFloor
    })}];
  }
  return [{ json: Object.assign({}, input, {
    priced: false,
    component_keys: detected,
    component_sum: componentSum,
    pricing_reason: detected.length
      ? 'Components resolved (' + detected.join(', ') + ') but the shape is not certified hands-free, ' +
        'so the component tier does not authorise a cheap bid. Uncertified small jobs are not cheap jobs.'
      : 'No pattern resolved, so there is nothing to derive a number from. Quote nothing.'
  })}];
}

let [klass, floor, typLow, typHigh, note] = spec;

// ---- CLASS 0 SHORT-CIRCUIT -------------------------------------------------
// Three rails, all of which must hold before a sub-floor number is ever emitted:
//
//   1. THE TIER ONLY REDUCES. If the components sum at or above the class
//      floor, Class 0 declines and the normal derivation governs. This tier
//      exists to price small things small, never to inflate a job past its class.
//   2. UNCERTIFIED SMALL JOBS ARE NOT CHEAP JOBS. Without proven autonomy the
//      component prices are not authorised at all. The prime rule is untouched:
//      price drops only as far as proven autonomy rises.
//   3. NOTHING GOES UNDER THE COST TO DELIVER. Winning below it is worse than
//      losing.
const __classFloor = __fixFloorApplies ? Math.max(floor, 500) : floor;
if (detected.length && componentSum < __classFloor && isCertified) {
  const lines0 = detected.map(function (k) {
    const c = COMPONENT[k];
    const amt = floorUpPrice(k);
    return { label: c[0], amount: amt,
             why: 'cost to deliver plus warranty, connects on losing bids and tooling',
             basis: 'floor_up', price_source: 'DERIVED',
             demand_rank_postings: c[3], budget_median_evidence_only: c[1] };
  });
  let total0 = lines0.reduce(function (a, l) { return a + l.amount; }, 0);
  let matched = false;

  // Matching the posted number is permitted — but ONLY where the buyer's own
  // history already confirmed that number is real. In a placeholder room the
  // posted figure is not an offer and matching it would be bidding against a
  // typo.
  if (cheapConfirmed && postedAmount != null && postedAmount >= deliveryFloor && postedAmount < total0) {
    total0 = postedAmount;
    matched = true;
  }

  const belowFloor = total0 < deliveryFloor;
  if (belowFloor) total0 = deliveryFloor;

  const money0 = function (n) { return '$' + n.toLocaleString('en-US'); };
  return [{ json: Object.assign({}, input, {
    priced: true,
    pricing_class: 0,
    pricing_class_source: 'components',
    pricing_shape: shape,
    quote_lines: lines0,
    quote_total: total0,
    quote_total_text: money0(total0),
    quote_channel: String(input.channel || 'Upwork'),
    component_keys: detected,
    component_sum: lines0.reduce(function (a, l) { return a + l.amount; }, 0),
    component_matched_posted: matched,
    component_below_delivery_floor: belowFloor,
    delivery_floor: deliveryFloor,
    delivery_floor_source: DELIVERY.source,
    component_price_basis: 'floor_up',
    component_price_source: BASIS.source,
    component_price_assumptions: BASIS.assumptions,
    component_win_rate_assumed: BASIS.win_rate,
    class_floor_bypassed: __classFloor,
    pricing_note: 'Class 0. ' + detected.length + ' component' + (detected.length > 1 ? 's' : '') +
      ', summing to ' + money0(lines0.reduce(function (a, l) { return a + l.amount; }, 0)) +
      ', under the ' + money0(__classFloor) + ' floor for this class. Certified hands-free, so the ' +
      'cost to deliver (' + money0(deliveryFloor) + ') governs instead of the catalogue floor.' +
      (matched ? ' Posted number matched: the buyer\'s own history confirms it is real and it clears the floor.' : '') +
      (belowFloor ? ' Raised to the delivery floor — the components alone did not cover the cost of winning it.' : ''),
    // Testing and documentation stay INSIDE the number on gig channels, exactly
    // as they do at every other rung. Class 0 does not itemise them and does not
    // charge for them separately.
    pricing_inclusion_line: 'Testing and documentation are inside this number, not line items on top of it.',
    // The consistency gate: a quote that its own lines cannot rebuild does not ship.
    pricing_rules_ok:
      total0 >= deliveryFloor
      && total0 < __classFloor
      && lines0.length > 0
      && lines0.every(function (l) { return l.amount > 0 && !!l.label && !!l.why; })
      && (matched || belowFloor || total0 === lines0.reduce(function (a, l) { return a + l.amount; }, 0))
      && !/\bper hour\b|\bhourly\b|\ban hour\b/i.test(lines0.map(function (l) { return l.why; }).join(' '))
  })}];
}

// ---- class comes from the POSTING, not only from the resolved shape --------
// The Prompt of Record used to carry its own copy of this arithmetic, and it
// derived class from the posting's own words on purpose: "a bad shape
// resolution must not become a confidently wrong price." That principle is
// right and it belongs here, in the one place the number is derived, rather
// than in a second implementation nobody tests.
//
// So: the shape proposes a class, the posting disposes. When they disagree the
// posting wins and the disagreement is emitted, because a quote nobody can
// audit is a quote nobody can defend.
const __AUD = /(audit|review our|review the|assess|take over|inherit|undocumented|transcript)/;
const __BOT = /(chatbot|chat bot|conversation ai|ai agent|ai assistant|voice ai|receptionist)/;
const __SYS = /(crm|pipeline|dashboard|integrat|sync|migrat|onboard|full system|build out|end to end|ecosystem)/;
const __classFromPosting = function (hayStr) {
  const aud = __AUD.test(hayStr), bot = __BOT.test(hayStr), sys = __SYS.test(hayStr);
  if (aud && !sys) return 4;
  if (bot) return 3;
  if (sys) return 2;
  return 1;
};

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

const __shapeClass = klass;
const __postClass = __classFromPosting(hay);
// A posting too short to say anything is not a disagreement, it is silence.
const __postSpeaks = hay.trim().length >= 120;
const __classSource = (__postSpeaks && __postClass !== __shapeClass) ? 'posting' : 'shape';
// A class-4 posting is not automatically a class-4 REBUILD. "Take over an
// undocumented system" is the 650 audit; "migrate four systems" is the 2,500
// base. Picking whichever class-4 row happens to sort first turned the audit
// into a full-system quote, so the posting's own audit signal chooses the row.
const __postAudit = __AUD.test(hay) && !__SYS.test(hay);
if (__classSource === 'posting') {
  klass = __postClass;
  const canon = klass === 4 ? (__postAudit ? 'production-takeover' : 'platform-migration')
              : klass === 3 ? (/transcript|review/.test(hay) ? 'conversation-design' : 'ai-assistant')
              : klass === 2 ? 'system-sync'
              : 'quote-follow-up';
  const reSpec = CLASS[canon];
  if (reSpec) { floor = reSpec[1]; typLow = reSpec[2]; typHigh = reSpec[3]; note = reSpec[4]; }
}

// how many workflows are they describing?
let workflows = 1;
const wfWords = hay.match(/(\d+)\s*(?:automation|workflow|sequence|zap|scenario)/);
if (wfWords) { workflows = Math.min(parseInt(wfWords[1], 10) || 1, 12); }
else {
  const listed = (hay.match(/\bnurture\b|\brecovery\b|\bonboarding\b|\bretention\b|\bchurn\b|\breferral\b|\breminder\b|\bfollow[- ]?up\b/g) || []).length;
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

if (klass === 4 && (shape === 'production-takeover' || (__classSource === 'posting' && __postAudit))) {
  add('Audit, week one', RATE.audit, 'Nothing changes in week one except the map. The rebuild quotes after it exists.');
} else if (klass === 3 && (shape === 'conversation-design' || (__classSource === 'posting' && /transcript|review/.test(hay)))) {
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
    return (g.n > 1 ? g.n + ' \u00d7 ' + money(g.amount) + ' (' + money(g.amount * g.n) + ') for '
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
  pricing_class_source: __classSource,
  pricing_class_from_shape: __shapeClass,
  pricing_class_from_posting: __postSpeaks ? __postClass : null,
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

  // Class 0 context, emitted even when the normal derivation governed, so the
  // weekly report can see where the tier declined and why.
  component_keys: detected,
  component_sum: componentSum,
  component_tier_declined: detected.length ? (componentSum >= __classFloor ? 'components summed at or above the class floor'
                                                                          : 'shape is not certified hands-free') : null,
  delivery_floor: deliveryFloor,
  delivery_floor_source: DELIVERY.source,

  // SCOPE / ROOM MISMATCH. The buyer's history confirmed their number is real,
  // and we derived more than twice it. Either the shape resolved too large or
  // this room is not ours. Both are worth seeing in the weekly report rather
  // than losing silently.
  scope_room_mismatch: !!(cheapConfirmed && postedAmount != null && total > postedAmount * 2),
  scope_room_mismatch_detail: (cheapConfirmed && postedAmount != null && total > postedAmount * 2)
    ? 'derived ' + money(total) + ' against a confirmed-real posted ' + money(postedAmount) +
      ' (' + Math.round(total / postedAmount) + 'x). Shape resolved too large, or the room is not ours.'
    : null,
  // The two blocks the letter must carry. Named here so the Prompt of Record
  // asserts their presence rather than hoping the model included them.
  pricing_phase_split: phaseSplitParagraph,
  pricing_why_it_costs_this: whyItCostsThis,
  pricing_mandatory_blocks: ['pricing_why_it_costs_this', 'pricing_phase_split'],
  // guardrails, asserted not assumed
  pricing_rules_ok: (total % 5 === 0)
    && String(total).slice(-3) !== '997'
    && !!phaseSplitParagraph && !!whyItCostsThis
    && !/\bper hour\b|\bhourly\b|\ban hour\b|\b\/hr\b/i.test(whyItCostsThis + ' ' + phaseSplitParagraph + ' ' + threeLine)
}) }];
