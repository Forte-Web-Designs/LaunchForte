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
// The pack only ever draws from the tool being shown, the far side of the seam
// when they named two, and our own n8n canvases.
var __packTools = [__pk.evidence_tool_shown, __pk.seam_shown].filter(Boolean);
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

var __wrong = [];
__sentences(letter).forEach(function (s) {
  if (!__CLAIM.test(s)) return;
  __TOOLS.forEach(function (p) {
    if (p[0].test(s) && __shownSlugs.indexOf(p[1]) === -1 && __wrong.indexOf(p[1]) === -1) {
      __wrong.push(p[1]);
    }
  });
});
if (__wrong.length) {
  hard.push('The letter says the attachment shows ' + __wrong.join(', ') +
    '. The pack is in ' + (__packTools.length ? __packTools.join(' and ') : 'nothing') +
    ', so that picture is not in the email. Describe what was attached or attach what was described.');
}
if (!__shotCount && __CLAIM.test(letter)) {
  hard.push('The letter refers to an attachment and nothing was attached.');
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
