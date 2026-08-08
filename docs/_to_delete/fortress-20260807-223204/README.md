# Fortress build docs
Read this before taking on a build. Everything cross-links.

| File | What it answers |
|---|---|
| `FORTRESS-BUILD-PLAYBOOK.md` | **Start here.** 17 products. Per product: the real Upwork ask, the pain, how to build it, what will bite you, the upsell ladder, the line that lands, and the exact screenshots to attach. |
| `PRODUCT-KIT-STANDARD.md` | The method: what makes a pattern sellable, the workflow standard, the cross-tool matching ladder, the repeatable recipe. |
| `BUILD-LEDGER.md` | The running tab: access held vs blocked, tool-by-tool gotchas, what is in each account. |
| `build-library.json` | Machine-readable registry: shape → n8n kit → tool implementations → status. |
| `kits/*.json` | 17 importable n8n workflows, 18 nodes each, built to the standard. Paste onto an n8n canvas to import. |
| `evidence-library/` | 374 filed screenshots in 21 shape folders. `manifest.json` indexes them and lists which tools cover each shape. |
| `kitgen.py` | Generates a new standard-compliant kit from ~15 lines of spec. |
| `differentiate.py` | Per-shape logic for the four nodes that would otherwise be boilerplate. |
| `playbookgen.py` | Regenerates the playbook from the specs and the library. |

## The one rule that makes this work
The library is keyed by **shape** (the pattern), not by tool. When a lead's tool has no
screenshot, take another tool from the same shape folder, **always ship the n8n canvas
alongside it**, and say the substitution out loud: *"that build is in GoHighLevel, this one's in
HubSpot; the tool changes, the architecture doesn't."* Naming it reads as confidence. Hiding it
reads as a bait-and-switch the moment they notice.

## Tool coverage
n8n · GoHighLevel · HubSpot · Shopify · Stripe · QuickBooks

## Accuracy notes — read before attaching anything to a proposal
- **Every workflow BUILT here is an unpublished draft**: the 17 `LF DEMO:` n8n kits and the 8
  `SAMPLE -` GoHighLevel workflows. None was published or activated.
- **Three PRE-EXISTING n8n workflows show a green "Published" badge** — Demo: Ecommerce Order Ops,
  Demo: Books Bridge, Demo: Lifecycle Engine. They were already live before this work began; they
  serve the public demo pages on launchforte.com. Nothing here published them.
- All records shown are fictional sample data.
- `evidence-library/_rejects/` holds 68 duplicates, mis-framed frames, and seven frames whose demo
  payloads carry email domains outside the sample-data whitelist. **Never ship from _rejects.**

## Housekeeping
`docs/_to_delete/` holds a superseded copy of this folder and the transfer zips. Delete it when
convenient — the sync bridge cannot remove files itself.
