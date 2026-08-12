/* Fortress system map generator.
 *
 * Paste into the browser console on any launchforte.app.n8n.cloud tab, then run
 *   copy(__MD)
 * and paste the result over docs/fortress/SYSTEM-MAP.md. Commit it.
 *
 * WHY THIS EXISTS. Prose written from memory cannot describe machinery nobody
 * remembers building. On Aug 12 a complete screenshot-attachment pipeline --
 * Shot List, Fetch Shot, Shot To JPEG, Make Proof PDF, Has Proof? -- sat unused
 * through a full day of testing, because it lived only inside an 82-node live
 * workflow and no document mentioned it. Every card that day was told not to
 * push its branch, which silently disabled that pipeline, the reviewing agent's
 * ability to verify a commit, AND the run recipe's proof path. One wrong
 * instruction, three broken systems, because the map was in nobody's head.
 *
 * This generator reads the DEPLOYED workflows. It is true by construction. If
 * SYSTEM-MAP.md disagrees with the tenant, regenerate rather than argue.
 */
(async () => {
  const H = { 'browser-id': localStorage.getItem('n8n-browserId') };

  /* The spine. Add an id here when a workflow becomes load-bearing.
     Do NOT switch this to "every active workflow" -- there are 380+, most of
     them client demos, and the map stops being readable. */
  const CORE = [
    'nuNkZu0VqDVwtS9d',  // Ops: Build Queue API
    'XOjXyxgywZJK3G5x',  // Ops: Dashboard API
    'Hl5zah3PZcHaEkuo',  // Proposal: Cockpit
    '7MY8Bqj42haaFbPF',  // Upwork: Job Engine
    'mb0BkCseIfoMUqT2',  // Error Watch
  ];

  const out = [];
  for (const id of CORE) {
    const w = (await fetch('/rest/workflows/' + id, { headers: H }).then(r => r.json())).data;
    if (!w || !w.nodes) { out.push({ id, err: 'unreadable' }); continue; }
    const fwd = w.connections || {};
    const chainOf = (start) => {
      const seen = new Set(); const order = []; let fr = [start]; let d = 0;
      while (fr.length && d < 50) {
        const nx = [];
        for (const n of fr) {
          if (seen.has(n)) continue;
          seen.add(n); order.push(n);
          ((fwd[n] && fwd[n].main) || []).forEach(a => (a || []).forEach(t => nx.push(t.node)));
        }
        fr = nx; d++;
      }
      return order;
    };
    const tbl = (n) => { const v = n.parameters && n.parameters.dataTableId; return v && (v.cachedResultName || v.value); };
    const triggers = w.nodes.filter(n => /webhook|Trigger/i.test(n.type));
    const entry = triggers.map(h => {
      const chain = chainOf(h.name);
      const nodes = chain.map(nm => w.nodes.find(x => x.name === nm)).filter(Boolean);
      return {
        trigger: h.name,
        path: (h.parameters && h.parameters.path) || null,
        method: (h.parameters && h.parameters.httpMethod) || null,
        tables: [...new Set(nodes.map(tbl).filter(Boolean))],
        conns: [...new Set(nodes.flatMap(n => n.credentials ? Object.values(n.credentials).map(c => c.name) : []))],
        chain: chain,
      };
    }).filter(e => e.path || e.chain.length > 3);
    out.push({ id: w.id, name: w.name, active: w.active, nodeCount: w.nodes.length, entry });
  }

  const L = [];
  L.push('# Fortress system map — GENERATED, do not hand-edit');
  L.push('');
  L.push('Regenerate with `docs/fortress/generators/system-map.js` in the browser console on a');
  L.push('`launchforte.app.n8n.cloud` tab, then `copy(__MD)` and paste over this file.');
  L.push('It reads the deployed workflows, so it is true by construction. If this file');
  L.push('disagrees with the tenant, the file is stale — regenerate it rather than argue.');
  L.push('');
  for (const w of out) {
    L.push('---'); L.push('');
    L.push('## ' + w.name); L.push('');
    L.push('`' + w.id + '` · ' + w.nodeCount + ' nodes · ' + (w.active ? 'ACTIVE' : 'inactive'));
    L.push('');
    for (const e of (w.entry || [])) {
      L.push('### ' + (e.path ? ('`' + (e.method || 'GET') + ' /webhook/' + e.path + '`') : ('trigger: ' + e.trigger)));
      L.push('');
      if (e.tables.length) L.push('- **data tables:** ' + e.tables.join(', '));
      if (e.conns.length) L.push('- **saved connections:** ' + e.conns.join(', '));
      L.push('- **chain:** ' + e.chain.join(' → '));
      L.push('');
    }
  }
  window.__MAP = out;
  window.__MD = L.join('\n');
  console.log('system map ready: ' + window.__MD.length + ' chars. Run  copy(__MD)  and paste over docs/fortress/SYSTEM-MAP.md');
  return window.__MD.length;
})();
