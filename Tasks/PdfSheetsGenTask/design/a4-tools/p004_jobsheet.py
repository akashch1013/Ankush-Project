# P004 "The Job Sheet" (2026-11-25): writes CH01/P004/index.html (verso facing P005).
# Book system copied from P005: 864x648 pt, 36 pt margins, 12 columns (49.5 pt) with 18 pt gutters, 18 pt baseline,
# running head at the outer (left) edge, moonclock folio bottom centre, brass hairline frame 14 pt inside the trim.
# Idea: the page is the controller. Column 0 is the exact position strip (+2 ... -8) running the full height of the
# page like the lift shaft: street level (0) sits beside the street scene, the store (-8) sits level with
# Vihaan's fingertip in P004-2. The painted strips in the art stay unlabelled (P004-2 has only 10 painted ticks).
import sys
sys.path.insert(0, "/home/akasdh/Desktop/Projects/ComicAgent/Tasks/PdfSheetsGenTask/design/a4-tools")
from common import sync_assets, TAIL, bln

T = "/home/akasdh/Desktop/Projects/ComicAgent/Tasks/"
PD = T + "PdfSheetsGenTask/CH01/P004"
OUT = PD + "/index.html"

M, COLW, GUT = 36, 49.5, 18
def colx(i): return M + i * (COLW + GUT)
def colr(i): return colx(i) + COLW          # right edge of column i

A_T, A_B = 36, 346          # row A: establishing panel, both captions on its arch band
B_T, B_B = 356, 612         # row B: P2 (left, full height) | P3 over P4 (right)
G = 10                      # panel gutter (user 2026-11-25: tight gutters, text on the art)
PX0, PX1 = colr(0) + G, 864 - M      # panel area 95.5 .. 828

# ---------- panels: (x, y, w, h, img w, img h, img left, img top) ----------
P1 = dict(x=PX0, y=A_T, w=PX1 - PX0, h=A_B - A_T)
P1.update(iw=P1["w"], ih=P1["w"] * 1024 / 1536, il=0)
P1["it"] = -0.077 * P1["ih"]          # window ~.06-.74: Tara's head to Tez the cub (lower left) stays in frame
W2 = 330
P2 = dict(x=PX0, y=B_T, w=W2, h=B_B - B_T, iw=W2, ih=W2, il=0, it=0)
RX = PX0 + W2 + G
RH = (B_B - B_T - G) / 2
P3 = dict(x=RX, y=B_T, w=PX1 - RX, h=RH)
P3.update(iw=P3["w"], ih=P3["w"] * 1536 / 1075, il=0)
P3["it"] = -0.12 * P3["ih"]
P4 = dict(x=RX, y=B_T + RH + G, w=PX1 - RX, h=RH)
P4.update(iw=P4["w"], ih=P4["w"] * 1536 / 1024, il=0)
P4["it"] = -0.25 * P4["ih"]

def img_pt(P, fx, fy):
    """image fraction -> page point"""
    return P["x"] + P["il"] + fx * P["iw"], P["y"] + P["it"] + fy * P["ih"]

FINGER = img_pt(P2, 0.222, 0.588)      # Vihaan's fingertip on the painted strip (QC'd from the pixels)
V_MOUTH = img_pt(P2, 0.523, 0.557)
T_MOUTH = img_pt(P3, 0.637, 0.207)
A_MOUTH = img_pt(P4, 0.493, 0.400)

# ---------- the strip insert (column 0) ----------
SX0, SX1 = colx(0), colr(0)            # 36 .. 85.5
Y_TOP, Y_BOT = 62.0, round(FINGER[1], 1)   # +2 and -8 marks; -8 is level with the fingertip
STEP = (Y_BOT - Y_TOP) / 10
VALS = [2, 1, 0, -1, -2, -3, -4, -5, -6, -7, -8]
def my(v): return Y_TOP + (2 - v) * STEP
FACE_L, FACE_R = SX0 + 6, SX1 - 6
TICK_L = FACE_R - 10
def lab(v): return ("+" + str(v)) if v > 0 else ("−" + str(-v)) if v < 0 else "0"

marks = []
for v in VALS:
    y = my(v)
    sw = 1.2 if v == 0 else .9
    marks.append(f'<path d="M{TICK_L - (4 if v == 0 else 0)} {y:.2f} H{FACE_R}" stroke="#2a2418" stroke-width="{sw}"/>')
    fs, fw = (17, 700) if v == 0 else (14, 600)
    marks.append(f'<text x="{TICK_L - 4 - (4 if v == 0 else 0)}" y="{y + fs * .34:.2f}" text-anchor="end" font-size="{fs}" font-weight="{fw}">{lab(v)}</text>')

def tail(x1, x2, by, tx, ty, bend=0.0):
    """P107-style curved tail: base x1..x2 on the balloon edge at y=by, tip at (tx,ty)"""
    mx = (x1 + x2) / 2
    c1 = (x1 + (tx - x1) * .35 + bend, by + (ty - by) * .55)
    c2 = (x2 + (tx - x2) * .35 + bend, by + (ty - by) * .55)
    return (f'<path d="M{x1:.1f} {by:.1f} Q{c1[0]:.1f} {c1[1]:.1f} {tx:.1f} {ty:.1f} Q{c2[0]:.1f} {c2[1]:.1f} {x2:.1f} {by:.1f}" '
            f'fill="#FFFDF6" stroke="#1d2433" stroke-width=".8" stroke-linejoin="round"/>'
            f'<path d="M{x1 + .6:.1f} {by - 1.1:.1f} L{x2 - .6:.1f} {by - 1.1:.1f}" stroke="#FFFDF6" stroke-width="2.4"/>')

def pnl(P, src, extra=""):
    return (f'<div class="pnl{extra}" style="left:{P["x"]:.2f}pt; top:{P["y"]:.2f}pt; width:{P["w"]:.2f}pt; height:{P["h"]:.2f}pt">'
            f'<img src="assets/img/{src}.jpg" alt="" style="left:{P["il"]:.2f}pt; top:{P["it"]:.2f}pt; width:{P["iw"]:.2f}pt; height:{P["ih"]:.2f}pt"></div>')

def stail(bx, y1, y2, tx, ty, bend=0.0):
    """curved tail whose base sits on a vertical balloon edge x=bx (y1..y2), tip at (tx,ty)"""
    c1 = (bx + (tx - bx) * .55, y1 + (ty - y1) * .35 + bend)
    c2 = (bx + (tx - bx) * .55, y2 + (ty - y2) * .35 + bend)
    return (f'<path d="M{bx:.1f} {y1:.1f} Q{c1[0]:.1f} {c1[1]:.1f} {tx:.1f} {ty:.1f} Q{c2[0]:.1f} {c2[1]:.1f} {bx:.1f} {y2:.1f}" '
            f'fill="#FFFDF6" stroke="#1d2433" stroke-width=".8" stroke-linejoin="round"/>'
            f'<path d="M{bx - 1.1:.1f} {y1 + .6:.1f} L{bx - 1.1:.1f} {y2 - .6:.1f}" stroke="#FFFDF6" stroke-width="2.4"/>')

# balloons (x, y, w, h), all ON the art, on calm parts (QC-NOTES-P002-P004), never over a face
BV = dict(x=P2["x"] + 0.035 * W2, y=P2["y"] + 0.44 * P2["ih"], w=0.425 * W2, h=44)     # over the box face + Tara's palm, left of Vihaan
BY = dict(x=P3["x"] + 8, y=P3["y"] + 6, w=54, h=26)                     # box top, left of Tara
BT = dict(x=P3["x"] + 8, y=P3["y"] + 37, w=0.52 * P3["w"], h=68)
BA = dict(x=P4["x"] + 6, y=P4["y"] + 8, w=0.37 * P4["w"], h=88)                   # over the box top / strip head, left of Ahana
def bal(B, text, cls="", pad=10):
    r = min(B["h"] / 2, 31)
    rad = "50%" if "ov" in cls else f"{r:.1f}pt"
    return (f'<div class="bal{cls}" style="left:{B["x"]:.2f}pt; top:{B["y"]:.2f}pt; width:{B["w"]:.2f}pt; height:{B["h"]:.2f}pt; border-radius:{rad}">'
            f'<span style="padding:0 {pad}pt">{text}</span></div>')

BALLOONS = bln([   # reading order; one outline per balloon + tail, "Yes." linked to Tara's next balloon
    dict(text="Eight marks below the street.", at=[BV["x"], BV["y"]], w=BV["w"], h=BV["h"], maxw=BV["w"] - 20,
         tip=(V_MOUTH[0] - 6, V_MOUTH[1] + 1)),
    dict(text="Yes.", at=[BY["x"], BY["y"] - 2]),
    dict(text="The numbers tell us where the lift is compared with this landing.", at=[BT["x"] + 14, BT["y"] + 10], w=BT["w"], h=BT["h"],
         maxw=BT["w"] - 24, shape="round", radius=26, link=1, tip=(T_MOUTH[0] - 9, T_MOUTH[1] + 1)),
    dict(text="How can we choose movements that will reach the store?", at=[BA["x"], BA["y"]], w=BA["w"], h=BA["h"],
         maxw=BA["w"] - 24, shape="round", radius=28, tip=(A_MOUTH[0] - 12, A_MOUTH[1] - 1)),
])

tails = [
    stail(BV["x"] + BV["w"] - 3, BV["y"] + 20, BV["y"] + 32, V_MOUTH[0] - 6, V_MOUTH[1] + 1),
    stail(BT["x"] + BT["w"], BT["y"] + 8, BT["y"] + 22, T_MOUTH[0] - 9, T_MOUTH[1] + 1),
    stail(BA["x"] + BA["w"], BA["y"] + 52, BA["y"] + 66, A_MOUTH[0] - 12, A_MOUTH[1] - 1),
]
# the neck that links "Yes." to Tara's second balloon (one speaking beat)
neck = (f'<path d="M{BY["x"] + 22} {BY["y"] + 27} C{BY["x"] + 23} {BY["y"] + 31} {BY["x"] + 23} {BT["y"] + 1} {BY["x"] + 21} {BT["y"] + 4} '
        f'L{BY["x"] + 33} {BT["y"] + 4} C{BY["x"] + 31} {BT["y"] + 1} {BY["x"] + 31} {BY["y"] + 31} {BY["x"] + 32} {BY["y"] + 27} Z" '
        f'fill="#FFFDF6" stroke="#1d2433" stroke-width=".8" stroke-linejoin="round"/>'
        f'<path d="M{BY["x"] + 22.6} {BY["y"] + 25.6} H{BY["x"] + 31.4} M{BY["x"] + 21.8} {BT["y"] + 2.6} H{BY["x"] + 32.2}" stroke="#FFFDF6" stroke-width="2.6"/>')

C1 = dict(x=P1["x"] + 6, y=P1["y"] + 4, w=0.40 * P1["w"])
C2 = dict(x=P1["x"] + 0.505 * P1["w"], y=P1["y"] + 4, w=0.275 * P1["w"])
CLIP_X, CLIP_Y = C1["x"] + 22, P1["y"] + 2       # brass clip pins the job sheet to the panel's top edge

style = f"""
  /* P004 "The Job Sheet": royal-blue controller lacquer, brass, cream enamel (previews P005's light field).
     Grid as P005: 36 pt margins, 12 x 49.5 pt columns, 18 pt gutters, 18 pt baseline. */
  .page.jobsheet {{ background:
        radial-gradient(ellipse 70% 62% at 52% 44%, #2c5cab 0%, #24509a 45%, #1c3f7c 78%, #16336a 100%);
        color: #1d2433; font-family: "Source Sans 3", sans-serif; font-size: 14pt; line-height: 18pt; }}
  .jobsheet .blk {{ position: absolute; }}
  .pnl {{ position: absolute; overflow: hidden; background: #0c1933; box-shadow: 0 2.5pt 7pt rgba(6, 14, 34, .55); }}
  .pnl img {{ position: absolute; display: block; max-width: none; }}
  .pnl::after {{ content: ""; position: absolute; inset: 0; border: 1pt solid #b3722f;
                box-shadow: inset 0 0 0 .5pt #0c1933, inset 0 0 10pt rgba(6, 14, 34, .35); pointer-events: none; }}
  .cap {{ background: #F7F1E3; border: .6pt solid #b3722f; padding: 5pt 9pt 6pt; box-sizing: border-box;
         font-family: "Source Serif 4", serif; font-weight: 400; font-size: 14pt; line-height: 18pt; color: #1d2433;
         box-shadow: 0 1.5pt 4pt rgba(6, 14, 34, .45); }}
  .cap.abs {{ position: absolute; }}
  .jobcol {{ display: flex; flex-direction: column; justify-content: flex-start; gap: 12pt; }}
  .jobcol .cap {{ position: static; width: auto; flex: 0 0 auto; padding: 8pt 10pt 9pt; }}
  .bal {{ position: absolute; background: #FFFDF6; border: .8pt solid #1d2433; display: flex; align-items: center;
         justify-content: center; text-align: center; box-sizing: border-box; z-index: 5;
         font-family: "Source Sans 3", sans-serif; font-weight: 600; font-size: 14pt; line-height: 18pt; color: #1d2433; }}
  .bal span {{ display: block; }}
  .nw {{ white-space: nowrap; }}
  i.m {{ white-space: nowrap; font-style: normal; }}
  .tails {{ position: absolute; left: 0; top: 0; width: 864pt; height: 648pt; overflow: visible; pointer-events: none; z-index: 4; }}
  .rh {{ font-family: "Source Sans 3", sans-serif; font-weight: 600; font-size: 10pt; line-height: 12pt; letter-spacing: 1.6pt;
        font-variant-caps: all-small-caps; color: #e2c486; white-space: nowrap; }}
  .fol {{ font-family: "Source Sans 3", sans-serif; font-weight: 600; font-size: 11pt; line-height: 13pt; color: #F7F1E3; letter-spacing: .4pt; }}
"""

body = f"""<div class="page jobsheet" id="page" data-chapter="CH01" data-page="P004">

<!-- ========== field + frame: lacquer sheen, brass hairline 14 pt inside the trim (as P005), card-rail entry, ruby finish ========== -->
<svg class="blk" style="left:0; top:0; width:864pt; height:648pt; z-index:0" viewBox="0 0 864 648" aria-hidden="true">
  <defs>
    <linearGradient id="bV" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f3d58f"/><stop offset=".35" stop-color="#d6a64e"/><stop offset=".7" stop-color="#b3722f"/><stop offset="1" stop-color="#6e4318"/></linearGradient>
    <linearGradient id="bH" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#6e4318"/><stop offset=".18" stop-color="#b3722f"/><stop offset=".42" stop-color="#f3d58f"/><stop offset=".62" stop-color="#d6a64e"/><stop offset="1" stop-color="#7a4a18"/></linearGradient>
    <radialGradient id="fMoon" cx=".38" cy=".35" r=".7"><stop offset="0" stop-color="#fff6da"/><stop offset=".6" stop-color="#f1d79a"/><stop offset="1" stop-color="#c99a4c"/></radialGradient>
    <radialGradient id="ruby" cx=".36" cy=".32" r=".75"><stop offset="0" stop-color="#e0685a"/><stop offset=".45" stop-color="#a8291f"/><stop offset="1" stop-color="#5e1210"/></radialGradient>
    <filter id="soft" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="1.4"/></filter>
  </defs>
  <!-- lacquer sheen: one faint diagonal highlight, darker toward the foot (the shaft goes down) -->
  <path d="M0 0 H330 L0 300 Z" fill="#4a78c4" fill-opacity=".10"/>
  <path d="M864 648 H560 L864 380 Z" fill="#0c1f48" fill-opacity=".22"/>
  <!-- gold pinstripe frame, broken at the card rail (entry), the folio and the ruby plate (finish) -->
  <path d="M410 634 H14 V14 H232 M566 14 H850 V634 H836 M790 634 H454" fill="none" stroke="#c9a24a" stroke-width=".75"/>
  <path d="M410 631.6 H16.4 V16.4 H232 M566 16.4 H847.6 V631.6 H836 M790 631.6 H454" fill="none" stroke="#c9a24a" stroke-width=".3" stroke-opacity=".5"/>
  <g fill="#c9a24a"><circle cx="14" cy="14" r="2.1"/><circle cx="850" cy="14" r="2.1"/><circle cx="14" cy="634" r="2.1"/></g>
  <g fill="#f3d58f"><circle cx="13.4" cy="13.4" r=".7"/><circle cx="849.4" cy="13.4" r=".7"/><circle cx="13.4" cy="633.4" r=".7"/></g>

  <!-- entry: the movement-card rail, one continuous brass channel with a dark groove (no slots, no cards) -->
  <rect x="232" y="11" width="334" height="7" rx="3.5" fill="#0a1630" fill-opacity=".45" transform="translate(0 1.4)" filter="url(#soft)"/>
  <rect x="232" y="11" width="334" height="7" rx="3.5" fill="url(#bV)" stroke="#5a3510" stroke-width=".5"/>
  <path d="M236 14.5 H562" stroke="#3a2208" stroke-width="1"/>
  <path d="M236 12.2 H562" stroke="#fff0c4" stroke-width=".4" stroke-opacity=".7"/>
  <circle cx="232" cy="14.5" r="4.2" fill="#d6a64e" stroke="#5a3510" stroke-width=".5"/><circle cx="231" cy="13.4" r="1.2" fill="#fff0c4"/>
  <circle cx="566" cy="14.5" r="4.2" fill="#b3722f" stroke="#5a3510" stroke-width=".5"/><circle cx="565" cy="13.4" r="1.1" fill="#f3d58f"/>

  <!-- finish: two dim ruby warning lamps in brass bezels on a short brass plate -->
  <rect x="790" y="627" width="46" height="14" rx="3" fill="#0a1630" fill-opacity=".45" transform="translate(0 1.4)" filter="url(#soft)"/>
  <rect x="790" y="627" width="46" height="14" rx="3" fill="#b3722f" stroke="#5a3510" stroke-width=".5"/>
  <path d="M792 628.4 H834" stroke="#f3d58f" stroke-width=".5" stroke-opacity=".8"/>
  <circle cx="804" cy="634" r="5" fill="#8a5a22" stroke="#5a3510" stroke-width=".5"/><circle cx="804" cy="634" r="3.9" fill="url(#ruby)"/><circle cx="802.8" cy="632.7" r="1" fill="#f3a093"/>
  <circle cx="822" cy="634" r="5" fill="#8a5a22" stroke="#5a3510" stroke-width=".5"/><circle cx="822" cy="634" r="3.9" fill="url(#ruby)"/><circle cx="820.8" cy="632.7" r="1" fill="#f3a093"/>

  <!-- moonclock folio: lit fraction 4/107 (waxing, lit on the right), brass ring, as P005 -->
  <circle cx="424" cy="630" r="8" fill="#0c1933" stroke="#c9a24a" stroke-width=".9"/>
  <circle cx="424" cy="630" r="5.4" fill="#22345a"/>
  <path d="M424 624.6 A5.4 5.4 0 0 1 424 635.4 A{5.4 * (1 - 2 * 4 / 107):.3f} 5.4 0 0 0 424 624.6 Z" fill="url(#fMoon)"/>
</svg>
<div class="blk fol" style="left:436pt; top:623.5pt">4</div>

<!-- running head at the verso's outer (left) edge -->
<div class="blk rh" style="left:{M}pt; top:19pt">CHAPTER 01 · NUMBERS · PG 004</div>

<!-- ========== HERO: the position strip, exact (+2 ... −8, equal spacing), full height like the shaft ========== -->
<svg class="blk" data-figure="position strip +2 to −8, equal intervals, 0 = street, −8 = store" style="left:0; top:0; width:864pt; height:648pt; z-index:3"
     viewBox="0 0 864 648" aria-label="Position strip from +2 down to −8">
  <defs>
    <linearGradient id="chan" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#6e4318"/><stop offset=".12" stop-color="#b3722f"/><stop offset=".3" stop-color="#f3d58f"/>
      <stop offset=".5" stop-color="#d6a64e"/><stop offset=".85" stop-color="#9a6526"/><stop offset="1" stop-color="#5a3510"/></linearGradient>
    <linearGradient id="enam" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#e6dcc4"/><stop offset=".2" stop-color="#F7F1E3"/><stop offset=".75" stop-color="#f3ebdc"/><stop offset="1" stop-color="#ddd0b3"/></linearGradient>
    <linearGradient id="cap" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f3d58f"/><stop offset=".35" stop-color="#d6a64e"/><stop offset=".7" stop-color="#b3722f"/><stop offset="1" stop-color="#6e4318"/></linearGradient>
    <radialGradient id="lampg" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#f7c684" stop-opacity=".95"/><stop offset=".4" stop-color="#f7c684" stop-opacity=".35"/><stop offset="1" stop-color="#f7c684" stop-opacity="0"/></radialGradient>
    <filter id="ss" x="-40%" y="-5%" width="180%" height="110%"><feGaussianBlur stdDeviation="2"/></filter>
  </defs>
  <!-- shadow, brass channel, enamel face -->
  <rect x="{SX0 + 2}" y="{A_T + 3}" width="{SX1 - SX0}" height="{B_B - A_T}" rx="5" fill="#06102a" fill-opacity=".5" filter="url(#ss)"/>
  <rect x="{SX0}" y="{A_T}" width="{SX1 - SX0}" height="{B_B - A_T}" rx="5" fill="url(#chan)" stroke="#5a3510" stroke-width="1"/>
  <rect x="{FACE_L}" y="{A_T + 12}" width="{FACE_R - FACE_L}" height="{Y_BOT - A_T + 4}" rx="2" fill="url(#enam)" stroke="#5a3510" stroke-width=".6"/>
  <path d="M{FACE_L + 1.2} {A_T + 13} V{Y_BOT + 15}" stroke="#ffffff" stroke-width="1" stroke-opacity=".7"/>
  <!-- top collar + finial (P005's thermometer collar, turned upright) -->
  <rect x="{SX0 + 4}" y="{A_T + 2}" width="{SX1 - SX0 - 8}" height="8" rx="2" fill="url(#cap)" stroke="#5a3510" stroke-width=".5"/>
  <!-- foot: brass plinth below the store mark, two slotted screws -->
  <rect x="{SX0 + 4}" y="{Y_BOT + 22}" width="{SX1 - SX0 - 8}" height="{B_B - Y_BOT - 28}" rx="2" fill="url(#cap)" stroke="#5a3510" stroke-width=".5"/>
  <g>
    <circle cx="{(SX0 + SX1) / 2}" cy="{(Y_BOT + 22 + B_B - 6) / 2:.1f}" r="3.2" fill="#8a5a22" stroke="#5a3510" stroke-width=".5"/><path d="M{(SX0 + SX1) / 2 - 2.2} {(Y_BOT + 22 + B_B - 6) / 2:.1f} h4.4" stroke="#3a2208" stroke-width=".8"/>
  </g>
  <!-- street level: a silver moonline across the face at 0 (P005's zero mark), then a brass hairline into the street panel -->
  <path d="M{FACE_L} {my(0):.2f} H{FACE_R}" stroke="#7f93ad" stroke-width="1.6" stroke-opacity=".55"/>
  <path d="M{FACE_R} {my(0):.2f} H{P1['x']}" stroke="#d6a64e" stroke-width="1"/>
  <circle cx="{P1['x'] - 2}" cy="{my(0):.2f}" r="1.6" fill="#d6a64e"/>
  <!-- the store: a lamp-gold glint on the −8 tick and a brass hairline to the edge of Vihaan's panel, level with his fingertip -->
  <path d="M{FACE_R} {Y_BOT:.2f} H{P2['x']}" stroke="#d6a64e" stroke-width="1"/>
  <circle cx="{FACE_R - 1}" cy="{Y_BOT:.2f}" r="9" fill="url(#lampg)"/>
  <circle cx="{FACE_R - 1}" cy="{Y_BOT:.2f}" r="2.5" fill="#f7c684" stroke="#9a6526" stroke-width=".4"/>
  <g>{''.join(marks)}</g>
</svg>
<style>.jobsheet svg text {{ font-family: "Source Sans 3", sans-serif; fill: #1d2433; }}</style>

<!-- ========== row A: the crew sees the whole job ========== -->
{pnl(P1, "P004-1")}
<!-- both captions ON the art: cream job-sheet plates over the gate arch / wall-lamp band, above every head -->
<div class="cap abs" style="left:{C1['x']:.2f}pt; top:{C1['y']:.2f}pt; width:{C1['w']:.2f}pt; z-index:2">A small lift car stands behind a brass safety gate at street level. Next to it is a control box with a row of slots. Numbered cards fit into those slots. Each card tells the lift how far to move and in which direction.</div>
<div class="cap abs" style="left:{C2['x']:.2f}pt; top:{C2['y']:.2f}pt; width:{C2['w']:.2f}pt; z-index:2">The children can now see their first job. They must send the empty car down to the helper, let it load the supplies and bring it back.</div>


<!-- ========== row B: reading the position strip ========== -->
{pnl(P2, "P004-2")}
{pnl(P3, "P004-3")}
{pnl(P4, "P004-4")}

<!-- P004-2: caption → Vihaan → caption, all ON the art (box face, left of Vihaan; jacket at the foot) -->
<div class="cap abs" style="left:{P2['x'] + 5}pt; top:{B_T + 5}pt; width:{0.565 * W2 - 5:.2f}pt; z-index:2; padding:4pt 8pt 5pt">Beside the shaft, a numbered strip shows the lift’s position. Street level is marked 0. Positive numbers are above it. Negative numbers are below. The store is at −8.</div>
<div class="cap abs" style="left:{P2['x'] + 0.43 * W2:.2f}pt; bottom:{648 - B_B + 5}pt; width:{0.57 * W2 - 5:.2f}pt; z-index:2; padding:4pt 8pt 5pt">Vihaan follows the strip with his finger.</div>

<!-- P004-3: Tara, one speaking beat in two linked balloons -->

<!-- P004-4: Ahana's question -->
{BALLOONS}

"""

head = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>ChandRush CH01 P004</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="assets/base.css">
<link rel="stylesheet" href="assets/kit.css">
<style>{style}</style>
</head>
<body>
"""
sync_assets(PD)
open(OUT, "w", encoding="utf-8").write(head + body + TAIL)
print("wrote", OUT)
print("finger", FINGER, "-8 at", Y_BOT, "step", round(STEP, 2), "0 at", round(my(0), 1))
print("mouths V", V_MOUTH, "T", T_MOUTH, "A", A_MOUTH)
