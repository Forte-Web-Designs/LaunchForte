# Fortress evidence library
Build-proof screenshots, sorted by SHAPE (the pattern), then tool.

Filename convention:  <shape>--<tool>--<view>.jpg

Folders are shapes. A shape folder holds every tool that implements it — that IS the
cross-tool fallback: when a lead's tool has no image, take another file from the same
folder, always ship the n8n canvas alongside it, and state the substitution out loud.

  _blockers/   honest intel: what is locked and why (not proof, keep anyway)
  _library/    overview and environment shots
  _rejects/    duplicates, mis-framed frames, and anything with leak risk. NEVER ship these.
  manifest.json  machine-readable index, with a per-shape list of which tools have proof

## Accuracy notes — read before attaching anything to a proposal
- **Every workflow BUILT in this work is an unpublished draft** — the 17 `LF DEMO:` n8n kits and
  the 8 `SAMPLE -` GoHighLevel workflows. None was ever published or activated.
- **Three pre-existing n8n workflows show a green "Published" badge**: Demo: Ecommerce Order Ops,
  Demo: Books Bridge, Demo: Lifecycle Engine. Those were already live before this work began —
  they serve the public demo pages on launchforte.com. Nothing here published them.
- All records shown are fictional sample data.
- Screenshots in `_rejects/` include seven frames whose demo payloads carry email domains that
  are not on the sample-data whitelist and could resolve to real businesses. They were pulled on
  the conservative reading. Do not ship them without checking those domains yourself.
