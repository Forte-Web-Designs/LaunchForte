# Launch Forte proposal generator (the one approved process)

Card 535. Pricing Standard 6A.3 names this generator (`fill_proposal_v13.py`), the template (`Launch-Forte-Proposal-Template-v13.html`) and the calculator (`purchase_choice.py`). v12 and v11 are retired. Anything else that builds a client proposal PDF is not approved.

Stops before any send. Never publishes, activates or emails. Financing is off by default and refused by this entry point.

## Find it
Library: `lf_reference query="proposal PDF generator"` returns this playbook (path `playbooks/proposal-generator.md`). The full bundle, including binary assets, lives in the repo `Forte-Web-Designs/LaunchForte` at `docs/fortress/generators/proposal`. Clone it, never copy files by hand.

## Run it (any Front Desk, Architect or Fortress session)
1. Read the rules through the connector, every time. Call `lf_rules` for `pricing` (all pages), `technology-partner-offer`, `client-document-hard-rules`, `voice`. Save each result as returned, one text file per rule (pages appended in order). If a result is too long to save whole, the file may hold the readback header lines exactly as returned (RULE, source, sha256, FRESHNESS) and, for pricing, section 2 and section 10 verbatim. Never retype or invent anything else.
2. `python3 rules_from_readbacks.py --pricing pricing.txt --offer offer.txt --hard hard.txt --voice voice.txt --out rules.json`
   The helper refuses anything that is not LIVE or VERIFIED (if the connector reports the Voice Rules UNVERIFIED, nothing is built unless Seth has ruled to accept the BRAIN mirror and `--allow-mirrored-voice` is passed, which is written into the report), and takes the rate card and the monthly plan fee from the saved text.
3. Write the client spec JSON (copy `examples/ridgeline-spec.json`, a fictional sample). You supply approved client facts, outcome blocks and part kinds with quantities. You never type a price, a total, a milestone or the plan fee: all are computed. Spec fields: `buyer` (status prospect, eligible, active_client, unknown, opted_out; platform direct or upwork; signed_agreement; seth_opt_out; scope_approved), `fill` (every client token), `blocks`, `word_check_allow` (snippets of lines where "we" or "our" plainly means Seth and the client together).
4. `python3 lf_proposal.py --spec spec.json --rules rules.json --out ./out`
5. Exit 0 means the automated checks passed, 3 means they need a person, 2 means it failed closed. Then open every page image in `out/pages-*` and read it. A passing report is not a visual review.
6. Hand the PDF, `qa_report-*.json` and the page images to Seth for review (card comment or PM review). Seth decides what is sent.

## What the checks do
- Rules: read time under 24 hours, each rule LIVE or VERIFIED, rate card and plan fee parsed from the text, the retired $750 plan refused, shas carried into the report.
- Eligibility: the resolver decides whether the optional Technology Partner pages appear (direct prospects with approved scope only). Upwork, signed or active clients, opted out and unknown buyers get a proposal with no plan and no plan price.
- Order: problem and outcomes, solution, scope, fixed investment, then the optional plan. The plan price is never on the cover or before the investment.
- Pricing: every block total is the sum of rate card parts, the two milestones are exactly half (any even whole dollar total), no typed price accepted, no internal piece math in client copy.
- Wording: the Client Document Hard Rules word list over the final PDF text (list stamped with rule sha `ee99703ddff9`), unfilled tokens, footer overflow, page images.
- Technology Partner copy is limited to what the offer rule lists as operating today. Monitoring, backups, IT help and security are promised only as "the systems we agree to cover" and "depends on the access and tools your accounts allow".

## Tests
`python3 test_lf_proposal.py`, `python3 test_offer_source.py`, `python3 test_resolver_conformance.py`.

## Changing it
Changes to prices, plan fee or eligibility belong in the canonical rules, never here. Changes to this process go through a card and Lead review.
