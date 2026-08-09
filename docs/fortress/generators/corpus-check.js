// corpus-check.js — run the LIVE pricing against 6,800 real postings.
//
// WHY THIS EXISTS
// ---------------
// pricing-check.py asserts the rules against twelve hand-written fixtures. All
// twelve passed while the arithmetic was quietly degenerate: on 653 real Upwork
// postings, 49% of them priced at exactly $2,500 and 92% counted exactly one
// workflow. Fixtures cannot find that, because a fixture is a case someone
// already thought of. A corpus can.
//
// WHERE IT RUNS, AND WHY IT IS NOT A PYTHON SCRIPT
// ------------------------------------------------
// The corpus lives in the Cockpit's own `upwork_jobs` data table. It stays
// there. Those are 6,800 real buyers' postings and this repo is public, so a
// snapshot of them is not going in it, and the check does not need one: it
// reads the table over the n8n REST API and reads the CURRENTLY DEPLOYED node
// code out of the workflow. It always tests what is actually live.
//
// Paste into the browser console on the n8n tab (an authenticated n8n session
// is the only credential involved — nothing here touches Upwork, which would
// risk the account and is never automated).
//
// WHAT IT ASSERTS
// ---------------
// Three hard invariants, and one ratchet.
//
//   HARD  no errors            every posting either prices or is refused
//   HARD  guardrails hold      every priced result reports pricing_rules_ok
//   HARD  ceiling discipline   every total over $3,500 carries a phase split
//   RATCH non-degeneracy       the commonest single total may not take a
//                              LARGER share of the corpus than the recorded
//                              baseline
//
// The ratchet is deliberate. The flatline is a known defect, recorded below as
// BASELINE rather than pretended away, and the check's job today is to stop it
// getting worse. When the scope counters are fixed, tighten TARGET downward and
// the ratchet becomes a floor under the improvement.
//
// Recorded 9 August 2026 against 653 priced postings:
//   commonest total  $2,500 at 49%   ·  distinct totals 30
//   median $2,500 · p75 $2,800 · over ceiling 7% (44/44 split)
//   workflows counted > 1 on 8% · systems counted > 2 on 26%
//   every posting with a budget >= $3,000 priced under it (34 of 34)

const BASELINE = { modeShare: 49, distinct: 30, priced: 653 };
const TARGET   = { modeShare: 25 };   // where a fixed scope counter should land

(async () => {
  const bid = localStorage.getItem('n8n-browserId');
  const H = { 'browser-id': bid };
  const log = (...a) => console.log(...a);

  // ---- the corpus, from the Cockpit's own table -----------------------------
  const tables = await (await fetch('/rest/data-tables-global?take=200',
    { credentials: 'include', headers: H })).json();
  const t = tables.data.data.find(x => x.name === 'upwork_jobs');
  if (!t) throw new Error('upwork_jobs not found');

  let all = [];
  for (let skip = 0; ; skip += 250) {
    const r = await (await fetch(
      `/rest/projects/${t.projectId}/data-tables/${t.id}/rows?take=250&skip=${skip}`,
      { credentials: 'include', headers: H })).json();
    const rows = (r.data && (r.data.data || r.data)) || [];
    if (!rows.length) break;
    all = all.concat(rows);
    if (all.length >= (r.data.count || 1e9)) break;
  }

  // Graded worth bidding, fixed price, a real dollar figure, a real posting.
  // Hourly jobs have no total to compare against; "not stated" has no anchor.
  const corpus = all.filter(x =>
    /^[AB]/.test((x.score || '').trim()) &&
    /^\d[\d,]*\s*USD$/i.test((x.budget || '').trim()) &&
    (x.description || '').length > 300);

  // ---- the node code, as deployed ------------------------------------------
  const wf = (await (await fetch('/rest/workflows/Hl5zah3PZcHaEkuo',
    { credentials: 'include', headers: H })).json()).data;
  const src = n => {
    const node = wf.nodes.find(x => x.name === n);
    if (!node) throw new Error('node missing from workflow: ' + n);
    return node.parameters.jsCode;
  };
  const evFn = new Function('$json', '$', src('Pick the evidence to attach'));
  const prFn = new Function('$json', '$', src('Price the build'));
  const NO = () => { throw new Error('no upstream node'); };

  // ---- run ------------------------------------------------------------------
  const results = [];
  for (const j of corpus) {
    const post = { description: j.description, jobTitle: j.title };
    let shape = null, res = null, error = null;
    try { shape = evFn(post, NO)[0].json.evidence_shape; }
    catch (e) { error = 'evidence: ' + e.message; }
    try {
      const $n = name => {
        if (name === 'Pick the evidence to attach')
          return { first: () => ({ json: { evidence_shape: shape } }) };
        throw new Error('no ' + name);
      };
      res = prFn({ job_post: j.description, jobTitle: j.title,
                   channel: 'Upwork', evidence_shape: shape }, $n)[0].json;
    } catch (e) { error = (error ? error + ' | ' : '') + 'pricing: ' + e.message; }
    results.push({ budget: +String(j.budget).replace(/[^0-9]/g, ''), shape, res, error });
  }

  const priced = results.filter(r => r.res && r.res.priced);
  const totals = priced.map(r => r.res.quote_total);
  const counts = {}; totals.forEach(v => counts[v] = (counts[v] || 0) + 1);
  const modeN = Math.max(...Object.values(counts));
  const modeVal = +Object.keys(counts).find(k => counts[k] === modeN);
  const modeShare = Math.round(modeN / priced.length * 100);
  const pct = q => totals.slice().sort((a, b) => a - b)[Math.floor(totals.length * q)];

  // ---- assert ---------------------------------------------------------------
  const fail = [];
  const errored = results.filter(r => r.error);
  if (errored.length) fail.push(`${errored.length} postings threw: ${errored[0].error}`);

  const leaky = priced.filter(r => !r.res.pricing_rules_ok);
  if (leaky.length) fail.push(`${leaky.length} priced results failed their own guardrails`);

  const unsplit = priced.filter(r => r.res.quote_total > 3500 && !r.res.quote_phased);
  if (unsplit.length) fail.push(
    `${unsplit.length} quotes over the $3,500 ceiling with no phase split`);

  if (modeShare > BASELINE.modeShare) fail.push(
    `the arithmetic got flatter: one number ($${modeVal.toLocaleString()}) now takes ` +
    `${modeShare}% of the corpus, baseline ${BASELINE.modeShare}%`);

  // ---- report ---------------------------------------------------------------
  log(`corpus        ${all.length} postings, ${corpus.length} A/B fixed-price with a budget`);
  log(`priced        ${priced.length}   refused ${results.length - priced.length}   errors ${errored.length}`);
  log(`guardrails    ${priced.length - leaky.length}/${priced.length} ok`);
  log(`ceiling       ${priced.filter(r => r.res.quote_total > 3500).length} over $3,500, ` +
      `${unsplit.length} of them unsplit`);
  log(`spread        median $${pct(0.5).toLocaleString()} · p75 $${pct(0.75).toLocaleString()} · ` +
      `${Object.keys(counts).length} distinct totals`);
  log(`concentration $${modeVal.toLocaleString()} takes ${modeShare}% ` +
      `(baseline ${BASELINE.modeShare}%, target ${TARGET.modeShare}%)`);
  const serious = priced.filter(r => r.budget >= 3000);
  log(`under budget  ${serious.filter(r => r.res.quote_total < r.budget).length}/${serious.length} ` +
      `of postings budgeted $3,000+`);
  log('');
  if (fail.length) { log('RESULT: FAIL'); fail.forEach(f => log('  - ' + f)); }
  else if (modeShare > TARGET.modeShare) {
    log(`RESULT: PASS (known defect held, not fixed — concentration ${modeShare}% vs target ${TARGET.modeShare}%)`);
  } else log('RESULT: PASS');

  return { priced: priced.length, modeShare, distinct: Object.keys(counts).length, fail };
})();
