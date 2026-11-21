"""Draw measured page models to PDF (ReportLab, fonts embedded) and PNG (PyMuPDF).

Drawing order = reading order: background, border, each panel's art and frame,
then every text element in manuscript order, then the page number. The PDF text
layer therefore reads in story order, which the audit relies on.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pymupdf
from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as rl_canvas

from .art import prepare_embed
from .design import register_fonts, tokens
from .layout import PageModel
from .paths import Batch, rel
from .shapes import Page, draw_balloon, draw_border, draw_caption_box

TITLE = "ChandRush: The Midnight Mela"


def draw_page(c, model: PageModel, batch: Batch, show_zones: bool = False) -> dict:
    T = tokens()
    W, H = T["page"]["width_pt"], T["page"]["height_pt"]
    pg = Page(c, W, H)
    th = model.theme
    record = {"page": model.page, "page_id": model.page_id, "theme": model.theme_name, "border": model.border,
              "mode": model.mode, "panels": []}

    pg.rect(0, 0, W, H, fill=th["bg"])
    draw_border(pg, model.border, th)

    for pm in model.panels:
        x0, y0, x1, y1 = pm.frame
        entry = {"panel_id": pm.panel_id, "frame": list(pm.frame), "art_kind": pm.art_kind,
                 "art": rel(pm.art_path) if pm.art_path else None, "art_sha256": pm.art_sha256}
        if pm.art_path and pm.placement:
            src, (ix, iy, iw, ih) = prepare_embed(pm.art_path, pm.placement, batch.cache_dir / "embed")
            c.saveState()
            clip = c.beginPath()
            clip.rect(x0, pg.y(y1), x1 - x0, y1 - y0)
            c.clipPath(clip, stroke=0, fill=0)
            c.drawImage(ImageReader(str(src)), ix, pg.y(iy + ih), iw, ih)
            c.restoreState()
            entry.update({"effective_ppi": round(pm.placement.ppi, 1),
                          "visible_crop_px": [round(v, 1) for v in pm.placement.crop_px],
                          "image_px": [pm.placement.img_w, pm.placement.img_h]})
        pg.rect(x0, y0, x1, y1, stroke=th["accent"], width=T["frame"]["stroke_pt"])
        record["panels"].append(entry)

    texts = sorted(model.all_texts, key=_reading_key(model))
    for ti in texts:
        _draw_text_item(pg, ti, th, model)
        if show_zones:
            pg.c.setDash(2, 2)
            pg.rect(*ti.box, stroke="#4fd9ff", width=0.5)
            pg.c.setDash()

    pn = T["page_number"]
    c.setFont(pn["font"], pn["size"])
    pg.fill_color(pn["color_on_dark"] if th.get("dark", True) else pn["color_on_light"])
    c.drawRightString(pn["right_x"], pg.y(pn["baseline_y"]), f"{model.page:02d}")

    record["texts"] = [{"block_id": t.block_id, "panel_id": t.panel_id, "type": t.type, "box": [round(v, 1) for v in t.box],
                        "lines": t.lines, "speaker": t.speaker,
                        "tail": t.tail, "tail_source": t.tail_source} for t in texts]
    return record


def _reading_key(model: PageModel):
    order = {}
    i = 0
    for pm in model.panels:
        for t in pm.texts:
            order[t.block_id] = i
            i += 1
    for t in model.page_texts:
        order[t.block_id] = i
        i += 1
    return lambda t: order.get(t.block_id, 999)


def _draw_text_item(pg: Page, ti, th, model: PageModel):
    T = tokens()
    c = pg.c
    x0, y0, x1, y1 = ti.box
    if ti.type == "caption":
        s = T["caption"]
        seed = int(hashlib.md5(ti.block_id.encode()).hexdigest()[:8], 16)  # stable across runs
        draw_caption_box(pg, x0, y0, x1 - x0, y1 - y0, th["caption_fill"], th["speckle"], s["radius"],
                         s["speckle_density_per_pt2"], s["speckle_radius"], seed=seed)
        c.setFont(ti.font, ti.size)
        pg.fill_color(ti.color)
        for i, line in enumerate(ti.lines):
            c.drawString(x0 + s["pad_x"], pg.y(ti.first_baseline + i * ti.leading), line)
    elif ti.type == "balloon":
        s = T["balloon"]
        draw_balloon(pg, x0, y0, x1 - x0, y1 - y0, s["radius"], s["fill"], s["stroke"], s["stroke_pt"], ti.tail)
        c.setFont(ti.font, ti.size)
        pg.fill_color(ti.color)
        cx = (x0 + x1) / 2
        for i, line in enumerate(ti.lines):
            c.drawCentredString(cx, pg.y(ti.first_baseline + i * ti.leading), line)
    elif ti.type == "reader":
        c.setFont(ti.font, ti.size)
        pg.fill_color(ti.color)
        for i, line in enumerate(ti.lines):
            y = pg.y(ti.first_baseline + i * ti.leading)
            if ti.align == "center":
                c.drawCentredString((x0 + x1) / 2, y, line)
            elif ti.align == "right":
                c.drawRightString(x1, y, line)
            else:
                c.drawString(x0, y, line)


def build_pdf(models: list[PageModel], batch: Batch, out_pdf: Path, show_zones: bool = False) -> list[dict]:
    register_fonts()
    T = tokens()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    # initialFontName keeps ReportLab from adding an unused, unembedded Helvetica to every page.
    c = rl_canvas.Canvas(str(out_pdf), pagesize=(T["page"]["width_pt"], T["page"]["height_pt"]), pageCompression=1,
                         initialFontName="SourceSans3-Regular", initialFontSize=8)
    c.setTitle(f"{TITLE} — {', '.join(m.page_id for m in models)}")
    c.setAuthor("ChandRush Approach1 pipeline")
    c.setSubject("Review proof. Text from Scripts/CH01_V07_PANEL_MANIFEST.json; layout by Approach1.")
    records = []
    for m in models:
        records.append(draw_page(c, m, batch, show_zones))
        c.showPage()
    c.save()
    return records


def pdf_to_pngs(pdf: Path, out_dir: Path, dpi: int = 300, prefix: str | None = None) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(pdf)
    outs = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=dpi)
        name = f"{prefix or pdf.stem}{'' if doc.page_count == 1 else f'-{i + 1:02d}'}.png"
        path = out_dir / name
        pix.save(path)
        outs.append(path)
    doc.close()
    return outs


def contact_sheet(pngs: list[Path], out: Path, cols: int = 3, thumb_w: int = 900) -> Path:
    thumbs = []
    for p in pngs:
        with Image.open(p) as im:
            im = im.convert("RGB")
            thumbs.append(im.resize((thumb_w, int(im.height * thumb_w / im.width)), Image.LANCZOS))
    if not thumbs:
        raise SystemExit("No pages to put on the contact sheet.")
    th_h = thumbs[0].height
    rows = (len(thumbs) + cols - 1) // cols
    gap = 24
    sheet = Image.new("RGB", (cols * thumb_w + (cols + 1) * gap, rows * th_h + (rows + 1) * gap), (24, 28, 36))
    for i, t in enumerate(thumbs):
        r, col = divmod(i, cols)
        sheet.paste(t, (gap + col * (thumb_w + gap), gap + r * (th_h + gap)))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out


def write_build_record(batch: Batch, records: list[dict], name: str) -> Path:
    out = batch.output / f"{name}.build.json"
    out.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
