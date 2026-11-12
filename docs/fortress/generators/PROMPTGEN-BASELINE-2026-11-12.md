# promptgen.py baseline, Nov 12 2026 (card 538)

promptgen.py reports 24 failing checks, the same 24 before and after the card 538 changes (measured on main at f1e8618 and on this branch).
None of them touch the offer, the plan price or the pricing rate card. The two checks that do (`one ongoing plan, price read from the canonical rule`
and `no second monthly number`) pass.

The 24 are about other parts of the prompt: wording bans that the prompt text itself quotes (demo, demonstration, not a named client, image link),
reference build and testimonial handling, the answers block delimiter, the proof block wiring, link rules and the video framing.
They predate this card, are unrelated to pricing, and belong to separate Cockpit prompt work. They are not fixed here and not hidden.

Offer path checks that must stay green: `python3 docs/fortress/generators/offer-copies-check.py` and `node docs/fortress/generators/offer-integration-test.js`.
