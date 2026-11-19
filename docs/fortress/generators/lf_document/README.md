# lf_document, one renderer and the Lead gate (Fortress work order 1, Nov 19 2026)

Reference build in Python. The dashboard MCP tool `lf_document` ports `core.py` and `figures.py` 1:1.

- `core.py`: resolver v2 (rule technology-partner-offer v2), the What's next section in the shape of the Phase 2 handoff Seth sent on Nov 19 (business goals and where each stands, next fixed phase first, "What I'd recommend for you: Technology Partner", the monthly list built live from the service status table, everyday requests, why it fits, honesty line, close). Plan price, member discount and positioning are parsed from Pricing Standard section 10 at run time; 750 is refused.
- `figures.py`: rule client-document-figures. Figures are numbered in reading order by the renderer.
- `render.py`: handoff, audit, architecture, proposal and quote in the sent guide's layout.
- `lead_gate.py`: fails a missing What's next, What's next where the resolver said no, a plan item the status table does not support, an undated figure, figures out of order, and word check hits.
- `tests/test_samples.py`: synthetic data only (repo rule). Client fixtures live in the Fortress 2 project.

Render: `python3 render.py specs_proposal_sample.json accounts/direct_prospect_sample.json sources/rules_snapshot_2026-11-19.json out/sample.pdf`
