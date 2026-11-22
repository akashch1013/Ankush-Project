#!/usr/bin/env python3
"""imggen.py: the ChandRush image tool for every stage (backgrounds and final panel art).
OpenAI Images API (gpt-image-2.5-sunburst) through the **Batch API only** (50% off).

A workspace (--ws DIR) holds:
  jobs.json         what to make: model, default quality/size and one entry per item (see SCHEMA below)
  prompts/<ID>.md   the item's prompt; only the text under '## PROMPT' is sent ('## CHECKS' is QC notes)
  state.json        status and call count per item (written by this tool)
  out/<ID>.png      the current image of each item; earlier attempts in out/history/
  batches/<name>/   requests, manifest, results of each submitted batch
  usage.tsv         every paid call with estimated USD (also appended to Tasks/pipeline/usage-all.tsv)

Commands (run from anywhere):
  status                              table of items: wave, status, calls, quality, refs
  check [ID...]                       refs exist, prompts present, sizes valid (free)
  dry-run ID                          show exactly what would be sent (prompt + refs in order, no network)
  batch build NAME (ID... | --ready | --wave N)   build requests (gen for todo/regen items, fix for queued fixes)
  batch submit NAME                   upload + start the batch
  batch wait NAME [--every 60]        poll until done, then fetch (run it in the background)
  batch fetch|status|cancel NAME      | batch list
  fix ID "one precise change" [--ref PATH ...]   queue a targeted edit of the current image for the next batch
  qc ID pass|fail [--regen] [--note "..."]       record the verdict (pass -> approved; usable as item:<ID> ref)
  accept ID --note "defect"           accept at the call cap (logs to ACCEPTED-AT-CAP.md)
  zoom ID x0,y0,x1,y1 [--scale 2]     crop (fractions) to out/zoom/<ID>.png for inspection
  cost                                total estimated spend of this workspace

Rules enforced here:
  * No immediate (non-batch) call unless --immediate-approved is given, which is only allowed when the user
    explicitly asked for it in the conversation.
  * quality 'max' refuses without --allow-max (user approval). Default quality is 'high'.
  * At most 3 calls per item (gen + fixes); --force only with the user's approval.
  * The API key is read from OPENAI_API_KEY / CHATGPT_API or BagroundGenTask/.env and never printed.

SCHEMA of jobs.json:
{
  "project": "chandrush-ch02-panels",
  "model": "gpt-image-2.5-sunburst", "quality": "high", "size": "1536x1024", "max_calls": 3,
  "items": {
    "P003-1": {"prompt": "prompts/P003-1.md",
               "refs": ["BagroundGenTask/ch02/out/plates/L02_B.png",            # paths relative to Tasks/
                        "../Charactors/CHANDRUSH CHARACTERS/AHANA CHARACTER SHEET.png",
                        "item:P002-2"],                                         # approved output of another item
               "size": "1536x1024", "quality": "high", "note": "why xhigh, if set"}
  }
}
An item's wave = 1 + the highest wave of the items it references with item:<ID>. --ready picks every
todo/regen item whose item: refs are all approved or accepted, plus every item with a queued fix.
"""
import argparse
import base64
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import uuid

PIPE = os.path.dirname(os.path.abspath(__file__))
TASKS = os.path.dirname(PIPE)
API = "https://api.openai.com/v1"
# USD per 1M tokens for gpt-image-2.5 (Sept 2026); batch is half of standard
RATES = {"sync": {"text": 5.0, "image": 8.0, "out": 30.0}, "batch": {"text": 2.5, "image": 4.0, "out": 15.0}}
BATCH_LIMIT = 190 * 1024 * 1024
TERMINAL = {"completed", "failed", "expired", "cancelled"}
DONE = ("approved", "accepted")
FIX = ("Use case: precise correction of Image 1, a ChandRush comic image ({rid}).\n"
       "Input images: Image 1 is the current image.{extra}\n"
       "Change only this: {instruction}\n"
       "Keep everything else exactly as it is in Image 1: camera, framing, perspective, architecture, characters' "
       "faces, hair, clothing and proportions, materials, colours, lighting, every other object, every existing "
       "physical inscription and every empty area reserved for lettering. Output the same image with only that "
       "correction. Do not add any text, speech bubble, caption, label, arrow or watermark.")


# ---------------------------------------------------------------- basics

def now():
    return dt.datetime.now().isoformat(timespec="seconds")


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


class WS:
    def __init__(self, path):
        self.dir = os.path.abspath(path)
        self.jobs = load_json(self.p("jobs.json"))
        if not self.jobs:
            sys.exit(f"no jobs.json in {self.dir}")
        self.jobs.setdefault("model", "gpt-image-2.5-sunburst")
        self.jobs.setdefault("quality", "high")
        self.jobs.setdefault("size", "1024x768")
        self.jobs.setdefault("max_calls", 3)
        self.items = self.jobs["items"]
        st = load_json(self.p("state.json"), {"items": {}, "fix_queue": {}})
        for rid in self.items:
            st["items"].setdefault(rid, {"status": "todo", "attempts": [], "note": ""})
        self.st = st

    def p(self, *parts):
        return os.path.join(self.dir, *parts)

    def save(self):
        save_json(self.p("state.json"), self.st)

    def item(self, rid):
        if rid not in self.items:
            sys.exit(f"unknown item {rid}")
        return self.items[rid]

    def calls(self, rid):
        return len(self.st["items"][rid]["attempts"])

    def quality(self, rid):
        return self.item(rid).get("quality", self.jobs["quality"])

    def size(self, rid):
        return self.item(rid).get("size", self.jobs["size"])

    def deps(self, rid):
        return [r[5:] for r in self.item(rid).get("refs", []) if r.startswith("item:")]

    def wave(self, rid, seen=()):
        if rid in seen:
            sys.exit(f"circular item: refs at {rid}")
        return 1 + max([self.wave(d, seen + (rid,)) for d in self.deps(rid)] or [0])

    def ref_file(self, ref):
        if ref.startswith("item:"):
            return self.p("out", ref[5:] + ".png")
        return ref if os.path.isabs(ref) else os.path.normpath(os.path.join(TASKS, ref))

    def prompt(self, rid):
        path = self.p(self.item(rid).get("prompt", f"prompts/{rid}.md"))
        if not os.path.exists(path):
            raise RuntimeError(f"{rid}: prompt file {os.path.relpath(path, self.dir)} is missing")
        text = open(path, encoding="utf-8").read()
        m = re.search(r"^##\s*PROMPT\s*$(.*?)(?=^##\s|\Z)", text, re.S | re.M)
        body = (m.group(1) if m else text).strip()
        if len(body) < 200:
            raise RuntimeError(f"{rid}: prompt is too short ({len(body)} chars); write the full prompt under ## PROMPT")
        return body


def ref_jpeg(path, cache_dir):
    """References go as JPEG data URLs (long edge <= 1536) to keep requests small. Cached by path+mtime."""
    from PIL import Image
    key = hashlib.sha1(f"{path}|{os.path.getmtime(path)}".encode()).hexdigest()[:16]
    out = os.path.join(cache_dir, key + ".jpg")
    if not os.path.exists(out):
        os.makedirs(cache_dir, exist_ok=True)
        im = Image.open(path).convert("RGB")
        im.thumbnail((1536, 1536))
        im.save(out, "JPEG", quality=90)
    with open(out, "rb") as fh:
        return "data:image/jpeg;base64," + base64.b64encode(fh.read()).decode("ascii")


def check_size(size):
    m = re.fullmatch(r"(\d+)x(\d+)", size)
    if not m:
        return f"size {size} is not WxH"
    w, h = map(int, m.groups())
    if w % 16 or h % 16:
        return f"size {size}: both edges must be multiples of 16"
    if max(w, h) > 2048 or max(w, h) / min(w, h) > 3:
        return f"size {size}: keep the long edge <= 2048 and the ratio <= 3:1"
    return None


# ---------------------------------------------------------------- API

def load_key():
    for k in ("OPENAI_API_KEY", "CHATGPT_API"):
        if os.environ.get(k):
            return os.environ[k].strip()
    for path in (os.path.join(TASKS, ".env"), os.path.join(TASKS, "BagroundGenTask", ".env")):
        if os.path.exists(path):
            for line in open(path, encoding="utf-8").read().splitlines():
                m = re.match(r"""^\s*(?:export\s+)?(CHATGPT_API|OPENAI_API_KEY)\s*=\s*["']?(.*?)["']?\s*$""", line)
                if m and m.group(2):
                    return m.group(2)
    sys.exit("No API key: put CHATGPT_API=... in Tasks/BagroundGenTask/.env (it is never printed).")


def multipart(fields, files):
    boundary = "----imggen" + uuid.uuid4().hex
    body = bytearray()
    for name, value in fields.items():
        body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode()
    for name, path, ctype in files:
        body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"; filename=\"{os.path.basename(path)}\""
                 f"\r\nContent-Type: {ctype}\r\n\r\n").encode()
        with open(path, "rb") as fh:
            body += fh.read()
        body += b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    return bytes(body), f"multipart/form-data; boundary={boundary}"


def api(key, method, path, body=None, files=None, raw=False, timeout=1500):
    if files:
        data, ctype = multipart(body or {}, files)
    elif body is not None:
        data, ctype = json.dumps(body).encode("utf-8"), "application/json"
    else:
        data, ctype = None, None
    headers = {"Authorization": f"Bearer {key}"}
    if ctype:
        headers["Content-Type"] = ctype
    for attempt in range(3):
        req = urllib.request.Request(API + path, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                content = resp.read()
            return content if raw else json.loads(content)
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "replace").replace(key, "<key>")[:1500]
            if e.code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(20 * (attempt + 1))
                continue
            raise RuntimeError(f"HTTP {e.code} on {method} {path}: {msg}") from None
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < 2 and method == "GET":  # a timed-out POST may still be billed
                time.sleep(20 * (attempt + 1))
                continue
            raise RuntimeError(f"network error on {method} {path}: {str(e).replace(key, '<key>')}") from None


def estimate(usage, mode):
    r = RATES[mode]
    det = usage.get("input_tokens_details") or {}
    img_in = det.get("image_tokens", 0)
    text_in = det.get("text_tokens", max(0, usage.get("input_tokens", 0) - img_in))
    return (text_in * r["text"] + img_in * r["image"] + usage.get("output_tokens", 0) * r["out"]) / 1e6


def log_usage(ws, rid, kind, via, usage, usd):
    det = usage.get("input_tokens_details") or {}
    row = (f"{now()}\t{ws.jobs.get('project', os.path.basename(ws.dir))}\t{rid}\t{kind}\t{via}\t"
           f"{det.get('text_tokens', '')}\t{det.get('image_tokens', '')}\t{usage.get('output_tokens', '')}\t{usd:.4f}\n")
    for path in (ws.p("usage.tsv"), os.path.join(PIPE, "usage-all.tsv")):
        new = not os.path.exists(path)
        with open(path, "a", encoding="utf-8") as fh:
            if new:
                fh.write("time\tproject\titem\tkind\tvia\ttext_in\timage_in\toutput\test_usd\n")
            fh.write(row)


# ---------------------------------------------------------------- jobs

def make_job(ws, rid, kind, instruction=None, extra_refs=(), allow_max=False):
    quality = ws.quality(rid)
    if quality == "max" and not allow_max:
        raise RuntimeError(f"{rid}: quality max needs the user's explicit approval (then pass --allow-max)")
    size = ws.size(rid)
    bad = check_size(size)
    if bad:
        raise RuntimeError(f"{rid}: {bad}")
    if kind == "gen":
        prompt = ws.prompt(rid)
        refs = list(ws.item(rid).get("refs", []))
    else:
        extra = "".join(f" Image {i + 2} is a reference for the correction only; copy nothing else from it."
                        for i in range(len(extra_refs)))
        prompt = FIX.format(rid=rid, instruction=instruction.strip(), extra=extra)
        refs = [f"item:{rid}"] + list(extra_refs)
    files = [ws.ref_file(r) for r in refs]
    for r, f in zip(refs, files):
        if not os.path.exists(f):
            raise RuntimeError(f"{rid}: reference {r} -> {f} is missing" +
                               (" (approve that item first)" if r.startswith("item:") else ""))
    body = {"model": ws.jobs["model"], "prompt": prompt, "size": size, "quality": quality, "n": 1,
            "output_format": "png"}
    if files:
        body["images"] = [{"image_url": ref_jpeg(f, ws.p("refcache"))} for f in files]
    return {"rid": rid, "kind": kind, "endpoint": "/images/edits" if files else "/images/generations",
            "body": body, "prompt": prompt, "prompt_sha": hashlib.sha256(prompt.encode()).hexdigest()[:12],
            "refs": refs, "instruction": instruction, "quality": quality, "size": size}


def store(ws, rid, job, b64, usage, via):
    rs = ws.st["items"][rid]
    os.makedirs(ws.p("out", "history"), exist_ok=True)
    cur = ws.p("out", f"{rid}.png")
    if os.path.exists(cur):
        os.replace(cur, ws.p("out", "history", f"{rid}.a{len(rs['attempts'])}.png"))
    with open(cur, "wb") as fh:
        fh.write(base64.b64decode(b64))
    usd = estimate(usage or {}, "batch" if via.startswith("batch") else "sync")
    rs["attempts"].append({"n": len(rs["attempts"]) + 1, "kind": job["kind"], "via": via, "at": now(),
                           "quality": job["quality"], "size": job["size"], "prompt_sha": job["prompt_sha"],
                           "refs": job["refs"], "instruction": job.get("instruction"), "usd": round(usd, 4)})
    rs["status"], rs["note"] = "review", ""
    rs.pop("prev_status", None)
    log_usage(ws, rid, job["kind"], via, usage or {}, usd)
    return usd


# ---------------------------------------------------------------- commands

def cmd_status(ws, a):
    print(f"{'item':14} wave  {'status':9} calls quality size       refs")
    for rid in ws.items:
        rs = ws.st["items"][rid]
        fixq = " +fix queued" if rid in ws.st["fix_queue"] else ""
        print(f"{rid:14} {ws.wave(rid):>4}  {rs['status']:9} {ws.calls(rid):>5} {ws.quality(rid):7} {ws.size(rid):10} "
              f"{', '.join(os.path.basename(r) for r in ws.item(rid).get('refs', []))}{fixq}"
              + (f"\n{'':16}note: {rs['note']}" if rs.get("note") else ""))


def cmd_check(ws, a):
    bad = 0
    for rid in a.ids or ws.items:
        errs = []
        try:
            ws.prompt(rid)
        except RuntimeError as e:
            errs.append(str(e))
        for r in ws.item(rid).get("refs", []):
            if r.startswith("item:"):
                if r[5:] not in ws.items:
                    errs.append(f"{r}: no such item")
            elif not os.path.exists(ws.ref_file(r)):
                errs.append(f"missing ref {r}")
        s = check_size(ws.size(rid))
        if s:
            errs.append(s)
        if ws.quality(rid) not in ("low", "medium", "high", "xhigh", "max"):
            errs.append(f"quality {ws.quality(rid)}")
        if ws.quality(rid) == "xhigh" and not ws.item(rid).get("note"):
            errs.append("xhigh needs a 'note' saying why this image is genuinely hard")
        print(f"{'ok  ' if not errs else 'BAD '}{rid}" + "".join(f"\n     - {e}" for e in errs))
        bad += bool(errs)
    if bad:
        sys.exit(f"{bad} item(s) not ready")


def cmd_dry(ws, a):
    job = make_job(ws, a.id, "gen")
    print(f"{job['endpoint']} · {ws.jobs['model']} · {job['size']} · quality {job['quality']} · sha {job['prompt_sha']}")
    for i, r in enumerate(job["refs"], 1):
        print(f"  Image {i}: {r}")
    print("---- PROMPT ----\n" + job["prompt"])


def bdir(ws, name):
    return ws.p("batches", name)


def batch_build(ws, a):
    if a.ids:
        ids = a.ids
    elif a.wave is not None:
        ids = [r for r in ws.items if ws.wave(r) == a.wave]
    elif a.ready:
        ids = list(ws.items)
    else:
        sys.exit("give item IDs, --ready or --wave N")
    jobs, skipped = [], []
    for rid in ids:
        ws.item(rid)
        rs = ws.st["items"][rid]
        cap = ws.calls(rid) >= ws.jobs["max_calls"] and not a.force
        try:
            if rid in ws.st["fix_queue"]:
                if cap:
                    skipped.append(f"{rid}: fix queued but the {ws.jobs['max_calls']}-call cap is reached -> accept it")
                    continue
                fq = ws.st["fix_queue"][rid]
                jobs.append(make_job(ws, rid, "fix", fq["instruction"], fq.get("refs", []), a.allow_max))
                continue
            if rs["status"] not in ("todo", "regen"):
                if a.ids:
                    skipped.append(f"{rid}: status {rs['status']}")
                continue
            if cap:
                skipped.append(f"{rid}: call cap reached -> accept it")
                continue
            waiting = [d for d in ws.deps(rid) if ws.st["items"][d]["status"] not in DONE]
            if waiting:
                skipped.append(f"{rid}: waits for {', '.join(waiting)}")
                continue
            jobs.append(make_job(ws, rid, "gen", allow_max=a.allow_max))
        except RuntimeError as e:
            skipped.append(str(e))
    for s in skipped:
        print("SKIP " + s)
    if not jobs:
        sys.exit("nothing to batch")
    if len({j["endpoint"] for j in jobs}) > 1:
        sys.exit("a batch takes one endpoint; build text-only items in a separate batch")
    os.makedirs(bdir(ws, a.name), exist_ok=False)
    path = os.path.join(bdir(ws, a.name), "requests.jsonl")
    man = {"name": a.name, "created": now(), "endpoint": "/v1" + jobs[0]["endpoint"], "jobs": []}
    with open(path, "w", encoding="utf-8") as fh:
        for j in jobs:
            cid = f"{j['rid']}~{j['kind']}~{ws.calls(j['rid']) + 1}"
            fh.write(json.dumps({"custom_id": cid, "method": "POST", "url": "/v1" + j["endpoint"], "body": j["body"]}) + "\n")
            man["jobs"].append({k: j[k] for k in ("rid", "kind", "quality", "size", "prompt_sha", "refs", "instruction")}
                               | {"custom_id": cid})
            with open(os.path.join(bdir(ws, a.name), f"{j['rid']}-{j['kind']}-prompt.txt"), "w", encoding="utf-8") as pf:
                pf.write(j["prompt"])
    man["bytes"] = os.path.getsize(path)
    save_json(os.path.join(bdir(ws, a.name), "manifest.json"), man)
    if man["bytes"] > BATCH_LIMIT:
        sys.exit(f"requests are {man['bytes'] / 2**20:.0f} MB, over the Batch API limit: build fewer items per batch")
    print(f"batch {a.name}: {len(jobs)} request(s), {man['bytes'] / 2**20:.1f} MB")
    for j in man["jobs"]:
        print(f"  {j['custom_id']:24} {j['quality']:5} {j['size']:10} refs: {', '.join(j['refs'])}")
    print(f"NEXT: imggen.py --ws {os.path.relpath(ws.dir)} batch submit {a.name}")


def batch_submit(ws, a):
    bd = bdir(ws, a.name)
    man = load_json(os.path.join(bd, "manifest.json"))
    if not man:
        sys.exit(f"no batch {a.name} (build it first)")
    if os.path.exists(os.path.join(bd, "batch.json")):
        sys.exit(f"{a.name} was submitted already")
    for j in man["jobs"]:
        if ws.st["items"][j["rid"]]["status"] == "queued":
            sys.exit(f"{j['rid']} is already queued in another batch")
    key = load_key()
    up = api(key, "POST", "/files", {"purpose": "batch"},
             files=[("file", os.path.join(bd, "requests.jsonl"), "application/jsonl")])
    b = api(key, "POST", "/batches", {"input_file_id": up["id"], "endpoint": man["endpoint"], "completion_window": "24h",
                                      "metadata": {"project": ws.jobs.get("project", "chandrush"), "batch": a.name}})
    save_json(os.path.join(bd, "batch.json"), b)
    for j in man["jobs"]:
        rs = ws.st["items"][j["rid"]]
        rs["prev_status"], rs["status"] = rs["status"], "queued"
        if j["kind"] == "fix":
            ws.st["fix_queue"].pop(j["rid"], None)
    ws.save()
    print(f"submitted {a.name}: {b['id']} ({b['status']}), {len(man['jobs'])} request(s)")
    print(f"NEXT: imggen.py --ws {os.path.relpath(ws.dir)} batch wait {a.name}   (in the background)")


def _refresh(ws, key, name):
    path = os.path.join(bdir(ws, name), "batch.json")
    b = load_json(path)
    if not b:
        sys.exit(f"{name} has not been submitted")
    b = api(key, "GET", f"/batches/{b['id']}")
    save_json(path, b)
    return b


def _line(name, b):
    c = b.get("request_counts") or {}
    return f"{name}: {b['status']} · {c.get('completed', 0)}/{c.get('total', 0)} done, {c.get('failed', 0)} failed"


def batch_status(ws, a):
    print(_line(a.name, _refresh(ws, load_key(), a.name)))


def batch_wait(ws, a):
    key, t0 = load_key(), time.time()
    while True:
        b = _refresh(ws, key, a.name)
        print(f"{now()} {_line(a.name, b)}", flush=True)
        if b["status"] in TERMINAL:
            break
        if time.time() - t0 > a.max_hours * 3600:
            sys.exit(f"still {b['status']} after {a.max_hours} h; run `batch wait {a.name}` again later")
        time.sleep(a.every)
    a.force = False
    batch_fetch(ws, a)


def batch_fetch(ws, a):
    bd = bdir(ws, a.name)
    key = load_key()
    b = _refresh(ws, key, a.name)
    if b["status"] not in TERMINAL:
        sys.exit(_line(a.name, b) + " (not finished)")
    if os.path.exists(os.path.join(bd, "fetched")) and not a.force:
        sys.exit(f"{a.name} was fetched already (--force to process it again)")
    jobs = {j["custom_id"]: j for j in load_json(os.path.join(bd, "manifest.json"))["jobs"]}
    seen, total = set(), 0.0
    for fid, fname in ((b.get("output_file_id"), "output.jsonl"), (b.get("error_file_id"), "errors.jsonl")):
        if not fid:
            continue
        with open(os.path.join(bd, fname), "wb") as fh:
            fh.write(api(key, "GET", f"/files/{fid}/content", raw=True))
        for line in open(os.path.join(bd, fname), encoding="utf-8"):
            if not line.strip():
                continue
            row = json.loads(line)
            job = jobs.get(row.get("custom_id"))
            if not job:
                continue
            seen.add(job["custom_id"])
            resp = row.get("response") or {}
            body = resp.get("body") or {}
            b64 = ((body.get("data") or [{}])[0]).get("b64_json") if resp.get("status_code") == 200 else None
            if b64:
                total += store(ws, job["rid"], job, b64, body.get("usage") or {}, f"batch:{a.name}")
                print(f"OK   {job['custom_id']} -> out/{job['rid']}.png")
            else:
                err = row.get("error") or body.get("error") or resp
                rs = ws.st["items"][job["rid"]]
                rs["status"], rs["note"] = rs.pop("prev_status", "todo"), f"batch {a.name} failed: {json.dumps(err)[:300]}"
                print(f"FAIL {job['custom_id']}: {json.dumps(err)[:300]}")
    for cid, job in jobs.items():
        rs = ws.st["items"][job["rid"]]
        if cid not in seen and rs["status"] == "queued":
            rs["status"], rs["note"] = rs.pop("prev_status", "todo"), f"batch {a.name} ended {b['status']} without a result"
            print(f"MISS {cid}")
    ws.save()
    with open(os.path.join(bd, "fetched"), "w") as fh:
        fh.write(now())
    print(f"{a.name}: fetched; est. ${total:.3f} at batch rates")
    print("NEXT: Read every new image, zoom-check it against its ## CHECKS, then `qc <ID> pass|fail`.")


def batch_cancel(ws, a):
    b = load_json(os.path.join(bdir(ws, a.name), "batch.json"))
    if not b:
        sys.exit(f"{a.name} has not been submitted")
    b = api(load_key(), "POST", f"/batches/{b['id']}/cancel")
    save_json(os.path.join(bdir(ws, a.name), "batch.json"), b)
    print(f"{a.name}: {b['status']} (fetch it once cancelled to release its items)")


def batch_list(ws, a):
    root = ws.p("batches")
    for name in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        man = load_json(os.path.join(root, name, "manifest.json")) or {}
        b = load_json(os.path.join(root, name, "batch.json")) or {}
        print(f"{name}: {len(man.get('jobs', []))} request(s) · {b.get('status', 'not submitted')}"
              + (" · fetched" if os.path.exists(os.path.join(root, name, "fetched")) else ""))


def cmd_fix(ws, a):
    ws.item(a.id)
    if not os.path.exists(ws.p("out", f"{a.id}.png")):
        sys.exit(f"{a.id} has no image yet")
    if ws.calls(a.id) >= ws.jobs["max_calls"] and not a.force:
        sys.exit(f"{a.id}: {ws.jobs['max_calls']}-call cap reached -> `accept {a.id} --note ...`")
    for r in a.ref:
        if not os.path.exists(ws.ref_file(r)):
            sys.exit(f"missing ref {r}")
    ws.st["fix_queue"][a.id] = {"instruction": a.instruction, "refs": a.ref, "at": now()}
    ws.st["items"][a.id]["status"] = "fixq"
    ws.save()
    print(f"{a.id}: fix queued for the next `batch build ... --ready` ({ws.calls(a.id) + 1}/{ws.jobs['max_calls']} calls)")


def cmd_qc(ws, a):
    rs = ws.st["items"][ws.item(a.id) and a.id]
    if a.verdict == "pass":
        rs["status"] = "approved"
    elif a.regen:
        if ws.calls(a.id) >= ws.jobs["max_calls"]:
            sys.exit(f"{a.id}: call cap reached -> `accept {a.id} --note ...`")
        rs["status"] = "regen"
    else:
        rs["status"] = "failed"
    rs["note"] = a.note or ""
    rs.setdefault("qc", []).append({"at": now(), "verdict": a.verdict, "note": a.note})
    ws.save()
    print(f"{a.id}: {rs['status']}")


def cmd_accept(ws, a):
    rs = ws.st["items"][ws.item(a.id) and a.id]
    rs["status"], rs["note"] = "accepted", "ACCEPTED AT CALL CAP: " + a.note
    ws.st["fix_queue"].pop(a.id, None)
    ws.save()
    with open(ws.p("ACCEPTED-AT-CAP.md"), "a", encoding="utf-8") as fh:
        fh.write(f"- {now()[:10]} **{a.id}** ({ws.calls(a.id)} calls): {a.note}\n")
    print(f"{a.id}: accepted at cap, logged in ACCEPTED-AT-CAP.md")


def cmd_zoom(ws, a):
    from PIL import Image
    im = Image.open(ws.p("out", f"{a.id}.png"))
    x0, y0, x1, y1 = map(float, a.box.split(","))
    w, h = im.size
    crop = im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
    crop = crop.resize((int(crop.width * a.scale), int(crop.height * a.scale)), Image.LANCZOS)
    os.makedirs(ws.p("out", "zoom"), exist_ok=True)
    out = ws.p("out", "zoom", f"{a.id}.png")
    crop.save(out)
    print(out)


def cmd_cost(ws, a):
    total, n = 0.0, 0
    for rs in ws.st["items"].values():
        for at in rs["attempts"]:
            total += at.get("usd", 0)
            n += 1
    print(f"{ws.jobs.get('project')}: {n} paid call(s), est. ${total:.3f}")


def cmd_gen(ws, a):
    """Immediate calls: only when the user explicitly asked for them in the conversation."""
    if not a.immediate_approved:
        sys.exit("Immediate calls are off. Every call goes through the Batch API (batch build/submit/wait). "
                 "Use --immediate-approved only if the user explicitly asked for an immediate call.")
    key = load_key()
    for rid in a.ids:
        if ws.calls(rid) >= ws.jobs["max_calls"] and not a.force:
            print(f"SKIP {rid}: call cap")
            continue
        job = make_job(ws, rid, "gen", allow_max=a.allow_max)
        res = api(key, "POST", job["endpoint"], job["body"])
        b64 = ((res.get("data") or [{}])[0]).get("b64_json")
        if not b64:
            print(f"FAIL {rid}: {json.dumps(res)[:300]}")
            continue
        usd = store(ws, rid, job, b64, res.get("usage") or {}, "immediate")
        ws.save()
        print(f"OK   {rid} -> out/{rid}.png (${usd:.3f})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ws", required=True, help="workspace folder holding jobs.json")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    s = sub.add_parser("check"); s.add_argument("ids", nargs="*")
    s = sub.add_parser("dry-run"); s.add_argument("id")
    s = sub.add_parser("batch")
    s.add_argument("action", choices=["build", "submit", "wait", "fetch", "status", "cancel", "list"])
    s.add_argument("name", nargs="?")
    s.add_argument("ids", nargs="*")
    s.add_argument("--ready", action="store_true")
    s.add_argument("--wave", type=int)
    s.add_argument("--every", type=int, default=60)
    s.add_argument("--max-hours", type=float, default=24)
    s.add_argument("--force", action="store_true")
    s.add_argument("--allow-max", action="store_true")
    s = sub.add_parser("fix"); s.add_argument("id"); s.add_argument("instruction")
    s.add_argument("--ref", action="append", default=[]); s.add_argument("--force", action="store_true")
    s = sub.add_parser("qc"); s.add_argument("id"); s.add_argument("verdict", choices=["pass", "fail"])
    s.add_argument("--regen", action="store_true"); s.add_argument("--note")
    s = sub.add_parser("accept"); s.add_argument("id"); s.add_argument("--note", required=True)
    s = sub.add_parser("zoom"); s.add_argument("id"); s.add_argument("box"); s.add_argument("--scale", type=float, default=2)
    sub.add_parser("cost")
    s = sub.add_parser("gen"); s.add_argument("ids", nargs="+"); s.add_argument("--immediate-approved", action="store_true")
    s.add_argument("--force", action="store_true"); s.add_argument("--allow-max", action="store_true")
    a = ap.parse_args()
    ws = WS(a.ws)
    if a.cmd == "batch":
        if a.action != "list" and not a.name:
            sys.exit("give the batch NAME")
        {"build": batch_build, "submit": batch_submit, "wait": batch_wait, "fetch": batch_fetch,
         "status": batch_status, "cancel": batch_cancel, "list": batch_list}[a.action](ws, a)
    else:
        {"status": cmd_status, "check": cmd_check, "dry-run": cmd_dry, "fix": cmd_fix, "qc": cmd_qc,
         "accept": cmd_accept, "zoom": cmd_zoom, "cost": cmd_cost, "gen": cmd_gen}[a.cmd](ws, a)


if __name__ == "__main__":
    main()
