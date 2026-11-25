import os, shutil
T = "/home/akasdh/Desktop/Projects/ComicAgent/Tasks/"
def sync_assets(page_dir):
    a = os.path.join(page_dir, "assets"); os.makedirs(os.path.join(a, "fonts"), exist_ok=True)
    for f in ("base.css", "kit.css"):
        shutil.copy(T + "PdfSheetsGenTask/design/" + f, os.path.join(a, f))
    for f in os.listdir(T + "pipeline/fonts"):
        if f.endswith(".ttf"):
            shutil.copy(T + "pipeline/fonts/" + f, os.path.join(a, "fonts", f))
    for f in ("Cinzel.ttf", "Rajdhani-Bold.ttf", "Rajdhani-SemiBold.ttf"):   # A3 only
        p = os.path.join(a, "fonts", f)
        if os.path.exists(p): os.remove(p)
def moon(t):
    k = max(0.0, min(1.0, t)); rx = 9 * abs(1 - 2 * k); sw = 0 if k < 0.5 else 1
    return ('<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="9" fill="#0c1933" stroke="#cfe0fa" stroke-opacity=".55" stroke-width=".7"/>'
            f'<path d="M10 1 A9 9 0 0 1 10 19 A{rx:.2f} 9 0 0 {sw} 10 1 Z" fill="#e9f1fc"/></svg>')
def glass(cls, x, y, w, h, inner, extra=""):
    return (f'<div class="glass {cls}" style="left:{x}pt; top:{y}pt; width:{w}pt; height:{h}pt; --x:{x}pt; --y:{y}pt{extra}">'
            f'<img class="under" src="assets/img/GLASS.jpg" alt="">{inner}</div>')
HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>ChandRush {ch} {pg}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="assets/base.css">
<link rel="stylesheet" href="assets/kit.css">
<style>
{style}
</style>
</head>
<body>
<div class="page a4" id="page" data-chapter="{ch}" data-page="{pg}">
"""
TAIL = """</div>
<script>
  /* screen only: scale the 12x9 in sheet to fit the window; printing ignores this */
  (function () {
    var p = document.getElementById("page");
    function fit() {
      p.style.zoom = 1;
      var s = Math.min(document.documentElement.clientWidth / p.offsetWidth, window.innerHeight / p.offsetHeight);
      p.style.zoom = s;
    }
    if (window.matchMedia && !window.matchMedia("print").matches) { window.addEventListener("resize", fit); fit(); }
  })();
</script>
</body>
</html>
"""

def bln(spec, z=8):
    """seamless speech balloons (body + tail drawn as one outline): see pipeline/balloon.py for the spec."""
    import sys as _s
    _s.path.insert(0, T + "pipeline")
    from balloon import balloons_html, report
    print(report(spec), file=_s.stderr)
    return balloons_html(spec, z)
