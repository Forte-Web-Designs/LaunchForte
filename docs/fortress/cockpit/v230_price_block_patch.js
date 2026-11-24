// Cockpit V2.30 patch (Seth Nov 23 2026, card dl1plsWm): the cover letter price block is built by code from the
// priced pieces as clean outcome blocks, one price each, plain counts underneath, then the Total and a fixed
// provisional line. The model writes only the prose around it. The itemized table in the review email is parsed
// from that same block, so the letter, the table and the ledger cannot disagree.
// Applied by script, never by hand: n8n workflow "Ops: Cockpit patcher" reads the live Cockpit (Hl5zah3PZcHaEkuo),
// runs patchCockpit(), and either creates a TEST COPY (mode "test", side effect nodes disabled) or, after the test
// copy passes, saves a backup and updates the live Cockpit (mode "promote"). Every replacement asserts its count.
// What it changes:
//   1. Final Render V2: the price block renderer (outcome blocks, no piece kind headings, no unit rates, provisional
//      line after the Total); the blocks are recorded on out.price_blocks; hyphenated compounds in the letter and the
//      Loom script are written as separate words; "go live" in the fixed payment line.
//   2. Cockpit Gate V2: the arithmetic check reads the block prices; every priced piece sits in exactly one block and
//      each block price equals its pieces; no repeated headings, piece kind labels, item kinds, unit rates or
//      hyphenated compounds; the provisional line is present; the calendar count check counts units, not lines.
//   3. Price Gate Engine: a moved item's coverage entry carries its unit count.
//   4. Read Rate Table also reads source_ref, and Compose Review Email labels the itemized table with the current
//      Pricing Standard version read from it and parses the new blocks.

/* ---------- injected code, written as real functions so nothing needs escaping ---------- */
function __renderPricingBlock(po) {
  var PROV = "Based on what I know so far, here's where I'd land. If anything changes once we talk it through, I'll update it before anything starts.";
  var money = function (n) { return '$' + Number(n || 0).toLocaleString('en-US'); };
  var dh = function (s) { return String(s || '').split(/(\s+)/).map(function (w) { return /:\/\/|@/.test(w) ? w : w.replace(/([A-Za-z0-9])-(?=[A-Za-z])/g, '$1 '); }).join(''); };
  var cap = function (s) { s = dh(String(s || '').trim().replace(/^the\s+/i, '')); return s.charAt(0).toUpperCase() + s.slice(1); };
  var systems = []; try { systems = ((($('Scope Merge').first().json || {}).scope_norm) || {}).systems || []; } catch (e) { systems = []; }
  var plat = String(systems[0] || 'your new platform').replace(/\(.*?\)/g, ' ').replace(/\bwhite label\b/ig, ' ').replace(/\baccount\b/ig, ' ').replace(/\s+/g, ' ').trim() || 'your new platform';
  var P = po.pieces || [];
  var pl = function (n, one, many) { return n + ' ' + (n === 1 ? one : many); };
  var q = function (p) { return Math.max(1, parseInt(p.quantity, 10) || 1); };
  var used = {};
  var take = function (pred) { var ix = []; P.forEach(function (p, i) { if (!used[i] && pred(p, i)) { used[i] = 1; ix.push(i); } }); return ix; };
  var blocks = [];
  if (P.some(function (p) { return /^migration_/.test(String(p.piece_type || '')); })) {
    var LINE = {
      migration_flow: function (n) { return pl(n, 'email and text automation', 'email and text automations') + ' rebuilt with your copy as is'; },
      migration_form: function (n) { return pl(n, 'signup form', 'signup forms') + ' rebuilt'; },
      migration_calendar: function (n) { return pl(n, 'calendar', 'calendars') + ' with your questions, buffers and reminders'; },
      migration_page_layout: function (n) { return pl(n, 'page design', 'page designs') + ' rebuilt to match your current pages'; },
      migration_page: function (n) { return n + ' more ' + (n === 1 ? 'page' : 'pages') + ' on those designs with your copy'; }
    };
    var lines = function (ix) { return ix.map(function (i) { var p = P[i]; return LINE[p.piece_type] ? LINE[p.piece_type](q(p)) : cap(p.piece_description); }); };
    var msg = take(function (p) { return p.piece_type === 'migration_flow' || p.piece_type === 'migration_form'; });
    if (msg.length) blocks.push({ title: msg.some(function (i) { return P[i].piece_type === 'migration_flow'; }) ? 'Your emails and texts running in ' + plat : 'Your forms rebuilt in ' + plat, pieces: msg, lines: lines(msg) });
    var cal = take(function (p) { return p.piece_type === 'migration_calendar'; });
    if (cal.length) {
      var trk = take(function (p) { return p.piece_type === 'config' && /\b(book\w*|calendars?|no[ -]?shows?|cancel\w*|appointments?)\b/i.test(String(p.piece_description || '')); });
      blocks.push({ title: trk.length ? 'Your calendars with booking tracking built in' : 'Your calendars rebuilt in ' + plat, pieces: cal.concat(trk),
        lines: lines(cal).concat(trk.map(function (i) { return /no[ -]?show|cancel/i.test(String(P[i].piece_description || '')) ? 'Booking, cancel and no show tracking built in' : cap(P[i].piece_description); })) });
    }
    var pgs = take(function (p) { return p.piece_type === 'migration_page_layout' || p.piece_type === 'migration_page'; });
    if (pgs.length) blocks.push({ title: 'Your pages rebuilt with every old link redirected', pieces: pgs, lines: lines(pgs) });
    P.forEach(function (p, i) {
      if (used[i] || p.piece_type !== 'connection') return; used[i] = 1;
      var d = String(p.piece_description || '');
      var s = systems.slice(1).map(function (x) { return String(x).replace(/\(.*?\)/g, ' ').trim(); }).find(function (x) { var k = x.toLowerCase().split(/\s+/)[0]; return k && d.toLowerCase().indexOf(k) >= 0; });
      if (s && /\b(purchases?|orders?|checkouts?)\b/i.test(d)) blocks.push({ title: s + ' purchases start your workflows', pieces: [i], lines: [s + ' purchases into ' + plat] });
      else blocks.push({ title: cap(d), pieces: [i], lines: q(p) > 1 ? [pl(q(p), 'connection', 'connections')] : [] });
    });
  }
  P.forEach(function (p, i) { if (used[i]) return; used[i] = 1; blocks.push({ title: cap(p.piece_description), pieces: [i], lines: q(p) > 1 ? [q(p) + ' of these'] : [] }); });
  blocks.forEach(function (b) { b.amount = b.pieces.reduce(function (s, i) { return s + Number(P[i].subtotal || 0); }, 0); });
  var out = ['For transparency on pricing, I price builds fixed, so you know the number before I start.', ''];
  blocks.forEach(function (b) { out.push(b.title + ': ' + money(b.amount)); b.lines.forEach(function (l) { out.push('    ' + l); }); out.push(''); });
  out.push('Total: ' + money(po.total));
  out.push('');
  out.push(PROV);
  __LF_BLOCKS = blocks;
  return out.join('\n');
}

function lfPriceRows(letter) {
  /* V2.30 (card dl1plsWm): rows are the outcome blocks of the letter's own price block, so the table can never disagree with what the buyer reads */
  const L = String(letter || ''); const rows = []; let total = null, provisional = false;
  const tm = L.match(/^\s*Total\s*:\s*(\$[\d,]+)(.*)$/im);
  if (tm) { total = tm[1]; provisional = /provisional/i.test(tm[2]) || /Based on what I know so far, here's where I'd land/i.test(L); }
  const bs = L.search(/(?:This is just what I can tell from your job posting|For transparency on pricing)/i), be = L.search(/^\s*Total\s*:/im);
  if (bs >= 0 && be > bs) {
    let cur = null;
    L.slice(bs, be).split('\n').forEach(function (raw) {
      const m = raw.match(/^(\S.*?):\s*(\$[\d,]+)\s*$/);
      if (m) { cur = { item: m[1], cat: '', amt: m[2] }; rows.push(cur); return; }
      const l = raw.trim();
      if (cur && l && /^\s{2,}/.test(raw)) cur.cat = cur.cat ? cur.cat + '; ' + l : l;
    });
  }
  return { rows, total, provisional };
}
function lfPsVersion() {
  let best = null;
  try { $('Read Rate Table').all().forEach(function (i) { const m = String((i.json || {}).source_ref || '').match(/Pricing Standard v(\d+)\.(\d+)/); if (m) { const v = [+m[1], +m[2]]; if (!best || v[0] > best[0] || (v[0] === best[0] && v[1] > best[1])) best = v; } }); } catch (e) {}
  return best ? 'Pricing Standard v' + best[0] + '.' + best[1] : 'Pricing Standard (version not read)';
}

function __v230GateBlock() {
  /* V2.30 (card dl1plsWm): the price block is outcome blocks rendered by code; every line "Title: $amount" is a block price */
  let blockSum = 0; const shownBlocks = [];
  const bStart = letter.search(/(?:This is just what I can tell from your job posting|For transparency on pricing, I price builds fixed)/i);
  const bEnd = letter.search(/^\s*Total\s*:/im);
  const block = bStart >= 0 && bEnd > bStart ? letter.slice(bStart, bEnd) : '';
  block.split('\n').forEach(l => {
    if (/\bat \$[\d,]+ each\b|\beach\s*:|\bper (?:flow|page|form|calendar|item)\b/i.test(l)) fails.push('UNIT RATE V2.30: the price block shows a unit rate: ' + l.trim());
    const m = l.match(/^(\S[^\n]*?): \$([\d,]+)\s*$/);
    if (m) { const s = +m[2].replace(/,/g, ''); blockSum += s; shownBlocks.push({ title: m[1], amount: s }); }
    else if (/\$\s?\d/.test(l)) fails.push('PRICE BLOCK V2.30: a money line that is not a block price: ' + l.trim());
  });
  const __titles = shownBlocks.map(b => b.title.toLowerCase());
  if (new Set(__titles).size !== __titles.length) fails.push('PRICE BLOCK V2.30: a block heading repeats');
  if (po && totals.length === 1) {
    if (totals[0] !== po.total) fails.push('PRICE MISMATCH: displayed ' + money(totals[0]) + ', structured ' + money(po.total));
    if (blockSum !== totals[0]) fails.push('PRICE ARITHMETIC: the lines add to ' + money(blockSum) + ', the total says ' + money(totals[0]));
    const sumPieces = (po.pieces || []).reduce((s, p) => s + Number(p.subtotal || 0), 0);
    if (sumPieces !== po.total) fails.push('PRICE OBJECT: pieces add to ' + money(sumPieces) + ', object total ' + money(po.total));
    const CARD = { connection: __LF_RATES.connection, config: __LF_RATES.config, judged: __LF_RATES.judged, surface: __LF_RATES.surface, risk: __LF_RATES.risk, systems: __LF_RATES.systems, audit: __LF_RATES.audit, migration_flow: __LF_RATES.migration_flow, migration_form: __LF_RATES.migration_form, migration_calendar: __LF_RATES.migration_calendar, migration_page_layout: __LF_RATES.migration_page_layout, migration_page: __LF_RATES.migration_page };
    (po.pieces || []).forEach(p => { if (CARD[p.piece_type] !== p.unit_price && !(p.rate_type === 'proven' && Math.round(CARD[p.piece_type] / 2) === p.unit_price)) fails.push('CARD RATE: ' + p.piece_description + ' at ' + money(p.unit_price) + ' is not the card ' + money(CARD[p.piece_type])); if (Number(p.unit_price) * Math.max(1, Number(p.quantity) || 1) !== Number(p.subtotal)) fails.push('PRICE OBJECT: ' + p.piece_description + ' subtotal is not its rate times its count'); });
    /* scope: every priced piece sits in exactly one shown block, and each block price equals its pieces */
    const pb = Array.isArray(out.price_blocks) ? out.price_blocks : null;
    if (!pb) fails.push('PRICE BLOCK V2.30: the renderer did not record its outcome blocks');
    else {
      const seen = {}; pb.forEach(b => (b.pieces || []).forEach(ix => { seen[ix] = (seen[ix] || 0) + 1; }));
      (po.pieces || []).forEach((p, ix) => { if (seen[ix] !== 1) fails.push('SCOPE/PRICE MISMATCH: a priced piece is shown ' + (seen[ix] || 0) + ' times: ' + p.piece_description); });
      pb.forEach(b => {
        const want = (b.pieces || []).reduce((s, ix) => s + Number(((po.pieces || [])[ix] || {}).subtotal || 0), 0);
        if (want !== b.amount) fails.push('PRICE BLOCK V2.30: ' + b.title + ' shows ' + money(b.amount) + ', its pieces add to ' + money(want));
        if (!shownBlocks.some(s => s.title === b.title && s.amount === b.amount)) fails.push('PRICE BLOCK V2.30: block not shown in the letter: ' + b.title);
      });
      if (shownBlocks.length !== pb.length) fails.push('PRICE BLOCK V2.30: the letter shows ' + shownBlocks.length + ' block prices, the renderer made ' + pb.length);
    }
  }
}

function __v230GateWords() {
  /* V2.30 (card dl1plsWm): no piece kind labels, item kinds or hyphenated compounds in the letter or the Loom; the provisional line follows the Total */
  try {
    const __lab = /^\s*(Two systems talking|Setup inside your existing tools|Moved over as is|Decisions|Dashboards and reports|Systems past the first two|Touches money or live records|Where I would start|Money or record changes)\s*$/im;
    [['letter', letter], ['Loom', loom]].forEach(([nm, t]) => {
      if (__lab.test(t)) fails.push('LABEL V2.30: a piece kind label is in the ' + nm);
      if (/\bmigration_[a-z_]+\b|\bpiece_type\b|\bmoved over as is\b/i.test(t)) fails.push('LABEL V2.30: an item kind is in the ' + nm);
      const words = String(t).split('\n').filter(l => !/^\s*INTRO VIDEO:/i.test(l)).join(' ').split(/\s+/).filter(w => !/:\/\/|@/.test(w));
      const hy = words.filter(w => /[A-Za-z0-9]-[A-Za-z]/.test(w));
      if (hy.length) fails.push('HYPHEN V2.30: hyphenated compound in the ' + nm + ': ' + hy.slice(0, 5).join(', '));
    });
    if (po && po.status === 'PRICED' && !__compactAudit && (po.pieces || []).length && letter.indexOf("Based on what I know so far, here's where I'd land. If anything changes once we talk it through, I'll update it before anything starts.") < 0) fails.push('PROVISIONAL V2.30: the provisional line is missing after the Total');
  } catch (e230) { fails.push('V2.30 word check could not run: ' + String(e230).slice(0, 120)); }
}

const __body = (fn) => { const s = fn.toString(); return s.slice(s.indexOf('{') + 1, s.lastIndexOf('}')).replace(/^\n/, ''); };

function patchCockpit(w, mode) {
  const av = w.activeVersion || {};
  const nodes = JSON.parse(JSON.stringify(av.nodes || w.nodes));
  const connections = JSON.parse(JSON.stringify(av.connections || w.connections));
  const N = (name) => { const n = nodes.find((x) => x.name === name); if (!n) throw new Error('V2.30 patch: no node ' + name); return n; };
  const rep = (name, find, repl, count) => {
    const n = N(name); const c = String(n.parameters.jsCode || '');
    const k = c.split(find).length - 1;
    if (k !== count) throw new Error('V2.30 patch: ' + name + ' expected ' + count + ' of [' + find.slice(0, 70) + '] found ' + k);
    n.parameters.jsCode = c.split(find).join(repl);
  };
  const cut = (name, startMark, endMark) => {
    const n = N(name); const c = String(n.parameters.jsCode || '');
    const s = c.indexOf(startMark); if (s < 0 || c.indexOf(startMark, s + 1) >= 0) throw new Error('V2.30 patch: ' + name + ' start mark not unique: ' + startMark.slice(0, 60));
    const e = c.indexOf(endMark, s); if (e < 0) throw new Error('V2.30 patch: ' + name + ' end mark missing: ' + endMark.slice(0, 60));
    return { n, c, s, e: e + endMark.length };
  };
  if (String(N('Final Render V2').parameters.jsCode).indexOf('V2.30') >= 0) throw new Error('V2.30 patch: already applied');
  if (String(N('Price Gate Engine').parameters.jsCode).indexOf('V2.29') < 0) throw new Error('V2.30 patch: V2.29 is not on this Cockpit');

  // 1. Final Render V2
  const FR = 'Final Render V2';
  { const x = cut(FR, 'function __renderPricingBlock(po) {', "  out.push('Total: ' + money(po.total));\n  return out.join('\\n');\n}");
    x.n.parameters.jsCode = x.c.slice(0, x.s) + '/* V2.30 (Seth Nov 23 2026, card dl1plsWm): the price block is outcome blocks built by code from the priced pieces; the model never writes it. */\nvar __LF_BLOCKS = null;\n' + __renderPricingBlock.toString() + x.c.slice(x.e); }
  rep(FR, 'rendered = __renderPricingBlock(po);', 'rendered = __renderPricingBlock(po); out.price_blocks = __LF_BLOCKS;', 1);
  rep(FR, "30 days of support after go-live are included.'", "30 days of support after go live are included.'", 1);
  rep(FR, '/(each:|Two systems talking|Setup inside|Decisions|Dashboards and reports|Systems past|Where I would start|Touches money)/i.test(p)', '/(each:|Two systems talking|Setup inside|Moved over as is|Decisions|Dashboards and reports|Systems past|Where I would start|Touches money)/i.test(p)', 1);
  rep(FR, '/^\\s*(Two systems talking|Setup inside your existing tools|Decisions|', '/^\\s*(Two systems talking|Setup inside your existing tools|Moved over as is|Decisions|', 1);
  rep(FR, 'out.final_render = { rendered_block: rendered,',
    "/* V2.30 (card dl1plsWm): hyphenated compounds in the letter and the Loom are written as separate words (Seth's standing rule) */ try { const __dh = s => String(s || '').split('\\n').map(l => /^\\s*INTRO VIDEO:/i.test(l) ? l : l.split(/(\\s+)/).map(w => /:\\/\\/|@/.test(w) ? w : w.replace(/([A-Za-z0-9])-(?=[A-Za-z])/g, '$1 ')).join('')).join('\\n'); const __b1 = out.coverLetter, __b2 = out.loomScript; if (typeof out.coverLetter === 'string') out.coverLetter = __dh(out.coverLetter); if (typeof out.loomScript === 'string') out.loomScript = __dh(out.loomScript); if (__b1 !== out.coverLetter || __b2 !== out.loomScript) notes.push('V2.30: hyphenated compounds written as separate words'); } catch (e230) { notes.push('V2.30 hyphen pass skipped: ' + String(e230).slice(0, 100)); }\nout.final_render = { rendered_block: rendered,", 1);

  // 2. Cockpit Gate V2
  const GATE = 'Cockpit Gate V2';
  { const x = cut(GATE, 'let blockSum = 0; const shownUnits = [];', "fails.push('SCOPE/PRICE MISMATCH: priced but not shown: ' + p.piece_description); });\n}");
    x.n.parameters.jsCode = x.c.slice(0, x.s) + __body(__v230GateBlock) + x.c.slice(x.e); }
  rep(GATE, 'const loomMoney = loom.match(', __body(__v230GateWords) + '\nconst loomMoney = loom.match(', 1);
  rep(GATE, "if (x.status === 'PRICED') byDel[t].priced++;", "if (x.status === 'PRICED') byDel[t].priced += Math.max(1, parseInt(x.units, 10) || 1); /* V2.30: a moved item line counts its units */", 1);

  // 3. Price Gate Engine: coverage entries for moved items carry their count
  rep('Price Gate Engine', "res.map.push({ deliverable: d.title, status: 'PRICED', piece: __ml, piece_type: d.piece_type, amount: __ms, why: 'moved as is, ' + __mu + ' items' });",
    "res.map.push({ deliverable: d.title, status: 'PRICED', piece: __ml, piece_type: d.piece_type, amount: __ms, units: __mu, why: 'moved as is, ' + __mu + ' items' });", 1);

  // 4. Read Rate Table reads source_ref; the review email table reads the blocks and the current version
  const rrt = N('Read Rate Table');
  if (String(rrt.parameters.url).indexOf('select=piece_kind,unit_rate_cents') < 0) throw new Error('V2.30 patch: Read Rate Table url drifted');
  rrt.parameters.url = String(rrt.parameters.url).replace('select=piece_kind,unit_rate_cents', 'select=piece_kind,unit_rate_cents,source_ref');
  const CRE = 'Compose Review Email';
  { const x = cut(CRE, 'function lfPriceRows(letter) {', "return { rows: rows.map(r => Object.assign(r, { item: cap(r.item) })), total, provisional };\n}\n");
    x.n.parameters.jsCode = x.c.slice(0, x.s) + lfPriceRows.toString() + '\n' + lfPsVersion.toString() + '\n' + x.c.slice(x.e); }
  rep(CRE, "h += sec('Itemized price · Pricing Standard v2.4', t);", "h += sec('Itemized price · ' + lfPsVersion(), t);", 1);
  rep(CRE, "30 days of support after go-live.'", "30 days of support after go live.'", 1);

  // Syntax check every patched code node.
  const AsyncFn = Object.getPrototypeOf(async function () {}).constructor;
  [FR, GATE, 'Price Gate Engine', CRE].forEach((n) => { try { new AsyncFn('$', '$input', N(n).parameters.jsCode); } catch (e) { throw new Error('V2.30 patch: syntax error in ' + n + ': ' + e.message); } });

  let name = w.name;
  if (mode === 'test') {
    name = 'TEST COPY Cockpit V2.30 (card dl1plsWm, side effect nodes disabled)';
    const SIDE = ['Email Backup', 'Archive Folder', 'Archive Pack', 'Archive Sketch', 'Mark Job', 'Write Run', 'Ledger Save', 'Save Page Truth', 'Post Proposal', 'Name The Call', 'Price The Call', 'Fire Forge'];
    nodes.forEach((n) => { if (SIDE.indexOf(n.name) >= 0) n.disabled = true; if (n.type === 'n8n-nodes-base.webhook') n.parameters.path = 'cockpit-test-v230-' + String(n.parameters.path || '').slice(-8); if (n.webhookId) n.webhookId = undefined; });
  }
  return { name, nodes, connections, settings: { executionOrder: (w.settings || {}).executionOrder || 'v1' } };
}
if (typeof module !== 'undefined') module.exports = { patchCockpit, __renderPricingBlock, lfPriceRows };
