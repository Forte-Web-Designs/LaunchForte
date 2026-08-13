# What is blocked, and what it costs

Short list. Everything else is either done or in progress.

## Needs one click from Seth

**HubSpot Workflows — the Launch Forte portal (51819426) is on Free Marketing
tools, not Marketing Hub Professional.** `SIM-EO-1-spec.md` (section 5) asks for
two workflows — `LF SAMPLE - New Tier 1 Target Account Enrollment` (Company-based)
and `LF SAMPLE - Proposal Sent Follow-Up Reminder` (Deal-based) — but
`/workflows/51819426` redirects straight to
`/pricing/51819426/upgrade/locked-nav-item?upgradeSource=workflows-marketing-locked-nav-item`
every time, regardless of which object the workflow would be built on: "Run
powerful automated email campaigns... Unlock this and more with Marketing Hub
Professional," with the plan-comparison table showing "Free Marketing tools" as
"Your current plan" (disabled) and a blank cell for "Omni-channel marketing
automation" there vs. "Up to 300 workflows for 10 teams" under Professional.
The account & billing usage page (`Other Limits`) carries no workflow limit at
all for this plan — there is no free-tier workflow allowance to work within, not
even a reduced one. Same shape as the Sequences block below: the only ways past
it are "Talk to Sales" or "Start 14-day trial," both a plan-tier change, which is
Seth's call, not a runner's. Nothing was built. Screenshot:
`docs/proof/eo-6-1-workflows-locked-marketing-hub-pro.png`. What it unblocks:
card `eo-6` (the SIM-EO-1 workflows) and anything later in the simulation that
assumes Workflows exists.

**HubSpot Sequences — the Launch Forte portal (51819426) is on Free Sales tools,
not Sales Hub Professional.** `SIM-EO-1-spec.md` (section 4) assumes Sales Hub
Professional and asks for a 5-step sequence, `LF SAMPLE - Target Account
Outreach - Corporate Gifting`. `/sequences/51819426` redirects straight to
`/pricing/51819426/upgrade/locked-nav-item?upgradeSource=sequences-locked-nav-item`
— "Never let a lead go cold... Unlock this and more with Sales Hub Professional,"
with the plan-comparison table showing "Free Sales tools" as "Your current plan"
(disabled) and Sequences with an empty cell there vs. "5,000 sequences per
account" under Professional. The only ways past it are "Talk to Sales" or
"Start 14-day trial" — both a plan-tier change, which is Seth's call, not a
runner's, even though the trial claims no card is required. Nothing was built;
no trial was started. Screenshot: `docs/proof/eo-5-1-sequences-locked-sales-hub-pro.png`.
What it unblocks: card `eo-5` (the SIM-EO-1 sequence) and anything later in the
simulation that assumes Sequences exists.

**Zoho Books — the organisation does not exist yet.**
`books.zoho.com` opens on "Welcome Seth Forte, let us know where your business
is" with two fields: Organization Name and Organization Location. Creating an
organisation is a form submission on Seth's account, so it stays his. Put
**Halden Restoration** and the location in, click "Let's get started", and the
rest is unblocked.

What it unblocks: `books-reconciliation` currently has QuickBooks or nothing.
The plan is four shots — an invoice matched to its payment showing the
reconciliation, the aging report, the recurring-invoice rule, and the bank
feed with a rule applied. 29 A/B-graded postings ask for invoice and payment
reconciliation, 62 for invoice chasing.

Zoho CRM itself is done: 24 accounts, 24 restoration deals, a stalled custom
view, and a live escalation rule with a tag, a task and a scheduled second
pass. Twenty-four shots filed.

## Working around

**Zoho's own sample records.** The account came seeded with ten `(Sample)`
companies — Benton, Chapman, Truhlar and Truhlar. They are Zoho's, not ours,
and they sit in the default All Deals view next to the restoration jobs. Zoho's
Setup has a "Remove sample data" button, which deletes; deleting is not
something I do on an account, so instead the **Stalled — quote out, close date
passed** custom view filters them out by date and every Zoho shot is taken
through that view or the workflow builder. If Seth wants them gone, Setup →
Data Administration → Remove sample data.

**Zoho rejects `example.com` webhook URLs.** The webhook action in the
escalation rule would not save against `https://ops.example.com/hooks/...` —
Zoho validates the host. The configuration screenshot was taken before saving,
which is the shot that mattered, and the rule saved with a tag, an instant task
and a scheduled second-pass task instead. Nothing about the story changes; the
handoff is real either way.

**Notion automations are a paid feature.** The database automation panel —
"automatically edit properties, create pages, send updates" — opens on the free
plan and shows nothing but an Upgrade button. So the Notion capture has no
automation shot and will not have one until the workspace is on a paid plan.
What replaced it is better evidence anyway: a saved **Stalled 7+ days** view
whose filter is the escalation rule written down, and a job page whose body
carries the runbook the automation would run. Both are things a buyer can read
without knowing what Notion charges for.

**Notion's view toolbar will not open its popovers under automation.** The
filter chip, sort chip and the rest of the row above the table refuse to open
their panels when driven through the extension — the `+ Add property` button in
the same page opens its menu fine, so it is that toolbar specifically. Every
Notion view in the library was therefore built through the internal
`saveTransactionsFanout` API and shot as a rendered result, not as a config
panel mid-edit. The filter chip still reads "2 rules" in frame.

## Worth a look, not blocking

**A long post-purchase brief matched books-reconciliation.** A 1,300-character
test posting that is dominantly Shopify → Klaviyo post-purchase work, with one
paragraph about refunds not reaching QuickBooks, resolved to
`books-reconciliation` and attached a QuickBooks pack. The accounting nouns are
heavy — quickbooks, refund, reconcil, attribution — and they outscored the
storefront ones. It is a scoring question, not a pack question, and the pack
did exactly what it was told. Flagging it rather than tuning weights blind.

**A tool name that is also an English word.** "posted **Monday** morning" put
Monday.com in `client_tools`; "contacted **instantly**" put Instantly.ai there;
"pick up the **slack**" put Slack there. Substring matching did it, and on a
posting that named Notion three times the pack still led with Monday.com
screenshots. Fixed by `TOOL_GUARD` in `buildnode.py`: for the ambiguous names
the bare word is no longer enough — the posting has to carry the domain
(`monday.com`), a product noun (`monday board`, `instantly campaign`, `slack
channel`, `notion database`) or a preposition that only makes sense in front of
a tool (`in Monday`, `using Instantly`). Missing a real mention costs a
substitution note. Inventing one costs the pack.

**The conversation-design alias went dead the moment its folder filled.**
`ALIAS` used to borrow only when the alias shape had no folder of its own. Two
Vapi shots got filed under `conversation-design`, the folder stopped being
empty, and the shape quietly dropped from thirteen GoHighLevel Conversation-AI
screenshots to a pack of **one**. Borrowing is additive now: the alias keeps
whatever it holds and inherits the rest. Minimum pack across all 24 shapes went
1 → 3.

**ClickUp's list grid eats keystrokes as hotkeys.** A single click on a cell
SELECTS it; the characters you type next are read as global shortcuts, not as
cell input. Driving a column of edits blind flagged five sample jobs as
Priorities and assigned one to the account owner before anything was typed into
a field. Cleared afterwards. The working pattern is `double_click` the cell,
type, then `double_click` the next one — and never batch it across a scroll,
because the grid re-flows between actions and the coordinates go stale mid-batch.

**Empty custom fields are what make a ClickUp board look like a demo.** Filling
eighteen rows by hand is dozens of interactions; the cheaper fix is
`Customize → Show empty fields → off`, which drops the "-" rows from the cards
and leaves a board that reads as a real pipeline. Two jobs carry full fields so
the record shot has something in it. The rest carry name, stage and job type.

**ClickUp's AI automations are on by default and they write to tasks.** The list
arrived with four active rules, two of them "AI Prioritize". They set a priority
on every task created, so a sample job appears with an Urgent flag nobody chose.
Worth knowing before a shot: the flag in frame is ClickUp's, not the design's.

**Upwork is never driven by automation. Ever.** Not the job feed, not contract
history, not messages, not sending. Upwork bans accounts for bot activity and
that account IS the business — no screenshot, posting or price is worth the
risk. Anything that needs Upwork is Seth's to do by hand, and the right move is
to ask him to copy across what is needed. The `upwork_jobs` data table inside
the Cockpit is the sanctioned way to reach posting data: it is our own table,
already scraped, and reading it touches nothing at upwork.com.
