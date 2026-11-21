#!/usr/bin/env python3
"""locgen.py: the ChandRush CH01 location images of Location Image Register V10 (32 plates, 4:3, 1K)
through the OpenAI Images API (gpt-image-2.5-sunburst). FLOW.md is the procedure; this is the tool.

  build                     Register V10 + manuscript -> work/records.json, work/briefs/<ID>.md, work/refs/
  check                     sources, plan, key, fonts
  brief ID                  print one record's brief (everything needed to write its prompt)
  lint ID... | all          validate prompts/<ID>.md before any spend
  gen ID... [--dry-run]     immediate API call per record (samples, single re-runs)
  fix ID "change" [--queue] targeted edit of the current plate (now, or queued for the next batch)
  qc ID pass|fail [--regen] record the verdict; an approved plate becomes a reference for later waves
  batch build|submit|wait|status|fetch|cancel|list   OpenAI Batch API, 50% off
  grid ID | zoom ID x0,y0,x1,y1   inspection helpers (fractions of width/height)
  callouts ID               write the callout skeleton; compose ID: title band + callouts -> out/final
  status | sheet | cost

Plates are the model's 4:3 scenic frames (no title, no callouts). compose adds the register's exact
two-line title band above the frame and the register's exact callouts, so no API call is ever spent on
lettering that a script can set. The API key comes from OPENAI_API_KEY / CHATGPT_API or .env and is
never printed.
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
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from xml.etree import ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTER = "Ref/Chap1 Corrected/CH01-LOCATION-IMAGE-REGISTER-V10.docx"
MANUSCRIPT = "Ref/Chap1 Corrected/CH01-PANELIZED-MANUSCRIPT-V02.docx"
SPATIAL_MAP = "Ref/Chap1 Corrected/WhatsApp Image 2026-11-03 at 08.55.20.jpeg"
API = "https://api.openai.com/v1"
# USD per 1M tokens for gpt-image-2.5 (model page, Sept 2026); batch is half of standard
RATES = {"sync": {"text": 5.0, "image": 8.0, "out": 30.0}, "batch": {"text": 2.5, "image": 4.0, "out": 15.0}}
BATCH_LIMIT = 190 * 1024 * 1024  # the Batch API takes input files up to 200 MB
TERMINAL = {"completed", "failed", "expired", "cancelled"}
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
IVORY, INDIGO, BRASS = (244, 238, 222), (30, 36, 69), (176, 141, 62)
FONTS = {"title": ["/usr/share/fonts/opentype/urw-base35/P052-Bold.otf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"],
         "callout": ["/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
                     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]}
REGIONS = {"lower-left": (0.17, 0.90), "lower-centre": (0.50, 0.92), "lower-right": (0.83, 0.90),
           "lower-margin": (0.50, 0.93), "upper-left": (0.17, 0.08), "upper-margin": (0.50, 0.07),
           "upper-right": (0.83, 0.08), "left-margin": (0.11, 0.50), "right-margin": (0.88, 0.50),
           "side": (0.88, 0.45), "opposite-side": (0.12, 0.45)}
FIX = ("Use case: precise correction of Image 1, ChandRush Chapter 01 location plate {rid} ({view}).\n"
       "Input images: Image 1 is the current plate.\n"
       "Change only this: {instruction}\n"
       "Keep everything else exactly as it is in Image 1: camera, framing, perspective, architecture, materials, "
       "colours, lighting, every other object and every existing inscription. Output the same 4:3 scenic image "
       "with only that correction.")


def p(*parts):
    return os.path.join(HERE, *parts)


def now():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def rel(path):
    return os.path.relpath(path, HERE)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def norm(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


# ---------------------------------------------------------------- sources

def _ptext(el):
    out = []
    for n in el.iter():
        if n.tag == W + "t":
            out.append(n.text or "")
        elif n.tag == W + "tab":
            out.append("\t")
        elif n.tag in (W + "br", W + "cr"):
            out.append("\n")
    return "".join(out).strip()


def docx_blocks(path):
    """Paragraphs and tables in reading order, including those inside content controls."""
    root = ET.fromstring(zipfile.ZipFile(path).read("word/document.xml"))
    blocks = []

    def walk(node):
        for c in node:
            if c.tag == W + "sdt":
                content = c.find(W + "sdtContent")
                if content is not None:
                    walk(content)
            elif c.tag == W + "p":
                st = c.find(f"{W}pPr/{W}pStyle")
                blocks.append(("p", st.get(W + "val") if st is not None else "", _ptext(c)))
            elif c.tag == W + "tbl":
                rows = [[" ".join(t for t in (_ptext(q) for q in tc.iter(W + "p")) if t) for tc in tr.findall(W + "tc")]
                        for tr in c.findall(W + "tr")]
                blocks.append(("tbl", "", rows))
    walk(root.find(W + "body"))
    return blocks


FIELDS = [("Location and construction", "construction"), ("Camera and framing", "camera"),
          ("Visible arrangement", "arrangement"), ("Master reference", "masters"), ("Image title", "title"),
          ("Appearance", "appearance"), ("Filename", "filename"), ("Location", "location")]


def parse_register(path):
    g = {"masters": [], "spatial": [], "appearance": []}
    recs, cur, section = [], None, None
    for kind, style, val in docx_blocks(path):
        if kind == "tbl":
            if cur is None and section == "master references":
                g["masters"] = [r for r in val[1:] if len(r) >= 2]
            elif cur is not None and section == "labels":
                cur["callouts"] = [{"text": r[0].strip(), "position": r[1].strip()} for r in val[1:] if r and r[0].strip()]
            continue
        if style.startswith("Heading"):
            m = re.match(r"(\d{2})\s+(.+)", val)
            if style == "Heading1" and m:
                cur = {"num": int(m.group(1)), "view": m.group(2).strip(), "callouts": []}
                recs.append(cur)
                section = None
            elif cur is None:
                section = val.strip().lower()
            elif val.strip().lower() == "title and labels":
                section = "labels"
            continue
        if not val:
            continue
        if cur is None:
            if section == "spatial layout":
                g["spatial"].append(val)
            elif section == "image appearance":
                g["appearance"].append(val)
            continue
        if section == "labels":
            cur["label_note"] = val
            continue
        for name, key in FIELDS:
            m = re.match(re.escape(name) + r"[\s:]+(.*)$", val, re.S)
            if m:
                cur[key] = m.group(1).strip()
                break
    for r in recs:
        m = re.match(r"([A-Z]\d{2}-[A-Z]\d{2})\s*\|\s*(.+)", r.get("location", ""))
        if not m:
            sys.exit(f"register record {r['num']}: cannot read its Location line")
        r["id"], r["location"] = m.group(1), m.group(2).strip()
        r["title"] = [t.strip() for t in r.get("title", "").split("\n") if t.strip()]
    return g, recs


def parse_manuscript(path):
    """Full text (for grep) and the location descriptions: each Heading3 with its SceneInstruction paragraphs."""
    blocks = docx_blocks(path)
    lines, locs, geo = [], {}, []
    for i, (kind, style, val) in enumerate(blocks):
        if kind == "tbl":
            lines += ["| " + " | ".join(c.replace("\n", " ") for c in row) + " |" for row in val]
            continue
        if not val:
            continue
        m = re.match(r"Heading(\d)", style)
        lines.append(("#" * int(m.group(1)) + " " if m else (f"[{style}] " if style and style != "Normal" else "")) + val)
        if style == "Heading3" and not val.startswith("Visual beat"):
            body, j = [], i + 1
            while j < len(blocks) and blocks[j][0] == "p" and blocks[j][1] == "SceneInstruction":
                body.append(blocks[j][2])
                j += 1
            if body and body not in locs.setdefault(norm(val), {"name": val, "versions": []})["versions"]:
                locs[norm(val)]["versions"].append(body)
        if style == "Heading2" and val.startswith("Geography and visual continuity"):
            j = i + 1
            while j < len(blocks) and blocks[j][0] == "p" and not blocks[j][1].startswith("Heading") \
                    and blocks[j][1] in ("SceneInstruction", "", "Normal"):
                if blocks[j][2]:
                    geo.append(blocks[j][2])
                j += 1
    return "\n".join(lines), locs, geo


ALIASES = {"lowerstoreofthelanternstreetgoodslift": "lanternstreetgoodsliftbayandcontroller"}


def load_records():
    d = load_json(p("work", "records.json"))
    if not d:
        sys.exit("work/records.json is missing: run `python3 locgen.py build` first")
    return d


def rec(d, rid):
    for r in d["records"]:
        if r["id"] == rid or f"{r['num']:02d}" == rid:
            return r
    sys.exit(f"unknown record {rid} (use IDs such as S01-B01)")


def load_plan():
    return load_json(p("spec", "plan.json"))


def plate_deps(plan, rid):
    return [r["ref"].split(":", 1)[1] for r in plan["records"][rid]["refs"] if r["ref"].startswith("plate:")]


def dependents(plan, rid):
    return [k for k in plan["records"] if rid in plate_deps(plan, k)]


def ref_path(ref):
    kind, name = ref.split(":", 1)
    return p("work", "refs", f"{kind}-{name}.jpg")


# ---------------------------------------------------------------- state

def load_state(d=None):
    st = load_json(p("out", "state.json"), {"records": {}, "fix_queue": {}})
    for r in (d or {}).get("records", []):
        st["records"].setdefault(r["id"], {"status": "todo", "attempts": [], "note": ""})
    return st


def save_state(st):
    save_json(p("out", "state.json"), st)


def calls(st, rid):
    return len(st["records"][rid]["attempts"])


def is_ready(plan, st, rid):
    return all(st["records"].get(dep, {}).get("status") == "approved" for dep in plate_deps(plan, rid))


def log_usage(rid, kind, via, usage, usd, secs):
    path = p("out", "usage.tsv")
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8") as fh:
        if new:
            fh.write("time\trecord\tkind\tvia\tseconds\ttext_in\timage_in\toutput\test_usd\n")
        det = usage.get("input_tokens_details") or {}
        fh.write(f"{now()}\t{rid}\t{kind}\t{via}\t{secs}\t{det.get('text_tokens', '')}\t{det.get('image_tokens', '')}\t"
                 f"{usage.get('output_tokens', '')}\t{usd:.4f}\n")


def estimate(usage, mode):
    r = RATES[mode]
    det = usage.get("input_tokens_details") or {}
    img_in = det.get("image_tokens", 0)
    text_in = det.get("text_tokens", max(0, usage.get("input_tokens", 0) - img_in))
    return (text_in * r["text"] + img_in * r["image"] + usage.get("output_tokens", 0) * r["out"]) / 1e6


def store_result(st, rid, job, b64, usage, via, secs=""):
    """Save a returned image as the record's current plate (the previous one goes to out/plates/history)."""
    rs = st["records"][rid]
    plate = p("out", "plates", f"{rid}.png")
    os.makedirs(p("out", "plates", "history"), exist_ok=True)
    if os.path.exists(plate):
        os.replace(plate, p("out", "plates", "history", f"{rid}.a{len(rs['attempts'])}.png"))
    with open(plate, "wb") as fh:
        fh.write(base64.b64decode(b64))
    usd = estimate(usage or {}, "batch" if via.startswith("batch") else "sync")
    rs["attempts"].append({"n": len(rs["attempts"]) + 1, "kind": job["kind"], "via": via, "at": now(),
                           "quality": job.get("quality"), "prompt_sha": job["prompt_sha"], "refs": job["refs"],
                           "instruction": job.get("instruction"),
                           "usage": usage, "usd": round(usd, 4)})
    rs["status"], rs["note"] = "review", ""
    rs.pop("prev_status", None)
    log_usage(rid, job["kind"], via, usage or {}, usd, secs)
    return usd


# ---------------------------------------------------------------- prompts

def prompt_sections(rid):
    path = p("prompts", f"{rid}.md")
    if not os.path.exists(path):
        return None
    secs, name = {}, None
    for line in read(path).splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            name = m.group(1).upper()
            secs[name] = []
        elif name:
            secs[name].append(line)
    return {k: "\n".join(v).strip() for k, v in secs.items()}


def full_prompt(rid):
    secs = prompt_sections(rid)
    return "\n\n".join([secs["PROMPT"], read(p("spec", "style.txt")).strip(), read(p("spec", "rules.txt")).strip()])


def lint(d, plan, rid):
    """Errors block spending; warnings are for the writer to judge."""
    r, errs, warns = rec(d, rid), [], []
    secs = prompt_sections(rid)
    if secs is None:
        return [f"prompts/{rid}.md does not exist yet"], []
    for need in ("PROMPT", "CHECKS", "CALLOUT PLAN"):
        if not secs.get(need):
            errs.append(f"missing or empty section `## {need}`")
    if errs:
        return errs, warns
    body, full = secs["PROMPT"], full_prompt(rid)
    if not 1200 <= len(body) <= 20000:
        errs.append(f"PROMPT is {len(body)} characters (expected 1200-20000)")
    if len(full) > 32000:
        errs.append(f"the full prompt is {len(full)} characters; the API limit is 32000")
    n = len(plan["records"][rid]["refs"])
    for i in range(1, n + 1):
        if f"Image {i}" not in body:
            errs.append(f"the plan attaches {n} image(s) but the PROMPT never names Image {i}")
    if f"Image {n + 1}" in body:
        errs.append(f"the PROMPT names Image {n + 1}, but only {n} image(s) are attached")
    for t in r["title"]:
        if t in body:
            errs.append(f"the title line {t!r} is in the PROMPT: the title band is added by compose, never painted")
    for c in r["callouts"]:
        if c["text"] in body:
            errs.append(f"callout text {c['text']!r} is in the PROMPT: callouts are added by compose, never painted")
    if "4:3" not in body:
        errs.append("the PROMPT does not state the 4:3 landscape frame")
    if not re.search(r"(?im)^physical inscriptions", body):
        errs.append("no `Physical inscriptions` line (write `Physical inscriptions: none` when there are none)")
    src = " ".join(r.get(k, "") for k in ("camera", "construction", "arrangement"))
    if "−" in src and re.search(r"(?<![\w−])-\d", body):
        warns.append("the record uses true minus signs (−) but the PROMPT writes an ASCII hyphen before a digit")
    if plan["records"][rid]["mode"] == "state-edit" and not re.search(r"(?i)change only", body):
        warns.append("state-edit record: say `Change only:` and list the changes, keeping everything else")
    checks = [x for x in secs["CHECKS"].splitlines() if x.strip().startswith(("-", "*"))]
    if len(checks) < 5:
        errs.append(f"CHECKS has {len(checks)} items (need at least 5: counts, states, inscriptions, layout, style)")
    for c in r["callouts"]:
        if c["text"] not in secs["CALLOUT PLAN"]:
            warns.append(f"CALLOUT PLAN does not mention {c['text']!r}")
    return errs, warns


# ---------------------------------------------------------------- API

def load_key():
    for k in ("OPENAI_API_KEY", "CHATGPT_API"):
        if os.environ.get(k):
            return os.environ[k].strip()
    path = p(".env")
    if os.path.exists(path):
        for line in read(path).splitlines():
            m = re.match(r"""^\s*(?:export\s+)?(CHATGPT_API|OPENAI_API_KEY)\s*=\s*["']?(.*?)["']?\s*$""", line)
            if m and m.group(2):
                return m.group(2)
    sys.exit("No API key: put CHATGPT_API=... in .env (it is never printed).")


def multipart(fields, files):
    boundary = "----locgen" + uuid.uuid4().hex
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
    """One HTTP call; 429 and 5xx are retried twice (network errors only on GET), the rest raised with the key scrubbed."""
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
            # a timed-out POST may still be generated and billed, so only reads are retried
            if attempt < 2 and method == "GET":
                time.sleep(20 * (attempt + 1))
                continue
            raise RuntimeError(f"network error on {method} {path}: {str(e).replace(key, '<key>')}") from None


def data_url(path):
    mime = "image/jpeg" if path.endswith(".jpg") else "image/png"
    with open(path, "rb") as fh:
        return f"data:{mime};base64," + base64.b64encode(fh.read()).decode("ascii")


def quality_of(plan, rid):
    return plan["records"][rid].get("quality", plan["quality"])


def make_job(d, plan, st, rid, kind, instruction=None, allow_max=False):
    """The exact request for one record: the same body is used by gen (immediately) and by batch."""
    r = rec(d, rid)
    quality = quality_of(plan, rid)
    if quality == "max" and not allow_max:
        raise RuntimeError(f"{rid}: quality max needs the user's approval (then pass --allow-max)")
    if kind == "gen":
        prompt = full_prompt(rid)
        images = [ref_path(x["ref"]) for x in plan["records"][rid]["refs"]]
    else:
        prompt = FIX.format(rid=rid, view=r["view"], instruction=instruction.strip()) + "\n\n" + read(p("spec", "rules.txt")).strip()
        images = [p("out", "plates", f"{rid}.png")]
    for img in images:
        if not os.path.exists(img):
            raise RuntimeError(f"{rid}: reference {rel(img)} is missing (approve its record first, or run build)")
    body = {"model": plan["model"], "prompt": prompt, "size": plan["size"], "quality": quality, "n": 1,
            "output_format": "png"}
    if images:
        body["images"] = [{"image_url": data_url(x)} for x in images]
    return {"rid": rid, "kind": kind, "endpoint": "/images/edits" if images else "/images/generations", "body": body,
            "prompt": prompt, "prompt_sha": sha(prompt), "refs": [rel(x) for x in images], "instruction": instruction,
            "quality": quality}


def run_job(key, job):
    t0 = time.time()
    try:
        res = api(key, "POST", job["endpoint"], job["body"])
    except RuntimeError as e:
        return job, None, str(e), 0
    item = (res.get("data") or [{}])[0]
    if not item.get("b64_json"):
        return job, None, "no image in the response: " + json.dumps(res)[:400], 0
    return job, res, None, round(time.time() - t0)


# ---------------------------------------------------------------- commands

def cmd_build(a):
    from PIL import Image
    for f in (REGISTER, MANUSCRIPT, SPATIAL_MAP):
        if not os.path.exists(p(f)):
            sys.exit(f"missing source: {f}")
    g, recs = parse_register(p(REGISTER))
    plan = load_plan()
    problems = []
    if len(recs) != 32:
        problems.append(f"register has {len(recs)} records, expected 32")
    for r in recs:
        for k in ("id", "filename", "camera", "construction", "arrangement", "appearance", "masters"):
            if not r.get(k):
                problems.append(f"{r.get('id', r['num'])}: no {k}")
        if len(r["title"]) != 2:
            problems.append(f"{r['id']}: title has {len(r['title'])} lines, expected 2")
        if not 2 <= len(r["callouts"]) <= 4:
            problems.append(f"{r['id']}: {len(r['callouts'])} callouts")
        if r["id"] not in plan["records"]:
            problems.append(f"{r['id']} is in the register but not in spec/plan.json")
    extra = set(plan["records"]) - {r["id"] for r in recs}
    if extra:
        problems.append(f"spec/plan.json has records the register does not: {sorted(extra)}")
    if problems:
        sys.exit("build stopped:\n  " + "\n  ".join(problems))
    text, locs, geo = parse_manuscript(p(MANUSCRIPT))
    os.makedirs(p("work", "briefs"), exist_ok=True)
    with open(p("work", "manuscript.md"), "w", encoding="utf-8") as fh:
        fh.write(text)
    with open(p(REGISTER), "rb") as fh:
        reg_sha = hashlib.sha256(fh.read()).hexdigest()[:12]
    save_json(p("work", "records.json"), {"built": now(), "register": REGISTER, "register_sha": reg_sha,
                                          "globals": g, "records": recs})
    os.makedirs(p("work", "refs"), exist_ok=True)
    for key, m in plan["masters"].items():
        dst = ref_path(f"master:{key}")
        if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(p(m["file"])):
            Image.open(p(m["file"])).convert("RGB").save(dst, "JPEG", quality=92)
    d = {"globals": g, "records": recs}
    for r in recs:
        with open(p("work", "briefs", f"{r['id']}.md"), "w", encoding="utf-8") as fh:
            fh.write(brief_text(d, plan, r, locs, geo))
    st = load_state(d)
    save_state(st)
    for rid, rs in st["records"].items():
        plate = p("out", "plates", f"{rid}.png")
        if rs["status"] == "approved" and os.path.exists(plate) and not os.path.exists(ref_path(f"plate:{rid}")):
            Image.open(plate).convert("RGB").save(ref_path(f"plate:{rid}"), "JPEG", quality=92)
    waves = {}
    for rid, pr in plan["records"].items():
        waves.setdefault(pr["wave"], []).append(rid)
    print(f"build: 32 records from {REGISTER} (sha {reg_sha}); briefs in work/briefs/; masters in work/refs/")
    for w in sorted(waves):
        print(f"  wave {w}: {len(waves[w])} records: {' '.join(sorted(waves[w], key=lambda x: rec(d, x)['num']))}")
    print(f"  manuscript text for grep: work/manuscript.md; {len(locs)} location headings found")


def brief_text(d, plan, r, locs, geo):
    pr = plan["records"][r["id"]]
    out = [f"# Brief {r['num']:02d} {r['id']}: {r['view']}", "",
           f"- **Location:** {r['location']}",
           f"- **Final file:** `out/final/{r['filename']}` (1024 px wide: title band + 1024x768 scenic frame)",
           f"- **Title band (set by `compose`, never painted):** {r['title'][0]} / {r['title'][1]}",
           f"- **Master reference (register):** {r['masters']}",
           f"- **Plan:** wave {pr['wave']}, mode `{pr['mode']}`, {plan['model']}, quality {quality_of(plan, r['id'])}, "
           f"{plan['size']}",
           ""]
    deps = dependents(plan, r["id"])
    if deps:
        out += [f"- **Design anchor:** once approved, this plate is a reference for {', '.join(deps)}. "
                "Establish every fitting those views will need, consistently and clearly.", ""]
    out += ["## Images to attach, in this order", ""]
    for i, x in enumerate(pr["refs"], 1):
        kind, name = x["ref"].split(":", 1)
        src = plan["masters"][name]["file"] if kind == "master" else f"out/plates/{name}.png (approved plate)"
        out.append(f"- **Image {i}:** `{x['ref']}` = `{rel(ref_path(x['ref']))}` from `{src}`. {x['role']}")
    out += ["", "## Register V10 record (the authority, verbatim)", "",
            f"**Camera and framing.** {r['camera']}", "", f"**Location and construction.** {r['construction']}", "",
            f"**Visible arrangement.** {r['arrangement']}", "", f"**Appearance.** {r['appearance']}", "",
            f"**Title and labels.** {r.get('label_note', '')}", "",
            "| Callout (set by `compose`, never painted) | Position and leader target |", "|---|---|"]
    out += [f"| {c['text']} | {c['position']} |" for c in r["callouts"]]
    g = d["globals"]
    out += ["", "## Register rules for every image", "", "**Spatial layout.** " + " ".join(g["spatial"]), "",
            "**Image appearance.** " + " ".join(g["appearance"]), "", "**Master references.**", ""]
    out += [f"- {row[0]}: {row[1]}" for row in g["masters"]]
    out += ["", "## Spatial authority", "", f"Open `{SPATIAL_MAP}` (position, adjacency, direction and levels; "
            "not to scale). Street left/right: from Entry Court looking towards Food Street. Bench left/centre/right: "
            "standing in the lane facing the right-wall bench. Translate physical sides into screen sides for this "
            "camera before writing the prompt.", "",
            "## Supporting manuscript context (the register wins any conflict)", ""]
    wanted = [norm(r["location"])] + [norm(m) for m in r["masters"].split(";")]
    seen = []
    for w in wanted:
        w = ALIASES.get(w, w)
        if w in locs and w not in seen:
            seen.append(w)
            for v in locs[w]["versions"]:
                out.append(f"### {locs[w]['name']}")
                out += [f"- {para}" for para in v]
                out.append("")
    out += ["**Geography and visual continuity.**", ""] + [f"- {para}" for para in geo]
    out += ["", "More story context: `grep -n` in `work/manuscript.md`.", ""]
    return "\n".join(out)


def cmd_check(a):
    plan, problems = load_plan(), []
    for f in [REGISTER, MANUSCRIPT, SPATIAL_MAP] + [m["file"] for m in plan["masters"].values()]:
        if not os.path.exists(p(f)):
            problems.append(f"missing source {f}")
    for f in ("spec/style.txt", "spec/rules.txt"):
        if not os.path.exists(p(f)):
            problems.append(f"missing {f}")
    for rid, pr in plan["records"].items():
        for x in pr["refs"]:
            kind, name = x["ref"].split(":", 1)
            if kind == "master" and name not in plan["masters"]:
                problems.append(f"{rid}: unknown master {name}")
            if kind == "plate":
                if name not in plan["records"]:
                    problems.append(f"{rid}: unknown plate {name}")
                elif plan["records"][name]["wave"] >= pr["wave"]:
                    problems.append(f"{rid} (wave {pr['wave']}) needs {name} (wave {plan['records'][name]['wave']})")
    d = load_json(p("work", "records.json"))
    if not d:
        problems.append("not built yet: run `python3 locgen.py build`")
    key = any(os.environ.get(k) for k in ("OPENAI_API_KEY", "CHATGPT_API")) or (
        os.path.exists(p(".env")) and re.search(r"(?m)^\s*(?:export\s+)?(CHATGPT_API|OPENAI_API_KEY)\s*=\s*\S", read(p(".env"))))
    if not key:
        problems.append("no API key in the environment or .env")
    for kind, paths in FONTS.items():
        if not any(os.path.exists(f) for f in paths):
            problems.append(f"no {kind} font found (compose falls back to the PIL default)")
    try:
        import PIL  # noqa: F401
    except ImportError:
        problems.append("Pillow is not installed")
    print("check: OK" if not problems else "check: PROBLEMS\n  " + "\n  ".join(problems))
    return 1 if problems else 0


def cmd_brief(a):
    d = load_records()
    print(read(p("work", "briefs", f"{rec(d, a.id)['id']}.md")))


def cmd_lint(a):
    d, plan = load_records(), load_plan()
    ids = [r["id"] for r in d["records"]] if a.ids == ["all"] else [rec(d, x)["id"] for x in a.ids]
    bad = 0
    for rid in ids:
        errs, warns = lint(d, plan, rid)
        if errs and a.ids == ["all"] and errs[0].endswith("does not exist yet"):
            print(f"{rid}: no prompt yet")
            continue
        bad += bool(errs)
        print(f"{rid}: {'FAIL' if errs else 'ok'}" + "".join(f"\n  ERROR {e}" for e in errs)
              + "".join(f"\n  warn  {w}" for w in warns))
    return 1 if bad else 0


def guard(d, plan, st, rid, force):
    """Why this record may not be sent now, or None."""
    rs = st["records"][rid]
    if rs["status"] == "queued":
        return "is queued in a batch that has not been fetched"
    if rs["status"] == "approved" and not force:
        return "is approved already (use --force to replace it)"
    if calls(st, rid) >= plan["max_calls_per_record"] and not force:
        return f"has used {calls(st, rid)} calls (cap {plan['max_calls_per_record']}); ask the user, then use --force"
    if not is_ready(plan, st, rid):
        return "waits for approved plates: " + ", ".join(x for x in plate_deps(plan, rid)
                                                       if st["records"][x]["status"] != "approved")
    return None


def cmd_gen(a):
    d, plan = load_records(), load_plan()
    st = load_state(d)
    jobs = []
    for x in a.ids:
        rid = rec(d, x)["id"]
        errs, warns = lint(d, plan, rid)
        why = ("prompt does not lint: " + "; ".join(errs)) if errs else guard(d, plan, st, rid, a.force)
        if why:
            print(f"SKIP {rid}: {why}")
            continue
        jobs.append(make_job(d, plan, st, rid, "gen", allow_max=a.allow_max))
    return send(a, d, plan, st, jobs)


def cmd_fix(a):
    d, plan = load_records(), load_plan()
    st = load_state(d)
    rid = rec(d, a.id)["id"]
    if not os.path.exists(p("out", "plates", f"{rid}.png")):
        sys.exit(f"{rid} has no plate to fix yet")
    if a.queue:
        st["fix_queue"][rid] = a.instruction
        st["records"][rid]["status"] = "fix"
        save_state(st)
        print(f"{rid}: fix queued for the next `batch build`")
        return 0
    rs = st["records"][rid]
    if calls(st, rid) >= plan["max_calls_per_record"] and not a.force:
        sys.exit(f"{rid} has used {calls(st, rid)} calls (cap {plan['max_calls_per_record']}); ask the user, then use --force")
    if rs["status"] == "queued":
        sys.exit(f"{rid} is queued in a batch")
    return send(a, d, plan, st, [make_job(d, plan, st, rid, "fix", a.instruction, a.allow_max)])


def send(a, d, plan, st, jobs):
    if not jobs:
        return 1
    for j in jobs:
        print(f"{j['rid']} {j['kind']} · {j['endpoint']} · {plan['model']} · {plan['size']} · quality {j['quality']} · "
              f"prompt {len(j['prompt'])} chars · prompt sha {j['prompt_sha']}"
              + "".join(f"\n    Image {i}: {x}" for i, x in enumerate(j["refs"], 1)))
        os.makedirs(p("out", "tmp"), exist_ok=True)
        with open(p("out", "tmp", f"{j['rid']}-{j['kind']}-prompt.txt"), "w", encoding="utf-8") as fh:
            fh.write(j["prompt"])
    if a.dry_run:
        print("dry run: nothing sent; the exact prompts are in out/tmp/<ID>-<kind>-prompt.txt")
        return 0
    key = load_key()
    print(f"{now()} sending {len(jobs)} request(s); each can take a few minutes", flush=True)
    rc = 0
    with ThreadPoolExecutor(max_workers=max(1, min(4, len(jobs)))) as pool:
        for fut in as_completed([pool.submit(run_job, key, j) for j in jobs]):
            job, res, err, secs = fut.result()
            if err:
                rc = 1
                print(f"{now()} FAIL {job['rid']}: {err}", flush=True)
                continue
            usd = store_result(st, job["rid"], job, res["data"][0]["b64_json"], res.get("usage") or {}, "sync", secs)
            save_state(st)
            u = res.get("usage") or {}
            print(f"{now()} OK   {job['rid']} {job['kind']}: out/plates/{job['rid']}.png in {secs}s; tokens in/out "
                  f"{u.get('input_tokens', '?')}/{u.get('output_tokens', '?')}; est. ${usd:.3f}", flush=True)
    print("NEXT: Read each plate, zoom-check it against prompts/<ID>.md CHECKS, then `qc <ID> pass|fail`.")
    return rc


def cmd_qc(a):
    from PIL import Image
    d, plan = load_records(), load_plan()
    st = load_state(d)
    rid = rec(d, a.id)["id"]
    rs = st["records"][rid]
    plate = p("out", "plates", f"{rid}.png")
    if not os.path.exists(plate):
        sys.exit(f"{rid} has no plate")
    if st["fix_queue"].pop(rid, None):
        print(f"{rid}: dropped its queued fix")
    if a.verdict == "pass":
        rs["status"], rs["note"] = "approved", a.note or ""
        Image.open(plate).convert("RGB").save(ref_path(f"plate:{rid}"), "JPEG", quality=92)
        used = [k for k in dependents(plan, rid) if st["records"][k]["attempts"]]
        print(f"{rid}: approved; now a reference for {', '.join(dependents(plan, rid)) or 'no other record'}")
        if used:
            print(f"  WARNING: {', '.join(used)} were generated from an earlier version of this plate")
    else:
        rs["status"], rs["note"] = ("regen" if a.regen else "fix"), a.note or ""
        print(f"{rid}: {rs['status']} ({rs['note']})")
    save_state(st)


# ---------------------------------------------------------------- batch

def batch_dir(name):
    return p("out", "batches", name)


def latest_batch():
    root = p("out", "batches")
    names = sorted(os.listdir(root)) if os.path.isdir(root) else []
    if not names:
        sys.exit("no batches yet")
    return names[-1]


def cmd_batch(a):
    return {"build": batch_build, "submit": batch_submit, "status": batch_status, "wait": batch_wait,
            "fetch": batch_fetch, "cancel": batch_cancel, "list": batch_list}[a.action](a)


def batch_build(a):
    d, plan = load_records(), load_plan()
    st = load_state(d)
    ids = [rec(d, x)["id"] for x in a.ids] if a.ids else [
        r["id"] for r in d["records"] if a.wave is None or plan["records"][r["id"]]["wave"] == a.wave]
    jobs, skipped = [], []
    for rid in ids:
        rs = st["records"][rid]
        if rid in st["fix_queue"]:
            if calls(st, rid) >= plan["max_calls_per_record"] and not a.force:
                skipped.append(f"{rid}: fix queued but the call cap is reached")
                continue
            jobs.append(make_job(d, plan, st, rid, "fix", st["fix_queue"][rid], a.allow_max))
            continue
        if rs["status"] not in ("todo", "regen"):
            if a.ids:
                skipped.append(f"{rid}: status {rs['status']}")
            continue
        errs, _ = lint(d, plan, rid)
        why = ("prompt does not lint: " + "; ".join(errs)) if errs else guard(d, plan, st, rid, a.force)
        if why:
            skipped.append(f"{rid}: {why}")
            continue
        jobs.append(make_job(d, plan, st, rid, "gen", allow_max=a.allow_max))
    for s in skipped:
        print("SKIP " + s)
    if not jobs:
        sys.exit("nothing to batch")
    endpoints = {j["endpoint"] for j in jobs}
    if len(endpoints) > 1:
        sys.exit("a batch takes one endpoint; these jobs mix " + ", ".join(sorted(endpoints)))
    waves = sorted({plan["records"][j["rid"]]["wave"] for j in jobs})
    name = a.name or dt.datetime.now().strftime("%Y%m%d-%H%M%S") + "-w" + "".join(map(str, waves))
    os.makedirs(batch_dir(name), exist_ok=False)
    path = os.path.join(batch_dir(name), "requests.jsonl")
    manifest = {"name": name, "created": now(), "endpoint": "/v1" + endpoints.pop(), "jobs": []}
    with open(path, "w", encoding="utf-8") as fh:
        for j in jobs:
            cid = f"{j['rid']}~{j['kind']}~{calls(st, j['rid']) + 1}"
            fh.write(json.dumps({"custom_id": cid, "method": "POST", "url": "/v1" + j["endpoint"], "body": j["body"]}) + "\n")
            manifest["jobs"].append({k: j[k] for k in ("rid", "kind", "quality", "prompt_sha", "refs", "instruction")}
                                    | {"custom_id": cid})
            with open(os.path.join(batch_dir(name), f"{j['rid']}-{j['kind']}-prompt.txt"), "w", encoding="utf-8") as pf:
                pf.write(j["prompt"])
    size = os.path.getsize(path)
    manifest["bytes"] = size
    save_json(os.path.join(batch_dir(name), "manifest.json"), manifest)
    if size > BATCH_LIMIT:
        sys.exit(f"{rel(path)} is {size / 2**20:.0f} MB, over the Batch API limit: build fewer records per batch")
    print(f"batch {name}: {len(jobs)} request(s), {size / 2**20:.1f} MB -> {rel(path)}")
    for j in manifest["jobs"]:
        print(f"  {j['custom_id']}  quality {j['quality']}  refs: {', '.join(j['refs'])}")
    print(f"NEXT: python3 locgen.py batch submit {name}")


def batch_submit(a):
    name = a.name or latest_batch()
    bd = batch_dir(name)
    man = load_json(os.path.join(bd, "manifest.json"))
    if not man:
        sys.exit(f"no batch {name}")
    if os.path.exists(os.path.join(bd, "batch.json")):
        sys.exit(f"{name} was submitted already")
    d = load_records()
    st = load_state(d)
    for j in man["jobs"]:
        if st["records"][j["rid"]]["status"] == "queued":
            sys.exit(f"{j['rid']} is already queued in another batch")
    key = load_key()
    up = api(key, "POST", "/files", {"purpose": "batch"},
             files=[("file", os.path.join(bd, "requests.jsonl"), "application/jsonl")])
    b = api(key, "POST", "/batches", {"input_file_id": up["id"], "endpoint": man["endpoint"],
                                      "completion_window": "24h",
                                      "metadata": {"project": "chandrush-ch01-v10", "batch": name}})
    save_json(os.path.join(bd, "batch.json"), b)
    for j in man["jobs"]:
        rs = st["records"][j["rid"]]
        rs["prev_status"], rs["status"] = rs["status"], "queued"
        if j["kind"] == "fix":
            st["fix_queue"].pop(j["rid"], None)
    save_state(st)
    print(f"submitted {name}: batch {b['id']} ({b['status']}), {len(man['jobs'])} request(s)")
    print(f"NEXT: python3 locgen.py batch wait {name}   (run it in the background; it fetches when done)")


def _refresh(key, bd):
    b = load_json(os.path.join(bd, "batch.json"))
    if not b:
        sys.exit(f"{os.path.basename(bd)} has not been submitted")
    b = api(key, "GET", f"/batches/{b['id']}")
    save_json(os.path.join(bd, "batch.json"), b)
    return b


def _line(name, b):
    c = b.get("request_counts") or {}
    return (f"{name}: {b['status']} · {c.get('completed', 0)}/{c.get('total', 0)} done, {c.get('failed', 0)} failed"
            + (f" · output file ready" if b.get("output_file_id") else ""))


def batch_status(a):
    name = a.name or latest_batch()
    print(_line(name, _refresh(load_key(), batch_dir(name))))


def batch_wait(a):
    name = a.name or latest_batch()
    key, t0 = load_key(), time.time()
    while True:
        b = _refresh(key, batch_dir(name))
        print(f"{now()} {_line(name, b)}", flush=True)
        if b["status"] in TERMINAL:
            break
        if time.time() - t0 > a.max_hours * 3600:
            sys.exit(f"still {b['status']} after {a.max_hours} h; run `batch wait {name}` again later")
        time.sleep(a.every)
    a.force = False
    return batch_fetch(a)


def batch_fetch(a):
    name = a.name or latest_batch()
    bd = batch_dir(name)
    key = load_key()
    b = _refresh(key, bd)
    if b["status"] not in TERMINAL:
        sys.exit(_line(name, b) + " (not finished)")
    if os.path.exists(os.path.join(bd, "fetched")) and not a.force:
        sys.exit(f"{name} was fetched already (use --force to process it again)")
    man = load_json(os.path.join(bd, "manifest.json"))
    jobs = {j["custom_id"]: j for j in man["jobs"]}
    d = load_records()
    st = load_state(d)
    seen, total = set(), 0.0
    for fid, fname in ((b.get("output_file_id"), "output.jsonl"), (b.get("error_file_id"), "errors.jsonl")):
        if not fid:
            continue
        with open(os.path.join(bd, fname), "wb") as fh:
            fh.write(api(key, "GET", f"/files/{fid}/content", raw=True))
        for line in read(os.path.join(bd, fname)).splitlines():
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
            rs = st["records"][job["rid"]]
            if b64:
                total += store_result(st, job["rid"], job, b64, body.get("usage") or {}, f"batch:{name}")
                print(f"OK   {job['custom_id']} -> out/plates/{job['rid']}.png")
            else:
                err = row.get("error") or body.get("error") or resp
                rs["status"], rs["note"] = rs.pop("prev_status", "todo"), f"batch {name} failed: {json.dumps(err)[:300]}"
                print(f"FAIL {job['custom_id']}: {json.dumps(err)[:300]}")
    for cid, job in jobs.items():
        if cid not in seen:
            rs = st["records"][job["rid"]]
            if rs["status"] == "queued":
                rs["status"], rs["note"] = rs.pop("prev_status", "todo"), f"batch {name} ended {b['status']} without a result"
                print(f"MISS {cid}: no result ({b['status']})")
    save_state(st)
    with open(os.path.join(bd, "fetched"), "w") as fh:
        fh.write(now())
    print(f"{name}: fetched; est. ${total:.3f} at batch rates")
    print("NEXT: Read every new plate, zoom-check it against its CHECKS, then `qc <ID> pass|fail`.")


def batch_cancel(a):
    name = a.name or latest_batch()
    b = load_json(os.path.join(batch_dir(name), "batch.json"))
    if not b:
        sys.exit(f"{name} has not been submitted")
    b = api(load_key(), "POST", f"/batches/{b['id']}/cancel")
    save_json(os.path.join(batch_dir(name), "batch.json"), b)
    print(f"{name}: {b['status']} (fetch it once cancelled to release its records)")


def batch_list(a):
    root = p("out", "batches")
    for name in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        man = load_json(os.path.join(root, name, "manifest.json")) or {}
        b = load_json(os.path.join(root, name, "batch.json")) or {}
        fetched = os.path.exists(os.path.join(root, name, "fetched"))
        print(f"{name}: {len(man.get('jobs', []))} request(s) · {b.get('status', 'not submitted')}"
              + (" · fetched" if fetched else ""))


# ---------------------------------------------------------------- inspection and compose

def font(kind, size):
    from PIL import ImageFont
    for f in FONTS[kind]:
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default(size)


def open_image(rid, final=False):
    from PIL import Image
    d = load_records()
    r = rec(d, rid)
    path = p("out", "final", r["filename"]) if final else p("out", "plates", f"{r['id']}.png")
    if not os.path.exists(path):
        sys.exit(f"no {'final' if final else 'plate'} for {r['id']} ({rel(path)})")
    return r, Image.open(path).convert("RGB")


def cmd_grid(a):
    from PIL import ImageDraw
    r, im = open_image(a.id, a.final)
    im = im.resize((1536, round(im.height * 1536 / im.width)))
    w, h = im.size
    dr = ImageDraw.Draw(im, "RGBA")
    f = font("callout", 18)
    for i in range(1, 20):
        major = i % 2 == 0
        x, y = round(w * i / 20), round(h * i / 20)
        col = (255, 220, 60, 200) if major else (255, 255, 255, 90)
        dr.line([(x, 0), (x, h)], fill=col, width=2 if major else 1)
        dr.line([(0, y), (w, y)], fill=col, width=2 if major else 1)
        if major:
            for pos in ((x + 3, 2), (x + 3, h - 22)):
                dr.text(pos, f".{i // 2}", font=f, fill=(255, 220, 60, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
            for pos in ((3, y + 2), (w - 30, y + 2)):
                dr.text(pos, f".{i // 2}", font=f, fill=(255, 220, 60, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
    out = p("out", "tmp", f"{r['id']}-grid.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out)
    print(f"{rel(out)}: lines every 0.05, labelled every 0.1 (x across, y down)")


def cmd_zoom(a):
    r, im = open_image(a.id, a.final)
    x0, y0, x1, y1 = (float(v) for v in a.box.split(","))
    if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
        sys.exit("box is x0,y0,x1,y1 as fractions, e.g. 0.6,0.2,0.9,0.5")
    crop = im.crop((round(x0 * im.width), round(y0 * im.height), round(x1 * im.width), round(y1 * im.height)))
    s = min(a.scale, 1600 / crop.width)
    crop = crop.resize((round(crop.width * s), round(crop.height * s)))
    out = p("out", "tmp", f"{r['id']}-zoom-{a.box.replace(',', '_')}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    crop.save(out)
    print(rel(out))


def cmd_callouts(a):
    d = load_records()
    r = rec(d, a.id)
    path = p("callouts", f"{r['id']}.json")
    if os.path.exists(path) and not a.force:
        sys.exit(f"{rel(path)} exists (use --force to overwrite)")
    items = []
    for c in r["callouts"]:
        m = re.match(r"([A-Za-z-]+)\s+callouts?", c["position"])
        region = m.group(1).lower() if m else "side"
        items.append({"text": c["text"], "where": c["position"], "box": list(REGIONS.get(region, REGIONS["side"])),
                      "targets": []})
    save_json(path, {"id": r["id"], "note": "box = centre of the label box; targets = leader end points; all as "
                     "fractions of the plate (x across, y down). Fill every targets list from the grid image.",
                     "callouts": items})
    print(f"{rel(path)}: {len(items)} callouts; fill each `targets` (and adjust `box`) from `grid {r['id']}`")


def draw_tracked(dr, xy, text, fnt, fill, tracking):
    x, y = xy
    for ch in text:
        dr.text((x, y), ch, font=fnt, fill=fill)
        x += dr.textlength(ch, font=fnt) + tracking


def tracked_width(dr, text, fnt, tracking):
    return sum(dr.textlength(ch, font=fnt) for ch in text) + tracking * (len(text) - 1)


def clarity(im):
    """Free local de-haze for finals: broad local contrast, then fine sharpening (plates stay untouched)."""
    from PIL import ImageFilter
    im = im.filter(ImageFilter.UnsharpMask(radius=24, percent=35, threshold=0))
    return im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=70, threshold=2))


def cmd_compose(a):
    from PIL import Image, ImageDraw
    d = load_records()
    r, plate = open_image(a.id)
    if not a.no_clarity:
        plate = clarity(plate)
    spec = load_json(p("callouts", f"{r['id']}.json"))
    if not spec:
        sys.exit(f"no callouts/{r['id']}.json: run `callouts {r['id']}` and fill its targets")
    want, got = sorted(c["text"] for c in r["callouts"]), sorted(c["text"] for c in spec["callouts"])
    if want != got:
        sys.exit(f"callout texts must be exactly the register's: {want}\n  got: {got}")
    w, h = plate.size
    s = w / 1024
    layer = plate.copy()
    dr = ImageDraw.Draw(layer)
    f = font("callout", round(14 * s))
    padx, pady, margin = round(7 * s), round(4 * s), round(6 * s)
    boxes = []
    for c in spec["callouts"]:
        if not c.get("targets"):
            sys.exit(f"{c['text']}: no targets yet")
        tw = dr.textlength(c["text"], font=f)
        asc, desc = f.getmetrics()
        bw, bh = tw + 2 * padx, asc + desc + 2 * pady
        cx = min(max(c["box"][0] * w, margin + bw / 2), w - margin - bw / 2)
        cy = min(max(c["box"][1] * h, margin + bh / 2), h - margin - bh / 2)
        box = (cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2)
        boxes.append((c, box))
        for tx, ty in c["targets"]:
            tx, ty = tx * w, ty * h
            if box[0] <= tx <= box[2] and box[1] <= ty <= box[3]:
                sys.exit(f"{c['text']}: a target lies inside its own label box; move the box")
            ex, ey = min(max(tx, box[0]), box[2]), min(max(ty, box[1]), box[3])
            if ((tx - ex) ** 2 + (ty - ey) ** 2) ** 0.5 > 0.4 * w:
                print(f"warn: {c['text']}: long leader; move the box closer to its target")
            dr.line([(ex, ey), (tx, ty)], fill=IVORY, width=max(3, round(4 * s)))
            dr.line([(ex, ey), (tx, ty)], fill=INDIGO, width=max(1, round(1.6 * s)))
            rr = max(2, round(3 * s))
            dr.ellipse([tx - rr - 1, ty - rr - 1, tx + rr + 1, ty + rr + 1], fill=IVORY)
            dr.ellipse([tx - rr, ty - rr, tx + rr, ty + rr], fill=INDIGO)
    for c, box in boxes:
        dr.rounded_rectangle(box, radius=round(3 * s), fill=IVORY, outline=INDIGO, width=max(1, round(s)))
        dr.text((box[0] + padx, box[1] + pady), c["text"], font=f, fill=INDIGO)
    band = round(84 * s)
    canvas = Image.new("RGB", (w, h + band), IVORY)
    canvas.paste(layer, (0, band))
    cd = ImageDraw.Draw(canvas)
    sizes, tracking = (round(17 * s), round(25 * s)), (round(2.2 * s), round(1.2 * s))
    fonts = [font("title", sizes[0]), font("title", sizes[1])]
    for i in (0, 1):
        while tracked_width(cd, r["title"][i], fonts[i], tracking[i]) > w - 48 * s and fonts[i].size > 10:
            fonts[i] = font("title", fonts[i].size - 1)
    y = [round(14 * s), round(40 * s)]
    for i in (0, 1):
        tw = tracked_width(cd, r["title"][i], fonts[i], tracking[i])
        draw_tracked(cd, ((w - tw) / 2, y[i]), r["title"][i], fonts[i], INDIGO, tracking[i])
    cd.rectangle([0, band - max(2, round(2 * s)), w, band], fill=BRASS)
    out = p("out", "final", r["filename"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    canvas.save(out)
    status = load_state(d)["records"][r["id"]]["status"]
    print(f"{rel(out)} ({w}x{h + band})" + ("" if status == "approved" else f"  [plate status: {status}]"))


def cmd_sheet(a):
    from PIL import Image, ImageDraw
    d, plan = load_records(), load_plan()
    st = load_state(d)
    if a.ids:
        ids = [rec(d, x)["id"] for x in a.ids]
    elif a.samples:
        ids = plan["samples"]
    else:
        ids = [r["id"] for r in d["records"] if a.wave is None or plan["records"][r["id"]]["wave"] == a.wave]
    cells = []
    for rid in ids:
        r = rec(d, rid)
        for path, kind in ((p("out", "final", r["filename"]), "final"), (p("out", "plates", f"{rid}.png"), "plate")):
            if os.path.exists(path):
                cells.append((f"{r['num']:02d} {rid} · {kind} · {st['records'][rid]['status']} · "
                              f"{calls(st, rid)} call(s)", Image.open(path).convert("RGB")))
                break
    if not cells:
        sys.exit("nothing generated for that selection yet")
    cw, cols = 640, min(3, len(cells))
    rows = [cells[i:i + cols] for i in range(0, len(cells), cols)]
    heights = [max(round(im.height * cw / im.width) for _, im in row) + 34 for row in rows]
    sheet = Image.new("RGB", (cols * cw + (cols + 1) * 10, sum(heights) + 10), (16, 18, 30))
    dr = ImageDraw.Draw(sheet)
    f, y = font("callout", 17), 10
    for row, hh in zip(rows, heights):
        for i, (label, im) in enumerate(row):
            x = 10 + i * (cw + 10)
            dr.text((x, y + 6), label, font=f, fill=(240, 205, 120))
            sheet.paste(im.resize((cw, round(im.height * cw / im.width))), (x, y + 30))
        y += hh
    name = a.name or ("samples" if a.samples else f"wave{a.wave}" if a.wave else "all" if not a.ids else "selection")
    out = p("out", "sheets", f"{name}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet.save(out)
    print(rel(out))


def cmd_status(a):
    d, plan = load_records(), load_plan()
    st = load_state(d)
    counts, spent = {}, {"sync": 0.0, "batch": 0.0}
    print("num id       wave mode        status    calls prompt  callouts final")
    for r in d["records"]:
        rid, pr, rs = r["id"], plan["records"][r["id"]], st["records"][r["id"]]
        counts[rs["status"]] = counts.get(rs["status"], 0) + 1
        for at in rs["attempts"]:
            spent["batch" if at["via"].startswith("batch") else "sync"] += at.get("usd", 0)
        errs, _ = lint(d, plan, rid) if os.path.exists(p("prompts", f"{rid}.md")) else (["-"], [])
        prompt = "-" if not os.path.exists(p("prompts", f"{rid}.md")) else "ok" if not errs else "FAIL"
        print(f"{r['num']:02d}  {rid}  {pr['wave']}    {pr['mode']:<11} {rs['status']:<9} {calls(st, rid)}     "
              f"{prompt:<7} {'yes' if os.path.exists(p('callouts', f'{rid}.json')) else '-':<8} "
              f"{'yes' if os.path.exists(p('out', 'final', r['filename'])) else '-'}"
              + (f"   note: {rs['note']}" if rs.get("note") else ""))
    ready = [r["id"] for r in d["records"] if st["records"][r["id"]]["status"] in ("todo", "regen")
             and is_ready(plan, st, r["id"])]
    print("\n" + " · ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    print(f"spent: ${spent['sync']:.2f} immediate + ${spent['batch']:.2f} batch = ${sum(spent.values()):.2f}")
    print(f"ready to generate now: {' '.join(ready) or 'none'}")
    if st["fix_queue"]:
        print(f"fixes queued for the next batch: {' '.join(st['fix_queue'])}")


# output tokens per 1024x768 image when no call at that quality has been measured yet
EXPECTED_OUT = {"low": 200, "medium": 600, "high": 1200, "xhigh": 2500, "max": 4815}


def cmd_cost(a):
    d, plan = load_records(), load_plan()
    st = load_state(d)
    outs, ins = {}, []
    for rs in st["records"].values():
        for at in rs["attempts"]:
            if at.get("usage"):
                outs.setdefault(at.get("quality") or "max", []).append(at["usage"].get("output_tokens", 0))
                ins.append(estimate({k: v for k, v in at["usage"].items() if k != "output_tokens"}, "sync"))
    avg_in = sum(ins) / len(ins) if ins else 0.02
    for q, v in sorted(outs.items()):
        print(f"measured {q}: {len(v)} call(s), average {sum(v) / len(v):.0f} output tokens")
    left = {}
    for r in d["records"]:
        if st["records"][r["id"]]["status"] in ("todo", "regen", "fix"):
            q = quality_of(plan, r["id"])
            left[q] = left.get(q, 0) + 1
    total = 0.0
    for q, n in sorted(left.items()):
        out = sum(outs[q]) / len(outs[q]) if q in outs else EXPECTED_OUT.get(q, 1200)
        per = out * RATES["sync"]["out"] / 1e6 + avg_in
        total += n * per
        print(f"left at {q}: {n} record(s) x ~${per:.3f} immediate / ~${per / 2:.3f} batch"
              + ("" if q in outs else " (estimate: not measured yet)"))
    print(f"remaining: ~${total / 2:.2f} by batch (plus fixes), ~${total:.2f} immediate")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build").set_defaults(fn=cmd_build)
    sub.add_parser("check").set_defaults(fn=cmd_check)
    s = sub.add_parser("brief")
    s.add_argument("id")
    s.set_defaults(fn=cmd_brief)
    s = sub.add_parser("lint")
    s.add_argument("ids", nargs="+")
    s.set_defaults(fn=cmd_lint)
    s = sub.add_parser("gen")
    s.add_argument("ids", nargs="+")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--force", action="store_true", help="replace an approved plate or pass the call cap")
    s.add_argument("--allow-max", action="store_true", help="permit quality max (only with the user's approval)")
    s.set_defaults(fn=cmd_gen)
    s = sub.add_parser("fix")
    s.add_argument("id")
    s.add_argument("instruction")
    s.add_argument("--queue", action="store_true", help="queue for the next batch instead of calling now")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--force", action="store_true")
    s.add_argument("--allow-max", action="store_true")
    s.set_defaults(fn=cmd_fix)
    s = sub.add_parser("qc")
    s.add_argument("id")
    s.add_argument("verdict", choices=["pass", "fail"])
    s.add_argument("--note", default="")
    s.add_argument("--regen", action="store_true", help="fail: regenerate with a revised prompt rather than fix")
    s.set_defaults(fn=cmd_qc)
    s = sub.add_parser("batch")
    s.add_argument("action", choices=["build", "submit", "status", "wait", "fetch", "cancel", "list"])
    s.add_argument("name", nargs="?", help="batch name (default: the latest)")
    s.add_argument("--wave", type=int)
    s.add_argument("--ids", nargs="*", default=[])
    s.add_argument("--every", type=int, default=60, help="wait: seconds between polls")
    s.add_argument("--max-hours", type=float, default=25)
    s.add_argument("--force", action="store_true")
    s.add_argument("--allow-max", action="store_true")
    s.set_defaults(fn=cmd_batch)
    for name, fn in (("grid", cmd_grid), ("zoom", cmd_zoom)):
        s = sub.add_parser(name)
        s.add_argument("id")
        if name == "zoom":
            s.add_argument("box")
            s.add_argument("--scale", type=float, default=3)
        s.add_argument("--final", action="store_true")
        s.set_defaults(fn=fn)
    s = sub.add_parser("callouts")
    s.add_argument("id")
    s.add_argument("--force", action="store_true")
    s.set_defaults(fn=cmd_callouts)
    s = sub.add_parser("compose")
    s.add_argument("id")
    s.add_argument("--no-clarity", action="store_true", help="skip the local contrast and sharpening pass")
    s.set_defaults(fn=cmd_compose)
    s = sub.add_parser("sheet")
    s.add_argument("ids", nargs="*")
    s.add_argument("--wave", type=int)
    s.add_argument("--samples", action="store_true")
    s.add_argument("--name")
    s.set_defaults(fn=cmd_sheet)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    sub.add_parser("cost").set_defaults(fn=cmd_cost)
    a = ap.parse_args()
    return a.fn(a) or 0


if __name__ == "__main__":
    sys.exit(main())
