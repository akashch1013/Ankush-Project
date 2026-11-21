#!/usr/bin/env python3
"""v2/gen.py: generate the v2 prompt pairs (text-only and with reference images) through the OpenAI Images API.

Jobs live in jobs.json; each prompt is prompts/<job>.txt, sent verbatim. Jobs with refs go to
/v1/images/edits with the reference PNGs attached in order (Image 1, Image 2...); the others go to
/v1/images/generations. Results land in out/<job>.png (an older result is kept as out/<job>.prevN.png),
usage in out/usage.tsv, and out/SHEET.png puts each record's no-ref and ref results side by side.
Key loading, the HTTP call and the cost estimate are api_gen.py's; the key is never printed.

  python3 v2/gen.py --dry-run                 # show every request, spend nothing
  python3 v2/gen.py 001-noref                 # one job
  python3 v2/gen.py --workers 4               # all jobs, 4 at a time
  python3 v2/gen.py --sheet                   # rebuild the comparison sheet only
"""
import argparse
import base64
import datetime as _dt
import json
import os
import sys
import threading
import time
import urllib.error
from concurrent.futures import ThreadPoolExecutor

V = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(V))
import api_gen  # noqa: E402  (parent folder: load_key, call, estimate, scrub, PRESETS)

OUT = os.path.join(V, "out")
LOG_LOCK = threading.Lock()


def load_jobs():
    with open(os.path.join(V, "jobs.json"), encoding="utf-8") as fh:
        return json.load(fh)["jobs"]


def log_usage(job, a, endpoint, size, secs, usage):
    cost = api_gen.estimate(usage)
    logp = os.path.join(OUT, "usage.tsv")
    with LOG_LOCK:
        new = not os.path.exists(logp)
        with open(logp, "a", encoding="utf-8") as fh:
            if new:
                fh.write("time\tjob\tmodel\tendpoint\tsize\tquality\tseconds\tinput_tokens\toutput_tokens\test_usd\n")
            fh.write(f"{_dt.datetime.now():%Y-%m-%d %H:%M:%S}\t{job}\t{a.model}\t{endpoint}\t{size}\t{a.quality}\t"
                     f"{secs:.0f}\t{usage.get('input_tokens', '')}\t{usage.get('output_tokens', '')}\t"
                     f"{'' if cost is None else f'{cost:.4f}'}\n")
    return cost


def run(job, a, key):
    with open(os.path.join(V, job["prompt"]), encoding="utf-8") as fh:
        prompt = fh.read().strip()
    size = a.size or api_gen.PRESETS[a.preset][job["ratio"]]
    refs = [os.path.join(V, r["file"]) for r in job["refs"]]
    files = [("image[]" if len(refs) > 1 else "image", r) for r in refs]
    endpoint = "edits" if files else "generations"
    head = (f"{job['id']} · {endpoint} · {a.model} · {size} · quality {a.quality} · prompt {len(prompt)} chars"
            + (f" · {len(refs)} reference image(s)" if refs else " · text-only"))
    if a.dry_run:
        return head + "".join(f"\n    Image {i}: {os.path.relpath(r, V)}" for i, r in enumerate(refs, 1))
    fields = {"model": a.model, "prompt": prompt, "size": size, "quality": a.quality, "n": 1}
    t0 = time.time()
    try:
        res = api_gen.call(key, endpoint, fields, files, a.timeout)
    except urllib.error.HTTPError as e:
        return f"FAIL {head}\n    API error {e.code}: {api_gen.scrub(e.read().decode('utf-8', 'replace'), key)[:600]}"
    except Exception as e:  # noqa: BLE001
        return f"FAIL {head}\n    request failed: {api_gen.scrub(str(e), key)}"
    secs = time.time() - t0
    b64 = ((res.get("data") or [{}])[0]).get("b64_json")
    if not b64:
        return f"FAIL {head}\n    no image in the response: {api_gen.scrub(json.dumps(res)[:400], key)}"
    dest = os.path.join(OUT, job["id"] + ".png")
    if os.path.exists(dest):
        n = 1
        while os.path.exists(os.path.join(OUT, f"{job['id']}.prev{n}.png")):
            n += 1
        os.replace(dest, os.path.join(OUT, f"{job['id']}.prev{n}.png"))
    with open(dest, "wb") as fh:
        fh.write(base64.b64decode(b64))
    usage = res.get("usage") or {}
    cost = log_usage(job["id"], a, endpoint, size, secs, usage)
    return (f"OK   {head}\n    saved {os.path.relpath(dest, V)} in {secs:.0f}s; tokens in/out "
            f"{usage.get('input_tokens', '?')}/{usage.get('output_tokens', '?')}; est. "
            f"${'?' if cost is None else f'{cost:.3f}'}")


def sheet(jobs):
    """out/SHEET.png: one row per record, no-ref on the left and ref on the right."""
    from PIL import Image, ImageDraw, ImageFont
    w = 960
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    rows = []
    for rec in sorted({j["record"] for j in jobs}):
        cells = []
        for variant in ("noref", "ref"):
            j = next((x for x in jobs if x["record"] == rec and x["id"].endswith("-" + variant)), None)
            path = j and os.path.join(OUT, j["id"] + ".png")
            if path and os.path.exists(path):
                im = Image.open(path).convert("RGB")
                cells.append((f"{rec} {j['title']} · {'text only' if variant == 'noref' else 'with refs'}",
                              im.resize((w, round(im.height * w / im.width)))))
        if cells:
            rows.append(cells)
    if not rows:
        return None
    heights = [max(im.height for _, im in r) + 40 for r in rows]
    canvas = Image.new("RGB", (2 * w + 12, sum(heights)), (16, 18, 30))
    d = ImageDraw.Draw(canvas)
    y = 0
    for r, h in zip(rows, heights):
        for i, (label, im) in enumerate(r):
            x = i * (w + 12)
            d.text((x + 10, y + 8), label, fill=(240, 205, 120), font=font)
            canvas.paste(im, (x, y + 40))
        y += h
    dest = os.path.join(OUT, "SHEET.png")
    canvas.save(dest)
    return dest


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("jobs", nargs="*", help="job ids such as 001-noref (default: all)")
    ap.add_argument("--model", default="gpt-image-2.5-sunburst")
    ap.add_argument("--preset", choices=list(api_gen.PRESETS), default="1k")
    ap.add_argument("--size", help="explicit WIDTHxHEIGHT (overrides --preset)")
    ap.add_argument("--quality", default="high")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--sheet", action="store_true", help="only rebuild out/SHEET.png")
    a = ap.parse_args()

    jobs = load_jobs()
    if a.sheet:
        print(sheet(jobs) or "nothing generated yet")
        return 0
    todo = [j for j in jobs if not a.jobs or j["id"] in a.jobs]
    unknown = set(a.jobs) - {j["id"] for j in jobs}
    if unknown:
        sys.exit(f"unknown job(s): {', '.join(sorted(unknown))}")
    os.makedirs(OUT, exist_ok=True)
    key = None if a.dry_run else api_gen.load_key()
    with ThreadPoolExecutor(max_workers=max(1, a.workers)) as pool:
        for line in pool.map(lambda j: run(j, a, key), todo):
            print(line, flush=True)
    if not a.dry_run:
        print("sheet:", sheet(jobs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
