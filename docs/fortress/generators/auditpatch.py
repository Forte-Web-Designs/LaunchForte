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

# What the patch relies on already existing in the node. If any of these are
# gone the node has been rewritten and this script must not guess.
REQUIRED = [
    ("the hard list", r"const hard = \[\]"),
    ("the letter",    r"const letter = String\(out\.coverLetter"),
    ("the script",    r"const loom = String\(out\.loomScript"),
    ("the channel",   r"const CHANNEL = \(run\.channel"),
    ("the throw",     r"throw new Error\('COCKPIT held the draft"),
]


def main():
    if len(sys.argv) < 2:
        print("usage: auditpatch.py <live-audit.js> [--check]")
        return 2
    live = open(sys.argv[1]).read()
    patch = open(PATCH).read()
    problems = 0

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
