#!/usr/bin/env python3
"""
promptgen.py — build and VALIDATE the Cockpit's "Prompt of Record" node.

Why this exists.

Every other node in the Cockpit comes out of a generator. This one did not. It
was hand-maintained inside n8n, which meant two things: nobody could diff it,
and when a wrapper got applied to it three times over — 21,946 characters
becoming 58,296 — nothing anywhere failed. It sat in the editor one Publish
click from going live, and the only reason it was caught was somebody counting
characters by hand.

So the body lives in git now, in prompt-of-record.js next to this file, and this
script is the thing that refuses to ship a broken one. It does not rewrite the
prompt. It asserts what must be true about it and then emits the deployable
node, which is the whole job:

  - it must parse as JavaScript
  - __walk must appear exactly 4 times. The triple-wrap read 12. That count is
    the corruption signature, and it is the check that would have caught it.
  - the voice rules Seth set must be present, and the wording he banned absent
  - the size must be in the band a real prompt occupies

Run it, and if it prints anything other than OK, do not deploy.

    python3 promptgen.py            # validate + write cockpit-prompt-node.js
    python3 promptgen.py --check    # validate only, exit 1 on failure
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "prompt-of-record.js")
OUT  = os.path.join(HERE, "cockpit-prompt-node.js")

# The corruption signature. A clean prompt mentions __walk four times: the
# helper and its three call sites. The triple-wrapped one mentioned it twelve.
WALK_EXPECTED = 4

# Seth's voice rules, as assertions rather than hopes. Each entry is
# (human name, regex that must be found).
MUST_CONTAIN = [
    ("questions answered last",
     r"answered LAST, in a block at the very bottom"),
    ("no preamble before the answers",
     r"never write\s*',\s*'\"on your questions\"|on your questions"),
    ("product framing, not a demo",
     r"framed as a PRODUCT rather than a demo"),
    ("similar and buildable, never a perfect fit",
     r"similar and definitely buildable"),
    ("the shoelaces line for tools we have not used",
     r"shoelaces versus"),
    ("write-versus-flag is the decision that shapes the build",
     r"allowed to WRITE versus"),
    ("monitoring retainer floor",
     r"\$750 a month"),
    ("ongoing retainer floor",
     r"\$2,500 a month"),
    ("retainer is a conversation that scales",
     r"treat it as a conversation, not a fixed line"),
    ("the derived price stands",
     r"Never round it, never end it in 997"),
    ("no hourly anything",
     r"no hourly rates, no hour counts"),
    ("the real track record is in the prompt, not a placeholder",
     r"THE TRACK RECORD\. REAL, AND THE ONLY BUILDS"),
    ("the one testimonial on file is present",
     r"6 Months to Speech"),
    ("the eight-page proposal shape is specified",
     r"EIGHT PAGES, THIS ORDER"),
    ("the proof block is actually wired into the payload",
     r"__PRICING_BRIEF \+ __PROOF|__PRICING_BRIEF\+__PROOF"),
    ("the brief targets the system prompt by name, not the longest string",
     r"o\.payload\.system = o\.payload\.system \+ __PRICING_BRIEF"),
    ("the answers block is delimited so ordering can be enforced",
     r"---ANSWERS--- on its own"),
    ("the model does not write its own sign off",
     r"Do not write a sign off yourself"),
    ("the video only promises what is attached",
     r"Only promise what is actually attached"),
    ("the video frames the shots as a shipped product, not a one-to-one fit",
     r"built and shipped\s*',\s*'multiple times|shipped\s+multiple times|may not be a one to one fit"),
    # Seth, Aug 8: "you cant send links until we are under contract. on upwork
    # it's not a matter of just getting into chat, you have to be under
    # contract." Getting a reply is not the unlock, so the prompt may not say
    # it is.
    ("links only travel once we are under contract",
     r"UNDER CONTRACT"),
    ("the earlier triggers are named so the model cannot reach for one",
     r"once you reply, once we are in chat, over chat"),
    # Seth, Aug 8: "the pdf on this one doesnt match what youre saying. theres
    # no klaviyo in those pdfs." Two selectors picked evidence independently.
    ("the attached pack is listed and declared the whole truth",
     r"WHAT IS ACTUALLY ATTACHED TO THIS EMAIL"),
    ("the tools the pictures are in are named explicitly",
     r"THE ONLY TOOLS THE PICTURES ARE IN"),
    ("a reference build the pack did not attach is filtered out",
     r"__attachedSlugs\.indexOf\(__slug\(r\.tool\)\)"),
    ("the close is gated on the pack, not on a reference build",
     r"if \(__refs\.length \|\| __shots\.length\)"),
    # Seth, Aug 8: "always own it. dont say 'the upsell engine' call it 'my
    # upsell engine' in all posts."
    ("the product is owned, never given a definite article",
     r"ALWAYS OWN THE PRODUCT"),
    ("the product name is handed over with my in front of it",
     r"put my in front of it: my "),
    ("the stored article is stripped before the name is handed over",
     r"product_name\)\.replace\(/\^\\s\*\(\?:the\|an\?\)\\s\+/i"),
    ("the link rule is one plain sentence, not a clause",
     r"Upwork does not allow sharing links before we are under contract"),
]

# Wording that must never reach a buyer. These are the phrases that made our own
# evidence sound like a toy: it is a product in the catalogue, and it is running.
MUST_NOT_CONTAIN = [
    ("calls the evidence a demonstration", r"\bdemonstration\b"),
    ("calls the evidence a demo",          r"\bdemo data\b|\bdemo instance\b|\btest account\b"),
    ("disowns it as not a real client",    r"not a named client|rather than a named client"),
    ("leaves an image placeholder",        r"IMAGE TO EMBED|\[IMAGE LINK\]|image link"),
    ("leaves a proposal token unfilled",   r"\[BUILD \d|\[TESTIMONIAL"),
    ("promises a link on reply instead of under contract",
     r"in the chat after they reply|links? (?:come|comes|will come) over chat|once they reply"),
]

# A real prompt sits in this band. Well under it means something truncated the
# body; well over it means something wrapped it.
SIZE_BAND = (18000, 45000)


def fail(msg):
    print("  FAIL  " + msg)
    return 1


def main():
    check_only = "--check" in sys.argv
    if not os.path.exists(SRC):
        print("FAIL: %s is missing. That file is the source of record." % SRC)
        return 2
    body = open(SRC).read()
    problems = 0

    # ---- 1. does it parse -------------------------------------------------
    probe = os.path.join(HERE, "_probe.js")
    open(probe, "w").write("function __node($json, $, $input, items) {\n%s\n}\n" % body)
    r = subprocess.run(["node", "--check", probe], capture_output=True, text=True)
    os.remove(probe)
    if r.returncode:
        problems += fail("does not parse as JavaScript: " + r.stderr.strip().splitlines()[-1][:120])
    else:
        print("  ok    parses as JavaScript")

    # ---- 2. the corruption signature --------------------------------------
    walks = len(re.findall(r"__walk", body))
    if walks != WALK_EXPECTED:
        problems += fail("__walk appears %d times, expected %d. %s"
                         % (walks, WALK_EXPECTED,
                            "That is the wrapper-applied-more-than-once signature."
                            if walks > WALK_EXPECTED else "Something stripped the wrapper."))
    else:
        print("  ok    __walk appears %d times" % walks)

    # ---- 3. size band -----------------------------------------------------
    lo, hi = SIZE_BAND
    if not (lo <= len(body) <= hi):
        problems += fail("%d chars, outside the %d-%d band" % (len(body), lo, hi))
    else:
        print("  ok    %d chars, inside the band" % len(body))

    # ---- 4. the rules that must be there ----------------------------------
    for name, pattern in MUST_CONTAIN:
        if re.search(pattern, body, re.I):
            print("  ok    %s" % name)
        else:
            problems += fail("missing rule: %s" % name)

    # ---- 5. the wording that must not ------------------------------------
    # Scanned line by line, skipping the lines that NAME the banned wording in
    # order to ban it. A prohibition mentioning "demonstration" is the fix, not
    # the bug, and a checker that cannot tell the two apart is noise.
    # The ban list is fenced in the source with LF-BANLIST markers, because a
    # heuristic that guesses which lines are prohibitions gets the continuation
    # lines wrong. Fences are exact.
    prose_lines, skipping = [], False
    for l in body.split("\n"):
        if "LF-BANLIST-START" in l: skipping = True;  continue
        if "LF-BANLIST-END"   in l: skipping = False; continue
        if not skipping: prose_lines.append(l)
    lines = prose_lines
    prose = "\n".join(lines)
    for name, pattern in MUST_NOT_CONTAIN:
        hit = re.search(pattern, prose, re.I)
        if hit:
            line = next(l for l in lines if re.search(pattern, l, re.I))
            problems += fail("%s — found %r in: %s"
                             % (name, hit.group(0), line.strip()[:90]))
        else:
            print("  ok    no %s" % name)

    print()
    if problems:
        print("RESULT: %d problem(s). DO NOT DEPLOY." % problems)
        return 1

    if not check_only:
        open(OUT, "w").write(body)
        print("wrote %s: %d chars" % (os.path.basename(OUT), len(body)))
    print("RESULT: OK")
    return 0


sys.exit(main())
