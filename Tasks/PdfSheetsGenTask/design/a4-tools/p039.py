import sys; sys.path.insert(0, ".")
from common import *
D = T + "PdfSheetsGenTask/CH01/P039/"
sync_assets(D)
def mt(s): return f'<span class="mt">{s}</span>'
# 7 velvet pouches (answer figure, inside Check your method)
def pouch(x):
    return (f'<g transform="translate({x} 0)">'
            '<path d="M5 9 C1 14 0 22 3 27 C6 31 18 31 21 27 C24 22 23 14 19 9 Z" fill="#234d95" stroke="#0b1530" stroke-width=".8"/>'
            '<path d="M7 12 C5 16 5 21 7 25" stroke="#5b7fc4" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
            '<path d="M5 9 L8 4 L12 7 L16 4 L19 9 Z" fill="#1a3a78" stroke="#0b1530" stroke-width=".8"/>'
            '<rect x="5" y="8.2" width="14" height="2.6" rx="1.2" fill="#d6a64e"/>'
            '<circle cx="12" cy="9.5" r="1.8" fill="#f6dca0"/></g>')
pouches = '<svg style="display:block; width:124pt; height:21pt" viewBox="0 0 188 32" aria-hidden="true">' + "".join(pouch(i * 26.5) for i in range(7)) + "</svg>"

# one pack's contents, drawn exactly: 19 pencils, 3 erasers, 7 pens
c = []
for i in range(19):
    x = 2 + i * 5.4
    c.append(f'<rect x="{x:.1f}" y="9" width="3.8" height="27" fill="#2f5fae"/><rect x="{x:.1f}" y="33" width="3.8" height="3" fill="#d6a64e"/>'
             f'<path d="M{x:.1f} 9 L{x+1.9:.2f} 2 L{x+3.8:.1f} 9 Z" fill="#ead2a4"/><path d="M{x+1.3:.2f} 4.4 L{x+1.9:.2f} 2 L{x+2.5:.2f} 4.4 Z" fill="#121a33"/>')
for i in range(3):
    x = 116 + i * 16
    c.append(f'<rect x="{x}" y="22" width="13" height="14" rx="2" fill="#efe6d6"/><rect x="{x}" y="22" width="13" height="5" rx="1.5" fill="#b3722f"/>')
for i in range(7):
    x = 172 + i * 7.4
    c.append(f'<rect x="{x:.1f}" y="4" width="4.6" height="32" rx="2" fill="#0f1d3d" stroke="#5b7fc4" stroke-width=".5"/><rect x="{x:.1f}" y="4" width="4.6" height="10" rx="2" fill="#d6a64e"/><line x1="{x+3.6:.1f}" y1="6" x2="{x+3.6:.1f}" y2="17" stroke="#f6dca0" stroke-width=".8"/>')
contents = '<svg style="display:block; width:230pt; height:40pt; margin-top:4pt" viewBox="0 0 230 40" aria-hidden="true">' + "".join(c) + "</svg>"

style = """  .eqgrid .eq { font-size: 18pt; }
  .eqgrid .lbl { padding-right: 2pt; }
  .work .eq { font-size: 19pt; margin: 2pt 0 4pt; }
  .work p { margin-bottom: 5pt; }
  .meth p { margin-bottom: 3pt; }
  .meth .eqgrid { row-gap: 0; margin: 2pt 0 0; }
  .work .eqgrid { row-gap: 0; margin: 0 0 6pt; }
  .meth .eqgrid .eq { font-size: 17pt; line-height: 21pt; }"""
H = []
H.append('<div class="scene"><img src="assets/img/SCENE.jpg" alt=""><i class="shade-top"></i><i class="vignette"></i></div>')
H.append('<i class="bloom" style="left:118pt; top:4pt; width:160pt; height:160pt"></i>')
H.append('<h1 class="marquee" style="left:26pt; top:24pt">Example 11</h1>')
H.append(f'<div class="folio" style="right:24pt; top:24pt">{moon(39/108)}39</div>')
q = '<p style="margin:0">Salim wants to pack 171 pencils, 27 erasers and 63 pens into gift packs. Every pack must contain the same number of pencils, the same number of erasers and the same number of pens, with nothing left over. Find the greatest number of packs and the number of each item in one pack.</p>'
H.append(glass("marble lift", 262, 20, 512, 110, q))
col1 = ('<div class="cue">Let’s work it through</div>'
        '<p>Each kind of item must be shared equally, with none left over. So the number of packs must divide 171, 27 and 63 exactly. We want as many packs as possible: that means finding their HCF.</p>'
        f'<div class="eq" data-math="171 = 1 × 171 = 3 × 57 = 9 × 19">171 = 1 × 171 = 3 × 57 = {mt(9)} × 19</div>'
        f'<div class="eq" data-math="27 = 1 × 27 = 3 × 9">27 = 1 × 27 = 3 × {mt(9)}</div>'
        f'<div class="eq" data-math="63 = 1 × 63 = 3 × 21 = 7 × 9">63 = 1 × 63 = 3 × 21 = 7 × {mt(9)}</div>'
        f'<p style="margin-top:6pt">The common factors are 1, 3 and 9. The greatest is {mt(9)}, so Salim can make {mt(9)} packs. Now share each kind of item among those {mt(9)} packs:</p>')
col2 = ('<div class="eqgrid">\n'
        f'<span class="lbl">Pencils per pack:</span> <span class="eq" data-math="171 ÷ 9 = 19">171 ÷ {mt(9)} = 19</span>\n'
        f'<span class="lbl">Erasers per pack:</span> <span class="eq" data-math="27 ÷ 9 = 3">27 ÷ {mt(9)} = 3</span>\n'
        f'<span class="lbl">Pens per pack:</span> <span class="eq" data-math="63 ÷ 9 = 7">63 ÷ {mt(9)} = 7</span>\n'
        '</div>'
        f'<p>Each pack contains 19 pencils, 3 erasers and 7 pens. Every pack has that same mixture; the numbers 19, 3 and 7 do not have to match each other. Check the pencils, for example: <span data-math="9 × 19 = 171" style="font-weight:700">{mt(9)} × 19 = 171.</span></p>' + contents)
work = f'<div class="work" style="display:grid; grid-template-columns:290pt 252pt; column-gap:16pt"><div>{col1}</div><div>{col2}</div></div>'
H.append(glass("lift", 26, 142, 590, 290, work))
# nine packs standing on the counter (3 rows, back to front)
rows = [(54, 252, [672, 730, 788]), (62, 290, [654, 720, 786]), (70, 332, [636, 710, 784])]
for w, y, xs in rows:
    for x in xs:
        H.append(f'<div class="prop" style="left:{x}pt; top:{y}pt; width:{w}pt"><img src="assets/img/PACK.png" alt=""></div>')
ny = ('<div class="cue">Now you try</div>'
      '<p style="margin:0">Josephine has 28 candies, 49 stickers and 35 magnets. She wants identical goodie bags with nothing left over. Find the greatest number of bags and how many of each item go in one bag.</p>')
H.append(glass("marble", 26, 444, 246, 190, ny))
meth = ('<div class="meth"><div style="display:flex; justify-content:space-between; align-items:center"><div class="cue" style="margin:0; white-space:nowrap">Check your method</div>' + pouches + '</div>'
        '<p>Factors of 28: 1, 2, 4, 7, 14, 28.</p>'
        '<p>Factors of 49: 1, 7, 49. Factors of 35: 1, 5, 7, 35.</p>'
        f'<p>The common factors are 1 and 7, so the HCF is {mt(7)}. She can make {mt(7)} bags:</p>'
        '<div style="display:flex; align-items:flex-end; justify-content:space-between"><div class="eqgrid">\n'
        f'<span class="eq" data-math="28 ÷ 7 = 4">28 ÷ {mt(7)} = 4</span> <span class="lbl">candies per bag</span>\n'
        f'<span class="eq" data-math="49 ÷ 7 = 7">49 ÷ {mt(7)} = 7</span> <span class="lbl">stickers per bag</span>\n'
        f'<span class="eq" data-math="35 ÷ 7 = 5">35 ÷ {mt(7)} = 5</span> <span class="lbl">magnets per bag</span>\n'
        '</div></div></div>')
H.append(glass("", 284, 444, 344, 190, meth))
H.append('<div class="say" style="left:640pt; top:424pt; width:206pt; --tx:62%; --tr:6deg">I like “nothing left over”. Especially at dinner.'
         '<svg class="tail" viewBox="0 0 24 26"><path d="M3 0 C6 10 5 18 1 26 C10 20 17 11 20 0"/></svg></div>')
H.append('<div class="actor" style="left:690pt; top:488pt; width:136pt"><img src="assets/img/TEZ.png" alt=""><i class="contact"></i></div>')
html = HEAD.format(ch="CH01", pg="P039", style=style) + "\n".join(H) + "\n" + TAIL
open(D + "index.html", "w", encoding="utf-8").write(html)
print("written", len(html))
