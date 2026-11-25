#!/usr/bin/env python3
"""CH01 P002 "The Cart Handle" (2026-11-25): story page, verso of the P002/P003 spread.
Grid: 864x648 pt, 36 pt margins, 12 columns (49.5 pt) with 18 pt gutters, 18 pt baseline.
  tier 1  P002-1 cols 0-11, y 36-270  (13 baselines): the cub-eye letterbox
  tier 2  P002-2 cols 0-6,  y 288-612 (18 baselines) | P002-3 cols 7-11
Border: the culprit cart. Timber corner block + the handle as the top arm, its grip right above
where Tez bumped it; a brass pinstripe carries on round the page; a quarter cart wheel finishes.
Writes PdfSheetsGenTask/CH01/P002/index.html."""
import math, pathlib

OUT = pathlib.Path(__file__).resolve().parents[2] / "CH01" / "P002" / "index.html"

M, COLW, GUT, BL = 36, 49.5, 18, 18
def colx(i): return M + i * (COLW + GUT)
def colw(a, b): return colx(b) + COLW - colx(a)          # columns a..b inclusive

T1, T1B = 36, 270
T2, T2B = 288, 612

# id, x, y, w, h, image px, scale (pt/px), img offset (pt)
PANELS = [
    dict(id="P002-1", x=colx(0), y=T1, w=colw(0, 11), h=T1B - T1, iw=1536, ih=1024),
    dict(id="P002-2", x=colx(0), y=T2, w=colw(0, 6),  h=T2B - T2, iw=1536, ih=1024),
    dict(id="P002-3", x=colx(7), y=T2, w=colw(7, 11), h=T2B - T2, iw=1024, ih=1024),
]
P = {p["id"]: p for p in PANELS}
# P002-1 (re-staged s2, 2026-11-25): fit width, show image rows .24-.683 (cart body, Tez's head on the grip, paving below the paws)
p = P["P002-1"]; p["s"] = p["w"] / 1536; p["ox"] = 0; p["oy"] = -0.24 * 1024 * p["s"]
# P002-2 (s2): fit height, show image x .016-.952 (the grip's end on the left, Navya's shoe on the right)
p = P["P002-2"]; p["s"] = p["h"] / 1024; p["ox"] = -0.016 * 1536 * p["s"]; p["oy"] = 0
# P002-3: fit height, centre crop (4.5 pt)
p = P["P002-3"]; p["s"] = p["h"] / 1024; p["ox"] = (p["w"] - 1024 * p["s"]) / 2; p["oy"] = 0

def at(pid, fx, fy):
    """image fraction -> page pt"""
    p = P[pid]
    return (p["x"] + p["ox"] + fx * p["iw"] * p["s"], p["y"] + p["oy"] + fy * p["ih"] * p["s"])

INK, IVORY = "#1d2433", "#FFFDF6"

def wedge(b1, b2, tip, ctrl):
    """curved tail: both edges bend through ctrl; the base seam is covered in ivory."""
    c1 = ((b1[0] + ctrl[0]) / 2 + (ctrl[0] - (b1[0] + b2[0]) / 2) * .0, ctrl[1])
    mx, my = (b1[0] + b2[0]) / 2, (b1[1] + b2[1]) / 2
    # second edge control sits a little toward b2 so the wedge tapers
    k1 = (ctrl[0] + (b1[0] - mx) * .35, ctrl[1] + (b1[1] - my) * .35)
    k2 = (ctrl[0] + (b2[0] - mx) * .35, ctrl[1] + (b2[1] - my) * .35)
    d = (f"M{b1[0]:.1f} {b1[1]:.1f} Q{k1[0]:.1f} {k1[1]:.1f} {tip[0]:.1f} {tip[1]:.1f} "
         f"Q{k2[0]:.1f} {k2[1]:.1f} {b2[0]:.1f} {b2[1]:.1f}")
    return (f'<path d="{d}" fill="{IVORY}" stroke="{INK}" stroke-width=".8" stroke-linejoin="round"/>'
            f'<path d="M{b1[0]:.1f} {b1[1]:.1f} L{b2[0]:.1f} {b2[1]:.1f}" stroke="{IVORY}" stroke-width="2.4"/>')

def ell(cx, cy, rx, ry, deg):
    a = math.radians(deg); return (cx + rx * math.cos(a), cy + ry * math.sin(a))

# ---------- lettering (page pt), measured on the gridded art ----------
# P002-1 caption: one line on the wet paving, bottom-centre, right of the paws/grip and left of Ahana's shoes (image x .47-.77, y > .62)
C1 = dict(x=round(at("P002-1", .468, 0)[0]), y=T1B - 6 - 29)
# P002-2 Ahana (first): one-line stadium on the dark stall wall/banner above her, left of the raised lamp (image x .18-.46, y .02-.11)
B2a = dict(x=116, y=294, w=136, h=30)
B2a_tip = at("P002-2", .352, .238)              # just above her crown, aimed at her mouth (.385,.40)
# P002-2 Tez (second): two-line pill on the stall wall above the cart, left of Ahana's curls (image x .03-.27, y .22-.37)
B2b = dict(x=44, y=359, w=116, h=48)
B2b_tip = at("P002-2", .292, .572)              # past her sleeve to his left ear tip, toward his mouth (.355,.63)
B2b_ctl = at("P002-2", .232, .480)              # the tail bends down over the cart rail
# P002-2 caption: one line low on the paving, below every paw and shoe (image y > .87)
C2 = dict(x=P["P002-2"]["x"] + 6, y=T2B - 6 - 29)
# P002-3 Ahana: one-line stadium in the sky where she glances, covering the moon (image x .49-.97, y .08-.17)
B3 = dict(x=664, y=314, w=158, h=30)
B3_tip = at("P002-3", .468, .222)               # on the curls right of her face, toward her mouth (.39,.32)

def tails_svg():
    out = []
    b = B2a; by = b["y"] + b["h"] - .3
    out.append(wedge((b["x"] + 66, by), (b["x"] + 79, by), B2a_tip, ((b["x"] + 72 + B2a_tip[0]) / 2 - 3, (by + B2a_tip[1]) / 2)))
    b = B2b; cx, cy, rx, ry = b["x"] + b["w"] / 2, b["y"] + b["h"] / 2, b["w"] / 2 - .3, b["h"] / 2 - .3
    by = b["y"] + b["h"] - .3
    out.append(wedge((b["x"] + 74, by), (b["x"] + 86, by), B2b_tip, B2b_ctl))
    b = B3; by = b["y"] + b["h"] - .3
    out.append(wedge((b["x"] + 18, by), (b["x"] + 30, by), B3_tip, ((b["x"] + 24 + B3_tip[0]) / 2 + 2, (by + B3_tip[1]) / 2 - 2)))
    return "\n  ".join(out)

def panel_html(p):
    return (f'<div class="pnl" style="left:{p["x"]}pt; top:{p["y"]}pt; width:{p["w"]}pt; height:{p["h"]}pt">'
            f'<img src="assets/img/{p["id"]}.jpg" alt="" style="left:{p["ox"]:.2f}pt; top:{p["oy"]:.2f}pt; '
            f'width:{p["iw"] * p["s"]:.2f}pt; height:{p["ih"] * p["s"]:.2f}pt"></div>')

def balloon(b, inner, shape):
    r = "border-radius:50%" if shape == "ov" else f"border-radius:{b['h'] / 2:.1f}pt"
    return f'<div class="bal" style="left:{b["x"]}pt; top:{b["y"]}pt; width:{b["w"]}pt; height:{b["h"]}pt; {r}">{inner}</div>'

# ---------- border: the cart ----------
# handle: from the corner block down to the grip, which sits right above Tez's bump (P002-1 image x .34)
GX = round(at("P002-1", .50, .5)[0])            # grip centre x
def lerp(a, b, t): return a + (b - a) * t
HX0, HY0, HX1, HY1 = 30, 7.5, GX - 9, 15.0      # rail centreline
ang = math.degrees(math.atan2(HY1 - HY0, HX1 - HX0))
grain = []
for i, (off, a, b) in enumerate([(-1.3, .05, .62), (.2, .18, .95), (1.4, .02, .44), (-.4, .55, .99), (1.0, .60, .88)]):
    x0, x1 = lerp(HX0, HX1, a), lerp(HX0, HX1, b)
    y0, y1 = lerp(HY0, HY1, a) + off, lerp(HY0, HY1, b) + off
    grain.append(f'<path d="M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f}" stroke="#8a6440" stroke-width=".4" stroke-opacity=".9"/>')

WC, WR = (864, 648), 46                          # quarter wheel: centre on the trim corner
spokes = []
for a in (192, 207, 222, 237, 252):
    r0, r1 = 10, WR - 7
    x0, y0 = WC[0] + r0 * math.cos(math.radians(a)), WC[1] + r0 * math.sin(math.radians(a))
    x1, y1 = WC[0] + r1 * math.cos(math.radians(a)), WC[1] + r1 * math.sin(math.radians(a))
    spokes.append(f'<path d="M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f}" stroke="#4a3220" stroke-width="3.4" stroke-linecap="round"/>'
                  f'<path d="M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f}" stroke="#7d5838" stroke-width="2.2" stroke-linecap="round"/>')

FOL_CX, FOL_CY, FR = 424, 630, 5.4
t = 2 / 107
moon_rx = FR * (1 - 2 * t)

BORDER = f'''<svg class="blk" style="left:0; top:0; width:864pt; height:648pt; z-index:5; pointer-events:none" viewBox="0 0 864 648" aria-hidden="true">
  <defs>
    <linearGradient id="brass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f3d58f"/><stop offset=".45" stop-color="#c98f45"/><stop offset=".75" stop-color="#b3722f"/><stop offset="1" stop-color="#6e4318"/></linearGradient>
    <linearGradient id="timber" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9a7048"/><stop offset=".35" stop-color="#7a5536"/><stop offset="1" stop-color="#4f3521"/></linearGradient>
    <radialGradient id="block" cx=".3" cy=".25" r=".9"><stop offset="0" stop-color="#8f6842"/><stop offset=".6" stop-color="#6b4a2e"/><stop offset="1" stop-color="#4a3220"/></radialGradient>
    <radialGradient id="moonG" cx=".38" cy=".35" r=".7"><stop offset="0" stop-color="#fff6da"/><stop offset=".6" stop-color="#f1d79a"/><stop offset="1" stop-color="#c99a4c"/></radialGradient>
    <filter id="soft" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="1.3"/></filter>
  </defs>

  <!-- brass pinstripe 12 pt inside the trim: leaves the grip, runs round the right and bottom, broken at the wheel and the folio -->
  <path fill="none" stroke="#c9a24a" stroke-width=".8" d="M{GX + 16} 12 H852 V{648 - WR - 8} M{864 - WR - 8} 636 H{FOL_CX + 22} M{FOL_CX - 14} 636 H60"/>
  <circle cx="58" cy="636" r="1.5" fill="#c9a24a"/>

  <!-- the handle's shadow on the field, then the timber rail itself -->
  <path d="M{HX0} {HY0 + 2.2} L{HX1} {HY1 + 2.2}" stroke="#0e1626" stroke-opacity=".45" stroke-width="5.6" filter="url(#soft)"/>
  <g transform="rotate({ang:.3f} {HX0} {HY0})">
    <rect x="{HX0}" y="{HY0 - 2.6}" width="{math.hypot(HX1 - HX0, HY1 - HY0):.1f}" height="5.2" fill="url(#timber)" stroke="#3a2616" stroke-width=".4"/>
    <path d="M{HX0} {HY0 - 2.1} h{math.hypot(HX1 - HX0, HY1 - HY0):.1f}" stroke="#c49a6c" stroke-width=".45" stroke-opacity=".7"/>
  </g>
  {''.join(grain)}
  <!-- brass ferrule, then the round wooden grip seen end-on (what Tez walked into) -->
  <g transform="rotate({ang:.3f} {HX1} {HY1})">
    <rect x="{HX1 - 7}" y="{HY1 - 3.3}" width="6" height="6.6" rx=".8" fill="url(#brass)" stroke="#5a3510" stroke-width=".45"/>
    <path d="M{HX1 - 6.2} {HY1 - 2.6} v5.2" stroke="#fff0c4" stroke-width=".5" stroke-opacity=".8"/>
  </g>
  <rect x="{GX - 9}" y="{HY1 - 5.5}" width="16" height="11" rx="2.2" fill="url(#timber)" stroke="#3a2616" stroke-width=".5"/>
  <ellipse cx="{GX + 7}" cy="{HY1}" rx="3.2" ry="5.5" fill="#8f6842" stroke="#3a2616" stroke-width=".5"/>
  <ellipse cx="{GX + 7}" cy="{HY1}" rx="1.6" ry="3" fill="none" stroke="#5a3d25" stroke-width=".4"/>
  <!-- a lamp-gold glint on the grip's underside, right above the spot where Tez's forehead met it -->
  <path d="M{GX - 6} {HY1 + 4.6} H{GX + 4}" stroke="#f7c684" stroke-width=".8" stroke-linecap="round" stroke-opacity=".9"/>

  <!-- ===== entry, top-left: the cart's timber corner block with a brass L-strap and two rivets ===== -->
  <path d="M0 0 H34 V34 H0 Z" fill="#0e1626" fill-opacity=".45" transform="translate(1.4 1.8)" filter="url(#soft)"/>
  <rect x="0" y="0" width="34" height="34" fill="url(#block)" stroke="#3a2616" stroke-width=".6"/>
  <path d="M2 8 H32 M2 17 H32 M2 26 H32" stroke="#4a3220" stroke-width=".4" stroke-opacity=".8"/>
  <path d="M3 5 C12 6 22 4 31 6 M3 22 C12 21 24 23 31 21" stroke="#a07a52" stroke-width=".35" stroke-opacity=".8" fill="none"/>
  <path d="M0 0 H34 V8 H8 V34 H0 Z" fill="url(#brass)" stroke="#5a3510" stroke-width=".5"/>
  <path d="M1 1 H33 M1 1 V33" stroke="#fff0c4" stroke-width=".6" stroke-opacity=".75"/>
  <circle cx="22" cy="4" r="1.9" fill="#7a4a18"/><circle cx="22" cy="4" r="1.2" fill="#d7a256"/><circle cx="21.6" cy="3.6" r=".45" fill="#fff0c4"/>
  <circle cx="4" cy="22" r="1.9" fill="#7a4a18"/><circle cx="4" cy="22" r="1.2" fill="#d7a256"/><circle cx="3.6" cy="21.6" r=".45" fill="#fff0c4"/>

  <!-- ===== finish, bottom-right: a quarter cart wheel rolls into the corner ===== -->
  <circle cx="{WC[0]}" cy="{WC[1]}" r="{WR + 1.5}" fill="#0e1626" fill-opacity=".4" transform="translate(-1.4 -1.6)" filter="url(#soft)"/>
  <circle cx="{WC[0]}" cy="{WC[1]}" r="{WR - 4}" fill="none" stroke="#6b4a2e" stroke-width="7.6"/>
  <circle cx="{WC[0]}" cy="{WC[1]}" r="{WR - 7.6}" fill="none" stroke="#4a3220" stroke-width=".6"/>
  <circle cx="{WC[0]}" cy="{WC[1]}" r="{WR - .8}" fill="none" stroke="#3b3a3c" stroke-width="1.8"/>
  <circle cx="{WC[0]}" cy="{WC[1]}" r="{WR - 1.5}" fill="none" stroke="#c9a24a" stroke-width=".5" stroke-opacity=".8"/>
  {''.join(spokes)}
  <circle cx="{WC[0]}" cy="{WC[1]}" r="11" fill="url(#brass)" stroke="#5a3510" stroke-width=".6"/>
  <circle cx="{WC[0]}" cy="{WC[1]}" r="6" fill="#b3722f" stroke="#5a3510" stroke-width=".4"/>
  <path d="M{WC[0] - 10} {WC[1] - 3.5} A10.5 10.5 0 0 1 {WC[0] - 3.5} {WC[1] - 10}" stroke="#fff0c4" stroke-width=".6" fill="none" stroke-opacity=".8"/>

  <!-- ===== folio: moonclock, lit fraction 2/107 (a hair of waxing light on the right), brass ring ===== -->
  <circle cx="{FOL_CX}" cy="{FOL_CY}" r="8" fill="#1b2a44" stroke="#c9a24a" stroke-width=".9"/>
  <circle cx="{FOL_CX}" cy="{FOL_CY}" r="{FR}" fill="#2c3c58"/>
  <path d="M{FOL_CX} {FOL_CY - FR} A{FR} {FR} 0 0 1 {FOL_CX} {FOL_CY + FR} A{moon_rx:.3f} {FR} 0 0 0 {FOL_CX} {FOL_CY - FR} Z" fill="url(#moonG)"/>
</svg>'''

# field light: the raised lamp's glow climbing out of P002-2 into the gutter above it
LAMP = at("P002-2", .478, .25)
FIELD = f'''<svg class="blk" style="left:0; top:0; width:864pt; height:648pt; z-index:0" viewBox="0 0 864 648" aria-hidden="true">
  <defs>
    <radialGradient id="lampG" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#f7c684" stop-opacity=".55"/><stop offset=".45" stop-color="#f7c684" stop-opacity=".18"/><stop offset="1" stop-color="#f7c684" stop-opacity="0"/></radialGradient>
    <radialGradient id="moonRim" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#a6c6f5" stop-opacity=".22"/><stop offset="1" stop-color="#a6c6f5" stop-opacity="0"/></radialGradient>
  </defs>
  <ellipse cx="{LAMP[0]:.1f}" cy="{(T1B + T2) / 2}" rx="120" ry="34" fill="url(#lampG)"/>
  <ellipse cx="{(colx(7) - GUT / 2):.1f}" cy="{(T1B + T2) / 2}" rx="60" ry="16" fill="url(#lampG)" opacity=".35"/>
  <ellipse cx="800" cy="20" rx="120" ry="40" fill="url(#moonRim)"/>
</svg>'''

STYLE = '''  /* P002 "The Cart Handle": blue-slate night, cart-timber border. 36 pt margins, 12 x 49.5 pt columns, 18 pt gutters, 18 pt baseline. */
  .page.cart { background: radial-gradient(ellipse 80% 75% at 35% 46%, #42567a 0%, #384961 50%, #2c3a52 100%);
               color: #1d2433; font-family: "Source Sans 3", sans-serif; font-size: 14pt; line-height: 18pt; }
  .cart .blk { position: absolute; }
  .pnl { position: absolute; overflow: hidden; background: #0c1426; z-index: 2;
         box-shadow: 0 2.5pt 7pt rgba(8, 14, 28, .55); }
  .pnl img { position: absolute; display: block; max-width: none; }
  .pnl::after { content: ""; position: absolute; inset: 0; border: 1pt solid #b3722f;
                box-shadow: inset 0 0 0 .5pt #0c1426, inset 0 0 10pt rgba(8, 14, 28, .35); pointer-events: none; }
  .cap { position: absolute; z-index: 6; background: #F7F1E3; border: .6pt solid #b3722f; padding: 5pt 8pt; white-space: nowrap;
         font-family: "Source Serif 4", serif; font-weight: 400; font-size: 14pt; line-height: 18pt; color: #1d2433;
         box-shadow: 0 1.5pt 4pt rgba(8, 14, 28, .40); }
  .bal { position: absolute; z-index: 6; background: #FFFDF6; border: .8pt solid #1d2433; display: flex; align-items: center;
         justify-content: center; text-align: center; box-sizing: border-box;
         font-family: "Source Sans 3", sans-serif; font-weight: 600; font-size: 14pt; line-height: 18pt; color: #1d2433; }
  .bal span { display: block; }
  .nw { white-space: nowrap; }
  .tails { position: absolute; left: 0; top: 0; width: 864pt; height: 648pt; overflow: visible; pointer-events: none; z-index: 7; }
  .rh { font-family: "Source Sans 3", sans-serif; font-weight: 600; font-size: 10pt; line-height: 12pt; letter-spacing: 1.6pt;
        font-variant-caps: all-small-caps; color: #e2c486; white-space: nowrap; z-index: 6; }
  .fol { font-family: "Source Sans 3", sans-serif; font-weight: 600; font-size: 11pt; line-height: 13pt; color: #F7F1E3; letter-spacing: .4pt; z-index: 6; }'''

HTML = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>ChandRush CH01 P002</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="assets/base.css">
<link rel="stylesheet" href="assets/kit.css">
<style>
{STYLE}
</style>
</head>
<body>
<div class="page cart" id="page" data-chapter="CH01" data-page="P002">

<!-- ========== field light ========== -->
{FIELD}

<!-- ========== panels ========== -->
{chr(10).join(panel_html(p) for p in PANELS)}

<!-- ========== border: the parked cart ========== -->
{BORDER}
<div class="blk fol" style="left:{FOL_CX + 12}pt; top:{FOL_CY - 6.5}pt">2</div>

<!-- running head (verso: outer edge = left), tucked under the handle -->
<div class="blk rh" style="left:{M}pt; top:20pt">CHAPTER 01 · NUMBERS · PG 002</div>

<!-- ========== P002-1: caption low on the paving ========== -->
<div class="cap" style="left:{C1["x"]}pt; top:{C1["y"]}pt">Tez walks into a parked cart handle.</div>

<!-- ========== P002-2: Ahana asks first (top), Tez answers (right), caption on the paving ========== -->
{balloon(B2a, '<span class="nw">Are you all right?</span>', "st")}
{balloon(B2b, '<span style="width:86pt">I knew that was there.</span>', "st")}
<div class="cap" style="left:{C2["x"]}pt; top:{C2["y"]}pt">Ahana catches the handle. She lifts the lamp higher.</div>

<!-- ========== P002-3: the joke, to the cart ========== -->
{balloon(B3, '<span class="nw">I was asking the cart.</span>', "st")}

<svg class="tails" viewBox="0 0 864 648" aria-hidden="true">
  {tails_svg()}
</svg>

</div>
<script>
  /* screen only: scale the 12x9 in sheet to fit the window; printing ignores this */
  (function () {{
    var p = document.getElementById("page");
    function fit() {{
      p.style.zoom = 1;
      var s = Math.min(document.documentElement.clientWidth / p.offsetWidth, window.innerHeight / p.offsetHeight);
      p.style.zoom = s;
    }}
    if (window.matchMedia && !window.matchMedia("print").matches) {{ window.addEventListener("resize", fit); fit(); }}
  }})();
</script>
</body>
</html>
'''
OUT.write_text(HTML, encoding="utf-8")
print("wrote", OUT)
