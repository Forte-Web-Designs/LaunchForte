// The priority board — paste into the browser console on launchforte.app.n8n.cloud.
//
// 985 fresh full-package jobs against 10 proposals a week is roughly 99x
// oversupply. Finding work stopped being the constraint some time ago; CHOOSING
// is the constraint, and nothing in the estate was ranking.
//
// The ranking, in one line:
//
//     score = (derived quote ÷ psm_estimate) × judge × buyer × freshness
//
// Return per Seth-minute is the spine, because his minutes are the only input
// that does not scale. The three multipliers are adjustments, never gates —
// same discipline as buyer math in triage.
//
// It reads the DEPLOYED nodes out of the workflow rather than carrying its own
// copy of the arithmetic. No posting text leaves n8n; only the board comes back.

const TOP_N = 15;
const WRITE_RANKS = false;   // true also stamps priority_rank onto proposals rows

(async () => {
  const PROJECT = 'G1EzIclYs4hXjhBw';
  const T = { upwork_jobs: 'iSZB081VXkJjbZs5', shapes: 'BLwjqEoeUemakJll', builds: 'GDNk0omQAG3AujNK',
              tools_kb: 'cstpHScKXAAmdv2y', blockers: '2wuFLuu5V0mvHtHp', proposals: 'ejwx9dNfbqQ4gyyW' };
  const bid = localStorage.getItem('n8n-browserId');
  const H = { 'browser-id': bid };
  const base = '/rest/projects/' + PROJECT + '/data-tables/';
  const page = async (id, skip) => { const r = await fetch(base + id + '/rows?take=250&skip=' + skip, { headers: H, credentials: 'include' }); const j = await r.json(); return j.data && j.data.data ? j.data : j; };
  const pull = async (id) => { const f = await page(id, 0); let rows = f.data.slice(); while (rows.length < f.count) { const n = await page(id, rows.length); if (!n.data.length) break; rows = rows.concat(n.data); } return rows; };

  const wr = await fetch('/rest/workflows/Hl5zah3PZcHaEkuo', { headers: H, credentials: 'include' });
  const wf = (await wr.json()).data;
  const code = n => { const x = wf.nodes.find(y => y.name === n); if (!x) throw new Error(n + ' is not deployed'); return x.parameters.jsCode; };
  const FN = {
    triage: new Function('$json', '$', '"use strict";' + code('Route the job')),
    evid:   new Function('$json', '$', '"use strict";' + code('Pick the evidence to attach')),
    price:  new Function('$json', '$', '"use strict";' + code('Price the build'))
  };

  const corpus = await pull(T.upwork_jobs);
  const REG = { 'Read Shapes (Cockpit)': await pull(T.shapes), 'Read Builds': await pull(T.builds),
                'Read Tools KB': await pull(T.tools_kb), 'Read Blockers': await pull(T.blockers) };
  const mk = extra => name => { const all = Object.assign({}, REG, extra || {}); if (!(name in all)) throw new Error('no node'); const rows = all[name]; return { all: () => rows.map(r => ({ json: r })), first: () => ({ json: rows[0] }) }; };

  const rows = []; let errors = 0;
  for (const j of corpus) {
    try {
      const e = FN.evid(j, mk({ 'Merge Context': [j] }))[0].json;
      const gm = [{ evidence_shape: e.evidence_shape }];
      const t = FN.triage(j, mk({ 'Merge Context': [j], 'Ground Match': gm }))[0].json;
      if (!t.bid_eligible || t.triage_action !== 'full_package') continue;   // the bid pool, nothing else
      if (t.role_shaped) continue;                                          // staffing seats are not builds
      const p = FN.price(Object.assign({}, e, t), mk({ 'Merge Context': [j], 'Ground Match': gm, 'Pick the evidence to attach': [e], 'Route the job': [t] }))[0].json;
      if (!p.priced || !(p.quote_total > 0)) continue;
      rows.push({ j: j, t: t, p: p });
    } catch (ex) { errors++; }
  }

  // ---- the ranking ---------------------------------------------------------
  const GRADE = { A: 1.30, B: 1.00, C: 0.70, U: 0.60 };
  const buyerMult = a => a == null ? 1.00 : a >= 1000 ? 1.25 : a >= 500 ? 1.10 : 0.90;
  const ageMult = d => Math.max(0.55, 1 - (d / 7) * 0.45);

  const board = rows.map(r => {
    const psm = Math.max(r.t.psm_estimate, 5);   // never divide by zero, never flatter a job to infinity
    const perMin = r.p.quote_total / psm;
    const g = GRADE[r.t.triage_judge_score] || 0.85;
    const b = buyerMult(r.t.buyer_avg_per_hire);
    const a = ageMult(r.t.age_days);
    return { r: r, quote: r.p.quote_total, psm: psm, perMin: perMin, g: g, b: b, a: a, score: perMin * g * b * a };
  }).sort((x, y) => y.score - x.score);

  const why = b => {
    const bits = ['$' + Math.round(b.perMin) + ' per Seth-minute'];
    if (b.g >= 1.3) bits.push('judge A'); else if (b.g <= 0.7) bits.push('judge ' + (b.r.t.triage_judge_score || '?'));
    bits.push(b.r.t.buyer_avg_per_hire != null ? 'buyer averages $' + Math.round(b.r.t.buyer_avg_per_hire) + ' a hire' : 'no buyer history');
    bits.push(b.r.t.age_days + 'd old');
    if (b.r.t.placeholder_budget) bits.push('posted number ignored as a placeholder');
    if (b.r.t.needs_sign_in) bits.push(b.r.t.needs_sign_in_flag);
    return bits.join(' · ');
  };

  console.log('PRIORITY BOARD — ' + board.length + ' bid-eligible priced full-package jobs, ' + errors + ' errors');
  console.log('score = (quote / psm) x judge x buyer x freshness');
  console.log('');
  board.slice(0, TOP_N).forEach((b, i) => {
    console.log((i + 1) + '. $' + b.quote + '  ' + b.psm + 'min  score ' + b.score.toFixed(1));
    console.log('   ' + String(b.r.j.title || '').replace(/\s+/g, ' ').slice(0, 90));
    console.log('   ' + why(b));
    console.log('   ' + b.r.j.url);
  });
  const top = board.slice(0, TOP_N);
  console.log('');
  // HONEST FRAMING (corrected Aug 9). The top 15 is not 11x the pool because the
  // ranking is clever. It is 11x because psm_estimate takes two values and the
  // top of the board is drawn entirely from the 10-minute bucket. Decomposed:
  //   10-min bucket vs whole pool ...... 2.2x   (the bucket, not the ranking)
  //   top 15 vs the 10-min bucket ...... 5.1x   (what the ordering adds)
  // And WITHIN that bucket, ordering by score and ordering by quote alone agree
  // 15 of 15 in the top slots, Spearman 0.977 — the judge, buyer and freshness
  // multipliers are very nearly decorative. Report it as bucket-versus-pool.
  const buckets = {};
  board.forEach(b => { (buckets[b.psm] = buckets[b.psm] || []).push(b); });
  console.log('');
  console.log('BY PSM BUCKET (the bucket does most of the work, not the ranking):');
  Object.keys(buckets).sort((a, b) => a - b).forEach(k => {
    const a = buckets[k];
    console.log('  psm ' + k + 'min  n=' + a.length + '  mean $/min ' + Math.round(a.reduce((x, y) => x + y.perMin, 0) / a.length));
  });
  const topBucket = buckets[top[0].psm] || [];
  console.log('  top ' + TOP_N + ' vs its own bucket: ' +
    (top.reduce((a, b) => a + b.perMin, 0) / top.length / (topBucket.reduce((a, b) => a + b.perMin, 0) / topBucket.length)).toFixed(1) + 'x');
  console.log('');
  console.log('top ' + TOP_N + ': mean quote $' + Math.round(top.reduce((a, b) => a + b.quote, 0) / top.length) +
              ', mean psm ' + Math.round(top.reduce((a, b) => a + b.psm, 0) / top.length) + 'min, mean $' +
              Math.round(top.reduce((a, b) => a + b.perMin, 0) / top.length) + '/min');
  console.log('board:      mean quote $' + Math.round(board.reduce((a, b) => a + b.quote, 0) / board.length) +
              ', mean psm ' + Math.round(board.reduce((a, b) => a + b.psm, 0) / board.length) + 'min, mean $' +
              Math.round(board.reduce((a, b) => a + b.perMin, 0) / board.length) + '/min');

  if (!WRITE_RANKS) { console.log('\nDRY RUN. Set WRITE_RANKS = true to stamp priority_rank onto proposals.'); return board.slice(0, TOP_N); }

  // Stamp the rank so the board can be SCORED later: did the jobs it ranked
  // first actually win? Without this the ranking can never be wrong out loud.
  let n = 0;
  for (let i = 0; i < top.length; i++) {
    const ref = top[i].r.j.ref; if (!ref) continue;
    const r = await fetch(base + T.proposals + '/rows', {
      method: 'PATCH', headers: Object.assign({ 'content-type': 'application/json' }, H), credentials: 'include',
      body: JSON.stringify({ filter: { type: 'and', filters: [{ columnName: 'ref', condition: 'eq', value: ref }] },
                             data: { priority_rank: i + 1, quoted_price: top[i].quote } })
    });
    if (r.ok) n++;
  }
  console.log('\nstamped priority_rank on ' + n + ' proposals rows.');
  return board.slice(0, TOP_N);
})();
