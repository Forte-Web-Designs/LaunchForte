// Cockpit V2.29 patch (Seth Nov 23 2026, card UBPwAL23, Pricing Standard v2.7 section 12).
// Applied by script, never by hand: n8n workflow "Ops: Cockpit V2.29 patcher" reads the live Cockpit (Hl5zah3PZcHaEkuo)
// through the n8n API, runs patchCockpit(), and either creates a TEST COPY (mode "test", side effect nodes disabled)
// or updates the live Cockpit (mode "promote"). Every replacement asserts its exact count, so a drifted Cockpit fails.
// What it changes:
//   1. Rates: every hard coded card rate in Price Gate Engine and Cockpit Gate V2 is read from the one rate table
//      (lf_unit_rates, node "Read Rate Table"), the same table lf_price uses. A missing kind fails closed.
//   2. Migration items: the scope reader counts moved items (flows, forms, calendars, page designs, pages) from the
//      buyer's own inventory; the engine prices them per item; unnamed items are held as NEEDS_DETAIL.
//   3. The calculator request carries the migration kinds; the Price Gate already refuses any total that differs.
function patchCockpit(w, mode) {
  const av = w.activeVersion || {};
  const nodes = JSON.parse(JSON.stringify(av.nodes || w.nodes));
  const connections = JSON.parse(JSON.stringify(av.connections || w.connections));
  const N = (name) => { const n = nodes.find((x) => x.name === name); if (!n) throw new Error('V2.29 patch: no node ' + name); return n; };
  const rep = (name, find, repl, count) => {
    const n = N(name); const c = String(n.parameters.jsCode || '');
    const k = c.split(find).length - 1;
    if (k !== count) throw new Error('V2.29 patch: ' + name + ' expected ' + count + ' of [' + find.slice(0, 70) + '] found ' + k);
    n.parameters.jsCode = c.split(find).join(repl);
  };
  if (String(N('Price Gate Engine').parameters.jsCode).indexOf('V2.29') >= 0) throw new Error('V2.29 patch: already applied');

  const KINDS = "['config','connection','judged','surface','risk','extra_system','audit','migration_flow','migration_form','migration_calendar','migration_page_layout','migration_page']";
  const LOADER = "/* V2.29 (Seth Nov 23 2026, card UBPwAL23): every rate comes from the one Launch Forte rate table (lf_unit_rates, node Read Rate Table), the table lf_price uses. Nothing is typed here; a missing kind fails closed. */\n" +
    "const __LF_RATES = (function () { const m = {}; try { $('Read Rate Table').all().forEach(function (i) { const r = i.json || {}; if (r.piece_kind && Number(r.unit_rate_cents) > 0) m[r.piece_kind] = Number(r.unit_rate_cents) / 100; }); } catch (e) {} " + KINDS + ".forEach(function (k) { if (!(m[k] > 0)) throw new Error('RATE TABLE REFUSED (fail closed): lf_unit_rates has no ' + k); }); m.systems = m.extra_system; return m; })();\n";
  const RATES6 = "{ connection: __LF_RATES.connection, config: __LF_RATES.config, judged: __LF_RATES.judged, surface: __LF_RATES.surface, risk: __LF_RATES.risk, systems: __LF_RATES.systems";
  const RATES_ALL = RATES6 + ", audit: __LF_RATES.audit, migration_flow: __LF_RATES.migration_flow, migration_form: __LF_RATES.migration_form, migration_calendar: __LF_RATES.migration_calendar, migration_page_layout: __LF_RATES.migration_page_layout, migration_page: __LF_RATES.migration_page }";

  // 1. Scope reader: migration kinds and counting.
  const MIGLINE = "'  MOVING EXISTING WORK (V2.29, Pricing Standard v2.7 section 12, Seth Nov 23 2026): when the buyer is moving things that already exist into a new platform with the same copy, design and logic, each moved item kind is its own deliverable with piece_type \\\"migration_flow\\\" (email or text automations, one kind whether they branch or not), \\\"migration_form\\\", \\\"migration_calendar\\\", \\\"migration_page_layout\\\" (one per distinct page design rebuilt: one design per page kind the inventory names, such as opt in, thank you or confirmation, replay, sales and application; a waitlist or newsletter signup page is an opt in) or \\\"migration_page\\\" (every other moved page, on a design already counted). units is the count from the buyer inventory, using the latest and most specific inventory in the text (a scope document beats an earlier message), excluding items the buyer says are retired or staying put. Moved items with no name or detail are a separate deliverable of the same piece_type with status \\\"NEEDS_DETAIL\\\". Imports, lists, segments, tags, custom fields, redirects, the sending domain and warmup, text registration, templates and brand styling, testing, the workflow map and the walkthrough are never deliverables. Anything rebuilt with new logic or changed on the way over is new work at the normal kinds, never a migration item. A native rebuild that replaces automations from another tool (such as booking, cancel and no show tracking that ran in Zapier) is one config. A live feed between two systems that stay in use (such as Shopify purchases into GoHighLevel) is one connection. Moving existing pages as is is migration, never website work. In systems, list only systems the finished build uses; systems that are only exported from and then switched off are not listed.',\n";
  rep('Scope Prompt', "'  surface only when the buyer explicitly asks", MIGLINE + "'  surface only when the buyer explicitly asks", 1);
  rep('Scope Prompt', "or \\\"ALREADY_DONE\\\" (the buyer reports it complete).',", "or \\\"ALREADY_DONE\\\" (the buyer reports it complete); or \\\"NEEDS_DETAIL\\\" (V2.29: a moved item the inventory names without detail).',", 1);
  rep('Scope Merge', "const KT = ['config', 'connection', 'judged', 'surface', 'risk'];", "const KT = ['config', 'connection', 'judged', 'surface', 'risk', 'migration_flow', 'migration_form', 'migration_calendar', 'migration_page_layout', 'migration_page']; /* V2.29 */", 1);
  rep('Scope Merge', "const ST = ['BUILD', 'INCLUDED', 'OPTIONAL_SEPARATE', 'ALREADY_DONE'];", "const ST = ['BUILD', 'INCLUDED', 'OPTIONAL_SEPARATE', 'ALREADY_DONE', 'NEEDS_DETAIL']; /* V2.29 */", 1);
  rep('Scope Merge', "units: Math.max(1, Math.min(50, parseInt(d.units, 10) || 1))", "units: Math.max(1, Math.min(/^migration_/.test(String(d.piece_type || '')) ? 500 : 50, parseInt(d.units, 10) || 1)) /* V2.29: moved items can number in the hundreds */", 1);

  // 2. Engine: rates from the table, migration pieces.
  const ENG = 'Price Gate Engine';
  N(ENG).parameters.jsCode = LOADER + N(ENG).parameters.jsCode;
  rep(ENG, "CARD = { connection: 400, config: 250, judged: 700, surface: 600, risk: 800, systems: 300 }", "CARD = " + RATES6 + " }", 1);
  rep(ENG, "CARD = { connection: 400, config: 250, judged: 700, surface: 600, risk: 800, systems: 300, audit: 650 }", "CARD = " + RATES_ALL, 2);
  rep(ENG, "unit_price: 650, quantity: 1, subtotal: 650", "unit_price: __LF_RATES.audit, quantity: 1, subtotal: __LF_RATES.audit", 2);
  rep(ENG, "unit_price: 300, quantity: 1, subtotal: 300", "unit_price: __LF_RATES.systems, quantity: 1, subtotal: __LF_RATES.systems", 1);
  rep(ENG, "unit_price: 400, quantity: 1, subtotal: 400", "unit_price: __LF_RATES.connection, quantity: 1, subtotal: __LF_RATES.connection", 1);
  rep(ENG, "unit_price: 250, quantity: 1, subtotal: 250", "unit_price: __LF_RATES.config, quantity: 1, subtotal: __LF_RATES.config", 1);
  const MIGBRANCH = "\n/* V2.29 MIGRATION (Pricing Standard v2.7 section 12): moving existing work as is, priced per item from the rate table; the Price Gate checks the total against the calculator. */ if (/^migration_(flow|form|calendar|page_layout|page)$/.test(String(d.piece_type || ''))) { var __mu = Math.max(1, parseInt(d.units, 10) || 1); if (d.status === 'NEEDS_DETAIL') { var enm = { deliverable: d.title, status: 'SEPARATE', piece: null, piece_type: d.piece_type, amount: 0, why: 'named without detail; confirmed with the buyer before it is priced (v2.7 section 12.2)' }; res.map.push(enm); res.separate.push(enm); return; } var __mr = __LF_RATES[d.piece_type]; var __ms = __mr * __mu; var __ml = __mu + ' ' + String(d.title || '').replace(/^\\s*\\d+\\s+/, ''); pieces.push({ piece_type: d.piece_type, piece_heading: 'Moved over as is', piece_description: __ml, rate_type: 'card', unit_price: __mr, quantity: __mu, subtotal: __ms, why: 'v2.7 section 12: ' + __mu + ' moved as is' }); res.map.push({ deliverable: d.title, status: 'PRICED', piece: __ml, piece_type: d.piece_type, amount: __ms, why: 'moved as is, ' + __mu + ' items' }); return; }";
  rep(ENG, "res.map.push(es); res.separate.push(es); return; }", "res.map.push(es); res.separate.push(es); return; }" + MIGBRANCH, 1);
  rep(ENG, "out.push('    ' + g[0].piece_description + ': ' + money(g[0].unit_price)); }", "out.push('    ' + g[0].piece_description + ': ' + money(Number(g[0].quantity) > 1 ? g[0].subtotal : g[0].unit_price)); } /* V2.29: a moved block shows its count and its total, never the unit rate */", 1);

  // 3. Calculator request and the card gate.
  rep('Calculator Pieces', "risk: 'risk', systems: 'extra_system', audit: 'audit', start: 'audit' };", "risk: 'risk', systems: 'extra_system', audit: 'audit', start: 'audit', migration_flow: 'migration_flow', migration_form: 'migration_form', migration_calendar: 'migration_calendar', migration_page_layout: 'migration_page_layout', migration_page: 'migration_page' }; /* V2.29 */", 1);
  const GATE = 'Cockpit Gate V2';
  N(GATE).parameters.jsCode = LOADER + N(GATE).parameters.jsCode;
  rep(GATE, "const CARD = { connection: 400, config: 250, judged: 700, surface: 600, risk: 800, systems: 300, audit: 650 };", "const CARD = " + RATES_ALL + ";", 1);
  rep(GATE, "const CARD2 = { connection: 400, config: 250, judged: 700, surface: 600, risk: 800, systems: 300, audit: 650 };", "const CARD2 = " + RATES_ALL + ";", 1);

  // 4. The rate table read, between Screening Pass and the engine (the engine reads its item from Screening Pass).
  const sp = N('Screening Pass'); const eng = N(ENG);
  nodes.push({ id: 'v229-read-rate-table', name: 'Read Rate Table', type: 'n8n-nodes-base.httpRequest', typeVersion: 4.2, position: [eng.position[0] - 220, eng.position[1] + 200], executeOnce: true,
    parameters: { method: 'GET', url: 'https://xndccqxgqobezzfuadni.supabase.co/rest/v1/lf_unit_rates?select=piece_kind,unit_rate_cents', authentication: 'predefinedCredentialType', nodeCredentialType: 'supabaseApi', options: {} },
    credentials: { supabaseApi: { id: 'vVbUtXM5hiFPSHPq', name: 'Supabase Dashboard (LF idempotency)' } }, retryOnFail: true, maxTries: 3, waitBetweenTries: 3000 });
  nodes.push({ id: 'v229-keep-item', name: 'Keep Screening Item', type: 'n8n-nodes-base.code', typeVersion: 2, position: [eng.position[0] - 110, eng.position[1] + 200],
    parameters: { mode: 'runOnceForAllItems', jsCode: "// V2.29: the rate table read replaced the item; the engine reads the Screening Pass item as before.\nreturn $('Screening Pass').all();" } });
  let rewired = 0;
  (connections['Screening Pass'].main || []).forEach((out) => (out || []).forEach((c) => { if (c.node === ENG) { c.node = 'Read Rate Table'; rewired++; } }));
  if (rewired !== 1) throw new Error('V2.29 patch: Screening Pass to engine edge count ' + rewired);
  connections['Read Rate Table'] = { main: [[{ node: 'Keep Screening Item', type: 'main', index: 0 }]] };
  connections['Keep Screening Item'] = { main: [[{ node: ENG, type: 'main', index: 0 }]] };

  // Syntax check every patched code node.
  const AsyncFn = Object.getPrototypeOf(async function () {}).constructor;
  ['Scope Prompt', 'Scope Merge', ENG, 'Calculator Pieces', GATE, 'Keep Screening Item'].forEach((n) => { try { new AsyncFn('$', '$input', N(n).parameters.jsCode); } catch (e) { throw new Error('V2.29 patch: syntax error in ' + n + ': ' + e.message); } });

  let name = w.name;
  if (mode === 'test') {
    name = 'TEST COPY Cockpit V2.29 (card UBPwAL23, side effect nodes disabled)';
    const SIDE = ['Email Backup', 'Archive Folder', 'Archive Pack', 'Archive Sketch', 'Mark Job', 'Write Run', 'Ledger Save', 'Save Page Truth', 'Post Proposal', 'Name The Call', 'Price The Call', 'Fire Forge'];
    nodes.forEach((n) => { if (SIDE.indexOf(n.name) >= 0) n.disabled = true; if (n.type === 'n8n-nodes-base.webhook') n.parameters.path = 'cockpit-test-v229-' + String(n.parameters.path || '').slice(-8); if (n.webhookId) n.webhookId = undefined; });
  }
  return { name, nodes, connections, settings: { executionOrder: (w.settings || {}).executionOrder || 'v1' } };
}
if (typeof module !== 'undefined') module.exports = { patchCockpit };
