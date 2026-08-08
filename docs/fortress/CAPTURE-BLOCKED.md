# What is blocked, and what it costs

Short list. Everything else is either done or in progress.

## Needs one click from Seth

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

## Worth a look, not blocking

**A long post-purchase brief matched books-reconciliation.** A 1,300-character
test posting that is dominantly Shopify → Klaviyo post-purchase work, with one
paragraph about refunds not reaching QuickBooks, resolved to
`books-reconciliation` and attached a QuickBooks pack. The accounting nouns are
heavy — quickbooks, refund, reconcil, attribution — and they outscored the
storefront ones. It is a scoring question, not a pack question, and the pack
did exactly what it was told. Flagging it rather than tuning weights blind.
