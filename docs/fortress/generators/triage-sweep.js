// Triage sweep — paste into the browser console on launchforte.app.n8n.cloud.
//
// Runs the DEPLOYED "Route the job" node over the whole upwork_jobs corpus and
// produces the two things build notes 1 and 5 ask for:
//
//   1. the listing_candidate ideas rows, aggregated by shape the same way the
//      judge aggregates product_gap — one row per shape that clears a threshold,
//      never one row per posting;
//   2. the weekly report's opportunities line: the listing_candidate count and
//      the room_below_floor count, so the shelf menu and the ignored-auction
//      volume are both visible without a ping.
//
// It reads the node source out of the live workflow rather than carrying its own
// copy, because a second implementation of the routing arithmetic is exactly the
// bug that was fixed in pricing. If the deployed node changes, this changes with it.
//
// No posting text ever leaves n8n: everything runs in the tab, and only counts
// come back.
//
// DRY RUN BY DEFAULT. Set WRITE = true to file the ideas rows.

const WRITE = false;
const THRESHOLD = 8; // a shape needs this many listing candidates before it earns a shelf SKU

(async () => {
  const PROJECT = 'G1EzIclYs4hXjhBw';
  const T = {
    upwork_jobs: 'iSZB081VXkJjbZs5', shapes: 'BLwjqEoeUemakJll', builds: 'GDNk0omQAG3AujNK',
    tools_kb: 'cstpHScKXAAmdv2y', blockers: '2wuFLuu5V0mvHtHp', ideas: 'LJ73ioRjnSL0uD3G'
  };
  const bid = localStorage.getItem('n8n-browserId');
  const H = { 'browser-id': bid };
  const base = '/rest/projects/' + PROJECT + '/data-tables/';

  const page = async (id, skip) => {
    const r = await fetch(base + id + '/rows?take=250&skip=' + skip, { headers: H, credentials: 'include' });
    const j = await r.json(); return j.data && j.data.data ? j.data : j;
  };
  const pull = async (id) => {
    const first = await page(id, 0); let rows = first.data.slice();
    while (rows.length < first.count) { const nx = await page(id, rows.length); if (!nx.data.length) break; rows = rows.concat(nx.data); }
    return rows;
  };

  // --- the node, from the workflow. One implementation, not two. -----------
  const wr = await fetch('/rest/workflows/Hl5zah3PZcHaEkuo', { headers: H, credentials: 'include' });
  const wf = (await wr.json()).data;
  const node = wf.nodes.find(n => n.name === 'Route the job');
  if (!node) throw new Error('Route the job is not deployed — nothing to sweep with.');
  const fn = new Function('$json', '$', '"use strict";' + node.parameters.jsCode);

  const corpus = await pull(T.upwork_jobs);
  const REG = {
    'Read Shapes (Cockpit)': await pull(T.shapes),
    'Read Builds': await pull(T.builds),
    'Read Tools KB': await pull(T.tools_kb),
    'Read Blockers': await pull(T.blockers)
  };
  const $r = (name) => {
    if (!(name in REG)) throw new Error('no node');
    const rows = REG[name];
    return { all: () => rows.map(r => ({ json: r })), first: () => ({ json: rows[0] }) };
  };

  const out = []; let errors = 0;
  for (const j of corpus) { try { out.push(fn(j, $r)[0].json); } catch (e) { errors++; } }

  // --- hard invariants. A sweep that finds these broken must not write. ----
  const bad = [];
  if (errors) bad.push(errors + ' postings threw');
  if (!out.every(o => o.triage_rules_ok === true)) bad.push('triage_rules_ok is false somewhere');
  if (out.some(o => o.room_below_floor && o.triage_action !== 'no_bid')) bad.push('a below-floor job did not end in no_bid');
  if (out.some(o => o.triage_action === 'lane_bid' && !o.lane_enabled)) bad.push('the lane bid while it ships OFF');
  if (out.some(o => o.certified && (o.triage_needs_call || o.triage_needs_client_account))) bad.push('a certified job needs a call or their account');
  if (out.some(o => !o.certified && !o.certified_failed_check)) bad.push('certified false without a named check');

  // --- the two counts the weekly report needs -----------------------------
  const listing = out.filter(o => o.listing_candidate);
  const belowFloor = out.filter(o => o.room_below_floor);

  const byShape = {};
  listing.forEach((o, i) => {
    const tools = (o.triage_tools || []);
    const key = tools.length ? tools[0] : (o.triage_shape || 'unclassified');
    (byShape[key] = byShape[key] || []).push(o);
  });
  const earned = Object.keys(byShape).filter(k => byShape[k].length >= THRESHOLD).sort((a, b) => byShape[b].length - byShape[a].length);

  const t = (k) => { const m = {}; out.forEach(o => { m[String(o[k])] = (m[String(o[k])] || 0) + 1; }); return m; };
  console.log('TRIAGE SWEEP');
  console.log('  postings      ', out.length, ' errors', errors);
  console.log('  invariants    ', bad.length ? 'BROKEN: ' + bad.join('; ') : 'all hold');
  console.log('  route         ', t('route'));
  console.log('  action        ', t('triage_action'));
  console.log('');
  console.log('OPPORTUNITIES LINE (paste into the weekly report):');
  console.log('  listing_candidate ' + listing.length + '   room_below_floor ' + belowFloor.length);
  console.log('  shelf menu (>= ' + THRESHOLD + '): ' + (earned.length ? earned.map(k => k + ' x' + byShape[k].length).join(', ') : 'nothing clears the threshold'));
  console.log('  certified today: ' + out.filter(o => o.certified).length);

  if (!WRITE) { console.log('\nDRY RUN. Set WRITE = true to file the ideas rows.'); return { listing: listing.length, below_floor: belowFloor.length, earned: earned }; }
  if (bad.length) { console.log('\nREFUSING TO WRITE: ' + bad.join('; ')); return; }

  // --- file the ideas rows, same discipline as product_gap ----------------
  const existing = await pull(T.ideas);
  const have = {};
  existing.forEach(r => { if (String(r.tag) === 'listing_candidate') have[String(r.shape)] = true; });

  let written = 0;
  for (const k of earned) {
    const shapeKey = 'upwork:' + k + ':listing_candidate';
    if (have[shapeKey]) { console.log('  skip (already filed) ' + shapeKey); continue; }
    const n = byShape[k].length;
    const row = {
      ts: new Date().toISOString(),
      tag: 'listing_candidate',
      shape: shapeKey,
      status: 'proposed',
      source: 'upwork_triage',
      build_size: n >= 40 ? 'M' : 'S',
      prompt: 'Shape ' + k + ' cleared the listing threshold: the delivery needs their account, so it cannot be ' +
              'bid hands-free, but the shape is kit-worthy. Serve this tier on a Project Catalog shelf instead of in an auction.',
      evidence: n + ' postings in the corpus route to the listing lane on ' + k +
                ', every one blocked from the volume lane by client-account access alone.',
      money: 0, list: 0, unsolved: 0, demoable: 0, total: 0
    };
    const r = await fetch(base + T.ideas + '/insert', {
      method: 'POST', headers: Object.assign({ 'content-type': 'application/json' }, H),
      credentials: 'include', body: JSON.stringify({ data: [row] })
    });
    console.log('  ' + (r.ok ? 'filed  ' : 'FAILED ' + r.status + ' ') + shapeKey + '  (' + n + ')');
    if (r.ok) written++;
  }
  console.log('\nwrote ' + written + ' listing_candidate rows.');
  return { listing: listing.length, below_floor: belowFloor.length, written: written };
})();
