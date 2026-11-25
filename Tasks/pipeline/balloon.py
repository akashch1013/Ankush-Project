#!/usr/bin/env python3
"""balloon.py: seamless speech balloons for ChandRush pages (stage 3).

Why: the old tails were separate SVG wedges laid over an HTML box, with a straight ivory line to hide the seam.
Where the tail left a curved edge (pill ends, ovals) the balloon's border showed through: a "broken" tail.

How: every balloon body and its tail (and any link to a second balloon from the same speaker) are drawn in ONE
SVG group with the union-stroke trick: (1) all shapes stroked at twice the line width, (2) all shapes filled on
top with no stroke. Only the outer half of the stroke survives, so body + tail read as one outline with no join,
whatever the shape and wherever the tail leaves it. The words stay HTML on top (editable, verbatim, textcheck-able).

Sizes come from the real font (Source Sans 3 SemiBold 14/18 pt, measured with PIL), so a balloon is never
too small for its words and never needs hand-tuned width/height.

Spec (a list of dicts, in reading order; units are page pt on the 864 x 648 sheet):
  {"text": "Are you all right?",          # verbatim manuscript words
   "at": [116, 294],                      # top-left of the balloon body  (or "center": [x, y])
   "tip": [245, 360],                     # where the tail ends: 4-8 pt short of the speaker's mouth
   "maxw": 190,                           # optional wrap width for the text (default 200; 1 line if it fits)
   "shape": "pill" | "oval" | "round" | "burst-free"   # optional, default pill (stadium; tall text -> round)
   "bend": 0.10,                          # optional tail curvature (-0.4..0.4; sign = which side it bows)
   "base": 13,                            # optional tail width where it leaves the body
   "exit": [0.3, 1.0],                    # optional: where the tail leaves, as fractions of the body box
   "link": 0,                             # optional: index of an earlier balloon of the SAME speaker -> a neck joins them
   "id": "b2"}                            # optional, for your own reference
No "tip" = no tail (off-panel voice must still have a tail pointing off the panel edge: give a tip outside it).

Use from a generator:   from balloon import balloons_html;  html += balloons_html(spec)
Use from the shell:     python3 pipeline/balloon.py PAGE_DIR      (reads PAGE_DIR/balloons.json, rewrites the
                        block between <!-- BALLOONS --> and <!-- /BALLOONS --> in index.html, or inserts it before
                        the page's closing </div> if the markers are missing), then run `pagekit.py render`.
                        python3 pipeline/balloon.py --measure "text" [--maxw 200]   -> lines and box size
"""
import html as _html
import json
import math
import os
import re
import sys

PIPE = os.path.dirname(os.path.abspath(__file__))
IVORY, INK, SHADOW = "#FFFDF6", "#1d2433", "rgba(8,14,28,.42)"
SIZE, LEAD = 14.0, 18.0          # V09 speech: 14/18 pt
PADX, PADY = 12.0, 7.0            # text inset inside a pill/round body
LINE = 0.8                        # visible outline width (pt)

_font = None


def _f():
    global _font
    if _font is None:
        from PIL import ImageFont
        _font = ImageFont.truetype(os.path.join(PIPE, "fonts", "SourceSans3.ttf"), 140)
        _font.set_variation_by_name("SemiBold")
    return _font


def text_w(s):
    return _f().getlength(s) / 10.0          # 140 px font -> 14 pt


def wrap(text, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if cur and text_w(t) > maxw:
            lines.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def balanced(text, maxw):
    """wrap at maxw, then narrow the measure while the line count holds: even, comic-style line lengths."""
    lines = wrap(text, maxw)
    n, best = len(lines), lines
    w = max(text_w(l) for l in lines)
    while w > 40:
        w -= 4
        t = wrap(text, w)
        if len(t) != n or max(text_w(l) for l in t) > w + .01:
            break
        best = t
    return best


def measure(b):
    lines = balanced(b["text"], b.get("maxw", 200))
    tw = max(text_w(l) for l in lines) + 1.5
    th = LEAD * len(lines)
    shape = b.get("shape") or ("pill" if len(lines) <= 2 else "round")
    if shape == "oval":                       # text box inscribed in the ellipse with a margin
        w, h = tw * 1.30 + 16, th * 1.42 + 12
    else:
        w, h = tw + 2 * PADX, th + 2 * PADY
    return lines, tw, th, shape, w, h


# ---------- geometry ----------
def inside(shape, x, y, w, h, px, py, r):
    if shape == "oval":
        cx, cy = x + w / 2, y + h / 2
        return ((px - cx) / (w / 2)) ** 2 + ((py - cy) / (h / 2)) ** 2 <= 1
    if not (x <= px <= x + w and y <= py <= y + h):
        return False
    qx = min(max(px, x + r), x + w - r)
    qy = min(max(py, y + r), y + h - r)
    return (px - qx) ** 2 + (py - qy) ** 2 <= r * r


def boundary(shape, x, y, w, h, r, ox, oy, tx, ty):
    """point where the segment origin->tip leaves the body (bisection)."""
    lo, hi = 0.0, 1.0
    for _ in range(40):
        m = (lo + hi) / 2
        if inside(shape, x, y, w, h, ox + (tx - ox) * m, oy + (ty - oy) * m, r):
            lo = m
        else:
            hi = m
    return ox + (tx - ox) * lo, oy + (ty - oy) * lo


def body_svg(shape, x, y, w, h, r):
    if shape == "oval":
        return f'<ellipse cx="{x + w / 2:.2f}" cy="{y + h / 2:.2f}" rx="{w / 2:.2f}" ry="{h / 2:.2f}"/>'
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{r:.2f}"/>'


def tail_svg(shape, x, y, w, h, r, tip, base=14.0, bend=0.18, exit=None):
    tx, ty = tip
    if inside(shape, x, y, w, h, tx, ty, r):
        raise ValueError(f"tail tip {tip} is inside the balloon at {x:.0f},{y:.0f}: move the tip out to the speaker")
    if exit:
        ox, oy = x + w * exit[0], y + h * exit[1]
        ox, oy = min(max(ox, x + r * .6), x + w - r * .6), min(max(oy, y + 2), y + h - 2)
        # aim from just inside that edge point
        cx, cy = x + w / 2, y + h / 2
        ox, oy = ox + (cx - ox) * .25, oy + (cy - oy) * .25
    else:
        # leave from the side facing the tip: origin on the body's long axis, clamped under the tip
        cx, cy = x + w / 2, y + h / 2
        if w >= h:
            ox, oy = min(max(tx, x + r), x + w - r), cy
            ox = cx + (ox - cx) * .55
        else:
            ox, oy = cx, min(max(ty, y + r), y + h - r)
            oy = cy + (oy - cy) * .55
    bx, by = boundary(shape, x, y, w, h, r, ox, oy, tx, ty)
    L = math.hypot(tx - bx, ty - by)
    ux, uy = (tx - bx) / L, (ty - by) / L          # along the tail
    nx, ny = -uy, ux                               # across it
    hw = base / 2
    # sink the base inside the body until both corners are safely inside (then the fill layer hides the join)
    depth = 3.0
    for _ in range(60):
        cxb, cyb = bx - ux * depth, by - uy * depth
        c1 = (cxb + nx * hw, cyb + ny * hw)
        c2 = (cxb - nx * hw, cyb - ny * hw)
        if inside(shape, x, y, w, h, *c1, r - 1.5) and inside(shape, x, y, w, h, *c2, r - 1.5) and \
           inside(shape, x, y, w, h, c1[0] + ux * 2.0, c1[1] + uy * 2.0, r) and \
           inside(shape, x, y, w, h, c2[0] + ux * 2.0, c2[1] + uy * 2.0, r):
            break
        depth += 1.0
    total = L + depth
    k = bend * total
    # both edges bow the same way (a curved comic tail); the far edge a little less so it tapers cleanly
    m1 = (c1[0] + (tx - c1[0]) * .5 + nx * k, c1[1] + (ty - c1[1]) * .5 + ny * k)
    m2 = (c2[0] + (tx - c2[0]) * .55 + nx * k * .8, c2[1] + (ty - c2[1]) * .55 + ny * k * .8)
    return (f'<path d="M{c1[0]:.2f} {c1[1]:.2f} Q{m1[0]:.2f} {m1[1]:.2f} {tx:.2f} {ty:.2f} '
            f'Q{m2[0]:.2f} {m2[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} Z"/>')


def neck_svg(a, b, width=7.0):
    (ax, ay), (bx, by) = a, b
    L = math.hypot(bx - ax, by - ay) or 1
    nx, ny = -(by - ay) / L * width / 2, (bx - ax) / L * width / 2
    return (f'<path d="M{ax + nx:.2f} {ay + ny:.2f} L{bx + nx:.2f} {by + ny:.2f} '
            f'L{bx - nx:.2f} {by - ny:.2f} L{ax - nx:.2f} {ay - ny:.2f} Z"/>')


# ---------- html ----------
def layout(spec):
    out = []
    for b in spec:
        lines, tw, th, shape, w, h = measure(b)
        if "w" in b:
            w = max(w, b["w"])
        if "h" in b:
            h = max(h, b["h"])
        if "center" in b:
            x, y = b["center"][0] - w / 2, b["center"][1] - h / 2
        else:
            x, y = b["at"]
        r = h / 2 if shape == "pill" else min(h / 2, w / 2, b.get("radius", 20.0))
        out.append(dict(b, lines=lines, tw=tw, th=th, shape=shape, x=x, y=y, w=w, h=h, r=r))
    return out


def groups(L):
    parent = list(range(len(L)))

    def find(i):
        while parent[i] != i:
            i = parent[i]
        return i
    for i, b in enumerate(L):
        if b.get("link") is not None:
            parent[find(i)] = find(b["link"])
    g = {}
    for i in range(len(L)):
        g.setdefault(find(i), []).append(i)
    return list(g.values())


def balloons_html(spec, z=8):
    L = layout(spec)
    parts = ["<!-- BALLOONS (generated by pipeline/balloon.py: edit the spec, not this block) -->"]
    for gi in groups(L):
        shapes = []
        for i in gi:
            b = L[i]
            shapes.append(body_svg(b["shape"], b["x"], b["y"], b["w"], b["h"], b["r"]))
            if b.get("tip"):
                shapes.append(tail_svg(b["shape"], b["x"], b["y"], b["w"], b["h"], b["r"], b["tip"],
                                       b.get("base", 13.0), b.get("bend", 0.10), b.get("exit")))
            if b.get("link") is not None:
                a = L[b["link"]]
                shapes.append(neck_svg((a["x"] + a["w"] / 2, a["y"] + a["h"] / 2),
                                       (b["x"] + b["w"] / 2, b["y"] + b["h"] / 2)))
        s = "".join(shapes)
        parts.append(
            f'<svg class="bln-art" style="position:absolute; left:0; top:0; width:864pt; height:648pt; overflow:visible; '
            f'pointer-events:none; z-index:{z}" viewBox="0 0 864 648" aria-hidden="true">'
            f'<g transform="translate(0.5 1.3)" fill="{SHADOW}" stroke="none">{s}</g>'
            f'<g fill="{IVORY}" stroke="{INK}" stroke-width="{2 * LINE}" stroke-linejoin="round">{s}</g>'
            f'<g fill="{IVORY}" stroke="none">{s}</g></svg>')
        for i in gi:
            b = L[i]
            text = "<br>".join(_html.escape(l) for l in b["lines"])   # fixed breaks: the browser can't re-wrap
            parts.append(
                f'<div class="bln-txt" style="position:absolute; z-index:{z + 1}; left:{b["x"]:.2f}pt; top:{b["y"]:.2f}pt; '
                f'width:{b["w"]:.2f}pt; height:{b["h"]:.2f}pt; display:flex; align-items:center; justify-content:center; '
                f'text-align:center; font-family:&quot;Source Sans 3&quot;, sans-serif; font-weight:600; font-size:{SIZE}pt; '
                f'line-height:{LEAD}pt; color:{INK}"><span style="display:block; white-space:nowrap">{text}</span></div>')
    parts.append("<!-- /BALLOONS -->")
    return "\n".join(parts)


def report(spec):
    """one line per balloon: box, lines, and any overlap between balloons (for the builder's log)."""
    L = layout(spec)
    rows = []
    for i, b in enumerate(L):
        rows.append(f'{i}: {b["shape"]:5} at {b["x"]:.0f},{b["y"]:.0f} size {b["w"]:.0f}x{b["h"]:.0f} '
                    f'{len(b["lines"])} line(s) | ' + " / ".join(b["lines"]))
        for j in range(i):
            a = L[j]
            if b.get("link") == j:
                continue
            if a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"] and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"]:
                rows.append(f"   WARN balloon {i} overlaps balloon {j}")
        if b["x"] < 0 or b["y"] < 0 or b["x"] + b["w"] > 864 or b["y"] + b["h"] > 648:
            rows.append(f"   WARN balloon {i} leaves the sheet")
    return "\n".join(rows)


def inject(page_dir):
    spec = json.load(open(os.path.join(page_dir, "balloons.json"), encoding="utf-8"))
    block = balloons_html(spec)
    p = os.path.join(page_dir, "index.html")
    src = open(p, encoding="utf-8").read()
    pat = re.compile(r"<!-- BALLOONS.*?<!-- /BALLOONS -->", re.S)
    if pat.search(src):
        src = pat.sub(lambda m: block, src)
    else:
        i = src.rfind("</div>\n<script")
        if i < 0:
            i = src.rfind("</div>")
        src = src[:i] + block + "\n" + src[i:]
    open(p, "w", encoding="utf-8").write(src)
    print(report(spec))
    print(f"balloons: {len(spec)} written into {p}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
    elif a[0] == "--measure":
        mw = float(a[a.index("--maxw") + 1]) if "--maxw" in a else 200
        print(report([{"text": a[1], "at": [0, 0], "maxw": mw}]))
    else:
        inject(a[0])
