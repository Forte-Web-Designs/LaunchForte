# 8 August — what changed

Two things: the pack stopped being a fixed shape, and the library grew by 115
pictures across four tools that had almost no coverage.

## The pack

Every send attached exactly four pictures from at most two tools, because
`MAX = 4` was a constant nobody had revisited. A four-line "connect Shopify to
Klaviyo" got four. A 4,000-character brief naming three systems got four. Equal
size on unequal asks is what a template looks like.

Packs now size themselves between three and eight, earned by the posting and
capped by it, and go up to three tools wide. The rule Seth set: **if the posting
names the tool, that tool is in the pack.** If it does not name one cleanly, the
pack slices across tools instead, because the claim is not "I did this once in
Klaviyo", it is "this pattern is mine and it stands up wherever you keep your
data".

Verified against the exact posting behind run 26901 — the Huwa Goods brief
naming Shopify and Klaviyo. It attached 4. It now attaches 7, across both.

Full mechanics in `PACK-SIZING.md`.

Two things the regression caught along the way, both worth remembering:

- **Sizing on match confidence was wrong.** Confidence moves with the scoring
  margin, the margin moves with contamination in the payload, and the same
  telehealth posting got six pictures on one run and seven on the next. What a
  buyer opens must never depend on what else rode in with the request. Every
  sizing term is now a function of the posting and the library and nothing else.
- **One pass over the tools spent the whole budget on tool one** and the third
  tool never appeared — claiming range in the letter and attaching a pack that
  shows one system. Tools are assigned in two passes now: every tool gets its
  lead picture before any tool gets a second.

## Pictures that admitted defeat

Seven shots announced in their own filename that the thing was switched off —
an empty agents list, a paused agent, a campaign list of drafts. They sort last
now and never reach a pack. Swept all 23 shapes: zero.

The fix took three attempts because the first pattern used `\b`, and this node
is emitted through a Python format string that reads a lone backslash-b as a
backspace. The regex shipped with every word boundary deleted. The tests looked
clean because a stale second copy of the node was being harnessed from the
wrong directory — worth knowing, because that trap is still there.

## The library: 651 → 766

| Tool | Before | After | The picture worth having |
|---|---:|---:|---|
| Supabase | 0 | 29 | The run log showing failed → failed → retried on a 429 |
| Zoho | 0 | 24 | The escalation rule end to end, and the criteria behind the stalled view |
| Slack | 2 | 22 | One channel telling the whole cycle, including the match that was flagged and **not** written |
| Calendly | 2 | 23 | A routing form that refuses to book active fire damage and says ring the emergency line |
| Klaviyo | 5 | 26 | The flow firing an internal alert on the path where it decided to stay silent |

The theme across all of them is the same, and it is the thing worth selling: a
system that records what it decided *not* to do is more convincing than one that
only shows its successes. A buyer's real fear is not that the automation fails
to send. It is that it sends to somebody it should not have and nobody finds
out.

## Still waiting on Seth

- **Zoho Books** — the organisation does not exist. Name it *Halden Restoration*
  and the reconciliation set is unblocked: invoice matched to payment, aging
  report, bank rule. 91 A/B-graded postings behind it.
- **Vapi** — signed out.
- **Notion** — the Chrome extension holds no permission for notion.so, so
  screenshots fail before they start.

## One to look at, not blocking

A long post-purchase brief that is dominantly Shopify → Klaviyo, with one
paragraph about refunds not reaching QuickBooks, resolves to
`books-reconciliation` and attaches a QuickBooks pack. The accounting nouns
outscore the storefront ones. It is a scoring question, not a pack question —
the pack did exactly what it was told. Flagged rather than tuned blind.
