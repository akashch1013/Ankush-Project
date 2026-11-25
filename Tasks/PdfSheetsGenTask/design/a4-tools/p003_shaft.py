#!/usr/bin/env python3
"""CH01 P003 "The Shaft" (story, recto) page generator. Writes PdfSheetsGenTask/CH01/P003/index.html.

Book system copied from P005 "Two Towns" (grid, running head, moonclock folio) and P107 (panel frames,
caption paper, speech balloons, curved tails).
Grid: 864x648 pt, 36 pt margins, 12 columns of 49.5 pt with 18 pt gutters, 18 pt baseline.
Left block = columns 0-8 (36-625.5): caption on the field, wide P003-1, a balloon band on the field, then
P003-3 | P003-4. Right = columns 9-11 (643.5-828): the full-height shaft panel P003-2.
Field: aubergine at the top -> store-lamp umber at the foot. Border: the brass safety gate (left rail,
latch at the entry), the lower store's timber landing as the page floor, a blank brass level plate at the finish.
"""
import math, pathlib

OUT = pathlib.Path(__file__).resolve().parents[2] / "CH01" / "P003" / "index.html"

M, COLW, GUT = 36, 49.5, 18
def colx(i): return M + i * (COLW + GUT)
def colr(i): return colx(i) + COLW

# ---------- panels (page pt). s = pt per image px; ox/oy = image offset inside the panel ----------
# 2026-11-25 (user): captions and balloons sit ON the art, never in a band between panels; tight 10 pt gutters.
CAP1 = dict(x=M + 6, y=42, w=310)                      # caption on P003-1's dark gate canopy (image x .004-.54, y .01-.18)
PANELS = [
    # P003-1: full width of cols 0-8, from the top margin; crop px y 0-737 (Tara's hand on the lamp, every head, all of Tez's head)
    dict(id="P003-1", x=M, y=36, w=colr(8) - M, h=283, iw=1536, ih=1024, s=(colr(8) - M) / 1536, ox=0, oy=0),
    # P003-2: the shaft, cols 9-11, full live height; window px x 310-802 (dark shaft top for the caption)
    dict(id="P003-2", x=colx(9), y=M, w=colr(11) - colx(9), h=576, iw=1024, ih=1536, s=576 / 1536, ox=-310 * 576 / 1536, oy=0),
    # P003-3 / P003-4 (re-staged s2 art): 10 pt under P003-1, 10 pt apart, to the bottom margin; whole square images
    # (P003-3 shows the whole image at 283 pt; P003-4 fits its width, image y .0-.95)
    dict(id="P003-3", x=M, y=329, w=282, h=283, iw=1024, ih=1024, s=283 / 1024, ox=-.5, oy=0),
    dict(id="P003-4", x=M + 292, y=329, w=colr(8) - (M + 292), h=283, iw=1024, ih=1024, s=(colr(8) - (M + 292)) / 1024, ox=0, oy=0),
]
P = {p["id"]: p for p in PANELS}

def at(pid, px, py):
    p = P[pid]
    return (p["x"] + p["ox"] + px * p["s"], p["y"] + p["oy"] + py * p["s"])

INK = "#1d2433"; IVORY = "#FFFDF6"

def tail(b1, b2, tip, bend=4.0):
    """P107 tail: curved wedge from base points b1,b2 (on the balloon edge) to tip; base seam covered in ivory."""
    mx1, my1 = (b1[0] + tip[0]) / 2, (b1[1] + tip[1]) / 2
    mx2, my2 = (b2[0] + tip[0]) / 2, (b2[1] + tip[1]) / 2
    dx, dy = tip[0] - (b1[0] + b2[0]) / 2, tip[1] - (b1[1] + b2[1]) / 2
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L * bend, dx / L * bend
    cx = (b1[0] + b2[0]) / 2 - dx / L * 1.2
    cy = (b1[1] + b2[1]) / 2 - dy / L * 1.2
    ux, uy = (b2[0] - b1[0]), (b2[1] - b1[1])
    c1 = (cx - ux * .5, cy - uy * .5); c2 = (cx + ux * .5, cy + uy * .5)
    return (f'<path d="M{b1[0]:.1f} {b1[1]:.1f} Q{mx1+nx:.1f} {my1+ny:.1f} {tip[0]:.1f} {tip[1]:.1f} '
            f'Q{mx2+nx*.6:.1f} {my2+ny*.6:.1f} {b2[0]:.1f} {b2[1]:.1f}" fill="{IVORY}" stroke="{INK}" stroke-width=".8" stroke-linejoin="round"/>'
            f'<path d="M{c1[0]:.1f} {c1[1]:.1f} L{c2[0]:.1f} {c2[1]:.1f}" stroke="{IVORY}" stroke-width="2.2"/>')

# ---------- balloons ON the art, over the calm band above Tara's head (her hair top is image y .155) ----------
mouth3 = at("P003-3", .475 * 1024, .255 * 1024)   # Tara's mouth, P003-3 (looking down, face turned screen-left)
mouth4 = at("P003-4", .375 * 1024, .255 * 1024)   # Tara's mouth, P003-4 (face turned screen-right)
# P003-3: two lines across the gate canopy and the lamp's crown (image x .03-.81, y .0-.14); its top edge sits 6 pt
# over the panel border
B3 = dict(x=M + 8, y=323, w=220, h=46)
# P003-4: three lines over the gate canopy, lamp crown and sky; it breaks the panel's top edge by 21 pt
# (over the gutter and P003-1's lowest strip of legs and robe, no faces) so it clears Tara's hair
B4 = dict(x=M + 300, y=308, w=282, h=64, r=22)
def tip_short(m, frm, short=7):
    dx, dy = m[0] - frm[0], m[1] - frm[1]; L = math.hypot(dx, dy)
    return (m[0] - dx / L * short, m[1] - dy / L * short)
# tails come in from the upper-left, over the dark wall beside her face, and stop just short of the mouth
B3base = ((B3["x"] + 84, B3["y"] + B3["h"] - .3), (B3["x"] + 98, B3["y"] + B3["h"] - .3))
B4base = ((B4["x"] + 126, B4["y"] + B4["h"] - .3), (B4["x"] + 140, B4["y"] + B4["h"] - .3))
B3tip = at("P003-3", .412 * 1024, .200 * 1024)    # at the edge of her silver hair, beside the face, toward the mouth
B4tip = at("P003-4", .428 * 1024, .243 * 1024)    # in the air just in front of her mouth (she faces screen-right)

# ---------- overlays ----------
# P003-1: exact level strip insert over the painted blank strip (px x 889-923, y 200-500): +2 ... -8, equal spacing
S1 = P["P003-1"]
SX0, SY0 = at("P003-1", 889, 203)
SX1, SY1 = at("P003-1", 923, 497)
LEVELS = list(range(2, -9, -1))           # +2 .. -8 (11 marks)
def lvl(v):
    return ("+" + str(v)) if v > 0 else ("−" + str(-v) if v < 0 else "0")
step = (SY1 - SY0 - 8) / (len(LEVELS) - 1)
strip_marks = []
for i, v in enumerate(LEVELS):
    y = SY0 + 4 + i * step
    strip_marks.append(f'<path d="M{SX0 + .6:.2f} {y:.2f} h{2.6 if v else 4:.1f}" stroke="#2a1d10" stroke-width="{.7 if v == 0 else .45}"/>'
                       f'<text x="{SX1 - .9:.2f}" y="{y + 2.1:.2f}" text-anchor="end">{lvl(v)}</text>')

# P003-2: "-8" on the blank brass landing plate (px 437-522, 940-976)
PL = at("P003-2", 437, 941); PR = at("P003-2", 522, 976)

SH = P["P003-2"]
SHX0, SHX1, SHY0, SHY1 = SH["x"], SH["x"] + SH["w"], SH["y"], SH["y"] + SH["h"]

BORDER = f'''
<svg class="blk" style="left:0; top:0; width:864pt; height:648pt; z-index:0" viewBox="0 0 864 648" aria-hidden="true">
  <defs>
    <linearGradient id="brass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f3d58f"/><stop offset=".45" stop-color="#c98f45"/><stop offset=".75" stop-color="#b3722f"/><stop offset="1" stop-color="#6e4318"/></linearGradient>
    <linearGradient id="brassH" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#6e4318"/><stop offset=".3" stop-color="#d6a64e"/><stop offset=".5" stop-color="#f3d58f"/><stop offset=".75" stop-color="#b3722f"/><stop offset="1" stop-color="#6e4318"/></linearGradient>
    <linearGradient id="timber" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a06a34"/><stop offset=".5" stop-color="#8a5a2b"/><stop offset="1" stop-color="#5e3a1b"/></linearGradient>
    <radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#f7c684" stop-opacity=".55"/><stop offset=".5" stop-color="#f7c684" stop-opacity=".16"/><stop offset="1" stop-color="#f7c684" stop-opacity="0"/></radialGradient>
    <radialGradient id="spill" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffc874" stop-opacity=".42"/><stop offset=".55" stop-color="#e8a24f" stop-opacity=".14"/><stop offset="1" stop-color="#e8a24f" stop-opacity="0"/></radialGradient>
    <radialGradient id="moonG" cx=".38" cy=".35" r=".7"><stop offset="0" stop-color="#fff6da"/><stop offset=".6" stop-color="#f1d79a"/><stop offset="1" stop-color="#c99a4c"/></radialGradient>
    <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.3"/></filter>
  </defs>

  <!-- store-lamp light rising out of the foot of the shaft onto the umber field and the landing -->
  <ellipse cx="{(SHX0 + SHX1) / 2:.1f}" cy="626" rx="150" ry="46" fill="url(#spill)"/>

  <!-- top pinstripe 12 pt inside the trim, from the latch to the right edge and down the right side; broken at the finish -->
  <path fill="none" stroke="#c9a24a" stroke-width=".8" d="M44 12 H852 V598"/>
  <path fill="none" stroke="#c9a24a" stroke-width=".3" stroke-opacity=".55" d="M44 14.4 H849.6 V598"/>

  <!-- ===== entry, top-left: the gate latch block (brass, knob, two rivets) ===== -->
  <g>
    <rect x="5.6" y="9.6" width="16" height="24" rx="1.6" fill="#140c1c" fill-opacity=".45" filter="url(#soft)"/>
    <rect x="4" y="7" width="16" height="24" rx="1.6" fill="url(#brass)" stroke="#5a3510" stroke-width=".6"/>
    <path d="M5 8 H19 M5 8 V30" stroke="#fff0c4" stroke-width=".6" stroke-opacity=".8"/>
    <circle cx="12" cy="13" r="1.1" fill="#6e4318"/><circle cx="12" cy="26" r="1.1" fill="#6e4318"/>
    <path d="M20 19.5 H32" stroke="#b3722f" stroke-width="2.4" stroke-linecap="round"/>
    <path d="M20 18.8 H32" stroke="#f3d58f" stroke-width=".6" stroke-opacity=".8"/>
    <circle cx="33.5" cy="19.5" r="3.2" fill="#7a4a18"/><circle cx="33.5" cy="19.5" r="2.4" fill="#d7a256"/><circle cx="32.7" cy="18.6" r=".9" fill="#fff0c4"/>
    <path d="M20 12 H44" stroke="#c9a24a" stroke-width=".8"/>
  </g>

  <!-- ===== left: the gate's side rail, a double brass rail with rivets on the 36 pt rhythm ===== -->
  <path d="M11 31 V612" stroke="#b3722f" stroke-width="1.1"/>
  <path d="M14.2 31 V612" stroke="#f3d58f" stroke-width=".6" stroke-opacity=".75"/>
  {''.join(f'<circle cx="12.6" cy="{y}" r="1.5" fill="#b3722f" stroke="#5a3510" stroke-width=".35"/>' for y in range(72, 612, 72))}
  <!-- rail foot: a brass shoe resting on the landing -->
  <rect x="7.6" y="612" width="10" height="5" rx="1" fill="url(#brass)" stroke="#5a3510" stroke-width=".45"/>

  <!-- ===== floor: the lower store's timber landing edge, broken at the folio ===== -->
  <g>
    <rect x="7.6" y="617" width="396" height="6.6" fill="url(#timber)"/>
    <rect x="452" y="617" width="342" height="6.6" fill="url(#timber)"/>
    <path d="M7.6 619.2 H403.6 M452 619.2 H794 M7.6 621.6 H403.6 M452 621.6 H794" stroke="#3e2410" stroke-width=".3" stroke-opacity=".55"/>
    <path d="M7.6 617.2 H403.6 M452 617.2 H794" stroke="#e0b070" stroke-width=".4" stroke-opacity=".7"/>
    <rect x="178" y="616.2" width="5" height="8.2" fill="#b3722f" stroke="#5a3510" stroke-width=".35"/>
    <rect x="638" y="616.2" width="5" height="8.2" fill="#b3722f" stroke="#5a3510" stroke-width=".35"/>
  </g>

  <!-- ===== finish, bottom-right: the blank brass level plate at the landing's end, in the store light ===== -->
  <circle cx="811" cy="620" r="34" fill="url(#glow)"/>
  <g>
    <rect x="801.4" y="613.6" width="26" height="14" rx="1.4" fill="#140c1c" fill-opacity=".4" filter="url(#soft)"/>
    <rect x="799" y="611" width="26" height="14" rx="1.4" fill="url(#brass)" stroke="#5a3510" stroke-width=".6"/>
    <rect x="801.2" y="613.2" width="21.6" height="9.6" rx=".8" fill="none" stroke="#6e4318" stroke-width=".4" stroke-opacity=".7"/>
    <circle cx="802.6" cy="618" r=".9" fill="#6e4318"/><circle cx="821.4" cy="618" r=".9" fill="#6e4318"/>
  </g>
  <path d="M852 598 V606" stroke="#c9a24a" stroke-width=".8"/>
  <circle cx="852" cy="607.5" r="1.4" fill="#c9a24a"/>

  <!-- ===== moonclock folio: lit fraction 3/107 (a thin waxing crescent, lit on the right), brass ring ===== -->
  <circle cx="422" cy="630" r="8" fill="#2a1a24" stroke="#c9a24a" stroke-width=".8"/>
  <circle cx="422" cy="630" r="5.4" fill="#3b2b3a"/>
  <path d="M422 624.6 A5.4 5.4 0 0 1 422 635.4 A{5.4 * (1 - 2 * 3 / 107):.3f} 5.4 0 0 0 422 624.6 Z" fill="url(#moonG)"/>
</svg>
<div class="blk fol" style="left:433pt; top:623.5pt">3</div>
<div class="blk rh" style="right:36pt; top:19pt">CHAPTER 01 · NUMBERS · PG 003</div>
'''

# ---------- shaft furniture: gate-rail side frames, guard ribs across the gutter top, lift cables ----------
GX = colr(8)            # left edge of the gutter between the left block and the shaft
SHAFT_SVG = f'''
<svg class="blk" style="left:0; top:0; width:864pt; height:648pt; z-index:3; pointer-events:none" viewBox="0 0 864 648" aria-hidden="true">
  <defs>
    <linearGradient id="railV" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#6e4318"/><stop offset=".35" stop-color="#d6a64e"/><stop offset=".55" stop-color="#f3d58f"/><stop offset="1" stop-color="#8a5622"/></linearGradient>
  </defs>
  <!-- the shaft's side frames as brass gate rails -->
  <rect x="{SHX0 - 2.2:.1f}" y="{SHY0 - 4}" width="4.4" height="{SHY1 - SHY0 + 8}" fill="url(#railV)" stroke="#4a2b0e" stroke-width=".4"/>
  <rect x="{SHX1 - 2.2:.1f}" y="{SHY0 - 4}" width="4.4" height="{SHY1 - SHY0 + 8}" fill="url(#railV)" stroke="#4a2b0e" stroke-width=".4"/>
  {''.join(f'<circle cx="{x:.1f}" cy="{y}" r="1.15" fill="#5a3510"/><circle cx="{x - .35:.1f}" cy="{y - .35}" r=".45" fill="#fff0c4"/>' for x in (SHX0, SHX1) for y in range(54, 612, 36))}
  <!-- three short guard ribs crossing the gutter at the top only: looking past the street guard -->
  {''.join(f'<rect x="{GX - 2:.1f}" y="{y}" width="{SHX0 - GX + 2:.1f}" height="2.6" rx="1.2" fill="#b3722f" stroke="#4a2b0e" stroke-width=".35"/><path d="M{GX - 1.5:.1f} {y + .7} H{SHX0:.1f}" stroke="#f3d58f" stroke-width=".5" stroke-opacity=".8"/>' for y in (44, 58, 72))}
  <!-- the lift's two hoist cables running down the gutter, out of the guard and down to the landing -->
  <path d="M{GX + 7.2:.1f} 76 V612 M{GX + 10.8:.1f} 76 V612" stroke="#2a1d1a" stroke-width="1.1" stroke-opacity=".85"/>
  <path d="M{GX + 6.9:.1f} 76 V612 M{GX + 10.5:.1f} 76 V612" stroke="#c9a26a" stroke-width=".3" stroke-opacity=".55" stroke-dasharray="1.2 1.4"/>
</svg>
'''

OVERLAY_SVG = f'''
<svg class="blk" style="left:0; top:0; width:864pt; height:648pt; z-index:4; pointer-events:none" viewBox="0 0 864 648" aria-hidden="true">
  <!-- P003-1: the controller's position strip, exact insert: +2 to -8, equal spacing, true minus signs -->
  <rect x="{SX0:.2f}" y="{SY0:.2f}" width="{SX1 - SX0:.2f}" height="{SY1 - SY0:.2f}" fill="#f1e6cc" stroke="#7a5326" stroke-width=".4"/>
  <rect x="{SX0:.2f}" y="{SY0:.2f}" width="1.2" height="{SY1 - SY0:.2f}" fill="#d9c7a0"/>
  <g font-family="Source Sans 3" font-weight="600" font-size="6.6" fill="#2a1d10">{''.join(strip_marks)}</g>
  <!-- P003-2: the -8 landing plate -->
  <text x="{(PL[0] + PR[0]) / 2:.2f}" y="{(PL[1] + PR[1]) / 2 + 3.6:.2f}" text-anchor="middle" font-family="Source Sans 3" font-weight="600" font-size="10.5" fill="#2a1d10" fill-opacity=".92">−8</text>
  <text x="{(PL[0] + PR[0]) / 2 + .4:.2f}" y="{(PL[1] + PR[1]) / 2 + 4.1:.2f}" text-anchor="middle" font-family="Source Sans 3" font-weight="600" font-size="10.5" fill="#f6dca0" fill-opacity=".35">−8</text>
</svg>
'''

CSS = '''
  /* P003 "The Shaft": story recto. Aubergine field warming to store-lamp umber at the foot. */
  .page.shaft { background: linear-gradient(to bottom, #3a2f48 0%, #46364F 46%, #4f3a3a 72%, #5a3c26 100%);
                color: #1d2433; font-family: "Source Sans 3", sans-serif; font-size: 14pt; line-height: 18pt; }
  .shaft .blk { position: absolute; }
  .pnl { position: absolute; overflow: hidden; background: #0c1020; box-shadow: 0 2.5pt 7pt rgba(16, 8, 20, .55); z-index: 1; }
  .pnl img { position: absolute; display: block; max-width: none; }
  .pnl::after { content: ""; position: absolute; inset: 0; border: 1pt solid #b3722f;
                box-shadow: inset 0 0 0 .5pt #120c18, inset 0 0 10pt rgba(12, 6, 18, .35); pointer-events: none; }
  /* the store lamp's warmth rising at the foot of the shaft */
  .pnl.shaftp::before { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 120pt; z-index: 1;
                        background: linear-gradient(to top, rgba(247, 198, 132, .16), rgba(247, 198, 132, 0)); pointer-events: none; }
  .cap { position: absolute; background: #F7F1E3; border: .6pt solid #b3722f; padding: 5pt 8pt; box-sizing: border-box;
         font-family: "Source Serif 4", serif; font-weight: 400; font-size: 14pt; line-height: 18pt; color: #1d2433;
         box-shadow: 0 1.5pt 4pt rgba(16, 8, 20, .45); z-index: 5; }
  .notch { position: absolute; z-index: 5; overflow: visible; }
  .bal { position: absolute; background: #FFFDF6; border: .8pt solid #1d2433; display: flex; align-items: center;
         justify-content: center; text-align: center; box-sizing: border-box; z-index: 5;
         font-family: "Source Sans 3", sans-serif; font-weight: 600; font-size: 14pt; line-height: 18pt; color: #1d2433; }
  .bal span { display: block; }
  .tails { position: absolute; left: 0; top: 0; width: 864pt; height: 648pt; overflow: visible; pointer-events: none; z-index: 6; }
  .rh { font-family: "Source Sans 3", sans-serif; font-weight: 600; font-size: 10pt; line-height: 12pt; letter-spacing: 1.6pt;
        font-variant-caps: all-small-caps; color: #d9b46a; white-space: nowrap; }
  .fol { font-family: "Source Sans 3", sans-serif; font-weight: 600; font-size: 11pt; line-height: 13pt; color: #F7F1E3; letter-spacing: .4pt; }
'''

def panel_html(p, extra=""):
    img_w = p["iw"] * p["s"]; img_h = p["ih"] * p["s"]
    return (f'<div class="pnl{extra}" style="left:{p["x"]}pt; top:{p["y"]}pt; width:{p["w"]}pt; height:{p["h"]}pt">'
            f'<img src="assets/img/{p["id"]}.jpg" alt="" style="left:{p["ox"]:.2f}pt; top:{p["oy"]:.2f}pt; width:{img_w:.2f}pt; height:{img_h:.2f}pt"></div>')

def balloon(b, html):
    return (f'<div class="bal" style="left:{b["x"]:.1f}pt; top:{b["y"]}pt; width:{b["w"]:.1f}pt; height:{b["h"]}pt; '
            f'border-radius:{b.get("r", b["h"]/2):.1f}pt">{html}</div>')

# caption notch: the caption paper's tongue reaching down into P003-1 (over its dark top-left canopy)
NX = CAP1["x"] + 22
NOTCH = (f'<svg class="notch" style="left:0; top:0; width:864pt; height:648pt" viewBox="0 0 864 648" aria-hidden="true">'
         f'<path d="M{NX} 83.4 L{NX + 9} 99 L{NX + 18} 83.4" fill="#F7F1E3" stroke="#b3722f" stroke-width=".6" stroke-linejoin="round"/>'
         f'<path d="M{NX + .8} 83.2 H{NX + 17.2}" stroke="#F7F1E3" stroke-width="1.6"/></svg>')

BODY = f'''
{BORDER}

<!-- ========== panels ========== -->
{panel_html(P["P003-1"])}
{panel_html(P["P003-2"], " shaftp")}
{panel_html(P["P003-3"])}
{panel_html(P["P003-4"])}
{SHAFT_SVG}
{OVERLAY_SVG}

<!-- ========== 1: caption on P003-1's dark gate canopy ========== -->
<div class="cap" style="left:{CAP1["x"]}pt; top:{CAP1["y"]}pt; width:{CAP1["w"]}pt">The knock comes again. This time they can hear where it comes from. There’s a lift in the left wall. Tara turns up a fixed lamp beside it.</div>

<!-- ========== 2: the shaft caption in the dark upper shaft ========== -->
<div class="cap" style="left:{SHX0 + 9:.1f}pt; top:{SHY0 + 12}pt; width:{158}pt">Far below, the wooden helper in the blue waistcoat stands beside its cart of supplies. It is tapping a metal box to attract attention.</div>

<!-- ========== 3 / 4: Tara's balloons on the art above her head, tails to her mouth ========== -->
{balloon(B3, '<span style="padding:0 13pt">That helper took the supplies down before the trouble began.</span>')}
{balloon(B4, '<span style="padding:0 9pt">Someone sent the empty lift back up and changed the return instructions. The helper’s still down there with the supplies.</span>')}
<svg class="tails" viewBox="0 0 864 648" aria-hidden="true">
  {tail(*B3base, B3tip, bend=3)}
  {tail(*B4base, B4tip, bend=3)}
</svg>
'''

HTML = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>ChandRush CH01 P003</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="assets/base.css">
<link rel="stylesheet" href="assets/kit.css">
<style>{CSS}</style>
</head>
<body>
<div class="page shaft" id="page" data-chapter="CH01" data-page="P003">
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
    for k, v in dict(mouth3=mouth3, B3tip=B3tip, mouth4=mouth4, B4tip=B4tip, strip0=(SX0, SY0), strip1=(SX1, SY1), plate=(PL, PR)).items():
        print(" ", k, v)
