#!/usr/bin/env python3
"""Builds the two sample previews shown on the Technology Partner pages.
They use the stylesheets of the approved Technology Review and Forte Intelligence designs, with a fictional company and
made up figures. No client's data is used. Output: preview-review.png and preview-magazine.png.
Usage: make_previews.py <approved_report.html> <approved_newsletter.html>   (any approved issue; only its styles and logo are read)"""
import re, sys, os
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))

def parts(path):
    h = open(path).read()
    css = re.findall(r"<style[^>]*>(.*?)</style>", h, re.S)[0]
    logo = re.search(r'<img[^>]*src="(data:image[^"]+)"', h[h.find("<body"):]).group(1)
    return css, logo

W = 330  # pt, native width of each preview page
FIX = f"@page{{margin:0}}body{{margin:0;background:#fff}}.pg,.mp{{width:{W}pt!important;padding:0 20pt!important;height:auto!important}}.band{{margin:0 -20pt!important;padding:14pt 20pt 10pt!important}}.band h1{{font-size:20pt!important}}.band .sub{{font-size:11pt!important}}.meta{{gap:16pt!important}}.stats{{grid-template-columns:repeat(2,1fr)!important}}.stat{{padding:7pt 8pt 7pt 0!important}}.stat+.stat{{padding-left:8pt!important}}.stat:nth-child(3){{border-left:0!important;padding-left:0!important}}.stat:nth-child(n+3){{border-top:1px solid var(--rule)}}.tag-sample{{background:#FFF7ED;border:1pt solid #C2410C;color:#9A3412;font:700 6.4pt Helvetica,Arial,sans-serif;letter-spacing:.08em;text-transform:uppercase;padding:3pt 20pt;text-align:left}}"

def review(css, logo):
    return f'''<!doctype html><meta charset=utf-8><style>{css}{FIX}</style><body><div class="pg" style="padding-bottom:12pt">
<div class="tag-sample" style="margin:0 -20pt">Sample layout &middot; fictional company &middot; made up figures</div>
<div class="band"><img src="{logo}"><div class="eyebrow">Monthly Technology Review</div><h1>Sample Company</h1><div class="sub">Month and year</div>
</div>
<div class="inner" style="padding-top:9pt"><div class="num">01 &nbsp;OVERVIEW</div>
<p class="lead">What I looked at this month, which systems I read myself, and which parts of the path I have not yet confirmed.</p>
<div class="fb" style="margin:6pt 0"><div class="fq">What I am still checking</div><p>Anything I have not verified, named plainly so nothing is called healthy before it is checked.</p></div>
<div class="fb fa" style="margin:6pt 0"><div class="fq">What needs your approval</div><p>The decisions that are yours, with my recommendation, and nothing changed before you agree.</p></div>
<div class="stats" style="grid-template-columns:repeat(2,1fr)!important"><div class="stat"><div class="v">00 of 00</div><div class="l">A count checked against a second record</div><div class="s">Source, read on a date</div></div><div class="stat"><div class="v">0</div><div class="l">An item that needs a decision</div><div class="s">Source, read on a date</div></div></div>
</div></div></body>'''

def magazine(css, logo):
    return f'''<!doctype html><meta charset=utf-8><style>{css}{FIX}.mp{{height:auto!important;overflow:visible!important;padding:0 20pt!important}}.cover{{margin:0 -20pt!important;padding:14pt 20pt 12pt!important}}.cover h1{{font-size:20pt!important;line-height:1.05!important}}.cover .dk{{font-size:9pt!important}}.st .n{{font-size:17pt!important}}.stats{{grid-template-columns:repeat(3,1fr)!important}}.stat:nth-child(3){{border-left:1px solid var(--rule)!important;padding-left:8pt!important}}.stat:nth-child(n+3){{border-top:0}}.tiles{{grid-template-columns:1fr 1fr!important}}</style><body><div class="mag"><div class="mp" style="padding-bottom:12pt">
<div class="tag-sample" style="margin:0 -20pt">Sample layout &middot; fictional company &middot; made up figures</div>
<div class="cover"><img class="lg" src="{logo}"><div class="ey">Forte Intelligence | Month and year | for Sample Company</div><div class="kk">This month in your industry</div>
<h1>The headline of the month for your industry</h1>
<div class="dk">A short summary of what changed this month and why it matters to a business like yours. Every figure carries its source and the date it was read.</div></div>
<div style="margin-top:10pt"><div class="stats"><div class="st"><div class="n b">00</div><div class="l">A sourced figure from your field</div></div><div class="st"><div class="n">00</div><div class="l">A second sourced figure</div></div><div class="st"><div class="n o">00</div><div class="l">A third sourced figure</div></div></div>
<div class="tiles"><div class="tile"><div class="tg">Pages 2 to 4</div><h3>The people and the numbers</h3><p>What is happening in your market.</p></div><div class="tile"><div class="tg">Pages 5 to 9</div><h3>How others show up</h3><p>Examples from your industry.</p></div><div class="tile"><div class="tg">Pages 10 and 11</div><h3>Rules and tools</h3><p>Changes in the software and rules around you.</p></div><div class="tile"><div class="tg">Page 12</div><h3>Ideas to try</h3><p>What it could mean for your business.</p></div></div></div></div></div></body>'''

def main(rp, np_):
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": int(W*1.34), "height": 900}, device_scale_factor=3)
        for name, fn, src, sel in (("preview-review.png", review, rp, ".pg"), ("preview-magazine.png", magazine, np_, ".mp")):
            css, logo = parts(src)
            pg.set_content(fn(css, logo)); pg.wait_for_timeout(300)
            pg.locator(sel).first.screenshot(path=os.path.join(HERE, name))
            from PIL import Image
            im = Image.open(os.path.join(HERE, name)); h = {"preview-review.png": 1215, "preview-magazine.png": 1165}[name]
            im.crop((0, 0, im.size[0], h)).save(os.path.join(HERE, name))
        b.close()
    from PIL import Image
    a = Image.open(os.path.join(HERE, "preview-review.png")); c = Image.open(os.path.join(HERE, "preview-magazine.png"))
    gap = 40; H = max(a.size[1], c.size[1])
    out = Image.new("RGB", (a.size[0] + gap + c.size[0], H), "white")
    out.paste(a, (0, 0)); out.paste(c, (a.size[0] + gap, 0)); out.save(os.path.join(HERE, "preview-both.png"))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
