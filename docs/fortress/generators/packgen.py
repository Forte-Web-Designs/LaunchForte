#!/usr/bin/env python3
"""
packgen.py — rebuild an evidence pack PDF from the frames already captured
in docs/fortress/evidence-library, for a given shape and tool.

    python3 packgen.py <shape> <tool>

Reads docs/fortress/evidence-library/manifest.json for the frames tagged with
that shape and tool, and writes docs/fortress/evidence-pdfs/<shape>--<tool>.pdf:
landscape US letter, a cover page, then one page per frame. The layout numbers
below were measured off docs/fortress/evidence-pdfs/project-ops--notion.pdf so
a rebuilt pack looks the same as one that was assembled by hand.
"""
import json, os, sys

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.colors import Color, black
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import ImageReader

HERE = os.path.dirname(os.path.abspath(__file__))
FORTRESS = os.path.dirname(HERE)
LIBRARY = os.path.join(FORTRESS, "evidence-library")
MANIFEST = os.path.join(LIBRARY, "manifest.json")
OUT_DIR = os.path.join(FORTRESS, "evidence-pdfs")

PAGE_W, PAGE_H = landscape(letter)
MARGIN = 56
CONTENT_W = PAGE_W - 2 * MARGIN
BORDER_COLOR = Color(229 / 255, 231 / 255, 235 / 255)

FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
ASCENT, DESCENT = 0.718, -0.207  # Helvetica AFM metrics, same for bold

TITLE_TOP = 542.618       # cover title, top of text block
GAP_TITLE_SUBTITLE = 9.1
GAP_SUBTITLE_PARA = 33.2
GAP_PARA_CONNECTS = 21.6
FOOTER_BASELINE = 44.7

FRAME_HEADER_TOP = 567.93
GAP_HEADER_CAPTION = 12.4

IMAGE_LEFT = MARGIN
IMAGE_BOTTOM = MARGIN
IMAGE_MAX_W = CONTENT_W
IMAGE_AREA_TOP_CAP = 500  # never let an image climb past here, whatever the caption does


def leading_for(size):
    return size * 1.45


def wrap(text, font, size, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = (current + " " + word).strip()
        if stringWidth(candidate, font, size) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_block(c, text, font, size, top_y, max_width=CONTENT_W, x=MARGIN):
    """Draws left-aligned, possibly-wrapped text starting with its top edge at top_y.
    Returns the y at the bottom of the last line (mirrors the block's bbox y0)."""
    lines = wrap(text, font, size, max_width)
    leading = leading_for(size)
    c.setFont(font, size)
    baseline = top_y - ASCENT * size
    for i, line in enumerate(lines):
        c.drawString(x, baseline - i * leading, line)
    last_baseline = baseline - (len(lines) - 1) * leading
    return last_baseline + DESCENT * size


def draw_line(c, text, font, size, top_y, x=MARGIN):
    """Draws one line verbatim (spacing preserved) — for text that must never wrap."""
    c.setFont(font, size)
    baseline = top_y - ASCENT * size
    c.drawString(x, baseline, text)
    return baseline + DESCENT * size


def humanize(slug):
    return slug.replace("-", " ").replace("_", " ").strip()


def load_manifest():
    with open(MANIFEST) as f:
        return json.load(f)


def frames_for(shape, tool):
    manifest = load_manifest()
    matches = [
        img for img in manifest["images"]
        if img["shape"] == shape and img["tool"] == tool
    ]
    matches.sort(key=lambda img: img["view"])
    frames = []
    for img in matches:
        candidates = [
            os.path.join(LIBRARY, img["file"]),
            os.path.join(FORTRESS, img["file"]),
        ]
        path = next((p for p in candidates if os.path.isfile(p)), None)
        if path is None:
            print(f"warning: frame listed in manifest but not found on disk, skipping: {img['file']}", file=sys.stderr)
            continue
        frames.append({"view": img["view"], "path": path})
    return frames


def beat_for(index, total):
    if total <= 1:
        return "RESULT"
    if index == 0:
        return "SYSTEM"
    if index == total - 1:
        return "RESULT"
    return "THINKING"


def caption_for(view):
    words = humanize(view)
    words = words[:1].upper() + words[1:]
    if not words.endswith("."):
        words += "."
    return words


def draw_cover(c, shape, tool):
    product = " ".join(w.capitalize() for w in humanize(shape).split())

    y = draw_block(c, product, FONT_BOLD, 26, TITLE_TOP)
    y = draw_line(c, f"{shape}  ·  built in {tool}", FONT, 12, y - GAP_TITLE_SUBTITLE)

    paragraph = (
        f"This pack shows a working {humanize(shape)} build running in {tool}, "
        f"captured frame by frame from sample data."
    )
    y = draw_block(c, paragraph, FONT, 13, y - GAP_SUBTITLE_PARA)

    connects = (
        f"What it connects to: {humanize(shape)} sits inside the Launch Forte automation "
        f"library; every frame here is sample data only."
    )
    draw_block(c, connects, FONT, 11, y - GAP_PARA_CONNECTS)

    c.setFont(FONT, 9)
    c.drawString(
        MARGIN, FOOTER_BASELINE,
        "Launch Forte  ·  sample data in accounts we own  ·  no client information appears in any frame",
    )
    c.showPage()


def draw_frame_page(c, index, total, view, image_path):
    header = f"{index + 1} of {total}   {beat_for(index, total)}"
    y = draw_line(c, header, FONT_BOLD, 10, FRAME_HEADER_TOP)
    caption_bottom = draw_block(c, caption_for(view), FONT, 12, y - GAP_HEADER_CAPTION)

    reader = ImageReader(image_path)
    img_w, img_h = reader.getSize()

    area_top = min(IMAGE_AREA_TOP_CAP, caption_bottom - 20)
    max_h = area_top - IMAGE_BOTTOM
    scale = min(IMAGE_MAX_W / img_w, max_h / img_h)
    draw_w, draw_h = img_w * scale, img_h * scale
    x = IMAGE_LEFT + (IMAGE_MAX_W - draw_w) / 2
    y0 = IMAGE_BOTTOM

    c.drawImage(reader, x, y0, width=draw_w, height=draw_h)
    c.setStrokeColor(BORDER_COLOR)
    c.setLineWidth(0.7)
    c.rect(x, y0, draw_w, draw_h, stroke=1, fill=0)
    c.showPage()


def build(shape, tool):
    frames = frames_for(shape, tool)
    if not frames:
        print(f"error: no frames found for shape={shape!r} tool={tool!r} in {MANIFEST}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f"{shape}--{tool}.pdf")

    c = canvas.Canvas(out_path, pagesize=(PAGE_W, PAGE_H))
    c.setTitle(f"{shape} · built in {tool}")
    c.setFillColor(black)
    c.setStrokeColor(black)

    draw_cover(c, shape, tool)
    for i, frame in enumerate(frames):
        c.setFillColor(black)
        draw_frame_page(c, i, len(frames), frame["view"], frame["path"])

    c.save()
    print(f"wrote {out_path} ({len(frames)} frame page(s))")


def main():
    if len(sys.argv) != 3:
        print("usage: python3 packgen.py <shape> <tool>", file=sys.stderr)
        sys.exit(1)
    build(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
