#!/usr/bin/env python3
"""api_gen.py: OpenAI Images API route for the bg.py queue (gpt-image-2.5 and friends).

Takes one job from the queue (or the job you name), sends its composed prompt, saves the
image to the job's SAVE AS path, logs token usage and estimated cost, then runs
`bg.py done`. Records with reference images use /v1/images/edits with the accepted
reference files attached in order. The master (no references) uses /v1/images/generations.

The API key is read from the environment (OPENAI_API_KEY or CHATGPT_API) or from .env
in this folder. It is never printed or written anywhere.

  python3 api_gen.py --set samples --worker API1                       # next ready job, 2K, high
  python3 api_gen.py --job 001-B --worker API1 --preset 4k --quality max
  python3 api_gen.py --set full --worker API2 --dry-run                # show the request, spend nothing

Sizes ("2k" is the default): 16:9 2048x1152, 4:3 2048x1536, 3:2 2160x1440.
"1k" (cheap prompt tests): 1280x720, 1024x768, 1056x704 (exact ratios, edges in multiples of 16).
"4k": 3840x2160, 3264x2448, 3504x2336. `done` keeps the native file and upscales to the
Draft 02 target.
"""
import argparse
import base64
import datetime as _dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://api.openai.com/v1/images"
PRESETS = {"1k": {"16:9": "1280x720", "4:3": "1024x768", "3:2": "1056x704"},
           "2k": {"16:9": "2048x1152", "4:3": "2048x1536", "3:2": "2160x1440"},
           "4k": {"16:9": "3840x2160", "4:3": "3264x2448", "3:2": "3504x2336"}}
# USD per 1M tokens (gpt-image-2 / 2.5 published rates): text in, image in, image out
RATES = {"text_in": 5.0, "image_in": 8.0, "image_out": 30.0}


def load_key():
    for k in ("OPENAI_API_KEY", "CHATGPT_API"):
        if os.environ.get(k):
            return os.environ[k].strip()
    path = os.path.join(HERE, ".env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            m = re.match(r"""^\s*(?:export\s+)?(CHATGPT_API|OPENAI_API_KEY)\s*=\s*["']?(.*?)["']?\s*$""", line)
            if m and m.group(2):
                return m.group(2)
    sys.exit("No API key found: put CHATGPT_API=... in .env (it is never printed).")


def scrub(text, key):
    return text.replace(key, "<key>") if key else text


def run_bg(*args):
    r = subprocess.run([sys.executable, os.path.join(HERE, "bg.py"), *args], capture_output=True, text=True, cwd=HERE)
    return r.returncode, (r.stdout + r.stderr).strip()


def job_payload(job_id, worker):
    sys.path.insert(0, HERE)
    import bg  # noqa: E402  (same folder)
    recs = bg.parse_records()
    j = bg.find_job(recs, job_id)
    if not j:
        sys.exit(f"unknown job {job_id}")
    return bg.job_payload(recs, j, worker)


def multipart(fields, files):
    boundary = "----bg" + uuid.uuid4().hex
    body = bytearray()
    for name, value in fields.items():
        body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n").encode("utf-8")
    for name, path in files:
        body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"; "
                 f"filename=\"{os.path.basename(path)}\"\r\nContent-Type: image/png\r\n\r\n").encode("utf-8")
        with open(path, "rb") as fh:
            body += fh.read()
        body += b"\r\n"
    body += f"--{boundary}--\r\n".encode("utf-8")
    return bytes(body), f"multipart/form-data; boundary={boundary}"


def call(key, endpoint, fields, files, timeout):
    if files:
        data, ctype = multipart(fields, files)
    else:
        data, ctype = json.dumps(fields).encode("utf-8"), "application/json"
    req = urllib.request.Request(f"{API}/{endpoint}", data=data,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": ctype})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def estimate(usage):
    if not usage:
        return None
    det = usage.get("input_tokens_details") or {}
    text_in = det.get("text_tokens", usage.get("input_tokens", 0) - det.get("image_tokens", 0))
    img_in = det.get("image_tokens", 0)
    out = usage.get("output_tokens", 0)
    return (text_in * RATES["text_in"] + img_in * RATES["image_in"] + out * RATES["image_out"]) / 1e6


def log_usage(job, model, endpoint, size, quality, secs, usage, revised):
    cost = estimate(usage)
    logp = os.path.join(HERE, "output", "_logs", "api-usage.tsv")
    os.makedirs(os.path.dirname(logp), exist_ok=True)
    new = not os.path.exists(logp)
    with open(logp, "a", encoding="utf-8") as fh:
        if new:
            fh.write("time\tjob\tmodel\tendpoint\tsize\tquality\tseconds\tinput_tokens\toutput_tokens\test_usd\trevised_prompt\n")
        fh.write(f"{_dt.datetime.now():%Y-%m-%d %H:%M:%S}\t{job}\t{model}\t{endpoint}\t{size}\t{quality}\t{secs:.0f}\t"
                 f"{usage.get('input_tokens', '')}\t{usage.get('output_tokens', '')}\t"
                 f"{'' if cost is None else f'{cost:.4f}'}\t{(revised or '')[:200]}\n")
    return cost


def fix(a):
    """Targeted edit of a job's current image: changes only what --fix describes."""
    d = job_payload(a.job, a.worker)
    nat_dir = os.path.join(HERE, "output", "_candidates" if "-" in a.job else "", "native")
    native = os.path.join(os.path.normpath(nat_dir), os.path.basename(d["save_as"])[:-4] + "_native.png")
    if not os.path.exists(native):
        sys.exit(f"no current native image for {a.job} ({native}); generate it first")
    from PIL import Image
    with Image.open(native) as im:
        size = f"{im.width}x{im.height}"
    prompt = ("Use case: precise-object-edit\nInput images: Image 1: the current location image to correct.\n"
              f"{a.fix.strip()}\nKeep everything else exactly the same: camera, composition, architecture, lighting, "
              "colours and every other object. No people, hands or figures; no captions, arrows or watermarks; "
              "no new lettering anywhere.")
    print(f"FIX {a.job} · edits · {a.model} · {size} · quality {a.quality} · prompt {len(prompt)} chars")
    if a.dry_run:
        print(prompt)
        return 0
    n = 1
    while os.path.exists(native[:-4] + f".v{n}.png"):
        n += 1
    keep = native[:-4] + f".v{n}.png"
    shutil.copy2(native, keep)
    key = load_key()
    t0 = time.time()
    try:
        res = call(key, "edits", {"model": a.model, "prompt": prompt, "size": size, "quality": a.quality, "n": 1},
                   [("image", native)], a.timeout)
    except urllib.error.HTTPError as e:
        sys.exit(f"API error {e.code}: {scrub(e.read().decode('utf-8', 'replace'), key)[:800]} (nothing changed)")
    except Exception as e:  # noqa: BLE001
        sys.exit(f"request failed: {scrub(str(e), key)} (nothing changed)")
    secs = time.time() - t0
    item = (res.get("data") or [{}])[0]
    if not item.get("b64_json"):
        sys.exit("no image in the response (nothing changed): " + scrub(json.dumps(res)[:500], key))
    with open(d["save_as"], "wb") as fh:
        fh.write(base64.b64decode(item["b64_json"]))
    cost = log_usage(a.job + "-fix", a.model, "edits", size, a.quality, secs, res.get("usage") or {},
                     item.get("revised_prompt"))
    print(f"fixed image saved in {secs:.0f}s; previous native kept as {keep}; est. ${'?' if cost is None else f'{cost:.3f}'}")
    rc, out = run_bg("done", a.job, "--worker", a.worker + "-fix", "--force")
    print(out)
    return rc


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--set", choices=["samples", "full"], default="samples")
    ap.add_argument("--worker", default="API1")
    ap.add_argument("--prefer", default="")
    ap.add_argument("--job", help="re-run a specific job (e.g. 001-B) instead of claiming the next one")
    ap.add_argument("--model", default="gpt-image-2.5-sunburst")
    ap.add_argument("--preset", choices=list(PRESETS), default="2k")
    ap.add_argument("--size", help="explicit WIDTHxHEIGHT (overrides --preset)")
    ap.add_argument("--quality", default="high", help="low | medium | high | xhigh | max | auto (2.5 models)")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--fix", metavar="TEXT", help="targeted fix of the job's current image (needs --job); the old "
                    "native is kept as *_native.vN.png")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if a.fix:
        if not a.job:
            sys.exit("--fix needs --job")
        return fix(a)
    if a.job:
        d = job_payload(a.job, a.worker)
    else:
        args = ["claim", "--set", a.set, "--worker", a.worker, "--json"] + (["--prefer", a.prefer] if a.prefer else [])
        if a.dry_run:
            args.append("--dry-run")
        rc, out = run_bg(*args)
        try:
            d = json.loads(out)
        except json.JSONDecodeError:
            sys.exit(out)
        if "job" not in d:
            rc2, txt = run_bg("claim", "--set", a.set, "--worker", a.worker, "--dry-run")
            sys.exit(txt)

    size = a.size or PRESETS[a.preset][d["ratio"]]
    files = [("image[]" if len(d["refs"]) > 1 else "image", r["path"]) for r in d["refs"]]
    endpoint = "edits" if files else "generations"
    fields = {"model": a.model, "prompt": d["prompt"], "size": size, "quality": a.quality, "n": 1}
    print(f"JOB {d['job']} · {d['id']} {d['title']} · {endpoint} · {a.model} · {size} · quality {a.quality}"
          + (f" · {len(files)} reference image(s)" if files else " · text-only"))
    if a.dry_run:
        print(f"prompt: {len(d['prompt'])} chars; would save to {d['save_as']}")
        for _, f in files:
            print(f"  attach {f}")
        return 0

    key = load_key()
    t0 = time.time()
    try:
        res = call(key, endpoint, fields, files, a.timeout)
    except urllib.error.HTTPError as e:
        msg = scrub(e.read().decode("utf-8", "replace"), key)[:800]
        run_bg("release", d["job"])
        sys.exit(f"API error {e.code}: {msg}\n(job released; nothing saved)")
    except Exception as e:  # noqa: BLE001
        run_bg("release", d["job"])
        sys.exit(f"request failed: {scrub(str(e), key)} (job released)")
    secs = time.time() - t0
    item = (res.get("data") or [{}])[0]
    b64 = item.get("b64_json")
    if not b64:
        run_bg("release", d["job"])
        sys.exit("no image in the response (job released): " + scrub(json.dumps(res)[:500], key))
    os.makedirs(os.path.dirname(d["save_as"]), exist_ok=True)
    with open(d["save_as"], "wb") as fh:
        fh.write(base64.b64decode(b64))
    usage = res.get("usage") or {}
    cost = estimate(usage)
    logp = os.path.join(HERE, "output", "_logs", "api-usage.tsv")
    os.makedirs(os.path.dirname(logp), exist_ok=True)
    new = not os.path.exists(logp)
    with open(logp, "a", encoding="utf-8") as fh:
        if new:
            fh.write("time\tjob\tmodel\tendpoint\tsize\tquality\tseconds\tinput_tokens\toutput_tokens\test_usd\trevised_prompt\n")
        fh.write(f"{_dt.datetime.now():%Y-%m-%d %H:%M:%S}\t{d['job']}\t{a.model}\t{endpoint}\t{size}\t{a.quality}\t"
                 f"{secs:.0f}\t{usage.get('input_tokens', '')}\t{usage.get('output_tokens', '')}\t"
                 f"{'' if cost is None else f'{cost:.4f}'}\t{(item.get('revised_prompt') or '')[:200]}\n")
    print(f"saved {d['save_as']} in {secs:.0f}s; tokens in/out {usage.get('input_tokens', '?')}/"
          f"{usage.get('output_tokens', '?')}; est. ${'?' if cost is None else f'{cost:.3f}'}")
    rc, out = run_bg("done", d["job"], "--worker", a.worker)
    print(out)
    print("NEXT: open the accepted file, zoom-check the IMAGE CHECKS, then let the user pick or reject.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
