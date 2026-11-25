#!/usr/bin/env python3
"""pagekit.py: build, check and print ChandRush pages (stage 3). Run from anywhere.

  new CH02 P003 [--theme theme-navy]     PdfSheetsGenTask/CH02/P003/index.html from the template, plus
                                         assets/base.css, assets/kit.css (creative kit) and assets/fonts
  img PAGE_DIR SRC NAME [--max 2400]     copy an image into PAGE_DIR/assets/img/NAME.jpg (JPEG q88, long edge <= max)
                                         keeps the artifact small; use .png only if transparency is needed (--png)
  numberline --from -8 --to 8 [--step 1] [--width 380] [--jump 3:7:+4] [--jump 7:1:-6] [--dot 1] [--vertical]
                                         print an exact SVG number line (paste it into the page). Jumps are drawn
                                         as labelled arcs from:to:label, above (+) or below (-) the line.
  backdrop PAGE_DIR PLATE [--blur 9] [--dark .62]
                                         the page's own location plate, softened (blurred, darkened) into
                                         assets/img/BACKDROP.jpg for <img class="backdrop"> on a .stage-backdrop page (free)
  scene PAGE_DIR PLATE [--mirror] [--crop x0,y0,x1,y1] [--blank x0,y0,x1,y1 ...] [--blur 10]
                                         A4: the location plate as the full-bleed world (assets/img/SCENE.jpg, 1728x1296)
                                         plus GLASS.jpg (the same picture blurred, 864x648) for <img class="under"> in
                                         every .glass pane. --blank wipes painted words/numbers (plate px, before mirror)
  cutout PAGE_DIR SRC NAME --poly "x,y x,y ..." [--feather 2]
                                         cut a character or prop out of existing art along a traced outline (SRC px)
                                         into assets/img/NAME.png, so it can stand in the scene (free)
  check PAGE_DIR                         mathcheck + local-assets check (no network fonts/images, no absolute paths)
  render PAGE_DIR                        check, then print Output/CHxx/CHxx-Pxxx.pdf and PAGE_DIR/preview.png
  artifact PAGE_DIR                      build PAGE_DIR/artifact.html (CSS + fonts inlined, no html/head/body wrapper)
                                         and print the Artifact publish arguments (file_path, files, title, icon)
  set CH01 P001-P005 [--name NAME]       ALL requested pages as ONE deliverable: Output/CH01/CH01-<NAME>.pdf (lossless join,
                                         manuscript order) + PdfSheetsGenTask/CH01/sets/<NAME>/artifact.html (every sheet
                                         stacked, CSS/ids namespaced per page) and its publish arguments. Pages: P001-P005,
                                         P001,P003 or P001-P003,P107. Default deliverable of every multi-page request.

A page is ready only when `render` prints OK (1 page, 864 x 648 pt) and mathcheck has 0 failures.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

PIPE = os.path.dirname(os.path.abspath(__file__))
TASKS = os.path.dirname(PIPE)
DESIGN = os.path.join(TASKS, "PdfSheetsGenTask", "design")
sys.path.insert(0, PIPE)


def page_ids(page_dir):
    page_dir = os.path.abspath(page_dir)
    pg, ch = os.path.basename(page_dir), os.path.basename(os.path.dirname(page_dir))
    if not re.fullmatch(r"P\d{3}", pg) or not re.fullmatch(r"CH\d{2}", ch):
        sys.exit(f"{page_dir}: expected PdfSheetsGenTask/CHxx/Pxxx")
    return ch, pg


def cmd_new(a):
    d = os.path.join(TASKS, "PdfSheetsGenTask", a.chapter, a.page)
    if os.path.exists(os.path.join(d, "index.html")) and not a.force:
        sys.exit(f"{d}/index.html exists (use --force to overwrite)")
    os.makedirs(os.path.join(d, "assets", "img"), exist_ok=True)
    shutil.copy(os.path.join(DESIGN, "base.css"), os.path.join(d, "assets", "base.css"))
    shutil.copy(os.path.join(DESIGN, "kit.css"), os.path.join(d, "assets", "kit.css"))   # creative kit (ART-DIRECTION.md)
    fd = os.path.join(d, "assets", "fonts")
    os.makedirs(fd, exist_ok=True)
    for f in os.listdir(os.path.join(PIPE, "fonts")):
        if f.endswith(".ttf"):
            shutil.copy(os.path.join(PIPE, "fonts", f), fd)
    html = open(os.path.join(DESIGN, "template.html"), encoding="utf-8").read()
    html = html.replace("{{CHAPTER}}", a.chapter).replace("{{PAGE}}", a.page).replace("{{THEME}}", a.theme)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
    print(d)


def cmd_img(a):
    from PIL import Image
    im = Image.open(a.src)
    im.thumbnail((a.max, a.max))
    out_dir = os.path.join(a.page_dir, "assets", "img")
    os.makedirs(out_dir, exist_ok=True)
    if a.png:
        out = os.path.join(out_dir, a.name + ".png")
        im.save(out, optimize=True)
    else:
        out = os.path.join(out_dir, a.name + ".jpg")
        im.convert("RGB").save(out, "JPEG", quality=88, optimize=True)
    print(f"{os.path.relpath(out, a.page_dir)}  {im.size[0]}x{im.size[1]}  {os.path.getsize(out) // 1024} KB")


def cmd_backdrop(a):
    from PIL import Image, ImageEnhance, ImageFilter
    im = Image.open(a.plate).convert("RGB")
    im.thumbnail((1400, 1400))
    im = im.filter(ImageFilter.GaussianBlur(a.blur * im.size[0] / 1024))
    im = ImageEnhance.Brightness(im).enhance(a.dark)
    im = ImageEnhance.Color(im).enhance(1.08)
    out = os.path.join(a.page_dir, "assets", "img", "BACKDROP.jpg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out, "JPEG", quality=80, optimize=True)
    print(f"{os.path.relpath(out, a.page_dir)}  {im.size[0]}x{im.size[1]}  {os.path.getsize(out) // 1024} KB")


def _box(v):
    return tuple(int(float(t)) for t in v.split(","))


def cmd_scene(a):
    from PIL import Image, ImageDraw, ImageFilter
    im = Image.open(a.plate).convert("RGB")
    for b in a.blank or []:                     # blank a painted label: soft blur + its own lightest colour
        b = _box(b)
        reg = im.crop(b)
        px = sorted(reg.getdata(), key=lambda p: -sum(p))[: max(1, len(reg.getdata()) // 3)]
        avg = tuple(sum(c[i] for c in px) // len(px) for i in range(3))
        fill = Image.blend(reg.filter(ImageFilter.GaussianBlur(18)), Image.new("RGB", reg.size, avg), 0.55)
        m = Image.new("L", reg.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((4, 4, reg.size[0] - 5, reg.size[1] - 5), 6, fill=255)
        im.paste(fill, b[:2], m.filter(ImageFilter.GaussianBlur(2.5)))
    if a.crop:
        im = im.crop(_box(a.crop))
    if a.mirror:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    big = im.resize((1728, 1296), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
    d = os.path.join(a.page_dir, "assets", "img")
    os.makedirs(d, exist_ok=True)
    big.save(os.path.join(d, "SCENE.jpg"), "JPEG", quality=88)
    big.resize((864, 648), Image.LANCZOS).filter(ImageFilter.GaussianBlur(a.blur)).save(os.path.join(d, "GLASS.jpg"), "JPEG", quality=85)
    print("assets/img/SCENE.jpg 1728x1296, assets/img/GLASS.jpg 864x648")


def cmd_cutout(a):
    from PIL import Image, ImageDraw, ImageFilter
    im = Image.open(a.src).convert("RGB")
    W, H, k = im.size[0], im.size[1], 3
    poly = [tuple(float(t) for t in p.split(",")) for p in a.poly.split()]
    m = Image.new("L", (W * k, H * k), 0)
    ImageDraw.Draw(m).polygon([(x * k, y * k) for x, y in poly], fill=255)
    m = m.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(a.feather))
    out = im.convert("RGBA"); out.putalpha(m)
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    out = out.crop((max(0, int(min(xs)) - 6), max(0, int(min(ys)) - 6), min(W, int(max(xs)) + 6), min(H, int(max(ys)) + 6)))
    dst = os.path.join(a.page_dir, "assets", "img", a.name + ".png")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    out.save(dst)
    print(f"{os.path.relpath(dst, a.page_dir)}  {out.size[0]}x{out.size[1]}")


def fmt(v):
    v = float(v)
    s = str(int(v)) if v == int(v) else f"{v:g}"
    return s.replace("-", "−")


def cmd_numberline(a):
    lo, hi, step = a.from_, a.to, a.step
    n = round((hi - lo) / step)
    L, pad = a.width, 16
    ticks = [lo + i * step for i in range(n + 1)]
    pos = lambda v: pad + (v - lo) / (hi - lo) * (L - 2 * pad)  # noqa: E731
    col, hi1, hi2 = "currentColor", "var(--hi1)", "var(--hi2)"
    H = 124
    base = 50
    parts = [f'<line x1="{pad - 6}" y1="{base}" x2="{L - pad + 6}" y2="{base}" stroke="{col}" stroke-width="1.2"/>',
             f'<path d="M{L - pad + 6},{base - 4} L{L - pad + 12},{base} L{L - pad + 6},{base + 4}" fill="{col}"/>',
             f'<path d="M{pad - 6},{base - 4} L{pad - 12},{base} L{pad - 6},{base + 4}" fill="{col}"/>']
    for t in ticks:
        x = pos(t)
        parts.append(f'<line x1="{x:.1f}" y1="{base - 5}" x2="{x:.1f}" y2="{base + 5}" stroke="{col}" stroke-width="1"/>')
        if a.labels_every and round((t - lo) / step) % a.labels_every == 0:
            parts.append(f'<text x="{x:.1f}" y="{base + 19}" text-anchor="middle" font-size="11" fill="{col}">{fmt(t)}</text>')
    for k, j in enumerate(a.jump):
        f, t, lab = j.split(":")
        f, t = float(f), float(t)
        x1, x2 = pos(f), pos(t)
        up = not lab.strip().startswith(("-", "−"))
        c = hi1 if up else hi2
        y = base - 26 - 8 * (k % 2) if up else base + 46 + 8 * (k % 2)
        y0 = base - 6 if up else base + 25   # below the tick labels
        parts.append(f'<path d="M{x1:.1f},{y0} L{x1:.1f},{y} L{x2:.1f},{y} L{x2:.1f},{y0}" fill="none" stroke="{c}" stroke-width="1.4"/>')
        parts.append(f'<path d="M{x2 - 4:.1f},{y0 + (-6 if up else 6)} L{x2:.1f},{y0} L{x2 + 4:.1f},{y0 + (-6 if up else 6)}" fill="none" stroke="{c}" stroke-width="1.4"/>')
        ty = y - 5 if up else y + 13
        parts.append(f'<text x="{(x1 + x2) / 2:.1f}" y="{ty}" text-anchor="middle" font-size="12" font-weight="700" fill="{c}">{lab.replace("-", chr(0x2212))}</text>')
    for d in a.dot:
        parts.append(f'<circle cx="{pos(float(d)):.1f}" cy="{base}" r="4" fill="{hi1}"/>')
    svg = (f'<svg class="numberline" viewBox="0 0 {L} {H}" width="{L}pt" height="{H}pt" '
           f'xmlns="http://www.w3.org/2000/svg" font-family="Source Sans 3, sans-serif">' + "".join(parts) + "</svg>")
    if a.vertical:
        svg = f'<div style="display:inline-block;transform:rotate(-90deg);transform-origin:center">{svg}</div>'
    print(svg)


def cmd_check(a, quiet=False):
    import mathcheck
    path = os.path.join(a.page_dir, "index.html")
    html = open(path, encoding="utf-8").read()
    errs = []
    for m in re.finditer(r"""(?:src|href)\s*=\s*["']([^"']+)["']|url\(\s*["']?([^"')]+)""", html):
        ref = m.group(1) or m.group(2)
        if ref.startswith(("data:", "#")):
            continue
        if re.match(r"^(https?:|file:|/)", ref):
            errs.append(f"non-local reference {ref} (copy it into assets/)")
        elif not os.path.exists(os.path.join(a.page_dir, ref)):
            errs.append(f"missing asset {ref}")
    for bad in ("TODO", "{{", "lorem", "Lorem"):
        if bad in html:
            errs.append(f"leftover placeholder '{bad}'")
    r = subprocess.run([sys.executable, os.path.join(PIPE, "mathcheck.py"), path], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode:
        errs.append("mathcheck failed (see above): fix the maths or the data-math tag")
    for e in errs:
        print("BAD  " + e)
    if errs:
        sys.exit(f"{len(errs)} problem(s)")
    print("check OK")


def cmd_render(a):
    from render_pdf import render
    cmd_check(a)
    ch, pg = page_ids(a.page_dir)
    out = os.path.join(TASKS, "Output", ch, f"{ch}-{pg}.pdf")
    render(os.path.join(a.page_dir, "index.html"), out, os.path.join(a.page_dir, "preview.png"), a.dpi)


def cmd_artifact(a):
    """Build PAGE_DIR/artifact.html for the Artifact tool: no doctype/html/head/body (the publisher adds them),
    base.css and fonts inlined (other-host stylesheets are blocked), images kept as published files."""
    import base64
    page_dir = os.path.abspath(a.page_dir)
    ch, pg = page_ids(page_dir)
    src = open(os.path.join(page_dir, "index.html"), encoding="utf-8").read()
    css = open(os.path.join(page_dir, "assets", "base.css"), encoding="utf-8").read()
    kit = os.path.join(page_dir, "assets", "kit.css")
    if os.path.exists(kit):
        css += "\n" + open(kit, encoding="utf-8").read()

    def font(m):
        path = os.path.join(page_dir, "assets", m.group(1))
        return "url(data:font/ttf;base64," + base64.b64encode(open(path, "rb").read()).decode() + ")"
    css = re.sub(r'url\("(fonts/[^"]+)"\)', font, css)
    title = f"ChandRush {ch} Page {int(pg[1:])}"   # the <title> names the artifact
    styles = "\n".join(re.findall(r"<style>(.*?)</style>", src, re.S))
    body = re.search(r"<body[^>]*>(.*)</body>", src, re.S).group(1)
    out = (f"<title>{title}</title>\n<style>\n{css}\n{styles}\n</style>\n" + body.strip() + "\n")
    dst = os.path.join(page_dir, "artifact.html")
    with open(dst, "w", encoding="utf-8") as fh:
        fh.write(out)
    files, total = {}, os.path.getsize(dst)
    # every way a page can point at its art: <img src>, SVG <image href>/xlink:href, CSS url()
    refs = re.findall(r'(?:src|href)="(assets/img/[^"]+)"', body) + re.findall(r'url\(["\']?(assets/img/[^"\')]+)', body + styles)
    for ref in sorted(set(refs)):
        full = os.path.join(page_dir, ref)
        if not os.path.exists(full):
            sys.exit(f"missing {ref}")
        total += os.path.getsize(full)
        files[ref] = os.path.relpath(full, os.getcwd())
    if os.path.getsize(dst) > 16 * 2**20:
        sys.exit("artifact.html is over 16 MB")
    print(json.dumps({"file_path": os.path.relpath(dst, os.getcwd()), "files": files,
                      "title": f"ChandRush {ch} Page {int(pg[1:])}", "icon": "book"}, indent=1))
    print(f"# artifact.html {os.path.getsize(dst) / 2**20:.1f} MB, {len(files)} image(s), total {total / 2**20:.1f} MB",
          file=sys.stderr)


def page_range(spec):
    """'P001-P005' or 'P001,P003,P007' or 'P001-P003,P107' -> ['P001', ...] (manuscript ids, never renumbered)"""
    out = []
    for part in spec.split(","):
        part = part.strip().upper()
        if "-" in part:
            a, b = part.split("-")
            out += [f"P{n:03d}" for n in range(int(a.lstrip("P")), int(b.lstrip("P")) + 1)]
        elif part:
            out.append(part if part.startswith("P") else f"P{int(part):03d}")
    return out


def cmd_set(a):
    """All requested pages in ONE deliverable: a combined PDF (lossless join of the page PDFs, manuscript order)
    and ONE artifact page that shows every sheet stacked (each page's CSS and SVG ids namespaced, so nothing clashes)."""
    import base64
    ch = a.chapter.upper()
    pages = [p for p in page_range(a.pages)]
    base_dir = os.path.join(TASKS, "PdfSheetsGenTask", ch)
    missing = [p for p in pages if not os.path.exists(os.path.join(TASKS, "Output", ch, f"{ch}-{p}.pdf"))]
    if missing:
        sys.exit("render these first: " + " ".join(missing))
    name = a.name or (f"{pages[0]}-{pages[-1]}" if len(pages) > 1 else pages[0])
    # 1. combined PDF: pdfunite copies the page objects as they are (no re-encoding, no rasterising)
    pdf = os.path.join(TASKS, "Output", ch, f"{ch}-{name}.pdf")
    subprocess.run(["pdfunite"] + [os.path.join(TASKS, "Output", ch, f"{ch}-{p}.pdf") for p in pages] + [pdf], check=True)
    # 2. one artifact with every sheet
    set_dir = os.path.join(base_dir, "sets", name)
    os.makedirs(set_dir, exist_ok=True)
    first = os.path.join(base_dir, pages[0])
    css = open(os.path.join(first, "assets", "base.css"), encoding="utf-8").read()
    kit = os.path.join(first, "assets", "kit.css")
    if os.path.exists(kit):
        css += "\n" + open(kit, encoding="utf-8").read()

    def font(m):
        return "url(data:font/ttf;base64," + base64.b64encode(open(os.path.join(first, "assets", m.group(1)), "rb").read()).decode() + ")"
    css = re.sub(r'url\("(fonts/[^"]+)"\)', font, css)
    css = re.sub(r"html,\s*body\s*\{[^}]*\}", "", css)          # the set page owns html/body
    sheets, files, scoped = [], {}, []
    for p in pages:
        d = os.path.join(base_dir, p)
        src = open(os.path.join(d, "index.html"), encoding="utf-8").read()
        st = "\n".join(re.findall(r"<style>(.*?)</style>", src, re.S))
        body = re.search(r"<body[^>]*>(.*)</body>", src, re.S).group(1)
        body = re.sub(r"<script\b.*?</script>", "", body, flags=re.S)
        ids = set(re.findall(r'\bid="([^"]+)"', body))
        for i in sorted(ids, key=len, reverse=True):
            new = f"{p}-{i}"
            body = re.sub(rf'\bid="{re.escape(i)}"', f'id="{new}"', body)
            body = re.sub(rf'url\(#{re.escape(i)}\)', f"url(#{new})", body)
            body = re.sub(rf'href="#{re.escape(i)}"', f'href="#{new}"', body)
            st = re.sub(rf'url\(#{re.escape(i)}\)', f"url(#{new})", st)
        body = re.sub(r'(src|href)="assets/', rf'\1="{p}/assets/', body)
        body = re.sub(r'url\((["\']?)assets/', rf'url(\1{p}/assets/', body)
        st = re.sub(r'url\((["\']?)assets/', rf'url(\1{p}/assets/', st)
        st = re.sub(r"/\*.*?\*/", "", st, flags=re.S)

        def scope(m, p=p):
            sel = m.group(1)
            if sel.strip().startswith("@"):
                return m.group(0)
            return ",".join(f"#s-{p} {x.strip()}" for x in sel.split(",")) + " {"
        scoped.append(re.sub(r"([^{}]+)\{", scope, st))
        sheets.append(f'<section class="sheet" id="s-{p}">{body.strip()}</section>')
        refs = re.findall(rf'(?:src|href)="({p}/assets/img/[^"]+)"', body) + re.findall(rf'url\(["\']?({p}/assets/img/[^"\')]+)', body + st)
        for ref in sorted(set(refs)):
            full = os.path.join(base_dir, ref)
            files[ref] = os.path.relpath(full, os.getcwd())
    title = f"ChandRush {ch} " + (f"Pages {int(pages[0][1:])}–{int(pages[-1][1:])}" if len(pages) > 1 else f"Page {int(pages[0][1:])}")
    out = (f"<title>{title}</title>\n<style>\n{css}\n" + "\n".join(scoped) + """
html, body { margin: 0; padding: 0; background: #0b1120; }
.set { display: flex; flex-direction: column; align-items: center; gap: 28px; padding-block: 28px; }
.sheet { position: relative; }
.sheet .page { box-shadow: 0 6px 28px rgba(0,0,0,.55); }
@media print { .set { gap: 0; padding: 0; } .sheet { break-after: page; } .sheet .page { box-shadow: none; } }
</style>
<div class="set">
""" + "\n".join(sheets) + """
</div>
<script>
  (function () {
    var ps = document.querySelectorAll(".sheet > .page");
    function fit() {
      var w = document.documentElement.clientWidth - 24;
      ps.forEach(function (p) { p.style.zoom = 1; p.style.zoom = Math.min(1, w / p.offsetWidth); });
    }
    window.addEventListener("resize", fit); fit();
  })();
</script>
""")
    dst = os.path.join(set_dir, "artifact.html")
    open(dst, "w", encoding="utf-8").write(out)
    if os.path.getsize(dst) > 16 * 2**20:
        sys.exit("artifact.html is over 16 MB")
    # contact sheet of the previews: the master reviews every page in one image (cheap), zooms only where needed
    try:
        from PIL import Image
        ims = [Image.open(os.path.join(base_dir, p, "preview.png")).convert("RGB") for p in pages]
        cols = 2 if len(ims) > 1 else 1
        w = 900 if cols == 2 else 1320
        th = [im.resize((w, int(im.height * w / im.width))) for im in ims]
        h = max(t.height for t in th)
        sheet = Image.new("RGB", (cols * w + (cols - 1) * 12, ((len(th) + cols - 1) // cols) * (h + 12)), (11, 17, 32))
        for i, t in enumerate(th):
            sheet.paste(t, ((i % cols) * (w + 12), (i // cols) * (h + 12)))
        sheet.save(os.path.join(set_dir, "contact.png"))
        print(f"contact sheet {os.path.join(set_dir, 'contact.png')}", file=sys.stderr)
    except Exception as e:
        print(f"(no contact sheet: {e})", file=sys.stderr)
    print(f"PDF  {pdf}  ({len(pages)} pages)", file=sys.stderr)
    print(json.dumps({"file_path": os.path.relpath(dst, os.getcwd()), "files": files, "title": title, "icon": "book"}, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("new"); s.add_argument("chapter"); s.add_argument("page")
    s.add_argument("--theme", default="theme-navy"); s.add_argument("--force", action="store_true")
    s = sub.add_parser("img"); s.add_argument("page_dir"); s.add_argument("src"); s.add_argument("name")
    s.add_argument("--max", type=int, default=2400); s.add_argument("--png", action="store_true")
    s = sub.add_parser("numberline")
    s.add_argument("--from", dest="from_", type=float, required=True); s.add_argument("--to", type=float, required=True)
    s.add_argument("--step", type=float, default=1); s.add_argument("--width", type=int, default=380)
    s.add_argument("--labels-every", type=int, default=1); s.add_argument("--jump", action="append", default=[])
    s.add_argument("--dot", action="append", default=[]); s.add_argument("--vertical", action="store_true")
    s = sub.add_parser("backdrop"); s.add_argument("page_dir"); s.add_argument("plate")
    s.add_argument("--blur", type=float, default=9); s.add_argument("--dark", type=float, default=.62);
    s = sub.add_parser("scene"); s.add_argument("page_dir"); s.add_argument("plate"); s.add_argument("--mirror", action="store_true")
    s.add_argument("--crop"); s.add_argument("--blank", action="append"); s.add_argument("--blur", type=float, default=10)
    s = sub.add_parser("cutout"); s.add_argument("page_dir"); s.add_argument("src"); s.add_argument("name")
    s.add_argument("--poly", required=True); s.add_argument("--feather", type=float, default=2.0)
    s = sub.add_parser("check"); s.add_argument("page_dir")
    s = sub.add_parser("render"); s.add_argument("page_dir"); s.add_argument("--dpi", type=int, default=110)
    s = sub.add_parser("artifact"); s.add_argument("page_dir")
    s = sub.add_parser("set"); s.add_argument("chapter"); s.add_argument("pages"); s.add_argument("--name")
    a = ap.parse_args()
    {"new": cmd_new, "img": cmd_img, "numberline": cmd_numberline, "backdrop": cmd_backdrop, "scene": cmd_scene, "cutout": cmd_cutout, "check": cmd_check, "render": cmd_render,
     "artifact": cmd_artifact, "set": cmd_set}[a.cmd](a)


if __name__ == "__main__":
    main()
