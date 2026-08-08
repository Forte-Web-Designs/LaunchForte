#!/usr/bin/env python3
"""
buildnode.py — emit the Cockpit's "Pick the evidence to attach" Code node.

v3. The v2 node baked a fixed list of four files per shape, chosen when the node
was generated. That is why a Pipedrive job said "not covered" and substituted
GoHighLevel the day AFTER we built the whole pattern in Pipedrive: the data was
a snapshot, and the snapshot was stale.

v3 embeds the WHOLE library grouped by shape and tool, and picks at RUN TIME:
  - resolve the shape from the job post (title weighted heavier than body)
  - detect the client's tool
  - if we have that tool inside that shape, build the send from THAT tool
  - if not, pick the best-covered tool, say the substitution out loud, and raise
    a gap notice so the Cockpit can email Seth and queue that build

Regenerate this node whenever the library changes. That is the whole lesson.
"""
import json, os, re

LIB = "/home/claude/evidence-library"
OUT = "/home/claude/cockpit-evidence-node.js"

# shape -> (product, opening line, four beat lines)
# Pull SHAPES out of heroes.py without executing its main()
_src = open("/home/claude/heroes.py").read().replace("\nmain()", "\n# main() suppressed")
_ns = {}
exec(compile(_src, "heroes.py", "exec"), _ns)
SHAPES = _ns["SHAPES"]


# Keywords for run-time shape resolution. Long words score 2, short score 1.
KW = {
"storefront-upsell":["shopify","woocommerce","bigcommerce","ecommerce","e-commerce","product bundle","bundle","upsell","cross-sell","cart","klaviyo","omnisend","recharge","variant","order placed"],
"books-reconciliation":["quickbooks","qbo","xero","netsuite","bookkeep","reconcil","invoice","payout","ledger","accounting","bank feed","month end","chart of accounts","aging","invoices chased"],
"scheduling":["calendar","booking","appointment","schedule","acuity","calendly","janeapp","no-show","show rate","reminder","availability","booked appointment"],
"reporting":["report","dashboard","analytics","kpi","metric","attribution","bigquery","looker","power bi","tableau","executive-ready","roas","cost per lead"],
"system-sync":["two-way","bidirectional","sync between","zapier","make.com","integromat","middleware","etl","field mapping","keep in sync","integration between","real-time sync",
 # How buyers actually say "make these two talk". Almost nobody writes "bidirectional".
 "talk to each other","talking to each other","talk to eachother","speak to each other",
 "connect them","connected to","connect to our","hook up","hooked up","tie together",
 "tied together","push to","pushed to","pull from","feed into","feeds into","flow into",
 "talking","retyp","re-typ","rekey","re-key","double entry","double-entry","manual entry",
 "copy and paste between","copying between","two systems","both systems","across systems",
 "single source of truth","one source of truth","stay in sync","out of sync","integrate with"],
"lead-routing":["lead routing","round robin","speed to lead","assign","distribut","inbound lead","response time","sla","lead qualification","mql","sql","lead scoring"],
"data-collection":["intake","form","survey","typeform","jotform","data entry","enrich","scrape","scraping","capture","submission","clean data","landing page","funnel"],
"client-onboarding":["onboard","kickoff","welcome","new client","first 48","checklist","handoff","review request","google review"],
"alerting":["alert","monitor","watchdog","notification","downtime","stall","breaking silently","nothing breaking","escalate when","error handling"],
"stalled-deal-escalation":["stalled","stuck","no movement","overdue","pipeline stage","stage-entry","stage entry","escalation","on hold","proposal pipeline","pipedrive","deal stage","not progressed","reactivated"],
"quote-follow-up":["quote","proposal follow","estimate","cadence","nurture","follow-up sequence","follow up sequence","drip","estimates followed"],
"reactivation":["dormant","win-back","winback","lapsed","churn","re-engage","reactivation","past customer","legacy records"],
"approval-routing":["approval","approve","sign-off","authoris","authoriz","on-hold reason","escalation rules","band"],
"platform-migration":["migrat","replatform","move from","switch from","transfer data","rebuild account","snapshot","import existing"],
"production-takeover":["take over","takeover","inherit","existing system","debug","fix existing","legacy system","undocumented","audit our","cleanup","clean up","cluttered","restructur"],
"voice-agent-intake":["voice ai","voice agent","ai receptionist","ivr","twilio","retell","elevenlabs","vapi","after hours","missed call","call routing","answering service","inbound call"],
"document-assembly":["document","pdf","contract","docusign","pandadoc","merge field","signature","retainer"],
"ai-assistant":["chatbot","chat bot","conversation ai","ai chat","ai agent","llm","gpt","claude","conversational","knowledge base","ai lead qualification","human handoff","ai appointment booking"],
"data-model-architecture":["custom field","data model","schema","property","object","field standard","data quality","custom object"],
"project-ops":["monday.com","monday","clickup","asana","notion","trello","board","subitem","sub-item","workload","capacity","sprint","project template","mirror column","board relation","gantt"],
"ai-research-agent":["perplexity","claude","anthropic","openai","gpt","deep research","research agent","market research","competitor research","summarise sources","summarize sources","cite","citation","rag","retrieval","vector","embedding","agentic","ai agent","agents and","setting up agents","brief","desk research"],
"conversation-design":["conversation design","conversational design","conversation architecture","chatbot copy","chatbot copywriter","bot copy","dialogue","dialog flow","intent","utterance","happy path","fallback message","escalation to human","tone of voice","script the bot","conversation flow","bot persona","review the conversation"],
"messaging-compliance":["a2p","10dlc","dlc","spf","dkim","dmarc","deliverability","sending domain","domain warming","carrier","opt-out","tcpa","can-spam","sender reputation"],
"cold-outreach":["instantly","instantly.ai","smartlead","apollo","cold email","outbound","email infrastructure","mailbox","inbox rotation","sequencer","prospect list"],
}


# Their words -> our answer. Buyers describe the same handful of systems in wildly
# different packaging; this maps the phrasing back to the pattern so the reply
# quotes THEM, not us. Phrases are lifted from real postings.
PAIN = {
"ai-research-agent":[
 ["setting up agents","agents scoped to one job each, with the tools each one is allowed to touch written down"],
 ["doing research","a research pass that keeps its sources, so every claim can be pointed at"],
 ["research","sources fetched and retained, not a summary of what the model already believed"],
 ["perplexity","live retrieval for the facts, and the model only for the writing"],
 ["claude","the model does the reasoning; the grounding and the handoff live outside it"],
 ["cite","a citation on every claim, and a refusal where there is nothing to cite"],
 ["deep research","depth measured in sources actually read, not in output length"]],
"conversation-design":[
 ["conversation architecture","the intent map, the escalation path, and what happens on the turn nobody scripted"],
 ["conversation design","designed around the failure turns rather than the greeting"],
 ["chatbot copywriter","copy written against a structure, so the tone survives the edge cases"],
 ["reviewing","an audit of where it currently guesses, and what it should say instead"],
 ["escalation","a handoff that carries the whole conversation, not a fresh start for the human"],
 ["intent","intents that map to actions the bot is actually allowed to take"],
 ["ghl","built where it will live, so the goals and triggers are the real ones"]],
"stalled-deal-escalation":[
 ["not progressed","a watcher on time-in-stage, so a quiet deal surfaces before it goes cold"],
 ["on hold","each on-hold reason routed to its own next step, not one dead bucket"],
 ["stage-entry","entry and exit criteria enforced by the system, so a stage cannot sit empty"],
 ["stage entry","entry and exit criteria enforced by the system, so a stage cannot sit empty"],
 ["escalation","an escalation ladder: owner, then manager, then principal"],
 ["overdue","overdue items named and owned rather than reported in aggregate"],
 ["stalled","a stalled-deal sweep that runs whether or not anyone remembers to look"],
 ["reactivated","consistent handling of won, lost, stalled and reactivated"],
 ["cluttered","a cleanup pass first: dead stages, unused fields, duplicate contacts"],
 ["follow-up cadence","a cadence that stops the moment they reply"]],
"lead-routing":[
 ["speed to lead","first touch inside five minutes, measured per owner"],
 ["round robin","round-robin assignment with an SLA timer that reassigns on silence"],
 ["lead qualification","qualification before routing, so the best leads reach the best closer"],
 ["missed call","missed-call text-back within sixty seconds"],
 ["response time","response time tracked per owner, because that is what changes behaviour"],
 ["mql","lifecycle transitions driven by rules rather than opinion"]],
"books-reconciliation":[
 ["reconcil","payouts matched to the cent; only genuine exceptions reach a person"],
 ["invoices chased","receivables chased on their own schedule"],
 ["bookkeep","the repeated ruling encoded once as a rule instead of every week"],
 ["month end","an aged-discrepancy report so nothing rots past thirty days"]],
"scheduling":[
 ["no-show","a no-show recovery path, because that slot is paid-for demand"],
 ["show rate","reminders at 24 hours and 1 hour, then a recovery branch"],
 ["booking","booking, confirmation and reminders as one sequence"],
 ["appointment","appointment automation that survives a reschedule"]],
"reporting":[
 ["attribution","source data that reconciles against the analytics rather than contradicting it"],
 ["executive-ready","one page that answers the three questions an owner actually asks"],
 ["dashboards are static","live filterable views instead of a manual snapshot"],
 ["cost per","cost per booked outcome, not cost per click"],
 ["reconciliation math","every rate printed with its N, and nothing compared below the threshold"]],
"system-sync":[
 ["two-way","an echo gate, so our own write coming back does not start a loop"],
 ["real-time","queue and retry when the far side is unreachable, never silent loss"],
 ["field mapping","explicit field mapping with a drift report for records that disagree anyway"],
 ["troubleshooting","the failure modes found and documented before they are inherited"]],
"data-collection":[
 ["scrap","extraction that refuses malformed input rather than writing half a record"],
 ["intake","validation, dedupe, then a clean record — in that order"],
 ["duplicate","deduplication on a stable key, never on name"],
 ["exception handling","exception handling for login failures and unexpected shapes"],
 ["landing page","capture wired to the CRM with real field mapping"]],
"project-ops":[
 ["board-relation","relations audited so widgets stop silently dropping items"],
 ["template","a template system, so a launch is not rebuilt from scratch"],
 ["subitem","a standardised subitem structure applied across boards"],
 ["workload","a workload view that makes capacity visible"],
 ["native","native automations only — no external middleware to maintain"],
 ["sprint","a live sprint view rather than a manual snapshot"]],
"messaging-compliance":[
 ["10dlc","A2P brand and campaign registration, including how rejections get handled"],
 ["dkim","SPF, DKIM and DMARC on a dedicated sending domain"],
 ["deliverability","domain warming on a ramp rather than a launch"],
 ["opt-out","consent and opt-out handling per channel"]],
"ai-assistant":[
 ["ai agent","an assistant that answers from a real knowledge base and refuses when it should"],
 ["human handoff","a human handover path with the context attached"],
 ["qualification","qualification and booking handled before a person is involved"],
 ["knowledge base","the knowledge source the bot is actually trained on"]],
"voice-agent-intake":[
 ["after hours","calls answered after hours instead of going to voicemail"],
 ["voice ai","a voice agent with persona, guardrails and an opt-out path"],
 ["call routing","routing to the right person with the call context attached"]],
"quote-follow-up":[
 ["estimates followed","follow-up that runs until it closes or dies"],
 ["quote","a cadence that checks for a reply before every touch"],
 ["nurture","escalating channel: email, then SMS, then a human call task"]],
"reactivation":[
 ["legacy records","a segmented recovery campaign against the dormant base"],
 ["dormant","dormancy measured per customer, not a blanket ninety days"],
 ["win-back","one honest win-back, never a series"]],
"production-takeover":[
 ["cluttered","a cleanup and restructure pass before anything new is built"],
 ["audit","observed behaviour mapped against documented behaviour first"],
 ["existing","nothing changed in week one except the map"],
 ["debug","the misfires, loops and duplicate sends traced to cause"]],
"approval-routing":[
 ["approval","auto-approve inside a band, route the rest by rule"],
 ["sign-off","every auto-approval recording who and why"]],
"platform-migration":[
 ["migrat","reversible batches; counts reconciled before anything commits"],
 ["snapshot","a reusable snapshot so the next build starts from the last one"]],
"storefront-upsell":[
 ["bundle","companion logic that stays silent when there is no honest pairing"],
 ["upsell","one suggestion, never a second"]],
"client-onboarding":[
 ["onboard","the first forty-eight hours as a sequence, not an improvisation"],
 ["review","review requests gated behind a satisfaction check"]],
}

# Nobody buys a tool. They buy a tool doing something that reaches ANOTHER tool,
# and the seam between the two is where the work actually is. This table is what
# lets a reply say "you said Airtable, which means you also have a CRM, and the
# hard part is the boundary" instead of talking about Airtable in a vacuum.
#
# partners : the systems this pattern normally sits between, most common first
# seam     : what crosses the boundary, and why that crossing is the hard part
STACK = {
"stalled-deal-escalation": dict(
  partners=["ghl", "hubspot", "pipedrive", "monday", "airtable"],
  seam="The CRM knows the deal stalled. It does not know who to chase, on what ladder, or how to prove it chased. That state has to live somewhere the CRM cannot hold it."),
"lead-routing": dict(
  partners=["ghl", "hubspot", "twilio", "airtable", "monday"],
  seam="The form is in one system, the owner roster in another, and the SLA clock in neither. The clock is the integration."),
"books-reconciliation": dict(
  partners=["quickbooks", "stripe", "shopify", "airtable"],
  seam="The payout processor and the ledger disagree by design — fees, timing, refunds. Reconciliation is not a report, it is a translation layer between two systems that count differently."),
"storefront-upsell": dict(
  partners=["shopify", "klaviyo", "stripe", "airtable"],
  seam="The store knows the order. The email tool knows the person. The companion mapping belongs to neither, so it needs a home that both can read."),
"scheduling": dict(
  partners=["ghl", "twilio", "hubspot", "airtable"],
  seam="The calendar owns the slot, the messaging system owns the reminder, and the no-show recovery has to survive both. A reschedule that only updates one side is the classic failure."),
"reporting": dict(
  partners=["hubspot", "ghl", "airtable", "google-sheets", "shopify", "stripe"],
  seam="Every source counts a lead slightly differently. The reporting layer is where you decide, once and in writing, whose definition wins."),
"system-sync": dict(
  partners=["hubspot", "airtable", "shopify", "ghl", "pipedrive", "monday"],
  seam="This pattern IS the seam. Two systems, one record, and an echo gate so our own write coming back does not start a loop at 3am."),
"client-onboarding": dict(
  partners=["ghl", "hubspot", "monday", "airtable", "google-sheets"],
  seam="Won in the CRM has to become tasks in the project tool, a folder somewhere, and an intake the client actually returns. Three systems, one moment."),
"data-collection": dict(
  partners=["airtable", "ghl", "hubspot", "google-sheets", "shopify"],
  seam="The form and the system of record are almost never the same tool. Everything expensive happens in the gap: duplicates, half-records, and fields that mean different things on each side."),
"quote-follow-up": dict(
  partners=["ghl", "pipedrive", "hubspot", "instantly"],
  seam="The quote lives in the CRM and the reply lands in a mailbox. Stopping the cadence means the mailbox has to be able to reach back into the CRM."),
"reactivation": dict(
  partners=["ghl", "shopify", "hubspot", "klaviyo", "airtable"],
  seam="Dormancy is a purchase-history question and the message is a marketing-tool question. Neither system holds both halves."),
"approval-routing": dict(
  partners=["pipedrive", "hubspot", "monday", "airtable"],
  seam="The request arrives in one place and the authority to approve lives in another. The audit trail has to span both or the band is unauditable."),
"alerting": dict(
  partners=["airtable", "zapier", "google-sheets", "twilio", "ghl"],
  seam="The thing that breaks and the thing that tells you are never the same system, and the watchdog must not depend on the system it is watching."),
"platform-migration": dict(
  partners=["ghl", "hubspot", "pipedrive", "airtable", "shopify"],
  seam="Migration is two data models arguing. The mapping decision — which field becomes which property — is the entire job; the import is the easy part."),
"production-takeover": dict(
  partners=["n8n", "zapier", "ghl", "hubspot", "airtable"],
  seam="An inherited system spans tools nobody documented together. Week one is drawing the map across all of them before touching any of them."),
"voice-agent-intake": dict(
  partners=["twilio", "ghl", "airtable", "hubspot"],
  seam="The call arrives at the phone system, the context lives in the CRM, and the booking is in the calendar. The caller experiences one thing; it is three."),
"document-assembly": dict(
  partners=["ghl", "hubspot", "google-sheets", "airtable", "stripe"],
  seam="Every merge field is a read from another system. A document that assembles before its source has answered is how blanks reach a client."),
"ai-assistant": dict(
  partners=["ghl", "hubspot", "airtable", "instantly"],
  seam="The model is not the product. The knowledge source it is grounded in, and the CRM it hands off to, are the product — and both live outside the model."),
"data-model-architecture": dict(
  partners=["hubspot", "airtable", "pipedrive", "ghl"],
  seam="The schema has to hold for every system that writes into it. A property that only makes sense in one tool is the one that breaks the reporting later."),
"project-ops": dict(
  partners=["monday", "clickup", "airtable", "hubspot", "ghl"],
  seam="The board is downstream of the CRM and upstream of the invoice. Work arriving without its deal context is what makes a board go stale."),
"messaging-compliance": dict(
  partners=["ghl", "twilio", "instantly", "hubspot"],
  seam="Registration lives with the carrier, the sending happens in the CRM, and neither tells the other when clearance lapses. Silence is the failure mode."),
"ai-research-agent": dict(
  partners=["n8n", "airtable", "hubspot", "google-sheets"],
  seam="The model is a renter, not an owner. The sources live on the web, the output has to land in something a person opens, and the agent is only the middle."),
"conversation-design": dict(
  partners=["ghl", "hubspot", "twilio", "airtable"],
  seam="The conversation happens in the messaging tool, the answer comes from a knowledge base, and the handoff lands in the CRM. Three systems, and the client only ever sees the seam when it fails."),
"cold-outreach": dict(
  partners=["instantly", "hubspot", "ghl", "airtable"],
  seam="The sequencer owns the send and the CRM owns the truth about whether that person is already a customer. Emailing an existing client is the mistake that costs the account."),
}


TOOL_WORDS = {
 "gohighlevel":"ghl","ghl":"ghl","highlevel":"ghl","hubspot":"hubspot","shopify":"shopify",
 "stripe":"stripe","quickbooks":"quickbooks","qbo":"quickbooks","zapier":"zapier","twilio":"twilio",
 "pipedrive":"pipedrive","monday.com":"monday","monday":"monday","activecampaign":"activecampaign",
 "xero":"xero","salesforce":"salesforce","airtable":"airtable","make.com":"make","zoho":"zoho",
 "klaviyo":"klaviyo","netsuite":"netsuite","clickup":"clickup","instantly":"instantly",
 "close.com":"close","notion":"notion","n8n":"n8n",
 # Added Aug 8 2026 after counting 2,281 A/B graded postings. The ones we now
 # hold shots for, plus the ones buyers name often enough that the letter should
 # be able to say the name back to them even when we do not hold it yet.
 "slack":"slack","calendly":"calendly","acuity":"calendly","supabase":"supabase",
 "vapi":"vapi","retell":"retell","elevenlabs":"elevenlabs","eleven labs":"elevenlabs",
 "wordpress":"wordpress","woocommerce":"wordpress","webflow":"webflow","wix":"wix",
 "squarespace":"squarespace","smartlead":"smartlead","apollo.io":"apollo",
 "gorgias":"gorgias","mailchimp":"mailchimp","looker":"looker","power bi":"powerbi",
 "docusign":"docusign","pandadoc":"pandadoc","typeform":"typeform","jotform":"jotform",
 "asana":"asana","trello":"trello","jira":"jira","intercom":"intercom","zendesk":"zendesk",
 "freshbooks":"freshbooks","keap":"keap","infusionsoft":"keap","whatsapp":"whatsapp",
}

PRETTY = {"ghl":"GoHighLevel","hubspot":"HubSpot","shopify":"Shopify","stripe":"Stripe",
 "quickbooks":"QuickBooks","zapier":"Zapier","twilio":"Twilio","pipedrive":"Pipedrive",
 "monday":"Monday.com","activecampaign":"ActiveCampaign","n8n":"n8n","xero":"Xero",
 "salesforce":"Salesforce","airtable":"Airtable","make":"Make","zoho":"Zoho","klaviyo":"Klaviyo",
 "netsuite":"NetSuite","clickup":"ClickUp","instantly":"Instantly.ai","close":"Close","notion":"Notion",
 "slack":"Slack","calendly":"Calendly","supabase":"Supabase","vapi":"Vapi","retell":"Retell",
 "elevenlabs":"ElevenLabs","wordpress":"WordPress","webflow":"Webflow","wix":"Wix",
 "squarespace":"Squarespace","smartlead":"Smartlead","apollo":"Apollo","gorgias":"Gorgias",
 "mailchimp":"Mailchimp","looker":"Looker Studio","powerbi":"Power BI","docusign":"DocuSign",
 "pandadoc":"PandaDoc","typeform":"Typeform","jotform":"Jotform","asana":"Asana",
 "trello":"Trello","jira":"Jira","intercom":"Intercom","zendesk":"Zendesk",
 "freshbooks":"FreshBooks","keap":"Keap","whatsapp":"WhatsApp"}


# A pattern can be a genuinely distinct ASK while the proof already sits under a
# sibling. A conversation-design job and an ai-assistant job get different words,
# different pain and a different product name — but the GoHighLevel Conversation
# AI screenshots ARE the conversation architecture, and filing a second copy of
# them under a new folder would be padding. So: separate story, borrowed shots.
ALIAS = {"conversation-design": "ai-assistant"}


def main():
    man = json.load(open(os.path.join(LIB, "manifest.json")))
    lib = {}
    for i in man["images"]:
        if i["shape"].startswith("_"):
            continue
        lib.setdefault(i["shape"], {}).setdefault(i["tool"], []).append(
            {"f": i["file"], "v": i["view"]})

    # A shape that borrows its shots keeps its OWN story and points at the
    # sibling's evidence. Separate ask, separate words, same proof.
    for alias, source in ALIAS.items():
        if source in lib and alias not in lib:
            lib[alias] = lib[source]

    story = {s: {"product": v["product"], "open": v["open"], "beats": v["beats"]}
             for s, v in SHAPES.items() if s in lib}
    # shapes present in the library but with no story yet — still usable, generic lines
    for s in lib:
        if s not in story:
            story[s] = {"product": s.replace("-", " ").title(), "open": "",
                        "beats": ["Here's the system.", "This is the logic underneath it.",
                                  "Running inside the tool.", "And what it produces."]}

    # ---- keyword specificity -------------------------------------------
    # Length was standing in for importance: any word over 8 characters scored
    # 2, everything else 1. That treats "quickbooks" and "conversational" as
    # equals, and it is why a UK accountancy posting tied 5-5 between
    # books-reconciliation and ai-research-agent. Books hit three concrete
    # nouns — quickbooks, xero, accounting. The research agent hit four generic
    # AI words — claude, openai, "ai agent", "agents and" — that appear in half
    # the AI-adjacent postings on the market. Same score, completely different
    # quality of evidence.
    #
    # So weight by how much a word NARROWS the field:
    #   claimed by more than one pattern  -> halved, it does not discriminate
    #   a tool we actually hold shots of  -> +1, naming your stack is a fact
    from collections import Counter
    _claims = Counter(w for words in KW.values() for w in set(words))
    _toolwords = set(TOOL_WORDS.keys())
    WEIGHT = {}
    for _words in KW.values():
        for _w in _words:
            if _w in WEIGHT:
                continue
            _v = 2.0 if len(_w) > 8 else 1.0
            if _claims[_w] > 1:
                _v *= 0.5
            if _w in _toolwords:
                _v += 1.0
            WEIGHT[_w] = _v

    js = """// Pick the evidence to attach  (v3 — runtime tool selection)
// ---------------------------------------------------------------------------
// Resolves SHAPE first, then picks the attachments from the CLIENT'S OWN TOOL
// when we have it. v2 baked a fixed four files per shape and went stale the day
// a new tool was built — a Pipedrive job substituted GoHighLevel the morning
// after we built it in Pipedrive. This picks at run time instead.
//
// Never attaches more than 4. Never mixes two CRMs. The n8n canvas is the one
// permitted companion because it is the architecture layer, not a rival tool.
// A tool-miss NEVER returns empty: it substitutes, says so out loud, and raises
// a gap notice so the Cockpit can tell Seth and queue that build.
// ---------------------------------------------------------------------------

const LIB    = %s;
const STORY  = %s;
// Where the generic picker cannot know which shot the LINE is describing, pin it.
// (beat 3 = their world, beat 4 = the result.) Same table SEND-THIS.md uses, so
// the Cockpit and the send-list never disagree about which shot a caption names.
const HINT   = %s;
// What each pattern normally sits BETWEEN. Nobody wants one tool doing one
// thing; they want a tool reaching another tool, and the seam is the work.
const STACK  = %s;
const KW     = %s;
// How much each word narrows the field. See buildnode.py for how it is derived.
const WEIGHT = %s;
const PAIN   = %s;
const TOOLS  = %s;
const PRETTY = %s;

// Pack size is decided per posting now, in section 4a. These are the walls.
const PACK_MIN = 3, PACK_MAX = 8;
const BASE = 'https://launchforte.com/built-with/shots/';
const pretty = t => PRETTY[t] || (t ? t[0].toUpperCase() + t.slice(1) : t);

const input = $json || {};

// ---- 0a. find the posting, even when the payload has lost it --------------
// v3.2, written after dumping $json from a real execution rather than guessing.
// The Cockpit's "Match Product" node joins the run against a stored shapes
// table and does NOT carry $json through, so by the time the payload reaches
// here the job posting is gone entirely — no jobPost, no jobTitle, none of the
// twenty field names this node reads. What arrives is a row from that table,
// carrying a `shape` from a record written days earlier.
//
// This node then honoured that handed-in shape and skipped its own matching
// (match_confidence came back "given", meaning nothing was ever scored). That
// is the whole bug: three unrelated postings returned the same four
// voice-agent-intake shots because none of them were ever read. The matcher
// was not wrong. It was never consulted.
//
// So: if $json has no posting in it, walk back up the workflow and take it
// from the node that still has it. Read-only, wrapped, and it degrades to the
// old behaviour if none of them resolve.
const POST_SOURCES = ['Ground Match', 'Merge Context', 'Read Job Row', 'Cockpit Form'];
const POSTING_KEYS = ['jobPost', 'job_post', 'jobDescription', 'job_description',
                      'posting', 'post', 'description', 'brief', 'text', 'body',
                      'content', 'details', 'requirements', 'scope', 'notes',
                      'message', 'summary', 'transcript'];
const carriesPosting = (o) => !!o && POSTING_KEYS.some(
  f => typeof o[f] === 'string' && o[f].trim().length > 40);

let src = input, postSource = '$json', postingRecovered = false;
if (!carriesPosting(input)) {
  for (const nm of POST_SOURCES) {
    try {
      const j = $(nm).first().json;
      if (carriesPosting(j)) {
        // input LAST so anything the current payload asserts still wins.
        src = Object.assign({}, j, input);
        postSource = nm; postingRecovered = true;
        break;
      }
    } catch (e) { /* node not in this branch, or not executed — keep looking */ }
  }
}

const title = [src.jobTitle, src.title].filter(Boolean).join(' ').toLowerCase();

// ---- 0. the posting, and ONLY the posting ---------------------------------
// v3.1. This used to concatenate twenty candidate field names into one haystack
// on the theory that missing a field name was the expensive failure. The
// opposite was true. Three unrelated postings — a GoHighLevel 10DLC job, a
// Pipedrive job and an Airtable job — all came back with the identical four
// voice-agent-intake shots, because something large and CONSTANT was riding in
// one of those twenty fields on every run. A 12,000-character constant beats a
// 900-character job post on raw keyword count every time, so the same shape won
// every time. The library was right, the shots were hosted, the PDF built, and
// the evidence was still wrong.
//
// So: read ONE posting field, chosen by priority, not all of them glued
// together. Enrichment fields (reason, angle, category, skills, toolsSeen) are
// our own words about the job, not the buyer's — they inform TOOL detection but
// they never vote on the shape.
//
// PRIMARY are fields that only ever hold a job posting. SECONDARY are fields
// that usually hold the posting but sometimes hold something else, so they are
// only consulted when no primary field arrived.
const PRIMARY   = ['jobPost', 'job_post', 'jobDescription', 'job_description',
                   'posting', 'post', 'description'];
const SECONDARY = ['brief', 'text', 'body', 'content', 'details',
                   'requirements', 'scope', 'notes', 'message', 'summary', 'transcript'];
// Fields we read for TOOL NAMES only. Never scored for shape.
const TOOLHINT  = ['toolsSeen', 'tools_seen', 'skills', 'category', 'tools', 'stack'];

// A field carrying OUR OWN text — the assembled prompt, the playbook, a
// previous run's output, the evidence library itself — is not the buyer
// describing their problem. It is us, echoed back, and it names every pattern
// and every tool we hold, which is exactly why it drowns the posting. Any field
// that reads like our side of the conversation is dropped, loudly, into
// evidence_input_fields so the next execution says so instead of guessing.
const SELF = ['launchforte', 'built-with/shots', 'built-with/packs',
              'prompt of record', 'evidence pack', 'pick the evidence to attach',
              'substitution_note', 'gap_notice', 'evidence_shape'];
const SHAPE_SLUGS = Object.keys(KW);
const looksLikeOurs = (s) => {
  for (const m of SELF) if (s.indexOf(m) !== -1) return true;
  // Three or more of our own pattern slugs in one field is our catalogue, not a
  // job post. A buyer does not write "books-reconciliation".
  let n = 0;
  for (const slug of SHAPE_SLUGS) if (s.indexOf(slug) !== -1 && ++n >= 3) return true;
  return false;
};

// Guards against one long field swamping the scoring even when it IS a posting.
const MAX_POST = 12000;

const fieldReport = [];
const readField = (name) => {
  const v = src[name];
  if (typeof v !== 'string') return null;
  const s = v.toLowerCase().trim();
  if (!s) return null;
  const ours = looksLikeOurs(s);
  fieldReport.push({ field: name, chars: v.length, ours: ours, used: false });
  return ours ? null : s;
};

// Read EVERY candidate, always, so the trace is complete even when the first
// field read is the one used. A trace that only lists the winner cannot tell
// you what it beat.
const clean = {};
for (const f of PRIMARY.concat(SECONDARY, TOOLHINT)) { const s = readField(f); if (s) clean[f] = s; }

let postField = null, post = '';
const pickFrom = (list) => {
  for (const f of list) {
    const s = clean[f];
    if (s && s.length > post.length) { post = s; postField = f; }
  }
};
pickFrom(PRIMARY);
if (!post) pickFrom(SECONDARY);
// Nothing survived the filter — fall back to the longest clean field of any
// kind rather than resolving on the title alone. Fail soft: a shape resolved
// from a thin signal is recoverable, an empty send is not.
if (!post) pickFrom(TOOLHINT);
if (post.length > MAX_POST) post = post.slice(0, MAX_POST);
const usedEntry = fieldReport.find(r => r.field === postField);
if (usedEntry) usedEntry.used = true;

// Tool names may be listed somewhere other than the posting body. Reading them
// cannot change the SHAPE — only which tool we show inside it — so this list
// stays wide.
const toolHay = [post].concat(
  TOOLHINT.map(f => src[f]).map(v => Array.isArray(v) ? v.join(' ') : v)
          .filter(v => typeof v === 'string')
          .map(v => v.toLowerCase())
          .filter(v => !looksLikeOurs(v))
).join(' ');

const body = post;
const HAY = (title + ' ' + body).trim();
const TOOL_HAY = (title + ' ' + toolHay).trim();

// Carried on every return path, including the refusals. When the evidence is
// wrong again, this says WHY without needing a separate diagnostic run: which
// field the shape was read from, how long each candidate was, and which ones
// were dropped for carrying our own text. "Verify the thing that would prove
// you wrong" — this is that thing, attached to every execution.
const INPUT_TRACE = {
  post_field: postField,
  post_chars: post.length,
  title_chars: title.length,
  truncated: post.length >= MAX_POST,
  fields_seen: fieldReport,
  dropped_as_ours: fieldReport.filter(r => r.ours).map(r => r.field),
  post_source: postSource,
  posting_recovered_upstream: postingRecovered,
};

// ---- 1. shape: title hits count triple, body once -------------------------
// A shape handed in by an upstream node is a HINT, not a verdict. It used to
// be a verdict, and the verdict came from a stale table row. Score the posting
// on its own words whenever we have them, and let the handed-in shape win only
// when we have nothing of our own to say.
let handed = src.shape || src.build_shape || src.matched_shape || null;
if (handed && !LIB[handed]) handed = null;
let shape = handed;
let ranked = [];
if (HAY) {
  ranked = Object.entries(KW).map(([s, words]) => {
    let n = 0;
    for (const w of words) {
      const weight = WEIGHT[w] !== undefined ? WEIGHT[w] : (w.length > 8 ? 2 : 1);
      if (title.includes(w)) n += weight * 3;
      else if (body.includes(w)) n += weight;
    }
    return { shape: s, score: n };
  }).filter(x => x.score > 0 && LIB[x.shape]).sort((a, b) => b.score - a.score);
  if (ranked.length) shape = ranked[0].shape;
}
// Nothing to read AND a shape handed in: we are trusting a value we cannot
// check. That is exactly how four voice-agent-intake shots got attached to a
// Pipedrive job. Flag it hard.
const shapeUnverified = !!handed && !HAY;

// ---- 2. the client's tools ------------------------------------------------
// Plural on purpose. Almost nobody wants one tool doing one thing — they want a
// tool doing something that reaches another tool, and the seam between the two
// is the part that is actually hard. So detect EVERY tool named, in the order
// the posting emphasises them, and keep the list.
//
// Two tiers, and the difference matters. A tool the BUYER named in their own
// posting is evidence they are in our world. A tool sitting in a category tag
// or a skills list is a marketplace label — it is often our stack echoed back,
// not theirs. The restaurant-menu job proved the cost of conflating them: a
// skills field reading "n8n, Zapier, GoHighLevel" made a graphic-design posting
// look like a tool we know well, cleared the refusal floor, and sent lead-routing
// screenshots to somebody who wanted a dinner menu laid out.
//
// So hint-tier tools may decide WHICH tool's screenshots to show once a shape
// has honestly resolved. They may never decide THAT we have a fit.
const toolsIn = (hay) => {
  const found = [];
  if (!hay) return found;
  const seen = new Set();
  Object.keys(TOOLS)
    .filter(w => hay.includes(w))
    .sort((a, b) => (title.includes(b) ? 1 : 0) - (title.includes(a) ? 1 : 0) || b.length - a.length)
    .forEach(w => { const t = TOOLS[w]; if (!seen.has(t)) { seen.add(t); found.push(t); } });
  return found;
};
let statedTools = toolsIn(HAY);          // the buyer's own words
const hintTools = toolsIn(TOOL_HAY).filter(t => statedTools.indexOf(t) === -1);
const stated = (src.client_tool || src.platform || '').toLowerCase().trim();
// An explicitly-set client_tool is somebody asserting the tool, not a tag.
if (stated) statedTools = [stated, ...statedTools.filter(t => t !== stated)];
// If the buyer named ANY tool, that is the list. Hint-tier tools are only read
// when the posting named none at all — otherwise a skills tag reading
// "GoHighLevel" puts a GoHighLevel screenshot in slot four of a Pipedrive send,
// and tells a research-agent buyer their tool is GHL. Both are lies we would
// have shipped with a straight face.
const toolSource = statedTools.length ? 'posting' : (hintTools.length ? 'hint-fields' : 'none');
let clientTools = statedTools.length ? statedTools : hintTools;
let clientTool = clientTools[0] || '';
// Only a tool the buyer actually named can vouch for a fit.
const namedTool = statedTools[0] || '';

// ---- 3. prefer a shape where we can actually show THEIR tool ---------------
// A GoHighLevel job should not be answered with HubSpot screenshots when a
// near-equal shape exists that we HAVE built in GoHighLevel.
if (clientTool && ranked.length > 1 && shape && !(LIB[shape] || {})[clientTool]) {
  const top = ranked[0].score;
  const better = ranked.find(r => r.score >= top * 0.6 && (LIB[r.shape] || {})[clientTool]);
  if (better) shape = better.shape;
}

// ---- 3b. a vague post about a tool we know well -----------------------------
// "GoHighLevel expert needed, not sure what we need yet" used to resolve to a
// weakly-scored shape we hold only in n8n, then substitute n8n — sending an n8n
// canvas to a GoHighLevel buyer while 116 GoHighLevel shots sat unused. When the
// request is vague but the TOOL is one we know, lead with the tool: pick the
// shape we hold the most evidence for in it. They asked about their tool; show
// it to them.
const shapesInTool = t => Object.keys(LIB)
  .filter(s => (LIB[s] || {})[t])
  .sort((a, b) => (LIB[b][t] || []).length - (LIB[a][t] || []).length);
// "Vague" means they did not clearly describe a pattern — a near-tie or a
// single thin hit. It does NOT mean "wrote a short post". Keying this off a raw
// score of 8 sent a Make/Zapier/n8n/GoHighLevel migration posting, which scored
// system-sync cleanly and unambiguously, to lead-routing instead, purely
// because it was concise.
const vagueRequest = !ranked.length || ranked[0].score <= 2 ||
  (ranked[0].score / Math.max(ranked[1] ? ranked[1].score : 1, 1)) < 1.3;
if (namedTool && shape && !(LIB[shape] || {})[namedTool] && vagueRequest) {
  const best = shapesInTool(namedTool)[0];
  if (best) shape = best;
}

// Our own reading beat a handed-in shape. Say so out loud rather than
// silently: a disagreement here is the upstream table drifting, and somebody
// should see it. Computed HERE, after the tool-preference steps, so it names
// the shape actually sent rather than the one ranking picked first.
const shapeOverride = (handed && shape && shape !== handed)
  ? { was: handed, now: shape, why: 'the posting scored ' + (ranked[0] ? ranked[0].score : 0) +
      ' on its own words and reads as "' + shape + '"; the shape handed in by the ' +
      'workflow was "' + handed + '", which is not what this posting describes' }
  : null;

// ---- their words, mirrored back --------------------------------------------
const painFor = (s) => (PAIN[s] || [])
  .filter(([phrase]) => HAY.includes(phrase))
  .map(([phrase, answer]) => ({ they_said: phrase, we_answer: answer }));

const top = ranked.length ? ranked[0].score : 0;
const second = ranked.length > 1 ? ranked[1].score : 0;

// ---- how sure are we, and about WHAT ---------------------------------------
// v3.3. Confidence used to be absolute thresholds on the raw keyword score:
// high needed 12 points, medium needed 6. That measures how MUCH the buyer
// wrote, not how clearly they said it. A 481-character post that names one
// thing precisely can never reach 12, so it could never be anything but
// "medium" no matter how obvious it was; a rambling 4,000-character post
// accumulates points and looks certain. It had the metric backwards.
//
// Certainty is MARGIN. If one pattern is well clear of the runner-up, the
// posting said which one it is. If two are neck and neck, it genuinely didn't,
// and no amount of length changes that. A real case: an accountancy posting
// that names QuickBooks scored books-reconciliation 5 and ai-research-agent 5 —
// a dead tie, correctly uncertain — and got the same "low" label as a posting
// that simply had few words in it. Meanwhile a 481-char dashboard post scored
// reporting 6 against project-ops 3, twice the runner-up and not remotely
// ambiguous, and got marked down for being short.
const margin = top / Math.max(second, 1);

// Naming the tool is a SEPARATE certainty from naming the pattern, and blending
// them into one number is what made the labels useless. "They said QuickBooks
// and we have QuickBooks" is a fact. It does not settle which pattern they
// want, and pretending otherwise is how a confident letter gets attached to the
// wrong build. So report them apart.
const toolCertainty = !namedTool ? 'none'
  : (LIB[shape] || {})[namedTool] ? 'named-and-covered'
  : 'named-not-covered';

// A single hit on one short generic word is not a match, however it scores.
const thin = top <= 2;  // one generic word is not a match, however it scores

// Margin alone is not enough. A "part time bookkeeper wanted, must know
// accounting" posting scores books-reconciliation 5 against a runner-up of 0 —
// infinite margin on almost no evidence, and it is a staffing ad, not a build.
// So "high" needs BOTH: clearly ahead of the field, and enough concrete
// evidence to be ahead of.
const SURE = 6;
const confidence = !ranked.length ? 'given'
  : thin ? 'low'
  // Well clear of the field, on evidence worth clearing it with.
  : (top >= SURE && (margin >= 2 || (margin >= 1.5 && toolCertainty === 'named-and-covered'))) ? 'high'
  // Ahead, but with a runner-up close enough to be worth naming.
  : (margin >= 1.3) ? 'medium'
  // Near-tie. This is the only honest "low": two patterns fit and the posting
  // does not choose between them.
  : 'low';

// ---- the floor: when the honest answer is "this is not us" -----------------
// A restaurant-menu design job used to score 1 point on the word "pdf", resolve
// to document-assembly, and come back with a confident document-automation
// pitch. That is fabrication, and it is worse than silence: it costs the reply
// AND the credibility. So there is a floor. Below it we say so and send nothing.
//
// The bar to clear is deliberately low but real — ONE of:
//   the posting names a tool we hold,     (they are in our world)
//   or it uses language from the pain table,  (they described a problem we fix)
//   or the shape scored like a genuine match. (the words line up on their own)
// A post that clears none of those is not a near-miss. It is a different job.
const painHits = shape ? painFor(shape).length : 0;
const topScore = ranked.length ? ranked[0].score : 0;
const knownTool = !!(namedTool && Object.keys(LIB).some(s => (LIB[s] || {})[namedTool]));
const belowFloor = !shape || (topScore < 5 && painHits === 0 && !knownTool);

if (belowFloor) {
  return [{ json: { ...input,
    proof_ok: false,
    should_skip: true,
    evidence: [], evidence_count: 0,
    evidence_shape: null,
    evidence_shape_candidates: ranked.slice(0, 3),
    evidence_input: { ...INPUT_TRACE, tool_source: toolSource },
    shape_override: shapeOverride,
    shape_unverified: shapeUnverified,
    client_tool: clientTool || null,
    client_tools: clientTools,
    match_confidence: 'none',
    stack_partners: [], stack_seam: null, seam_shown: null, stack_note: null,
    skip_reason: 'Nothing here matches a pattern we have built. Closest guess was "' +
      (shape || 'none') + '" at ' + topScore + ' points, with no tool we hold and no ' +
      'language from the pain table. Reaching for a build here would mean inventing ' +
      'the fit. Skip it rather than send something stitched together.',
    gap_notice: null,
  }}];
}

const entry = shape ? LIB[shape] : null;
if (!entry) {
  return [{ json: { ...input, proof_ok: false, evidence: [], evidence_count: 0,
    evidence_shape: shape,
    evidence_reason: shape ? 'no evidence filed for shape: ' + shape
                           : 'could not resolve a shape from the job post',
    evidence_shape_candidates: ranked.slice(0, 3),
    evidence_input: { ...INPUT_TRACE, tool_source: toolSource },
    shape_override: shapeOverride,
    shape_unverified: shapeUnverified,
    client_tool: clientTool || null,
    client_tools: clientTools,
    stack_partners: [], stack_seam: null, seam_shown: null, stack_note: null,
    gap_notice: clientTool ? ('No evidence for ' + pretty(clientTool) + ' and no shape resolved.') : null,
  }}];
}

// ---- 4. which tools do we show? -------------------------------------------
// The rule, in Seth's words: if the posting names the tool, show that tool. If
// it does not name one cleanly, or there is more we could show, slice it across
// tools — because the claim is not "I once did this in Klaviyo", it is "this
// pattern is mine and it stands up wherever you keep your data".
const toolsHere = Object.keys(entry).filter(t => t !== 'n8n');
const rank = ['ghl','hubspot','pipedrive','shopify','quickbooks','stripe','monday',
              'activecampaign','zapier','twilio','airtable','instantly','klaviyo',
              'supabase','zoho','slack','notion','clickup','calendly','vapi'];

// Tools THEY named that we actually hold, in the order they named them. These
// are not negotiable. A posting that says Klaviyo and gets a pack with no
// Klaviyo in it has already lost, however good the other pictures are.
const theirsCovered = clientTools.filter(t => entry[t] && t !== 'n8n');
const covered = theirsCovered.length > 0;
// Only tools the buyer WROTE decide how wide and how deep the pack goes.
// clientTools falls back to hint fields — skills tags, categories, whatever
// else rode in — and those are a guess. Sizing on a guess is what made the
// same telehealth posting attach a Klaviyo shot on a clean run and a second
// GoHighLevel shot on a contaminated one. A guess may still pick which tool
// leads; it may not change what the buyer receives.
const namedHeld = (toolSource === 'posting' ? statedTools : [])
  .filter(t => entry[t] && t !== 'n8n');
const namedAndHeld = namedHeld.length > 0;
// Their FIRST-named tool is the one they will look for. Missing it is still a
// gap worth queueing even when we could show a different tool they mentioned.
const primaryMissing = !!(clientTool && !entry[clientTool]);
const an = w => (/^[aeiou]/i.test(w) ? 'an ' : 'a ') + w;

// Everything else this shape lives in, best-known first. When they named
// nothing we hold, this IS the pack: same pattern, three houses.
const spread = rank.filter(t => toolsHere.includes(t) && !theirsCovered.includes(t))
                   .concat(toolsHere.filter(t => !theirsCovered.includes(t)));
const uniq = a => a.filter((x, i) => a.indexOf(x) === i);

// How wide the pack goes. Every tool they named earns a place. When they named
// none, breadth is the argument, so take up to three. When they named one and
// we have it, one more tool shows the seam without turning the pack into a
// tour of rival CRMs.
const WIDTH = namedHeld.length >= 2 ? Math.min(3, namedHeld.length)
            : namedHeld.length === 1 ? 2
            : 3;
const showTools = uniq(theirsCovered.concat(spread)).slice(0, WIDTH);

// Back-compat: the prompt, the audit and the send list all still read these
// two scalars. They now mean "the first tool" and "the second tool" rather
// than "the tool" and "the seam", and the array below is the real answer.
const shown   = showTools[0] || 'n8n';
const partner = showTools[1] || null;

// ---- 4a. how many pictures has this posting earned? -----------------------
// A four-line "connect Shopify to Klaviyo" post does not need eight images. A
// scoped brief that names three systems, describes the failure and lists
// requirements does — and sending four there reads as a template. So the size
// is earned by the ask, then capped by how much DISTINCT evidence we hold.
//
// Every term here has to be a function of THE POSTING and the library, and
// nothing else. Sizing on match confidence was the first version and it was
// wrong: confidence moves with the scoring margin, contamination in the
// payload moves the margin, and the regression caught the same buyer getting
// six pictures on one run and seven on the next. What a buyer opens must never
// depend on what else rode in with the request.
const __postLen = (post || '').length;
let PACK = 3
  + (__postLen > 2600 ? 2 : __postLen > 1000 ? 1 : 0)
  + Math.min(2, Math.max(0, showTools.length - 1))
  + (painFor(shape).length >= 3 ? 1 : 0)
  + (namedAndHeld ? 1 : 0)
  // They named nothing we hold, so there is no single right tool to be inside.
  // Breadth is the argument instead — the same pattern standing up in three
  // places — and breadth needs the room to be visible.
  + (!namedAndHeld && showTools.length >= 3 ? 1 : 0);
// A four-line posting that gets eight pictures reads as a template, however
// good the pictures are. The ask sets the ceiling as well as the floor.
const lenCap = __postLen > 2600 ? 8 : __postLen > 1400 ? 7 : __postLen > 700 ? 6 : 5;
PACK = Math.max(PACK_MIN, Math.min(PACK_MAX, Math.min(PACK, lenCap)));

// Some shots in the library say, in their own filename, that the thing is not
// running: an empty agents list, a paused agent, a campaign list with nothing
// but drafts in it. They were captured while a tool was being set up and they
// are honest, but a buyer opening a PDF and finding an empty state has learned
// something we did not want to teach. So they sort last everywhere, and only
// ever arrive as the final backfill when a shape holds nothing else.
//
// "draft order" is excluded on purpose: in Shopify a draft order is a product
// noun, not a confession.
// No \b and no \s in this pattern, on purpose. The JS below is emitted through
// a Python format string, and Python reads a lone backslash-b as a backspace
// character - so the first version of this regex shipped with every word
// boundary silently deleted and matched almost nothing. View names are
// hyphen-separated, so hyphen and underscore ARE the boundaries here.
const __WEAK = /(^|[-_])(?:empty[-_]?state|inactive|paused|placeholder|blank)([-_]|$)|(^|[-_])drafts?(?![-_]orders)([-_]|$)/i;
const weak = s => __WEAK.test(String((s && s.v) || ''));
// Stable, and weak-last. Array.prototype.sort is stable in every engine n8n
// runs on, so equal-strength shots keep the order the library gave them.
const strongFirst = arr => (arr || []).slice().sort((a, b) => (weak(a) ? 1 : 0) - (weak(b) ? 1 : 0));

// Two passes, always: a running shot that matches the pattern beats a
// not-running shot that matches it better. Filtering weak shots at the call
// sites was not enough - "campaigns-list-draft" contains "list", so the
// generic result-shot fallback found it anyway.
const pick = (arr, ...pats) => {
  const all = arr || [];
  for (const pool of [all.filter(x => !weak(x)), all]) {
    for (const p of pats) { const h = pool.find(x => x.v.includes(p)); if (h) return h; }
  }
  return null;
};
const n8n = entry['n8n'] || [];
const own = entry[shown] || [];

const beats = STORY[shape].beats;
const chosen = [];
const used = new Set();
const push = (f, line, beat) => {
  if (!f || !line || used.has(f.f) || chosen.length >= PACK) return;
  used.add(f.f);
  chosen.push({ f, line, beat, tool: f.__tool || shown });
};
const canvas = pick(n8n, 'kit-canvas-18-nodes', 'canvas');
const logic  = pick(n8n, 'node-v2-decision-if', 'node-v2-gap-report', 'node-validate');
const hint   = HINT[shape] || [];
const stack  = STACK[shape] || null;

// Beat one and two are always the machine: the shape of it, then the decision
// inside it. Those are the same picture whoever the buyer is.
push(canvas, beats[0], 'system');
push(logic,  beats[1], 'thinking');

// Then the tools, in two passes rather than one. The first pass gives every
// tool its lead picture, so a three-tool pack in a five-slot budget still shows
// three tools instead of two tools twice. Only once every tool has been seen
// does the second pass spend what is left on the far side of each.
//
// The one-pass version looked tidier and was wrong: it exhausted the budget on
// tool one and the third tool never appeared, which is the exact failure —
// claiming range in the letter and attaching a pack that shows one system.
const lead = {}, tail = {};
showTools.forEach((t, i) => {
  const shots = strongFirst(entry[t] || []).map(s => Object.assign({}, s, { __tool: t }));
  // The hint pins which shot a caption is describing, so it wins - but only
  // among shots that are actually running. A hint that matches nothing except
  // an empty state is a caption pointing at a picture of nothing, and that is
  // how "campaigns-list-draft" led a cold outreach pack on the first cut.
  // Every fallback is tried against the running shots BEFORE the pattern list is
  // widened to include the rest. Exhausting the patterns first is what put
  // "campaigns-list-draft" in the result slot: no running shot in that shape
  // contains the word list, so a pattern match on a draft beat a plain running
  // shot that matched nothing. A running picture the caption describes loosely
  // is worth more than a perfect match on an empty screen.
  const strong = shots.filter(s => !weak(s));
  const LEADPAT = ['canvas', 'builder', 'automation', 'settings', 'config', 'trigger'];
  const TAILPAT = ['board', 'list', 'dashboard', 'record', 'detail', 'saved', 'summary'];
  lead[t] = (i === 0 && hint[0] && pick(strong, hint[0]))
            || pick(strong, ...LEADPAT) || strong[0]
            || pick(shots, ...LEADPAT) || shots[0];
  const rest = shots.filter(s => s !== lead[t]);
  const restStrong = rest.filter(s => !weak(s));
  tail[t] = (i === 0 && hint[1] && pick(restStrong, hint[1]))
            || pick(restStrong, ...TAILPAT) || restStrong[0]
            || pick(rest, ...TAILPAT) || rest[0];
});
const seamLineFor = t => 'And the far side of it, in ' + pretty(t) +
  ' — the same record after it crosses. ' +
  (stack ? stack.seam
         : 'The handoff is the part that actually breaks, so it is the part worth showing.');

showTools.forEach((t, i) => {
  push(lead[t], i === 0 ? beats[2] : seamLineFor(t), i === 0 ? 'their-world' : 'the-seam');
});
showTools.forEach((t, i) => {
  push(tail[t], i === 0 ? beats[3]
                        : 'What it looks like in ' + pretty(t) + ' once the run is done.',
       i === 0 ? 'result' : 'the-seam');
});

// Still short? Backfill from anything this shape holds that has not been used,
// rather than shipping four when seven exist. Padding costs the deal, but so
// does leaving proof in the folder.
if (chosen.length < PACK) {
  const pool = strongFirst(showTools.concat(spread).reduce(
    (acc, t) => acc.concat((entry[t] || []).map(s => Object.assign({}, s, { __tool: t }))),
    []).concat(n8n.map(s => Object.assign({}, s, { __tool: 'n8n' }))));
  for (const f of pool) {
    if (chosen.length >= PACK) break;
    push(f, beats[3] || beats[2], 'more');
  }
}

const attach = chosen.slice(0, PACK);
// The pack is the whole truth downstream, so the tool list has to be what is
// actually IN it, not what we hoped to show. A tool we planned and then found
// no unused shot for must not appear here.
const attachedTools = uniq(attach.map(a => a.tool).filter(t => t && t !== 'n8n'));
const seamShown = attachedTools.filter(t => t !== shown);

return [{ json: {
  ...input,
  proof_ok: attach.length > 0,
  evidence_shape: shape,
  evidence_shape_candidates: ranked.slice(0, 3),
  evidence_input: { ...INPUT_TRACE, tool_source: toolSource },
  shape_override: shapeOverride,
  shape_unverified: shapeUnverified,
  product_name: STORY[shape].product,
  evidence_open: STORY[shape].open,
  evidence_tool_shown: pretty(shown),
  // The real answer. Every tool a picture in this pack is actually inside, in
  // the order the pack tells it. Downstream treats THIS as the truth; the two
  // scalars either side of it are the old shape kept alive for the send list.
  evidence_tools_shown: attachedTools.map(pretty),
  client_tool: clientTool || null,
  client_tools: clientTools,
  client_tool_covered: covered,
  evidence_is_exact_tool: covered,

  // ---- the integration story ----------------------------------------------
  // Answers "what does this connect TO", which is the question underneath
  // almost every posting even when the posting names one tool.
  stack_partners: stack ? stack.partners.map(pretty) : [],
  stack_seam: stack ? stack.seam : null,
  // Set when THEY named two tools and we hold the pattern in both.
  seam_shown: seamShown.length ? pretty(seamShown[0]) : null,
  seams_shown: seamShown.map(pretty),
  // Why the pack is the size it is, so a short one can be read as a decision
  // rather than a shortage.
  pack_size: attach.length,
  pack_target: PACK,
  pack_width: showTools.length,
  // The line to open the integration paragraph with, whether or not we attached
  // a far-side shot. Uses their own tools when they named them.
  stack_note: stack
    ? (clientTools.length > 1
        ? ('You have named ' + clientTools.slice(0, 3).map(pretty).join(' and ') +
           '. The build is not in either of them, it is in the boundary: ' + stack.seam)
        : (clientTool
            ? (pretty(clientTool) + ' is rarely the whole picture here — this pattern normally sits ' +
               'between it and ' +
               stack.partners.filter(p => p !== clientTool).slice(0, 2).map(pretty).join(' or ') +
               '. ' + stack.seam)
            : stack.seam))
    : null,
  evidence: attach.map(a => ({ file: a.f.f, url: BASE + a.f.f.split('/').pop(),
                               line: a.line, beat: a.beat })),
  evidence_count: attach.length,
  substitution_note: (!covered && clientTool)
    ? ('That build is in ' + pretty(shown) + ' rather than ' + pretty(clientTool) +
       ", because that's where my last two clients lived. The tool changes; the architecture doesn't.")
    : (primaryMissing
        ? ("Showing this in " + pretty(shown) + ", which you also named — the " +
           pretty(clientTool) + " side is the same pattern with the same seam.")
        : null),
  // Feeds the "we don't have their tool" branch: email Seth, queue that build.
  // What THEY said, paired with how it is handled. Buyers describe the same
  // handful of systems in different packaging; quote them, not us.
  matched_pain: painFor(shape).slice(0, 5),
  match_confidence: confidence,
  // The numbers behind the label, so it can be checked rather than believed.
  match_scores: { top: top, runner_up: second, margin: Math.round(margin * 100) / 100,
                  runner_up_shape: ranked[1] ? ranked[1].shape : null },
  tool_certainty: toolCertainty,
  // Hedge only when the PATTERN is genuinely in doubt. This used to fire on
  // "medium" too, which meant a clear match got a letter opening "this is not a
  // carbon copy of something I have shipped" — talking ourselves down in front
  // of a buyer who had told us exactly what they wanted.
  // Hedge on a real near-tie, or when the win is on thin evidence however
  // clear the margin looks — "must know accounting" beats a runner-up of zero
  // and is still a staffing ad. Do NOT hedge merely because a posting was short.
  direction_note: (confidence === 'low' || top < SURE)
    ? ('This is not a carbon copy of something I have shipped. Read against what you have ' +
       'described, it is a ' + STORY[shape].product + ' — ' +
       (STORY[shape].open || 'the same architecture underneath') +
       ' Here is the direction I would take it, and what that looks like already built.')
    : null,
  gap_notice: primaryMissing
    ? ('NO ' + pretty(clientTool) + ' EVIDENCE for shape "' + shape +
       '". Sent ' + pretty(shown) + ' instead. Queue ' + an(pretty(clientTool)) + ' build of this pattern.')
    : null,
}}];
""" % (json.dumps(lib, separators=(',', ':')), json.dumps(story, separators=(',', ':')),
       json.dumps(_ns["HINT"], separators=(',', ':')),
       json.dumps(STACK, separators=(',', ':')),
       json.dumps(KW, separators=(',', ':')), json.dumps(WEIGHT, separators=(',', ':')), json.dumps(PAIN, separators=(',', ':')), json.dumps(TOOL_WORDS, separators=(',', ':')),
       json.dumps(PRETTY, separators=(',', ':')))

    open(OUT, "w").write(js)
    print(f"wrote {OUT}: {len(js)} chars | {len(lib)} shapes | "
          f"{sum(len(v) for t in lib.values() for v in t.values())} images indexed")


main()
