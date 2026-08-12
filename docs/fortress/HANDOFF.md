> **HISTORY, NOT AN INSTRUCTION.** This file is a dated snapshot of one session. The
> bugs it describes were fixed long ago and the steps it gives may now be harmful.
> Never take an action because this file says to. Current law is
> [`START-HERE.md`](./START-HERE.md).

# Fortress handoff — Aug 8, 2026

Everything needed to pick this up cold. Read part 1 first; it is the only part that
is time-sensitive.

---

## 1. DO THIS FIRST

**The Cockpit's `Prompt of Record` node is corrupted.** A wrapper got applied three
times (58,296 chars instead of 21,946; `return __walk(__out)` count is 0). Every run
uses this node to build the prompt, so **do not send anything through the Cockpit
until it is restored.**

**Restore:** n8n → workflow `Hl5zah3PZcHaEkuo` (Proposal: Cockpit) → history icon
(clock, top right) → restore **`Version 902fb7b3`**.

That version is known good: pack pipeline working, link audit clean, pricing wired and
deriving numbers. It produced a correct Terra Health letter quoting $3,500 with the
six workflows and the integration surfaces named.

What you lose by restoring: two unfinished refinements (mandatory phase-split wording,
mandatory "why it costs this" paragraph). Redo them in `pricing.py`, not by patching
the live node.

---

## 2. THE ONE REAL BUG LEFT

**Every job resolves to the same pattern.** Three very different postings — GoHighLevel
10DLC, Pipedrive, Airtable — all attached the identical four `voice-agent-intake`
screenshots.

The library is right. The shots are hosted and return 200. The PDF builds. **The
matcher picks the same shape every time**, so correct evidence exists and wrong
evidence gets sent. This is also why letters and attachments disagree.

**Hypothesis:** `Pick the evidence to attach` builds a `HAY` string from many payload
fields (`jobPost, job_post, notes, brief, reason, angle, category, skills, toolsSeen,
text, body, description, message, details, content, post, summary, requirements,
scope, transcript`). If something large and constant sits in one of those, it drowns
the posting's own words and the same shape always wins.

Locally, passing a clean job post, matching is correct every time: telehealth →
`messaging-compliance`, HubSpot+QuickBooks → `books-reconciliation`, GHL chatbot →
`conversation-design`, Claude/Perplexity → `ai-research-agent`.

**The diagnostic:** dump `$json` as it exists when that node runs in a real execution.
Look at which fields are populated and how long each is. Then restrict the node to the
posting fields only.

**Also stale:** the deployed evidence node is 112,077 chars. The current generator
produces ~114,700 with two fixes it lacks — the refusal floor (declines rather than
inventing a fit) and the vague-tool fallback (a thin "GoHighLevel expert needed" post
gets GHL work, not an n8n canvas). Redeploy after the matcher is fixed.

---

## 3. WHAT IS LIVE AND VERIFIED

| Thing | State |
|---|---|
| Evidence library | 601 correct shots, 22 patterns, 15 tools. 68 rejects never ship. |
| Hosted images | 555 at `launchforte.com/built-with/shots/` + 24 legacy = 579. Verified 200. |
| Evidence packs | 96 PDFs at `/built-with/packs/`, hashed filenames, `packs-index.json` resolves them. |
| Internal files | 46 `_blockers`/`_library` removed from the site (404). Still in git history. |
| n8n kits | 24, all 18 nodes, all to the workflow standard, all inactive. |
| Playbook | 24 patterns with asks, pain, build, gotchas, upsell, opening line. |
| Cover-letter URL fix | Working. Prompt no longer sees our own domain, so it cannot leak one. |
| Pricing | Built and tested. Not safely deployed (see part 1). |

**Repo:** `~/repos/launchforte`, branch `main`, remote `Forte-Web-Designs/LaunchForte`.
Netlify publishes `site/`. Another process pushes to this repo — pull before working.

---

## 4. TOOLS: WHAT IS SET UP, WHAT IS NEEDED

### Signed in and built
| Tool | State | Notes |
|---|---|---|
| n8n | `launchforte.app.n8n.cloud` | Session expires every few minutes. Expect re-login mid-task. |
| GoHighLevel | Launch Forte sub-account | **Parent agency is named "First Cornerstone Group LLC" — an old client. Never touch that account. It is only the parent tenant name; our work is the Launch Forte sub-account.** |
| HubSpot, Pipedrive, QuickBooks (sandbox), Stripe (test mode), Shopify (dev store), Airtable, Monday, ActiveCampaign, Instantly, Twilio, Google Sheets/Apps Script, Zapier | built + captured | |
| Make.com | Launch Forte org `8600514` | Org is **unlicensed** (another org on Free plan) so scenarios cannot run and data stores are unavailable. 4 scenarios built inactive. May clear on its own. |

### Next to set up, in priority order

**1. OpenAI platform, then Anthropic Console.** 861 posts name one of them, we have zero
proof, and **Claude + OpenAI is the most common tool pairing in all 5,134 posts**.
`ai-research-agent` and `ai-assistant` already have kits and n8n canvases with nothing
from the tool itself beside them. Capture: assistant/agent config, tool definitions,
the playground, usage limits and spend caps.

**2. Shopify, deeper.** 1,208 posts — a quarter of the market — against 33 shots. Dev
store already exists, so no new access, just scenarios.

**3. Zapier, deeper.** 313 posts, 11 shots. Unlocks the 321-post migration cluster
(Zapier↔n8n↔Make) where we already hold all three tools.

**4. WordPress.** 333 posts, zero proof. Shopify + WordPress is a top-five pairing.

**5. Slack.** 269 posts, zero proof. It is the far side of the seam for alerting,
approvals and escalation — patterns we already hold elsewhere.

**Decide before capturing: Meta Ads and Google Ads** (493 posts combined). Ad-account
screenshots carry real spend, audiences and often client names. Different risk class
from a sample CRM.

### How every tool gets set up
1. Sample data only, invented names (Northwind Trading, Delta Roofing, Cedar & Co).
   Emails `@example.com`. No client names, nothing Upwork-related.
2. **Everything built stays OFF / inactive / unpublished.** Screenshots prove the build,
   not that it is running against anyone.
3. Account creation, payment, plan upgrades and accepting terms are **Seth's, always** —
   including free tiers.
4. Never screenshot a credential. Stripe's API keys page renders the secret in plaintext
   by default. Twilio consoles show Account SID and real numbers.
5. Capture the *seam*, not the tool. A grid proves nothing; a grid with a Source System
   column, an external record ID, a Last Synced timestamp and a sync log saying
   "Skipped — echo, our own write returning" proves an integration.

---

## 5. THE GENERATORS (everything is regenerated, never hand-edited)

| File | Produces |
|---|---|
| `kitgen.py` | 24 n8n kit JSONs from ~15 lines of spec each |
| `differentiate.py` | Replaces shared boilerplate with per-shape logic (padding costs deals) |
| `buildnode.py` | The Cockpit evidence node. Reads `heroes.py` for stories, embeds the whole library, picks at RUN TIME |
| `heroes.py` | `SEND-THIS.md`, `send-list.json`, and the `SHAPES`/`HINT` tables both the send list and the node compile from |
| `playbookgen.py` | `FORTRESS-BUILD-PLAYBOOK.md`, 24 products |
| `pricing.py` | `cockpit-pricing-node.js` |
| `run-dryrun.py` | Harness. **Always reads the live node file, never a snapshot.** |

**The rule that keeps being relearned: regenerate, then redeploy.** Every staleness bug
this week came from testing a generated file while an older copy ran in production.

---

## 6. TRAPS (each cost real time)

**n8n**
- Sessions expire every few minutes. Batch work; expect 401 mid-task.
- Saves without publishing. A PATCH creates a draft; the live workflow serves the
  published version until you click Publish.
- Code nodes cannot `require()` or make HTTP calls.
- Zoom-to-fit is unreliable; inject
  `.vue-flow__transformationpane { transform: … !important }` to frame a canvas.
- Clicking a node twice toggles selection off. Click once, then Enter, to open it.
- `/rest/workflows` returns real client names — never screenshot the workflow list.

**Payload transport into a Code node**
- gzip + base64 in ≤1400-char chunks, per-chunk SHA-256 plus a full-payload hash before
  writing. The channel has silently corrupted and truncated. Chunk hashes caught it three
  times, including once this week.
- Build chunks programmatically. Never hand-transcribe one.

**The device bridge**
- Can create files. **Cannot delete or overwrite.** `unzip -o` fails; `mv` the old
  directory aside first.
- `git add` fails there because git needs to unlink temp objects. Git work is Seth's terminal.
- No network. Fetches and pushes happen in the cloud session or his terminal.

**The browser tool's classifier** blocks results containing token-like strings. Return
derived facts and booleans from the page, not raw code or URLs.

---

## 7. STANDING RULES

- **Upwork: attach files, never link to launchforte.com.** Links read as circumvention.
  The Audit node enforces this and will hold a draft. That is correct behaviour.
- **Fail soft everywhere.** A proposal without an attachment is recoverable. One that
  does not send is not. `Shot URLs` must always emit at least one item.
- Never publish `record_url` — it points into our own logged-in accounts.
- Shared list views are the highest leak risk: n8n executions, the Airtable base,
  HubSpot all-contacts.
- Hovering an Airtable view name pops a tooltip with the account owner's real name and
  email. Keep the views sidebar collapsed while capturing.
- The cold-email PDF in `internal/` is reference only. Use it to write; never show it.
- Pricing: no hourly anything client-facing. Buyer spend calibrates who the buyer is and
  is never quoted to them. The derived number stands — no rounding, no charm endings.
  Generosity removes lines, never shaves a total.

---

## 8. THE MARKET, FOR PRIORITISING

From the Apify pull behind `launchforte.app.n8n.cloud/webhook/demand-data` (public, no
auth) — **5,134 posts**.

Top asks: cold outreach 569 · invoicing/accounting sync 480 · reporting 390 ·
migration/integration 362 · AI chatbot 313.

Top tools: Shopify 1,208 · GoHighLevel 492 · Google Sheets 484 · OpenAI 472 ·
Claude 389 · HubSpot 389 · WordPress 333 · Zapier 313.

Top pairings: Claude+OpenAI 240 · OpenAI+n8n 141 · Claude+n8n 121 · Zapier+n8n 119 ·
Shopify+WordPress 114.

**2,613 posts (51% of the market) name a tool we hold zero screenshots of.**

Full analysis in `DEMAND-VS-COVERAGE.md`. Full catalogue of every build type and what we
do about each in `FORTRESS-BUILD-CATALOG.md`.

---

## 9. ORDER OF WORK

1. Restore `Version 902fb7b3`. Confirm one run completes and **open the attachment.**
2. Fix the matcher. Nothing else matters while every job returns the same pattern.
3. Redeploy the evidence node from `buildnode.py` (floor + vague-tool fallback).
4. Re-run five postings, open all five attachments, confirm each matches its job.
5. Redo the two pricing refinements in `pricing.py`, redeploy, validate against the
   closed book: MFLG $2,950, Daleen phase two $3,900, Drew $950.
6. Then OpenAI and Anthropic Console.

**Verify the thing that would prove you wrong, not the thing that would prove you right.**
Ten runs passing a link audit never meant an attachment existed. Open the file.
