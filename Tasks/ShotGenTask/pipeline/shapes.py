"""Vector shapes for page furniture: caption boxes, speech balloons with tails,
and the outer border ornaments reproduced from the Opening V04 sample.

Geometry is expressed in page points with a TOP-LEFT origin (the same system
used by the layout files and by PyMuPDF measurements of the samples). The
`Page` helper converts to ReportLab's bottom-left origin when drawing.
"""
from __future__ import annotations

import math
import random

from .design import hex_rgb

K = 0.5522847498  # cubic Bezier circle constant


class Page:
    """Thin wrapper over a ReportLab canvas using top-left coordinates."""

    def __init__(self, canvas, width: float, height: float):
        self.c = canvas
        self.w = width
        self.h = height

    def y(self, y: float) -> float:
        return self.h - y

    def path(self, ops):
        p = self.c.beginPath()
        for op in ops:
            kind = op[0]
            if kind == "M":
                p.moveTo(op[1], self.y(op[2]))
            elif kind == "L":
                p.lineTo(op[1], self.y(op[2]))
            elif kind == "C":
                p.curveTo(op[1], self.y(op[2]), op[3], self.y(op[4]), op[5], self.y(op[6]))
            elif kind == "Z":
                p.close()
        return p

    def fill_color(self, hexcolor: str):
        self.c.setFillColorRGB(*hex_rgb(hexcolor))

    def stroke_color(self, hexcolor: str):
        self.c.setStrokeColorRGB(*hex_rgb(hexcolor))

    def rect(self, x0, y0, x1, y1, fill=None, stroke=None, width=1.0):
        if fill:
            self.fill_color(fill)
        if stroke:
            self.stroke_color(stroke)
            self.c.setLineWidth(width)
        self.c.rect(x0, self.y(y1), x1 - x0, y1 - y0, stroke=1 if stroke else 0, fill=1 if fill else 0)

    def line(self, x0, y0, x1, y1, color, width):
        self.stroke_color(color)
        self.c.setLineWidth(width)
        self.c.line(x0, self.y(y0), x1, self.y(y1))

    def circle(self, cx, cy, r, fill=None, stroke=None, width=0.7):
        if fill:
            self.fill_color(fill)
        if stroke:
            self.stroke_color(stroke)
            self.c.setLineWidth(width)
        self.c.circle(cx, self.y(cy), r, stroke=1 if stroke else 0, fill=1 if fill else 0)

    def polyline(self, points, color, width, close=False):
        ops = [("M", *points[0])] + [("L", *pt) for pt in points[1:]]
        if close:
            ops.append(("Z",))
        self.stroke_color(color)
        self.c.setLineWidth(width)
        self.c.drawPath(self.path(ops), stroke=1, fill=0)


# ---------------------------------------------------------------- rounded shapes

def rounded_rect_ops(x, y, w, h, r, tail=None):
    """Clockwise rounded rectangle; optionally splices a straight tail into one edge.

    tail = {"edge": "top|right|bottom|left", "pos": centre of tail base along the edge
            (absolute x for top/bottom, absolute y for left/right), "base": width, "tip": (x, y)}
    """
    r = max(0.0, min(r, w / 2, h / 2))
    ops = [("M", x + r, y)]

    def splice(edge, a, b):
        if tail and tail["edge"] == edge:
            half = tail["base"] / 2
            p = tail["pos"]
            if edge == "top":
                ops.extend([("L", p - half, y), ("L", *tail["tip"]), ("L", p + half, y)])
            elif edge == "right":
                ops.extend([("L", x + w, p - half), ("L", *tail["tip"]), ("L", x + w, p + half)])
            elif edge == "bottom":
                ops.extend([("L", p + half, y + h), ("L", *tail["tip"]), ("L", p - half, y + h)])
            elif edge == "left":
                ops.extend([("L", x, p + half), ("L", *tail["tip"]), ("L", x, p - half)])
        ops.append(("L", a, b))

    splice("top", x + w - r, y)
    ops.append(("C", x + w - r + K * r, y, x + w, y + r - K * r, x + w, y + r))
    splice("right", x + w, y + h - r)
    ops.append(("C", x + w, y + h - r + K * r, x + w - r + K * r, y + h, x + w - r, y + h))
    splice("bottom", x + r, y + h)
    ops.append(("C", x + r - K * r, y + h, x, y + h - r + K * r, x, y + h - r))
    splice("left", x, y + r)
    ops.append(("C", x, y + r - K * r, x + r - K * r, y, x + r, y))
    ops.append(("Z",))
    return ops


def plan_tail(x, y, w, h, r, target, base, min_len, max_len, gap):
    """Choose the edge, base position and tip for a balloon tail aimed at `target`.

    The tip stops `gap` points short of the target point, which the layout
    records in clear space just beside the speaker's mouth (never on the face).
    """
    cx, cy = x + w / 2, y + h / 2
    tx, ty = target
    dx, dy = tx - cx, ty - cy
    if abs(dx) < 1e-6 and abs(dy) < 1e-6:
        dy = 1.0
    # Which edge does the centre->target ray leave through?
    if abs(dy) * (w / 2) >= abs(dx) * (h / 2):
        edge = "bottom" if dy > 0 else "top"
        t = (h / 2) / abs(dy)
        pos = cx + dx * t
        lo, hi = x + r + base / 2 + 1, x + w - r - base / 2 - 1
        pos = min(max(pos, lo), hi) if lo <= hi else cx
        bx, by = pos, (y + h if edge == "bottom" else y)
    else:
        edge = "right" if dx > 0 else "left"
        t = (w / 2) / abs(dx)
        pos = cy + dy * t
        lo, hi = y + r + base / 2 + 1, y + h - r - base / 2 - 1
        pos = min(max(pos, lo), hi) if lo <= hi else cy
        bx, by = (x + w if edge == "right" else x), pos
    vx, vy = tx - bx, ty - by
    dist = math.hypot(vx, vy)
    if dist < 1e-6:
        vx, vy, dist = (0.0, 1.0, 1.0)
    length = max(min_len, min(dist - gap, max_len))
    tip = (bx + vx / dist * length, by + vy / dist * length)
    # Never let the tip fold back inside the balloon body.
    if x - 0.5 <= tip[0] <= x + w + 0.5 and y - 0.5 <= tip[1] <= y + h + 0.5:
        out = {"bottom": (0, 1), "top": (0, -1), "right": (1, 0), "left": (-1, 0)}[edge]
        tip = (bx + out[0] * min_len, by + out[1] * min_len)
    return {"edge": edge, "pos": pos, "base": base, "tip": tip, "length": length,
            "aims_at": [round(tx, 1), round(ty, 1)], "distance_to_target": round(dist, 1)}


def draw_caption_box(page: Page, x, y, w, h, fill, speckle, radius, density, speck_r, seed):
    page.fill_color(fill)
    page.c.drawPath(page.path(rounded_rect_ops(x, y, w, h, radius)), stroke=0, fill=1)
    # Paper grain: tiny dots in a slightly darker tint, as in the sample captions.
    rng = random.Random(seed)
    count = int(w * h * density)
    page.fill_color(speckle)
    for _ in range(count):
        px = rng.uniform(x + radius * 0.6, x + w - radius * 0.6)
        py = rng.uniform(y + radius * 0.6, y + h - radius * 0.6)
        page.c.circle(px, page.y(py), speck_r, stroke=0, fill=1)


def draw_balloon(page: Page, x, y, w, h, radius, fill, stroke, stroke_w, tail):
    page.fill_color(fill)
    page.stroke_color(stroke)
    page.c.setLineWidth(stroke_w)
    page.c.setLineJoin(1)
    page.c.drawPath(page.path(rounded_rect_ops(x, y, w, h, radius, tail)), stroke=1, fill=1)
    page.c.setLineJoin(0)


# ---------------------------------------------------------------- borders

def draw_border(page: Page, variant: str, theme: dict) -> None:
    a = theme["accent"]
    W, H = page.w, page.h
    if variant in (None, "", "none"):
        return
    if variant == "lantern_brackets":  # Opening p08
        for sx, sy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            def fx(v):
                return v if sx == 0 else W - v
            def fy(v):
                return v if sy == 0 else H - v
            pts = [(fx(69), fy(11)), (fx(29), fy(11)), (fx(29), fy(18)), (fx(11), fy(18)), (fx(11), fy(69))]
            page.polyline(pts, a, 0.9)
            page.circle(fx(69), fy(11), 2.0, stroke=a, width=0.7)
    elif variant == "silver_moonline":  # Opening p10
        page.line(11, 14, 11, H - 14, a, 0.85)
        page.line(W - 11, 14, W - 11, H - 14, a, 0.85)
        page.line(22, 12, W - 22, 12, a, 0.5)
        page.line(22, H - 12, W - 22, H - 12, a, 0.5)
        for xx in (11, W - 11):
            for yy in (17, 32, H - 32, H - 17):
                page.circle(xx, yy, 2.0, fill=a)
    elif variant == "mirror_diamond":  # Opening p11
        cx = W / 2
        for yy in (12, H - 12):
            page.line(16, yy, cx - 18, yy, a, 0.7)
            page.line(cx + 18, yy, W - 16, yy, a, 0.7)
            page.polyline([(cx, yy - 5), (cx + 8, yy), (cx, yy + 5), (cx - 8, yy)], a, 0.9, close=True)
        page.line(12, 36, 12, H - 36, a, 0.6)
        page.line(W - 12, 36, W - 12, H - 36, a, 0.6)
    elif variant == "gate_arch":  # Opening p12: an arched lintel over the page
        ops = [("M", 11, H - 13), ("L", 11, 26),
               ("C", 11 + 2 / 3 * (W / 2 - 11), 26 - 2 / 3 * 34, W - 11 - 2 / 3 * (W / 2 - 11), 26 - 2 / 3 * 34, W - 11, 26),
               ("L", W - 11, H - 13)]
        page.stroke_color(a)
        page.c.setLineWidth(0.9)
        page.c.drawPath(page.path(ops), stroke=1, fill=0)
        page.line(11, H - 12, W - 11, H - 12, a, 0.65)
    elif variant == "cube_chamfer":  # Opening p03
        for sx, sy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            def fx(v):
                return v if sx == 0 else W - v
            def fy(v):
                return v if sy == 0 else H - v
            page.polyline([(fx(77), fy(11)), (fx(24), fy(11)), (fx(11), fy(24)), (fx(11), fy(77))], a, 1.1)
            page.circle(fx(23), fy(23), 2.0, fill=a)
    elif variant == "pavilion_hem":  # Opening p06
        for top in (True, False):
            pts = []
            xx, i = 14.0, 0
            while xx <= W - 14 + 0.1:
                if top:
                    pts.append((xx, 16 if i % 2 == 0 else 9))
                else:
                    pts.append((xx, H - 16 if i % 2 == 0 else H - 9))
                xx += 24
                i += 1
            page.polyline(pts, a, 0.7)
        page.line(12, 30, 12, H - 30, a, 0.55)
        page.line(W - 12, 30, W - 12, H - 30, a, 0.55)
    elif variant == "double_frame":  # Opening p07
        page.stroke_color(a)
        page.c.setLineWidth(0.85)
        page.c.drawPath(page.path(rounded_rect_ops(9, 9, W - 18, H - 18, 2)), stroke=1, fill=0)
        page.stroke_color(theme.get("accent2", a))
        page.c.setLineWidth(0.7)
        page.c.drawPath(page.path(rounded_rect_ops(14, 14, W - 28, H - 28, 1)), stroke=1, fill=0)
    else:
        raise SystemExit(f"Unknown border variant '{variant}'")
