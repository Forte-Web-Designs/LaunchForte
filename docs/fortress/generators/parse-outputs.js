const run = $('Prompt of Record').first().json;
const resp = $input.first().json;
const body = resp.body || resp;
if (resp.statusCode && resp.statusCode >= 400) {
  throw new Error('COCKPIT: the model call returned ' + resp.statusCode + '. ' + JSON.stringify(body).slice(0, 300));
}
const parts = (body && body.content) || [];
const text = parts.filter(p => p && p.type === 'text').map(p => p.text).join('\n').trim();
if (!text) throw new Error('COCKPIT: the model returned no text. Stop rather than send an empty draft.');
let raw = text.replace(/^\`\`\`(?:json)?/i, '').replace(/\`\`\`$/, '').trim();
const a = raw.indexOf('{'), b = raw.lastIndexOf('}');
if (a > 0 || b < raw.length - 1) raw = raw.slice(a, b + 1);
let out;
try { out = JSON.parse(raw); }
catch (e) { throw new Error('COCKPIT: the model did not return clean JSON (' + e.message + '). First 200 chars: ' + raw.slice(0, 200)); }
for (const k of ['coverLetter', 'loomScript', 'sketch']) {
  if (!out[k]) throw new Error('COCKPIT: the model output is missing ' + k + '.');
}

// ---------------------------------------------------------------------------
// STRUCTURAL NORMALISATION
//
// The letter's shape used to be a request in the prompt: body, then sign off,
// then the buyer's questions. Across five live runs the model honoured it three
// times. Two letters had no sign off at all, one put the questions above it, and
// the video promised screenshots on two of the three sends that had them.
//
// So it stops being a request. The model writes the parts; the ORDER is decided
// here, in code, where it cannot vary. Same reason the price and the evidence
// are derived rather than asked for.
// ---------------------------------------------------------------------------
const SIGNOFF = 'Seth Forte';

const paras = (s) => String(s || '').split(/\n\s*\n/).map(p => p.trim()).filter(Boolean);
const isSignoff = (p) => /^seth\s+forte[.,]?$/i.test(p.trim());

// Anything the model left as scaffolding. A bracketed token in a letter a buyer
// reads is the tell that nobody looked at it before it went.
function deScaffold(list) {
  return list
    .filter(p => !/^\[.*\]$/.test(p))
    .filter(p => !/^(blueprint|draft|cover ?letter|subject|title)\s*:?\s*$/i.test(p))
    .map(p => p.replace(/^[ \t]*intro video[ \t]*:.*$/gim, ''))
    .map(p => p.replace(/\[[A-Z][A-Z0-9 _\-]{2,30}\]/g, ''))
    .map(p => p.replace(/[ \t]{2,}/g, ' ').trim())
    .filter(Boolean);
}

function fixLetter(letter) {
  let P = deScaffold(paras(letter));

  // The answers ride behind a delimiter the prompt asks for. If the model drops
  // the delimiter, fall back to recognising the answers by how they read —
  // never guess more than the trailing run of paragraphs.
  let answers = [];
  const d = P.findIndex(p => /^-{2,}\s*ANSWERS\s*-{2,}$/i.test(p));
  if (d >= 0) {
    answers = P.slice(d + 1);
    P = P.slice(0, d);
  } else {
    const looksLikeAnswer = (p) => /from your stack|the most complex|closest delivered|you asked about|on the integrations|on your questions/i.test(p);
    while (P.length > 2 && (looksLikeAnswer(P[P.length - 1]) || isSignoff(P[P.length - 1]))) {
      answers.unshift(P.pop());
    }
  }

  // Exactly one sign off, and it sits between the body and the answers. Every
  // other copy of it goes.
  P = P.filter(p => !isSignoff(p));
  answers = answers.filter(p => !isSignoff(p));

  return { text: P.concat([SIGNOFF]).concat(answers).join('\n\n'),
           answersFound: answers.length, byDelimiter: d >= 0 };
}

const SHOT_PROMISE = 'I am going to attach a couple of screenshots from a similar product I have built and shipped multiple times, so you can take a look. It may not be a one to one fit, but it is similar and I have real experience with the idea behind what you are asking for.';

function fixScript(script, hasShots) {
  let P = paras(script);
  const mentions = P.some(p => /screenshot/i.test(p));
  let added = false, removed = false;
  if (hasShots && !mentions) {
    P.splice(Math.max(P.length - 1, 0), 0, SHOT_PROMISE);
    added = true;
  }
  // Promising a picture that is not in the email is the one unrecoverable thing
  // the script can do, so a claim without attachments is cut, not softened.
  if (!hasShots && mentions) {
    P = P.filter(p => !/screenshot/i.test(p));
    removed = true;
  }
  return { text: P.join('\n\n'), added, removed };
}

let __ev = {};
try { __ev = $('Pick the evidence to attach').first().json || {}; } catch (e) { __ev = {}; }
const __hasShots = (__ev.evidence_count || 0) > 0;

const __L = fixLetter(out.coverLetter);
const __S = fixScript(out.loomScript, __hasShots);
const __wasLetter = String(out.coverLetter || '');
out.coverLetter = __L.text;
out.loomScript = __S.text;

// Observable, like everything else that decides something on its own.
const normalised = {
  answers_paragraphs: __L.answersFound,
  answers_found_by: __L.byDelimiter ? 'delimiter' : (__L.answersFound ? 'reading' : 'none present'),
  signoff_was_missing: !/seth\s+forte/i.test(__wasLetter),
  scaffolding_stripped: __wasLetter.length - out.coverLetter.length,
  had_attachments: __hasShots,
  script_promise_added: __S.added,
  script_promise_removed: __S.removed,
};

return [{ json: { run, out, normalised } }];