#!/usr/bin/env python3
"""
differentiate.py — replace the shared boilerplate in each kit with logic that is
actually specific to its shape.

Four Code nodes were byte-identical across all 17 kits: the rate limit, the
logger, the weekly read, and the gap report. The gap report was the worst of
them, because its NAME promised specifics while its body was a template. A
technical buyer who opens two of these side by side sees padding, and padding
costs the deal.

This rewrites those four bodies per shape, and replaces the single-boolean
decision with a condition that shows real reasoning.
"""
import json, glob, os

# ceiling: (calls per minute, why that number)
# log: the fields worth keeping for THIS shape
# digest: the weekly gap report, written to match its own name
S = {
"storefront-upsell": dict(
  ceiling=(40, "Storefront APIs throttle hard during flash sales, which is exactly when this fires most"),
  log="orderId: $json.order_id, companion: $json.companion || 'none', suggested: $json.outcome === 'suggested'",
  digest="""// Which companions actually converted — the only number that justifies the build.
const runs = Object.values($getWorkflowStaticData('global').runs || {});
const week = runs.filter(r => r.at > Date.now() - 7*864e5);
const suggested = week.filter(r => r.suggested);
const taken = suggested.filter(r => r.accepted);
const rate = suggested.length ? Math.round(taken.length / suggested.length * 100) : null;
return [{ json: {
  suggested: suggested.length,
  taken: taken.length,
  note: rate === null
    ? 'No companions suggested this week. Either the catalogue has no pairs or the rules are too tight.'
    : `${rate}% of suggestions converted. Pairs that never convert should be retired from the map.`,
} }];""",
  decide="={{ $json.companion != null && $json.companion.inStock && !$json.alreadyOwned }}"),

"books-reconciliation": dict(
  ceiling=(30, "Ledger APIs are the slowest in the stack and rate-limit per organisation, not per key"),
  log="payoutId: $json.payout_id, amount: $json.amount, matched: $json.matched, delta: $json.delta || 0",
  digest="""// What is still unreconciled, and how old — this is the number the bookkeeper opens first.
const open = Object.values($getWorkflowStaticData('global').unmatched || {});
const now = Date.now();
const aged = open.map(o => ({ ...o, days: Math.floor((now - o.at) / 864e5) }));
const over30 = aged.filter(o => o.days > 30);
return [{ json: {
  unmatched: aged.length,
  oldestDays: aged.length ? Math.max(...aged.map(o => o.days)) : 0,
  over30: over30.length,
  note: over30.length
    ? `${over30.length} items past 30 days. These are the ones that turn into a month-end problem.`
    : 'Nothing aged past 30 days.',
} }];""",
  decide="={{ $json.matched === true && Math.abs($json.delta) < 0.01 }}"),

"scheduling": dict(
  ceiling=(60, "Reminder bursts cluster at the top of the hour, so the ceiling has to survive a spike"),
  log="bookingId: $json.booking_id, startsAt: $json.starts_at, attended: $json.attended",
  digest="""// No-shows recovered versus lost — the difference is the whole ROI of this build.
const runs = Object.values($getWorkflowStaticData('global').runs || {});
const week = runs.filter(r => r.at > Date.now() - 7*864e5);
const noShows = week.filter(r => r.attended === false);
const rebooked = noShows.filter(r => r.rebooked);
return [{ json: {
  noShows: noShows.length,
  rebooked: rebooked.length,
  lost: noShows.length - rebooked.length,
  note: noShows.length
    ? `${rebooked.length} of ${noShows.length} no-shows rebooked. The rest are paid-for demand that evaporated.`
    : 'No no-shows this week.',
} }];""",
  decide="={{ $json.attended === true || $json.rescheduled === true }}"),

"reporting": dict(
  ceiling=(20, "Each run fans out across every source, so one report is many upstream calls"),
  log="period: $json.period, sources: $json.sourcesRead, n: $json.n, published: $json.published",
  digest="""// Which sources went quiet this week — a silent source is a wrong report.
const seen = $getWorkflowStaticData('global').sources || {};
const stale = Object.entries(seen)
  .filter(([, at]) => at < Date.now() - 7*864e5)
  .map(([name]) => name);
return [{ json: {
  sourcesTracked: Object.keys(seen).length,
  stale,
  note: stale.length
    ? `${stale.join(', ')} sent nothing for 7 days. The report is quietly smaller, not smaller.`
    : 'Every source reported in the last 7 days.',
} }];""",
  decide="={{ $json.n >= 30 && $json.sourcesRead === $json.sourcesExpected }}"),

"system-sync": dict(
  ceiling=(50, "Both directions share this ceiling, so a burst on one side must not starve the other"),
  log="recordId: $json.record_id, source: $json.source, echo: $json.isEcho, written: $json.written",
  digest="""// Records that drifted apart anyway — the ones the sync could not resolve.
const drift = Object.values($getWorkflowStaticData('global').drift || {});
const unresolved = drift.filter(d => !d.resolved);
return [{ json: {
  drifted: unresolved.length,
  bothChanged: unresolved.filter(d => d.bothSidesChanged).length,
  note: unresolved.length
    ? `${unresolved.length} records disagree. Where both sides changed, a human has to pick a winner.`
    : 'Both systems agree on every record.',
} }];""",
  decide="={{ $json.isEcho !== true && $json.remoteUpdatedAt < $json.localUpdatedAt }}"),

"lead-routing": dict(
  ceiling=(80, "Paid campaigns deliver leads in bursts and the fast lane is worthless if it queues"),
  log="leadId: $json.lead_id, source: $json.source, score: $json.score, owner: $json.owner, lane: $json.lane",
  digest="""// Median speed to lead, by owner — the number that actually changes behaviour.
const runs = Object.values($getWorkflowStaticData('global').runs || {});
const week = runs.filter(r => r.at > Date.now() - 7*864e5 && r.firstTouchMs);
const byOwner = {};
for (const r of week) (byOwner[r.owner] ||= []).push(r.firstTouchMs);
const median = a => { const s=[...a].sort((x,y)=>x-y); return s[Math.floor(s.length/2)]; };
const rows = Object.entries(byOwner).map(([owner, ms]) => ({
  owner, medianMinutes: Math.round(median(ms) / 60000), leads: ms.length }));
const slow = rows.filter(r => r.medianMinutes > 5);
return [{ json: { rows, note: slow.length
  ? `${slow.map(r=>r.owner).join(', ')} are past the 5 minute mark. That is where the leads are dying.`
  : 'Every owner is inside 5 minutes.' } }];""",
  decide="={{ $json.score >= 70 && $json.owner != null }}"),

"stalled-deal-escalation": dict(
  ceiling=(25, "This runs as a sweep over the whole pipeline, so it must not exhaust the CRM quota"),
  log="dealId: $json.deal_id, stage: $json.stage, idleDays: $json.idleDays, escalatedTo: $json.escalatedTo",
  digest="""// What is still stalled, and on whom — named, because unnamed stalls never move.
const stalled = Object.values($getWorkflowStaticData('global').stalled || {});
const byOwner = {};
for (const d of stalled) (byOwner[d.owner] ||= []).push(d);
const rows = Object.entries(byOwner).map(([owner, deals]) => ({
  owner, count: deals.length,
  oldestDays: Math.max(...deals.map(d => d.idleDays)),
  value: deals.reduce((s, d) => s + (d.value || 0), 0) }));
return [{ json: { rows, note: rows.length
  ? `${rows.reduce((s,r)=>s+r.count,0)} deals stalled, worth ${rows.reduce((s,r)=>s+r.value,0)}. Escalation is by owner, not a group email.`
  : 'Nothing stalled past the window.' } }];""",
  decide="={{ $json.touchedRecently !== true && $json.idleDays >= 7 && $json.stage !== 'closed' }}"),

"quote-follow-up": dict(
  ceiling=(45, "Cadence touches batch overnight and must not trip the sending provider"),
  log="quoteId: $json.quote_id, touch: $json.touchNumber, replied: $json.replied, stopped: $json.stopped",
  digest="""// Quotes still unanswered, and how old — a quote nobody chased is a quote nobody lost fairly.
const open = Object.values($getWorkflowStaticData('global').quotes || {}).filter(q => !q.replied);
const now = Date.now();
const aged = open.map(q => ({ ...q, days: Math.floor((now - q.sentAt) / 864e5) }));
const cold = aged.filter(q => q.days > 14);
return [{ json: {
  open: aged.length,
  cold: cold.length,
  value: cold.reduce((s, q) => s + (q.value || 0), 0),
  note: cold.length
    ? `${cold.length} quotes past 14 days with no reply. Past that the cadence stops and a human should call.`
    : 'Every open quote is inside the cadence window.',
} }];""",
  decide="={{ $json.replied !== true && $json.touchNumber < 4 }}"),

"approval-routing": dict(
  ceiling=(35, "Approval bursts follow month-end, so the ceiling is sized for the spike not the average"),
  log="requestId: $json.request_id, amount: $json.amount, band: $json.band, approver: $json.approver, auto: $json.withinBand",
  digest="""// Approvals still waiting, and on whom — the bottleneck has a name or it never clears.
const waiting = Object.values($getWorkflowStaticData('global').pending || {});
const byApprover = {};
for (const r of waiting) (byApprover[r.approver] ||= []).push(r);
const rows = Object.entries(byApprover).map(([approver, items]) => ({
  approver, waiting: items.length,
  oldestHours: Math.round(Math.max(...items.map(i => Date.now() - i.at)) / 36e5) }));
const stuck = rows.filter(r => r.oldestHours > 48);
return [{ json: { rows, note: stuck.length
  ? `${stuck.map(r=>r.approver).join(', ')} have items past 48 hours. That is the bottleneck, by name.`
  : 'Nothing waiting past 48 hours.' } }];""",
  decide="={{ $json.withinBand === true && $json.approver != null && $json.amount > 0 }}"),

"platform-migration": dict(
  ceiling=(15, "Migration batches are heavy reads; a low ceiling is deliberate so the source stays usable"),
  log="batchId: $json.batch_id, sourceCount: $json.sourceCount, destCount: $json.destCount, committed: $json.countsMatch",
  digest="""// Batches migrated, and anything left behind — the second half is the one that matters.
const batches = Object.values($getWorkflowStaticData('global').batches || {});
const failed = batches.filter(b => !b.committed);
const orphaned = failed.reduce((s, b) => s + (b.sourceCount - b.destCount), 0);
return [{ json: {
  batches: batches.length,
  rolledBack: failed.length,
  recordsLeftBehind: orphaned,
  note: orphaned
    ? `${orphaned} records did not make it. Do not delete anything at source until this reads zero.`
    : 'Every batch reconciled exactly. Source is safe to decommission.',
} }];""",
  decide="={{ $json.countsMatch === true && $json.sourceCount > 0 }}"),

"production-takeover": dict(
  ceiling=(10, "Probing an inherited system deliberately runs slow so we never become its outage"),
  log="jobId: $json.job_id, matchesDocs: $json.matchesDocs, surprise: $json.surprise || null",
  digest="""// What is still undocumented — the map of where the bodies are.
const probes = Object.values($getWorkflowStaticData('global').probes || {});
const surprises = probes.filter(p => !p.matchesDocs);
const byArea = {};
for (const s of surprises) byArea[s.area] = (byArea[s.area] || 0) + 1;
return [{ json: {
  probed: probes.length,
  undocumented: surprises.length,
  byArea,
  note: surprises.length
    ? `${surprises.length} behaviours do not match the docs. Change none of these until each is understood.`
    : 'Observed behaviour matches documentation everywhere we have looked.',
} }];""",
  decide="={{ $json.matchesDocs === true && $json.probeComplete === true }}"),

"data-collection": dict(
  ceiling=(70, "Form spam arrives in floods, and the ceiling is the first line of defence"),
  log="submissionId: $json.submission_id, existing: $json.existing, fieldsFilled: $json.fieldsFilled",
  digest="""// Fields most often left blank — the form is too long exactly there.
const subs = Object.values($getWorkflowStaticData('global').submissions || {});
const blanks = {};
for (const s of subs) for (const f of (s.missing || [])) blanks[f] = (blanks[f] || 0) + 1;
const ranked = Object.entries(blanks).sort((a, b) => b[1] - a[1]).slice(0, 5);
return [{ json: {
  submissions: subs.length,
  worstFields: ranked,
  note: ranked.length
    ? `"${ranked[0][0]}" was skipped ${ranked[0][1]} times. Either make it optional or explain why you need it.`
    : 'Every field is being completed.',
} }];""",
  decide="={{ $json.existing === true && $json.confidence > 0.8 }}"),

"client-onboarding": dict(
  ceiling=(20, "Onboarding fans out into task creation, so one client is many writes"),
  log="clientId: $json.client_id, intakeReturned: $json.intakeReturned, dayCount: $json.dayCount",
  digest="""// Onboardings stuck past day two — the first impression is already going wrong.
const active = Object.values($getWorkflowStaticData('global').onboarding || {});
const stuck = active.filter(c => !c.intakeReturned && c.dayCount >= 2);
return [{ json: {
  inFlight: active.length,
  stuck: stuck.length,
  oldestDays: stuck.length ? Math.max(...stuck.map(c => c.dayCount)) : 0,
  note: stuck.length
    ? `${stuck.length} clients have not returned intake. Day three is where the relationship starts to slip.`
    : 'Every active onboarding is on track.',
} }];""",
  decide="={{ $json.intakeReturned === true && $json.dayCount <= 2 }}"),

"alerting": dict(
  ceiling=(100, "The watchdog must never be the thing that is throttled, so its ceiling is the highest here"),
  log="jobId: $json.job_id, stalled: $json.stalled, minutesSince: $json.minutesSince, alerted: $json.alerted",
  digest="""// Alerts raised, and how many were real — a watchdog nobody trusts gets muted.
const alerts = Object.values($getWorkflowStaticData('global').alerts || {});
const week = alerts.filter(a => a.at > Date.now() - 7*864e5);
const real = week.filter(a => a.confirmed);
const precision = week.length ? Math.round(real.length / week.length * 100) : null;
return [{ json: {
  raised: week.length,
  confirmed: real.length,
  precision,
  note: precision === null ? 'No alerts this week.'
    : precision < 80
      ? `Only ${precision}% of alerts were real. Below 80% people start ignoring them — tighten the threshold.`
      : `${precision}% precision. The alarm is still trusted.`,
} }];""",
  decide="={{ $json.stalled === true && $json.minutesSince > $json.threshold }}"),

"voice-agent-intake": dict(
  ceiling=(60, "Calls arrive in waves after hours and a queued caller hangs up"),
  log="callId: $json.call_id, selfServe: $json.selfServe, intent: $json.intent, escalated: $json.escalated",
  digest="""// Calls handled versus escalated — and which intents keep needing a human.
const calls = Object.values($getWorkflowStaticData('global').calls || {});
const week = calls.filter(c => c.at > Date.now() - 7*864e5);
const escalated = week.filter(c => c.escalated);
const byIntent = {};
for (const c of escalated) byIntent[c.intent] = (byIntent[c.intent] || 0) + 1;
const worst = Object.entries(byIntent).sort((a, b) => b[1] - a[1])[0];
return [{ json: {
  handled: week.length - escalated.length,
  escalated: escalated.length,
  note: worst
    ? `"${worst[0]}" escalated ${worst[1]} times. That is the next intent worth teaching it.`
    : 'Nothing escalated this week.',
} }];""",
  decide="={{ $json.selfServe === true && $json.intentConfidence > 0.7 }}"),

"reactivation": dict(
  ceiling=(25, "Win-backs are a sweep over the whole base and must never look like a blast"),
  log="customerId: $json.customer_id, normalGapDays: $json.normalGap, sinceDays: $json.sinceDays, sent: $json.overdue",
  digest="""// Dormant customers recovered — measured against each customer's own rhythm.
const touched = Object.values($getWorkflowStaticData('global').winbacks || {});
const week = touched.filter(w => w.at > Date.now() - 7*864e5);
const returned = week.filter(w => w.orderedSince);
return [{ json: {
  contacted: week.length,
  returned: returned.length,
  revenue: returned.reduce((s, w) => s + (w.orderValue || 0), 0),
  note: week.length
    ? `${returned.length} of ${week.length} came back. One honest message each — never a series.`
    : 'Nobody was genuinely overdue this week.',
} }];""",
  decide="={{ $json.overdue === true && $json.sinceDays > ($json.normalGap * 1.5) }}"),

"document-assembly": dict(
  ceiling=(30, "Assembly pulls a full record per document, so the ceiling protects the record store"),
  log="recordId: $json.record_id, template: $json.template, resolved: $json.allFieldsResolved, missing: $json.missingFields",
  digest="""// Documents held, and which field was missing — the same field is usually to blame.
const held = Object.values($getWorkflowStaticData('global').held || {});
const counts = {};
for (const h of held) for (const f of (h.missingFields || [])) counts[f] = (counts[f] || 0) + 1;
const ranked = Object.entries(counts).sort((a, b) => b[1] - a[1]);
return [{ json: {
  held: held.length,
  worstField: ranked[0] ? ranked[0][0] : null,
  note: ranked.length
    ? `"${ranked[0][0]}" was missing on ${ranked[0][1]} documents. Fix it upstream and most of these clear.`
    : 'Every document assembled with all fields resolved.',
} }];""",
  decide="={{ $json.allFieldsResolved === true && $json.missingFields.length === 0 }}"),
}

RATE = """// {why}.
const s = $getWorkflowStaticData('global');
const now = Date.now();
s.window = (s.window || []).filter(t => now - t < 60000);
const allowed = s.window.length < {n};
if (allowed) s.window.push(now);
return [{{ json: {{ ...$json, allowed, ceiling: {n}, inWindow: s.window.length }} }}];"""

LOG = """// A path that is not logged cannot be improved. These are the fields worth keeping for this build.
const s = $getWorkflowStaticData('global');
s.runs = s.runs || {{}};
const row = {{ at: Date.now(), {fields} }};
s.runs[$json.dedupeKey] = row;
return [{{ json: {{ ...row, ok: true }} }}];"""

changed = 0
for p in sorted(glob.glob("kits/*.json")):
    slug = os.path.basename(p)[:-5]
    spec = S.get(slug)
    if not spec:
        print("no spec for", slug); continue
    w = json.load(open(p))
    n, why = spec["ceiling"]
    for nd in w["nodes"]:
        nm = nd["name"]
        if nm == "Hold the rate limit":
            nd["parameters"]["jsCode"] = RATE.format(n=n, why=why); changed += 1
        elif nm == "Log the run, both paths":
            nd["parameters"]["jsCode"] = LOG.format(fields=spec["log"]); changed += 1
        elif nd["type"].endswith("code") and nm not in (
                "Validate what arrived", "Read the week of runs") and not nm.startswith("Deduplicate"):
            nd["parameters"]["jsCode"] = spec["digest"]; changed += 1
        elif nd["type"].endswith(".if") and nm not in ("Malformed, refuse it", "Already handled, stop here"):
            nd["parameters"]["conditions"]["conditions"][0]["leftValue"] = spec["decide"]; changed += 1
    json.dump(w, open(p, "w"), indent=2)

print(f"rewrote {changed} node bodies across {len(glob.glob('kits/*.json'))} kits")
