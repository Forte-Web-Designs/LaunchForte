// Route the job.
//
// Triage v2, as arithmetic. This node runs BEFORE any effort spends and answers
// one question: which of the four lanes does this job belong in, and is Fortress
// PROVABLY able to hold it hands-free.
//
// The prime rule, in code:
//   Underpaid work is permitted ONLY where Fortress provably handles the job all
//   the way, end to end, with no issue of any kind. Provably means the six checks
//   below, never a prediction.
//
// Which forces one design decision that governs the whole file:
//
//   EVERY CHECK FAILS CLOSED.
//
// A missing record is a failed check, not a skipped one. If the builds registry
// is not upstream, check 1 fails. If a tool has no row in the known-path library,
// check 2 fails. If the rehearsal timestamp is empty, check 6 fails. The gate
// opens only as real records appear, and it can never open by accident of
// plumbing. When in doubt, the doubt decides: full price or no bid.
//
// Nothing here changes how value-room jobs are treated. A heavy job comes out of
// this node routed 'heavy' with every downstream stage untouched, which is the
// point: the $15k engine is not in scope, and everything below it gets a lane
// instead of a judgement call.

// ---------------------------------------------------------------------------
// DIALS. Every one of these is a stated policy number, not a tuned constant.
// ---------------------------------------------------------------------------

// The volume lane ships OFF. It opens when Seth sets or confirms the floor and
// the monthly connects budget — build note 3. Until then a certified job is
// still routed and still reported; it just does not bid.
const LANE = {
  enabled: false,
  floor: 200,                    // BID minimum for certified hands-free rooms. Nothing else.
  connects_budget_monthly: null, // unset. The lane cannot open with this null.
  rehearsal_max_age_days: 14     // check 6
};

// The catalogue floors. These govern every ladder and full-treatment quote
// exactly as written in LAUNCH_FORTE_PRICING_CATALOG.md; triage only reads them
// to decide whether a posted budget is worth a full package or a short reply.
const CATALOG_FIX_FLOOR = 500;

// Projected Seth-minutes. Each part is a thing that actually consumes his hands.
const PSM = {
  signin_assist: 15,   // he signs in, the session gets handed over
  red_confirm: 30,     // the rollback law: every live-system change validated and reversible
  call: 60,            // scheduling, the call itself, the notes after
  thread_round: 5,     // one round of back-and-forth in the Upwork thread
  no_proven_kit: 90,   // no kit means he defines the build before anything runs
  unknown_surface: 30, // a surface with no known path is a surface he walks first
  unknown_surface_cap: 90
};

// Shapes whose delivery is calls, scoping or migration by nature. These are
// full treatment regardless of what the posting says, because the scoping
// conversation is the work.
const HEAVY_SHAPES = [
  'platform-migration', 'crm-implementation', 'saas-backend-build',
  'workspace-rearchitecture', 'automation-stack-standup',
  'expert-architecture-advisory', 'production-takeover',
  'voice-agent-intake', 'service-desk-standup', 'warehouse-modeling'
];

// ---------------------------------------------------------------------------
// UPSTREAM READS. Every one optional, every one failing closed.
// ---------------------------------------------------------------------------

const readNode = function (name) {
  try {
    const all = $(name).all();
    return all.map(function (i) { return i.json; }).filter(Boolean);
  } catch (e) {
    return null; // not upstream on this branch. Null is distinct from empty.
  }
};

// The job row. This node sits downstream of three data-table reads, so $json is
// whatever the last read emitted, not the posting. Merge Context is where the job
// row actually lives; $json is the fallback for running this node anywhere else
// (the ingest path, the fixture harness).
let input = $json || {};
(function () {
  const mc = readNode('Merge Context');
  if (mc && mc[0] && (mc[0].title || mc[0].description)) { input = mc[0]; }
})();

// The resolved shape, if Ground Match got there first.
let shape = input.evidence_shape || input.shape || null;
if (!shape) {
  const gm = readNode('Ground Match');
  if (gm && gm[0]) { shape = gm[0].evidence_shape || gm[0].shape || null; }
}

const shapesRows  = readNode('Read Shapes (Cockpit)') || readNode('Read Shapes');
const buildsRows  = readNode('Read Builds G')  || readNode('Read Builds');
const toolsRows   = readNode('Read Tools KB')  || readNode('Read Tools');
const wallsRows   = readNode('Read Blockers')  || readNode('Read Walls');

// ---------------------------------------------------------------------------
// THE POSTING, normalised.
// ---------------------------------------------------------------------------

const hay = [input.title, input.description, input.skills, input.angle, input.reason]
  .filter(Boolean).join(' ').toLowerCase();

const jobType = String(input.job_type || '').toUpperCase();
const budgetRaw = String(input.budget == null ? '' : input.budget).trim();

// "2400 USD" -> fixed 2400. "20-45/hr" -> hourly, top of band. "not stated" -> null.
const parseBudget = function (s) {
  const t = s.toLowerCase();
  if (!t || /not stated|n\/a|none/.test(t)) return { kind: 'not_stated', amount: null, high: null };
  const hourly = /\/\s*hr|per hour|hourly|an hour/.test(t) || jobType === 'HOURLY';
  const nums = (t.match(/\d[\d,]*(?:\.\d+)?/g) || []).map(function (n) { return parseFloat(n.replace(/,/g, '')); });
  if (!nums.length) return { kind: hourly ? 'hourly' : 'not_stated', amount: null, high: null };
  return {
    kind: hourly ? 'hourly' : 'fixed',
    amount: nums[0],
    high: nums.length > 1 ? nums[nums.length - 1] : nums[0]
  };
};
const budget = parseBudget(budgetRaw);

// ---------------------------------------------------------------------------
// GRADE 2: BUYER MATH. Adjusts where in a range a quote lands. NEVER gates.
// Missing stats never block routing — they just leave room null.
// ---------------------------------------------------------------------------

const spend = Number(input.client_spend);
const hires = Number(input.client_hires);
let buyerAvgPerHire = null;
if (isFinite(spend) && isFinite(hires) && hires > 0) {
  buyerAvgPerHire = Math.round((spend / hires) * 100) / 100;
} else if (isFinite(Number(input.avg_per_contract)) && Number(input.avg_per_contract) > 0) {
  buyerAvgPerHire = Number(input.avg_per_contract);
}

let room = null;
const postedAtOrUnderFixFloor = budget.kind === 'fixed' && budget.amount != null && budget.amount <= CATALOG_FIX_FLOOR;
if (postedAtOrUnderFixFloor || (buyerAvgPerHire != null && buyerAvgPerHire < 500)) {
  room = 'auction';
} else if (budget.amount != null || buyerAvgPerHire != null) {
  room = 'value';
}
// room stays null when nothing is known. Null never blocks.

// A posted FIXED budget under the lane floor. The one figure that ends a job
// with no reply at all, because there is no price at which the auction is worth
// entering.
const roomBelowFloor = budget.kind === 'fixed' && budget.amount != null && budget.amount < LANE.floor;

// ---------------------------------------------------------------------------
// THE TWO POSTING SIGNALS the shape record cannot supply.
// ---------------------------------------------------------------------------

// A call with US, not "API call", not "call center", not "after-hours calls".
const CALL_RE = /(discovery|kick[\s-]?off|intro(?:ductory)?|onboarding|quick|initial|brief|short)\s+(call|zoom|meeting|chat)|(hop|jump|get|be)\s+on\s+a\s+(call|zoom)|(schedule|book|set\s?up|arrange)\s+a\s+(call|zoom|meeting|time)|\b(zoom|google\s?meet|ms\s?teams)\s+(call|meeting)|call\s+with\s+(us|me|our\s+team)|speak\s+(with|to)\s+(us|me|our\s+team)|weekly\s+(call|sync|standup)/;
const needsCall = CALL_RE.test(hay);

// Client-account access. The shape record is authoritative; the posting is only
// a fallback, and the fallback is deliberately broad because a false "no access
// needed" is the expensive error.
const ACCESS_RE = /(our|my|their|the client'?s?)\s+(account|crm|portal|instance|workspace|sub[\s-]?account|system|dashboard|backend|admin|tenant|environment|site)|admin\s+access|give\s+(you|us)\s+access|grant\s+access|provide\s+(you\s+)?(with\s+)?(access|credentials|logins?)|credentials\s+will|access\s+to\s+our/;
let accessSource = 'posting';
let needsClientAccount = ACCESS_RE.test(hay);
if (shape && shapesRows) {
  const row = shapesRows.filter(function (r) { return r.shape === shape; })[0];
  if (row) {
    const al = String(row.access_list || '').trim();
    // A shape record with a populated access_list names, in words, the client
    // account the delivery needs. That is a record, not an inference.
    needsClientAccount = al.length > 0 && !/^(none|n\/a|no access)/i.test(al);
    accessSource = 'shape_record';
  }
}

// Thread weight: how many rounds of back-and-forth this posting is going to cost
// before it is even scoped. Vague postings cost more rounds.
const vague = hay.length < 300 || !/\d/.test(hay);
const threadRounds = vague ? 6 : 2;

// ---------------------------------------------------------------------------
// TOOL SURFACES IN THE DELIVERY PLAN.
// ---------------------------------------------------------------------------

let planTools = [];
if (toolsRows) {
  const seen = {};
  toolsRows.forEach(function (t) {
    const name = String(t.tool || '').toLowerCase().trim();
    if (!name || seen[name] || name.length < 3) return;
    if (hay.indexOf(name) === -1) return;
    seen[name] = true;
    planTools.push(t);
  });
}

// ---------------------------------------------------------------------------
// THE CERTIFICATION GATE. Six checks, every one a lookup, every one failing closed.
// ---------------------------------------------------------------------------

const checks = [];
const check = function (n, name, pass, detail) { checks.push({ n: n, name: name, pass: !!pass, detail: detail }); };

// 1. PROVEN KIT. Built end to end before, with proof. A row that says
//    "estimated only, nothing built" is a brief, not a kit.
(function () {
  if (!buildsRows) { return check(1, 'proven_kit', false, 'builds registry not readable from here'); }
  const proven = buildsRows.filter(function (b) {
    const st = String(b.status || '').toLowerCase();
    const stub = String(b.stubs || '').toLowerCase();
    const isProven = (st === 'proven' || st === 'built' || st === 'delivered' || st === 'shipped')
      && Number(b.proven_minutes) > 0
      && !/estimated only|nothing built/.test(stub);
    if (!isProven) return false;
    const cls = String(b.shape_class || '').toLowerCase();
    return shape && (cls === String(shape).toLowerCase() || cls.indexOf(String(shape).toLowerCase()) !== -1);
  });
  check(1, 'proven_kit', proven.length > 0,
    proven.length ? proven[0].slug + ' proven at ' + proven[0].proven_minutes + ' minutes'
                  : 'no proven kit for ' + (shape || 'an unresolved shape') + ' — kit candidate, never a volume bid');
})();

// 2. KNOWN PATH per surface. Exact clicks on file, or a working API route.
(function () {
  if (!toolsRows) { return check(2, 'known_path', false, 'known-path library not readable from here'); }
  if (!planTools.length) { return check(2, 'known_path', false, 'no tool surface resolved, so no path can be on file'); }
  const missing = planTools.filter(function (t) {
    const ep = String(t.endpoint_status || '');
    const apiRoute = /^answered 2/.test(ep);
    const clicks = String(t.notes || '').length > 40 && String(t.have_credential || '') === 'yes';
    return !(apiRoute || clicks);
  }).map(function (t) { return t.tool; });
  check(2, 'known_path', missing.length === 0,
    missing.length ? 'no path on file for: ' + missing.join(', ') : planTools.length + ' surfaces have a path on file');
})();

// 3. ZERO OPEN WALLS on those surfaces.
(function () {
  if (!wallsRows) { return check(3, 'no_open_walls', false, 'known-walls ledger not readable from here'); }
  const open = wallsRows.filter(function (w) {
    const st = String(w.status || '').toLowerCase();
    if (st !== 'open' && st !== 'sent') return false;
    const subj = String(w.subject || '').toLowerCase();
    if (!subj) return false;
    return planTools.some(function (t) { return String(t.tool || '').toLowerCase() === subj; }) || hay.indexOf(subj) !== -1;
  });
  check(3, 'no_open_walls', open.length === 0,
    open.length ? 'open wall: ' + open.map(function (w) { return w.subject + ' (' + w.blocker_id + ')'; }).join(', ')
                : 'no open wall on the resolved surfaces');
})();

// 4. NO CLIENT-ACCOUNT ACCESS.
check(4, 'no_client_account', !needsClientAccount,
  needsClientAccount ? 'delivery needs their account (' + accessSource + ')' : 'house-deliverable, no client account');

// 5. NO CALL.
check(5, 'no_call', !needsCall, needsCall ? 'the posting asks for a call' : 'no call asked for');

// 6. FRESHNESS. A green rehearsal within fourteen days. Guarantees in this
//    domain are rehearsed, never purchased.
(function () {
  if (!toolsRows) { return check(6, 'freshness', false, 'known-path library not readable, so no rehearsal can be read'); }
  if (!planTools.length) { return check(6, 'freshness', false, 'no surface resolved, so no rehearsal to read'); }
  const cutoff = Date.now() - LANE.rehearsal_max_age_days * 86400000;
  const stale = planTools.filter(function (t) {
    const ts = Date.parse(t.session_last_verified || '');
    return !isFinite(ts) || ts < cutoff;
  }).map(function (t) { return t.tool; });
  check(6, 'freshness', stale.length === 0,
    stale.length ? 'rehearsal missing or older than ' + LANE.rehearsal_max_age_days + ' days for: ' + stale.join(', ')
                 : 'all surfaces rehearsed green inside ' + LANE.rehearsal_max_age_days + ' days');
})();

const failed = checks.filter(function (c) { return !c.pass; });
const certified = failed.length === 0;
// Named, so a false never arrives without a reason attached.
const certifiedFailedCheck = certified ? null : failed.map(function (c) { return c.n + ':' + c.name; }).join(', ');

// Everything passes EXCEPT the client-account check. That is the listing lane:
// the shape could be hands-free, the delivery just lives in their tenant.
const onlyAccessFails = failed.length === 1 && failed[0].n === 4;

// ---------------------------------------------------------------------------
// GRADE 1: psm_estimate, THE ROUTER.
// ---------------------------------------------------------------------------

const psmParts = [];
const addPsm = function (label, minutes, why) { if (minutes > 0) psmParts.push({ label: label, minutes: minutes, why: why }); };

if (needsClientAccount) {
  addPsm('Sign-in assist', PSM.signin_assist, 'his hands on the login, then the session hands over');
  addPsm('RED confirm taps', PSM.red_confirm, 'the rollback law: every live-system change validated and reversible');
}
if (needsCall) addPsm('Call', PSM.call, 'scheduling, the call, and the notes after it');
addPsm('Thread', threadRounds * PSM.thread_round, threadRounds + ' rounds of back-and-forth before it is even scoped');
if (!checks[0].pass) addPsm('No proven kit', PSM.no_proven_kit, 'he defines the build before anything can run');
if (!checks[1].pass) {
  const n = Math.min(Math.max(planTools.length, 1), 3);
  addPsm('Unknown surfaces', Math.min(n * PSM.unknown_surface, PSM.unknown_surface_cap), 'a surface with no path on file is a surface he walks first');
}

const psmEstimate = psmParts.reduce(function (a, p) { return a + p.minutes; }, 0);

// ---------------------------------------------------------------------------
// THE FOUR ROUTES.
// ---------------------------------------------------------------------------

const heavyShape = shape && HEAVY_SHAPES.indexOf(String(shape)) !== -1;
let route, routeWhy;

if (needsCall || heavyShape) {
  route = 'heavy';
  routeWhy = needsCall ? 'a call is asked for, so the scoping conversation is the work'
                       : 'the shape is calls, scoping or migration by nature';
} else if (certified) {
  route = 'hands_free_house';
  routeWhy = 'all six checks pass against records that already exist';
} else if (onlyAccessFails) {
  route = 'hands_free_shape_client_access';
  routeWhy = 'the shape could be hands-free; delivery needs their account';
} else {
  route = 'assisted';
  routeWhy = 'real Seth-minutes: ' + failed.map(function (c) { return c.name; }).join(', ');
}

// The volume lane is fixed-price only. Hourly is impossible by mechanism,
// because the time tracker screenshots the working screen.
const hourlyBlocksLane = budget.kind === 'hourly' || jobType === 'HOURLY';
if (route === 'hands_free_house' && hourlyBlocksLane) {
  route = 'assisted';
  routeWhy = 'hourly post: the volume lane is impossible by mechanism, the tracker screenshots the screen';
}
// The lane also requires a stated budget at or above the floor.
if (route === 'hands_free_house' && !(budget.kind === 'fixed' && budget.amount != null && budget.amount >= LANE.floor)) {
  route = 'assisted';
  routeWhy = 'no stated fixed budget at or above the $' + LANE.floor + ' lane floor';
}

// ---------------------------------------------------------------------------
// WHAT ACTUALLY HAPPENS. The route is a lane; the action is the behaviour.
// ---------------------------------------------------------------------------

// The judge's existing A/B/C score, if it ran. Triage reads it; triage never
// recomputes it. An empty score means unscored, not failed.
const judgeScore = String(input.score || '').trim().toUpperCase() || null;

let action, actionWhy, bid = null;
const listingCandidate = route === 'hands_free_shape_client_access' || (needsClientAccount && !needsCall && !heavyShape);

if (roomBelowFloor) {
  action = 'no_bid';
  actionWhy = 'posted $' + budget.amount + ' sits under the $' + LANE.floor + ' floor. No bid, no reply, nothing spends.';
} else if (route === 'hands_free_shape_client_access') {
  action = 'no_bid';
  actionWhy = 'the tier gets served on a shelf instead of in an auction: this files a listing candidate, not a bid.';
} else if (route === 'hands_free_house') {
  if (LANE.enabled && LANE.connects_budget_monthly != null) {
    action = 'lane_bid';
    bid = LANE.floor;
    actionWhy = 'certified hands-free. Bid the floor within minutes of the alert; speed is the weapon and the floor is the boundary.';
  } else {
    action = 'lane_held';
    actionWhy = 'certified, but the volume lane ships OFF until the floor and the monthly connects budget are confirmed.';
  }
} else if (room === 'auction') {
  // Heavy runs through this same test rather than around it. "Full treatment:
  // calls, scoping, migrations — VALUE ROOMS ONLY." A job that needs a call is
  // not thereby worth a package; needing a call in a thin room is the most
  // expensive combination there is.
  action = 'short_reply';
  actionWhy = 'thin room on a job that costs real minutes. The short courteous template, no full package.';
} else if (judgeScore === 'C' || judgeScore === 'U') {
  // Triage adds lanes BELOW the judge; it does not overrule it. The A/B/C score
  // already answered "is this an A-fit", and a C is not one. Promoting a C to a
  // full package because the buyer happens to be rich is how 2,646 postings in
  // this corpus talked themselves into a package nobody would have approved.
  action = 'short_reply';
  actionWhy = 'a real room, but the judge scored this ' + judgeScore + '. Lanes sit below the judge, they do not overrule it.';
} else {
  action = 'full_package';
  actionWhy = 'real minutes and a real room: ladder pricing, the articulation does the selling.';
}

// The cockpit should not spend on anything that is not getting a package.
const triageStop = (action === 'no_bid' || action === 'lane_held' || action === 'lane_bid');

// ---------------------------------------------------------------------------

return [{ json: Object.assign({}, input, {
  triaged: true,
  triage_version: 'v2',

  // grade 1, the router
  psm_estimate: psmEstimate,
  psm_parts: psmParts,

  // grade 2, the price adjuster. Never a gate.
  buyer_avg_per_hire: buyerAvgPerHire,
  room: room,
  room_below_floor: roomBelowFloor,

  // the lane
  route: route,
  route_why: routeWhy,
  listing_candidate: listingCandidate,

  // the gate
  certified: certified,
  certified_failed_check: certifiedFailedCheck,
  certification_checks: checks,

  // what happens
  triage_action: action,
  triage_action_why: actionWhy,
  triage_stop: triageStop,
  triage_bid: bid,

  // context the letter and the pricing node read
  triage_needs_call: needsCall,
  triage_needs_client_account: needsClientAccount,
  triage_access_source: accessSource,
  triage_budget_kind: budget.kind,
  triage_budget_amount: budget.amount,
  triage_hourly_convert: hourlyBlocksLane,
  triage_shape: shape,
  triage_judge_score: judgeScore,
  triage_tools: planTools.map(function (t) { return t.tool; }),
  lane_enabled: LANE.enabled,
  lane_floor: LANE.floor,

  // guardrails, asserted not assumed
  triage_rules_ok:
    ['hands_free_house', 'hands_free_shape_client_access', 'assisted', 'heavy'].indexOf(route) !== -1
    && checks.length === 6
    && (certified === (checks.filter(function (c) { return c.pass; }).length === 6))
    && (certified || !!certifiedFailedCheck)
    && !(route === 'hands_free_house' && (needsCall || needsClientAccount))
    && !(action === 'lane_bid' && !LANE.enabled)
    && !(action === 'lane_bid' && bid < LANE.floor)
    && !(roomBelowFloor && action !== 'no_bid')
}) }];
