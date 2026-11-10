"""Build docs/putting-plastic-on-a-pedestal.pdf from README.md (the paper), so the GitHub page and the PDF match.

    pip install markdown pillow playwright && python -m playwright install chromium
    python3 tools/make_pdf.py [--out path.pdf]

Images are copied as downscaled JPEGs into a temp folder first (Chromium otherwise embeds them losslessly),
then the PDF is packed with qpdf if it is installed. Prints a heartbeat per step.

Copyright Matthew Armstrong (https://github.com/The-Dorkknight). PolyForm Noncommercial 1.0.0. No warranty.
"""
import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

import markdown
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "https://github.com/The-Dorkknight/putting-plastic-on-a-pedestal"
VERSION = "1.0"
DATE = "10 November 2026"

CSS = r"""
@page { size: A4; margin: 16mm 15mm 18mm 15mm; }
:root { --ink:#1F2433; --muted:#5A6072; --orange:#FF7A1A; --blue:#2D6CDF; --teal:#0FB5A4; --purple:#B04FCF; --sun:#FFB000; }
html { font-family: Inter, "DejaVu Sans", Arial, sans-serif; font-size: 10pt; color: var(--ink); line-height: 1.5; background:#fff; }
body { margin: 0; }
h1, h2, h3, .cover-title { font-family: Poppins, Inter, "DejaVu Sans", sans-serif; line-height: 1.2; }
h2 { font-size: 17pt; margin: 0 0 8pt 0; padding: 9pt 12pt; color: #fff; border-radius: 8pt;
     background: linear-gradient(90deg, var(--orange), #FF4E7A 55%, var(--blue)); break-after: avoid; }
h2.newpage { break-before: page; }
h3 { font-size: 12.5pt; color: var(--orange); margin: 14pt 0 4pt; break-after: avoid; }
p, li { orphans: 3; widows: 3; }
a { color: var(--blue); text-decoration: none; }
strong { color: #111; }
img { max-width: 100%; height: auto; display: block; margin: 8pt auto; break-inside: avoid; }
figure, p:has(> img) { break-inside: avoid; }
blockquote { margin: 10pt 0; padding: 8pt 12pt; border-left: 5pt solid var(--sun); background: #FFF6E0; border-radius: 0 8pt 8pt 0; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8.6pt; background: #EEF3FF; padding: 0 3pt; border-radius: 3pt; }
pre { background: #EEF3FF; padding: 8pt; border-radius: 6pt; white-space: pre-wrap; }
table { border-collapse: collapse; width: 100%; font-size: 8.6pt; margin: 8pt 0; break-inside: auto; }
th { background: var(--blue); color: #fff; text-align: left; padding: 4pt 5pt; }
td { padding: 3.5pt 5pt; border-bottom: 1px solid #E3E7F0; vertical-align: top; }
tr:nth-child(even) td { background: #F6F8FD; }
tr { break-inside: avoid; }
hr { border: 0; height: 3pt; background: linear-gradient(90deg, var(--teal), var(--blue), var(--purple)); border-radius: 2pt; margin: 14pt 0; }
sub { color: var(--muted); }
.cover { height: 258mm; display: flex; flex-direction: column; break-after: page; }
.cover img { width: 100%; margin: 0 0 12pt 0; border-radius: 10pt; }
.cover-title { font-size: 31pt; font-weight: 800; margin: 4pt 0 2pt; color: var(--ink); }
.cover-sub { font-size: 15pt; font-weight: 600; color: var(--orange); margin-bottom: 6pt; font-family: Poppins, Inter, sans-serif; }
.cover-tag { font-size: 10.5pt; color: var(--muted); font-style: italic; margin-bottom: 12pt; }
.cover-meta { font-size: 10pt; margin-bottom: 10pt; }
.pills { margin: 4pt 0 12pt; }
.pill { display: inline-block; padding: 3pt 9pt; border-radius: 99pt; font-weight: 700; font-size: 9pt; color: #fff; margin-right: 5pt; }
.cover blockquote { margin-top: auto; }
.toc { columns: 2; column-gap: 14pt; font-size: 10pt; }
.toc li { margin: 2pt 0; }
"""


def beat(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def shrink(src, tmp, maxw=1500, q=80):
    """Downscaled JPEG copy (white background); returns its file:// URI."""
    im = Image.open(src)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, "white")
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    out = os.path.join(tmp, os.path.splitext(os.path.basename(src))[0] + ".jpg")
    im.save(out, "JPEG", quality=q, optimize=True, progressive=True)
    return "file://" + out


def build(out):
    tmp = tempfile.mkdtemp(prefix="pedestal_pdf_")
    md = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    beat("README read")

    # cover: the art, the title block and the "physically untested" box come from the README itself
    box = re.search(r"^> \*\*Physically untested\.\*\*.*?$", md, flags=re.M).group(0)
    body = md[md.index("## Abstract"):]
    body = re.sub(r"## Contents\n.*?\n---\n", "", body, flags=re.S)       # the PDF gets its own contents list
    cover_img = shrink(os.path.join(ROOT, "docs", "images", "cover.jpg"), tmp, 1600, 84)

    exts = ["tables", "fenced_code", "sane_lists", "toc", "attr_list"]
    body_html = markdown.markdown(body, extensions=exts)
    box_html = markdown.markdown(box, extensions=exts)

    # images: compressed local copies; every heading 2 after the first two starts a page
    def img(m):
        src = m.group(1)
        if src.startswith("http"):
            return ""
        return m.group(0).replace(src, shrink(os.path.join(ROOT, src), tmp))
    body_html = re.sub(r'<img[^>]*src="([^"]+)"[^>]*>', img, body_html)
    body_html = re.sub(r'href="(?!#|https?:|mailto:)([^"]+)"', lambda m: f'href="{REPO}/blob/main/{m.group(1)}"', body_html)
    n = [0]

    def h2(m):
        n[0] += 1
        num = re.search(r'id="(\d+)-', m.group(0))
        # the long sections start a page; the short ones at the end run on
        return m.group(0).replace("<h2", '<h2 class="newpage"', 1) if num and int(num.group(1)) in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15) else m.group(0)
    body_html = re.sub(r"<h2[^>]*>", h2, body_html)
    toc = "".join(f'<li><a href="#{i}">{html.escape(re.sub("<[^>]+>", "", t))}</a></li>'
                  for i, t in re.findall(r'<h2[^>]*id="([^"]+)"[^>]*>(.*?)</h2>', body_html) if not t.startswith("Abstract"))
    beat(f"{body_html.count('<img')} figures compressed")

    cover = f"""<section class="cover">
<img src="{cover_img}" alt="Putting Plastic on a Pedestal">
<div class="cover-title">Putting Plastic on a Pedestal</div>
<div class="cover-sub">Experimental methods of plastic waste reduction for 3D printing</div>
<div class="cover-tag">Hollow towers, fat lobes, thin caps and tethers strung between walls:
a hobbyist's field guide and a defensive publication</div>
<div class="cover-meta"><b>Matthew Armstrong</b> (The-Dorkknight) &middot; Version {VERSION} &middot; First published {DATE}<br>
{REPO}</div>
<div class="pills"><span class="pill" style="background:#E5384B">PHYSICALLY UNTESTED</span>
<span class="pill" style="background:#2D6CDF">DEFENSIVE PUBLICATION</span>
<span class="pill" style="background:#0FB5A4">CC BY-SA 4.0</span></div>
{box_html}
</section>"""
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Putting Plastic on a Pedestal</title>
<style>{CSS}</style></head><body>{cover}
<h2 id="contents-pdf">Contents</h2><ol class="toc" start="0" style="list-style:none;padding-left:0">{toc}</ol>
{body_html}</body></html>"""
    hp = os.path.join(tmp, "paper.html")
    open(hp, "w", encoding="utf-8").write(page)
    beat("HTML written, printing with Chromium")

    from playwright.sync_api import sync_playwright
    footer = (f'<div style="font-size:7.5pt;color:#5A6072;width:100%;padding:0 15mm;display:flex;justify-content:space-between;'
              f'font-family:Inter,sans-serif"><span>Putting Plastic on a Pedestal &middot; v{VERSION} &middot; physically untested '
              f'&middot; CC BY-SA 4.0</span><span>page <span class="pageNumber"></span> / <span class="totalPages"></span></span></div>')
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-proxy-server", "--allow-file-access-from-files"])
        pg = b.new_page()
        pg.goto("file://" + hp, wait_until="load")
        pg.pdf(path=out, format="A4", print_background=True, display_header_footer=True,
               header_template="<span></span>", footer_template=footer,
               margin={"top": "16mm", "bottom": "18mm", "left": "15mm", "right": "15mm"})
        b.close()
    if shutil.which("qpdf"):
        packed = out + ".packed"
        subprocess.run(["qpdf", "--object-streams=generate", "--compress-streams=y", "--recompress-flate", out, packed], check=False)
        if os.path.exists(packed):
            os.replace(packed, out)
    shutil.rmtree(tmp, ignore_errors=True)
    beat(f"wrote {out} ({os.path.getsize(out) / 1e6:.2f} MB)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "putting-plastic-on-a-pedestal.pdf"))
    a = ap.parse_args()
    build(a.out)
    sys.exit(0)
