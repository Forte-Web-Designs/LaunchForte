#!/usr/bin/env python3
"""
packgen.py — rebuild an evidence pack PDF from the frames already captured
in docs/fortress/evidence-library, for one shape and one tool. Packs stop
being assembled by hand.

Usage:
    python3 packgen.py <shape> <tool>

Reads every docs/fortress/evidence-library/<shape>/<shape>--<tool>--*.jpg
frame and writes docs/fortress/evidence-pdfs/<shape>--<tool>.pdf: a cover
page (product name, shape/tool, pitch paragraph, "What it connects to:",
sample-data footer), then one page per frame ("N of M   BEAT", caption
above a centred image with a thin grey border) — landscape US letter, the
same shape as every pack already in evidence-pdfs/.
"""
import os
import sys
import glob

from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import ImageReader

HERE = os.path.dirname(os.path.abspath(__file__))
FORTRESS = os.path.dirname(HERE)
LIBRARY = os.path.join(FORTRESS, "evidence-library")
OUT_DIR = os.path.join(FORTRESS, "evidence-pdfs")

PAGE_W, PAGE_H = landscape(letter)
MARGIN = 56
CONTENT_W = PAGE_W - 2 * MARGIN

DARK = (17 / 255, 24 / 255, 39 / 255)
MUTED = (107 / 255, 114 / 255, 128 / 255)
BORDER = (229 / 255, 231 / 255, 235 / 255)

FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

FOOTER = ("Launch Forte  ·  sample data in accounts we own  ·  "
          "no client information appears in any frame")

# Product name and pitch paragraph per shape — Fortress editorial voice,
# kept in step with generators/heroes.py's SHAPES table.
PRODUCT = {
    'ai-assistant': 'The Straight Answer Desk',
    'ai-research-agent': 'The Research Desk',
    'alerting': 'The Watch',
    'approval-routing': 'The Approval Router',
    'books-reconciliation': 'The Reconciliation Build',
    'client-onboarding': 'The Onboarding Build',
    'cold-outreach': 'The Outreach Engine',
    'conversation-design': 'The Conversation Architecture',
    'data-collection': 'The Intake System',
    'data-model-architecture': 'The Data Layer',
    'document-assembly': 'The Document Build',
    'lead-routing': 'The Lead Router',
    'messaging-compliance': 'The Deliverability Build',
    'platform-migration': 'The Migration Build',
    'production-takeover': 'The Takeover Build',
    'project-ops': 'The Operations Board',
    'quote-follow-up': 'The Follow Up',
    'reactivation': 'The Win-Back',
    'reporting': 'The Reporting Layer',
    'scheduling': 'The Booking System',
    'stalled-deal-escalation': 'The Rescue',
    'storefront-upsell': 'The Upsell Engine',
    'system-sync': 'The Sync Build',
    'voice-agent-intake': 'The Voice Intake',
}

OPEN = {
    'ai-assistant': 'An assistant that guesses is worse than no assistant, because people stop trusting the answers and go back to phoning you.',
    'ai-research-agent': 'An agent that researches is easy. An agent that can show you where every sentence came from is the one you can actually put in front of a client.',
    'alerting': "Something breaks silently and the business hears it from a customer. That's the most expensive way to find out.",
    'approval-routing': 'Approvals sit in an inbox with no ladder, so the bottleneck is invisible until someone asks why nothing shipped.',
    'books-reconciliation': "The hours don't go into the matching. They go into the handful of rows a human has to judge.",
    'client-onboarding': "The first 48 hours set the tone for the whole engagement, and they're usually improvised.",
    'cold-outreach': "Volume isn't the problem. Deliverability and reply handling are, and they're what nobody sets up properly.",
    'conversation-design': 'Most chatbot projects are copywriting projects wearing an AI costume. The bot fails on the turn nobody scripted, not on the greeting everybody polished.',
    'data-collection': 'A half-record in the CRM is worse than no record, because it looks complete.',
    'data-model-architecture': 'Most CRM problems are data-model problems wearing a workflow costume.',
    'document-assembly': 'The document with a blank merge field is the one that goes out to a client.',
    'lead-routing': 'Five minutes is the whole game. A lead that waits an hour is worth a fraction of one answered fast.',
    'messaging-compliance': "Messaging that isn't registered and authenticated doesn't get delivered, and nobody tells you — it just quietly stops arriving.",
    'platform-migration': 'Migrations lose records quietly. Nobody finds out until the customer who was lost calls.',
    'production-takeover': "I don't change anything in week one. I map what it actually does versus what it's documented to do.",
    'project-ops': 'Most board problems are architecture problems: relations pointing at dead boards, no templates, and no way to see who is drowning.',
    'quote-follow-up': "Following up on a quote is nobody's actual job, so it quietly becomes nobody's.",
    'reactivation': 'Customers stop buying and nobody notices, because nothing is watching their own rhythm.',
    'reporting': "Most dashboards lie by omission. A zero that means 'unknown' looks exactly like a zero that means zero.",
    'scheduling': "Confirmation is the easy half. The money is in what happens when someone doesn't turn up.",
    'stalled-deal-escalation': "Your stalled-proposal problem is the one I'd fix first, because it's the one quietly costing you deals.",
    'storefront-upsell': 'Every order that ships without its obvious companion is margin you already paid to acquire.',
    'system-sync': 'Two systems disagreeing about the same customer is how a CRM quietly stops being trusted.',
    'voice-agent-intake': 'Calls outside business hours go to voicemail, and voicemail is where leads go to die.',
}

# "What it connects to:" — the seam this shape sits on, kept in step with
# STACK in generators/cockpit-evidence-node.js.
SEAM = {
    'ai-assistant': 'The model is not the product. The knowledge source it is grounded in, and the CRM it hands off to, are the product — and both live outside the model.',
    'ai-research-agent': 'The model is a renter, not an owner. The sources live on the web, the output has to land in something a person opens, and the agent is only the middle.',
    'alerting': 'The thing that breaks and the thing that tells you are never the same system, and the watchdog must not depend on the system it is watching.',
    'approval-routing': 'The request arrives in one place and the authority to approve lives in another. The audit trail has to span both or the band is unauditable.',
    'books-reconciliation': 'The payout processor and the ledger disagree by design — fees, timing, refunds. Reconciliation is not a report, it is a translation layer between two systems that count differently.',
    'client-onboarding': 'Won in the CRM has to become tasks in the project tool, a folder somewhere, and an intake the client actually returns. Three systems, one moment.',
    'cold-outreach': 'The sequencer owns the send and the CRM owns the truth about whether that person is already a customer. Emailing an existing client is the mistake that costs the account.',
    'conversation-design': 'The conversation happens in the messaging tool, the answer comes from a knowledge base, and the handoff lands in the CRM. Three systems, and the client only ever sees the seam when it fails.',
    'data-collection': 'The form and the system of record are almost never the same tool. Everything expensive happens in the gap: duplicates, half-records, and fields that mean different things on each side.',
    'data-model-architecture': 'The schema has to hold for every system that writes into it. A property that only makes sense in one tool is the one that breaks the reporting later.',
    'document-assembly': 'Every merge field is a read from another system. A document that assembles before its source has answered is how blanks reach a client.',
    'lead-routing': 'The form is in one system, the owner roster in another, and the SLA clock in neither. The clock is the integration.',
    'messaging-compliance': 'Registration lives with the carrier, the sending happens in the CRM, and neither tells the other when clearance lapses. Silence is the failure mode.',
    'platform-migration': 'Migration is two data models arguing. The mapping decision — which field becomes which property — is the entire job; the import is the easy part.',
    'production-takeover': 'An inherited system spans tools nobody documented together. Week one is drawing the map across all of them before touching any of them.',
    'project-ops': 'The board is downstream of the CRM and upstream of the invoice. Work arriving without its deal context is what makes a board go stale.',
    'quote-follow-up': 'The quote lives in the CRM and the reply lands in a mailbox. Stopping the cadence means the mailbox has to be able to reach back into the CRM.',
    'reactivation': 'Dormancy is a purchase-history question and the message is a marketing-tool question. Neither system holds both halves.',
    'reporting': 'Every source counts a lead slightly differently. The reporting layer is where you decide, once and in writing, whose definition wins.',
    'scheduling': 'The calendar owns the slot, the messaging system owns the reminder, and the no-show recovery has to survive both. A reschedule that only updates one side is the classic failure.',
    'stalled-deal-escalation': 'The CRM knows the deal stalled. It does not know who to chase, on what ladder, or how to prove it chased. That state has to live somewhere the CRM cannot hold it.',
    'storefront-upsell': 'The store knows the order. The email tool knows the person. The companion mapping belongs to neither, so it needs a home that both can read.',
    'system-sync': 'This pattern IS the seam. Two systems, one record, and an echo gate so our own write coming back does not start a loop at 3am.',
    'voice-agent-intake': 'The call arrives at the phone system, the context lives in the CRM, and the booking is in the calendar. The caller experiences one thing; it is three.',
}

DEFAULT_OPEN = "Proof from a real build. Sample data only, nothing here was ever published or activated."
DEFAULT_SEAM = "This pattern sits inside a wider stack — ask and I'll show you the seam it needs."


def wrap(text, font, size, max_width):
    """Greedy word-wrap text to max_width at (font, size)."""
    words = text.split(" ")
    lines, line = [], ""
    for word in words:
        candidate = (line + " " + word).strip()
        if not line or stringWidth(candidate, font, size) <= max_width:
            line = candidate
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_wrapped(c, text, x, y, font, size, color, max_width, leading):
    """Draw text wrapped to max_width, one line per Tj. Returns the y just past the last line."""
    c.setFont(font, size)
    c.setFillColorRGB(*color)
    for line in wrap(text, font, size, max_width):
        c.drawString(x, y, line)
        y -= leading
    return y


def beat_for(index, total):
    if index == 0:
        return "SYSTEM"
    if index == total - 1:
        return "RESULT"
    return "THINKING" if index == 1 else "DETAIL"


def caption_for(path):
    """Turn the frame's view slug (the segment after the last '--') into a caption."""
    stem = os.path.splitext(os.path.basename(path))[0]
    view = stem.split("--")[-1]
    words = view.replace("-", " ").replace("_", " ").strip()
    if not words:
        return "Frame."
    sentence = words[0].upper() + words[1:]
    return sentence + "."


def draw_cover(c, shape, tool):
    product = PRODUCT.get(shape, shape.replace("-", " ").title())
    c.setFont(FONT_BOLD, 26)
    c.setFillColorRGB(*DARK)
    c.drawString(MARGIN, 522, product)

    c.setFont(FONT, 12)
    c.setFillColorRGB(*MUTED)
    c.drawString(MARGIN, 498, f"{shape}  ·  built in {tool}")

    paragraph = OPEN.get(shape, DEFAULT_OPEN)
    draw_wrapped(c, paragraph, MARGIN, 452, FONT, 13, DARK, CONTENT_W, 19)

    seam = SEAM.get(shape, DEFAULT_SEAM)
    connects = f"What it connects to: {seam}"
    draw_wrapped(c, connects, MARGIN, 400, FONT, 11, MUTED, CONTENT_W, 16)

    c.setFont(FONT, 9)
    c.setFillColorRGB(*MUTED)
    c.drawString(MARGIN, 44, FOOTER)
    c.showPage()


def draw_frame(c, index, total, path):
    beat = beat_for(index, total)
    c.setFont(FONT_BOLD, 10)
    c.setFillColorRGB(*MUTED)
    c.drawString(MARGIN, 560, f"{index + 1} of {total}   {beat}")

    caption = caption_for(path)
    caption_bottom = draw_wrapped(c, caption, MARGIN, 536, FONT, 12, DARK, CONTENT_W, 17)

    image = ImageReader(path)
    iw, ih = image.getSize()
    aspect = iw / ih

    max_h = max(caption_bottom - 20 - MARGIN, 40)
    w, h = CONTENT_W, CONTENT_W / aspect
    if h > max_h:
        h = max_h
        w = h * aspect

    x = MARGIN + (CONTENT_W - w) / 2
    y = MARGIN
    c.drawImage(image, x, y, w, h)
    c.setStrokeColorRGB(*BORDER)
    c.setLineWidth(0.7)
    c.rect(x, y, w, h, stroke=1, fill=0)
    c.showPage()


def main():
    if len(sys.argv) != 3:
        print("usage: python3 packgen.py <shape> <tool>", file=sys.stderr)
        sys.exit(1)

    shape, tool = sys.argv[1], sys.argv[2]
    pattern = os.path.join(LIBRARY, shape, f"{shape}--{tool}--*.jpg")
    frames = sorted(glob.glob(pattern))
    if not frames:
        print(f"no frames found for {pattern}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f"{shape}--{tool}.pdf")

    c = canvas.Canvas(out_path, pagesize=(PAGE_W, PAGE_H))
    draw_cover(c, shape, tool)
    for i, frame in enumerate(frames):
        draw_frame(c, i, len(frames), frame)
    c.save()

    print(f"wrote {out_path}: {len(frames)} frames")


if __name__ == "__main__":
    main()
