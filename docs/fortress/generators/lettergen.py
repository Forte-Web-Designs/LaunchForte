#!/usr/bin/env python3
"""
lettergen.py — build and TEST the Cockpit's "Parse Outputs" node.

Parse Outputs used to do one job: turn the model's reply into JSON or fail
loudly. It now does a second one, and the second one is the point.

The letter's shape — body, then sign off, then the buyer's questions — was a
request in the prompt. Across five live sends the model honoured it three times:
two letters had no sign off at all, one put the questions above it, and the Loom
script promised screenshots on two of the three sends that actually had them.
Asking nicely has a ceiling and that was it.

So the order is decided in code now. The model writes the parts; this node puts
them in sequence, guarantees exactly one sign off, strips the scaffolding the
model leaves behind, and makes the video promise match what is really attached.

The fixtures below are the real letter shapes from live runs 26240, 26272 and
26274. If a change to the normaliser breaks one of them it breaks a letter that
actually went to a buyer, which is the only test worth having.

    python3 lettergen.py            # test + write cockpit-parse-node.js
    python3 lettergen.py --check    # test only, exit 1 on failure
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "parse-outputs.js")
OUT  = os.path.join(HERE, "cockpit-parse-node.js")

# The three shapes live runs actually produced.
FIXTURES = [
    {
        "name": "questions last, no sign off at all (runs 26272, 26273)",
        "letter": "Hey, reading the post it sounds like you want the orders to stop being retyped.\n\n"
                  "One thing worth knowing up front about Shopify.\n\n"
                  "Again, this needs more conversation, but most of what I build is a product in my catalogue.\n\n"
                  "I am on Central time, so Eastern standups are easy.\n\n"
                  "From your stack I have shipped in n8n, Zapier and Shopify. The most complex thing I have "
                  "built and run is a 22 workflow estate, intake through reporting.",
        "shots": 4,
    },
    {
        "name": "sign off last, questions above it (run 26274)",
        "letter": "Hey, reading the post it sounds like you want transcripts summarised.\n\n"
                  "Straight up front, I have not used Gong.\n\n"
                  "Again, this needs more conversation, but this mirrors my research agent product.\n\n"
                  "From your stack I have shipped in n8n and OpenAI. The most complex thing I have built "
                  "and run is a production estate of 60 plus workflows.\n\n"
                  "Seth Forte",
        "shots": 3,
    },
    {
        "name": "stray label and a bracketed placeholder on top (run 26240)",
        "letter": "Blueprint\n\nIntro video: [LINK]\n\n"
                  "Hey, reading the post it sounds like you need somebody inside the accounts weekly.\n\n"
                  "Again, this needs more conversation, but this mirrors my reachability audit.\n\n"
                  "Seth Forte\n\n"
                  "---ANSWERS---\n\n"
                  "From your stack I have shipped in n8n and GoHighLevel.",
        "shots": 4,
    },
    {
        "name": "no attachments — the video must not promise a picture",
        "letter": "Hey, reading the post it sounds like a rebuild rather than an automation.\n\n"
                  "Seth Forte",
        "shots": 0,
        "script": "Hey, quick one.\n\nI am going to attach some screenshots so you can see it.\n\n"
                  "If it fits, great. No worries either way.",
    },
]

HARNESS = """
%(body)s
const __out = [];
for (const f of FIXTURES) {
  const ev = { evidence_count: f.shots };
  const $ = () => ({ first: () => ({ json: ev }) });
  const out = { coverLetter: f.letter,
                loomScript: f.script || 'Hey, quick one.\\n\\nHere is the sketch.\\n\\nIf it fits, great.',
                sketch: {} };
  const run = {};
  __out.push(__body($, out, run, f));
}
console.log(JSON.stringify(__out));
"""


def build_harness(body):
    # wrap the node body so it can be driven with fixtures instead of n8n globals
    inner = body.split("// ---------------------------------------------------------------------------", 1)[1]
    inner = "// ---" + inner
    fn = ("function __body($, out, run, f) {\n" + inner.replace(
        "return [{ json: { run, out, normalised } }];",
        "return { letter: out.coverLetter, script: out.loomScript, normalised: normalised };") + "\n}\n")
    return "const FIXTURES = " + json.dumps(FIXTURES) + ";\n" + fn + HARNESS % {"body": ""}


def main():
    check_only = "--check" in sys.argv
    body = open(SRC).read()
    problems = 0

    probe = os.path.join(HERE, "_probe_parse.js")
    open(probe, "w").write("function __n($json, $, $input, items) {\n%s\n}\n" % body)
    r = subprocess.run(["node", "--check", probe], capture_output=True, text=True)
    os.remove(probe)
    if r.returncode:
        print("  FAIL  does not parse: " + r.stderr.strip().splitlines()[-1][:120])
        return 1
    print("  ok    parses as JavaScript")

    harness = os.path.join(HERE, "_harness.js")
    open(harness, "w").write(build_harness(body))
    r = subprocess.run(["node", harness], capture_output=True, text=True)
    os.remove(harness)
    if r.returncode:
        print("  FAIL  harness threw: " + r.stderr.strip().splitlines()[-1][:200])
        return 1
    results = json.loads(r.stdout)

    for f, res in zip(FIXTURES, results):
        letter, script = res["letter"], res["script"]
        paras = [p.strip() for p in re.split(r"\n\s*\n", letter) if p.strip()]
        bad = []

        signoffs = [i for i, p in enumerate(paras) if re.match(r"^seth\s+forte[.,]?$", p, re.I)]
        if len(signoffs) != 1:
            bad.append("%d sign offs, expected exactly 1" % len(signoffs))

        answers_at = [i for i, p in enumerate(paras) if re.search(r"from your stack", p, re.I)]
        if answers_at:
            if answers_at[-1] != len(paras) - 1:
                bad.append("the answers are not the last paragraph")
            if signoffs and signoffs[0] > answers_at[0]:
                bad.append("the sign off comes after the answers")

        if re.search(r"\[[A-Z][A-Z0-9 _\-]{2,30}\]", letter):
            bad.append("a bracketed placeholder survived")
        if re.match(r"^(blueprint|draft|subject)\b", letter, re.I):
            bad.append("a stray label survived on the first line")
        if re.search(r"^-{2,}\s*ANSWERS", letter, re.M):
            bad.append("the delimiter survived into the letter")

        mentions = bool(re.search(r"screenshot", script, re.I))
        if f["shots"] and not mentions:
            bad.append("attachments exist but the video never mentions them")
        if not f["shots"] and mentions:
            bad.append("no attachments but the video promises screenshots")

        if bad:
            problems += 1
            print("  FAIL  %s" % f["name"])
            for b in bad:
                print("          - " + b)
        else:
            print("  ok    %s" % f["name"])

    print()
    if problems:
        print("RESULT: %d fixture(s) failed. DO NOT DEPLOY." % problems)
        return 1
    if not check_only:
        open(OUT, "w").write(body)
        print("wrote %s: %d chars" % (os.path.basename(OUT), len(body)))
    print("RESULT: OK")
    return 0


sys.exit(main())
