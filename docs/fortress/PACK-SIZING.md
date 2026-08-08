# How big a pack is, and what is in it

Until 8 August every send attached exactly four pictures from at most two
tools. That was not a decision, it was a constant — `MAX = 4` — and it showed.
A four-line "connect Shopify to Klaviyo" posting got four images. A scoped
brief naming three systems, describing the failure and listing requirements got
the same four. Identical size on unequal asks reads as a template, which is the
one thing a proposal cannot afford to read as.

Seth, 8 August: *"some packs have 4 images, some can have more than 4. some can
have multiple tools to get the point across... if the job posting explicitly
states the tool, be sure to show that tool. if it doesnt cleanly, or theres more
we can do here, show it."*

So the pack sizes itself now, between three and eight.

## Which tools

The order is not negotiable.

1. **Tools the buyer wrote, that we hold.** If the posting says Klaviyo and we
   have Klaviyo in that shape, Klaviyo is in the pack. This is the whole point
   of holding a library.
2. **Everything else that shape lives in**, best-known first. This only fills
   space the buyer's own tools did not claim.

How wide it goes depends on what they told us:

| What the posting named | Tools in the pack | Why |
|---|---|---|
| Two or more we hold | up to 3 | They described a stack; the seam between their systems is the work |
| Exactly one we hold | 2 | Depth in theirs, plus one far side so the integration is visible |
| None we hold, or none at all | 3 | There is no right tool to be inside, so breadth is the argument: the same pattern standing up in three places |

Only tools the buyer **wrote** count here. `clientTools` falls back to hint
fields — skills tags, categories, whatever else rode in on the payload — and
those are a guess. A guess may still pick which tool leads. It may not change
what the buyer receives. Sizing on a guess is what made the same telehealth
posting attach a Klaviyo shot on a clean run and a second GoHighLevel shot on a
contaminated one, and the regression caught it.

## How many pictures

Three, plus:

- **+1** if the posting is over 1,000 characters, **+2** over 2,600
- **+1** per extra tool in the pack, up to +2
- **+1** if the shape has three or more pain phrases the posting hits
- **+1** if they named a tool and we hold it
- **+1** if they named nothing we hold and the pack is three tools wide

Then capped by the ask itself: 5 pictures under 700 characters, 6 under 1,400,
7 under 2,600, 8 above. Floor 3, ceiling 8.

Every term is a function of the posting and the library and nothing else. The
first version used match confidence, which moves with the scoring margin, which
moves with contamination in the payload — so the same buyer got six pictures on
one run and seven on the next. What a buyer opens must never depend on what
else rode in with the request. `matcher-test.py` enforces this.

## The order inside the pack

Two passes, not one.

1. The n8n canvas — the shape of the system.
2. The n8n decision node — the logic underneath it.
3. **Every tool gets its lead picture** before any tool gets a second one.
4. Then, with whatever budget is left, each tool's result shot in the same order.

The one-pass version read better and was wrong: it spent the budget on tool one
and the third tool never appeared, which is the exact failure — claiming range
in the letter and attaching a pack that shows one system.

## What downstream reads

The pack publishes `evidence_tools_shown`: every tool a picture in the pack is
actually inside, in the order the pack tells it. That is the truth. It is
derived from the attached shots, not from what we intended to show, so a tool we
planned and then found no unused picture for never appears in it.

`evidence_tool_shown` and `seam_shown` still exist and still mean the first and
second tool. They are the old fixed shape, kept alive for the send list and for
any run generated before this change.

The prompt and the audit both read the array. The prompt now also states the
picture count outright, because a model told "four screenshots are attached" in
one place and handed six in another will describe four.

## Shots that say they are not running

Seven pictures in the library announce, in their own filename, that the thing
is switched off: `agents-empty-state`, `agent-paused-inactive`,
`campaigns-list-draft`, `flow-list-inactive`, `landing-pages-sample-draft`,
`flow-canvas-upsell-draft`. They were captured while a tool was being set up.
They are honest, and a buyer opening a PDF and finding an empty screen has
learned something we did not want to teach.

So they sort last everywhere and are only reached when a shape holds nothing
else. Every fallback — the pinned hint, the "their world" pattern list, the
"result" pattern list — is tried against the running shots first, and only then
widened. That ordering matters: `campaigns-list-draft` contains the word
*list*, so the result-shot fallback found it on the first cut even though six
running Instantly shots were sitting right there. A running picture the caption
describes loosely is worth more than a perfect pattern match on an empty
screen.

Shopify's **draft orders** are excluded from the rule on purpose. There, draft
is a product noun, not a confession.

One footnote worth keeping. The first version of that pattern used `\b` word
boundaries, and this node is emitted through a Python format string — Python
reads a lone backslash-b as a backspace character, so the regex shipped with
every boundary silently deleted and matched almost nothing. The pattern now
uses hyphen and underscore as its boundaries, which is what view names actually
separate on, and nothing in it needs escaping.
