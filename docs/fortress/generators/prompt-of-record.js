// PATCH __LF_PRICING — derive the quote from parts the client can rebuild.
// Class comes from what the POSTING describes, never from the resolved shape:
// a bad shape resolution must not become a confidently wrong price.
const __p = (function () {
  const j = $json || {};
  const hay = String((j.job_post||j.jobPost||j.text||'')+' '+(j.jobTitle||j.title||'')+' '+(j.notes||'')).toLowerCase();
  const R={audit:650,simple:800,base:2500,surface:300,docs:250,testPct:0.15,retainer:750,ceiling:3500};
  const aud=/(audit|review our|review the|assess|take over|inherit|undocumented|transcript)/.test(hay);
  const bot=/(chatbot|chat bot|conversation ai|ai agent|ai assistant|voice ai|receptionist)/.test(hay);
  const sys=/(crm|pipeline|dashboard|integrat|sync|migrat|onboard|full system|build out|end to end|ecosystem)/.test(hay);
  const k=(aud&&!sys)?4:bot?3:sys?2:1;
  let wf=1; const m=hay.match(/(\d+)\s*(automation|workflow|sequence|zap|scenario)/);
  if(m){wf=Math.min(parseInt(m[1],10)||1,12);} else {
    const L=(hay.match(/nurture|recovery|onboarding|retention|churn|referral|reminder|follow up|follow-up/g)||[]).length;
    if(L>1){wf=Math.min(L,12);} }
  const T=['gohighlevel','ghl','hubspot','pipedrive','salesforce','zoho','shopify','stripe','quickbooks','xero','airtable','monday','clickup','notion','twilio','slack','zapier','make','n8n','instantly','klaviyo','activecampaign','calendly','wordpress','google sheets','hyros'];
  const sn=Math.max(T.filter(function(t){return hay.indexOf(t)!==-1;}).length,1);
  const lines=[]; let sub=0;
  const add=function(l,a,w){lines.push('- '+l+': $'+a.toLocaleString('en-US')+'. '+w); sub+=a;};
  if(k===4&&aud){add('Audit, week one',R.audit,'Nothing changes in week one except the map. The rebuild quotes after it exists.');}
  else if(k===3&&/transcript|review/.test(hay)){add('Transcript audit',R.audit,'Twenty real transcripts in, the three failure turns named.');}
  else if(k===1){add('Workflow build',R.simple,'One trigger, one system, one outcome.');
    for(let i=1;i<wf;i++){add('Additional workflow',R.simple,'Rides the same records as the first.');} }
  else {add('Full system base',R.base,'Covers the first two workflows across the first two systems.');
    for(let i=2;i<wf;i++){add('Additional workflow',R.simple,'Beyond the two the base covers.');} }
  const ex=Math.max(sn-2,0);
  for(let i=0;i<ex;i++){add('Integration surface',R.surface,'Each system past the first two.');}
  const bs=sub; const gig=/upwork|gig/i.test(String(j.channel||'Upwork'));
  if(!gig){add('Testing and hardening on real data',Math.round(bs*R.testPct),'Your data, not a sandbox.');
    add('Documentation and handoff',R.docs,'You own the whole thing when I am gone.');}
  add('Warranty, 30 days, fix anything we built',0,'Included, and on the sheet so you can see it.');
  const tot=sub; let ph=null;
  if(gig&&tot>R.ceiling){const p1=Math.min(R.base+(ex?R.surface:0),R.ceiling); ph='Split by phase: $'+p1.toLocaleString('en-US')+' phase one, $'+(tot-p1).toLocaleString('en-US')+' phase two. A first engagement lands at or under about $3,500, so scope splits rather than the number inflating or being discounted.';}
  const A={1:'Published 2026 freelancer bands put a single workflow at $1,000 to $6,000.',2:'Published 2026 benchmarks put a build this shape at $2,000 to $8,000 for three to ten workflows with APIs.',3:'Custom bots run $1,000 to $5,000 bare and $10,000 to $30,000 at an agency.',4:'Complex multi-system work runs $8,000 to $20,000+ at the top of published bands.'};
  return {k:k,wf:wf,sn:sn,tot:tot,lines:lines.join('\n'),ph:ph,anchor:A[k]};
})();
const __PRICING_BRIEF = ['','=== PRICING, DERIVED. USE THESE PARTS, DO NOT INVENT A NUMBER ===',
  'Class '+__p.k+'. '+__p.wf+' workflow(s) across '+__p.sn+' system(s).','Lines:',__p.lines,
  'Derived total: $'+__p.tot.toLocaleString('en-US')+'. Quote this exact figure. Never round it, never end it in 997, never discount it. Remove a line instead and the number drops with it.',
  (__p.ph||''),'Anchor you may cite: '+__p.anchor,
  'Retainer: treat it as a conversation, not a fixed line. Say it scales with the work — the number of client accounts covered, the build volume week to week, and how much of the calls-and-oversight side they want. Two floors you may quote: monitoring-shaped retainers start at $750 a month; ongoing retainer work starts at $2,500 a month and scales with accounts and builds. Offer a more accurate number once they confirm how many client accounts you would be covering and the build volume they expect week to week. 43% of businesses using freelancers for automation hit at least one critical workflow failure from lack of ongoing support (Zapier, State of Business Automation).',
  'Why it costs this: what they pay for is the part invisible until it fails. Input validation with a refusal path so malformed data never becomes a half-record. Deduplication, because the same event arrives twice more often than anyone expects. Rate limiting so the vendor ceiling is respected rather than discovered in production. Retries with an error branch so a failed call alerts instead of failing silently. Logging on both paths. And a second scheduled trigger that keeps finding what nobody noticed. Those are the lines a cheaper quote skips, and the buyer does not learn which until something breaks quietly. They are visible node by node in the attached build.',
  'ABSOLUTE: no hourly rates, no hour counts, no time in hours anywhere. Never mention what other buyers have spent.',
  '=== END PRICING ===',''].join('\n');

// ---------------------------------------------------------------------------
// THE PROOF BLOCK — generated by proposalgen.py. Do not hand edit.
//
// Fifteen blanks used to ship in every proposal: six build slots and three
// testimonial slots, all empty, all marked 'tokens missing'. The model left
// them empty because it had nothing true to put there, which was correct.
// These are the real ones, from the proposal that shipped and settled.
// ---------------------------------------------------------------------------
const __PROOF = ['',
  '=== THE TRACK RECORD. REAL, AND THE ONLY BUILDS THAT MAY BE NAMED ===',
  'Never invent a client, a number or a quote. Never name a company.',
  'If a build is not on this list it does not exist for this proposal.',
  '50+ projects delivered.',
  '100% client satisfaction.',
  '5 weeks to go live.',
  '14 days of support after handover.',
  '',
  'COMPARABLE BUILDS, described by client TYPE only:',
  '1. Online Course Platform — enrollment and course delivery lived on two disconnected platforms; rebuilt as one connected system, cutting manual enrollment work to zero.',
  '2. Financial Services Firm — capital call notices were tracked and chased by hand across spreadsheets; automated the notice cascade and the payment reconciliation end to end.',
  '3. Cleaning Services Company — operations were scattered and there was no system to start from; a four milestone build brought them onto one connected system from a standing start.',
  '4. Restoration Contractor — reporting lived across scattered spreadsheets; delivered one dashboard the office and the client could both trust.',
  '5. Moving Company — field crews worked off memory and phone calls; shipped a mobile app that tracks every stage of a move as it happens.',
  '6. Grocery Industry Association — a marketing automation had gone stale inside a portal already running dozens of live workflows; reconciled it against the working ones and relaunched it without breaking anything already in motion.',
  '',
  'THE ONE TESTIMONIAL ON FILE. Use it verbatim or not at all:',
  '"The process was smooth and stress free from start to finish. I would call it a ten out of ten, and I am already planning to come back for the next project."',
  '  — Chelsea, Founder, 6 Months to Speech',
  '',
  '=== THE SHAPE OF A LAUNCH FORTE PROPOSAL. EIGHT PAGES, THIS ORDER ===',
  '01 Cover: reference, date, client name, the engagement title, and one sentence on what they end up with. Then prepared for, engagement type, delivery window, investment.',
  '02 Situation: where things stand in their own words and numbers. The path today drawn as steps with ONE marked failure point, then what this is costing now, then what changes. Name the break in a single bolded sentence.',
  '03 Scope: the deliverables, numbered 01 upward, each a heading and two or three plain sentences. The last two are always a live acceptance test and a handover.',
  '04 Investment: the derived figure, the milestone split, and a week by week schedule. Then what is and is not included, changes and scope, revisions, payment.',
  '05 Track record: the four numbers, one testimonial, and the comparable builds below.',
  '06 Operating terms: how updates work, what to expect, keeping things moving, acceptance, decision maker, support, cancellation and refunds.',
  '07 Standard terms: the thirteen numbered clauses, unchanged, version dated.',
  '08 Acceptance: what is needed to begin — access, information, kickoff — and the four step approval: reply, invoice, fund and send access, the clock starts.',
  '',
  'A PLACEHOLDER IN A PROPOSAL IS A DEFECT. If a fact is not above, cut the',
  'line rather than leave a bracketed token in a document a client reads.',
].join('\n');


// PATCH __LF_NO_OWN_URLS — the model was shown our own image URLs (referenceBuilds
// carries shot_url) while being told 'Zero URLs'. It leaked one into the COVER
// LETTER and Audit held the draft, correctly: a launchforte.com link in an Upwork
// letter reads as circumvention. Proof travels as an attached PDF now, so the
// prompt never needs our URLs. This strips ONLY our own domain from the prompt
// text; Attach Reference Builds still receives the real URLs it needs.
const __out = (function () {
const _rows = $('Read Template').all().map(function (i) { return i.json; });
const _tpl = _rows.filter(function (r) { return r.key === 'active'; })[0] || _rows[0] || {};
const _proofRow = _rows.filter(function (r) { return r.key === 'proof'; })[0];
const PROOF_LINES = _proofRow ? String(_proofRow.body || '').split(String.fromCharCode(10)).filter(Boolean) : [];
const TEMPLATE_VERSION = _tpl.version || 'unknown';
const TEMPLATE = _tpl.body || '';
if (!TEMPLATE || TEMPLATE.length < 5000) {
  throw new Error('COCKPIT: the proposal_template row is missing or too short (' + (TEMPLATE||'').length + ' chars). Nothing was generated.');
}
const NL = String.fromCharCode(10);
const j = $('Ground Match').first().json;
const CHANNEL = (j.channel === 'external') ? 'external' : 'upwork';
const UPWORK_RULES = [
  'CHANNEL RULES, UPWORK. These override anything that conflicts.',
  'Sign as Seth Forte. The words Launch Forte never appear anywhere a client reads.',
  'Zero URLs, zero email addresses, zero booking links, zero phone numbers.',
  'Scheduling stays on platform: ask for a couple of windows, Monday to Friday, 9 to 5 Central.',
  'LINKS ARE NOT A CHAT THING, THEY ARE A CONTRACT THING. On Upwork a link cannot be sent when they reply, cannot be sent in chat, and cannot be sent in an interview. Nothing carrying a URL may travel until we are UNDER CONTRACT. Getting into the messages is not the unlock; the contract is.',
  'So never promise a link on any earlier trigger. Never write once you reply, once we are in chat, over chat, in the messages, when we connect, on the call, or anything with the same shape, attached to a link, a demo, a store, a walkthrough or a login.',
  'IF THE LINK RULE NEEDS SAYING AT ALL, SAY IT PLAINLY AND STOP. The whole sentence is: Upwork does not allow sharing links before we are under contract. Do not build a clause around it, do not turn it into a promise about what happens later, and never write anything of the shape anything carrying a URL is something I share once we are working together. State the rule, move on.',
  'What may be offered BEFORE a contract: the attachments already in this email, and answers to anything they ask. Nothing else needs offering.',
  'PRICING DISCIPLINE: the platform ceiling is separate from the value ceiling. A number that reads as gig-platform agency price gets discounted or skipped before the pitch is even read, regardless of how well justified it is.',
  'STANDING UPWORK CEILING, until real data says otherwise: land at or under roughly $3,000 to $3,500 for a first engagement, even when the honestly scoped value or hourly math would support more.',
  'IF TRUE SCOPE EXCEEDS THE CEILING, SPLIT, DO NOT INFLATE: propose a smaller first phase that fits under the ceiling, with Phase 2 and Phase 3 named as a non-binding roadmap. Never quote the full number and hope.',
  'CITE BOTH CEILINGS IN YOUR REASONING: ground the number in the pricing repository value-based figure AND the Upwork platform ceiling. When they conflict, propose the phase split rather than silently picking one.'
].join(NL);
const DIRECT_RULES = [
  'CHANNEL RULES, DIRECT CLIENT. These override anything that conflicts.',
  'Launch Forte branding is correct. Sign as Seth Forte, Launch Forte.',
  'seth@launchforte.com may be named as the preferred channel of record.',
  'A booking link may be offered as a convenience, never as a gate: calendly.com/seth-launchforte.',
  'Pricing is direct pricing. Everything else about how the work runs is identical.', 'CITATION RULE (direct-channel only): every specific dollar figure or price in the letter must be traceable to its source. In your reasoning, ground each number in either a pricing repository line (name the SKU or line item) or a stated floor and the reason for it. Do not put citation text in the letter itself -- the letter stays plain client-facing prose. This is an internal discipline check, not new client-facing copy.',
].join(NL);
const CHANNEL_RULES = (CHANNEL === 'upwork') ? UPWORK_RULES : DIRECT_RULES;
const PROOF_BLOCK = PROOF_LINES.length ? [
  'PROOF LINES, real delivered work. Pick AT MOST ONE, the single most relevant to this job,',
  'and weave it into the letter as one sentence, ex: I have done this shape before: {line}.',
  'If none of them genuinely matches the work, use NONE and write the letter without a proof line.',
  'Never stretch a line to fit. Never use more than one. Never invent a number or a detail not in the line.',
  PROOF_LINES.map(function (l, i) { return '  ' + (i + 1) + '. ' + l; }).join(String.fromCharCode(10))
].join(String.fromCharCode(10)) : 'No proof lines are loaded, so write the letter without one.';
const OUTPUT_CONTRACT = [
  'You produce four things in one pass and return them as ONE JSON object and nothing else.',
  'No preamble, no markdown fences. The first character of your reply is {.',
  'SHAPE:',
  '{',
  '  "coverLetter": "the full letter, plain text, paragraphs separated by blank lines, 150 to 400 words",',
  '  "loomScript": "word for word speech, 130 to 380 words",',
  '  "onScreen": "the ONE thing the video shows on screen, under 12 words",',
  '  "sketch": {',
  '    "title": "Sketch: what the job is, three or four plain words, NEVER the word your",',
  '    "mainIdea": "two to four plain lowercase words naming the build, used for the filename",',
  '    "archetype": "pipeline or hub or fork",',
  '    "nodes": ["two to four words each, three to five of them"],',
  '    "decisionIndex": 0,',
  '    "edgeNodes": [{ "label": "three to six words", "fix": "three to six words" }],',
  '    "glyph": { "kind": "timer or bell", "label": "two words", "onNode": 0 },',
  '    "reframe": "one short sentence, optional",',
  '    "easyLine": "one short sentence, optional",',
  '    "annotations": { "calibration": "one sentence", "safety": "one sentence" }',
  '  }',
  '}',
  'NEVER state a number of hours anywhere in the letter or the script, not even quoting the job post back.',
  'No hourly rates, no hour estimates, no time in hours. If the post says 25 hours, do not repeat it.',
  'THE COVER LETTER follows the structure and rules above exactly.',
'ORDERING, HARD RULE, OVERRIDES ANY STRUCTURE ABOVE. Any screening or interview questions the',
'buyer asked are answered LAST, in a block at the very bottom of the letter, after the sign off.',
'Never weave them through the body, never open with them, never break the body to address them.',
'The body runs in this order: the read on what they actually need; one thing worth knowing up',
'front about their own tool; anything we have not used, said straight; the product this mirrors',
'and what the picture shows; the close. THEN, and only then, the answers.',
'Answer them in prose, in their order, no numbering and no headings. No preamble — never write',
'"on your questions", "to answer your questions", "your five questions, in order" or anything',
'like it. Just answer, leading with what is concrete and true.',
'The shape to aim for, as one or two sentences: "From your stack I have shipped in A, B and C.',
'The most complex thing I have built and run is <the single hardest estate or system>, <what it',
'spans end to end>, with <the part that proves it runs unattended>."',
'MARK THE BOUNDARY so the ordering can be enforced downstream: put a line containing exactly',
'---ANSWERS--- on its own, immediately before that block. Nothing after it except the answers.',
'Do not write a sign off yourself and do not add any bracketed placeholder, label or heading',
'above the first paragraph. The sign off is placed automatically, in the right position.',
  'THE LOOM SCRIPT is speech. Short lines broken at breath points, ellipses where he pauses.',
  'Its closing references the attached sketch by name.',
  'THE LOOM SCRIPT, WHAT IT IS ALLOWED TO PROMISE. Only promise what is actually attached.',
  'If screenshots are attached (the reference builds block above is not empty), say plainly that',
  'he is going to attach a couple of screenshots from a similar product he has built and shipped',
  'multiple times, so they can take a look, and that it may not be a one to one fit but it is',
  'similar and he has real experience with the idea behind their ask.',
  'If there are NO screenshots, never mention screenshots in the script at all. Reference only',
  'the sketch by name. Promising a picture that is not in the email is the one unrecoverable',
  'thing this script can do.',
  'THE SKETCH IS A HAND DRAWN ONE PAGE DRAWING, NOT A DOCUMENT. Hard rules:',
  'HOW THE MARGINS TALK. Concrete nouns and plain words only: clean, wonky, quiet, messy, boring, easy.',
  'CANON: the win is the invoices that start clean. That beats day one data quality, because you can',
  'picture an invoice and nobody on earth says data quality out loud. Write the thing, not the category.',
  'BANNED IN THE SKETCH: edge cases, the flow, data quality, and any aphorism shaped like X are the job',
  'or the real X is Y. Those read as a model being clever. Name the actual failure instead,',
  'ex: returning clients get welcomed twice. A scar is a thing that happened, never a lesson.',
  'The title is just the job idea in three or four plain words. The page already opens with',
  'Just taking a stab at it, so never write that line yourself and never restate it.',
  'THE LOCKED PHRASE BANK. The margins can only speak in these sentences. The page already prints',
  'the stance, the calibration, the safety line, the diagram header and the scar cluster label,',
  'so NEVER write those yourself. You supply only: title, mainIdea, nodes, edgeNodes, glyph, reframe.',
  'TITLE: the job main idea in plain words. Never the word sketch.',
  'REFRAME: the shape is locked. It reads The win here is {something you can picture}.',
  'Exemplar: The win here is consistent clean data. Swap the object to this job own nouns,',
  'ex: The win here is invoices that start clean, or The win here is leads that never sit.',
  'Never change the sentence shape.',
  'GLYPH label must be exactly one of: this step is timed | counted in and out | this step is watched | every run is written down | if it goes quiet, you hear about it | written, then read back',
  'SCARS ARE PAIRED. Each edgeNode carries a label (the gotcha) AND a fix (your answer to it).',
  'A gotcha alone reads as cryptic doom and the client cannot tell whose problem it is.',
  'Send exactly TWO pairs. Use Seth own wording, matched to the job class.',
  'Nouns may adapt to this job objects, the shape never does. THE PAIRED BANK, label then fix:',
  '  Forms: half filled forms / saved, finished later',
  '  Data: duplicates unknowingly popping up / checked before a new one is created | 2 systems not speaking the same language / changes show up on both sides',
  '  Books: cents off forever / matched to the penny | paid twice, never caught / every payment matched once | refunds not making sense / tied back to their invoice | invoice not making sense / flagged before it sends',
  '  Leads: green checkmark, nothing sent / checked that it actually sent | replied, no one followed up / every reply gets assigned to someone | hot for an hour, took too long to respond / answered inside the hour | forgot about the lead / every lead gets contacted automatically',
  '  Comms: people ignoring alerts / you only get the ones that matter | right message, wrong person / checked before it sends',
  '  Scheduling: running on the wrong day / runs when you expect it to | timezones messing up appointments / times checked against their time zone | the double booked days / double bookings caught before they happen',
  '  Migrations: fields mapping wrong / verified on a test batch | half finished batch / counted in, counted out',
  '  Reporting: chart not refreshing / refreshed on its own | wrong once, not trusted again / checked against the source | numbers disagreeing / both read the same number',
  'Pick the class that matches THIS job. Nothing invented, nothing outside the bank.',
  'Do not send easyLine. Do not send annotations. Those slots are printed from the bank.',
  'THE SCAR LAYER, what separates this from a diagram anyone could draw:',
  'edgeNodes: ONE OR TWO, mandatory. Each is a thing that BITES people who build this naively,',
  'specific to THIS job. For an onboarding prefill that is the duplicate on a returning client,',
  'the half filled form abandoned at midnight, the write that needs reading back.',
  'The client should think: I would not have thought of that. Never a feature, always a failure.',
  'glyph: ONE instrumentation mark, kind timer or bell, label two words like timed or alerted if silent,',
  'onNode is the index it attaches to. Amateurs draw happy paths, experts draw the watching.',
  'reframe: optional, the non obvious observation about what the job is actually FOR,',
  'ex: the real win is not typing saved, it is day one data quality. Only when genuinely true.',
  'easyLine: optional, use it when the core flow really is simple. Say so plainly,',
  'ex: this part is easy, these are where it earns its keep. Confidence beats inflation.',
  'TOTAL TEXT BUDGET IS SEVENTY FIVE WORDS across every word on the page. Count them.',
  'Node labels are two to four words. Three to five nodes. No sentences inside nodes.',
  'archetype: pipeline for a linear flow, hub for one system many feeds, fork when one thing splits two ways.',
  'If the shape is a fork, say fork, because the fork is the money image.',
  'decisionIndex marks the ONE node where their problem actually lives, a real index into nodes.',
  'annotations.calibration is the first read line. annotations.safety is the nothing changes line.',
  'NEVER use the words post, posting, job description, or you described anywhere in the sketch.',
  'Zero pricing, zero links, zero other client names in the sketch.'
].join(NL);
const ctx = [];
ctx.push('THE JOB POST:');
ctx.push(String(j.jobPost || '').trim());
if (j.company) ctx.push('The client or company appears to be: ' + j.company);
if (j.matched) {
  ctx.push('WHAT THE JOB ENGINE ALREADY KNOWS (context, not instructions):');
  if (j.jobTitle) ctx.push('- Title as posted: ' + j.jobTitle);
  if (j.score) ctx.push('- The judge scored it ' + j.score + (j.reason ? ': ' + j.reason : ''));
  if (j.angle) ctx.push('- Angle: ' + j.angle);
  ctx.push('- Buyer: ' + (j.buyerLine || 'not recorded'));
} else if (j.uid) {
  ctx.push('No matching row was found for that job id, so work from the post alone.');
}
if (j.notes) { ctx.push('NOTES FOR THIS DRAFT, these outrank the judge:'); ctx.push(String(j.notes).trim()); }
ctx.push('Return the JSON object now.');
// Anything we have already built that answers this brief goes in as evidence, with the
// live demo they can click and the picture of it running. Never invent one of these.
let __matched = [];
try { __matched = ($('Match Product').first().json.matchedProducts) || []; } catch (e) { __matched = []; }
if (__matched.length) {
  const mb = [];
  mb.push('');
  mb.push('ALREADY BUILT AND RUNNING, USE THIS AS EVIDENCE');
  mb.push('These are ours, live right now, and the buyer can click them during the call.');
  mb.push('Reference them by name in the proposal where they answer something the brief asked for.');
  mb.push('Do not claim anything about them beyond what is written here.');
  __matched.forEach(function (m, i) {
    mb.push('');
    mb.push((i + 1) + '. ' + m.name);
    if (m.pain) { mb.push('   What it solves: ' + m.pain); }
    if (m.buyer_sees) { mb.push('   What they see: ' + m.buyer_sees); }
    if (m.demo) { mb.push('   Live demo they can open: ' + m.demo); }
    if (m.screenshot) { mb.push('   Screenshot of it running: ' + m.screenshot); }
    if (m.market) { mb.push('   Why it exists: ' + m.market); }
    mb.push('   Matched this brief on: ' + m.why_matched);
  });
  mb.push('');
  ctx.push(mb.join(NL));
}

// ---------------------------------------------------------------------------
// THE PACK IS THE SOURCE OF TRUTH ABOUT WHAT IS IN THE EMAIL.
//
// Two things pick evidence and they were never reconciled. `Match Reference`
// scores its own table against the brief and hands the model a build to
// describe. `Pick the evidence to attach` picks, independently, the shots that
// actually go in the PDF. On a Shopify plus Klaviyo posting, Match Reference
// won a Klaviyo build and the pack shipped Shopify. The letter described a
// Klaviyo screenshot that was not in the attachment, which is the one defect
// that costs the deal outright: the buyer opens the PDF to check.
//
// So the pack decides. Anything the pack did not attach is not described.
// ---------------------------------------------------------------------------
let __pack = {};
try { __pack = $('Pick the evidence to attach').first().json || {}; } catch (e) { __pack = {}; }
const __slug = function (s) { return String(s || '').toLowerCase().replace(/[^a-z0-9]/g, ''); };
// The pack decides its own width now — one tool when the buyer named one, up
// to three when they named none and range is the argument — so the tool list
// has to come from the pack itself. The two scalars are the old fixed shape
// and are only a fallback for a run that predates evidence_tools_shown.
const __packTools = Array.isArray(__pack.evidence_tools_shown) && __pack.evidence_tools_shown.length
  ? __pack.evidence_tools_shown
  : [__pack.evidence_tool_shown, __pack.seam_shown];
const __attachedTools = __packTools.concat(['n8n']).filter(Boolean).map(String)
  .filter(function (t, i, a) { return a.indexOf(t) === i; });
const __attachedSlugs = __attachedTools.map(__slug);
const __shots = Array.isArray(__pack.evidence) ? __pack.evidence : [];
if (__shots.length) {
  const pb = [];
  pb.push('');
  pb.push('WHAT IS ACTUALLY ATTACHED TO THIS EMAIL. THIS LIST IS THE WHOLE TRUTH.');
  pb.push('The buyer opens the PDF while they are reading the letter. Describing a picture');
  pb.push('that is not in it is worse than attaching nothing, because it reads as a template.');
  pb.push('You may describe THESE and nothing else:');
  __shots.forEach(function (s, i) {
    pb.push('  ' + (i + 1) + '. ' + String(s.line || '').trim());
  });
  pb.push('');
  pb.push('THE ONLY TOOLS THE PICTURES ARE IN: ' + __attachedTools.join(', ') + '.');
  if (__attachedTools.length > 2) {
    pb.push('That is more than one tool on purpose. They did not name one clearly enough to');
    pb.push('build the whole pack inside it, so the pack shows the same pattern standing up in');
    pb.push('each of them. Say that plainly if you use it — the point is that the architecture');
    pb.push('travels, not that we happen to own three logins.');
  }
  pb.push('There are ' + __shots.length + ' pictures, not four and not some other number.');
  pb.push('Do not say how many unless you have counted this list.');
  pb.push('Never say or imply that a screenshot, a picture or the attachment shows any other');
  pb.push('tool. If they named a tool that is not in that list, you may still talk about it —');
  pb.push('what you may not do is claim we are showing them a picture of it.');
  pb.push('Never write the attached screenshot shows X unless X is one of the lines above.');
  pb.push('');
  ctx.push(pb.join(NL));
}

// If we have already done this inside the same tool they are asking about, the cover
// letter should close on it, with the picture. This is the strongest thing we own.
let __refs = [];
try { __refs = ($('Match Reference').first().json.referenceBuilds) || []; } catch (e) { __refs = []; }
// A reference build the pack did not attach is a description with no picture
// behind it. Drop it rather than let the model reach for it.
const __refsAll = __refs.length;
if (__shots.length) {
  __refs = __refs.filter(function (r) {
    return __attachedSlugs.indexOf(__slug(r.tool)) !== -1;
  });
}
// The close used to be gated on a reference build. When Match Reference came
// back empty the letter silently lost its product paragraph, its tool note and
// its banned-wording list, even though a full pack of shots went out with it.
// The pack is enough to write the close, so the pack is what gates it now.
if (__refs.length || __shots.length) {
  const rb = [];
  rb.push('');
  rb.push('IF THEY NAMED A TOOL WE HAVE NOT USED: say so straight up front, in one plain sentence, and');
  rb.push('do not pad it. Then explain why it is not the risk they think: its API sits on the same frame');
  rb.push('as the ones we do hold, the connectors are the easy quarter of a build like this, and after');
  rb.push('doing this long enough the difference from an architect\'s point of view is shoelaces versus');
  rb.push('velcro. The part that actually decides the build is what an agent is allowed to WRITE versus');
  rb.push('only flag, set on day one — an agent that posts to the ledger with no read back will');
  rb.push('eventually post something wrong with total confidence. Then point at the structure in the');
  rb.push('screenshots, which is the part that carries over whatever the tool is called.');
  rb.push('');
  rb.push('WE HAVE BUILT THIS INSIDE THE TOOL THEY ARE ASKING ABOUT');
  rb.push('Close the cover letter with a short paragraph on this, framed as a PRODUCT rather than a demo.');
  rb.push('The frame, in Seth\'s words: again, this needs more conversation, but most of what he builds is');
  rb.push('either fully or partially a product in his catalogue, and theirs closely mirrors <product name>.');
  rb.push('ALWAYS OWN THE PRODUCT. Write my <product name>, never the <product name>. It is his, he built');
  rb.push('it, and the definite article makes it sound like a thing off a shelf that anyone could point at.');
  rb.push('Same everywhere it appears: my Upsell Engine, my reachability audit, my escalation build.');
  rb.push('Then say in one clause what the picture is showing, and close with: and yours would look like');
  rb.push('this, with <their subject> in place of <ours>. It is production ready and already working, so');
  rb.push('say it is similar and definitely buildable — never claim it is a perfect or exact fit.');
  /* LF-BANLIST-START — the checker skips this block; it names the banned wording in order to ban it */
  rb.push('BANNED WORDING, do not write any of these under any circumstances: demonstration, demo,');
  rb.push('demo data, test account, my own account rather than a client, not a named client, or any');
  rb.push('bracketed placeholder such as IMAGE LINK. Never write the words image link at all.');
  rb.push('The picture is attached to the email. It does not get announced, linked, or placeheld.');
  /* LF-BANLIST-END */
  if (__pack.product_name) {
    rb.push('');
    // The catalogue stores it as "The Upsell Engine". Handing that over with
    // "put my in front of it" produced "it is my The Upsell Engine" in a letter
    // that shipped. The article belongs to the table, not to the sentence.
    rb.push('THE PRODUCT THIS ONE IS. Use this name, not one you invent, and put my in front of it: my '
            + String(__pack.product_name).replace(/^\s*(?:the|an?)\s+/i, ''));
    if (__pack.evidence_open) { rb.push('   What it is: ' + __pack.evidence_open); }
    if (__pack.substitution_note) { rb.push('   Say this about the tool it is shown in: ' + __pack.substitution_note); }
    if (__pack.direction_note) { rb.push('   This is not a carbon copy, so say: ' + __pack.direction_note); }
    if (__pack.stack_note) { rb.push('   On what it connects to: ' + __pack.stack_note); }
    if (__pack.gap_notice) { rb.push('   Known gap, handle it honestly rather than papering over it: ' + __pack.gap_notice); }
  }
  if (__shots.length && !__refs.length) {
    rb.push('');
    rb.push('There is no separate reference build to draw on, so the paragraph is written from the');
    rb.push('attached pack above and nothing else. Describe one of those pictures, by what it shows.');
  }
  if (__refsAll && !__refs.length) {
    rb.push('A reference build scored against this brief but its picture is NOT in the attachment,');
    rb.push('so it has been withheld from you on purpose. Do not go looking for it.');
  }
  __refs.forEach(function (r, i) {
    rb.push('');
    rb.push((i + 1) + '. ' + r.headline + '  [tool: ' + r.tool + ']');
    rb.push('   What we did: ' + r.what_we_did);
    rb.push('   What the picture shows: ' + r.what_it_shows);
    if (r.sample_note) { rb.push('   The exact line it wrote onto the record: ' + r.sample_note); }
    if (r.image) { rb.push('   (its picture is attached to the email — never write a link, a URL or a placeholder for it)'); }
    if (r.tool_named_in_brief) { rb.push('   They named this tool in their brief, so lead with it.'); }
  });
  rb.push('');
  ctx.push(rb.join(NL));
}

const payload = {
  model: 'claude-fable-5',
  // 16,000 was not a budget for the answer, it was a budget for the answer AND
  // the thinking. On the hardest posting in the set — a four thousand character
  // brief with a $400 ceiling against our $2,500 floor — the model spent all
  // 16,000 on thinking and returned content of type thinking and nothing else.
  // stop_reason came back max_tokens, Parse Outputs threw "the model returned no
  // text", and the same posting failed the same way twice. That is not a flake,
  // it is a ceiling. The letter needs room left over after the thinking is done.
  max_tokens: 32000,
  system: TEMPLATE + NL + NL + String(j.groundingBlock || "") + NL + NL + CHANNEL_RULES + NL + NL + PROOF_BLOCK + NL + NL + OUTPUT_CONTRACT,
  messages: [{ role: 'user', content: ctx.join(NL) }]
};
// The forge already learns what access each shape needs and stores it on the
// shapes row. Reading it back here means the proposal states what we need from
// the client up front, instead of discovering it after the work is sold.
var __shapes = [];
try { __shapes = $('Read Shapes (Cockpit)').all().map(function (i) { return i.json || {}; }); } catch (e) { __shapes = []; }
var __sh = String(j.shape || j.shape_class || j.shapeClass || '').trim().toLowerCase();
var __match = __shapes.filter(function (r) { return String(r.shape || '').trim().toLowerCase() === __sh && __sh; })[0];
var __access = __match ? String(__match.access_list || '').trim() : '';
if (__access) {
  payload.system = payload.system + NL + NL +
    'WHAT WE NEED TO GET STARTED. The shape library records that this kind of work needs the access below. Include a short section in the proposal naming each item plainly, say why it is needed in one clause, and say that the client creates it in their own account and can revoke it at any time. Do not imply we will proceed without it.' + NL + __access;
}
return [{ json: Object.assign({}, j, { payload: payload, templateVersion: TEMPLATE_VERSION, channel: CHANNEL, access_list: __access }) }];
})();
const __clean = (v) => typeof v === 'string'
  ? v.replace(/https?:\/\/(?:www\.)?launchforte\.com\/[^\s'"`)\]]*/gi, '(attached)')
  : v;
const __walk = (o) => {
  if (Array.isArray(o)) return o.map(__walk);
  if (o && typeof o === 'object') { const c = {}; for (const k in o) c[k] = __walk(o[k]); return c; }
  return __clean(o);
};
const __w = __walk(__out);
// Append the pricing brief and the proof block to the SYSTEM PROMPT, by name.
// This used to append to whichever top-level string happened to be the longest,
// which meant the target moved the moment the payload gained a field — and the
// payload is about to gain the job post back. A brief that lands on a random
// key is a brief the model may never read. The old behaviour survives only as a
// fallback for a payload with no system prompt at all.
(function () {
  var a = Array.isArray(__w) ? __w : [__w];
  for (var i = 0; i < a.length; i++) {
    var o = a[i] && a[i].json ? a[i].json : a[i];
    if (!o || typeof o !== 'object') continue;
    if (o.payload && typeof o.payload.system === 'string') {
      o.payload.system = o.payload.system + __PRICING_BRIEF + __PROOF;
      o.pricing_total = __p.tot; o.pricing_class = __p.k; o.brief_target = 'payload.system';
      continue;
    }
    var bk = null, bl = 0;
    for (var kk in o) { if (typeof o[kk] === 'string' && o[kk].length > bl) { bl = o[kk].length; bk = kk; } }
    if (bk && bl > 400) {
      o[bk] = o[bk] + __PRICING_BRIEF + __PROOF;
      o.pricing_total = __p.tot; o.pricing_class = __p.k; o.brief_target = bk;
    }
  }
})();
return __w;
