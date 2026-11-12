#!/usr/bin/env python3
"""Turn saved lf_rules readbacks into rules.json (card 535).

A session calls lf_rules for: pricing (all pages), technology-partner-offer, client-document-hard-rules, voice. It saves each tool
result, exactly as returned, into one text file per rule (pages of one rule appended in order). Then:

    python3 rules_from_readbacks.py --pricing pricing.txt --offer offer.txt --hard hard.txt --voice voice.txt --out rules.json

Nothing is retyped. The freshness line and sha come from each readback header; the generator refuses anything that is not LIVE or VERIFIED.
"""
import argparse, json, re, datetime, sys


def header(txt, name):
    fr = re.search(r"FRESHNESS:\s*([A-Z]+)", txt)
    sha = re.search(r"sha256\s+([0-9a-f]{12})", txt)
    if not fr or not sha:
        sys.exit("REFUSED: the %s readback has no FRESHNESS line or sha. Save the lf_rules result exactly as returned." % name)
    return fr.group(1), sha.group(1)


def section(txt, start, end):
    m = re.search(r"^## %s\..*?(?=^## %s\.)" % (re.escape(start), re.escape(end)), txt, re.S | re.M)
    if not m:
        sys.exit("REFUSED: pricing section %s not found in the readback (pages missing?)." % start)
    return m.group(0)


def main():
    ap = argparse.ArgumentParser()
    for k in ("pricing", "offer", "hard", "voice", "out"):
        ap.add_argument("--" + k, required=True)
    a = ap.parse_args()
    t = {k: open(getattr(a, k), encoding="utf-8").read() for k in ("pricing", "offer", "hard", "voice")}
    out = {"read_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    fr, sha = header(t["pricing"], "pricing")
    out["pricing"] = {"sha12": sha, "freshness": fr, "section_2": section(t["pricing"], "2", "3"), "section_10": section(t["pricing"], "10", "11")}
    for key, src in (("technology_partner_offer", "offer"), ("client_document_hard_rules", "hard"), ("voice", "voice")):
        fr, sha = header(t[src], src)
        out[key] = {"sha12": sha, "freshness": fr}
    json.dump(out, open(a.out, "w"), indent=2)
    print("wrote", a.out, {k: (v.get("sha12"), v.get("freshness")) for k, v in out.items() if isinstance(v, dict)})


if __name__ == "__main__":
    main()
