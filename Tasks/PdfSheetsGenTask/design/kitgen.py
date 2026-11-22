#!/usr/bin/env python3
"""kitgen.py: build kit.css, the ChandRush creative kit (Art Direction A3 "Lantern Street", see ART-DIRECTION.md).

    python3 PdfSheetsGenTask/design/kitgen.py      -> writes PdfSheetsGenTask/design/kit.css

Audience: 11-year-olds: cool and aspirational, never kiddish. Colours, materials and lighting are SAMPLED FROM THE
LOCATION PLATES (BagroundGenTask/out/plates): royal-blue lacquered planks with gold pinstripe trim, brass with warm
highlights, cream marble, warm stone, lamp gold against moonlight. Class names are stable across A2 -> A3.
Every motif is a small SVG embedded as a data URI, so pages stay self-contained. Edit HERE, never kit.css by hand.
After a change, re-render the galleries:
    python3 pipeline/render_pdf.py PdfSheetsGenTask/design/kit-gallery-1.html /tmp/k1.pdf --png PdfSheetsGenTask/design/kit-1.png
    python3 pipeline/render_pdf.py PdfSheetsGenTask/design/kit-gallery-2.html /tmp/k2.pdf --png PdfSheetsGenTask/design/kit-2.png
The kit draws no letters or numbers (printed words come only from the manuscript).
"""
import math
import os
import random
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))

# sampled from the plates (2026-11-22): royal #234d95, navy shadow #0c1933, lamp gold #f7c684, brass #b3722f,
# cream marble, warm stone #87634c, moonlight #a6c6f5, warning red #bd2d1b
P = dict(void="#0a1428", night="#0c1933", indigo="#16306a", steel="#234d95", brass="#d0a050", brasshi="#f7d9a0",
         brasslo="#8a5a20", cyan="#a6c6f5", teal="#1f4f9a", ember="#f2a541", crimson="#9b2230", ice="#a6c6f5",
         ivory="#efe4d0", parch="#e9dcc4", ink="#121a33", kraft="#d6bf98", royal="#234d95", copper="#b3722f", stone="#87634c")

NS = "xmlns='http://www.w3.org/2000/svg'"


def uri(svg):
    svg = " ".join(svg.split())
    return 'url("data:image/svg+xml,' + urllib.parse.quote(svg, safe=" =:/,;'()-.") + '")'


def svg(vb, body):
    return f"<svg {NS} viewBox='{vb}'>{body}</svg>"


# ------------------------------------------------------------------ stage textures
def stars(seed=3, n=26, col=P["ivory"]):
    rnd = random.Random(seed)
    b = ""
    for _ in range(n):
        c = col if rnd.random() > .2 else P["ice"]
        b += (f"<circle cx='{rnd.uniform(0,220):.1f}' cy='{rnd.uniform(0,220):.1f}' r='{rnd.uniform(.3,.95):.2f}' "
              f"fill='{c}' opacity='{rnd.uniform(.25,.85):.2f}'/>")
    x, y = rnd.uniform(30, 190), rnd.uniform(30, 190)
    b += (f"<path d='M{x} {y-3.2} L{x+.5} {y-.5} L{x+3.2} {y} L{x+.5} {y+.5} L{x} {y+3.2} L{x-.5} {y+.5} L{x-3.2} {y} "
          f"L{x-.5} {y-.5} Z' fill='{P['brasshi']}' opacity='.7'/>")
    return svg("0 0 220 220", b)


def jali(col=P["brass"], op=".10", sw="1.1"):
    """Mughal jali lattice: 8-point star tile"""
    b = (f"<g fill='none' stroke='{col}' stroke-width='{sw}' opacity='{op}'>"
         "<rect x='17' y='17' width='26' height='26'/><path d='M30 11 L49 30 L30 49 L11 30 Z'/>"
         "<path d='M30 0 V11 M60 30 H49 M30 60 V49 M0 30 H11 M0 0 L17 17 M60 0 L43 17 M60 60 L43 43 M0 60 L17 43'/>"
         "<circle cx='30' cy='30' r='4.5'/></g>")
    return svg("0 0 60 60", b)


def blueprint(col=P["cyan"]):
    """large construction drawing watermark: compass rose, arcs, dimension lines (no numbers)"""
    b = f"<g fill='none' stroke='{col}' stroke-width='1'>"
    cx, cy = 300, 300
    for r in (60, 120, 200, 280):
        b += f"<circle cx='{cx}' cy='{cy}' r='{r}' stroke-dasharray='{'4 6' if r in (120, 280) else 'none'}'/>"
    for k in range(16):
        a = math.radians(k * 22.5)
        r1, r2 = (40, 290) if k % 4 == 0 else (70, 210)
        b += f"<line x1='{cx+r1*math.cos(a):.1f}' y1='{cy+r1*math.sin(a):.1f}' x2='{cx+r2*math.cos(a):.1f}' y2='{cy+r2*math.sin(a):.1f}'/>"
    b += f"<path d='M{cx} {cy-110} L{cx+16} {cy} L{cx} {cy+110} L{cx-16} {cy} Z M{cx-110} {cy} L{cx} {cy-16} L{cx+110} {cy} L{cx} {cy+16} Z'/>"
    b += "<path d='M20 560 H580 M20 552 V568 M580 552 V568 M30 560 L40 556 M30 560 L40 564 M570 560 L560 556 M570 560 L560 564'/>"
    b += "<path d='M560 20 V540 M552 20 H568 M552 540 H568'/></g>"
    return svg("0 0 600 600", b)


def grain():
    return svg("0 0 220 220", "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' "
               "stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 .32 0 0 0 0 .25 0 0 0 0 .14 0 0 0 .5 0'/></filter>"
               "<rect width='220' height='220' filter='url(#n)'/>")


def skyline(fill="#04081a", bulb="#ffd27a"):
    b = f"<g fill='{fill}'>"
    for x, w, h in ((0, 70, 36), (64, 56, 28), (190, 80, 42), (262, 60, 26), (400, 84, 38)):
        b += f"<path d='M{x} 90 L{x} {90-h*0.45:.0f} L{x+w/2:.0f} {90-h} L{x+w} {90-h*0.45:.0f} L{x+w} 90 Z'/>"
        b += f"<path d='M{x+w/2:.0f} {90-h} V{82-h}' stroke='{fill}' stroke-width='1.5'/>"
    cx, cy, r = 150, 46, 32
    b += f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='none' stroke='{fill}' stroke-width='2.6'/>"
    for k in range(12):
        a = math.radians(k * 30)
        b += f"<line x1='{cx}' y1='{cy}' x2='{cx + r*math.cos(a):.1f}' y2='{cy + r*math.sin(a):.1f}' stroke='{fill}' stroke-width='1.1'/>"
    b += f"<path d='M{cx-13} 90 L{cx} {cy} L{cx+13} 90 Z'/>"
    b += f"<path d='M318 90 V62 Q350 30 382 62 V90 Z'/><path d='M350 38 V26' stroke='{fill}' stroke-width='2'/></g>"
    for k in range(24):
        a = math.radians(k * 15)
        b += f"<circle cx='{cx + r*math.cos(a):.1f}' cy='{cy + r*math.sin(a):.1f}' r='.9' fill='{bulb}'/>"
    return svg("0 0 480 90", b)


def planks():
    """royal-blue painted vertical planks with dark seams and grain, like the Lantern Street stall walls"""
    tones = ("#21438a", "#1d3c7d", "#244892", "#1b3876", "#22428a")
    b = ""
    for i, t in enumerate(tones):
        x = i * 28
        b += f"<rect x='{x}' y='0' width='28' height='240' fill='{t}'/>"
        b += f"<path d='M{x+7} 0 V240 M{x+15} 0 V240 M{x+22} 0 V240' stroke='#ffffff' stroke-opacity='.035' stroke-width='.8'/>"
        b += f"<rect x='{x}' y='0' width='1.3' height='240' fill='#0b1a3c' opacity='.85'/>"
    b += ("<filter id='w'><feTurbulence type='fractalNoise' baseFrequency='.02 .6' numOctaves='2' seed='4'/>"
          "<feColorMatrix values='0 0 0 0 .05 0 0 0 0 .08 0 0 0 0 .2 0 0 0 .45 0'/></filter><rect width='140' height='240' filter='url(#w)'/>")
    return svg("0 0 140 240", b)


def marble():
    """soft cream marble veins (overlay on a cream fill)"""
    return svg("0 0 300 300", "<filter id='m'><feTurbulence type='fractalNoise' baseFrequency='.008 .025' numOctaves='4' seed='9'/>"
               "<feColorMatrix values='0 0 0 0 .45 0 0 0 0 .38 0 0 0 0 .3 0 0 0 -1.6 1.15'/></filter>"
               "<rect width='300' height='300' filter='url(#m)' opacity='.22'/>")


def emblem_tile():
    """the banners' gold moon disc + four-point star, on a royal band"""
    b = (f"<circle cx='15' cy='15' r='6.2' fill='none' stroke='{P['brass']}' stroke-width='1'/><circle cx='15' cy='15' r='4.2' fill='{P['brass']}' opacity='.85'/>"
         f"<path d='M45 7 L46.6 13.4 L53 15 L46.6 16.6 L45 23 L43.4 16.6 L37 15 L43.4 13.4 Z' fill='{P['brass']}'/>")
    return svg("0 0 60 30", b)


def emblem():
    b = (f"<circle cx='50' cy='50' r='46' fill='none' stroke='{P['brass']}' stroke-width='2'/><circle cx='50' cy='50' r='40' fill='none' stroke='{P['brass']}' stroke-width='.8'/>"
         f"<path d='M58 24 A28 28 0 1 0 76 58 A22 22 0 1 1 58 24 Z' fill='{P['brass']}'/>"
         f"<path d='M42 30 L44 38 L52 40 L44 42 L42 50 L40 42 L32 40 L40 38 Z' fill='{P['brasshi']}'/>")
    return svg("0 0 100 100", b)


# ------------------------------------------------------------------ ornament
def deco_corner(rot=0):
    """Art-Deco stepped corner (top-left at rot 0)"""
    b = (f"<g transform='rotate({rot} 20 20)' fill='none' stroke='{P['brass']}' stroke-width='1.3'>"
         "<path d='M2 38 V13 H7 V7 H13 V2 H38'/><path d='M6 38 V17 H11 V11 H17 V6 H38' opacity='.55' stroke-width='.8'/>"
         f"<path d='M12 16 L16 12 L20 16 L16 20 Z' fill='{P['brass']}' stroke='none'/></g>")
    return svg("0 0 40 40", b)


def rule_orn():
    b = (f"<g fill='none' stroke='{P['brass']}' stroke-width='1'><path d='M0 6 H44 M76 6 H120'/>"
         f"<path d='M50 6 L60 0.8 L70 6 L60 11.2 Z' fill='{P['brass']}' fill-opacity='.25'/>"
         f"<circle cx='60' cy='6' r='2' fill='{P['brass']}'/><path d='M44 6 L48 3.5 M44 6 L48 8.5 M76 6 L72 3.5 M76 6 L72 8.5'/></g>")
    return svg("0 0 120 12", b)


def lightstring():
    b = (f"<defs><radialGradient id='g'><stop offset='0' stop-color='#ffd98a' stop-opacity='.75'/>"
         f"<stop offset='.4' stop-color='#ff9a4a' stop-opacity='.22'/><stop offset='1' stop-color='#ff9a4a' stop-opacity='0'/></radialGradient></defs>"
         f"<path d='M0 4 Q45 20 90 4' fill='none' stroke='#1d2238' stroke-width='1'/>")
    for x in (15, 45, 75):
        t = x / 90
        y = 4 + 32 * t * (1 - t)
        b += (f"<circle cx='{x}' cy='{y+6:.1f}' r='11' fill='url(#g)'/><rect x='{x-1.3}' y='{y:.1f}' width='2.6' height='2.6' fill='#2a2a2a'/>"
              f"<ellipse cx='{x}' cy='{y+5.6:.1f}' rx='2.1' ry='3' fill='#fff1c2'/>")
    return svg("0 0 90 32", b)


def gear(col=P["brass"], teeth=14):
    b = f"<g fill='none' stroke='{col}' stroke-width='3'>"
    pts = []
    for k in range(teeth * 2):
        a = math.pi * k / teeth
        r = 92 if k % 2 == 0 else 80
        a1, a2 = a - math.pi / teeth * .42, a + math.pi / teeth * .42
        pts += [(100 + r * math.cos(a1), 100 + r * math.sin(a1)), (100 + r * math.cos(a2), 100 + r * math.sin(a2))]
    b += "<path d='M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z'/>"
    b += "<circle cx='100' cy='100' r='60'/><circle cx='100' cy='100' r='18'/>"
    for k in range(6):
        a = math.radians(k * 60)
        b += f"<line x1='{100+18*math.cos(a):.1f}' y1='{100+18*math.sin(a):.1f}' x2='{100+60*math.cos(a):.1f}' y2='{100+60*math.sin(a):.1f}'/>"
    return svg("0 0 200 200", b + "</g>")


def dial():
    """moon-dial arc (precision instrument) 104 x 40; centre (52, 54), radius 44, -62..62 deg from vertical"""
    cx, cy, r = 52, 54, 44
    a0, a1 = math.radians(-62), math.radians(62)
    b = (f"<path d='M{cx+r*math.sin(a0):.2f} {cy-r*math.cos(a0):.2f} A{r} {r} 0 0 1 {cx+r*math.sin(a1):.2f} {cy-r*math.cos(a1):.2f}' "
         f"fill='none' stroke='{P['brass']}' stroke-width='.9'/>")
    for k in range(21):
        a = math.radians(-62 + k * 6.2)
        ln = 5 if k % 5 == 0 else 2.6
        b += (f"<line x1='{cx+(r+1)*math.sin(a):.2f}' y1='{cy-(r+1)*math.cos(a):.2f}' x2='{cx+(r+1+ln)*math.sin(a):.2f}' "
              f"y2='{cy-(r+1+ln)*math.cos(a):.2f}' stroke='{P['brass']}' stroke-width='{1 if k % 5 == 0 else .6}'/>")
    b += f"<path d='M86 37 H102' stroke='{P['ember']}' stroke-width='1.2'/>"
    return svg("0 0 104 40", b)


def torn(col="#000"):
    return svg("0 0 24 8", f"<path d='M0 8 L0 3 L3 1.2 L6 4 L9 .6 L12 3.6 L15 1 L18 4.2 L21 1.4 L24 3 L24 8 Z' fill='{col}'/>")


# ------------------------------------------------------------------ icons: monoline technical (stroke only), 24 x 24
S = "fill='none' stroke='{c}' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'"
ICONS = {
    "thermo": "<rect x='9.5' y='2' width='5' height='14' rx='2.5' {s}/><circle cx='12' cy='19' r='3.4' {s}/><path d='M16 6 H18 M16 9 H18 M16 12 H18' {s}/>",
    "eye": "<path d='M2 12 Q12 3.5 22 12 Q12 20.5 2 12 Z' {s}/><circle cx='12' cy='12' r='3.2' {s}/>",
    "key": "<circle cx='7' cy='12' r='4.2' {s}/><path d='M11.2 12 H22 M18 12 V15.5 M21 12 V14.5' {s}/>",
    "pencil": "<path d='M4 20 L5 15.5 L16.5 4 L20 7.5 L8.5 19 Z M14.5 6 L18 9.5 M4 20 L8.5 19' {s}/>",
    "magnifier": "<circle cx='10' cy='10' r='6.5' {s}/><path d='M15 15 L21.5 21.5' {s}/>",
    "compass": "<circle cx='12' cy='4.5' r='2' {s}/><path d='M11 6.4 L5 21 M13 6.4 L19 21 M7.4 15 Q12 17.5 16.6 15' {s}/>",
    "gear": "<circle cx='12' cy='12' r='3' {s}/><path d='M12 2.5 V5.5 M12 18.5 V21.5 M2.5 12 H5.5 M18.5 12 H21.5 M5.3 5.3 L7.4 7.4 M16.6 16.6 L18.7 18.7 M5.3 18.7 L7.4 16.6 M16.6 7.4 L18.7 5.3' {s}/><circle cx='12' cy='12' r='6.5' {s}/>",
    "crate": "<path d='M12 2.5 L21 7 V17 L12 21.5 L3 17 V7 Z M3 7 L12 11.5 L21 7 M12 11.5 V21.5 M7.5 4.8 L16.5 9.3' {s}/>",
    "moon": "<path d='M15 3 A9 9 0 1 0 21 15 A7 7 0 1 1 15 3 Z' {s}/>",
    "spark": "<path d='M12 2 L13.6 10.4 L22 12 L13.6 13.6 L12 22 L10.4 13.6 L2 12 L10.4 10.4 Z' {s}/>",
    "city": "<path d='M2 21 H22 M4 21 V11 H8 V21 M8 21 V6 H13 V21 M13 21 V9 H17 V21 M17 21 V13 H20 V21 M10 9 V9.5 M10 12 V12.5 M15 12 V12.5' {s}/>",
    "snow": "<path d='M12 2 V22 M3.3 7 L20.7 17 M3.3 17 L20.7 7 M9.5 3.8 L12 6 L14.5 3.8 M9.5 20.2 L12 18 L14.5 20.2' {s}/>",
    "sun": "<circle cx='12' cy='12' r='4.5' {s}/><path d='M12 2 V4.5 M12 19.5 V22 M2 12 H4.5 M19.5 12 H22 M4.9 4.9 L6.7 6.7 M17.3 17.3 L19.1 19.1 M4.9 19.1 L6.7 17.3 M17.3 6.7 L19.1 4.9' {s}/>",
    "ticket": "<path d='M2 7 H22 V10 A2 2 0 0 0 22 14 V17 H2 V14 A2 2 0 0 0 2 10 Z M8 7.5 V16.5' {s}/>",
    "lantern": "<path d='M12 1.5 V4 M9 4 H15 L16.5 7 V16 L15 19 H9 L7.5 16 V7 Z M7.5 7 H16.5 M7.5 16 H16.5 M12 19 V22' {s}/>",
    "target": "<circle cx='12' cy='12' r='9' {s}/><circle cx='12' cy='12' r='4.5' {s}/><path d='M12 1 V5 M12 19 V23 M1 12 H5 M19 12 H23' {s}/>",
}


def icon(name, c):
    return uri(svg("0 0 24 24", ICONS[name].replace("{s}", S.replace("{c}", c))))


def css():
    g = uri(grain())
    out = [f"""/* ChandRush CREATIVE KIT, Art Direction A3 "Lantern Street". GENERATED by kitgen.py: edit kitgen.py, not this file.
   Readers are 11: cool and aspirational, never kiddish. Colours, materials and light come from the location plates.
   How and when to use each piece: ART-DIRECTION.md. Live gallery: kit-gallery-1.html / kit-gallery-2.html (kit-1.png, kit-2.png).
   The kit draws no letters or numbers. Every printed word still comes from the manuscript. */

@font-face {{ font-family: "Cinzel"; src: url("fonts/Cinzel.ttf") format("truetype"); font-weight: 400 900; font-style: normal; }}
@font-face {{ font-family: "Rajdhani"; src: url("fonts/Rajdhani-SemiBold.ttf") format("truetype"); font-weight: 600; font-style: normal; }}
@font-face {{ font-family: "Rajdhani"; src: url("fonts/Rajdhani-Bold.ttf") format("truetype"); font-weight: 700; font-style: normal; }}
@font-face {{ font-family: "Caveat"; src: url("fonts/Caveat.ttf") format("truetype"); font-weight: 400 700; font-style: normal; }}

.page {{
  --void: {P['void']}; --night: {P['night']}; --indigo: {P['indigo']}; --steel: {P['steel']}; --brass: {P['brass']};
  --brasshi: {P['brasshi']}; --brasslo: {P['brasslo']}; --cyan: {P['cyan']}; --teal: {P['teal']}; --ember: {P['ember']};
  --crimson: {P['crimson']}; --ice: {P['ice']}; --ivory: {P['ivory']}; --parch: {P['parch']}; --inkc: {P['ink']}; --kraft: {P['kraft']};
  --epic: "Cinzel", "Source Serif 4", serif; --tech: "Rajdhani", "Source Sans 3", sans-serif; --hand: "Caveat", "Source Serif 4", serif;
  --lift: 0 1pt 0 rgba(0,0,0,.25), 0 8pt 22pt rgba(0,0,0,.45);
  --royal: {P['royal']}; --copper: {P['copper']}; --stone: {P['stone']};
  --metal: linear-gradient(180deg, #fbe2a8 0%, #e3b060 32%, #b3722f 64%, #6e4518 88%, #c98f45 100%);
  --lacquer: linear-gradient(165deg, #2a519a 0%, #1d3c7d 45%, #132b62 100%);
}}

/* base.css classes (.eq, .h-sub, .note) read --ink/--head/--muted: light objects reset them to dark ink, dark stages to ivory */
.stage-parchment, .obj, .sheet, .mcard, .ledger, .ticket, .tag, .flap, .letter, .capnote, .say {{
  --ink: var(--inkc); --head: var(--inkc); --muted: #4a5266; --cap: var(--ivory); --cap-ink: var(--inkc); }}
.plaque {{ --ink: #2e2108; --head: #2e2108; }}
.stage-cinema, .stage-jali, .stage-planks, .stage-blueprint, .stage-backdrop, .slate, .sheet.glass {{ --ink: var(--ivory); --head: var(--brasshi); --muted: #b7c0d6; }}

/* ---------------------------------------------------------------- 1. STAGES (class on .page) */
.stage-cinema {{ color: var(--ivory); background:
  {uri(stars(3))} 0 0 / 220pt 220pt, {uri(stars(17, 14))} 90pt 60pt / 300pt 300pt,
  radial-gradient(ellipse 40% 36% at 88% 4%, rgba(166,198,245,.24), transparent 70%),
  radial-gradient(ellipse 34% 30% at 6% 30%, rgba(247,198,132,.16), transparent 70%),
  radial-gradient(ellipse 60% 40% at 50% 100%, rgba(247,198,132,.14), transparent 70%),
  linear-gradient(180deg, #13295e 0%, #0e1f48 55%, #0c1933 100%); }}
/* royal-blue lacquered planks, the Lantern Street stall wall (stage-jali kept as an alias) */
.stage-planks, .stage-jali {{ color: var(--ivory); background:
  radial-gradient(ellipse 45% 40% at 12% 8%, rgba(247,198,132,.30), transparent 70%),
  radial-gradient(ellipse 40% 35% at 92% 10%, rgba(166,198,245,.14), transparent 70%),
  radial-gradient(ellipse 120% 90% at 50% 45%, transparent 55%, rgba(8,16,40,.55) 100%),
  {uri(planks())} 0 0 / 120pt 206pt; }}
/* the page's own location plate, softened: <img class="backdrop" src="assets/img/BACKDROP.jpg"> (pagekit.py backdrop) */
.stage-backdrop {{ color: var(--ivory); background: #0c1933; }}
.backdrop {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; pointer-events: none; }}
.backdrop-veil {{ position: absolute; inset: 0; pointer-events: none;
  background: radial-gradient(ellipse 110% 90% at 50% 45%, rgba(12,25,51,.25), rgba(8,16,40,.7)); }}
.stage-blueprint {{ color: var(--ivory); background: {uri(blueprint(P['brass']))} right -80pt top -90pt / 560pt 560pt no-repeat,
  linear-gradient(160deg, #1d3c7d, #12285e 60%, #0c1933); }}
.stage-parchment {{ color: var(--inkc); background: {uri(marble())} 0 0 / 300pt 300pt, {g} 0 0 / 220pt 220pt,
  radial-gradient(ellipse 85% 80% at 50% 45%, #f3ead8 50%, #dcc9a6 100%); }}

.grain {{ background-image: {g}; background-size: 220pt 220pt; }}
.glow {{ position: absolute; border-radius: 50%; pointer-events: none;
  background: radial-gradient(circle, rgba(247,198,132,.45) 0%, rgba(247,198,132,.14) 40%, transparent 70%); }}
.glow.cyan, .glow.moon {{ background: radial-gradient(circle, rgba(166,198,245,.40) 0%, rgba(166,198,245,.12) 40%, transparent 70%); }}
.skyline {{ position: absolute; left: 0; right: 0; bottom: 0; height: 64pt; pointer-events: none;
  background: {uri(skyline())} 0 100% / auto 100% repeat-x, linear-gradient(180deg, transparent 20%, rgba(247,198,132,.14) 100%); }}
.watermark {{ position: absolute; pointer-events: none; opacity: var(--wm, .08); background: center / contain no-repeat; }}
.watermark.gear {{ background-image: {uri(gear())}; }}
.watermark.compass {{ background-image: {uri(blueprint(P['brass']))}; }}
.watermark.emblem, .emblem {{ background-image: {uri(emblem())}; }}
.emblem {{ position: absolute; width: 40pt; height: 40pt; background-size: contain; background-repeat: no-repeat; pointer-events: none; }}

/* ---------------------------------------------------------------- 2. ORNAMENT (pick one or two per page; all wordless) */
/* Art-Deco page frame: <div class="deco-frame"></div> (inset 12pt; set left/top/right/bottom to change) */
.deco-frame {{ position: absolute; inset: 12pt; pointer-events: none; border: .7pt solid rgba(201,160,70,.55);
  background: {uri(deco_corner(0))} left -1pt top -1pt / 34pt no-repeat, {uri(deco_corner(90))} right -1pt top -1pt / 34pt no-repeat,
              {uri(deco_corner(180))} right -1pt bottom -1pt / 34pt no-repeat, {uri(deco_corner(270))} left -1pt bottom -1pt / 34pt no-repeat; }}
.deco-frame::before {{ content: ""; position: absolute; inset: 3.5pt; border: .4pt solid rgba(201,160,70,.35); }}
/* HUD corner brackets for any object: put <i class="hud"></i> inside it (.cyan / .ember variants) */
.hud {{ position: absolute; inset: -5pt; pointer-events: none; --hc: var(--brass);
  background: linear-gradient(var(--hc),var(--hc)) left top / 13pt 2.4pt no-repeat, linear-gradient(var(--hc),var(--hc)) left top / 2.4pt 13pt no-repeat,
    linear-gradient(var(--hc),var(--hc)) right top / 13pt 2.4pt no-repeat, linear-gradient(var(--hc),var(--hc)) right top / 2.4pt 13pt no-repeat,
    linear-gradient(var(--hc),var(--hc)) left bottom / 13pt 2.4pt no-repeat, linear-gradient(var(--hc),var(--hc)) left bottom / 2.4pt 13pt no-repeat,
    linear-gradient(var(--hc),var(--hc)) right bottom / 13pt 2.4pt no-repeat, linear-gradient(var(--hc),var(--hc)) right bottom / 2.4pt 13pt no-repeat; }}
.hud.cyan, .hud.moon {{ --hc: var(--ice); }} .hud.ember {{ --hc: var(--ember); }}
/* brass photo-corner mounts for any object: <i class="mounts"></i> inside it */
.mounts {{ position: absolute; inset: -3pt; pointer-events: none;
  background: linear-gradient(135deg, var(--brass) 50%, transparent 50%) left top / 14pt 14pt no-repeat,
    linear-gradient(225deg, var(--brass) 50%, transparent 50%) right top / 14pt 14pt no-repeat,
    linear-gradient(315deg, var(--brass) 50%, transparent 50%) right bottom / 14pt 14pt no-repeat,
    linear-gradient(45deg, var(--brass) 50%, transparent 50%) left bottom / 14pt 14pt no-repeat; }}
/* royal lacquer band with the banners' gold moon-and-star emblems (jali-band kept as an alias) */
.trim-band, .jali-band {{ position: absolute; background: {uri(emblem_tile())} 0 50% / 40pt 20pt repeat-x, var(--lacquer);
  border-top: 1.2pt solid var(--brass); border-bottom: 1.2pt solid var(--brass); box-shadow: inset 0 3pt 0 -1.8pt rgba(247,217,160,.5), 0 3pt 8pt rgba(0,0,0,.4); }}
.lightstring {{ position: absolute; height: 30pt; background: {uri(lightstring())} 0 0 / 84pt 30pt repeat-x; pointer-events: none; }}
.rule-orn {{ display: block; height: 12pt; margin: 6pt 0; background: {uri(rule_orn())} center / auto 100% no-repeat; }}

/* ---------------------------------------------------------------- 3. TYPE ROLES (body text stays Source Sans 3 / Serif 4 at 14/18) */
.h-title {{ font: 700 34pt/1.05 var(--epic); letter-spacing: .035em; color: var(--title-c, var(--brasshi)); margin: 0;
  text-shadow: 0 0 14pt rgba(243,213,138,.25), 0 2pt 0 rgba(0,0,0,.35); }}
.h-title.ink {{ --title-c: var(--inkc); text-shadow: none; }}
.h-title .alt {{ color: #cfe0fa; text-shadow: 0 0 14pt rgba(166,198,245,.4), 0 2pt 0 rgba(0,0,0,.35); }}
/* sub-heads ("Example 11", "Now you try", "Check your method"): technical, tracked caps */
.label {{ display: inline-flex; align-items: center; gap: 7pt; font: 700 18pt/1 var(--tech); letter-spacing: .09em; text-transform: uppercase;
  color: var(--label-c, var(--brasslo)); margin: 0 0 7pt; }}
.label .ico {{ width: 18pt; height: 18pt; }}
.label.on-dark {{ --label-c: var(--brasshi); }} .label.cyan, .label.royal {{ --label-c: #1f4f9a; }} .label.ember {{ --label-c: #9b4a1c; }}
.hand {{ font: 600 19pt/21pt var(--hand); }}
.tech {{ font-family: var(--tech); }}

/* etched brass nameplate for a title or heading */
.nameplate {{ position: absolute; padding: 9pt 26pt 7pt; border-radius: 3pt; background: var(--metal); color: #2e2108;
  font: 700 22pt/1.05 var(--epic); letter-spacing: .05em; text-align: center; text-shadow: 0 1pt 0 rgba(255,240,200,.55);
  box-shadow: inset 0 0 0 1.4pt rgba(90,60,10,.55), inset 0 0 0 3pt rgba(255,236,180,.45), var(--lift); }}
.nameplate::before, .nameplate::after {{ content: ""; position: absolute; top: 50%; width: 6pt; height: 6pt; margin-top: -3pt; border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #fff4d0, #7a5718 70%); box-shadow: 0 0 0 .6pt rgba(60,40,5,.5); }}
.nameplate::before {{ left: 8pt; }} .nameplate::after {{ right: 8pt; }}

/* ---------------------------------------------------------------- 4. READING OBJECTS (light fields, dark ink, 14/18 body) */
.obj {{ position: absolute; color: var(--inkc); }}
.lift {{ box-shadow: var(--lift); }}
.tilt-l {{ transform: rotate(-.8deg); }} .tilt-r {{ transform: rotate(.7deg); }}

/* ivory sheet: the default reading field. .glass = dark glass panel (short text only) */
.sheet {{ position: absolute; color: var(--inkc); background: {uri(marble())} 0 0 / 300pt 300pt, {g} 0 0 / 220pt 220pt, var(--sheet-bg, var(--ivory));
  border-radius: 3pt; padding: 14pt 18pt; box-shadow: var(--lift); outline: .6pt solid rgba(201,160,70,.5); outline-offset: -5pt; }}
.sheet.cool {{ --sheet-bg: #e9e6de; }}
/* royal lacquer panel with gold pinstripe (.glass kept as the class name): short text only */
.sheet.glass, .lacquer {{ color: var(--ivory); background: {g} 0 0 / 220pt 220pt, var(--lacquer);
  outline: .8pt solid rgba(208,160,80,.85); outline-offset: -5pt; box-shadow: inset 0 1pt 0 rgba(247,217,160,.25), var(--lift); }}
.torn-b {{ border-bottom-left-radius: 0; border-bottom-right-radius: 0;
  -webkit-mask: linear-gradient(#000,#000) top / 100% calc(100% - 7pt) no-repeat, {uri(torn())} bottom / 22pt 7.5pt repeat-x;
          mask: linear-gradient(#000,#000) top / 100% calc(100% - 7pt) no-repeat, {uri(torn())} bottom / 22pt 7.5pt repeat-x; }}
.shadowed {{ filter: drop-shadow(0 5pt 8pt rgba(0,0,0,.4)); }}   /* on a WRAPPER of masked shapes, short text only */

/* mission file card: questions, briefs. Cut top-right corner + brass inner line. */
.mcard {{ position: absolute; color: var(--inkc); background: {uri(marble())} 0 0 / 300pt 300pt, {g} 0 0 / 220pt 220pt, var(--ivory); padding: 14pt 22pt 14pt 18pt;
  clip-path: polygon(0 0, calc(100% - 20pt) 0, 100% 20pt, 100% 100%, 0 100%); }}
.mcard::before {{ content: ""; position: absolute; inset: 5pt; border: .6pt solid rgba(201,160,70,.7); pointer-events: none;
  clip-path: polygon(0 0, calc(100% - 17pt) 0, 100% 17pt, 100% 100%, 0 100%); }}
.mcard::after {{ content: ""; position: absolute; top: 0; right: 0; width: 20pt; height: 20pt; background: linear-gradient(225deg, transparent 47%, var(--brass) 47% 53%, transparent 53%); }}

/* VIP pass: "Try / Now you try / Pause and think". Royal-blue stub with a brass icon, perforation, brass foil edge.
   <div class="ticket"><i class="stub"><i class="ico i-ticket"></i></i>…</div> */
.ticket {{ position: absolute; color: var(--inkc); padding: 13pt 22pt 13pt 58pt; border-radius: 5pt;
  background: var(--metal) right / 7pt 100% no-repeat,
    linear-gradient(90deg, var(--tk-stub, #16306a) 0 42pt, transparent 42pt), {uri(marble())} 0 0 / 300pt 300pt, {g} 0 0 / 220pt 220pt, var(--ivory);
  -webkit-mask: radial-gradient(circle 6pt at 42pt 0, transparent 97%, #000) top / 100% 51% no-repeat,
                radial-gradient(circle 6pt at 42pt 100%, transparent 97%, #000) bottom / 100% 51% no-repeat;
          mask: radial-gradient(circle 6pt at 42pt 0, transparent 97%, #000) top / 100% 51% no-repeat,
                radial-gradient(circle 6pt at 42pt 100%, transparent 97%, #000) bottom / 100% 51% no-repeat; }}
.ticket::before {{ content: ""; position: absolute; left: 42pt; top: 9pt; bottom: 9pt; border-left: 1.3pt dashed rgba(20,26,46,.35); }}
.ticket > .stub {{ position: absolute; left: 10pt; top: 50%; width: 22pt; height: 22pt; transform: translateY(-50%); }}
.ticket > .stub > .ico {{ width: 22pt; height: 22pt; }}
.ticket.ember {{ --tk-stub: #6e1f2a; }} .ticket.teal {{ --tk-stub: #0c1933; }}

/* cargo tag (kraft card, brass eyelet): shop/stock problems. Draw the twine as SVG. */
.tag {{ position: absolute; color: var(--inkc); background: {g} 0 0 / 220pt 220pt, var(--tg, #e9dcc0); padding: 14pt 20pt 14pt 46pt;
  clip-path: polygon(24pt 0, 100% 0, 100% 100%, 24pt 100%, 0 calc(50% + 20pt), 0 calc(50% - 20pt));
  -webkit-mask: radial-gradient(circle 5pt at 18pt 50%, transparent 96%, #000); mask: radial-gradient(circle 5pt at 18pt 50%, transparent 96%, #000); }}
.tag::after {{ content: ""; position: absolute; left: 10pt; top: calc(50% - 8pt); width: 16pt; height: 16pt; border-radius: 50%;
  border: 2.4pt solid var(--brass); box-shadow: inset 0 0 0 .6pt rgba(60,40,5,.5); }}

/* field notebook (Moleskine-style): worked steps. Dark cover edge, stitched spine, elastic band; optional <i class="bookmark"></i>. */
.ledger {{ position: absolute; color: var(--inkc); padding: 15pt 32pt 13pt 26pt; border-radius: 2pt 4pt 4pt 2pt;
  background: linear-gradient(90deg, transparent calc(100% - 22pt), #0c1933 calc(100% - 22pt) calc(100% - 15pt), transparent calc(100% - 15pt)),
    {g} 0 0 / 220pt 220pt, #f4ecdc;
  box-shadow: -5pt 0 0 0 #16306a, -5pt 3pt 0 0 #0c1933, var(--lift); }}
.ledger::before {{ content: ""; position: absolute; left: 8pt; top: 10pt; bottom: 10pt; border-left: 1pt dashed rgba(20,26,46,.3); }}
.ledger > .bookmark {{ position: absolute; bottom: -18pt; left: 46pt; width: 9pt; height: 26pt; background: var(--crimson);
  clip-path: polygon(0 0, 100% 0, 100% 100%, 50% 78%, 0 100%); }}

/* sealed answer panel: "Check your method / thinking". Tear line, folded corner, brass seal with an eye or key.
   <div class="flap" style="--under:…"><i class="seal"><i class="ico i-eye ink"></i></i>…</div> */
.flap {{ position: absolute; color: var(--inkc); background: {uri(marble())} 0 0 / 300pt 300pt, {g} 0 0 / 220pt 220pt, var(--fl, #ebe3d2); border-radius: 2pt 2pt 4pt 4pt;
  padding: 22pt 18pt 13pt; box-shadow: var(--lift); border-top: 1.6pt dashed rgba(35,77,149,.75); }}
.flap::before {{ content: ""; position: absolute; top: -1.6pt; right: 0; width: 22pt; height: 22pt;
  background: linear-gradient(225deg, var(--under, #0c1933) 0 50%, #d3c3a2 50% 100%); box-shadow: -1.5pt 1.5pt 2pt rgba(0,0,0,.25); }}
.flap > .seal {{ position: absolute; top: -15pt; left: 18pt; width: 28pt; height: 28pt; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  background: radial-gradient(circle at 35% 30%, #fbe7a8, #c9a046 55%, #8a6420); box-shadow: inset 0 0 0 2pt rgba(255,240,200,.45), 0 2pt 4pt rgba(0,0,0,.4); }}
.flap > .seal > .ico {{ width: 16pt; height: 16pt; }}

/* etched brass plate: the one key result */
.plaque {{ position: absolute; color: #2e2108; background: var(--metal); border-radius: 3pt; padding: 10pt 26pt;
  box-shadow: inset 0 0 0 1.4pt rgba(90,60,10,.55), inset 0 0 0 3pt rgba(255,236,180,.45), var(--lift); }}
.plaque::before, .plaque::after {{ content: ""; position: absolute; top: 50%; width: 6pt; height: 6pt; margin-top: -3pt; border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #fff4d0, #7a5718 70%); }}
.plaque::before {{ left: 8pt; }} .plaque::after {{ right: 8pt; }}

/* royal lacquer panel with brass edge: a short rule or readout (light text) */
.slate {{ position: absolute; color: var(--ivory); padding: 12pt 16pt; border-radius: 3pt; background: var(--lacquer);
  border: 1pt solid var(--brass); box-shadow: inset 0 0 0 3pt rgba(12,25,51,.5), inset 0 0 0 3.8pt rgba(208,160,80,.55), 0 0 14pt rgba(166,198,245,.15), var(--lift); }}

/* invitation letter: a narrator's opening. <div class="letter"><i class="mounts"></i><i class="wax"></i>…</div> */
.letter {{ position: absolute; color: var(--inkc); background: {uri(marble())} 0 0 / 300pt 300pt, {g} 0 0 / 220pt 220pt, #f1e8d6; padding: 16pt 22pt;
  font: 400 14pt/18pt var(--serif); box-shadow: var(--lift); }}
.letter > .wax {{ position: absolute; right: 14pt; bottom: -12pt; width: 30pt; height: 30pt; border-radius: 47% 53% 50% 50%;
  background: radial-gradient(circle at 38% 34%, #c8485a, #9b2230 55%, #5e1220); box-shadow: 0 2pt 3pt rgba(0,0,0,.4), inset 0 0 0 3pt rgba(0,0,0,.12); }}
.letter > .wax::after {{ content: ""; position: absolute; inset: 7pt; border-radius: 50%; border: 1.2pt solid rgba(255,220,220,.45); }}

/* story narration caption */
.capnote {{ position: absolute; background: var(--ivory); color: var(--inkc); font: 400 14pt/18pt var(--serif); padding: 8pt 12pt;
  border-radius: 2pt; box-shadow: 0 1pt 0 rgba(0,0,0,.2), 0 4pt 10pt rgba(0,0,0,.35); outline: .5pt solid rgba(201,160,70,.6); outline-offset: -3pt; }}

/* ---------------------------------------------------------------- 5. SPEECH (graphic-novel balloons) */
.say {{ position: absolute; background: var(--say-bg, #f7f1e4); color: var(--inkc); border: 1.2pt solid #10142a; border-radius: 50% / 46%;
  padding: 11pt 20pt; font: 600 14pt/18pt var(--sans); text-align: center; }}
.say > svg.tail {{ position: absolute; width: 22pt; height: 24pt; left: var(--tx, 30%); top: calc(100% - 3pt); overflow: visible;
  transform: rotate(var(--tr, 0deg)); transform-origin: 50% 0; }}
.say > svg.tail.up {{ top: auto; bottom: calc(100% - 3pt); transform: scaleY(-1) rotate(var(--tr, 0deg)); transform-origin: 50% 100%; }}
.say > svg.tail path {{ fill: var(--say-bg, #f7f1e4); stroke: #10142a; stroke-width: 1.2pt; stroke-linejoin: round; }}
.say.aside {{ --say-bg: #efe4d0; font: 600 19pt/21pt var(--hand); border-width: 1pt; }}   /* companion remark to the reader */

/* ---------------------------------------------------------------- 6. ART HOLDERS */
/* jharokha (carved window). Needs the <svg class="defs"> block from kit-gallery-2.html once per page. */
.jharokha {{ position: absolute; }}
.jharokha > img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: var(--fx, 50%) var(--fy, 50%); clip-path: url(#jharokha); }}
.jharokha > svg.rim {{ position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible; }}
.jharokha > svg.rim path {{ fill: none; vector-effect: non-scaling-stroke; }}
.jharokha > .sill {{ position: absolute; left: -8%; right: -8%; bottom: -9pt; height: 12pt; border-radius: 2pt; background: var(--metal); box-shadow: 0 3pt 6pt rgba(0,0,0,.45); }}
.jharokha > .sill::before, .jharokha > .sill::after {{ content: ""; position: absolute; top: 12pt; width: 14pt; height: 13pt;
  background: linear-gradient(#b8893a, #6e4d14); clip-path: polygon(0 0, 100% 0, 60% 100%, 40% 100%); }}
.jharokha > .sill::before {{ left: 14%; }} .jharokha > .sill::after {{ right: 14%; }}
.snap {{ position: absolute; background: #f4f1ea; padding: 7pt 7pt 20pt; box-shadow: 0 4pt 12pt rgba(0,0,0,.5); transform: rotate(var(--r, 2deg)); }}
.snap > img {{ display: block; width: 100%; height: 100%; object-fit: cover; object-position: var(--fx, 50%) var(--fy, 50%); }}
.pop {{ position: absolute; z-index: 5; filter: drop-shadow(0 8pt 10pt rgba(0,0,0,.55)); pointer-events: none; }}
.pop > img {{ width: 100%; height: 100%; object-fit: contain; object-position: var(--fx, 50%) 100%; }}
.frame-panel {{ position: absolute; overflow: hidden; border-radius: 3pt; border: 1.4pt solid var(--brass);
  box-shadow: inset 0 0 0 1.2pt rgba(0,0,0,.5), var(--lift); background: #000; }}
.frame-panel > img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: var(--fx, 50%) var(--fy, 50%); }}
.frame-panel.round {{ border-radius: 50%; }}

/* ---------------------------------------------------------------- 7. FOLIO: moonset dial (book-wide signature)
   <div class="moonclock" style="left:…;top:…;--t:.36"><i class="arc"></i><i class="arm"><b>39</b></i></div>
   --t = page / last page of the chapter (0 = moonrise, 1 = moonset). .light on pale stages. */
.moonclock {{ position: absolute; width: 104pt; height: 40pt; overflow: hidden; pointer-events: none; }}
.moonclock > .arc {{ position: absolute; inset: 0; background: {uri(dial())} 0 0 / 100% 100% no-repeat; }}
.moonclock > .arm {{ position: absolute; left: 51pt; top: 10pt; width: 2pt; height: 44pt; transform-origin: 1pt 44pt;
  transform: rotate(calc(-62deg + var(--t, .5) * 124deg)); }}
.moonclock > .arm > b {{ position: absolute; left: -10pt; top: -10pt; width: 21pt; height: 21pt; border-radius: 50%;
  transform: rotate(calc(62deg - var(--t, .5) * 124deg));
  background: radial-gradient(circle at 30% 64%, rgba(120,120,135,.30) 0 1.8pt, transparent 2.2pt), radial-gradient(circle at 66% 36%, rgba(120,120,135,.26) 0 2.2pt, transparent 2.6pt),
    radial-gradient(circle at 40% 35%, #fbf8ee, #ddd6c3 70%, #b9b19c);
  box-shadow: 0 0 8pt 2pt rgba(166,198,245,.5); font: 700 10.5pt/21pt var(--tech); color: #121a33; text-align: center; }}
.moonclock.light > .arm > b {{ box-shadow: 0 0 0 .8pt rgba(138,100,32,.6), 0 0 6pt 1pt rgba(201,160,70,.35); }}

/* maths colour (V09 job, plate family): royal blue tracks the moving/compared quantity, copper is the second role */
.mt {{ color: #1f4f9a !important; }} .mr {{ color: #a3561c !important; }}
.slate .mt, .sheet.glass .mt, .lacquer .mt, .stage-cinema > .mt {{ color: #cfe0fa !important; }}

/* ---------------------------------------------------------------- 8. ICONS: monoline technical, wordless.
   <i class="ico i-thermo"></i> (brass) · add .cy cyan, .em ember, .iv ivory, .ink dark */
.ico {{ display: inline-block; width: 1.15em; height: 1.15em; vertical-align: -0.2em; background: center / contain no-repeat; }}
"""]
    for name in ICONS:
        out.append(f".ico.i-{name} {{ background-image: {icon(name, P['brass'])}; }}\n")
        out.append(f".ico.i-{name}.ro {{ background-image: {icon(name, '#1f4f9a')}; }} .ico.i-{name}.cu {{ background-image: {icon(name, P['copper'])}; }}\n")
        out.append(f".ico.i-{name}.cy {{ background-image: {icon(name, P['ice'])}; }} .ico.i-{name}.em {{ background-image: {icon(name, P['ember'])}; }} "
                   f".ico.i-{name}.iv {{ background-image: {icon(name, P['ivory'])}; }} .ico.i-{name}.ink {{ background-image: {icon(name, P['ink'])}; }}\n")
    return "".join(out)


if __name__ == "__main__":
    dst = os.path.join(HERE, "kit.css")
    with open(dst, "w", encoding="utf-8") as fh:
        fh.write(css())
    print(dst, os.path.getsize(dst) // 1024, "KB")
