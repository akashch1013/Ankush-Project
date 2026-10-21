"""Artwork placement: cover-fit into frames, crop maths, effective ppi,
placeholder / stand-in rasters for layout proofs, and review overlays.

Images are never stretched: one uniform scale per image, cropped by the frame.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

from .design import tokens
from .paths import FONTS


@dataclass
class Placement:
    frame: tuple[float, float, float, float]   # page pt, top-left origin
    img_w: int
    img_h: int
    scale: float                               # pt per image pixel
    x: float                                   # page position of the image's top-left corner
    y: float

    @property
    def ppi(self) -> float:
        return 72.0 / self.scale

    @property
    def crop_px(self) -> tuple[float, float, float, float]:
        fx0, fy0, fx1, fy1 = self.frame
        return ((fx0 - self.x) / self.scale, (fy0 - self.y) / self.scale,
                (fx1 - self.x) / self.scale, (fy1 - self.y) / self.scale)

    def img_to_page(self, u: float, v: float) -> tuple[float, float]:
        """Normalised image coordinates (0..1) -> page points."""
        return (self.x + u * self.img_w * self.scale, self.y + v * self.img_h * self.scale)

    def page_to_img(self, px: float, py: float) -> tuple[float, float]:
        return ((px - self.x) / (self.img_w * self.scale), (py - self.y) / (self.img_h * self.scale))

    def visible_norm(self) -> tuple[float, float, float, float]:
        l, t, r, b = self.crop_px
        return (l / self.img_w, t / self.img_h, r / self.img_w, b / self.img_h)


def cover_fit(frame, img_w: int, img_h: int, focus=(0.5, 0.5), zoom: float = 1.0) -> Placement:
    fx0, fy0, fx1, fy1 = frame
    fw, fh = fx1 - fx0, fy1 - fy0
    s = max(fw / img_w, fh / img_h) * max(zoom, 1.0)
    dw, dh = img_w * s, img_h * s
    ox = fw / 2 - focus[0] * dw
    oy = fh / 2 - focus[1] * dh
    ox = min(0.0, max(fw - dw, ox))
    oy = min(0.0, max(fh - dh, oy))
    return Placement(frame=tuple(frame), img_w=img_w, img_h=img_h, scale=s, x=fx0 + ox, y=fy0 + oy)


def legal_gen_size(frame_w_pt: float, frame_h_pt: float) -> tuple[int, int]:
    """Largest gpt-image-2-legal size with the frame's aspect, aiming at the target ppi.
    Rules (Codex imagegen skill): edges multiple of 16, max edge 3840, ratio <= 3:1,
    total pixels <= ~3.69 MP to stay out of the 'experimental' range."""
    a = tokens()["art"]
    ratio = frame_w_pt / frame_h_pt
    ratio = min(max(ratio, 1 / a["gen_max_ratio"]), a["gen_max_ratio"])
    w = frame_w_pt / 72 * a["target_ppi"]
    h = w / ratio
    scale = min(1.0, a["gen_max_edge"] / max(w, h), (a["gen_max_pixels"] / (w * h)) ** 0.5)
    w, h = w * scale, h * scale
    m = a["gen_multiple"]
    w = max(m, int(w // m) * m)
    h = max(m, int(h // m) * m)
    while w * h < a["gen_min_pixels"]:
        w += m
        h = max(m, int(round(w / ratio / m)) * m)
    return w, h


def fallback_size(frame_w_pt: float, frame_h_pt: float) -> tuple[int, int]:
    fb = tokens()["art"]["fixed_size_fallbacks"]
    r = frame_w_pt / frame_h_pt
    if r > 1.2:
        return tuple(fb["landscape"])
    if r < 0.83:
        return tuple(fb["portrait"])
    return tuple(fb["square"])


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def prepare_embed(image_path: Path, placement: Placement, cache_dir: Path) -> tuple[Path, tuple[float, float, float, float]]:
    """Crop the visible region (plus 2 px) and save a high-quality JPEG for embedding.
    Returns (file, (x, y, w, h)) where the crop should be drawn on the page."""
    l, t, r, b = placement.crop_px
    L, T = max(0, int(l) - 2), max(0, int(t) - 2)
    R, B = min(placement.img_w, int(r + 0.999) + 2), min(placement.img_h, int(b + 0.999) + 2)
    key = hashlib.sha1(f"{sha256_file(image_path)}:{L},{T},{R},{B}".encode()).hexdigest()[:16]
    cache_dir.mkdir(parents=True, exist_ok=True)
    out = cache_dir / f"{image_path.stem}-{key}.jpg"
    if not out.exists():
        with Image.open(image_path) as im:
            im.convert("RGB").crop((L, T, R, B)).save(out, "JPEG", quality=93, subsampling=0, optimize=True)
    s = placement.scale
    return out, (placement.x + L * s, placement.y + T * s, (R - L) * s, (B - T) * s)


# ------------------------------------------------------------ proof rasters

def _font(size: int, bold: bool = True):
    name = "SourceSans3-Semibold.ttf" if bold else "SourceSans3-Regular.ttf"
    try:
        return ImageFont.truetype(str(FONTS / name), size)
    except OSError:
        return ImageFont.load_default()


def placeholder_raster(frame_w_pt: float, frame_h_pt: float, lines: list[str], out: Path, ppi: int = 110) -> Path:
    """Grey hatched placeholder with a raster label (raster on purpose: proof labels
    must never appear in the PDF text layer that the audit compares)."""
    w, h = max(8, int(frame_w_pt / 72 * ppi)), max(8, int(frame_h_pt / 72 * ppi))
    im = Image.new("RGB", (w, h), (59, 74, 90))
    d = ImageDraw.Draw(im)
    step = max(10, w // 40)
    for i in range(-h, w, step):
        d.line([(i, 0), (i + h, h)], fill=(68, 85, 103), width=1)
    f = _font(max(12, int(h * 0.055)))
    y = int(h * 0.38)
    for line in lines:
        tw = d.textlength(line, font=f)
        d.text(((w - tw) / 2, y), line, font=f, fill=(225, 232, 237))
        y += int(f.size * 1.35)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out)
    return out


def standin_raster(source: Path, lines: list[str], out: Path, frame_w_pt: float, frame_h_pt: float,
                   focus=(0.5, 0.5), max_edge: int = 1400) -> Path:
    """Darkened copy of a location reference, pre-cropped to the frame's shape, with
    a 'STAND-IN' banner. Used only to preview composition before real art exists."""
    with Image.open(source) as im:
        im = im.convert("RGB")
        p = cover_fit((0, 0, frame_w_pt, frame_h_pt), im.width, im.height, focus, 1.0)
        l, t, r, b = (int(round(v)) for v in p.crop_px)
        im = im.crop((max(0, l), max(0, t), min(im.width, r), min(im.height, b)))
        im.thumbnail((max_edge, max_edge))
        im = ImageEnhance.Brightness(im).enhance(0.62)
        im = ImageEnhance.Color(im).enhance(0.55)
        w, h = im.size
        d = ImageDraw.Draw(im, "RGBA")
        size = max(12, int(min(h * 0.06, w * 0.9 / max(10, max(len(s) for s in lines) * 0.55))))
        f = _font(size)
        band_h = int(f.size * (1.5 * len(lines) + 0.6))
        y0 = int(h * 0.5 - band_h / 2)
        d.rectangle([0, y0, w, y0 + band_h], fill=(10, 20, 35, 170))
        y = y0 + int(f.size * 0.4)
        for line in lines:
            tw = d.textlength(line, font=f)
            d.text(((w - tw) / 2, y), line, font=f, fill=(242, 236, 217, 255))
            y += int(f.size * 1.5)
        out.parent.mkdir(parents=True, exist_ok=True)
        im.save(out)
    return out


def review_overlay(art: Path, placement: Placement, zones: list[dict], tail_points: list[dict], out: Path,
                   max_w: int = 1600) -> Path:
    """Show the planned crop, reserved text zones, tail targets and a 0..1 grid on the art."""
    with Image.open(art) as src:
        im = src.convert("RGB")
    W, H = im.size
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    l, t, r, b = placement.crop_px
    shade = (0, 0, 0, 140)
    d.rectangle([0, 0, W, t], fill=shade)
    d.rectangle([0, b, W, H], fill=shade)
    d.rectangle([0, t, l, b], fill=shade)
    d.rectangle([r, t, W, b], fill=shade)
    lw = max(2, W // 500)
    # grid every 0.1 of the full image
    f = _font(max(12, W // 80), bold=False)
    for i in range(1, 10):
        x = W * i / 10
        y = H * i / 10
        d.line([(x, 0), (x, H)], fill=(255, 255, 255, 60), width=1)
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 60), width=1)
        d.text((x + 3, 3), f"{i / 10:.1f}", font=f, fill=(255, 255, 255, 200))
        d.text((3, y + 3), f"{i / 10:.1f}", font=f, fill=(255, 255, 255, 200))
    d.rectangle([l, t, r, b], outline=(215, 180, 104, 255), width=lw * 2)
    fz = _font(max(14, W // 60))
    for z in zones:
        u0, v0 = placement.page_to_img(z["box"][0], z["box"][1])
        u1, v1 = placement.page_to_img(z["box"][2], z["box"][3])
        box = [u0 * W, v0 * H, u1 * W, v1 * H]
        d.rectangle(box, outline=(80, 220, 255, 255), width=lw, fill=(80, 220, 255, 40))
        d.text((box[0] + 4, box[1] + 2), z["label"], font=fz, fill=(80, 220, 255, 255))
    for p in tail_points:
        cx, cy = p["u"] * W, p["v"] * H
        rr = max(6, W // 150)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(255, 60, 200, 255), width=lw)
        d.text((cx + rr + 3, cy - rr), p["label"], font=fz, fill=(255, 60, 200, 255))
    im = Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")
    if W > max_w:
        im = im.resize((max_w, int(H * max_w / W)), Image.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out)
    return out
