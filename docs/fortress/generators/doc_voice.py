"""Document voice check (Seth, Nov 22 2026 2:38 and 2:39 PM CT, BRAIN rule:voice section DOCUMENT VOICE).

All documentation (proposals, quotes, audits, handoff guides, architecture documents, SOPs, intro decks, evidence
packs, the Technology Partner PDF): Launch Forte is the subject. Never we, us, our or our team. "I" stays only in the
opening paragraph of the Technology Partner section, accountability lines and the sign off. Client pages, recaps,
Loom scripts and client messages are not checked here (they stay in Seth's first person)."""
import re

# Spans where "I" is allowed, matched on whitespace normalised text.
ALLOWED = [
    r"After I build this, I would be happy to keep helping.*?asked me for anything new\.",   # proposal TP opening paragraph
    r"If you want me around afterwards.*?cancel anytime\.",                                  # audit TP opening paragraph
    r"I answer for the changes I make and for what I report, and I tell you plainly when something is outside what the plan covers\. Launch Forte.s monthly checks cover the systems we agree on and connect\.",   # Seth Nov 22 2026 2:42 PM CT, verbatim
    r"After I build this, I would be happy to keep helping with the technology side of your business too\.",
    r"I answer for the changes I make and for what I report, and I tell you plainly when something is outside what the plan covers\.",   # Seth Nov 22 2026 2:45 PM CT two page standard
    r"I will not call anything healthy that I have not checked\.",
    r"I only report something as checked once I have checked it[^.]*\.",
]
WE = re.compile(r"\b(we|We|WE|us|Us|our|Our|ours|ourselves|we're|We're|we'll|We'll|we've|We've)\b")
ME = re.compile(r"\b(I|I'm|I'll|I've|I'd|me|Me|my|My|mine)\b")


# Seth, Nov 22 2026 2:42 PM CT, hard rule for all client facing copy: Seth handles the work himself. Never bring in, refer to,
# hand off to or partner with a specialist, contractor, agency or anyone else.
OUTSIDE_HELP = re.compile(r"\b(quietly|specialists?|bring(?:s|ing)? in|refer(?:s|red|ring)? you|hand(?:s|ed|ing)? (?:it |this |them )?off|subcontract\w*)\b", re.I)


def outside_help(text):
    t = re.sub(r"\s+", " ", text or "")
    return ['wording: "%s" in "...%s..." (Seth handles the work himself, never a specialist, referral or hand off)'
            % (m.group(0), t[max(0, m.start() - 40):m.end() + 40].strip()) for m in OUTSIDE_HELP.finditer(t)]


# Seth, Nov 22 2026 3:06 PM CT: no documentation names Upwork (proposals, audits, handoff guides, architecture documents,
# the Technology Partner PDF, evidence packs). Only the Launch Forte intro deck may.
UPWORK = re.compile(r"\bup\s?work\b", re.I)


def problems(text):
    t = re.sub(r"\s+", " ", text or "")
    t = re.sub(r"(?:\b[A-Z]{1,3} ){2,}[A-Z]{1,3}\b", " ", t)   # letter spaced eyebrow labels (W H AT T H I S I S)
    t = re.sub(r"\bmy\.launchforte\.com\S*", " ", t)          # the demo link
    t = re.sub(r"\"[^\"]*\"|\u201c[^\u201d]*\u201d", " ", t)       # the client's own quoted words
    for a in ALLOWED:
        t = re.sub(a, " ", t, flags=re.S)
    out = outside_help(text)
    out += ['wording: "%s" (no documentation names Upwork, only the intro deck)' % m.group(0) for m in UPWORK.finditer(re.sub(r"\s+", " ", text or ""))]
    for m in WE.finditer(t):
        out.append('voice: "%s" in "...%s..." (Launch Forte is the subject, never we, us or our)' % (m.group(0), t[max(0, m.start() - 40):m.end() + 40].strip()))
    for m in ME.finditer(t):
        out.append('voice: "%s" in "...%s..." (I only in the TP opening paragraph, accountability lines and the sign off)' % (m.group(0), t[max(0, m.start() - 40):m.end() + 40].strip()))
    return out
