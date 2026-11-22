#!/usr/bin/env python3
"""kitgen.py: build kit.css, the ChandRush creative kit (Art Direction A1, see ART-DIRECTION.md).

    python3 PdfSheetsGenTask/design/kitgen.py      -> writes PdfSheetsGenTask/design/kit.css

Every motif is a small SVG drawn here and embedded as a data URI, so pages stay self-contained and the artifact
needs no extra files. Edit motifs and colours HERE, never kit.css by hand. After a change, re-render the gallery:
    python3 pipeline/render_pdf.py PdfSheetsGenTask/design/kit-gallery-1.html /tmp/k1.pdf --png PdfSheetsGenTask/design/kit-1.png
All motifs are wordless: no letters or numbers are ever drawn by the kit (book rule: printed words come only from
the manuscript).
"""
import math
import os
import random
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))

# The Midnight Mela palette (ART-DIRECTION.md section 3)
P = dict(night="#0e1838", indigo="#1d2f6b", indigo2="#2b4590", gold="#f2b441", marigold="#f28c28",
         yellow="#f7c531", rani="#d63f7a", peacock="#12807f", parrot="#6aa84f", kite="#e0483b",
         sky="#8fc7e8", cream="#fff7e6", paper="#fbf1dc", ink="#1c2340", brass="#c9962e", mint="#e6f4ef")

NS = "xmlns='http://www.w3.org/2000/svg'"


def uri(svg):
    svg = " ".join(svg.split())
    return 'url("data:image/svg+xml,' + urllib.parse.quote(svg, safe=" =:/,;'()-.") + '")'


def svg(vb, body):
    return f"<svg {NS} viewBox='{vb}'>{body}</svg>"


# ------------------------------------------------------------------ garlands and edges
def toran(colors, string=P["brass"]):
    """bunting swag: 5 flags with a shisha (mirror) dot on each"""
    b = f"<path d='M0 4 Q60 18 120 4' fill='none' stroke='{string}' stroke-width='1.3'/>"
    y = lambda x: 4 + 28 * (x / 120) * (1 - x / 120)
    for x, c in zip([12, 36, 60, 84, 108], colors):
        b += (f"<path d='M{x-9} {y(x-9):.1f} L{x+9} {y(x+9):.1f} L{x} {y(x)+25:.1f} Z' fill='{c}'/>"
              f"<circle cx='{x}' cy='{y(x)+8:.1f}' r='2.3' fill='{P['cream']}' stroke='{P['gold']}' stroke-width='.7'/>")
    return svg("0 0 120 44", b)


def marigolds():
    b = f"<path d='M0 2 Q50 22 100 2' fill='none' stroke='#5a7d2c' stroke-width='1.1'/>"
    for i in range(10):
        x = 5 + i * 10
        t = x / 100
        y = 2 + 40 * t * (1 - t)
        c, d = (P["marigold"], "#c85a0c") if i % 2 else (P["yellow"], "#e0880f")
        b += (f"<circle cx='{x}' cy='{y:.1f}' r='5.2' fill='{c}' stroke='{d}' stroke-width='1.8' stroke-dasharray='1.3 .9'/>"
              f"<circle cx='{x}' cy='{y:.1f}' r='1.8' fill='{d}'/>")
    b += f"<ellipse cx='50' cy='19' rx='2.2' ry='5' fill='{P['parrot']}' transform='rotate(20 50 19)'/>"
    return svg("0 0 100 34", b)


def lanterns():
    b = (f"<defs><radialGradient id='g'><stop offset='0' stop-color='{P['gold']}' stop-opacity='.55'/>"
         f"<stop offset='1' stop-color='{P['gold']}' stop-opacity='0'/></radialGradient></defs>"
         f"<path d='M0 6 Q70 22 140 6' fill='none' stroke='{P['brass']}' stroke-width='1.2'/>")
    for x, c in ((35, P["marigold"]), (105, P["rani"])):
        b += (f"<circle cx='{x}' cy='36' r='26' fill='url(#g)'/>"
              f"<line x1='{x}' y1='12' x2='{x}' y2='21' stroke='{P['brass']}' stroke-width='1'/>"
              f"<rect x='{x-5}' y='20' width='10' height='3' rx='1' fill='{P['gold']}'/>"
              f"<ellipse cx='{x}' cy='36' rx='10' ry='13' fill='{c}'/>"
              f"<path d='M{x-5} 24 Q{x-9} 36 {x-5} 48 M{x} 23 V49 M{x+5} 24 Q{x+9} 36 {x+5} 48' fill='none' stroke='#00000033' stroke-width='1'/>"
              f"<ellipse cx='{x-3}' cy='31' rx='3' ry='5' fill='#ffffff44'/>"
              f"<rect x='{x-5}' y='48' width='10' height='3' rx='1' fill='{P['gold']}'/>"
              f"<path d='M{x} 51 V60' stroke='{c}' stroke-width='2'/>")
    return svg("0 0 140 66", b)


def fairy_lights():
    b = f"<path d='M0 8 Q20 18 40 8 T80 8' fill='none' stroke='#22305a' stroke-width='1'/>"
    for x, y, c in ((20, 13, P["gold"]), (60, 13, P["rani"]), (40, 8, P["sky"]), (0, 8, P["parrot"]), (80, 8, P["parrot"])):
        b += (f"<circle cx='{x}' cy='{y+5}' r='6' fill='{c}' opacity='.30'/>"
              f"<rect x='{x-1.6}' y='{y}' width='3.2' height='2.4' fill='#3a3a3a'/>"
              f"<ellipse cx='{x}' cy='{y+5}' rx='2.6' ry='3.4' fill='{c}'/>")
    return svg("0 0 80 26", b)


def awning(c):
    b = ""
    for i, col in enumerate((c, P["cream"])):
        x = i * 28
        b += f"<path d='M{x} 0 H{x+28} V24 A14 9 0 0 1 {x} 24 Z' fill='{col}'/>"
    b += f"<rect x='0' y='0' width='56' height='3' fill='#00000030'/>"
    b += f"<path d='M0 24 A14 9 0 0 0 28 24 A14 9 0 0 0 56 24' fill='none' stroke='#00000026' stroke-width='1'/>"
    return svg("0 0 56 34", b)


def stars(seed=7, fill=P["cream"]):
    rnd = random.Random(seed)
    b = ""
    for _ in range(22):
        b += (f"<circle cx='{rnd.uniform(0,180):.1f}' cy='{rnd.uniform(0,180):.1f}' r='{rnd.uniform(.45,1.4):.2f}' "
              f"fill='{fill}' opacity='{rnd.uniform(.35,.95):.2f}'/>")
    for _ in range(3):
        x, y, s = rnd.uniform(10, 170), rnd.uniform(10, 170), rnd.uniform(2.5, 4)
        b += (f"<path d='M{x} {y-s} Q{x} {y} {x+s} {y} Q{x} {y} {x} {y+s} Q{x} {y} {x-s} {y} Q{x} {y} {x} {y-s} Z' "
              f"fill='{P['gold']}' opacity='.85'/>")
    return svg("0 0 180 180", b)


def dabu(col=P["cream"], op=".16"):
    """indigo dabu block-print repeat: 4-petal flower, crescent, dots"""
    b = f"<g fill='{col}' opacity='{op}'>"
    for a in (0, 45, 90, 135):
        b += f"<ellipse cx='18' cy='18' rx='2.8' ry='7.5' transform='rotate({a} 18 18)'/>"
    b += "<circle cx='18' cy='18' r='2.4'/>"
    b += "<path d='M57 46 A9 9 0 1 0 63 62 A7 7 0 1 1 57 46 Z'/>"
    b += "<circle cx='54' cy='18' r='1.7'/><circle cx='18' cy='54' r='1.7'/><circle cx='36' cy='36' r='1.1'/>"
    b += "<circle cx='0' cy='36' r='1.1'/><circle cx='36' cy='0' r='1.1'/><circle cx='72' cy='36' r='1.1'/><circle cx='36' cy='72' r='1.1'/>"
    b += "</g>"
    return svg("0 0 72 72", b)


def paws(col=P["brass"]):
    def paw(x, y, r):
        return (f"<g transform='rotate({r} {x} {y})' fill='{col}'><ellipse cx='{x}' cy='{y}' rx='4.2' ry='3.6'/>"
                f"<circle cx='{x-4.6}' cy='{y-4.4}' r='1.6'/><circle cx='{x-1.6}' cy='{y-6.6}' r='1.7'/>"
                f"<circle cx='{x+1.8}' cy='{y-6.6}' r='1.7'/><circle cx='{x+4.8}' cy='{y-4.4}' r='1.6'/></g>")
    return svg("0 0 64 30", paw(14, 24, 75) + paw(46, 12, 105))


def rangoli():
    """quarter rangoli for a corner at (0,0)"""
    b = ""
    for i, a in enumerate(range(6, 90, 14)):
        r = math.radians(a)
        x, y = 44 * math.cos(r), 44 * math.sin(r)
        c = (P["rani"], P["marigold"], P["peacock"], P["gold"], P["parrot"], P["rani"], P["marigold"])[i % 7]
        b += f"<ellipse cx='{x:.1f}' cy='{y:.1f}' rx='9' ry='4.2' fill='{c}' transform='rotate({a} {x:.1f} {y:.1f})'/>"
        x2, y2 = 66 * math.cos(r), 66 * math.sin(r)
        b += f"<circle cx='{x2:.1f}' cy='{y2:.1f}' r='2.2' fill='{P['gold']}'/>"
    b += f"<path d='M0 26 A26 26 0 0 0 26 0' fill='none' stroke='{P['gold']}' stroke-width='2.4'/>"
    b += f"<path d='M0 16 A16 16 0 0 0 16 0 L0 0 Z' fill='{P['rani']}'/>"
    b += f"<path d='M0 56 A56 56 0 0 0 56 0' fill='none' stroke='{P['cream']}' stroke-width='1' stroke-dasharray='2 3' opacity='.8'/>"
    b += f"<path d='M0 78 A78 78 0 0 0 78 0' fill='none' stroke='{P['gold']}' stroke-width='1.2' opacity='.8'/>"
    return svg("0 0 90 90", b)


def skyline(fill="#050a1e", bulb=P["gold"]):
    """night-fair horizon: tents, a Ferris wheel, a carousel dome (tile 480 x 90)"""
    b = f"<g fill='{fill}'>"
    for x, w, h in ((0, 70, 38), (64, 56, 30), (190, 80, 44), (262, 60, 28), (400, 84, 40)):
        b += f"<path d='M{x} 90 L{x} {90-h*0.45:.0f} L{x+w/2:.0f} {90-h} L{x+w} {90-h*0.45:.0f} L{x+w} 90 Z'/>"
        b += f"<path d='M{x+w/2:.0f} {90-h} V{82-h} L{x+w/2+9:.0f} {85-h} L{x+w/2:.0f} {88-h}' />"
    cx, cy, r = 150, 46, 32
    b += f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='none' stroke='{fill}' stroke-width='3'/>"
    for k in range(8):
        a = math.radians(k * 45)
        b += f"<line x1='{cx}' y1='{cy}' x2='{cx + r*math.cos(a):.1f}' y2='{cy + r*math.sin(a):.1f}' stroke='{fill}' stroke-width='1.6'/>"
        b += f"<rect x='{cx + r*math.cos(a)-4:.1f}' y='{cy + r*math.sin(a)+1:.1f}' width='8' height='6' rx='1.5'/>"
    b += f"<path d='M{cx-14} 90 L{cx} {cy} L{cx+14} 90 Z'/>"
    b += f"<path d='M318 90 V62 Q350 34 382 62 V90 Z'/><path d='M350 40 V30' stroke='{fill}' stroke-width='2'/>"
    b += "</g>"
    for k in range(16):
        a = math.radians(k * 22.5)
        b += f"<circle cx='{cx + r*math.cos(a):.1f}' cy='{cy + r*math.sin(a):.1f}' r='1.3' fill='{bulb}'/>"
    for x in range(324, 380, 8):
        b += f"<circle cx='{x}' cy='{60 - 0.0*(x-350)**2:.0f}' r='1.1' fill='{bulb}'/>"
    return svg("0 0 480 90", b)


def torn(col="#000"):
    return svg("0 0 24 8", f"<path d='M0 8 L0 3 L3 1.2 L6 4 L9 .6 L12 3.6 L15 1 L18 4.2 L21 1.4 L24 3 L24 8 Z' fill='{col}'/>")


def grain():
    return svg("0 0 220 220", "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' "
               "stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 .35 0 0 0 0 .25 0 0 0 0 .12 0 0 0 .55 0'/></filter>"
               "<rect width='220' height='220' filter='url(#n)'/>")


# ------------------------------------------------------------------ icons (wordless role markers, 24 x 24)
ICONS = {
    "star": f"<path d='M12 2 L14.9 8.6 L22 9.3 L16.6 14 L18.2 21 L12 17.3 L5.8 21 L7.4 14 L2 9.3 L9.1 8.6 Z' fill='{P['gold']}' stroke='{P['brass']}' stroke-width='.8'/>",
    "moon": f"<path d='M15 3 A9 9 0 1 0 21 15 A7 7 0 1 1 15 3 Z' fill='{P['yellow']}' stroke='{P['brass']}' stroke-width='.8'/>",
    "lantern": (f"<line x1='12' y1='0' x2='12' y2='4' stroke='{P['brass']}'/><rect x='9' y='3.5' width='6' height='2' rx='.6' fill='{P['gold']}'/>"
                f"<ellipse cx='12' cy='12' rx='6.5' ry='7' fill='{P['rani']}'/><path d='M9 6 Q6.5 12 9 18 M12 5 V19 M15 6 Q17.5 12 15 18' stroke='#00000040' fill='none' stroke-width='.8'/>"
                f"<rect x='9' y='18.5' width='6' height='2' rx='.6' fill='{P['gold']}'/><line x1='12' y1='20.5' x2='12' y2='24' stroke='{P['rani']}' stroke-width='1.4'/>"),
    "ticket": (f"<path d='M2 7 H22 V10 A2 2 0 0 0 22 14 V17 H2 V14 A2 2 0 0 0 2 10 Z' fill='{P['yellow']}' stroke='{P['brass']}' stroke-width='.8'/>"
               f"<line x1='8' y1='7.5' x2='8' y2='16.5' stroke='{P['brass']}' stroke-dasharray='1.2 1.2'/><circle cx='15' cy='12' r='2.2' fill='{P['rani']}'/>"),
    "pencil": (f"<g transform='rotate(-40 12 12)'><rect x='4' y='9.5' width='13' height='5' fill='{P['marigold']}'/><rect x='2' y='9.5' width='2.6' height='5' fill='{P['rani']}'/>"
               f"<path d='M17 9.5 L22 12 L17 14.5 Z' fill='#f3d9a8'/><path d='M20.4 11.2 L22 12 L20.4 12.8 Z' fill='{P['ink']}'/></g>"),
    "magnifier": (f"<circle cx='10' cy='10' r='6.5' fill='{P['mint']}' stroke='{P['peacock']}' stroke-width='2.2'/>"
                  f"<line x1='15' y1='15' x2='21.5' y2='21.5' stroke='{P['brass']}' stroke-width='3' stroke-linecap='round'/><path d='M7 8 Q8.5 6 11 6.5' stroke='#fff' fill='none'/>"),
    "key": (f"<circle cx='7' cy='12' r='4.6' fill='none' stroke='{P['gold']}' stroke-width='2.4'/><path d='M11.5 12 H22 M18 12 V16 M21 12 V15' "
            f"stroke='{P['gold']}' stroke-width='2.2' fill='none' stroke-linecap='round'/>"),
    "eye": (f"<path d='M2 12 Q12 3 22 12 Q12 21 2 12 Z' fill='#fff' stroke='{P['peacock']}' stroke-width='1.6'/><circle cx='12' cy='12' r='3.6' fill='{P['peacock']}'/>"
            f"<circle cx='13' cy='11' r='1.1' fill='#fff'/>"),
    "paw": (f"<g fill='{P['marigold']}'><ellipse cx='12' cy='15.5' rx='5.4' ry='4.6'/><circle cx='5.8' cy='9.6' r='2.1'/><circle cx='9.8' cy='6.4' r='2.2'/>"
            f"<circle cx='14.2' cy='6.4' r='2.2'/><circle cx='18.2' cy='9.6' r='2.1'/></g>"),
    "gift": (f"<rect x='3' y='9' width='18' height='12' rx='1.5' fill='{P['rani']}'/><rect x='2' y='7' width='20' height='4' rx='1' fill='#e8679a'/>"
             f"<rect x='10.5' y='7' width='3' height='14' fill='{P['gold']}'/><path d='M12 7 Q6 1 6.5 5.5 Q7 7 12 7 Q18 1 17.5 5.5 Q17 7 12 7 Z' fill='{P['gold']}'/>"),
    "bag": (f"<path d='M6 9 H18 L20 22 H4 Z' fill='{P['peacock']}'/><path d='M8 9 Q12 4 16 9' fill='none' stroke='{P['gold']}' stroke-width='1.6'/>"
            f"<circle cx='12' cy='15' r='2' fill='{P['yellow']}'/>"),
    "sun": (f"<g stroke='{P['marigold']}' stroke-width='1.8' stroke-linecap='round'><path d='M12 1.5 V4.5 M12 19.5 V22.5 M1.5 12 H4.5 M19.5 12 H22.5 "
            f"M4.6 4.6 L6.7 6.7 M17.3 17.3 L19.4 19.4 M4.6 19.4 L6.7 17.3 M17.3 6.7 L19.4 4.6'/></g><circle cx='12' cy='12' r='5.6' fill='{P['yellow']}'/>"),
    "snow": (f"<g stroke='{P['sky']}' stroke-width='1.7' stroke-linecap='round' fill='none'><path d='M12 2 V22 M3.3 7 L20.7 17 M3.3 17 L20.7 7'/>"
             f"<path d='M9.5 3.8 L12 6 L14.5 3.8 M9.5 20.2 L12 18 L14.5 20.2'/></g>"),
    "house": (f"<path d='M3 11 L12 3.5 L21 11' fill='{P['kite']}'/><rect x='5' y='10.5' width='14' height='10.5' fill='{P['cream']}' stroke='{P['brass']}' stroke-width='.8'/>"
              f"<rect x='8' y='13' width='3.5' height='3.5' fill='{P['yellow']}'/><rect x='13' y='14' width='3' height='7' fill='{P['indigo']}'/>"),
    "thermo": (f"<rect x='9.5' y='2' width='5' height='15' rx='2.5' fill='#fff' stroke='{P['ink']}' stroke-width='1'/><circle cx='12' cy='19' r='3.8' fill='{P['kite']}' stroke='{P['ink']}' stroke-width='1'/>"
               f"<rect x='11' y='9' width='2' height='9' fill='{P['kite']}'/>"),
}


def css():
    out = [f"""/* ChandRush CREATIVE KIT (Art Direction A1). GENERATED by kitgen.py: edit kitgen.py, not this file.
   How and when to use each piece: ART-DIRECTION.md. Live gallery: kit-gallery-1.html / kit-gallery-2.html (kit-1.png, kit-2.png).
   Rule: the kit draws no letters or numbers. Every printed word still comes from the manuscript. */

@font-face {{ font-family: "Baloo 2"; src: url("fonts/Baloo2.ttf") format("truetype"); font-weight: 400 800; font-style: normal; }}
@font-face {{ font-family: "Kalam"; src: url("fonts/Kalam-Regular.ttf") format("truetype"); font-weight: 400; font-style: normal; }}
@font-face {{ font-family: "Kalam"; src: url("fonts/Kalam-Bold.ttf") format("truetype"); font-weight: 700; font-style: normal; }}

.page {{
  --night: {P['night']}; --indigo: {P['indigo']}; --indigo2: {P['indigo2']}; --gold: {P['gold']}; --marigold: {P['marigold']};
  --yellow: {P['yellow']}; --rani: {P['rani']}; --peacock: {P['peacock']}; --parrot: {P['parrot']}; --kite: {P['kite']};
  --sky: {P['sky']}; --cream: {P['cream']}; --paperc: {P['paper']}; --inkc: {P['ink']}; --brass: {P['brass']}; --mint: {P['mint']};
  --display: "Baloo 2", "Source Sans 3", sans-serif; --hand: "Kalam", "Source Serif 4", serif;
  --lift: 0 1.5pt 0 rgba(0,0,0,.10), 0 6pt 16pt rgba(10,16,44,.30);
}}

/* base.css classes (.eq, .h-sub, .note, .title) read --ink / --head / --muted: every light reading object resets them
   to dark ink, every dark stage to cream, so text is always readable whatever the stage. */
.stage-paper, .stage-paper-cool, .stage-split, .obj, .sheet, .ledger, .ticket, .tag, .flap, .scroll, .capnote, .say {{
  --ink: var(--inkc); --head: var(--inkc); --muted: #4b5468; --cap: #fff7e2; --cap-ink: var(--inkc); }}
.plaque {{ --ink: #3b2a08; --head: #3b2a08; }}
.stage-night, .stage-dabu, .stage-dabu-teal, .stage-dusk, .slate {{ --ink: var(--cream); --head: var(--gold); --muted: #c9d0e2; }}

/* ---------------------------------------------------------------- 1. STAGES: the world behind the page (pick one) */
.stage-night {{ background: {uri(stars(7))} 0 0 / 180pt 180pt, {uri(stars(19, P['sky']))} 60pt 90pt / 240pt 240pt,
  radial-gradient(ellipse 70% 60% at 50% 0%, #2b4590 0%, #17265a 55%, #0c1534 100%); color: var(--cream); }}
.stage-dabu {{ background: {uri(dabu())} 0 0 / 54pt 54pt, linear-gradient(160deg, #22377a, #17295e 60%, #142250); color: var(--cream); }}
.stage-dabu-teal {{ background: {uri(dabu(P['cream'], '.14'))} 0 0 / 54pt 54pt, linear-gradient(160deg, #17706f, #0f5554); color: var(--cream); }}
.stage-dusk {{ background: {uri(stars(11))} 0 0 / 180pt 180pt,
  linear-gradient(180deg, #13214a 0%, #2c2a63 42%, #6b3a72 72%, #c8566a 90%, #f08a3c 100%); color: var(--cream); }}
.stage-paper {{ background: {uri(grain())} 0 0 / 220pt 220pt, radial-gradient(ellipse 80% 75% at 50% 45%, #fffaf0 55%, #f4e4c6 100%); color: var(--inkc); }}
.stage-paper-cool {{ background: {uri(grain())} 0 0 / 220pt 220pt, radial-gradient(ellipse 80% 75% at 50% 45%, #f7fbfb 55%, #dcebee 100%); color: var(--inkc); }}
.stage-split {{ background: linear-gradient(90deg, #fff4e0 0 50%, #e4f1f8 50% 100%); }}

/* textures and glows you can add to any block */
.grain {{ background-image: {uri(grain())}; background-size: 220pt 220pt; }}
.glow {{ position: absolute; border-radius: 50%; pointer-events: none;
  background: radial-gradient(circle, rgba(242,180,65,.55) 0%, rgba(242,180,65,.18) 40%, transparent 70%); }}
.skyline {{ position: absolute; left: 0; right: 0; bottom: 0; height: 70pt; pointer-events: none;
  background: {uri(skyline())} 0 100% / auto 100% repeat-x, linear-gradient(180deg, transparent 0%, rgba(242,140,40,.0) 30%, rgba(242,140,40,.22) 100%); }}
.skyline.ink {{ background-image: {uri(skyline('#1a2a5a', P['gold']))}; }}

/* ---------------------------------------------------------------- 2. GARLANDS AND EDGES (one per page, top or one side) */
.toran {{ position: absolute; height: 40pt; background: {uri(toran([P['rani'], P['marigold'], P['peacock'], P['gold'], P['parrot']]))} 0 0 / 110pt 40pt repeat-x; pointer-events: none; }}
.toran.cool {{ background-image: {uri(toran([P['peacock'], P['sky'], P['gold'], P['indigo2'], P['cream']]))}; }}
.toran.warm {{ background-image: {uri(toran([P['kite'], P['yellow'], P['rani'], P['marigold'], P['gold']]))}; }}
.marigold {{ position: absolute; height: 30pt; background: {uri(marigolds())} 0 0 / 90pt 30pt repeat-x; pointer-events: none; }}
.lanterns {{ position: absolute; height: 62pt; background: {uri(lanterns())} 0 0 / 130pt 62pt repeat-x; pointer-events: none; }}
.fairy {{ position: absolute; height: 22pt; background: {uri(fairy_lights())} 0 0 / 70pt 22pt repeat-x; pointer-events: none; }}
.awning {{ position: absolute; height: 36pt; background: {uri(awning(P['rani']))} 0 0 / 50pt 32pt repeat-x;
  filter: drop-shadow(0 3pt 3pt rgba(0,0,0,.28)); pointer-events: none; }}
.awning.teal {{ background-image: {uri(awning(P['peacock']))}; }}
.awning.marigold {{ background-image: {uri(awning(P['marigold']))}; }}
.awning.indigo {{ background-image: {uri(awning(P['indigo2']))}; }}
.paws {{ position: absolute; height: 20pt; background: {uri(paws())} 0 0 / 44pt 20pt repeat-x; opacity: .55; pointer-events: none; }}
.rangoli {{ position: absolute; width: 90pt; height: 90pt; background: {uri(rangoli())} 0 0 / 100% 100% no-repeat; pointer-events: none; }}
.rangoli.tr {{ transform: scaleX(-1); }} .rangoli.bl {{ transform: scaleY(-1); }} .rangoli.br {{ transform: scale(-1,-1); }}
.dabu-band {{ position: absolute; background: {uri(dabu(P['cream'], '.5'))} 0 0 / 36pt 36pt, var(--indigo); }}

/* ---------------------------------------------------------------- 3. TYPE ROLES (body text stays Source Sans 3 14/18) */
.h-title {{ font: 800 34pt/1.02 var(--display); letter-spacing: -.005em; color: var(--title-c, var(--gold)); margin: 0;
  text-shadow: 0 2pt 0 rgba(0,0,0,.22); }}
.h-title.ink {{ --title-c: var(--inkc); text-shadow: 0 2pt 0 rgba(242,180,65,.55); }}
.h-chip {{ display: inline-flex; align-items: center; gap: 6pt; font: 700 17pt/1.1 var(--display); color: var(--chip-c, var(--inkc)); margin: 0 0 6pt; }}
.h-chip .ico {{ width: 20pt; height: 20pt; }}
.hand {{ font: 400 15pt/19pt var(--hand); }}
.display {{ font-family: var(--display); }}

/* ribbon banner for a heading: <div class="ribbon rani">Example 11</div> */
.ribbon {{ display: inline-block; position: relative; padding: 5pt 26pt 3pt; font: 800 20pt/1.1 var(--display); color: #fff;
  background: var(--rb, var(--rani)); clip-path: polygon(0 0, 100% 0, calc(100% - 11pt) 50%, 100% 100%, 0 100%, 11pt 50%);
  text-shadow: 0 1pt 0 rgba(0,0,0,.25); }}
.ribbon.teal {{ --rb: var(--peacock); }} .ribbon.marigold {{ --rb: var(--marigold); }} .ribbon.indigo {{ --rb: var(--indigo2); }} .ribbon.parrot {{ --rb: #4f8f37; }}

/* hanging signboard: a painted mela board on two strings */
.sign {{ position: absolute; padding: 8pt 18pt 6pt; border-radius: 8pt; background: linear-gradient(#24397d, #1a2c66);
  border: 2.2pt solid var(--gold); box-shadow: inset 0 0 0 2.5pt #1a2c66, inset 0 0 0 3.3pt rgba(242,180,65,.6), var(--lift);
  color: var(--cream); font: 800 26pt/1.05 var(--display); text-align: center; }}
.sign::before, .sign::after {{ content: ""; position: absolute; top: -40pt; width: 1.4pt; height: 40pt; background: var(--brass); }}
.sign::before {{ left: 18%; transform: rotate(-8deg); transform-origin: bottom; }} .sign::after {{ right: 18%; transform: rotate(8deg); transform-origin: bottom; }}
.sign.rani {{ background: linear-gradient(#e0548a, #c23468); box-shadow: inset 0 0 0 2.5pt #c23468, inset 0 0 0 3.3pt rgba(255,240,200,.7), var(--lift); }}
.sign.teal {{ background: linear-gradient(#1a8f8d, #0f6d6c); box-shadow: inset 0 0 0 2.5pt #0f6d6c, inset 0 0 0 3.3pt rgba(255,240,200,.7), var(--lift); }}

/* ---------------------------------------------------------------- 4. READING OBJECTS (light fields, dark ink, 14/18 body) */
.obj {{ position: absolute; color: var(--inkc); }}
.lift {{ box-shadow: var(--lift); }}
.tilt-l {{ transform: rotate(-1.2deg); }} .tilt-r {{ transform: rotate(1.1deg); }}

/* paper sheet: the default reading field (cream handmade paper) */
.sheet {{ position: absolute; background: {uri(grain())} 0 0 / 220pt 220pt, var(--sheet-bg, #fffaf0); color: var(--inkc);
  border-radius: 6pt; padding: 14pt 18pt; box-shadow: var(--lift); }}
.sheet.mint {{ --sheet-bg: #eef8f3; }} .sheet.sky {{ --sheet-bg: #eef6fb; }} .sheet.blush {{ --sheet-bg: #fff0f3; }} .sheet.butter {{ --sheet-bg: #fff6d8; }}

/* torn bottom/top edge for a sheet: add class torn-b / torn-t */
.torn-b {{ border-bottom-left-radius: 0; border-bottom-right-radius: 0;
  -webkit-mask: linear-gradient(#000,#000) top / 100% calc(100% - 7pt) no-repeat, {uri(torn())} bottom / 22pt 7.5pt repeat-x;
          mask: linear-gradient(#000,#000) top / 100% calc(100% - 7pt) no-repeat, {uri(torn())} bottom / 22pt 7.5pt repeat-x; }}
.torn-t {{ border-top-left-radius: 0; border-top-right-radius: 0;
  -webkit-mask: linear-gradient(#000,#000) bottom / 100% calc(100% - 7pt) no-repeat, {uri(torn())} top / 22pt 7.5pt repeat-x;
          mask: linear-gradient(#000,#000) bottom / 100% calc(100% - 7pt) no-repeat, {uri(torn())} top / 22pt 7.5pt repeat-x; transform: none; }}
.shadowed {{ filter: drop-shadow(0 4pt 6pt rgba(10,16,44,.32)); }}   /* use on a WRAPPER of masked shapes (masks cut box-shadow) */

/* crew notebook: worked steps. Spiral rings on the left, rani margin rule. Add .dots for faint squared paper. */
.ledger {{ position: absolute; color: var(--inkc); border-radius: 3pt 8pt 8pt 3pt; padding: 14pt 18pt 12pt 46pt;
  background: linear-gradient(90deg, transparent 33pt, rgba(214,63,122,.55) 33pt 34.2pt, transparent 34.2pt), #fffdf5; box-shadow: var(--lift); }}
.ledger::before {{ content: ""; position: absolute; left: -7pt; top: 12pt; bottom: 12pt; width: 18pt;
  background: radial-gradient(circle at 50% 50%, #fffdf5 0 3pt, #3b3f4a 3.2pt 4.6pt, transparent 4.9pt) 0 0 / 18pt 19pt repeat-y; }}
.ledger.dots {{ background: linear-gradient(90deg, transparent 33pt, rgba(214,63,122,.55) 33pt 34.2pt, transparent 34.2pt),
  radial-gradient(circle, rgba(29,47,107,.16) .7pt, transparent 1pt) 0 0 / 12pt 12pt, #fffdf5; }}

/* admission ticket: questions / "Try". Stub on the left holds a wordless icon: <div class="ticket"><i class="stub"><i class="ico ticket"></i></i>…</div> */
.ticket {{ position: absolute; color: var(--inkc); background: var(--tk, #ffe9ad); border-radius: 7pt; padding: 12pt 16pt 12pt 50pt;
  -webkit-mask: radial-gradient(circle 8pt at 0 50%, transparent 97%, #000) left / 51% 100% no-repeat,
                radial-gradient(circle 8pt at 100% 50%, transparent 97%, #000) right / 51% 100% no-repeat;
          mask: radial-gradient(circle 8pt at 0 50%, transparent 97%, #000) left / 51% 100% no-repeat,
                radial-gradient(circle 8pt at 100% 50%, transparent 97%, #000) right / 51% 100% no-repeat; }}
.ticket::before {{ content: ""; position: absolute; left: 38pt; top: 6pt; bottom: 6pt; border-left: 1.6pt dashed rgba(120,80,20,.45); }}
.ticket::after {{ content: ""; position: absolute; inset: 4pt; border: 1pt solid rgba(201,150,46,.55); border-radius: 5pt; pointer-events: none; }}
.ticket > .stub {{ position: absolute; left: 9pt; top: 50%; width: 22pt; height: 22pt; transform: translateY(-50%); }}
.ticket > .stub > .ico {{ width: 22pt; height: 22pt; }}
.ticket.pink {{ --tk: #ffd9e6; }} .ticket.mint {{ --tk: #d9f2ea; }} .ticket.sky {{ --tk: #dcefff; }}

/* gift / price tag with a punched hole: put a .string svg from kit-gallery-2 next to it if you like */
.tag {{ position: absolute; color: var(--inkc); background: var(--tg, #fff3d6); padding: 14pt 18pt 14pt 44pt; border-radius: 0 8pt 8pt 0;
  clip-path: polygon(26pt 0, 100% 0, 100% 100%, 26pt 100%, 0 calc(50% + 22pt), 0 calc(50% - 22pt));
  -webkit-mask: radial-gradient(circle 5.5pt at 19pt 50%, transparent 96%, #000); mask: radial-gradient(circle 5.5pt at 19pt 50%, transparent 96%, #000); }}
.tag::after {{ content: ""; position: absolute; left: 11pt; top: calc(50% - 8.5pt); width: 17pt; height: 17pt; border-radius: 50%; border: 2pt solid var(--gold); }}
.tag.pink {{ --tg: #ffe3ec; }} .tag.mint {{ --tg: #e2f5ee; }}

/* reveal flap: answers / "Check your …". A dashed fold line and a folded corner say "lift me after you try". */
.flap {{ position: absolute; color: var(--inkc); background: var(--fl, #e9f6f1); border-radius: 3pt 3pt 9pt 9pt; padding: 20pt 16pt 12pt;
  box-shadow: var(--lift); border-top: 2pt dashed rgba(18,128,127,.6); }}
.flap::before {{ content: ""; position: absolute; top: -2pt; right: -0.5pt; width: 24pt; height: 24pt;
  background: linear-gradient(225deg, var(--under, #fffaf0) 0 50%, #bfe3d7 50% 100%); border-bottom-left-radius: 5pt;
  box-shadow: -1.5pt 1.5pt 2pt rgba(0,0,0,.18); }}
.flap > .pull {{ position: absolute; top: -13pt; left: 18pt; width: 34pt; height: 22pt; border-radius: 12pt 12pt 4pt 4pt;
  background: var(--peacock); display: flex; align-items: center; justify-content: center; box-shadow: 0 2pt 3pt rgba(0,0,0,.2); }}
.flap > .pull > .ico {{ width: 17pt; height: 17pt; }}
.flap.butter {{ --fl: #fff3cf; }} .flap.butter::before {{ background: linear-gradient(225deg, var(--under, #fffaf0) 0 50%, #f3dc95 50% 100%); }}
.flap.butter > .pull {{ background: var(--marigold); }}

/* brass plaque: one key result or rule */
.plaque {{ position: absolute; color: #3b2a08; background: linear-gradient(180deg, #fff1c9, #f7d77e 60%, #eec35c);
  border: 2pt solid var(--brass); border-radius: 7pt; padding: 10pt 22pt; box-shadow: inset 0 0 0 2pt #fff4d2, inset 0 0 0 3pt rgba(150,100,20,.35), var(--lift); }}
.plaque::before, .plaque::after {{ content: ""; position: absolute; top: 50%; width: 6pt; height: 6pt; margin-top: -3pt; border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #fff6d8, #a0741f); }}
.plaque::before {{ left: 7pt; }} .plaque::after {{ right: 7pt; }}

/* chalk slate: short items only (light text on dark, keep it brief) */
.slate {{ position: absolute; background: radial-gradient(ellipse at 40% 30%, #2f4a45, #1f3330); color: #f3f6ee; border: 7pt solid #9a6a3a;
  border-radius: 6pt; padding: 12pt 16pt; box-shadow: inset 0 0 0 1pt rgba(0,0,0,.4), var(--lift); }}

/* welcome scroll: narrator caption that opens a section */
.scroll {{ position: absolute; color: var(--inkc); background: {uri(grain())} 0 0 / 220pt 220pt, #fff6df; padding: 14pt 22pt;
  font: 400 14pt/18pt var(--serif); border-left: 0; border-right: 0; box-shadow: var(--lift); }}
.scroll::before, .scroll::after {{ content: ""; position: absolute; top: -6pt; bottom: -6pt; width: 12pt; border-radius: 6pt;
  background: linear-gradient(90deg, #b9802c, #f2cf7d 45%, #a86f22); box-shadow: 0 2pt 3pt rgba(0,0,0,.3); }}
.scroll::before {{ left: -8pt; }} .scroll::after {{ right: -8pt; }}

/* washi tape: holds paper to the page. --r rotates it. */
.tape {{ position: absolute; width: 64pt; height: 17pt; transform: rotate(var(--r, -5deg)); opacity: .92; pointer-events: none;
  background: repeating-linear-gradient(45deg, rgba(214,63,122,.78) 0 5pt, rgba(255,246,230,.7) 5pt 10pt);
  clip-path: polygon(0 0, 4% 18%, 0 36%, 4% 54%, 0 72%, 4% 90%, 0 100%, 100% 100%, 96% 82%, 100% 64%, 96% 46%, 100% 28%, 96% 10%, 100% 0); }}
.tape.teal {{ background: repeating-linear-gradient(45deg, rgba(18,128,127,.78) 0 5pt, rgba(255,246,230,.7) 5pt 10pt); }}
.tape.gold {{ background: radial-gradient(circle, rgba(255,250,235,.9) 1.6pt, transparent 2pt) 0 0 / 8pt 8pt, rgba(242,180,65,.85); }}
.tape.green {{ background: repeating-linear-gradient(90deg, rgba(106,168,79,.8) 0 6pt, rgba(255,246,230,.7) 6pt 9pt); }}

/* ---------------------------------------------------------------- 5. SPEECH, ASIDES, CAPTIONS */
/* comic balloon with a curved SVG tail (copy the tail svg from kit-gallery-2.html). --tx tail x, --tr tail rotation */
.say {{ position: absolute; background: var(--say-bg, #fffdf6); color: var(--inkc); border: 1.4pt solid var(--inkc); border-radius: 50% / 48%;
  padding: 11pt 20pt; font: 600 14.5pt/18pt var(--display); text-align: center; }}
.say > svg.tail {{ position: absolute; width: 24pt; height: 26pt; left: var(--tx, 30%); top: calc(100% - 3pt); overflow: visible;
  transform: rotate(var(--tr, 0deg)); transform-origin: 50% 0; }}
.say > svg.tail.up {{ top: auto; bottom: calc(100% - 3pt); transform: scaleY(-1) rotate(var(--tr, 0deg)); transform-origin: 50% 100%; }}
.say > svg.tail path {{ fill: var(--say-bg, #fffdf6); stroke: var(--inkc); stroke-width: 1.4pt; stroke-linejoin: round; }}
.say.aside {{ --say-bg: #fff8e8; font: 400 15pt/19pt var(--hand); border-width: 1.1pt; }}   /* companion remark to the reader */
.say.aside.cool {{ --say-bg: #eef6fb; }}
.say.shout {{ border-radius: 30%; font-weight: 800; }}

/* narration caption: cream slip with a gold star pin */
.capnote {{ position: absolute; background: #fff7e2; color: var(--inkc); font: 400 14pt/18pt var(--serif); padding: 8pt 12pt 8pt 14pt;
  border-radius: 3pt; box-shadow: 0 1pt 0 rgba(0,0,0,.08), 0 3pt 8pt rgba(10,16,44,.28); border-left: 3pt solid var(--gold); }}

/* ---------------------------------------------------------------- 6. ART HOLDERS (panels, companions) */
/* jharokha window: an Indian carved window for a companion or a scene peek.
   Needs the <svg class="defs"> block from kit-gallery-2.html once per page (it defines clip-path #jharokha). */
.jharokha {{ position: absolute; }}
.jharokha > img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: var(--fx, 50%) var(--fy, 50%);
  clip-path: url(#jharokha); }}
.jharokha > svg.rim {{ position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible; }}
.jharokha > svg.rim path {{ fill: none; vector-effect: non-scaling-stroke; }}
.jharokha > .sill {{ position: absolute; left: -9%; right: -9%; bottom: -10pt; height: 14pt; border-radius: 3pt;
  background: linear-gradient(#f6d27a, #c9962e 60%, #9a6f1f); box-shadow: 0 3pt 5pt rgba(0,0,0,.35); }}
.jharokha > .sill::before, .jharokha > .sill::after {{ content: ""; position: absolute; top: 14pt; width: 16pt; height: 14pt;
  background: linear-gradient(#c9962e, #8a6119); clip-path: polygon(0 0, 100% 0, 60% 100%, 40% 100%); }}
.jharokha > .sill::before {{ left: 14%; }} .jharokha > .sill::after {{ right: 14%; }}

/* snapshot: a taped photo of a moment (art with its own background) */
.snap {{ position: absolute; background: #fffdf8; padding: 7pt 7pt 20pt; box-shadow: 0 3pt 10pt rgba(0,0,0,.38); transform: rotate(var(--r, 2.5deg)); }}
.snap > img {{ display: block; width: 100%; height: 100%; object-fit: cover; object-position: var(--fx, 50%) var(--fy, 50%); }}

/* cut-out character that steps OUT of a frame (transparent PNG). Keep it above the frame's edge. */
.pop {{ position: absolute; z-index: 5; filter: drop-shadow(0 6pt 8pt rgba(8,12,36,.45)); pointer-events: none; }}
.pop > img {{ width: 100%; height: 100%; object-fit: contain; object-position: var(--fx, 50%) 100%; }}

/* story panel with a painted brass edge; .arch gives the top a mela-arch shape */
.frame-panel {{ position: absolute; overflow: hidden; border-radius: 8pt; border: 2.2pt solid var(--gold);
  box-shadow: inset 0 0 0 1.5pt rgba(0,0,0,.35), var(--lift); background: #000; }}
.frame-panel > img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: var(--fx, 50%) var(--fy, 50%); }}
.frame-panel.round {{ border-radius: 50%; }}

/* ---------------------------------------------------------------- 7. FOLIO: the moonset clock (book-wide signature)
   <div class="moonclock" style="left:…;top:…;--t:.36"><i class="arc"></i><i class="arm"><b>39</b></i></div>
   --t = page / last page of the chapter (0 = moonrise at left, 1 = moonset at right). */
.moonclock {{ position: absolute; width: 104pt; height: 40pt; overflow: hidden; pointer-events: none; }}
.moonclock > .arc {{ position: absolute; left: 6pt; top: 8pt; width: 92pt; height: 92pt; border-radius: 50%;
  border: 1.3pt dotted var(--mc-line, rgba(242,180,65,.85)); }}
.moonclock > .arm {{ position: absolute; left: 51pt; top: 8pt; width: 2pt; height: 46pt; transform-origin: 1pt 46pt;
  transform: rotate(calc(-62deg + var(--t, .5) * 124deg)); }}
.moonclock > .arm > b {{ position: absolute; left: -10pt; top: -11pt; width: 22pt; height: 22pt; border-radius: 50%;
  transform: rotate(calc(62deg - var(--t, .5) * 124deg));
  background: radial-gradient(circle at 34% 32%, #fffbea 0 30%, #f9e7a8 60%, #e9c86a); box-shadow: 0 0 6pt 2pt rgba(242,180,65,.55);
  font: 800 10pt/22pt var(--display); color: #3b2a08; text-align: center; }}
.moonclock::after {{ content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 9pt;
  background: {uri(skyline('#050a1e', P['gold']))} 0 100% / auto 100% repeat-x; opacity: var(--mc-sky, 1); }}
.moonclock.light {{ --mc-line: rgba(160,116,31,.7); --mc-sky: .55; }}

/* ---------------------------------------------------------------- 8. ICONS (wordless role markers): <i class="ico i-star"></i> */
.ico {{ display: inline-block; width: 1.15em; height: 1.15em; vertical-align: -0.2em; background: center / contain no-repeat; }}
"""]
    for name, body in ICONS.items():
        out.append(f".ico.i-{name} {{ background-image: {uri(svg('0 0 24 24', body))}; }}\n")
    return "".join(out)


if __name__ == "__main__":
    dst = os.path.join(HERE, "kit.css")
    with open(dst, "w", encoding="utf-8") as fh:
        fh.write(css())
    print(dst, os.path.getsize(dst) // 1024, "KB")
