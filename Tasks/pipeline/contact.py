#!/usr/bin/env python3
"""contact.py: tile rendered page previews into low-res contact sheets for cheap review.

One sheet costs about as many image tokens as two full previews, but shows up to 12 pages,
so the master and art-director can judge rhythm, colour, hero and variety across a run and
open a full preview.png only for the pages they flag.

  contact.py CH01                      every built page of CH01
  contact.py CH01 P001-P040            a range (pages without a preview.png are listed as missing)
  contact.py CH01 P005 P039 P041       named pages
  options: --per 12 (pages per sheet)  --cols 4  --thumb 480 (thumbnail width, px)

Writes PdfSheetsGenTask/<CHxx>/contact/<CHxx>-<first>-<last>.jpg and prints one path per sheet.

montage() is the shared tiler; imggen.py uses qc_sheets() for the labelled QC sheet after a batch fetch.
"""
import argparse
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

TASKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def page_ids(ch_dir, specs):
    if not specs:
        return sorted(d for d in os.listdir(ch_dir) if re.fullmatch(r"P\d{3}", d))
    out = []
    for s in specs:
        m = re.fullmatch(r"P(\d{3})-P?(\d{3})", s)
        if m:
            out += [f"P{n:03d}" for n in range(int(m[1]), int(m[2]) + 1)]
        elif re.fullmatch(r"P\d{3}", s):
            out.append(s)
        else:
            sys.exit(f"bad page spec: {s} (use P005 or P001-P040)")
    return out


def font(size):
    for f in ("DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def montage(entries, path, cols, tw, th, label_h=None):
    """Tile (label, image_path) entries into one JPEG at path: each image fitted into a tw x th cell with
    its label above it. Returns path."""
    if not entries:
        raise ValueError("montage needs at least one image")
    label_h = label_h or max(18, tw // 16)
    pad = 8
    f = font(label_h - 4)
    cols = min(cols, len(entries))
    rows = -(-len(entries) // cols)
    sheet = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + label_h + pad) + pad), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    for k, (label, src) in enumerate(entries):
        x = pad + (k % cols) * (tw + pad)
        y = pad + (k // cols) * (th + label_h + pad)
        with Image.open(src) as raw:
            im = raw.convert("RGB")
        im.thumbnail((tw, th), Image.LANCZOS)
        sheet.paste(im, (x + (tw - im.width) // 2, y + label_h))
        d.text((x + 2, y + 1), label, fill=(255, 220, 120), font=f)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    sheet.save(path, quality=82)
    return path


def qc_sheets(entries, out_base, cols=4, cell=380, rows=3):
    """QC sheets of (label, image_path) entries, each sheet <= ~1600 px on the long side
    (4 x 3 cells of 380 px -> 1560 x 1244). Writes <out_base>-1.jpg, -2.jpg, ... and returns their paths."""
    per = cols * rows
    return [montage(entries[i:i + per], f"{out_base}-{i // per + 1}.jpg", cols, cell, cell, label_h=26)
            for i in range(0, len(entries), per)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("chapter")
    ap.add_argument("pages", nargs="*")
    ap.add_argument("--per", type=int, default=12)
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--thumb", type=int, default=480)
    a = ap.parse_args()

    ch_dir = os.path.join(TASKS, "PdfSheetsGenTask", a.chapter)
    if not os.path.isdir(ch_dir):
        sys.exit(f"no such chapter folder: {ch_dir}")
    ids = page_ids(ch_dir, a.pages)
    have = [p for p in ids if os.path.isfile(os.path.join(ch_dir, p, "preview.png"))]
    missing = [p for p in ids if p not in have]
    if not have:
        sys.exit("no previews found" + (f" (missing: {' '.join(missing)})" if missing else ""))

    out_dir = os.path.join(ch_dir, "contact")
    os.makedirs(out_dir, exist_ok=True)
    tw = a.thumb
    for i in range(0, len(have), a.per):
        group = have[i:i + a.per]
        path = os.path.join(out_dir, f"{a.chapter}-{group[0]}-{group[-1]}.jpg")
        montage([(p, os.path.join(ch_dir, p, "preview.png")) for p in group], path, a.cols, tw, tw * 3 // 4)  # 12x9 in
        print(os.path.relpath(path, TASKS))
    if missing:
        nums = [int(p[1:]) for p in missing]
        runs, start = [], nums[0]
        for prev, n in zip(nums, nums[1:] + [None]):
            if n != prev + 1:
                runs.append(f"P{start:03d}" if start == prev else f"P{start:03d}-P{prev:03d}")
                start = n
        print(f"missing preview ({len(missing)}):", " ".join(runs))


if __name__ == "__main__":
    main()
