# Fortress build docs
Read this before taking on a build. Everything cross-links.

| File | What it answers |
|---|---|
| `FORTRESS-BUILD-PLAYBOOK.md` | **Start here.** 17 products. Per product: the real Upwork ask, the pain, how to build it, what will bite you, the upsell ladder, the line that lands, and the exact screenshots to attach. |
| `PRODUCT-KIT-STANDARD.md` | The method. What makes a pattern sellable, the workflow standard, the cross-tool matching ladder, the repeatable recipe. |
| `BUILD-LEDGER.md` | The running tab. Access held vs blocked, tool-by-tool gotchas, what is in each account. |
| `build-library.json` | Machine-readable registry: shape → n8n kit → tool implementations → status. |
| `kits/*.json` | 17 importable n8n workflows, 18 nodes each, built to the standard. Paste onto an n8n canvas to import. |
| `evidence-library/` | 310 screenshots in 22 shape folders. `manifest.json` indexes them. |
| `kitgen.py` | Generates a new standard-compliant kit from ~15 lines of spec. |
| `playbookgen.py` | Regenerates the playbook from the specs and the library. |

## The one rule that makes this work
The library is keyed by **shape** (the pattern), not by tool. When a lead's tool has no
screenshot, take another tool from the same shape folder and **always ship the n8n canvas
alongside it** — then say the substitution out loud: *"that build is in GoHighLevel, this one's
in HubSpot; the tool changes, the architecture doesn't."* Naming it reads as confidence.
Hiding it reads as a bait-and-switch the moment they notice.

## Tools covered
n8n (54) · GoHighLevel (78) · HubSpot (49) · Shopify (33) · Stripe (13) · QuickBooks (12)

Every workflow pictured is an unpublished draft. Every record is fictional sample data.
