"""Turn a page contract + Director layout into a fully measured page model.

The layout file says WHERE things go (frames, caption anchors, balloon anchors,
tail targets). This module measures the real text with the real fonts, sizes
every box, aims every tail, picks the art for each frame, and reports anything
that does not fit. It never shrinks type or edits text to make things fit.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image

from . import state as st
from .art import Placement, cover_fit, fallback_size, legal_gen_size, placeholder_raster, sha256_file, standin_raster
from .design import TextTooWide, missing_glyphs, theme, tokens, widest, wrap_balanced, wrap_greedy
from .paths import PROJECT, Batch
from .shapes import plan_tail


@dataclass
class TextItem:
    type: str
    block_id: str
    panel_id: str
    text: str
    lines: list
    box: tuple
    font: str
    size: float
    leading: float
    color: str
    align: str
    first_baseline: float
    speaker: str | None = None
    tail: dict | None = None
    tail_source: str | None = None


@dataclass
class PanelModel:
    panel_id: str
    frame: tuple
    art_path: Path | None
    art_kind: str
    placement: Placement | None
    art_sha256: str | None
    gen_size: tuple
    fallback_size: tuple
    texts: list = field(default_factory=list)


@dataclass
class PageModel:
    page: int
    page_id: str
    theme_name: str
    theme: dict
    border: str
    panels: list
    page_texts: list
    errors: list
    warnings: list
    mode: str

    @property
    def all_texts(self):
        out = []
        for p in self.panels:
            out.extend(p.texts)
        out.extend(self.page_texts)
        return out


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _anchor(at, w, h, anchor):
    x, y = at
    if anchor in ("tl", None):
        return x, y
    if anchor == "tr":
        return x - w, y
    if anchor == "bl":
        return x, y - h
    if anchor == "br":
        return x - w, y - h
    if anchor == "tc":
        return x - w / 2, y
    if anchor == "bc":
        return x - w / 2, y - h
    if anchor == "c":
        return x - w / 2, y - h / 2
    raise ValueError(f"Unknown anchor {anchor}")


def _inside(box, frame, inset=0.0):
    return (box[0] >= frame[0] + inset - 0.01 and box[1] >= frame[1] + inset - 0.01
            and box[2] <= frame[2] - inset + 0.01 and box[3] <= frame[3] - inset + 0.01)


def _overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def choose_art(batch: Batch, state: dict, panel_id: str, mode: str, layout_panel: dict, contract_panel: dict,
               frame) -> tuple[Path | None, str]:
    """Pick the image for a frame according to the build mode."""
    if mode in ("final", "latest"):
        path = st.approved_art(batch, state, panel_id)
        if path and path.exists():
            return path, "approved"
        if mode == "latest":
            path = st.latest_art(batch, state, panel_id)
            if path and path.exists():
                return path, "unapproved"
    fw, fh = frame[2] - frame[0], frame[3] - frame[1]
    label = [panel_id, "ART PENDING", contract_panel["focus"]]
    if mode in ("final", "latest", "standin"):
        refs = [r for r in contract_panel["resolved_references"] if r["kind"] == "location" and r["path"]]
        if refs:
            src = PROJECT / refs[0]["path"]
            focus = tuple(layout_panel.get("art", {}).get("standin_focus", [0.5, 0.5]))
            out = batch.cache_dir / f"standin-{panel_id}-{int(fw)}x{int(fh)}-{focus[0]:.2f}-{focus[1]:.2f}.png"
            if not out.exists():
                standin_raster(src, ["STAND-IN · LOCATION REFERENCE", f"{panel_id} · ART PENDING"], out,
                               fw, fh, focus)
            return out, "standin"
    out = batch.cache_dir / f"placeholder-{panel_id}.png"
    gen = layout_panel.get("art", {}).get("gen_size") or legal_gen_size(fw, fh)
    placeholder_raster(fw, fh, label + [f"generate at {gen[0]}×{gen[1]}"], out)
    return out, "placeholder"


def model_page(batch: Batch, page: int, mode: str = "final") -> PageModel:
    contract = load_json(batch.contract_path(page))
    layout = load_json(batch.layout_path(page))
    state = st.load(batch)
    T = tokens()
    th = theme(layout["theme"])
    errors, warnings = [], []

    blocks = {}
    for cp in contract["panels"]:
        for b in cp["printable"]:
            blocks[b["block_id"]] = (cp["panel_id"], b)
    non_printable_ids = {b["block_id"] for cp in contract["panels"] for b in cp["non_printable"]}
    contract_panels = {cp["panel_id"]: cp for cp in contract["panels"]}

    layout_ids = [p["panel_id"] for p in layout["panels"]]
    if layout_ids != [cp["panel_id"] for cp in contract["panels"]]:
        errors.append(f"Layout panels {layout_ids} do not match manuscript panels/order "
                      f"{[cp['panel_id'] for cp in contract['panels']]}")

    used_blocks: dict[str, int] = {}
    panels, page_texts = [], []
    content = (T["page"]["margin_left"], T["page"]["margin_top"],
               T["page"]["width_pt"] - T["page"]["margin_right"], T["page"]["content_bottom"])

    for lp in layout["panels"]:
        pid = lp["panel_id"]
        cp = contract_panels.get(pid)
        if cp is None:
            errors.append(f"{pid}: not in contract")
            continue
        frame = tuple(lp["frame"])
        if not _inside(frame, content):
            errors.append(f"{pid}: frame {frame} leaves the content area {content}")
        fw, fh = frame[2] - frame[0], frame[3] - frame[1]
        art_cfg = lp.get("art", {})
        gen = tuple(art_cfg.get("gen_size") or legal_gen_size(fw, fh))
        art_path, kind = choose_art(batch, state, pid, mode, lp, cp, frame)
        placement = None
        art_sha = None
        if art_path:
            with Image.open(art_path) as im:
                iw, ih = im.size
            real = kind in ("approved", "unapproved")
            focus = art_cfg.get("focus", [0.5, 0.5]) if real else [0.5, 0.5]  # stand-ins are pre-cropped
            zoom = art_cfg.get("zoom", 1.0) if real else 1.0
            placement = cover_fit(frame, iw, ih, focus, zoom)
            if kind in ("approved", "unapproved"):
                art_sha = sha256_file(art_path)
                if placement.ppi < T["art"]["review_min_ppi"]:
                    warnings.append(f"{pid}: effective {placement.ppi:.0f} ppi is below the review minimum "
                                    f"{T['art']['review_min_ppi']} ppi")
        pm = PanelModel(pid, frame, art_path, kind, placement, art_sha, gen, fallback_size(fw, fh))
        for item in lp.get("text", []):
            ti = _measure(item, pid, blocks, non_printable_ids, used_blocks, th, pm, errors, warnings)
            if ti:
                if ti.type in ("caption", "balloon") and not _inside(ti.box, frame, 6):
                    warnings.append(f"{pid}: {ti.type} {ti.block_id} sits closer than 6 pt to (or outside) its frame")
                pm.texts.append(ti)
        panels.append(pm)

    for item in layout.get("page_text", []):
        ti = _measure(item, item.get("panel_id", ""), blocks, non_printable_ids, used_blocks, th, None, errors, warnings)
        if ti:
            page_texts.append(ti)

    for bid, (pid, b) in blocks.items():
        n = used_blocks.get(bid, 0)
        if n == 0:
            errors.append(f"{pid}: printable block {bid} ({b['role']}) is not placed on the page")
        elif n > 1:
            errors.append(f"{pid}: printable block {bid} is placed {n} times")

    all_texts = [t for p in panels for t in p.texts] + page_texts
    for i, a in enumerate(all_texts):
        if not _inside(a.box, (0, 0, T["page"]["width_pt"], T["page"]["height_pt"]), 12):
            errors.append(f"{a.panel_id}: {a.type} {a.block_id} is within 12 pt of the trim edge")
        for b in all_texts[i + 1:]:
            if _overlap(a.box, b.box):
                errors.append(f"Text boxes overlap: {a.block_id} and {b.block_id}")

    return PageModel(page, contract["page_id"], layout["theme"], th, layout.get("border", "none"),
                     panels, page_texts, errors, warnings, mode)


def _measure(item, pid, blocks, non_printable_ids, used_blocks, th, pm, errors, warnings):
    T = tokens()
    bid = item["block"]
    if bid in non_printable_ids:
        errors.append(f"{pid}: layout tries to print non-printable block {bid}")
        return None
    if bid not in blocks:
        errors.append(f"{pid}: unknown block {bid}")
        return None
    owner, b = blocks[bid]
    used_blocks[bid] = used_blocks.get(bid, 0) + 1
    if any(r.get("bold") or r.get("italic") or r.get("superscript") or r.get("subscript") for r in b.get("runs", [])):
        errors.append(f"{owner}: block {bid} has emphasis runs; the story renderer does not draw them yet")
    text = b["render_text"]
    kind = item["type"]
    font = {"caption": T["caption"]["font"], "balloon": T["balloon"]["font"], "reader": T["reader"]["font"]}.get(kind)
    if font:
        missing = missing_glyphs(font, text)
        if missing:
            errors.append(f"{owner}: {bid} uses characters {missing} that {font} cannot draw")
    try:
        if kind == "caption":
            s = T["caption"]
            lines = wrap_greedy(text, s["font"], s["size"], item["w"] - 2 * s["pad_x"])
            w = widest(lines, s["font"], s["size"]) + 2 * s["pad_x"] + 1.5
            h = s["first_baseline_from_top"] + (len(lines) - 1) * s["leading"] + s["bottom_from_last_baseline"]
            x, y = _anchor(item["at"], w, h, item.get("anchor", "tl"))
            return TextItem("caption", bid, owner, text, lines, (x, y, x + w, y + h), s["font"], s["size"],
                            s["leading"], s["color"], "left", y + s["first_baseline_from_top"])
        if kind == "balloon":
            s = T["balloon"]
            lines = wrap_balanced(text, s["font"], s["size"], item["max_w"] - 2 * s["pad_x"])
            w = widest(lines, s["font"], s["size"]) + 2 * s["pad_x"]
            h = s["first_baseline_from_top"] + (len(lines) - 1) * s["leading"] + s["bottom_from_last_baseline"]
            x, y = _anchor(item["at"], w, h, item.get("anchor", "tl"))
            ti = TextItem("balloon", bid, owner, text, lines, (x, y, x + w, y + h), s["font"], s["size"],
                          s["leading"], s["color"], "center", y + s["first_baseline_from_top"],
                          speaker=b.get("speaker"))
            target, source = None, None
            tail = item.get("tail_to", {})
            real_art = pm is not None and pm.art_kind in ("approved", "unapproved") and pm.placement is not None
            if real_art and tail.get("img"):
                if tail.get("art_sha256") and tail["art_sha256"] != pm.art_sha256:
                    warnings.append(f"{owner}: tail target for {bid} was recorded on different art; re-check it")
                target = pm.placement.img_to_page(*tail["img"])
                source = "art"
            elif tail.get("page"):
                target = tuple(tail["page"])
                source = "layout-default"
                if real_art:
                    warnings.append(f"{owner}: balloon {bid} tail uses the layout default; record tail_to.img on the art")
            if target is None:
                errors.append(f"{owner}: balloon {bid} has no tail target")
            else:
                ti.tail = plan_tail(x, y, w, h, s["radius"], target, s["tail_base"], s["tail_length"],
                                    s["tail_max_length"], s["tail_gap_to_target"])
                ti.tail_source = source
            return ti
        if kind == "reader":
            s = T["reader"]
            lines = wrap_greedy(text, s["font"], s["size"], item["w"])
            w = item["w"]
            h = s["size"] * 1.2 + (len(lines) - 1) * s["leading"]
            x, y = _anchor(item["at"], w, h, item.get("anchor", "tl"))
            color = s["color_on_dark"] if th.get("dark", True) else s["color_on_light"]
            return TextItem("reader", bid, owner, text, lines, (x, y, x + w, y + h), s["font"], s["size"],
                            s["leading"], color, item.get("align", "left"), y + s["size"] * 0.95)
    except TextTooWide as exc:
        errors.append(f"{owner}: {bid}: {exc}")
        return None
    errors.append(f"{owner}: unknown text type '{kind}'")
    return None
