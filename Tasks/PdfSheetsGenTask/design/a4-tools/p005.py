import sys; sys.path.insert(0, ".")
from common import *
D = T + "PdfSheetsGenTask/CH01/P005/"
sync_assets(D)
# ---------- gauge (question figure: only 12°C, −12°C and 0) ----------
GX, GY = 340, 176                    # svg origin on the page
cx, y0, k = 101, 142, 7.2            # tube centre, zero line, pt per degree
Y = lambda t: y0 - k * t
g = []
g.append(f'<rect x="{cx-15}" y="{Y(15)-14}" width="30" height="{Y(-15)-Y(15)+28}" rx="15" fill="#0b1530" fill-opacity=".55" stroke="#d6a64e" stroke-width="1.4"/>')
g.append(f'<rect x="{cx-9}" y="{Y(15)-4}" width="18" height="{y0-Y(15)+4}" rx="6" fill="#f7c684" fill-opacity=".55"/>')
g.append(f'<rect x="{cx-9}" y="{y0}" width="18" height="{Y(-15)-y0+4}" rx="6" fill="#bcd8fb" fill-opacity=".6"/>')
g.append(f'<rect x="{cx-12}" y="{Y(15)-12}" width="5" height="{Y(-15)-Y(15)+24}" rx="2.5" fill="#ffffff" fill-opacity=".22"/>')
for t in range(-15, 16):
    y = Y(t); major = t % 5 == 0
    L = 12 if major else 7
    col = "#f6dca0" if t > 0 else ("#ffffff" if t == 0 else "#d7e7fb")
    g.append(f'<line x1="{cx-17-L}" y1="{y:.1f}" x2="{cx-17}" y2="{y:.1f}" stroke="{col}" stroke-width="{1.3 if major else .8}"/>')
    g.append(f'<line x1="{cx+17}" y1="{y:.1f}" x2="{cx+17+L}" y2="{y:.1f}" stroke="{col}" stroke-width="{1.3 if major else .8}"/>')
# caps
g.append(f'<rect x="{cx-19}" y="{Y(15)-22}" width="38" height="12" rx="3" fill="#b8862f" stroke="#f6dca0" stroke-width=".8"/>')
g.append(f'<rect x="{cx-19}" y="{Y(-15)+10}" width="38" height="12" rx="3" fill="#b8862f" stroke="#f6dca0" stroke-width=".8"/>')
g.append(f'<rect x="{cx-6}" y="{Y(15)-30}" width="12" height="9" rx="2" fill="#8a5a20"/>')
# zero line and label
g.append(f'<line x1="{cx-46}" y1="{y0}" x2="{cx+46}" y2="{y0}" stroke="#ffffff" stroke-width="1.6"/>')
g.append(f'<text x="{cx+52}" y="{y0+6}" font-family="Big Shoulders Display" font-weight="800" font-size="18" fill="#ffffff">0</text>')
# readings: 12 (warm, right) and −12 (cold, left)
g.append(f'<circle cx="{cx}" cy="{Y(12):.1f}" r="5.5" fill="#f7c684" stroke="#ffffff" stroke-width="1.2"/>')
g.append(f'<circle cx="{cx}" cy="{Y(-12):.1f}" r="5.5" fill="#d7e7fb" stroke="#ffffff" stroke-width="1.2"/>')
g.append(f'<line x1="{cx+30}" y1="{Y(12):.1f}" x2="{cx+40}" y2="{Y(12):.1f}" stroke="#f6dca0" stroke-width="1.2"/>')
g.append(f'<line x1="{cx-40}" y1="{Y(-12):.1f}" x2="{cx-30}" y2="{Y(-12):.1f}" stroke="#d7e7fb" stroke-width="1.2"/>')
gauge = f'<svg class="abs" style="left:{GX}pt; top:{GY}pt; width:200pt; height:300pt; overflow:visible" viewBox="0 0 200 300" aria-hidden="true">' + "".join(g) + "</svg>"
tag12 = f'<div class="tag12" style="left:{GX+cx+40}pt; top:{GY+Y(12)-14:.1f}pt">12°C</div>'
tagm12 = f'<div class="tagm12" style="left:{GX+cx-40-66}pt; top:{GY+Y(-12)-14:.1f}pt">−12°C</div>'
# ---------- number line (answer figure) ----------
X = lambda v: 14 + (v + 12) * 10.2
n = [f'<line x1="{X(-12)-6}" y1="44" x2="{X(12)+6}" y2="44" stroke="#f6dca0" stroke-width="1.4"/>']
for v in range(-12, 13):
    big = v in (-12, -2, 0, 12)
    n.append(f'<line x1="{X(v):.1f}" y1="{39 if big else 41}" x2="{X(v):.1f}" y2="{49 if big else 47}" stroke="{"#ffffff" if v == 0 else "#f6dca0"}" stroke-width="{1.3 if big else .7}"/>')
n.append(f'<path d="M{X(-12):.1f} 37 C {X(-12)+12:.1f} 6, {X(-2)-12:.1f} 6, {X(-2):.1f} 35" fill="none" stroke="#cfe0fa" stroke-width="1.6"/>')
n.append(f'<path d="M{X(-2)-5:.1f} 29 L{X(-2):.1f} 36 L{X(-2)+3:.1f} 28" fill="none" stroke="#cfe0fa" stroke-width="1.6"/>')
n.append(f'<text x="{(X(-12)+X(-2))/2:.1f}" y="13" text-anchor="middle" font-family="Source Sans 3" font-weight="700" font-size="13" fill="#cfe0fa">+10</text>')
n.append(f'<circle cx="{X(-12):.1f}" cy="44" r="5" fill="#0b1530" stroke="#cfe0fa" stroke-width="1.8"/>')
n.append(f'<circle cx="{X(-2):.1f}" cy="44" r="5" fill="#cfe0fa"/>')
n.append(f'<circle cx="{X(12):.1f}" cy="44" r="5" fill="#f7c684"/>')
for v, c in ((-12, "#cfe0fa"), (-2, "#cfe0fa"), (0, "#ffffff"), (12, "#f7c684")):
    n.append(f'<text x="{X(v):.1f}" y="66" text-anchor="middle" font-family="Source Sans 3" font-weight="700" font-size="12.5" fill="{c}">{str(v).replace("-", "−")}</text>')
numberline = '<svg style="display:block; width:268pt; height:70pt; overflow:visible" viewBox="0 0 268 70" aria-hidden="true">' + "".join(n) + "</svg>"

style = """  /* P005: Sarah's temperatures (tracked) in moonlight, Sam's in lamp gold */
  .page .glass .mt { color: #cfe0fa; } .page .glass .mr { color: #f7c684; }
  .page .glass.frost .mt { color: #1f4f9a; } .page .glass.frost .mr { color: #a3561c; }
  .glass.frost::before { background: linear-gradient(180deg, rgba(236,244,254,.80), rgba(214,229,247,.86)); }
  .tag12, .tagm12 { position: absolute; width: 66pt; height: 28pt; border-radius: 4pt; text-align: center;
    font: 800 19pt/28pt "Big Shoulders Display", sans-serif; letter-spacing: .03em; box-shadow: 0 6pt 14pt rgba(2,5,14,.55); }
  .tag12  { background: #2a1a0e; color: #f7c684; border: 1pt solid #d6a64e; }
  .tagm12 { background: #e6f0fc; color: #1f4f9a; border: 1pt solid #ffffff; }
  .two { display: grid; grid-template-columns: 262pt 268pt; column-gap: 18pt; }"""
H = []
H.append('<div class="scene"><img src="assets/img/SCENE.jpg" alt=""><i class="shade-top"></i><i class="vignette"></i><i class="shade-bottom"></i></div>')
H.append('<i class="bloom moon" style="left:398pt; top:78pt; width:140pt; height:140pt"></i>')
H.append('<i class="bloom" style="left:672pt; top:150pt; width:150pt; height:150pt"></i>')
H.append('<h1 class="marquee" style="left:26pt; top:22pt">Numbers <span class="ice">below zero</span></h1>')
H.append(f'<div class="folio" style="right:24pt; top:24pt">{moon(5/108)}05</div>')
left = ('<i class="rime tl"></i>'
        '<p class="voice">Before we choose the lift’s movements, let’s get to know the numbers on its strip. You’re part of the crew too, and you can take your time. The clock belongs to the adventure. You can pause, reread or come back tomorrow without making ChandRush less safe.</p>'
        '<div class="rule-brass"></div>'
        '<p>Why is <span class="mt">−12°C</span> colder than <span class="mr">12°C</span>? We’ll start with numbers below zero, then explore equal groups, quick division checks, squares and cubes. Each idea will help you choose a calculation and understand why it works.</p>'
        '<p>We’ll work through this chapter together. Keep a pencil nearby: when you reach a Try or Practice question, cover the working underneath and have a go. Then uncover it and compare the steps, not only the final number.</p>')
H.append(glass("frost", 26, 88, 308, 384, left))
q = '<p style="margin:0">Sam’s town is at <span class="mr">12°C</span>. Sarah’s town is at <span class="mt">−12°C</span>. Both temperatures contain 12, but Sarah will certainly want the warmer coat! What difference does that little minus sign make?</p>'
H.append(glass("lift", 548, 88, 290, 132, q))
p = '<p style="margin:0"><span class="cue run">Pause and think.</span> Why might Sam feel comfortable while Sarah feels very cold? If Sarah’s temperature rises by 10°C, will her town be as warm as Sam’s?</p>'
H.append(glass("", 548, 232, 290, 112, p))
H.append(gauge); H.append(tag12); H.append(tagm12)
H.append('<div class="actor" style="left:604pt; top:356pt; width:256pt"><img src="assets/img/AHANA.png" alt=""></div>')
chk = ('<div class="two"><div>'
       '<div class="cue">Check your thinking</div>'
       '<p>12°C is 12 degrees above zero; <span class="mt">−12°C</span> is 12 degrees below zero. Sam’s town is warmer. From <span class="mt">−12°C</span>, a rise of 10°C takes Sarah’s town to <span class="mt">−2°C</span>:</p>'
       '<div class="eq" data-math="−12 + 10 = −2"><span class="mt">−12</span> + 10 = <span class="mt">−2</span></div>'
       '</div><div>' + numberline +
       '<p style="margin-top:6pt"><span class="mt">−2°C</span> is still colder than Sam’s <span class="mr">12°C</span>. Sarah’s town has warmed up, but it has not caught up with Sam’s.</p>'
       '</div></div>')
H.append(glass("lift", 26, 484, 590, 144, chk))
html = HEAD.format(ch="CH01", pg="P005", style=style) + "\n".join(H) + "\n" + TAIL
open(D + "index.html", "w", encoding="utf-8").write(html)
print("written", len(html))
