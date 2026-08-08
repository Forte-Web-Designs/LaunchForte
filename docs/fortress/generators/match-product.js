// What has already been built that answers this brief? Score the job post against every
// product we can actually show, and hand the winners to the proposal as evidence.
const specs = $input.all().map(function (i) { return i.json; })
  .filter(function (s) { return s && s.product_key && s.demo_endpoint && (s.proof_ok === true || String(s.proof_ok).toLowerCase() === 'true'); });
let brief = '';
try {
  const j = $('Merge Context').first().json;
  brief = [j.job_post, j.notes, j.company, j.title].filter(Boolean).join(' ');
} catch (e) { brief = ''; }
if (!brief) { try { brief = JSON.stringify($('Read Job Row').first().json).slice(0, 4000); } catch (e2) { brief = ''; } }
const hay = String(brief).toLowerCase();

const STOP = { the:1, and:1, for:1, with:1, that:1, this:1, from:1, into:1, your:1, our:1, are:1, you:1 };
const words = function (s) {
  const seen = {};
  String(s || '').toLowerCase().split(/[^a-z0-9]+/).forEach(function (w) { if (w.length > 3 && !STOP[w]) { seen[w] = 1; } });
  return Object.keys(seen);
};
const briefWords = words(hay);

const scored = specs.map(function (s) {
  const bag = words([s.name, s.pain_point, s.what_the_buyer_sees, s.tools_required, s.upwork_evidence].join(' '));
  let hits = 0;
  const matched = [];
  briefWords.forEach(function (w) { if (bag.indexOf(w) !== -1) { hits++; if (matched.length < 6) { matched.push(w); } } });
  const nameHit = words(s.name).filter(function (w) { return hay.indexOf(w) !== -1; }).length;
  return { s: s, score: hits + nameHit * 3, matched: matched };
});
scored.sort(function (a, b) { return b.score - a.score; });
// a couple of stray shared words is not a match. require real overlap.
const winners = scored.filter(function (x) { return x.score >= 4; }).slice(0, 2);

const evidence = winners.map(function (x) {
  const s = x.s;
  return {
    key: s.product_key, name: s.name,
    pain: String(s.pain_point || ''),
    buyer_sees: String(s.what_the_buyer_sees || ''),
    demo: String(s.demo_endpoint || ''),
    workflow: String(s.workflow_url || ''),
    screenshot: String(s.screenshot_url || ''),
    market: String(s.upwork_evidence || ''),
    why_matched: x.matched.join(', '), score: x.score
  };
});

// Hand the upstream items back WITH the run context still attached.
//
// This used to return the shapes-table rows alone. The comment said "so nothing
// downstream changes shape", and it was half right: the table's shape survived
// and the RUN's shape did not. Every node after this one — the evidence picker,
// the pricing, the Prompt of Record — received a row from a table and no job
// post, and honoured the `shape` field on that row. That row carried
// voice-agent-intake, so three unrelated postings came back with the same four
// voice-agent-intake screenshots. The matcher was never wrong. It was never
// asked.
//
// The run context goes on FIRST so any key the table row defines still wins:
// downstream behaviour for those fields is unchanged. The posting simply comes
// back too.
let __run = {};
try { __run = $('Merge Context').first().json || {}; }
catch (e) {
  try { __run = $('Ground Match').first().json || {}; } catch (e2) { __run = {}; }
}
const carry = $('Read Shapes (Cockpit)').all();
return carry.map(function (it) {
  return { json: Object.assign({}, __run, it.json, {
    matchedProducts: evidence, matchedCount: evidence.length,
    briefWordCount: briefWords.length,
    run_context_restored: Object.keys(__run).length }) };
});