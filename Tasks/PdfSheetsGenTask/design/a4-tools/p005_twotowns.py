# P005 "Two Towns, One Line" (2026-11-25): writes CH01/P005/index.html.
# Grid: 864x648 pt, 36 pt margins, 12 columns (49.5 pt) with 18 pt gutters, 18 pt baseline.
# Hero: graded M01-D04 skyline band (p005_hero.py) + an exact brass thermometer rail, -15..15, 0 at x=432.
T = "/home/akasdh/Desktop/Projects/ComicAgent/Tasks/"
OUT = T + "PdfSheetsGenTask/CH01/P005/index.html"

M = 36                      # outer margin
COLW, GUT = 49.5, 18
def colx(i): return M + i * (COLW + GUT)          # left edge of column i (0..11)
BAND_T, BAND_B = 36, 210    # hero band
X0, U = 432, 24             # thermometer: 0 at the page centre, 24 pt per degree
TUBE_Y = 214                # tube centre: the band's bottom rail
READ_T, READ_B = 270, 612   # reading area (16th..34th baseline)
def tx(v): return X0 + v * U

# ---------- thermometer rail ----------
ticks = []
for v in range(-15, 16):
    x = tx(v)
    big = v % 5 == 0
    ticks.append(f'<path d="M{x} {TUBE_Y + 9} V{TUBE_Y + (19 if big else 14)}" stroke="#2a2418" stroke-width="{1 if big else .55}"/>')
labels = []
for v in range(-15, 16, 5):
    s = ("−" + str(-v)) if v < 0 else str(v)
    w = 700 if v == 0 else 600
    labels.append(f'<text x="{tx(v)}" y="{TUBE_Y + 34}" text-anchor="middle" font-weight="{w}">{s}</text>')

# rime on the cold half of the tube: fine hairlines from the left cap to 0
import random
random.seed(5)
rime = []
x = tx(-15) - 6
while x < X0 - 6:
    y0 = TUBE_Y + random.choice([-7.2, 7.2])
    l = random.uniform(1.5, 3.2) * (1 - (x - tx(-15)) / (X0 - tx(-15))) + .6
    dy = -l if y0 > TUBE_Y else l
    rime.append(f"M{x:.1f} {y0:.1f} l{random.uniform(-1.5, 1.5):.1f} {dy * .6:.1f} m0 0 l{random.uniform(.8, 2):.1f} {dy * .3:.1f}")
    x += random.uniform(3.5, 9)

# answer number line, -12..12 in 228 pt (9 pt per unit)
AU, AX0 = 9, 6
def ax(v): return AX0 + (v + 12) * AU
anl_ticks = "".join(f'<path d="M{ax(v)} {33 if v == 0 else 35} V{47 if v == 0 else 45}" stroke="#1d2433" stroke-width="{1 if v == 0 else .55}"/>' for v in range(-12, 13))

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>ChandRush CH01 P005</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="assets/base.css">
<link rel="stylesheet" href="assets/kit.css">
<style>
  /* P005 "Two Towns, One Line": lesson opener on cream. Grid 36 pt margins, 12 x 49.5 pt columns, 18 pt gutters, 18 pt baseline. */
  .page.towns {{ background: #F7F1E3; color: #1d2433; font-family: "Source Sans 3", sans-serif; font-size: 14pt; line-height: 18pt; }}
  .towns .blk {{ position: absolute; }}
  .towns p {{ margin: 0 0 9pt; font-size: 14pt; line-height: 18pt; color: #1d2433; orphans: 2; widows: 2; }}
  .towns .mt {{ color: #1F6F6B; font-weight: 700; }}
  .towns .mr {{ color: #B5603A; font-weight: 700; }}
  .nw {{ white-space: nowrap; }}
  i.pl {{ font-style: normal; }}
  .rh {{ font-family: "Source Sans 3", sans-serif; font-weight: 600; font-size: 10pt; line-height: 12pt; letter-spacing: 1.6pt;
        font-variant-caps: all-small-caps; color: #7a5a2e; white-space: nowrap; }}
  .sh {{ font-family: "Source Sans 3", sans-serif; font-weight: 600; color: #121a33; font-size: 18pt; line-height: 22pt;
        margin: 0 0 5pt; display: flex; align-items: center; white-space: nowrap; }}
  .sh::after {{ content: ""; display: block; flex: 1; height: 0; border-top: .6pt solid #b3722f; margin-left: 10pt; opacity: .8; }}
  .cap.welcome {{ position: static; display: block; width: auto; background: #FFFDF6; border: .6pt solid #b3722f; padding: 6pt 9pt 7pt; box-sizing: border-box; margin: 0 0 18pt;
         font-family: "Source Serif 4", serif; font-weight: 400; font-size: 14pt; line-height: 18pt; color: #1d2433;
         box-shadow: 0 1.5pt 4pt rgba(91, 74, 46, .20); break-inside: avoid; }}
  .flow {{ column-count: 2; column-gap: 18pt; column-fill: auto; }}
  .pause {{ background: #E6EDF1; border-left: 2pt solid #5f8fa0; padding: 8pt 10pt 9pt; box-sizing: border-box; break-inside: avoid;
           margin-top: 14pt; }}
  .pause p {{ margin: 0; }}
  .pause b {{ font-weight: 600; color: #1d3f4f; }}
  .qhead {{ break-inside: avoid; margin-top: 14pt; }}
  .ans {{ background: #EFE6D2; padding: 10pt 12pt 12pt; box-sizing: border-box; border-top: 1.1pt solid #b3722f;
         box-shadow: inset 0 .6pt 0 #f3d58f; display: flex; flex-direction: column; }}
  .ans p {{ margin: 0 0 6pt; }}
  .ans .sh {{ margin-bottom: 8pt; }}
  .eq {{ font-family: "Source Sans 3", sans-serif; font-size: 30pt; line-height: 36pt; font-weight: 600; color: #1d2433;
        white-space: nowrap; margin: 10pt 0 8pt; }}
  .eq .op {{ font-weight: 400; color: #1d2433; }}
  .plq {{ position: absolute; width: 76pt; height: 30pt; display: flex; align-items: center; justify-content: center;
         font-family: "Source Sans 3", sans-serif; font-weight: 700; font-size: 17pt; line-height: 20pt; letter-spacing: .2pt; z-index: 6; }}
  .plq.cold {{ color: #F3F8FA; }}
  .plq.warm {{ color: #FFF6E6; }}
  .fol {{ font-family: "Source Sans 3", sans-serif; font-weight: 600; font-size: 11pt; line-height: 13pt; color: #1d2433; letter-spacing: .4pt; }}
  .hero {{ position: absolute; left: {M}pt; top: {BAND_T}pt; width: 792pt; height: {BAND_B - BAND_T}pt; overflow: hidden;
          box-shadow: 0 2pt 7pt rgba(40, 30, 15, .28); z-index: 1; }}
  .hero img {{ display: block; width: 100%; height: 100%; }}
  .hero::after {{ content: ""; position: absolute; inset: 0; border: 1pt solid #b3722f; box-shadow: inset 0 0 0 1.6pt rgba(12, 25, 51, .55), inset 0 0 26pt rgba(8, 16, 34, .35); }}
  .ahana {{ position: absolute; display: block; z-index: 3; filter: drop-shadow(0 1.5pt 3pt rgba(8, 16, 34, .45)); }}
  .nl {{ display: block; overflow: visible; margin: 4pt 0 14pt; }}
</style>
</head>
<body>
<div class="page towns" id="page" data-chapter="CH01" data-page="P005">

<!-- ========== frame: a brass hairline 14 pt inside the trim, broken at the folio; quiet corner rivets ========== -->
<svg class="blk" style="left:0; top:0; width:864pt; height:648pt; z-index:0" viewBox="0 0 864 648" aria-hidden="true">
  <defs>
    <radialGradient id="fMoon" cx=".38" cy=".35" r=".7"><stop offset="0" stop-color="#fff6da"/><stop offset=".6" stop-color="#f1d79a"/><stop offset="1" stop-color="#c99a4c"/></radialGradient>
  </defs>
  <path d="M410 634 H14 V14 H850 V634 H454" fill="none" stroke="#b3722f" stroke-width=".75"/>
  <path d="M410 631.6 H16.4 V16.4 H847.6 V631.6 H454" fill="none" stroke="#b3722f" stroke-width=".3" stroke-opacity=".55"/>
  <g fill="#b3722f"><circle cx="14" cy="14" r="2.1"/><circle cx="850" cy="14" r="2.1"/><circle cx="14" cy="634" r="2.1"/><circle cx="850" cy="634" r="2.1"/></g>
  <g fill="#f3d58f"><circle cx="13.4" cy="13.4" r=".7"/><circle cx="849.4" cy="13.4" r=".7"/><circle cx="13.4" cy="633.4" r=".7"/><circle cx="849.4" cy="633.4" r=".7"/></g>
  <!-- moonclock folio: lit fraction 5/107 (waxing, lit on the right), brass ring -->
  <circle cx="424" cy="630" r="8" fill="#1b2a44" stroke="#b3722f" stroke-width=".9"/>
  <circle cx="424" cy="630" r="5.4" fill="#2c3c58"/>
  <path d="M424 624.6 A5.4 5.4 0 0 1 424 635.4 A{5.4 * (1 - 2 * 5 / 107):.3f} 5.4 0 0 0 424 624.6 Z" fill="url(#fMoon)"/>
</svg>
<div class="blk fol" style="left:436pt; top:623.5pt">5</div>

<!-- running head (chapter level, from pages.json book + chapter_label) -->
<div class="blk rh" style="right:{M}pt; top:19pt">CHAPTER 01 · NUMBERS · PG 005</div>

<!-- ========== HERO: two towns, one skyline (M01-D04, cold left / warm right, graded in PIL) ========== -->
<div class="hero"><img src="assets/img/HERO.jpg" alt=""></div>

<!-- Ahana stands on the zero line, between the two towns; her head breaks the band's top edge -->
<img class="ahana" src="assets/img/AHANA.png" alt="" style="left:332pt; top:22pt; width:177pt; height:200pt">

<!-- ========== the brass thermometer rail, -15..15 (24 pt per degree, 0 at x=432) ========== -->
<svg class="blk" style="left:0; top:0; width:864pt; height:648pt; z-index:4" viewBox="0 0 864 648" aria-hidden="true">
  <defs>
    <linearGradient id="gTube" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffffff" stop-opacity=".95"/><stop offset=".22" stop-color="#eef3f8"/>
      <stop offset=".55" stop-color="#d4dde7"/><stop offset="1" stop-color="#9aabbf"/></linearGradient>
    <linearGradient id="gTemp" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#a6c6f5" stop-opacity=".55"/><stop offset=".46" stop-color="#cfe0fa" stop-opacity=".25"/>
      <stop offset=".54" stop-color="#f7c684" stop-opacity=".25"/><stop offset="1" stop-color="#f7c684" stop-opacity=".6"/></linearGradient>
    <linearGradient id="gBrassV" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f3d58f"/><stop offset=".35" stop-color="#d6a64e"/><stop offset=".7" stop-color="#b3722f"/><stop offset="1" stop-color="#6e4318"/></linearGradient>
    <radialGradient id="gBulb" cx=".36" cy=".34" r=".72">
      <stop offset="0" stop-color="#ffffff"/><stop offset=".3" stop-color="#dfe9f4"/><stop offset=".78" stop-color="#9fb3cc"/><stop offset="1" stop-color="#5d7290"/></radialGradient>
    <linearGradient id="gTeal" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2f8a85"/><stop offset=".55" stop-color="#1F6F6B"/><stop offset="1" stop-color="#134846"/></linearGradient>
    <linearGradient id="gTerra" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#cf7a50"/><stop offset=".55" stop-color="#B5603A"/><stop offset="1" stop-color="#7f3d1f"/></linearGradient>
    <linearGradient id="gRime" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#ffffff" stop-opacity=".7"/><stop offset=".6" stop-color="#ffffff" stop-opacity=".25"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient>
    <filter id="fs" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="1.6"/></filter>
  </defs>

  <!-- cream bed under the rail (keeps the labels on paper), and the rail's soft shadow -->
  <rect x="{M}" y="{TUBE_Y + 8}" width="792" height="34" fill="#F7F1E3"/>
  <rect x="{tx(-15) - 14}" y="{TUBE_Y - 4}" width="{tx(15) - tx(-15) + 34}" height="14" rx="7" fill="#3b2a12" fill-opacity=".28" filter="url(#fs)"/>

  <!-- glass tube with a cold-to-warm tint, brass end caps, the bulb at the cold end -->
  <rect x="{tx(-15) - 8}" y="{TUBE_Y - 7.5}" width="{tx(15) - tx(-15) + 16}" height="15" rx="7.5" fill="url(#gTube)" stroke="#6b7a8c" stroke-width=".6"/>
  <rect x="{tx(-15) - 8}" y="{TUBE_Y - 7.5}" width="{tx(15) - tx(-15) + 16}" height="15" rx="7.5" fill="url(#gTemp)"/>
  <path d="M{tx(-15)} {TUBE_Y - 4} H{tx(15)}" stroke="#ffffff" stroke-width="1.4" stroke-opacity=".9" stroke-linecap="round"/>
  <!-- frost: a pale rime film on the cold half of the glass, fading out at 0 -->
  <rect x="{tx(-15) - 8}" y="{TUBE_Y - 7.5}" width="{X0 - tx(-15) + 8}" height="15" rx="7.5" fill="url(#gRime)"/>
  <!-- left: bulb + collar -->
  <rect x="{tx(-15) - 22}" y="{TUBE_Y - 9.5}" width="12" height="19" rx="2" fill="url(#gBrassV)" stroke="#5a3510" stroke-width=".5"/>
  <circle cx="{tx(-15) - 34}" cy="{TUBE_Y}" r="12" fill="url(#gBulb)" stroke="#5d7290" stroke-width=".6"/>
  <ellipse cx="{tx(-15) - 38}" cy="{TUBE_Y - 4.5}" rx="3.4" ry="2.2" fill="#ffffff" fill-opacity=".9"/>
  <!-- right: collar + finial -->
  <rect x="{tx(15) + 10}" y="{TUBE_Y - 9.5}" width="12" height="19" rx="2" fill="url(#gBrassV)" stroke="#5a3510" stroke-width=".5"/>
  <path d="M{tx(15) + 22} {TUBE_Y - 5} L{tx(15) + 31} {TUBE_Y - 2.5} V{TUBE_Y + 2.5} L{tx(15) + 22} {TUBE_Y + 5} Z" fill="#b3722f" stroke="#5a3510" stroke-width=".5"/>
  <circle cx="{tx(15) + 33.5}" cy="{TUBE_Y}" r="3" fill="#d6a64e" stroke="#5a3510" stroke-width=".5"/>

  <!-- engraved scale under the tube: every 1, longer every 5 -->
  <g>{''.join(ticks)}</g>
  <g font-family="Source Sans 3" font-size="14" fill="#1d2433">{''.join(labels)}</g>
  <!-- zero: a silver moonline mark where the two towns meet -->
  <path d="M{X0} {TUBE_Y - 7.5} V{TUBE_Y + 7.5}" stroke="#7f93ad" stroke-width="1.2"/>
  <path d="M{X0 - .6} {TUBE_Y - 7.5} V{TUBE_Y + 7.5}" stroke="#ffffff" stroke-width=".4"/>

  <!-- marker posts and plaques: -12 (Sarah, teal) and 12 (Sam, terracotta) -->
  <g>
    <path d="M{tx(-12)} {TUBE_Y - 8} V{TUBE_Y - 30}" stroke="#b3722f" stroke-width="2"/>
    <path d="M{tx(-12) - .6} {TUBE_Y - 8} V{TUBE_Y - 30}" stroke="#f3d58f" stroke-width=".5"/>
    <rect x="{tx(-12) - 6}" y="{TUBE_Y - 9.5}" width="12" height="19" rx="2" fill="#1F6F6B" stroke="#0f3f3c" stroke-width=".6"/>
    <path d="M{tx(-12)} {TUBE_Y - 9.5} V{TUBE_Y + 9.5}" stroke="#F3F8FA" stroke-width="1"/>
    <rect x="{tx(-12) - 38}" y="{TUBE_Y - 64 + 1.5}" width="76" height="32" rx="3" fill="#0c1933" fill-opacity=".35" filter="url(#fs)"/>
    <rect x="{tx(-12) - 38}" y="{TUBE_Y - 64}" width="76" height="32" rx="3" fill="url(#gTeal)" stroke="#d6a64e" stroke-width="1.6"/>
    <rect x="{tx(-12) - 35.5}" y="{TUBE_Y - 61.5}" width="71" height="27" rx="2" fill="none" stroke="#cfe0fa" stroke-width=".5" stroke-opacity=".7"/>
  </g>
  <g>
    <path d="M{tx(12)} {TUBE_Y - 8} V{TUBE_Y - 30}" stroke="#b3722f" stroke-width="2"/>
    <path d="M{tx(12) - .6} {TUBE_Y - 8} V{TUBE_Y - 30}" stroke="#f3d58f" stroke-width=".5"/>
    <rect x="{tx(12) - 6}" y="{TUBE_Y - 9.5}" width="12" height="19" rx="2" fill="#B5603A" stroke="#6e3216" stroke-width=".6"/>
    <path d="M{tx(12)} {TUBE_Y - 9.5} V{TUBE_Y + 9.5}" stroke="#FFF6E6" stroke-width="1"/>
    <rect x="{tx(12) - 38}" y="{TUBE_Y - 64 + 1.5}" width="76" height="32" rx="3" fill="#0c1933" fill-opacity=".35" filter="url(#fs)"/>
    <rect x="{tx(12) - 38}" y="{TUBE_Y - 64}" width="76" height="32" rx="3" fill="url(#gTerra)" stroke="#d6a64e" stroke-width="1.6"/>
    <rect x="{tx(12) - 35.5}" y="{TUBE_Y - 61.5}" width="71" height="27" rx="2" fill="none" stroke="#f7c684" stroke-width=".5" stroke-opacity=".7"/>
  </g>
</svg>
<div class="plq cold" style="left:{tx(-12) - 38}pt; top:{TUBE_Y - 63}pt">−12°C</div>
<div class="plq warm" style="left:{tx(12) - 38}pt; top:{TUBE_Y - 63}pt">12°C</div>

<!-- ========== reading: columns 1-2 flow (welcome, intro, question, pause) ========== -->
<div class="blk flow" style="left:{M}pt; top:{READ_T}pt; width:{colx(8) - GUT - M}pt; height:{READ_B - READ_T}pt">
  <div class="cap welcome">Before we choose the lift’s movements, let’s get to know the numbers on its strip. You’re part of the crew too, and you can take your time. The clock belongs to the adventure. You can pause, reread or come back tomorrow without making ChandRush less safe.</div>
  <p>Why is <i class="pl" data-math="−12 < 12"><b class="mt nw">−12°C</b> colder than <b class="mr nw">12°C</b></i>? We’ll start with numbers below zero, then explore equal groups, quick division checks, squares and cubes. Each idea will help you choose a calculation and understand why it works.</p>
  <p style="margin:0">We’ll work through this chapter together. Keep a pencil nearby: when you reach a Try or Practice question, cover the working underneath and have a go. Then uncover it and compare the steps, not only the final number.</p>
  <div class="qhead">
    <div class="sh">Numbers below zero</div>
    <p style="margin:0">Sam’s town is at <b class="mr nw">12°C</b>. Sarah’s town is at <b class="mt nw">−12°C</b>. Both temperatures contain 12, but Sarah will certainly want the warmer coat! What difference does that little minus sign make?</p>
  </div>
  <div class="pause"><p><b>Pause and think.</b> Why might Sam feel comfortable while Sarah feels very cold? If Sarah’s temperature rises by 10°C, will her town be as warm as Sam’s?</p></div>
</div>

<!-- ========== column 3: Check your thinking (answer paper) ========== -->
<div class="blk ans" style="left:{colx(8)}pt; top:{READ_T}pt; width:{colx(12) - GUT - colx(8)}pt; height:{READ_B - 16 - READ_T}pt">
  <div class="sh">Check your thinking</div>
  <p><b class="mr nw">12°C</b> is 12 degrees above zero; <b class="mt nw">−12°C</b> is 12 degrees below zero. Sam’s town is warmer. From <b class="mt nw">−12°C</b>, a rise of 10°C takes Sarah’s town to <b class="mt nw">−2°C</b>:</p>
  <div class="eq" data-math="−12 + 10 = −2"><span class="mt">−12</span> <span class="op">+</span> 10 <span class="op">=</span> <span class="mt">−2</span></div>
  <svg class="nl" data-math="−12 + 10 = −2" width="228pt" height="62pt" viewBox="0 0 228 62" aria-hidden="true">
    <defs><marker id="ah" viewBox="0 0 8 8" refX="6.5" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#1F6F6B"/></marker></defs>
    <path d="M1 40 H227" stroke="#1d2433" stroke-width=".9"/>
    {anl_ticks}
    <path d="M{ax(-12)} 33 C{ax(-12) + 14} 9 {ax(-2) - 14} 9 {ax(-2) - 1} 32" fill="none" stroke="#1F6F6B" stroke-width="1.3" marker-end="url(#ah)"/>
    <text x="{(ax(-12) + ax(-2)) / 2}" y="13" text-anchor="middle" font-family="Source Sans 3" font-weight="600" font-size="14" fill="#1F6F6B">+10</text>
    <circle cx="{ax(-12)}" cy="40" r="3.6" fill="#EFE6D2" stroke="#1F6F6B" stroke-width="1.4"/>
    <circle cx="{ax(-2)}" cy="40" r="3.8" fill="#1F6F6B"/>
    <circle cx="{ax(12)}" cy="40" r="3.8" fill="#B5603A"/>
    <g font-family="Source Sans 3" font-size="14" fill="#1d2433"><text x="{ax(-12)}" y="60" text-anchor="middle">−12</text><text x="{ax(-2)}" y="60" text-anchor="middle">−2</text><text x="{ax(0) + 1}" y="60" text-anchor="middle">0</text><text x="{ax(12)}" y="60" text-anchor="middle">12</text></g>
  </svg>
  <p style="margin:0"><i class="pl" data-math="−2 < 12"><b class="mt nw">−2°C</b> is still colder than Sam’s <b class="mr nw">12°C</b></i>. Sarah’s town has warmed up, but it has not caught up with Sam’s.</p>
</div>

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
"""
open(OUT, "w", encoding="utf-8").write(html)
print("wrote", OUT)
