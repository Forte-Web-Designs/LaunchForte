/* ---------------------------------------------------------------------------
   LF-AUDIT-EVIDENCE-START — spliced into the Audit node by auditpatch.py.

   Two holds, both from real sends on Aug 8 2026.

   1. THE ATTACHMENT MUST MATCH THE CLAIM.
      Seth: "the pdf on this one doesnt match what youre saying. theres no
      klaviyo in those pdfs." Two nodes pick evidence and they were never
      reconciled: Match Reference scores its own table and hands the model a
      build to describe, while Pick the evidence to attach independently picks
      the shots that go in the PDF. On a Shopify plus Klaviyo posting the letter
      described a Klaviyo screenshot that was not in the attachment. The buyer
      opens the PDF while they are reading, so this one is found every time.

   2. LINKS ARE A CONTRACT THING, NOT A CHAT THING.
      Seth: "you cant send links until we are under contract. on upwork its not
      a matter of just getting into chat, you have to be under contract."
      A letter promised store links "over chat once you reply". Getting a reply
      is not the unlock, so that is a promise the platform will not let us keep.

   The prompt asks for both. Parse Outputs repairs both. This is the floor under
   the two of them, because a wrong claim about our own evidence is the one
   thing a buyer can check in ten seconds.
   --------------------------------------------------------------------------- */
var __pk = {};
try { __pk = $('Pick the evidence to attach').first().json || {}; } catch (e) { __pk = {}; }
var __slug = function (s) { return String(s || '').toLowerCase().replace(/[^a-z0-9]/g, ''); };
// The pack sets its own width now, so read the list it published. The two
// scalars are the old fixed shape, kept only so a run generated before the
// variable-width pack still audits instead of flagging every tool as unshown.
var __packTools = (Array.isArray(__pk.evidence_tools_shown) && __pk.evidence_tools_shown.length
  ? __pk.evidence_tools_shown
  : [__pk.evidence_tool_shown, __pk.seam_shown]).filter(Boolean);
var __shownSlugs = __packTools.map(__slug).concat(['n8n']);
var __shotCount = Number(__pk.evidence_count || 0);

// Word-boundary matches only. A substring test flags "closely" as Close and
// "instantly" as Instantly, and a checker that cries wolf gets switched off.
var __TOOLS = [
  [/\bgo\s?high\s?level\b|\bghl\b/i, 'gohighlevel'], [/\bhubspot\b/i, 'hubspot'],
  [/\bpipedrive\b/i, 'pipedrive'], [/\bshopify\b/i, 'shopify'],
  [/\bquickbooks\b|\bqbo\b/i, 'quickbooks'], [/\bstripe\b/i, 'stripe'],
  [/\bmonday\.?com\b/i, 'monday'], [/\bactivecampaign\b/i, 'activecampaign'],
  [/\bzapier\b/i, 'zapier'], [/\btwilio\b/i, 'twilio'], [/\bairtable\b/i, 'airtable'],
  [/\binstantly\.ai\b/i, 'instantly'], [/\bklaviyo\b/i, 'klaviyo'],
  [/\bsalesforce\b/i, 'salesforce'], [/\bmailchimp\b/i, 'mailchimp'],
  [/\bcalendly\b/i, 'calendly'], [/\bzoho\b/i, 'zoho'], [/\bxero\b/i, 'xero'],
  [/\bwordpress\b/i, 'wordpress'], [/\bwebflow\b/i, 'webflow'], [/\basana\b/i, 'asana'],
  [/\bclickup\b/i, 'clickup'], [/\btrello\b/i, 'trello'], [/\bintercom\b/i, 'intercom'],
  [/\bzendesk\b/i, 'zendesk'], [/\bsmartlead\b/i, 'smartlead'], [/\bgorgias\b/i, 'gorgias'],
  [/\brecharge\b/i, 'recharge'], [/\bshipstation\b/i, 'shipstation'],
  [/\bfreshbooks\b/i, 'freshbooks'], [/\bnetsuite\b/i, 'netsuite'],
  [/\bgong\.io\b|\bgong\b/i, 'gong'], [/\bslack\b/i, 'slack'], [/\bnotion\b/i, 'notion']
];
var __CLAIM = /\b(attach\w*|screenshot\w*|picture|pictures|shot|shots|image|images|pdf|pack)\b/i;
var __sentences = function (t) { return String(t || '').split(/(?<=[.!?])\s+/); };

// Naming a tool ANYWHERE in a sentence that also mentions the attachment is not
// the defect. The first cut of this check held a draft over "I synced a
// furniture retailer's Shopify orders into Xero, and the order state work in
// the screenshots runs through the orders API" — a true sentence about a real
// build, with Xero sixty characters away from the word screenshots. A hold that
// fires on honest prose gets switched off, and then it protects nothing.
//
// What is actually wrong is a DEPICTION claim: the attachment is said to show
// the tool. That is a short-range grammatical relation, so it is matched as
// one — the attachment word, a depiction verb, then the tool, all inside the
// span a sentence like that occupies.
var __ATT = '(?:attached|attachment|screenshots?|pictures?|shots?|images?|pdf|pack)';
var __VERB = '(?:shows?|showing|shown|is|are|of|from|in|with)';
// A depiction claim runs until the sentence stops talking about the picture and
// starts talking about Seth. "The screenshots show X, and I have also shipped
// this inside HubSpot" is two claims, and only the first one is about the
// attachment. So cut the sentence at the first I-have/we-built clause that
// comes AFTER the attachment word, then look inside what is left.
//
// After, not anywhere: "From your stack I have shipped in Shopify and Klaviyo,
// and the attached screenshots come from a live Klaviyo build" puts the
// experience clause FIRST, and cutting there would throw away the lie.
var __EXP = /\b(?:i|we)\s+(?:(?:have|had|has|also|already|recently|just|since|once|previously)\s+){0,3}(?:built|build|shipped|ship|did|do|done|ran|run|set|worked|delivered|made|used)\b/i;
var __upToDepiction = function (sentence) {
  var a = sentence.search(new RegExp(__ATT, 'i'));
  if (a < 0) return sentence;
  var tail = sentence.slice(a);
  var e = tail.search(__EXP);
  return e < 0 ? sentence : sentence.slice(0, a + e);
};
var __depicts = function (sentence, toolRe) {
  var t = toolRe.source.replace(/^\\b|\\b$/g, '');
  var scoped = __upToDepiction(sentence);
  // The window is wide because a real caption keeps listing: "the screenshots
  // show the wizard in GoHighLevel, the settings in Instantly, and the consent
  // state in Klaviyo" is one claim about three tools, and the third one is as
  // checkable as the first. The clause cut above is what makes a wide window
  // safe; without it, widening turned every honest experience line into a hold.
  var fwd = new RegExp(__ATT + '\\b[^.!?]{0,25}?\\b' + __VERB + '\\b[^.!?]{0,110}?(?:' + t + ')', 'i');
  var back = new RegExp('(?:' + t + ')[\\w\\s,\'-]{0,25}\\b' + __ATT + '\\b', 'i');
  return fwd.test(scoped) || back.test(sentence);
};

// The sketch is on every run whether or not there is a pack, so "the attached
// sketch shows the shape of it on one page" is always a true sentence. The
// first cut held a draft over exactly that. Take the sketch out of the sentence
// before asking what the attachment is claimed to show.
var __desketch = function (s) {
  return String(s).replace(/\b(?:the\s+)?attached\s+sketch\b/ig, 'SKETCH')
                  .replace(/\bsketch\b/ig, 'SKETCH');
};

var __wrong = [];
__sentences(letter).forEach(function (raw) {
  var s = __desketch(raw);
  if (!__CLAIM.test(s)) return;
  __TOOLS.forEach(function (p) {
    if (__shownSlugs.indexOf(p[1]) !== -1 || __wrong.indexOf(p[1]) !== -1) return;
    if (p[0].test(s) && __depicts(s, p[0])) { __wrong.push(p[1]); }
  });
});
if (__wrong.length) {
  hard.push('The letter says the attachment shows ' + __wrong.join(', ') +
    '. The pack is in ' + (__packTools.length ? __packTools.join(' and ') : 'nothing') +
    ', so that picture is not in the email. Describe what was attached or attach what was described.');
}
// Only a claim about a PICTURE depends on the pack. Everything else that gets
// called an attachment — the sketch, the client pack — ships regardless.
var __SHOTWORD = /\b(screenshots?|pictures?|images?|shots?)\b/i;
if (!__shotCount && __SHOTWORD.test(__desketch(letter))) {
  hard.push('The letter refers to a screenshot and no screenshots were attached.');
}

/* nothing carrying a URL travels before a contract */
var __LINKY = /\b(link|links|url|urls|demo|walkthrough|storefront|store|login|log in|dashboard|screens?|portal|site|page|video|loom|recording|access)\b|\bthe live (?:one|version|link|demo|build|system|thing)\b/i;
var __EARLY = /\b(once|after|when|as soon as|the moment)\b[^.!?]{0,60}\b(you|we|they)\b[^.!?]{0,40}\b(reply|replies|respond|message|chat|connect|talk|interview)\b|\b(over|in|via|through) (?:the )?(chat|messages|dm|dms|inbox|thread)\b|\bin the interview\b/i;
if (CHANNEL === 'upwork') {
  [['cover letter', letter], ['video script', loom]].forEach(function (pair) {
    __sentences(pair[1]).forEach(function (s) {
      if (__LINKY.test(s) && __EARLY.test(s)) {
        hard.push('The ' + pair[0] + ' promises something before we are under contract: "' +
          s.trim().slice(0, 90) + '". On Upwork a link cannot travel on a reply or in chat.');
      }
    });
  });
}
/* LF-AUDIT-EVIDENCE-END */
