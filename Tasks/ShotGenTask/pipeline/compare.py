"""Side-by-side comparison of a built page with a page from the approved sample PDF,
to check that spacing, colours, captions, balloons and borders match the look."""
from __future__ import annotations

from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont

from .paths import FONTS, SAMPLES, Batch, rel

SAMPLE_PDF = SAMPLES / "pdf" / "CHANDRUSH-OPENING-V04-STORY-CONTINUITY-REVISION.pdf"


def render_pdf_page(pdf: Path, index: int, dpi: int) -> Image.Image:
    doc = pymupdf.open(pdf)
    pix = doc[index].get_pixmap(dpi=dpi)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    doc.close()
    return im


def cmd_compare(batch: Batch, page: int, sample_page: int, which: str, dpi: int = 100) -> Path:
    suffix = {"final": "", "standin": "-STANDIN-PROOF", "placeholder": "-LAYOUT-PROOF", "latest": "-LATEST"}[which]
    folder = batch.output / "proofs" if which in ("standin", "placeholder") else batch.pdf_dir
    ours = folder / f"CH01-P{page:03d}{suffix}.pdf"
    if not ours.exists():
        raise SystemExit(f"{rel(ours)} not found; build it first.")
    a = render_pdf_page(SAMPLE_PDF, sample_page - 1, dpi)
    b = render_pdf_page(ours, 0, dpi)
    gap, label_h = 30, 44
    out_im = Image.new("RGB", (a.width + b.width + 3 * gap, max(a.height, b.height) + label_h + 2 * gap), (24, 28, 36))
    out_im.paste(a, (gap, gap + label_h))
    out_im.paste(b, (2 * gap + a.width, gap + label_h))
    d = ImageDraw.Draw(out_im)
    try:
        f = ImageFont.truetype(str(FONTS / "SourceSans3-Semibold.ttf"), 26)
    except OSError:
        f = ImageFont.load_default()
    d.text((gap, gap), f"SAMPLE · Opening V04 page {sample_page:02d}", font=f, fill=(215, 180, 104))
    d.text((2 * gap + a.width, gap), f"APPROACH1 · CH01-P{page:03d} ({which})", font=f, fill=(215, 180, 104))
    out = batch.compare_dir / f"COMPARE-CH01-P{page:03d}-vs-OPENING-P{sample_page:02d}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    out_im.save(out)
    print(f"Wrote {rel(out)}")
    return out
