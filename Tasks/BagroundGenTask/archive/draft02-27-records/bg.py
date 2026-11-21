#!/usr/bin/env python3
"""bg.py (v2): shared work queue for the ChandRush Chapter 01 location images.

Source of truth: CH01-LOCATION-IMAGE-GENERATION-DRAFT-02.docx (27 numbered image
records). `import` turns the draft into prompts/CH01-LOC-RECORDS.md, LOCATION-BIBLE.md,
REUSE.md and geography-guide.png, merging records-meta.json (worker lanes, sample
anchors, beat coverage). Any number of workers can run at once: claims are atomic,
a record is handed out only when every reference image it needs has been accepted,
and anchors wait for the user's pick.

Commands:
  import [DOCX] [--force]       rebuild records/bible/reuse from the draft
  check                         validate records, references and manuscript coverage
  claim  --worker W [--prefer LB,TB] [--set samples|full] [--json] [--dry-run]
  done   JOB --worker W [--note "..."] [--crop] [--force]
  release JOB
  pick   ID LETTER              accept a candidate (e.g. pick 001 B)
  status [--set samples|full]
  sheet  [--set samples|full]
  index                         rewrite RECORDS.md (record table + beat map)
  zoom   FILE x0,y0,x1,y1       crop a region (fractions 0-1) at full resolution
  urls   get PATH | set PATH URL   cache of uploaded reference URLs (Higgsfield)
  selftest                      concurrency/dependency/size test in a scratch copy

A job is a record ID (e.g. 012) or an anchor candidate (e.g. 001-B). A record is done
when its accepted file output/CH01_LOC_<ID>.png exists; the native generation is kept
in output/native/.
"""
import argparse
import datetime as _dt
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

ROOT = os.environ.get("BG_ROOT") or os.path.dirname(os.path.abspath(__file__))
FAST = os.environ.get("BG_FAST") == "1"          # selftest: skip the real upscale
RECORDS_FILE = os.path.join("prompts", "CH01-LOC-RECORDS.md")
META_FILE = "records-meta.json"
DEFAULT_DOCX = "CH01-LOCATION-IMAGE-GENERATION-DRAFT-02.docx"
MANUSCRIPT = os.path.join("..", "..", "CH01-INTEGRATED-MANUSCRIPT-V04.docx")
FAMILIES = ["LS", "LB", "TB", "KB", "HR", "MR", "CP", "GT", "FS"]
TARGETS = {"16:9": (3840, 2160), "4:3": (3600, 2700), "3:2": (3600, 2400)}
RATIO_WORDS = {"16:9": "landscape 16:9", "4:3": "landscape 4:3", "3:2": "landscape 3:2"}
NATIVE_HINT = {"16:9": "e.g. 2560x1440 or larger", "4:3": "e.g. 2048x1536 or larger", "3:2": "e.g. 2400x1600 or larger"}
STALE_CLAIM_S = 30 * 60
STALE_LOCK_S = 120
RATIO_TOL = 0.03
STYLE_START = "Create a richly rendered, semi-realistic storybook environment illustration"


def p(*parts):
    return os.path.join(ROOT, *parts)


def now():
    return time.time()


def stamp():
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def out_path(rec):
    return p("output", rec["output"])


def native_path(rec_or_name):
    name = rec_or_name["output"] if isinstance(rec_or_name, dict) else rec_or_name
    return p("output", "native", name[:-4] + "_native.png")


# =========================================================================== import

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _docx_blocks(path):
    from xml.etree import ElementTree as ET
    z = zipfile.ZipFile(path)
    root = ET.fromstring(z.read("word/document.xml"))
    rels = z.read("word/_rels/document.xml.rels").decode("utf-8")
    blocks = []
    for el in root.find(W_NS + "body"):
        txt = "".join(x.text or "" for x in el.iter(W_NS + "t")).strip()
        if el.tag == W_NS + "p":
            st = None
            pp = el.find(W_NS + "pPr")
            if pp is not None and pp.find(W_NS + "pStyle") is not None:
                st = pp.find(W_NS + "pStyle").get(W_NS + "val")
            img = el.find(".//" + W_NS + "drawing") is not None
            blocks.append({"kind": "p", "style": st, "text": txt, "image": img})
        elif el.tag == W_NS + "tbl":
            rows = [["".join(x.text or "" for x in tc.iter(W_NS + "t")).strip() for tc in tr.findall(W_NS + "tc")]
                    for tr in el.findall(W_NS + "tr")]
            blocks.append({"kind": "table", "rows": rows})
    media = [n for n in z.namelist() if n.startswith("word/media/")]
    return blocks, z, media


def _split_refs(text):
    refs = []
    for m in re.finditer(r"CH01_LOC_(\d{3})\.png\s*[—–-]\s*(.*?)(?=;\s*CH01_LOC_\d{3}\.png|$)", text):
        refs.append({"id": m.group(1), "role": m.group(2).strip().rstrip(";").strip()})
    return refs


def _sentences(text):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9“\"])", text.strip())
    return [s.strip() for s in parts if s.strip()]


def parse_draft(docx):
    blocks, z, media = _docx_blocks(docx)
    sections, cur = [], None
    for b in blocks:
        if b["kind"] == "p" and b["style"] == "Heading1":
            cur = {"title": b["text"], "blocks": []}
            sections.append(cur)
        elif cur is not None:
            cur["blocks"].append(b)
        elif b["kind"] == "p" and b["style"] in ("Title", "Subtitle"):
            sections.append({"title": "_" + b["style"], "blocks": [b]})
        elif b["kind"] == "p" and b["text"]:
            sections.append({"title": "_intro", "blocks": [b]})
    records = []
    for s in sections:
        m = re.match(r"CH01 LOC (\d{3}) (.+)$", s["title"])
        if not m:
            continue
        rec = {"id": m.group(1), "title": m.group(2).strip(), "refs": [], "prompt_paras": [], "checks": []}
        in_prompt = False
        for b in s["blocks"]:
            if b["kind"] != "p" or not b["text"]:
                continue
            t = b["text"]
            if b["style"] == "Heading2" and t.lower().startswith("generation prompt"):
                in_prompt = True
                continue
            if t.startswith("Output."):
                om = re.search(r"(CH01_LOC_\d{3}\.png)\s*\|\s*([\d:]+)\s*\|\s*(\d+)\s*[×x]\s*(\d+)\s*px\s*\|\s*(.+)$", t)
                if om:
                    rec.update(output=om.group(1), ratio=om.group(2), target=f"{om.group(3)}x{om.group(4)}",
                               treatment=om.group(5).strip())
            elif t.startswith("New references."):
                body = t[len("New references."):].strip()
                rec["refs"] = _split_refs(body)
                rec["refs_text"] = body
            elif t.startswith("View."):
                rec["view"] = t[len("View."):].strip()
            elif t.startswith("Visual state."):
                rec["state"] = t[len("Visual state."):].strip()
            elif t.startswith("Image checks."):
                rec["checks"] = _sentences(t[len("Image checks."):])
                in_prompt = False
            elif in_prompt:
                rec["prompt_paras"].append(t)
        rec["prompt"] = "\n\n".join(rec.pop("prompt_paras"))
        records.append(rec)
    return {"sections": sections, "records": records, "zip": z, "media": media}


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _write_generated(rel, body, source, force):
    path = p(rel)
    header = f"<!-- GENERATED by `python3 bg.py import` from {source}. Edit the draft (or records-meta.json) and re-import. body-sha:{_sha(body)} -->\n"
    if os.path.exists(path) and not force:
        old = open(path, encoding="utf-8").read()
        hm = re.match(r"<!-- GENERATED .*? body-sha:([0-9a-f]+) -->\n", old)
        if not hm or _sha(old[hm.end():]) != hm.group(1):
            sys.exit(f"REFUSED: {rel} was edited by hand since the last import. Re-run with --force to overwrite.")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(header + body)


def cmd_import(a):
    docx = p(a.docx) if not os.path.isabs(a.docx) else a.docx
    if not os.path.exists(docx):
        sys.exit(f"draft not found: {docx}")
    d = parse_draft(docx)
    meta = json.load(open(p(META_FILE), encoding="utf-8"))
    recs = d["records"]
    if not recs:
        sys.exit("no 'CH01 LOC ###' records found in the draft")
    src = os.path.basename(docx)
    # ---------------- records
    out = [f"# CH01 location image records ({len(recs)})\n",
           f"Imported from `{src}`. Run order is ascending ID; parallel workers keep it because every record "
           "references only lower IDs. Fields below `- family:` come from records-meta.json.\n"]
    for r in recs:
        m = meta.get(r["id"], {})
        mode = "edit" if "edit" in r.get("treatment", "").lower() else "generate"
        out.append(f"## {r['id']} · {r['title']}")
        out.append(f"- output: {r.get('output', '')}")
        out.append(f"- ratio: {r.get('ratio', '')}")
        out.append(f"- target: {r.get('target', '')}")
        out.append(f"- treatment: {r.get('treatment', '')}")
        out.append(f"- mode: {mode}")
        if r["refs"]:
            out.append("- refs:")
            for i, ref in enumerate(r["refs"], 1):
                out.append(f"  {i}. @{ref['id']} — {ref['role']}")
        else:
            out.append(f"- refs: none ({r.get('refs_text', '')})")
        out.append(f"- view: {r.get('view', '')}")
        out.append(f"- state: {r.get('state', '')}")
        out.append(f"- family: {m.get('family', '')}")
        out.append(f"- set: {m.get('set', 'full')}")
        out.append(f"- anchor: {'yes' if m.get('anchor') else 'no'}")
        out.append(f"- candidates: {m.get('candidates', 1)}")
        out.append(f"- beats: {m.get('beats', '') or '—'}")
        out.append(f"- insets: {m.get('insets', '') or '—'}")
        out.append("")
        out.append("```text")
        out.append(r["prompt"])
        out.append("```")
        out.append("")
        out.append("**Image checks**")
        for c in r["checks"]:
            out.append(f"- {c}")
        out.append("\n---\n")
    _write_generated(RECORDS_FILE, "\n".join(out), src, a.force)
    # ---------------- bible
    bible = ["# Location Bible: ChandRush Chapter 01 (from Draft 02)\n",
             f"Imported verbatim from `{src}`, apart from Markdown formatting. The draft is the authority; "
             "`README.md` lists the workflow decisions and known source issues.\n"]
    skip = re.compile(r"^(CH01 LOC \d{3}|Image register|Reuse without additional location images)")
    img_written = False
    for s in d["sections"]:
        if s["title"].startswith("_"):
            for b in s["blocks"]:
                if b["text"]:
                    bible.append(f"**{b['text']}**\n" if s["title"] != "_intro" else b["text"] + "\n")
            continue
        if skip.match(s["title"]):
            continue
        bible.append(f"## {s['title']}\n")
        for b in s["blocks"]:
            if b["kind"] == "table":
                rows = b["rows"]
                bible.append("| " + " | ".join(rows[0]) + " |")
                bible.append("|" + "---|" * len(rows[0]))
                for row in rows[1:]:
                    bible.append("| " + " | ".join(row) + " |")
                bible.append("")
            elif b["style"] == "Heading2":
                bible.append(f"### {b['text']}\n")
            elif b.get("image") and d["media"]:
                with open(p("geography-guide.png"), "wb") as fh:
                    fh.write(d["zip"].read(d["media"][0]))
                img_written = True
                bible.append("![Lantern Street geography guide](geography-guide.png)\n")
            elif b["text"]:
                bible.append(b["text"] + "\n")
    _write_generated("LOCATION-BIBLE.md", "\n".join(bible), src, a.force)
    # ---------------- register + reuse
    reuse = ["# Reuse notes: page production, not extra images\n",
             f"Imported from `{src}`. These notes say how to make every other story moment from the 27 accepted "
             "images by crops and small local edits. They add **no** generation jobs.\n"]
    for s in d["sections"]:
        if s["title"].startswith("Image register"):
            reuse.append("## Image register\n")
            for b in s["blocks"]:
                if b["kind"] == "table":
                    rows = b["rows"]
                    reuse.append("| " + " | ".join(rows[0]) + " |")
                    reuse.append("|" + "---|" * len(rows[0]))
                    reuse += ["| " + " | ".join(r) + " |" for r in rows[1:]]
                    reuse.append("")
                elif b["text"]:
                    reuse.append(b["text"] + "\n")
        if s["title"].startswith("Reuse without additional location images"):
            reuse.append("## Reuse without additional location images\n")
            for b in s["blocks"]:
                if not b.get("text"):
                    continue
                if "|" in b["text"]:
                    head, body = [x.strip() for x in b["text"].split("|", 1)]
                    imgs, _, rest = body.partition(". ")
                    reuse.append(f"### {head} ({imgs})\n\n{rest}\n")
                else:
                    reuse.append(b["text"] + "\n")
    _write_generated("REUSE.md", "\n".join(reuse), src, a.force)
    missing_meta = [r["id"] for r in recs if r["id"] not in meta]
    print(f"imported {len(recs)} records from {src} → {RECORDS_FILE}, LOCATION-BIBLE.md, REUSE.md"
          + (", geography-guide.png" if img_written else ""))
    if missing_meta:
        print("WARNING: no records-meta.json entry for " + ", ".join(missing_meta))
    return 0


# =========================================================================== records

def parse_records():
    path = p(RECORDS_FILE)
    if not os.path.exists(path):
        sys.exit(f"{RECORDS_FILE} missing: run `python3 bg.py import` first")
    text = open(path, encoding="utf-8").read()
    recs, order = {}, 0
    for m in re.finditer(r"^## (\d{3}) · (.+?)\n(.*?)(?=^## \d{3} · |\Z)", text, re.M | re.S):
        rid, title, body = m.group(1), m.group(2).strip(), m.group(3)
        r = {"id": rid, "title": title, "order": order, "refs": [], "checks": [], "prompt": "", "errors": []}
        order += 1
        in_refs = False
        for line in body.splitlines():
            fm = re.match(r"^- (output|ratio|target|treatment|mode|refs|view|state|family|set|anchor|candidates|beats|insets):\s*(.*)$", line)
            if fm:
                key, val = fm.group(1), fm.group(2).strip()
                in_refs = key == "refs" and not val
                if key != "refs":
                    r[key] = val
                continue
            rm = re.match(r"^\s+(\d+)\.\s+@(\d{3})\s+—\s+(.*)$", line)
            if in_refs and rm:
                r["refs"].append({"n": int(rm.group(1)), "id": rm.group(2), "role": rm.group(3).strip()})
                continue
            if line.strip() and not line.startswith("  "):
                in_refs = False
        tm = re.search(r"```text\n(.*?)\n```", body, re.S)
        if tm:
            r["prompt"] = tm.group(1).strip()
        cm = re.search(r"\*\*Image checks\*\*\n(.*?)(?=\n---|\Z)", body, re.S)
        if cm:
            r["checks"] = [l[2:].strip() for l in cm.group(1).splitlines() if l.startswith("- ")]
        r["candidates"] = int(r.get("candidates", "1") or 1)
        r["anchor"] = r.get("anchor", "no") == "yes"
        r["beats"] = parse_beats(r.get("beats", "—"))
        r["insets"] = re.findall(r"Q\d\d", r.get("insets", ""))
        if rid in recs:
            r["errors"].append("duplicate id")
        recs[rid] = r
    return recs


def parse_beats(s):
    out = []
    for part in s.split(";"):
        m = re.match(r"\s*(\d\d[A-Z])\s+([A-Z](?:\s*,\s*[A-Z])*)", part)
        if m:
            out += [f"{m.group(1)} {x}" for x in re.split(r"\s*,\s*", m.group(2))]
    return out


_META_CACHE = {}


def load_meta():
    path = p(META_FILE)
    if path not in _META_CACHE:
        _META_CACHE[path] = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    return _META_CACHE[path]


def compose_prompt(rec, recs):
    """The exact text a worker sends to the image model: header, the user's art direction
    (records-meta.json `_style_overlay`), the draft's generation prompt verbatim, then any
    record-specific clarification (records-meta.json `clarify`)."""
    meta = load_meta()
    lines = [f"Aspect ratio: {RATIO_WORDS.get(rec['ratio'], rec['ratio'])}; generate at the largest size available."]
    if rec["refs"]:
        lines.append("Reference images, attached in this order:")
        for ref in sorted(rec["refs"], key=lambda x: x["n"]):
            t = recs.get(ref["id"], {}).get("title", "")
            lines.append(f"- Image {ref['n']} (accepted location image {ref['id']}, {t}): {ref['role']}.")
        if rec.get("mode") == "edit":
            lines.append("This is an edit of Image 1: keep its camera and everything not named below exactly as it is.")
    else:
        lines.append("Reference images: none. Establish this location from the description.")
    lines.append(f"View: {rec.get('view', '')}")
    lines.append(f"Visual state: {rec.get('state', '')}")
    parts = ["\n".join(lines)]
    overlay = (meta.get("_style_overlay") or "").strip()
    if overlay:
        parts.append(overlay)
    parts.append(rec["prompt"])
    clarify = ((meta.get(rec["id"]) or {}).get("clarify") or "").strip()
    if clarify:
        parts.append("Clarification for this image: " + clarify)
    return "\n\n".join(parts)


# =========================================================================== jobs

def jobs_for(recs, which):
    jobs = []
    for r in sorted(recs.values(), key=lambda x: x["order"]):
        rset = r.get("set", "full")
        if which == "samples" and rset != "samples":
            continue
        if r["anchor"] and rset == which:
            for i in range(r["candidates"]):
                L = "ABCDEFGH"[i]
                jobs.append({"job": f"{r['id']}-{L}", "rec": r, "candidate": L,
                             "out": p("output", "_candidates", f"{r['output'][:-4]}-{L}.png")})
        elif r["anchor"]:
            jobs.append({"job": r["id"], "rec": r, "candidate": None, "out": out_path(r), "needs_pick": True})
        else:
            jobs.append({"job": r["id"], "rec": r, "candidate": None, "out": out_path(r)})
    return jobs


def find_job(recs, job_id):
    for which in ("samples", "full"):
        for j in jobs_for(recs, which):
            if j["job"] == job_id:
                return j
    return None


def claim_path(job_id):
    return p("output", "_claims", f"{job_id}.claim")


def read_claim(job_id):
    try:
        with open(claim_path(job_id), encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def claim_active(job_id):
    c = read_claim(job_id)
    return bool(c) and now() - c.get("t", 0) < STALE_CLAIM_S


def ref_file(recs, rid):
    r = recs.get(rid)
    if not r:
        return None
    nat = native_path(r)
    return nat if os.path.exists(nat) else out_path(r)


def job_state(recs, j):
    if os.path.exists(j["out"]):
        return "done"
    if j["candidate"] and os.path.exists(out_path(j["rec"])):
        return "done"          # the user already picked this record: remaining candidates are not needed
    if claim_active(j["job"]):
        return "claimed"
    if j.get("needs_pick"):
        return "pick"
    missing = [ref["id"] for ref in j["rec"]["refs"] if ref["id"] not in recs or not os.path.exists(out_path(recs[ref["id"]]))]
    if missing:
        j["missing"] = missing
        return "waiting"
    return "ready"


class Lock:
    """Global mutex for queue changes (mkdir is atomic on local filesystems)."""

    def __init__(self):
        self.path = p("output", "_claims", ".lock")

    def __enter__(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        deadline = now() + 60
        while True:
            try:
                os.mkdir(self.path)
                return self
            except FileExistsError:
                try:
                    if now() - os.path.getmtime(self.path) > STALE_LOCK_S:
                        os.rmdir(self.path)
                        continue
                except FileNotFoundError:
                    continue
                if now() > deadline:
                    sys.exit("bg.py: queue lock busy for 60 s; try again")
                time.sleep(random.uniform(0.03, 0.15))

    def __exit__(self, *exc):
        try:
            os.rmdir(self.path)
        except FileNotFoundError:
            pass


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ledger_rows():
    path = p("output", "_ledger.tsv")
    rows = []
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 4:
                rows.append({"job": parts[0], "worker": parts[1], "sha": parts[2], "time": parts[3]})
    return rows


def ledger_add(job, worker, digest, refs="", size=""):
    path = p("output", "_ledger.tsv")
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8") as fh:
        if new:
            fh.write("job\tworker\tnative_sha256\ttime\treferences_used\tnative_size\n")
        fh.write(f"{job}\t{worker}\t{digest}\t{stamp()}\t{refs}\t{size}\n")


# =========================================================================== printing

def job_payload(recs, j, worker):
    r = j["rec"]
    refs = [{"image": ref["n"], "id": ref["id"], "path": ref_file(recs, ref["id"]), "role": ref["role"]}
            for ref in sorted(r["refs"], key=lambda x: x["n"])]
    return {"job": j["job"], "id": r["id"], "title": r["title"], "family": r.get("family"),
            "treatment": r.get("treatment"), "mode": r.get("mode"), "candidate": j["candidate"],
            "ratio": r["ratio"], "target": r["target"], "native_hint": NATIVE_HINT.get(r["ratio"], ""),
            "refs": refs, "view": r.get("view"), "state": r.get("state"), "save_as": j["out"],
            "prompt": compose_prompt(r, recs), "checks": r["checks"],
            "done_cmd": f"python3 bg.py done {j['job']} --worker {worker}"}


def print_job(d):
    print(f"JOB {d['job']}  ·  {d['id']} {d['title']}  ·  {d['treatment']}  ·  mode: {d['mode']}")
    print(f"RATIO {d['ratio']}: generate {RATIO_WORDS.get(d['ratio'])} at the largest native size ({d['native_hint']}); "
          f"`done` keeps the native file and upscales proportionately to {d['target']}. Higgsfield aspect_ratio={d['ratio']}")
    if d["refs"]:
        print("ATTACH, in this order" + (" (Image 1 is the image being edited):" if d["mode"] == "edit" else ":"))
        for r in d["refs"]:
            print(f"  Image {r['image']}: {r['path']}\n           role: {r['role']}")
    else:
        print("ATTACH: nothing (text-only master; never attach the old location pack)")
    print(f"VIEW: {d['view']}")
    print(f"VISUAL STATE: {d['state']}")
    print(f"SAVE AS: {d['save_as']}")
    print("-----BEGIN PROMPT-----")
    print(d["prompt"])
    print("-----END PROMPT-----")
    print("IMAGE CHECKS (open the saved image; zoom on every label, count and order):")
    for c in d["checks"]:
        print(f"  [ ] {c}")
    print(f"THEN: {d['done_cmd']}   (add --note \"...\" if a check still fails after the fixes)")


# =========================================================================== commands

def cmd_claim(a):
    recs = parse_records()
    prefer = [f.strip() for f in (a.prefer or "").split(",") if f.strip()]
    with Lock():
        jobs = jobs_for(recs, a.set)
        states = [(j, job_state(recs, j)) for j in jobs]
        ready = [j for j, s in states if s == "ready"]
        ready.sort(key=lambda j: (0 if j["rec"].get("family") in prefer else 1, j["rec"]["order"], j["job"]))
        if ready:
            j = ready[0]
            if not a.dry_run:
                with open(claim_path(j["job"]), "w", encoding="utf-8") as fh:
                    json.dump({"worker": a.worker, "t": now(), "at": stamp()}, fh)
            d = job_payload(recs, j, a.worker)
            print(json.dumps(d, indent=1)) if a.json else print_job(d)
            return 0
    if all(s == "done" for _, s in states):
        print(json.dumps({"status": "ALL DONE"}) if a.json else "ALL DONE")
        return 3
    picks = {j["rec"]["id"] for j, s in states if s == "pick"}
    for j, s in states:
        if s == "waiting":
            for rid in j.get("missing", []):
                anc = recs.get(rid)
                if anc and anc["anchor"]:
                    cands = [x for x in jobs_for(recs, anc.get("set", "full")) if x["rec"]["id"] == rid and x["candidate"]]
                    if cands and all(os.path.exists(x["out"]) for x in cands):
                        picks.add(rid)
    claimed = [j["job"] for j, s in states if s == "claimed"]
    picks = sorted(picks)
    if a.json:
        print(json.dumps({"status": "WAIT", "claimed_by_others": claimed, "pick_needed": picks}))
    else:
        if picks:
            print("PICK NEEDED: " + ", ".join(picks) + "  (candidates in output/_candidates; the USER chooses, then: "
                  "python3 bg.py pick <ID> <letter>)")
        print("WAIT: nothing is ready right now. In progress elsewhere: " + (", ".join(claimed) or "none"))
    return 4 if picks and not claimed else 2


def _finish_image(rec, src, crop):
    """Keep the native file, make the accepted PNG at the record's target size. Returns info dict."""
    from PIL import Image
    tw, th = (int(x) for x in rec["target"].split("x"))
    want = tw / th
    with Image.open(src) as im:
        im.load()
        native = im.convert("RGB")
    w, h = native.size
    got = w / h
    info = {"native": f"{w}x{h}", "notes": []}
    if abs(got - want) / want > RATIO_TOL and not crop:
        raise ValueError(f"aspect {w}x{h} ({got:.3f}) does not match {rec['ratio']} ({want:.3f}). Regenerate at "
                         f"{rec['ratio']}, or, only if no required equipment would be lost, re-run done with --crop.")
    if max(w, h) < 900:
        raise ValueError(f"native image too small ({w}x{h})")
    return native, (tw, th), info


def cmd_done(a):
    recs = parse_records()
    j = find_job(recs, a.job)
    if not j:
        sys.exit(f"unknown job {a.job}")
    src = j["out"]
    if not os.path.exists(src):
        sys.exit(f"REFUSED: {src} does not exist. Save the generated image there first.")
    rec = j["rec"]
    try:
        native, (tw, th), info = _finish_image(rec, src, a.crop)
    except Exception as e:  # noqa: BLE001
        sys.exit(f"REFUSED: {e}")
    nat_dir = p("output", "native") if not j["candidate"] else p("output", "_candidates", "native")
    os.makedirs(nat_dir, exist_ok=True)
    nat_file = os.path.join(nat_dir, os.path.basename(src)[:-4] + "_native.png")
    native.save(nat_file, "PNG")
    digest = sha256(nat_file)
    refs_used = ",".join(f"CH01_LOC_{r['id']}.png" for r in sorted(rec["refs"], key=lambda x: x["n"])) or "none"
    with Lock():
        dup = [r for r in ledger_rows() if r["sha"] == digest and r["job"] != a.job and not r["worker"].startswith("pick")]
        if dup and not a.force:
            os.remove(nat_file)
            sys.exit(f"REFUSED: identical image already recorded for {dup[0]['job']}. "
                     "You probably copied the wrong file: copy the image made for THIS job.")
        # proportional fit: crop the (tiny or approved) ratio excess at the centre, then resize
        w, h = native.size
        want = tw / th
        if w / h > want:
            nw = round(h * want)
            box = ((w - nw) // 2, 0, (w - nw) // 2 + nw, h)
        else:
            nh = round(w / want)
            box = (0, (h - nh) // 2, w, (h - nh) // 2 + nh)
        fitted = native.crop(box)
        scale = tw / fitted.size[0]
        if FAST:
            fitted.save(src, "PNG")
        else:
            from PIL import Image
            fitted.resize((tw, th), Image.LANCZOS).save(src, "PNG", optimize=False)
        if scale > 2.0:
            info["notes"].append(f"upscaled x{scale:.2f}: inspect fine detail (labels, grids) at full size")
        ledger_add(a.job, a.worker, digest, refs_used, info["native"])
        if a.note:
            with open(p("output", "REVIEW-NOTES.md"), "a", encoding="utf-8") as fh:
                fh.write(f"- **{a.job}** {rec['title']} ({a.worker}, {stamp()}): {a.note}\n")
        try:
            os.remove(claim_path(a.job))
        except FileNotFoundError:
            pass
    print(f"DONE {a.job}: native {info['native']} kept at {nat_file}; accepted file {tw}x{th} → {src}"
          + ("  NOTE: " + "; ".join(info["notes"]) if info["notes"] else ""))
    return 0


def cmd_release(a):
    with Lock():
        try:
            os.remove(claim_path(a.job))
            print(f"released {a.job}")
        except FileNotFoundError:
            print(f"{a.job} was not claimed")
    return 0


def cmd_pick(a):
    recs = parse_records()
    r = recs.get(a.id)
    if not r or not r["anchor"]:
        sys.exit(f"{a.id} is not an anchor record")
    L = a.letter.upper()
    src = p("output", "_candidates", f"{r['output'][:-4]}-{L}.png")
    nsrc = p("output", "_candidates", "native", f"{r['output'][:-4]}-{L}_native.png")
    if not os.path.exists(src):
        sys.exit(f"no candidate {src} (finish it with `done` first)")
    dst = out_path(r)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    for f in (dst, native_path(r)):
        if os.path.exists(f):
            os.replace(f, f[:-4] + f".replaced-{int(now())}.png")
    shutil.copy2(src, dst)
    if os.path.exists(nsrc):
        os.makedirs(os.path.dirname(native_path(r)), exist_ok=True)
        shutil.copy2(nsrc, native_path(r))
    with Lock():
        ledger_add(r["id"], f"pick-{L}", sha256(dst))
    print(f"PICKED {r['id']} = candidate {L} → {dst}")
    return 0


def cmd_status(a):
    recs = parse_records()
    by, claimed, picks = {}, [], set()
    for j in jobs_for(recs, a.set):
        s = job_state(recs, j)
        f = j["rec"].get("family", "?")
        by.setdefault(f, {"done": 0, "total": 0, "ready": 0, "claimed": 0, "waiting": 0, "pick": 0})
        by[f]["total"] += 1
        by[f][s] += 1
        if s == "claimed":
            c = read_claim(j["job"])
            claimed.append(f"{j['job']} by {c['worker']} for {int((now() - c['t']) / 60)} min")
        if s == "pick":
            picks.add(j["rec"]["id"])
    tot, done = sum(v["total"] for v in by.values()), sum(v["done"] for v in by.values())
    print(f"Set: {a.set}   jobs done {done}/{tot}   (accepted records: "
          f"{sum(1 for r in recs.values() if os.path.exists(out_path(r)))}/{len(recs)})")
    print("family  done/total  ready  claimed  waiting  pick")
    for f in FAMILIES:
        if f in by:
            v = by[f]
            print(f"{f:6}  {v['done']:>4}/{v['total']:<5}  {v['ready']:>5}  {v['claimed']:>7}  {v['waiting']:>7}  {v['pick']:>4}")
    if claimed:
        print("In progress: " + "; ".join(claimed))
    if picks:
        print("Anchors not yet picked: " + ", ".join(sorted(picks)) + " (sample round first)")
    notes = p("output", "REVIEW-NOTES.md")
    if os.path.exists(notes):
        print(f"REVIEW-NOTES.md: {sum(1 for l in open(notes, encoding='utf-8') if l.startswith('- '))} item(s)")
    return 0


def _font(size):
    from PIL import ImageFont
    for cand in (os.path.join(ROOT, "..", "ShotGenTask", "fonts", "SourceSans3-Semibold.ttf"),
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(cand):
            return ImageFont.truetype(cand, size)
    return ImageFont.load_default()


def make_sheet(items, out, title):
    from PIL import Image, ImageDraw
    if not items:
        return False
    tw, th, pad, lab = 520, 300, 16, 34
    cols = min(4, len(items))
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + lab + pad) + pad + 50), (22, 28, 40))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 12), title, fill=(240, 230, 200), font=_font(26))
    for i, (label, path) in enumerate(items):
        rr, c = divmod(i, cols)
        x, y = pad + c * (tw + pad), 50 + pad + rr * (th + lab + pad)
        try:
            with Image.open(path) as im:
                im = im.convert("RGB")
                im.thumbnail((tw, th))
                sheet.paste(im, (x + (tw - im.width) // 2, y + (th - im.height) // 2))
        except Exception:  # noqa: BLE001
            d.rectangle([x, y, x + tw, y + th], outline=(200, 80, 80))
        d.text((x, y + th + 6), label, fill=(235, 235, 235), font=_font(20))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet.save(out)
    return True


def cmd_sheet(a):
    recs = parse_records()
    made = []
    if a.set == "samples":
        items = []
        for j in jobs_for(recs, "samples"):
            if os.path.exists(j["out"]):
                items.append((f"{j['job']}  {j['rec']['title'][:36]}", j["out"]))
        for r in recs.values():
            if r.get("set") == "samples" and os.path.exists(out_path(r)):
                items.append((f"{r['id']}  PICKED", out_path(r)))
        if make_sheet(items, p("output", "_sheets", "SAMPLES.png"), "ChandRush CH01 locations: sample round"):
            made.append(p("output", "_sheets", "SAMPLES.png"))
    else:
        items = [(f"{r['id']}  {r['title'][:38]}", out_path(r)) for r in sorted(recs.values(), key=lambda x: x["order"])
                 if os.path.exists(out_path(r))]
        for f in FAMILIES:
            fam = [(lbl, pth) for (lbl, pth), r in zip(items, [recs[i[0][:3]] for i in items]) if r.get("family") == f]
            if make_sheet(fam, p("output", "_sheets", f"{f}.png"), f"ChandRush CH01 locations: {f}"):
                made.append(p("output", "_sheets", f"{f}.png"))
        if make_sheet(items, p("output", "_sheets", "ALL.png"), "ChandRush CH01 locations: all accepted records"):
            made.append(p("output", "_sheets", "ALL.png"))
        cand = [(os.path.basename(f)[:-4], os.path.join(p("output", "_candidates"), f))
                for f in sorted(os.listdir(p("output", "_candidates"))) if f.endswith(".png")]
        pend = [c for c in cand if not os.path.exists(out_path(recs[c[0][9:12]]))] if cand else []
        if pend and make_sheet(pend, p("output", "_sheets", "CANDIDATES.png"), "Candidates waiting for a pick"):
            made.append(p("output", "_sheets", "CANDIDATES.png"))
    print("\n".join(made) if made else "nothing to show yet")
    return 0


def cmd_zoom(a):
    from PIL import Image
    x0, y0, x1, y1 = (float(v) for v in a.box.split(","))
    with Image.open(a.file) as im:
        w, h = im.size
        crop = im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
        if max(crop.size) < 1200:
            k = 1200 / max(crop.size)
            crop = crop.resize((int(crop.width * k), int(crop.height * k)), Image.LANCZOS)
        out = p("output", "_sheets", f"zoom-{os.path.basename(a.file)[:-4]}-{a.box.replace(',', '_')}.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        crop.save(out)
    print(out)
    return 0


def manuscript_beats():
    path = p(MANUSCRIPT)
    if not os.path.exists(path):
        return None, None
    xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
    text = re.sub(r"<[^>]+>", "", re.sub(r"</w:p>", "\n", xml))
    beats = list(dict.fromkeys(f"{m.group(1)} {m.group(2)}"
                               for m in re.finditer(r"Visual beat CH01 (\d\d[A-Z]) ([A-Z])\b", text)))
    return beats, sorted(set(re.findall(r"Companion inset (Q\d\d)", text)))


def cmd_check(a):
    recs = parse_records()
    errs, warns = [], []
    meta = json.load(open(p(META_FILE), encoding="utf-8"))
    ids = sorted(recs)
    if ids != [f"{i:03d}" for i in range(1, len(ids) + 1)]:
        errs.append("record IDs are not consecutive from 001: " + ", ".join(ids))
    for rid, r in recs.items():
        e = lambda msg: errs.append(f"{rid}: {msg}")  # noqa: E731
        for x in r["errors"]:
            e(x)
        if r.get("output") != f"CH01_LOC_{rid}.png":
            e(f"output '{r.get('output')}' should be CH01_LOC_{rid}.png")
        if r.get("ratio") not in TARGETS:
            e(f"ratio '{r.get('ratio')}' not in {list(TARGETS)}")
        elif r.get("target") != "%dx%d" % TARGETS[r["ratio"]]:
            e(f"target {r.get('target')} differs from the workflow setting for {r['ratio']}")
        if r.get("family") not in FAMILIES:
            e(f"family '{r.get('family')}' missing or unknown (records-meta.json)")
        if r.get("mode") not in ("edit", "generate"):
            e("mode must be edit or generate")
        for ref in r["refs"]:
            if ref["id"] not in recs:
                e(f"reference {ref['id']} is not a record")
            elif ref["id"] >= rid:
                e(f"reference {ref['id']} is not an earlier ID (ascending-order rule)")
        if r.get("mode") == "edit" and not r["refs"]:
            e("an edit needs its source image as Image 1")
        if rid != "001" and not r["refs"]:
            e("only the master may be text-only")
        if not r["prompt"].startswith(STYLE_START):
            e("generation prompt does not start with the shared style paragraph")
        if "without characters" not in r["prompt"]:
            e("generation prompt lacks the no-characters sentence")
        if not r.get("view") or not r.get("state"):
            e("view/state missing")
        if not r["checks"]:
            e("no image checks")
        if r["anchor"] and r["candidates"] < 2:
            e("anchor needs candidates ≥ 2")
        if r["anchor"] and r.get("set") == "samples" and any(not recs[x["id"]]["anchor"] or recs[x["id"]].get("set") != "samples"
                                                             for x in r["refs"] if x["id"] in recs):
            e("sample anchors may only reference other sample anchors")
        if "Locations/" in r["prompt"] or ".png" in r["prompt"]:
            e("prompt names a file (the old location pack is excluded; attach images instead)")
    for k in meta:
        if not k.startswith("_") and k not in recs:
            warns.append(f"records-meta.json has {k} but the records do not")
    if not (meta.get("_style_overlay") or "").strip():
        warns.append("no _style_overlay in records-meta.json: images get the draft's style only")
    clar = [k for k, v in meta.items() if not k.startswith("_") and isinstance(v, dict) and v.get("clarify")]
    beats, insets = manuscript_beats()
    covered = {b for r in recs.values() for b in r["beats"]}
    cq = {q for r in recs.values() for q in r["insets"]}
    if beats is None:
        warns.append("manuscript not found: beat coverage not checked")
    else:
        miss = [b for b in beats if b not in covered]
        extra = sorted(covered - set(beats))
        if miss:
            errs.append(f"{len(miss)} manuscript beats have no record: {', '.join(miss)}")
        if extra:
            errs.append("records list beats not in the manuscript: " + ", ".join(extra))
        mq = [q for q in insets if q not in cq]
        if mq:
            errs.append("insets with no record: " + ", ".join(mq))
    for f in ("LOCATION-BIBLE.md", "REUSE.md"):
        if not os.path.exists(p(f)):
            errs.append(f"{f} missing: run `python3 bg.py import`")
    longest = max(recs.values(), key=lambda r: len(compose_prompt(r, recs)))
    print(f"records: {len(recs)} ({sum(r.get('mode') == 'edit' for r in recs.values())} edits); anchors: "
          + ", ".join(f"{r['id']}×{r['candidates']}" for r in recs.values() if r["anchor"]))
    if beats is not None:
        print(f"coverage: {len([b for b in beats if b in covered])}/{len(beats)} beats, "
              f"{len([q for q in insets if q in cq])}/{len(insets)} insets (via REUSE.md crops and local edits)")
    print(f"longest composed prompt: {longest['id']} {len(compose_prompt(longest, recs))} chars")
    print(f"art direction overlay: {'ON' if (meta.get('_style_overlay') or '').strip() else 'off'}; "
          f"clarifications: {', '.join(clar) or 'none'}")
    print("sample round: " + ", ".join(j["job"] for j in jobs_for(recs, "samples")))
    for w in warns:
        print("WARN", w)
    for x in errs:
        print("ERROR", x)
    print("check: OK" if not errs else f"check: {len(errs)} error(s)")
    return 0 if not errs else 1


def cmd_index(a):
    recs = parse_records()
    rows = []
    for r in sorted(recs.values(), key=lambda x: x["order"]):
        refs = ", ".join(x["id"] for x in r["refs"]) or "none"
        flag = "⚓ " if r["anchor"] else ""
        rows.append(f"| {flag}**{r['id']}** | {r['title']} | {r['treatment']} | {r['ratio']} {r['target']} | {refs} | "
                    f"{r.get('family')} | {r.get('set')}{' ×' + str(r['candidates']) if r['anchor'] else ''} | "
                    f"{', '.join(r['beats']) or '—'}{(' · ' + ', '.join(r['insets'])) if r['insets'] else ''} |")
    beats, insets = manuscript_beats()
    bm = [f"| {b} | {', '.join(r['id'] for r in sorted(recs.values(), key=lambda x: x['order']) if b in r['beats']) or '**MISSING**'} |"
          for b in (beats or [])]
    text = ["# RECORDS: the 27 location images and the story moments they serve", "",
            "Generated by `python3 bg.py index`. ⚓ = anchor: made as candidates, and the user picks one. "
            "Every other story moment comes from these images by crops and local edits (`REUSE.md`).", "",
            "| ID | Image | Treatment | Ratio, target px | References | Lane | Set | Beats served (via reuse) |",
            "|---|---|---|---|---|---|---|---|", *rows, "",
            "## Beat → record map", "", "| Visual beat | Record(s) |", "|---|---|", *bm, "",
            "## Companion insets (soft-edged crops)", "", "| Inset | Record |", "|---|---|",
            *[f"| {q} | {', '.join(r['id'] for r in recs.values() if q in r['insets']) or '**MISSING**'} |" for q in (insets or [])], ""]
    with open(p("RECORDS.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(text))
    print(f"wrote RECORDS.md ({len(recs)} records, {len(bm)} beats)")
    return 0


def cmd_urls(a):
    path = p("output", "_uploads.json")
    with Lock():
        data = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
        key = os.path.abspath(a.path)
        digest = sha256(key) if os.path.exists(key) else ""
        if a.action == "get":
            hit = data.get(key)
            print(hit["url"] if hit and hit.get("sha") == digest else "")
            return 0 if hit and hit.get("sha") == digest else 1
        data[key] = {"url": a.url, "sha": digest, "at": stamp()}
        with open(path + ".tmp", "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=1)
        os.replace(path + ".tmp", path)
        print("saved")
    return 0


# =========================================================================== selftest

def cmd_selftest(a):
    from PIL import Image
    tmp = tempfile.mkdtemp(prefix="bg2-selftest-")
    shutil.copytree(p("prompts"), os.path.join(tmp, "prompts"))
    shutil.copy(p(META_FILE), os.path.join(tmp, META_FILE))
    for sub in ("_candidates", "_claims", "_sheets", "native"):
        os.makedirs(os.path.join(tmp, "output", sub), exist_ok=True)
    env = dict(os.environ, BG_ROOT=tmp, BG_FAST="1")
    me = os.path.abspath(__file__)
    ok = True
    sizes = {"16:9": (1600, 900), "4:3": (1200, 900), "3:2": (1350, 900)}
    global ROOT
    old_root, ROOT = ROOT, tmp
    recs = parse_records()

    def run(*args):
        r = subprocess.run([sys.executable, me, *args], env=env, capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    def claim_all(which, n=8):
        procs = [subprocess.Popen([sys.executable, me, "claim", "--set", which, "--worker", f"T{i}", "--json"],
                                  env=env, stdout=subprocess.PIPE, text=True) for i in range(n)]
        got = []
        for pr in procs:
            try:
                d = json.loads(pr.communicate()[0])
            except json.JSONDecodeError:
                continue
            if "job" in d:
                got.append(d)
        return got

    seed = [0]

    def fake(path, ratio):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        seed[0] += 1
        rnd = random.Random(seed[0])
        Image.new("RGB", sizes[ratio], tuple(rnd.randint(0, 255) for _ in range(3))).save(path)

    def check(cond, msg):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + msg)
        ok = ok and cond

    try:
        got = claim_all("samples")
        j1 = sorted(d["job"] for d in got)
        check(len(j1) == len(set(j1)), f"8 concurrent claims: no job handed out twice ({len(j1)} handed out)")
        check(j1 == ["001-A", "001-B", "001-C"], f"round 1 = master 001 x3 (got {j1})")
        rc, out = run("done", "001-A", "--worker", "T0")
        check(rc != 0 and "REFUSED" in out, "done refuses a missing file")
        Image.new("RGB", (1200, 900), (1, 2, 3)).save(got[0]["save_as"])
        rc, out = run("done", got[0]["job"], "--worker", "T")
        check(rc != 0 and "aspect" in out, "done refuses a wrong ratio (4:3 image for a 16:9 record)")
        for d in got:
            fake(d["save_as"], d["ratio"])
            run("done", d["job"], "--worker", "T")
        check(os.path.exists(os.path.join(tmp, "output", "_candidates", "native", "CH01_LOC_001-A_native.png")),
              "the native file is retained")
        rc, out = run("claim", "--set", "samples", "--worker", "T9")
        check("PICK NEEDED: 001" in out, "claim reports PICK NEEDED for 001")
        run("pick", "001", "B")
        got2 = claim_all("samples", 12)
        j2 = sorted(d["job"] for d in got2)
        want2 = sorted(f"{x}-{c}" for x in ("002", "008", "015", "019") for c in "AB")
        check(j2 == want2, f"after the pick the 4 sublocation anchors x2 are released ({len(j2)} jobs)")
        with open(os.path.join(tmp, "output", "_claims", "002-A.claim"), "w") as fh:
            json.dump({"worker": "dead", "t": now() - STALE_CLAIM_S - 5}, fh)
        rc, out = run("claim", "--set", "samples", "--worker", "T1", "--json")
        check('"002-A"' in out, "a stale claim (> 30 min) is reclaimed")
        for d in got2:
            fake(d["save_as"], d["ratio"])
            run("done", d["job"], "--worker", "T")
        shutil.copy(os.path.join(tmp, "output", "_candidates", "native", "CH01_LOC_002-A_native.png"),
                    os.path.join(tmp, "output", "dup.png"))
        for x in ("002", "008", "015", "019"):
            run("pick", x, "A")
        # full run
        violations, n_jobs, pick_seen, dup_tested = 0, 0, False, False
        for _ in range(100):
            batch = claim_all("full", 4)
            if not batch:
                rc, out = run("claim", "--set", "full", "--worker", "T")
                if "PICK NEEDED: 024" in out:
                    pick_seen = True
                    run("pick", "024", "A")
                    continue
                break
            for d in batch:
                for ref in recs[d["id"]]["refs"]:
                    if not os.path.exists(out_path(recs[ref["id"]])):
                        violations += 1
                if d["id"] in ("025", "026", "027") and not os.path.exists(out_path(recs["024"])):
                    violations += 1
                if not dup_tested and d["ratio"] == "4:3":
                    dup_tested = True
                    shutil.copy(os.path.join(tmp, "output", "dup.png"), d["save_as"])
                    rc, out = run("done", d["job"], "--worker", "T")
                    check(rc != 0 and "identical" in out, "done refuses an image already recorded for another job")
                fake(d["save_as"], d["ratio"])
                rc, out = run("done", d["job"], "--worker", "T")
                n_jobs += 1
        check(violations == 0, "no record was handed out before every image it references was accepted")
        check(pick_seen, "the run pauses for the 024 pick before 025, 026 and 027")
        rc, out = run("claim", "--set", "full", "--worker", "T", "--json")
        n_acc = sum(1 for r in recs.values() if os.path.exists(out_path(r)))
        check('"ALL DONE"' in out and n_acc == len(recs),
              f"full run drains to ALL DONE with all {n_acc}/{len(recs)} records accepted ({n_jobs} jobs after the samples)")
    finally:
        ROOT = old_root
        shutil.rmtree(tmp, ignore_errors=True)
    print("selftest: OK" if ok else "selftest: FAILED")
    return 0 if ok else 1


# =========================================================================== main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    im = sub.add_parser("import")
    im.add_argument("docx", nargs="?", default=DEFAULT_DOCX)
    im.add_argument("--force", action="store_true")
    sub.add_parser("check")
    c = sub.add_parser("claim")
    c.add_argument("--worker", required=True)
    c.add_argument("--prefer", default="")
    c.add_argument("--set", choices=["samples", "full"], default="full")
    c.add_argument("--json", action="store_true")
    c.add_argument("--dry-run", action="store_true")
    d = sub.add_parser("done")
    d.add_argument("job")
    d.add_argument("--worker", default="?")
    d.add_argument("--note", default="")
    d.add_argument("--crop", action="store_true", help="centre-crop to the record ratio (only if no required equipment is lost)")
    d.add_argument("--force", action="store_true")
    r = sub.add_parser("release")
    r.add_argument("job")
    pk = sub.add_parser("pick")
    pk.add_argument("id")
    pk.add_argument("letter")
    s = sub.add_parser("status")
    s.add_argument("--set", choices=["samples", "full"], default="full")
    sh = sub.add_parser("sheet")
    sh.add_argument("--set", choices=["samples", "full"], default="full")
    sub.add_parser("index")
    z = sub.add_parser("zoom")
    z.add_argument("file")
    z.add_argument("box", help="x0,y0,x1,y1 as fractions, e.g. 0.6,0.3,0.9,0.6")
    u = sub.add_parser("urls")
    u.add_argument("action", choices=["get", "set"])
    u.add_argument("path")
    u.add_argument("url", nargs="?", default="")
    sub.add_parser("selftest")
    a = ap.parse_args()
    fn = {"import": cmd_import, "check": cmd_check, "claim": cmd_claim, "done": cmd_done, "release": cmd_release,
          "pick": cmd_pick, "status": cmd_status, "sheet": cmd_sheet, "index": cmd_index, "zoom": cmd_zoom,
          "urls": cmd_urls, "selftest": cmd_selftest}[a.cmd]
    sys.exit(fn(a))


if __name__ == "__main__":
    main()
