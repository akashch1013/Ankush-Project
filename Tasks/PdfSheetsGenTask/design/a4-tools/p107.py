#!/usr/bin/env python3
"""CH01 P107 (story finale) page generator: B1 family, Food Street border (peacock teal, canopy seam,
brass bracket, hanging lantern). Writes PdfSheetsGenTask/CH01/P107/index.html. Run from anywhere."""
import math, pathlib
import sys as _sys; _sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); from common import bln

OUT = pathlib.Path(__file__).resolve().parents[2] / "CH01" / "P107" / "index.html"

# ---------- panels (page pt) ----------
# id, x, y, w, h, image px size, image placement: scale (pt/px), offset x/y (pt, applied to img)
PANELS = [
    dict(id="P107-1", x=24,  y=24,  w=566, h=300, iw=1536, ih=1024, s=566/1536, ox=0,  oy=-8, arch=True),
    dict(id="P107-2", x=600, y=24,  w=240, h=300, iw=1024, ih=1536, s=240/1024, ox=0,  oy=-9),
    dict(id="P107-3", x=24,  y=334, w=250, h=274, iw=1536, ih=1024, s=274/1024, ox=-480*274/1024, oy=0),
    dict(id="P107-4", x=284, y=334, w=176, h=274, iw=1536, ih=1024, s=274/1024, ox=-850*274/1024, oy=0),
    dict(id="P107-5", x=470, y=334, w=370, h=274, iw=1536, ih=1024, s=274/1024, ox=-153*274/1024, oy=0),
]
P = {p["id"]: p for p in PANELS}

def at(pid, px, py):
    """image pixel -> page pt"""
    p = P[pid]
    return (p["x"] + p["ox"] + px * p["s"], p["y"] + p["oy"] + py * p["s"])

INK = "#1d2433"; IVORY = "#FFFDF6"

# ---------- tails ----------
def tail(b1, b2, tip, bend=4.0):
    """curved wedge from base points b1,b2 (on the balloon edge) to tip; base seam covered in ivory."""
    mx1, my1 = (b1[0] + tip[0]) / 2, (b1[1] + tip[1]) / 2
    mx2, my2 = (b2[0] + tip[0]) / 2, (b2[1] + tip[1]) / 2
    dx, dy = tip[0] - (b1[0] + b2[0]) / 2, tip[1] - (b1[1] + b2[1]) / 2
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L * bend, dx / L * bend
    cx = (b1[0] + b2[0]) / 2 - dx / L * 1.2   # cover line sits just inside the balloon
    cy = (b1[1] + b2[1]) / 2 - dy / L * 1.2
    ux, uy = (b2[0] - b1[0]), (b2[1] - b1[1])
    c1 = (cx - ux * .5, cy - uy * .5); c2 = (cx + ux * .5, cy + uy * .5)
    return (f'<path d="M{b1[0]:.1f} {b1[1]:.1f} Q{mx1+nx:.1f} {my1+ny:.1f} {tip[0]:.1f} {tip[1]:.1f} '
            f'Q{mx2+nx*.6:.1f} {my2+ny*.6:.1f} {b2[0]:.1f} {b2[1]:.1f}" fill="{IVORY}" stroke="{INK}" stroke-width=".8" stroke-linejoin="round"/>'
            f'<path d="M{c1[0]:.1f} {c1[1]:.1f} L{c2[0]:.1f} {c2[1]:.1f}" stroke="{IVORY}" stroke-width="2.2"/>')

def ell(cx, cy, rx, ry, deg):
    a = math.radians(deg); return (cx + rx * math.cos(a), cy + ry * math.sin(a))

def stadium_end(x, y, w, h, deg, right=True):
    r = h / 2; cx = x + w - r if right else x + r; cy = y + r
    a = math.radians(deg); return (cx + r * math.cos(a), cy + r * math.sin(a))

# ---------- balloons / captions (page pt) ----------
# P107-2 Tez: stadium in the calm upper-left; tail down the gap between Riya and Tara, pointing at Tez's mouth
B2 = dict(x=604, y=52, w=180, h=46)
tez_mouth = at("P107-2", 500, 997)
B2tip = at("P107-2", 590, 765)
# P107-4 Tara "Come.": ellipse left of her face, tail to her mouth (profile faces left)
B4 = dict(x=287, y=360, w=58, h=32)
tara4_mouth = at("P107-4", 1135, 232)
B4tip = at("P107-4", 1098, 238)
# P107-5 Tara: wide flat stadium across the calm top, tail from its right end to her mouth
B5 = dict(x=494, y=338, w=214, h=66)
tara5_mouth = at("P107-5", 1122, 252)
B5tip = at("P107-5", 1086, 262)

BALLOONS = bln([   # reading order; one outline per balloon + tail (pipeline/balloon.py)
    dict(text="Please tell me he hasn’t ruined dinner.", at=[B2["x"], B2["y"]], w=B2["w"], h=B2["h"], maxw=B2["w"] - 22, tip=B2tip, bend=-.06),
    dict(text="Come.", at=[B4["x"], B4["y"]], w=B4["w"], h=B4["h"], shape="oval", tip=B4tip),
    dict(text="I’ll tell you what I know. But first, nobody touches those serving controls.", at=[B5["x"], B5["y"]], w=B5["w"], h=B5["h"],
         maxw=B5["w"] - 24, shape="round", radius=24, tip=B5tip),
])

def tails_svg():
    out = []
    # P107-2: base on the flat bottom edge
    by = B2["y"] + B2["h"]
    out.append(tail((B2["x"] + 130, by - .2), (B2["x"] + 143, by - .2), B2tip, bend=-5))
    # P107-4: ellipse
    cx, cy, rx, ry = B4["x"] + B4["w"] / 2, B4["y"] + B4["h"] / 2, B4["w"] / 2, B4["h"] / 2
    out.append(tail(ell(cx, cy, rx - .2, ry - .2, 2), ell(cx, cy, rx - .2, ry - .2, 38), B4tip, bend=2))
    # P107-5: right end of the stadium
    out.append(tail(stadium_end(B5["x"], B5["y"], B5["w"], B5["h"] - .4, 8), stadium_end(B5["x"], B5["y"], B5["w"], B5["h"] - .4, 42), B5tip, bend=2.5))
    return "\n  ".join(out)

def panel_html(p):
    img_w = p["iw"] * p["s"]; img_h = p["ih"] * p["s"]
    cls = "pnl arch" if p.get("arch") else "pnl"
    return (f'<div class="{cls}" style="left:{p["x"]}pt; top:{p["y"]}pt; width:{p["w"]}pt; height:{p["h"]}pt">'
            f'<img src="assets/img/{p["id"]}.jpg" alt="" style="left:{p["ox"]:.2f}pt; top:{p["oy"]:.2f}pt; width:{img_w:.2f}pt; height:{img_h:.2f}pt"></div>')

# ---------- border (Food Street: peacock-teal lacquer, saffron-brass pinstripe, canopy seam, brass bracket, lantern) ----------
def scallops(x0, x1, y, n, depth):
    step = (x1 - x0) / n; d = f"M{x0} {y}"
    for i in range(n):
        a = x0 + i * step
        d += f" Q{a + step/2:.1f} {y + depth*2:.1f} {a + step:.1f} {y}"
    return d

SEAM_X0, SEAM_X1, SEAM_Y = 214, 470, 10.5
BORDER = f'''
<svg class="blk" style="left:0; top:0; width:864pt; height:648pt" viewBox="0 0 864 648" aria-hidden="true">
  <defs>
    <linearGradient id="brass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f3d58f"/><stop offset=".45" stop-color="#c98f45"/><stop offset=".75" stop-color="#b3722f"/><stop offset="1" stop-color="#6e4318"/></linearGradient>
    <linearGradient id="brassR" x1="1" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#6e4318"/><stop offset=".3" stop-color="#b3722f"/><stop offset=".6" stop-color="#d9a55a"/><stop offset="1" stop-color="#f3d58f"/></linearGradient>
    <linearGradient id="lantern" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#6e4318"/><stop offset=".35" stop-color="#d9a55a"/><stop offset=".55" stop-color="#f3d58f"/><stop offset="1" stop-color="#7a4a18"/></linearGradient>
    <radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#f7c684" stop-opacity=".75"/><stop offset=".45" stop-color="#f7c684" stop-opacity=".22"/><stop offset="1" stop-color="#f7c684" stop-opacity="0"/></radialGradient>
    <radialGradient id="spill" cx=".5" cy="0" r=".9"><stop offset="0" stop-color="#f7c684" stop-opacity=".30"/><stop offset="1" stop-color="#f7c684" stop-opacity="0"/></radialGradient>
    <radialGradient id="moonG" cx=".38" cy=".35" r=".7"><stop offset="0" stop-color="#fff6da"/><stop offset=".6" stop-color="#f1d79a"/><stop offset="1" stop-color="#c99a4c"/></radialGradient>
    <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.3"/></filter>
  </defs>

  <!-- lacquer sheen: a faint diagonal highlight on the teal -->
  <path d="M0 0 H300 L0 260 Z" fill="#3f8584" fill-opacity=".10"/>
  <path d="M864 648 H600 L864 420 Z" fill="#0d2c2b" fill-opacity=".25"/>

  <!-- Lantern Street light spilling out of the doorway panel onto the gutter -->
  <ellipse cx="300" cy="329" rx="250" ry="14" fill="url(#spill)"/>

  <!-- saffron-brass pinstripe 12 pt inside the trim; broken at the entry seam, the folio and the finish lantern -->
  <path fill="none" stroke="#c9a24a" stroke-width=".8"
        d="M{SEAM_X1+14} 12 H852 V606 M{844} 636 M{772} 636 H448 M416 636 H12 V162"/>

  <!-- ===== entry, top-left: brass post-bracket corner joint ===== -->
  <g>
    <path d="M1.6 1.6 H47 V12 L40 19 H19 V40 L12 47 H1.6 Z" fill="#081c1b" fill-opacity=".35" transform="translate(1.4 1.6)" filter="url(#soft)"/>
    <path d="M0 0 H46 V12 L39 19 H19 V39 L12 46 H0 Z" fill="url(#brass)" stroke="#5a3510" stroke-width=".6"/>
    <path d="M45.4 1 V11.6 L38.6 18.4 H18.4 V38.6 L11.6 45.4" fill="none" stroke="#5a3510" stroke-width=".9" stroke-opacity=".7"/>
    <path d="M2 2 H44 M2 2 V44" fill="none" stroke="#fff0c4" stroke-width=".8" stroke-opacity=".8"/>
    <circle cx="9.5" cy="9.5" r="3.1" fill="#7a4a18"/><circle cx="9.5" cy="9.5" r="2.2" fill="#d7a256"/><circle cx="8.7" cy="8.6" r=".9" fill="#fff0c4"/>
  </g>
  <!-- the doorway moulding: a brass echo of the arch, from the bracket's foot to the top margin -->
  <path d="M15 152 A179 137 0 0 1 194 15" fill="none" stroke="#b3722f" stroke-width="1.1"/>
  <path d="M17.2 152 A176.8 134.8 0 0 1 194 17.2" fill="none" stroke="#f3d58f" stroke-width=".45" stroke-opacity=".6"/>
  <circle cx="15" cy="154" r="2" fill="#b3722f" stroke="#6e4318" stroke-width=".4"/>
  <!-- curved brace from the bracket into the arch corner -->
  <path d="M19 39 C40 44 52 52 58 66" fill="none" stroke="#b3722f" stroke-width="1"/>
  <circle cx="58.4" cy="67.4" r="1.8" fill="#b3722f" stroke="#6e4318" stroke-width=".4"/>
  <!-- canopy seam along the top margin: two scalloped curves (saffron over brass) and a curled brass terminal -->
  <path d="M194 15 H{SEAM_X0}" fill="none" stroke="#b3722f" stroke-width="1.1"/>
  <rect x="{SEAM_X0-3}" y="11.6" width="4" height="7.4" rx="1.4" fill="#b3722f" stroke="#6e4318" stroke-width=".4"/>
  <path d="{scallops(SEAM_X0, SEAM_X1, SEAM_Y, 6, 3.0)}" fill="none" stroke="#e0913a" stroke-width="1"/>
  <path d="{scallops(SEAM_X0, SEAM_X1, SEAM_Y + 3.2, 6, 3.0)}" fill="none" stroke="#c9a24a" stroke-width=".6"/>
  <path d="M{SEAM_X1} {SEAM_Y} C{SEAM_X1+7} {SEAM_Y} {SEAM_X1+10} {SEAM_Y+5} {SEAM_X1+7} {SEAM_Y+7.4} C{SEAM_X1+4.6} {SEAM_Y+9.2} {SEAM_X1+2} {SEAM_Y+7.2} {SEAM_X1+3.4} {SEAM_Y+5.2}" fill="none" stroke="#b3722f" stroke-width="1"/>

  <!-- ===== top-right, bottom-left: small plain corner ticks ===== -->
  <path d="M846 6 H858 V18" fill="none" stroke="#c9a24a" stroke-width="1.1"/><circle cx="858" cy="6" r="1.4" fill="#c9a24a"/>
  <path d="M6 630 V642 H18" fill="none" stroke="#c9a24a" stroke-width="1.1"/><circle cx="6" cy="642" r="1.4" fill="#c9a24a"/>

  <!-- ===== finish, bottom-right: smaller bracket joint, short return arm, hanging lantern (the chapter's last light) ===== -->
  <g transform="translate(864 648) scale(-1 -1)">
    <path d="M1.6 1.6 H37 V10 L31 16 H16 V31 L10 37 H1.6 Z" fill="#081c1b" fill-opacity=".3" transform="translate(-1.4 -1.6)" filter="url(#soft)"/>
    <path d="M0 0 H36 V10 L30 16 H16 V30 L10 36 H0 Z" fill="url(#brassR)" stroke="#5a3510" stroke-width=".6"/>
    <path d="M35.4 1 V9.6 L29.6 15.4 H15.4 V29.6 L9.6 35.4" fill="none" stroke="#fff0c4" stroke-width=".7" stroke-opacity=".6"/>
    <circle cx="8" cy="8" r="2.6" fill="#7a4a18"/><circle cx="8" cy="8" r="1.8" fill="#d7a256"/>
  </g>
  <path d="M855 614 H776 C770 614 768 618 771 620.6 C773.4 622.4 776 620.6 775 618.6" fill="none" stroke="#b3722f" stroke-width="1"/>
  <path d="M855 615.4 H778" fill="none" stroke="#f3d58f" stroke-width=".45" stroke-opacity=".6"/>
  <circle cx="808" cy="630" r="26" fill="url(#glow)"/>
  <path d="M808 614 V620" stroke="#8a5a22" stroke-width=".7"/>
  <circle cx="808" cy="620.6" r="1.4" fill="none" stroke="#b3722f" stroke-width=".6"/>
  <!-- lantern: domed cap, glass body with brass ribs, base finial -->
  <path d="M801.6 625 C802 621.8 804.6 621.6 808 621.6 C811.4 621.6 814 621.8 814.4 625 Z" fill="url(#lantern)" stroke="#6e4318" stroke-width=".5"/>
  <path d="M802.6 625 H813.4 L812.2 636 H803.8 Z" fill="#ffd98c" stroke="#7a4a18" stroke-width=".5"/>
  <path d="M804.6 625.6 H811.4 L810.6 635.4 H805.4 Z" fill="#fff3c8"/>
  <path d="M806.2 625 L806.4 636 M809.8 625 L809.6 636" stroke="#9a6526" stroke-width=".5"/>
  <path d="M803.4 636 H812.6 L811 638.6 H805 Z" fill="url(#lantern)" stroke="#6e4318" stroke-width=".4"/>
  <path d="M808 638.6 V641.4" stroke="#b3722f" stroke-width=".8"/><circle cx="808" cy="642" r=".9" fill="#b3722f"/>

  <!-- ===== folio: the moon is full on the chapter's last page (107/107), set in a brass ring ===== -->
  <circle cx="422" cy="636" r="8" fill="#0d2c2b" stroke="#c9a24a" stroke-width=".7"/>
  <circle cx="422" cy="636" r="5.4" fill="url(#moonG)"/>
  <circle cx="420.4" cy="634.6" r="1.2" fill="#e2c486" fill-opacity=".7"/><circle cx="423.8" cy="637.6" r=".8" fill="#e2c486" fill-opacity=".6"/>
</svg>
<div class="blk fol" style="left:433pt; top:629.5pt">107</div>
'''

CSS = '''
  /* B1 family, story re-material for Food Street: peacock-teal lacquer field, light matte reading shapes */
  .page.foodst { background: radial-gradient(ellipse 75% 70% at 50% 48%, #2b6665 0%, #245857 55%, #183f3e 100%);
                 color: #1d2433; font-family: "Source Sans 3", sans-serif; font-size: 14pt; line-height: 18pt; }
  .foodst .blk { position: absolute; }
  .pnl { position: absolute; overflow: hidden; background: #0c1f1f;
         box-shadow: 0 2.5pt 7pt rgba(4, 18, 18, .55); }
  .pnl img { position: absolute; display: block; max-width: none; }
  .pnl::after { content: ""; position: absolute; inset: 0; border: 1pt solid #b3722f; border-radius: inherit;
                box-shadow: inset 0 0 0 .5pt #0c1f1f, inset 0 0 10pt rgba(5, 20, 20, .35); pointer-events: none; }
  .pnl.arch { border-top-left-radius: 170pt 130pt; }
  /* warm Lantern Street light entering the doorway panel from behind the group */
  .pnl.arch::before { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 70pt; z-index: 1;
                      background: linear-gradient(to top, rgba(247, 198, 132, .22), rgba(247, 198, 132, 0)); pointer-events: none; }

  .cap { position: absolute; background: #F7F1E3; border: .6pt solid #b3722f; padding: 5pt 8pt;
         font-family: "Source Serif 4", serif; font-weight: 400; font-size: 14pt; line-height: 18pt; color: #1d2433;
         box-shadow: 0 1.5pt 4pt rgba(10, 25, 25, .35); }
  .bal { position: absolute; background: #FFFDF6; border: .8pt solid #1d2433; display: flex; align-items: center;
         justify-content: center; text-align: center; box-sizing: border-box;
         font-family: "Source Sans 3", sans-serif; font-weight: 600; font-size: 14pt; line-height: 18pt; color: #1d2433; }
  .bal.ov { border-radius: 50%; }
  .bal span { display: block; }
  .nw { white-space: nowrap; }
  .tails { position: absolute; left: 0; top: 0; width: 864pt; height: 648pt; overflow: visible; pointer-events: none; }
  .fol { font-family: "Source Sans 3", sans-serif; font-weight: 600; font-size: 11pt; line-height: 13pt; color: #F7F1E3; letter-spacing: .4pt; }
'''

def balloon(b, html, shape):
    r = "border-radius:50%" if shape == "ov" else f"border-radius:{b['h']/2:.1f}pt"
    return (f'<div class="bal" style="left:{b["x"]}pt; top:{b["y"]}pt; width:{b["w"]}pt; height:{b["h"]}pt; {r}">{html}</div>')

BODY = f'''
<!-- ========== panels ========== -->
{chr(10).join(panel_html(p) for p in PANELS)}

<!-- ========== border ========== -->
{BORDER}

<!-- ========== P107-1: caption in the calm upper right ========== -->
<div class="cap" style="left:274pt; top:32pt; width:290pt">Power reaches the shutters. They rise, revealing Food Street. Bowls have fallen. A cart blocks the entrance. A dosa hangs over a plate far too small to hold it.</div>

<!-- ========== P107-2: caption breaks the top frame; Tez's balloon in the calm upper-left ========== -->
<div class="cap" style="left:608pt; top:20pt"><span class="nw">Tez’s ears drop.</span></div>

<!-- ========== P107-3 caption ========== -->
<div class="cap" style="left:32pt; top:342pt; width:118pt">Tara takes the evidence sleeve from Ahana.</div>

<!-- ========== P107-4 / P107-5 Tara ========== -->
{BALLOONS}
'''

HTML = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>ChandRush CH01 P107</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="assets/base.css">
<link rel="stylesheet" href="assets/kit.css">
<style>{CSS}</style>
</head>
<body>
<div class="page foodst" id="page" data-chapter="CH01" data-page="P107">
{BODY}
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

if __name__ == "__main__":
    OUT.write_text(HTML, encoding="utf-8")
    print("wrote", OUT)
    for k, v in dict(tez_mouth=tez_mouth, B2tip=B2tip, tara4_mouth=tara4_mouth, B4tip=B4tip, tara5_mouth=tara5_mouth, B5tip=B5tip).items():
        print(f"  {k}: {v[0]:.1f}, {v[1]:.1f}")
