#!/usr/bin/env python3
"""
auditpatch.py — splice the evidence and link holds into the Audit node.

The Audit node is the one node in the Cockpit that is not generated. It is 75
lines of accumulated checks, every one of them earned by a draft that went out
wrong, and rewriting it from scratch to add two more would risk dropping one
silently. So this patches rather than regenerates: it takes the live body,
inserts the block from audit-evidence-patch.js immediately above the throw, and
refuses if anything about the shape is not what it expects.

    python3 auditpatch.py live-audit.js       # writes cockpit-audit-node.js
    python3 auditpatch.py live-audit.js --check
"""
import os, re, subprocess, sys

HERE  = os.path.dirname(os.path.abspath(__file__))
PATCH = os.path.join(HERE, "audit-evidence-patch.js")
OUT   = os.path.join(HERE, "cockpit-audit-node.js")

ANCHOR = "\nif (hard.length) {"

# Exact-text retunes applied to the live body alongside the splice. Each is
# (name, old, new) and each must match exactly once.
#
# The word ceiling: 460 was set when the letter was body plus close. It now
# carries a tool note, a gap note, the product paragraph and the answers block,
# and letters have been held at 473, 489 and 552 words. A held draft is worse
# than a long one — the letter goes to Seth, not to the buyer, and he is the one
# who decides what to cut. So the hard stop moves out to 550 and a soft note
# lands above 480, which tells him it ran long instead of eating the draft.
RETUNE = [
    ("the word ceiling",
     "if (words(letter) > 460) hard.push('The cover letter is too long (' + words(letter) + ' words).');",
     "if (words(letter) > 550) hard.push('The cover letter is too long (' + words(letter) + ' words).');\n"
     "else if (words(letter) > 480) soft.push('The cover letter runs ' + words(letter) + ' words, which is long. "
     "It ships either way — worth a read before you send.');"),
]

# What the patch relies on already existing in the node. If any of these are
# gone the node has been rewritten and this script must not guess.
REQUIRED = [
    ("the hard list", r"const hard = \[\]"),
    ("the letter",    r"const letter = String\(out\.coverLetter"),
    ("the script",    r"const loom = String\(out\.loomScript"),
    ("the channel",   r"const CHANNEL = \(run\.channel"),
    ("the throw",     r"throw new Error\('COCKPIT held the draft"),
]


# Real sentences from real sends. The first two are the defects. The rest are
# the honest prose the first cut of this check held a draft over, which is the
# more expensive failure of the two: a hold that cries wolf gets switched off.
FIXTURES = [
    # (letter, script, pack tool, seam tool, should hold?, why)
    ("Most of what I build is a product in my catalogue, and the Klaviyo side of yours closely "
     "mirrors my reachability audit. The attached screenshot shows every buyer in a store lined "
     "up against Klaviyo, sorted by spend.", "", "Shopify", None, True,
     "the real one: the pack was Shopify and the letter described a Klaviyo shot"),

    ("From your stack I have shipped in both Shopify and Klaviyo, and the attached screenshots "
     "come from a live Shopify and Klaviyo build of mine.", "", "Shopify", None, True,
     "claims the shots come from a Klaviyo build; the pack has no Klaviyo in it"),

    ("On backend, apps, and integrations, I have done this shape before, I synced a furniture "
     "retailer's Shopify orders into Xero automatically, daily, hands off, and the order state "
     "work in the screenshots runs through the orders API.", "", "Shopify", None, False,
     "true sentence about a real build; Xero is nowhere near a claim about the picture"),

    ("The screenshots show the same shape you would need here, and I have also shipped this "
     "inside HubSpot for a services client.", "", "Shopify", None, False,
     "the HubSpot clause is a separate claim about experience, not about the picture"),

    ("The attached screenshot shows the deal board after the escalation fires, in Pipedrive.",
     "", "Pipedrive", None, False, "the pack IS Pipedrive"),

    ("The far side is in the second shot: the same record once it lands in QuickBooks.",
     "", "Shopify", "QuickBooks", False, "QuickBooks is the seam shot, so it really is attached"),

    ("Upwork rules keep URLs out of proposals, so store links come over chat once you reply.",
     "", "Shopify", None, True, "promises a link on a reply rather than under contract"),

    ("Happy to walk it end to end once we are working together.",
     "I will send you the live one in the messages as soon as you reply.", "Shopify", None, True,
     "the video promises the live link on a reply"),

    ("Happy to walk the whole thing end to end once we are working together, screens and all.",
     "", "Shopify", None, False, "under contract wording, which is the wording we want"),

    ("The video walks through how I would sequence that first slice, and the attached sketch "
     "shows the shape of it on one page, with the place these builds usually bite marked on it.",
     "", None, None, False,
     "the sketch ships on every run, so referring to it is true even with no pack"),

    ("The attached sketch shows where the GoHighLevel side would sit once it is wired.",
     "", "Shopify", None, False,
     "naming a tool in a sentence about the SKETCH is not a claim about a screenshot"),

    ("The attached screenshots show the same board in Shopify.", "", None, None, True,
     "claims screenshots when the pack came back empty"),
]

HARNESS = """
%(patch)s
return hard;
"""


def run_fixtures(patch):
    import json as _json
    cases = [{"letter": a, "loom": b, "tool": c, "seam": d} for a, b, c, d, _, _ in FIXTURES]
    js = ("const CASES = " + __import__("json").dumps(cases) + ";\n"
          "function __run(c) {\n"
          "  const hard = [];\n"
          "  const CHANNEL = 'upwork';\n"
          "  const letter = c.letter, loom = c.loom;\n"
          "  const $ = () => ({ first: () => ({ json: {\n"
          "    evidence_tool_shown: c.tool, seam_shown: c.seam, evidence_count: c.tool ? 4 : 0 } }) });\n"
          + patch + "\n  return hard;\n}\n"
          "console.log(JSON.stringify(CASES.map(__run)));\n")
    path = os.path.join(HERE, "_probe_fixtures.js")
    open(path, "w").write(js)
    r = subprocess.run(["node", path], capture_output=True, text=True)
    os.remove(path)
    if r.returncode:
        print("  FAIL  fixture harness threw: " + r.stderr.strip().splitlines()[-1][:200])
        return 1
    results = __import__("json").loads(r.stdout)
    bad = 0
    for (letter, loom, tool, seam, expect, why), held in zip(FIXTURES, results):
        if bool(held) == expect:
            print("  ok    %s %s" % ("HOLD " if expect else "pass ", why))
        else:
            bad += 1
            print("  FAIL  %s — expected %s, got %s"
                  % (why, "a hold" if expect else "no hold", held or "nothing"))
    return bad


def main():
    patch = open(PATCH).read()

    if "--fixtures" in sys.argv or len(sys.argv) < 2:
        bad = run_fixtures(patch)
        print()
        print("RESULT: %s" % ("OK" if not bad else "%d fixture(s) failed. DO NOT DEPLOY." % bad))
        return 1 if bad else 0

    live = open(sys.argv[1]).read()
    problems = run_fixtures(patch)

    if "LF-AUDIT-EVIDENCE-START" in live:
        print("  ok    already patched — stripping the old block first")
        live = re.sub(r"/\* -+\n\s*LF-AUDIT-EVIDENCE-START.*?/\* LF-AUDIT-EVIDENCE-END \*/\n",
                      "", live, flags=re.S)

    for name, pat in REQUIRED:
        if re.search(pat, live):
            print("  ok    found %s" % name)
        else:
            print("  FAIL  %s is missing — the node is not the shape this patch expects" % name)
            problems += 1

    if live.count(ANCHOR) != 1:
        print("  FAIL  the insertion point appears %d times, expected 1" % live.count(ANCHOR))
        problems += 1

    if problems:
        print("\nRESULT: %d problem(s). DO NOT DEPLOY." % problems)
        return 1

    body = live.replace(ANCHOR, "\n" + patch + ANCHOR, 1)

    for name, old, new in RETUNE:
        if body.count(old) == 1:
            body = body.replace(old, new)
            print("  ok    retuned %s" % name)
        elif body.count(new) >= 1:
            print("  ok    %s already retuned" % name)
        else:
            print("  FAIL  %s: the line to retune appears %d times" % (name, body.count(old)))
            return 1

    probe = os.path.join(HERE, "_probe_audit.js")
    open(probe, "w").write("function __n($json, $, $input, items) {\n%s\n}\n" % body)
    r = subprocess.run(["node", "--check", probe], capture_output=True, text=True)
    os.remove(probe)
    if r.returncode:
        print("  FAIL  patched node does not parse: " + r.stderr.strip().splitlines()[-1][:140])
        return 1
    print("  ok    patched node parses as JavaScript")

    # the two new holds must actually be reachable
    for name, pat in [("the attachment-mismatch hold", r"so that picture is not in the email"),
                      ("the before-contract hold", r"before we are under contract")]:
        if pat.replace("\\", "") in body or re.search(pat, body):
            print("  ok    %s is present" % name)
        else:
            print("  FAIL  %s did not land" % name)
            return 1

    print("\n  live %d chars -> patched %d chars (+%d)" % (len(live), len(body), len(body) - len(live)))
    if "--check" not in sys.argv:
        open(OUT, "w").write(body)
        print("wrote %s" % os.path.basename(OUT))
    print("RESULT: OK")
    return 0


sys.exit(main())
