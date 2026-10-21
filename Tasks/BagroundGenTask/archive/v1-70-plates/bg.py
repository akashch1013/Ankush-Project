#!/usr/bin/env python3
"""bg.py: shared work queue for the ChandRush Chapter 01 background plates.

Any number of workers (Codex sub-agents, `codex exec` processes, Claude sub-agents,
or a person in ChatGPT) can run at once. Claims are atomic, so no plate is
generated twice, and an edit only becomes ready once its parent file exists.

Commands:
  check                         validate prompts/*.md and coverage of the manuscript
  claim  --worker W [--prefer LB,TB] [--set samples|full] [--json] [--dry-run]
  done   JOB --worker W [--note "..."] [--force]
  release JOB
  pick   PLATE LETTER           copy a sample candidate to the plate's save path
  status [--set samples|full]
  sheet  [--set samples|full] [--family LB]
  index                         rewrite PLATES.md from prompts/*.md
  urls   get PATH | set PATH URL   (cache of uploaded reference URLs, e.g. for Higgsfield)
  selftest                      concurrency and dependency test in a scratch copy

A job is a plate ID (e.g. LB-04b) or, for sample candidates, an ID plus a letter
(e.g. LS-01-B). Done means the job's output file exists.
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

FAMILIES = ["LS", "LB", "TB", "KB", "HR", "MR", "CP", "GT", "FS"]
ASPECTS = {
    "16:9": ("landscape 16:9", "1672x941"),
    "4:3": ("landscape 4:3", "1448x1086"),
    "3:4": ("portrait 3:4", "1086x1448"),
}
MAX_PROMPT = 1800
STALE_CLAIM_S = 30 * 60
STALE_LOCK_S = 120
MANUSCRIPT = os.path.join("..", "..", "CH01-INTEGRATED-MANUSCRIPT-V04.docx")
ID_RE = r"(?:LS|LB|TB|KB|HR|MR|CP|GT|FS)-\d\d[a-z]?R?"

ROOT = os.environ.get("BG_ROOT") or os.path.dirname(os.path.abspath(__file__))
ASSUME_FILE_REFS = os.environ.get("BG_ASSUME_FILE_REFS") == "1"


def p(*parts):
    return os.path.join(ROOT, *parts)


def now():
    return time.time()


def stamp():
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# --------------------------------------------------------------------------- parsing

def parse_plates():
    plates, order = {}, 0
    for fam in FAMILIES:
        path = p("prompts", f"{fam}.md")
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8").read()
        for m in re.finditer(r"^## (\S+) · (.+?)\n(.*?)(?=^## |\Z)", text, re.M | re.S):
            pid, title, body = m.group(1), m.group(2).strip(), m.group(3)
            pl = {"id": pid, "title": title, "file": f"prompts/{fam}.md", "order": order,
                  "refs": [], "checks": [], "prompt": "", "errors": []}
            order += 1
            in_refs = False
            for line in body.splitlines():
                fm = re.match(r"^- (\w+):\s*(.*)$", line)
                if fm and not line.startswith("- [") and fm.group(1) in (
                        "family", "kind", "parent", "set", "candidates", "anchor", "aspect",
                        "refs", "save", "beats", "insets", "slug"):
                    key, val = fm.group(1), fm.group(2).strip()
                    in_refs = key == "refs"
                    if key != "refs":
                        pl[key] = val
                    continue
                rm = re.match(r"^\s+(\d+)\.\s+(.*?)\s+—\s+(.*)$", line)
                if in_refs and rm:
                    target = rm.group(2).strip().strip("`")
                    pl["refs"].append({"n": int(rm.group(1)), "target": target, "role": rm.group(3).strip()})
                    continue
                if line.strip() and not line.startswith("  "):
                    in_refs = False
            tm = re.search(r"```text\n(.*?)\n```", body, re.S)
            if tm:
                pl["prompt"] = tm.group(1).strip()
            cm = re.search(r"\*\*Checks\*\*\n(.*?)(?=\n---|\Z)", body, re.S)
            if cm:
                pl["checks"] = [l[2:].strip() for l in cm.group(1).splitlines() if l.startswith("- ")]
            pl["candidates"] = int(pl.get("candidates", "1") or 1)
            pl["anchor"] = pl.get("anchor", "no").lower() == "yes"
            pl["beats"] = parse_beats(pl.get("beats", "—"))
            pl["insets"] = re.findall(r"Q\d\d", pl.get("insets", ""))
            if pid in plates:
                pl["errors"].append("duplicate id")
            plates[pid] = pl
    return plates


def parse_beats(s):
    out = []
    for part in s.split(";"):
        m = re.match(r"\s*(\d\d[A-Z])\s+([A-Z](?:\s*,\s*[A-Z])*)", part)
        if m:
            for letter in re.split(r"\s*,\s*", m.group(2)):
                out.append(f"{m.group(1)} {letter}")
    return out


def ref_path(plates, target):
    """Absolute path for a ref target: '@ID' (another plate's save file) or a file path."""
    if target.startswith("@"):
        pl = plates.get(target[1:])
        return p(pl["save"].strip("`")) if pl else None
    return os.path.normpath(os.path.join(ROOT, target))


def ref_exists(plates, target):
    path = ref_path(plates, target)
    if path is None:
        return False
    if not target.startswith("@") and ASSUME_FILE_REFS:
        return True
    return os.path.exists(path)


# --------------------------------------------------------------------------- jobs

def jobs_for(plates, which):
    """List of job dicts in run order for set 'samples' or 'full'."""
    jobs = []
    for pl in sorted(plates.values(), key=lambda x: x["order"]):
        if which == "samples" and pl.get("set") != "samples":
            continue
        if pl["anchor"]:
            if which == "samples":
                for i in range(pl["candidates"]):
                    letter = "ABCDEFGH"[i]
                    jobs.append({"job": f"{pl['id']}-{letter}", "plate": pl,
                                 "out": p("output", "_candidates", f"{pl['id']}-{letter}.png"),
                                 "candidate": letter})
            else:
                jobs.append({"job": pl["id"], "plate": pl, "out": p(pl["save"].strip("`")),
                             "candidate": None, "needs_pick": True})
        else:
            jobs.append({"job": pl["id"], "plate": pl, "out": p(pl["save"].strip("`")), "candidate": None})
    return jobs


def find_job(plates, job_id):
    for which in ("samples", "full"):
        for j in jobs_for(plates, which):
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


def job_state(plates, j):
    """done | claimed | ready | pick | waiting"""
    if os.path.exists(j["out"]):
        return "done"
    if claim_active(j["job"]):
        return "claimed"
    if j.get("needs_pick"):
        return "pick"
    missing = [r["target"] for r in j["plate"]["refs"] if not ref_exists(plates, r["target"])]
    if missing:
        j["missing"] = missing
        return "waiting"
    return "ready"


# --------------------------------------------------------------------------- lock

class Lock:
    """Global mutex for queue changes: mkdir is atomic on every local filesystem."""

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


# --------------------------------------------------------------------------- image helpers

def try_pil():
    try:
        from PIL import Image  # noqa: F401
        return True
    except ImportError:
        return False


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


def ledger_add(job, worker, digest):
    with open(p("output", "_ledger.tsv"), "a", encoding="utf-8") as fh:
        fh.write(f"{job}\t{worker}\t{digest}\t{stamp()}\n")


def normalise_image(path, aspect):
    """Verify the file is an image, convert to real PNG, return (w, h, warnings)."""
    warnings = []
    if not try_pil():
        return None, None, ["PIL not installed: image not verified"]
    from PIL import Image
    with Image.open(path) as im:
        im.load()
        fmt, w, h = im.format, im.width, im.height
        if fmt != "PNG":
            im.convert("RGB").save(path, "PNG")
            warnings.append(f"converted {fmt} to PNG")
    if max(w, h) < 600:
        raise ValueError(f"image too small ({w}x{h})")
    if aspect in ASPECTS:
        a, b = (int(x) for x in aspect.split(":"))
        want, got = a / b, w / h
        if abs(got - want) / want > 0.12:
            warnings.append(f"aspect {w}x{h} differs from {aspect}: check key content is inside the frame")
    return w, h, warnings


# --------------------------------------------------------------------------- printing

def job_payload(plates, j, worker):
    pl = j["plate"]
    aspect = pl.get("aspect", "")
    words, px = ASPECTS.get(aspect, (aspect, "?"))
    refs = []
    for r in sorted(pl["refs"], key=lambda r: r["n"]):
        refs.append({"image": r["n"], "path": ref_path(plates, r["target"]), "role": r["role"]})
    return {
        "job": j["job"], "plate": pl["id"], "title": pl["title"], "family": pl.get("family"),
        "kind": pl.get("kind"), "parent": pl.get("parent"), "candidate": j["candidate"],
        "aspect": aspect, "aspect_words": words, "pixel_hint": px,
        "refs": refs, "save_as": j["out"], "prompt": pl["prompt"], "checks": pl["checks"],
        "done_cmd": f"python3 bg.py done {j['job']} --worker {worker}",
    }


def print_job(d):
    print(f"JOB {d['job']}  ·  {d['title']}  ·  {d['kind']}" + (f" of {d['parent']}" if d['kind'] == 'edit' else ""))
    print(f"ASPECT {d['aspect']}: ask for {d['aspect_words']} (about {d['pixel_hint']} px); Higgsfield aspect_ratio={d['aspect']}")
    print("ATTACH, in this order (Image 1 first):")
    for r in d["refs"]:
        print(f"  Image {r['image']}: {r['path']}\n           role: {r['role']}")
    print(f"SAVE AS: {d['save_as']}")
    print("-----BEGIN PROMPT-----")
    print(d["prompt"])
    print("-----END PROMPT-----")
    print("CHECKS (open the saved image and tick every line):")
    for c in d["checks"]:
        print(f"  [ ] {c}")
    print(f"THEN: {d['done_cmd']}   (add --note \"...\" if a check still fails after one fix)")


# --------------------------------------------------------------------------- commands

def cmd_claim(a):
    plates = parse_plates()
    prefer = [f.strip() for f in (a.prefer or "").split(",") if f.strip()]
    with Lock():
        jobs = jobs_for(plates, a.set)
        states = [(j, job_state(plates, j)) for j in jobs]
        ready = [j for j, s in states if s == "ready"]
        if prefer:
            ready.sort(key=lambda j: (0 if j["plate"].get("family") in prefer else 1, j["plate"]["order"]))
        if ready:
            j = ready[0]
            if not a.dry_run:
                with open(claim_path(j["job"]), "w", encoding="utf-8") as fh:
                    json.dump({"worker": a.worker, "t": now(), "at": stamp()}, fh)
            d = job_payload(plates, j, a.worker)
            print(json.dumps(d, indent=1)) if a.json else print_job(d)
            return 0
    # nothing ready
    if all(s == "done" for _, s in states):
        print(json.dumps({"status": "ALL DONE"}) if a.json else "ALL DONE")
        return 3
    picks = sorted({j["plate"]["id"] for j, s in states if s == "pick"})
    waiting_on_pick = set()
    for j, s in states:
        if s == "waiting":
            for t in j.get("missing", []):
                if t.startswith("@") and plates.get(t[1:], {}).get("anchor"):
                    waiting_on_pick.add(t[1:])
    if a.set == "samples":
        for pid in sorted(waiting_on_pick):
            cands = [x for x, s in states if x["plate"]["id"] == pid and x["candidate"]]
            if cands and all(os.path.exists(x["out"]) for x in cands):
                picks.append(pid)
    picks = sorted(set(picks))
    claimed = [j["job"] for j, s in states if s == "claimed"]
    msg = {"status": "WAIT", "claimed_by_others": claimed, "pick_needed": picks}
    if a.json:
        print(json.dumps(msg))
    else:
        if picks:
            print("PICK NEEDED: " + ", ".join(picks) + " (candidates in output/_candidates; the user chooses, "
                  "then: python3 bg.py pick <ID> <letter>)")
        print("WAIT: nothing is ready right now. In progress elsewhere: " + (", ".join(claimed) or "none"))
    return 4 if picks and not claimed else 2


def cmd_done(a):
    plates = parse_plates()
    j = find_job(plates, a.job)
    if not j:
        sys.exit(f"unknown job {a.job}")
    if not os.path.exists(j["out"]):
        sys.exit(f"REFUSED: {j['out']} does not exist. Save the image there first.")
    try:
        w, h, warns = normalise_image(j["out"], j["plate"].get("aspect", ""))
    except Exception as e:  # noqa: BLE001
        sys.exit(f"REFUSED: {j['out']} is not a usable image ({e})")
    digest = sha256(j["out"])
    with Lock():
        dup = [r for r in ledger_rows() if r["sha"] == digest and r["job"] != a.job]
        if dup and not a.force:
            sys.exit(f"REFUSED: identical file already recorded for {dup[0]['job']}. "
                     "You probably copied the wrong image. Copy the savedPath of THIS generation.")
        ledger_add(a.job, a.worker, digest)
        if a.note:
            with open(p("output", "REVIEW-NOTES.md"), "a", encoding="utf-8") as fh:
                fh.write(f"- **{a.job}** ({a.worker}, {stamp()}): {a.note}\n")
        try:
            os.remove(claim_path(a.job))
        except FileNotFoundError:
            pass
    print(f"DONE {a.job} ({w}x{h})" + ("" if not warns else "  NOTE: " + "; ".join(warns)))
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
    plates = parse_plates()
    pl = plates.get(a.plate)
    if not pl or not pl["anchor"]:
        sys.exit(f"{a.plate} is not an anchor plate")
    src = p("output", "_candidates", f"{a.plate}-{a.letter.upper()}.png")
    if not os.path.exists(src):
        sys.exit(f"no candidate {src}")
    dst = p(pl["save"].strip("`"))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        os.replace(dst, dst[:-4] + f".replaced-{int(now())}.png")
    shutil.copy2(src, dst)
    with Lock():
        ledger_add(a.plate, f"pick-{a.letter.upper()}", sha256(dst))
    print(f"PICKED {a.plate} = candidate {a.letter.upper()} → {dst}")
    return 0


def cmd_status(a):
    plates = parse_plates()
    jobs = jobs_for(plates, a.set)
    by_fam, claimed, picks = {}, [], set()
    for j in jobs:
        s = job_state(plates, j)
        fam = j["plate"].get("family", "?")
        by_fam.setdefault(fam, {"done": 0, "total": 0, "ready": 0, "claimed": 0, "waiting": 0, "pick": 0})
        by_fam[fam]["total"] += 1
        by_fam[fam][s] = by_fam[fam].get(s, 0) + 1
        if s == "claimed":
            c = read_claim(j["job"])
            claimed.append(f"{j['job']} by {c['worker']} for {int((now() - c['t']) / 60)} min")
        if s == "pick":
            picks.add(j["plate"]["id"])
    tot = sum(v["total"] for v in by_fam.values())
    done = sum(v["done"] for v in by_fam.values())
    print(f"Set: {a.set}   done {done}/{tot}")
    print("family  done/total  ready  claimed  waiting  pick")
    for fam in FAMILIES:
        if fam in by_fam:
            v = by_fam[fam]
            print(f"{fam:6}  {v['done']:>4}/{v['total']:<5}  {v['ready']:>5}  {v['claimed']:>7}  {v['waiting']:>7}  {v['pick']:>4}")
    if claimed:
        print("In progress: " + "; ".join(claimed))
    if picks:
        print("Anchors still to pick (run the sample round first): " + ", ".join(sorted(picks)))
    notes = p("output", "REVIEW-NOTES.md")
    if os.path.exists(notes):
        n = sum(1 for l in open(notes, encoding="utf-8") if l.startswith("- "))
        print(f"REVIEW-NOTES.md: {n} accepted issue(s)")
    return 0


def _font(size):
    from PIL import ImageFont
    for cand in (os.path.join(ROOT, "..", "ShotGenTask", "fonts", "SourceSans3-Semibold.ttf"),
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(cand):
            return ImageFont.truetype(cand, size)
    return ImageFont.load_default()


def make_sheet(items, out_path, title):
    from PIL import Image, ImageDraw
    if not items:
        return False
    tw, th, pad, lab = 480, 300, 16, 34
    cols = min(4, len(items))
    rows = (len(items) + cols - 1) // cols
    W = cols * (tw + pad) + pad
    H = rows * (th + lab + pad) + pad + 50
    sheet = Image.new("RGB", (W, H), (22, 28, 40))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 12), title, fill=(240, 230, 200), font=_font(26))
    for i, (label, path) in enumerate(items):
        r, c = divmod(i, cols)
        x, y = pad + c * (tw + pad), 50 + pad + r * (th + lab + pad)
        try:
            with Image.open(path) as im:
                im = im.convert("RGB")
                im.thumbnail((tw, th))
                sheet.paste(im, (x + (tw - im.width) // 2, y + (th - im.height) // 2))
        except Exception:  # noqa: BLE001
            d.rectangle([x, y, x + tw, y + th], outline=(200, 80, 80))
        d.text((x, y + th + 6), label, fill=(235, 235, 235), font=_font(20))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    sheet.save(out_path)
    return True


def cmd_sheet(a):
    if not try_pil():
        sys.exit("PIL (Pillow) is needed for contact sheets")
    plates = parse_plates()
    made = []
    if a.set == "samples":
        items = []
        for j in jobs_for(plates, "samples"):
            if os.path.exists(j["out"]):
                items.append((f"{j['job']}  {j['plate']['title'][:34]}", j["out"]))
            pl = j["plate"]
            if pl["anchor"] and os.path.exists(p(pl["save"].strip("`"))) and j["candidate"] == "A":
                items.append((f"{pl['id']}  PICKED", p(pl["save"].strip("`"))))
        out = p("output", "_sheets", "SAMPLES.png")
        if make_sheet(items, out, "ChandRush CH01 backgrounds: sample round"):
            made.append(out)
    else:
        for fam in FAMILIES:
            if a.family and fam != a.family:
                continue
            items = []
            for pl in sorted(plates.values(), key=lambda x: x["order"]):
                if pl.get("family") == fam and os.path.exists(p(pl["save"].strip("`"))):
                    items.append((f"{pl['id']}  {pl['title'][:36]}", p(pl["save"].strip("`"))))
            out = p("output", "_sheets", f"{fam}.png")
            if make_sheet(items, out, f"ChandRush CH01 backgrounds: {fam}"):
                made.append(out)
    print("\n".join(made) if made else "nothing to show yet")
    return 0


def manuscript_beats():
    path = p(MANUSCRIPT)
    if not os.path.exists(path):
        return None, None
    xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
    text = re.sub(r"<[^>]+>", "", re.sub(r"</w:p>", "\n", xml))
    beats = list(dict.fromkeys(f"{m.group(1)} {m.group(2)}"
                               for m in re.finditer(r"Visual beat CH01 (\d\d[A-Z]) ([A-Z])\b", text)))
    insets = sorted(set(re.findall(r"Companion inset (Q\d\d)", text)))
    return beats, insets


def cmd_check(a):
    plates = parse_plates()
    errs, warns = [], []
    if not plates:
        sys.exit("no plates found in prompts/*.md")
    ids = set(plates)
    for pid, pl in plates.items():
        e = lambda msg: errs.append(f"{pid}: {msg}")  # noqa: E731
        for x in pl["errors"]:
            e(x)
        fam = pl.get("family")
        if fam not in FAMILIES or not pid.startswith(fam + "-"):
            e(f"family '{fam}' does not match id")
        if pl.get("kind") not in ("base", "edit"):
            e("kind must be base or edit")
        if pl.get("set") not in ("samples", "full"):
            e("set must be samples or full")
        if pl.get("aspect") not in ASPECTS:
            e(f"aspect '{pl.get('aspect')}' not one of {list(ASPECTS)}")
        save = (pl.get("save") or "").strip("`")
        if not re.match(rf"output/{fam}/{re.escape(pid)}_[a-z0-9-]+\.png$", save):
            e(f"save path '{save}' should be output/{fam}/{pid}_<slug>.png")
        if pl["anchor"] and (pl["candidates"] < 2 or pl.get("set") != "samples"):
            e("anchor plates need set: samples and candidates ≥ 2")
        if not pl["refs"]:
            e("no refs")
        for r in pl["refs"]:
            t = r["target"]
            if t.startswith("@"):
                if t[1:] not in ids:
                    e(f"ref {t} is not a plate")
            elif not os.path.exists(ref_path(plates, t)):
                e(f"ref file missing: {t}")
        if pl.get("kind") == "edit":
            par = pl.get("parent", "")
            first = sorted(pl["refs"], key=lambda r: r["n"])[0]["target"] if pl["refs"] else ""
            if not par or par == "—":
                e("edit without parent")
            elif first not in ("@" + par, par) and not first.endswith(par):
                e(f"edit parent {par} must be Image 1 (got {first})")
        pr = pl["prompt"]
        if not pr:
            e("no ```text prompt block")
        else:
            if len(pr) > MAX_PROMPT:
                e(f"prompt is {len(pr)} chars (max {MAX_PROMPT})")
            av = re.search(r"^Avoid:(.*)$", pr, re.M)
            if not av:
                e("prompt has no Avoid: line")
            else:
                low = av.group(1).lower()
                if not re.search(r"people|figure", low):
                    e("Avoid line must exclude people/figures")
                if "text" not in low:
                    e("Avoid line must exclude text")
            if re.search(ID_RE, pr):
                e("prompt mentions a plate ID (the image model cannot see IDs)")
            if re.search(r"\.png|\.jpg|output/", pr, re.I):
                e("prompt mentions a filename")
            for n in re.findall(r"Image (\d+)", pr):
                if int(n) > len(pl["refs"]):
                    e(f"prompt mentions Image {n} but only {len(pl['refs'])} attached")
        if len(pl["checks"]) < 2:
            e("needs at least 2 checks")
    # dependency cycles
    def deps(pid):
        return [r["target"][1:] for r in plates[pid]["refs"] if r["target"].startswith("@") and r["target"][1:] in ids]
    state = {}
    def visit(pid, stack):
        if state.get(pid) == 1:
            errs.append("dependency cycle: " + " → ".join(stack + [pid]))
            return
        if state.get(pid) == 2:
            return
        state[pid] = 1
        for d in deps(pid):
            visit(d, stack + [pid])
        state[pid] = 2
    for pid in ids:
        visit(pid, [])
    # coverage
    beats, insets = manuscript_beats()
    covered = {b for pl in plates.values() for b in pl["beats"]}
    covered_q = {q for pl in plates.values() for q in pl["insets"]}
    if beats is None:
        warns.append("manuscript not found: beat coverage not checked")
    else:
        missing = [b for b in beats if b not in covered]
        extra = sorted(covered - set(beats))
        if missing:
            errs.append(f"{len(missing)} manuscript beats have no plate: {', '.join(missing)}")
        if extra:
            errs.append(f"plates list beats not in the manuscript: {', '.join(extra)}")
        mq = [q for q in insets if q not in covered_q]
        if mq:
            errs.append("insets with no plate: " + ", ".join(mq))
    n_base = sum(1 for x in plates.values() if x.get("kind") == "base")
    n_edit = sum(1 for x in plates.values() if x.get("kind") == "edit")
    longest = max(plates.values(), key=lambda x: len(x["prompt"]))
    print(f"plates: {len(plates)} ({n_base} base, {n_edit} edit); anchors: "
          f"{', '.join(x['id'] for x in plates.values() if x['anchor'])}")
    if beats is not None:
        print(f"coverage: {len({b for b in beats if b in covered})}/{len(beats)} beats, "
              f"{len([q for q in insets if q in covered_q])}/{len(insets)} insets")
    print(f"longest prompt: {longest['id']} {len(longest['prompt'])} chars")
    sj = jobs_for(plates, "samples")
    print(f"sample round: {len(sj)} jobs ({', '.join(j['job'] for j in sj)})")
    for w in warns:
        print("WARN", w)
    for x in errs:
        print("ERROR", x)
    print("check: OK" if not errs else f"check: {len(errs)} error(s)")
    return 0 if not errs else 1


def cmd_index(a):
    plates = parse_plates()
    rows = []
    for pl in sorted(plates.values(), key=lambda x: x["order"]):
        kind = pl.get("kind", "")
        if kind == "edit":
            kind += f" of {pl.get('parent')}"
        beats = ", ".join(pl["beats"]) or "—"
        ins = ", ".join(pl["insets"])
        flag = "⚓ " if pl["anchor"] else ""
        rows.append(f"| {flag}**{pl['id']}** | {pl['title']} | {kind} | {pl.get('aspect')} | {pl.get('set')} | "
                    f"{beats}{(' · insets ' + ins) if ins else ''} | `{pl['save'].strip('`')}` |")
    beats, insets = manuscript_beats()
    beat_map = []
    if beats:
        for b in beats:
            owners = [pl["id"] for pl in sorted(plates.values(), key=lambda x: x["order"]) if b in pl["beats"]]
            beat_map.append(f"| {b} | {', '.join(owners) or '**MISSING**'} |")
    text = [
        "# PLATES — every background plate and the beats it serves",
        "",
        "Generated by `python3 bg.py index` from `prompts/*.md`. Do not edit by hand; edit the prompt files.",
        "",
        f"{len(plates)} plates. ⚓ = anchor (made as 2–3 candidates in the sample round; the user picks one). "
        "Edits change only a state of their parent plate.",
        "",
        "| Plate | Title | Kind | Aspect | Set | Beats served | File |",
        "|---|---|---|---|---|---|---|",
        *rows,
        "",
        "## Beat → plate map (from the manuscript)",
        "",
        "| Visual beat | Plate(s) |",
        "|---|---|",
        *beat_map,
        "",
        "## Companion insets",
        "",
        "Insets are soft-edged crops of these plates (no extra generation).",
        "",
        "| Inset | Plate |",
        "|---|---|",
        *[f"| {q} | {', '.join(pl['id'] for pl in plates.values() if q in pl['insets']) or '**MISSING**'} |"
          for q in (insets or [])],
        "",
    ]
    with open(p("PLATES.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(text))
    print(f"wrote PLATES.md ({len(plates)} plates, {len(beat_map)} beats)")
    return 0


def cmd_urls(a):
    path = p("output", "_uploads.json")
    with Lock():
        data = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
        key = os.path.abspath(a.path)
        digest = sha256(key) if os.path.exists(key) else ""
        if a.action == "get":
            hit = data.get(key)
            if hit and hit.get("sha") == digest:
                print(hit["url"])
                return 0
            print("")
            return 1
        data[key] = {"url": a.url, "sha": digest, "at": stamp()}
        with open(path + ".tmp", "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=1)
        os.replace(path + ".tmp", path)
        print("saved")
    return 0


# --------------------------------------------------------------------------- selftest

def cmd_selftest(a):
    if not try_pil():
        sys.exit("selftest needs Pillow")
    from PIL import Image
    tmp = tempfile.mkdtemp(prefix="bg-selftest-")
    shutil.copytree(p("prompts"), os.path.join(tmp, "prompts"))
    for sub in FAMILIES + ["_candidates", "_claims", "_sheets"]:
        os.makedirs(os.path.join(tmp, "output", sub), exist_ok=True)
    env = dict(os.environ, BG_ROOT=tmp, BG_ASSUME_FILE_REFS="1")
    me = os.path.abspath(__file__)
    ok = True

    def run(*args):
        r = subprocess.run([sys.executable, me, *args], env=env, capture_output=True, text=True)
        return r.returncode, r.stdout.strip(), r.stderr.strip()

    def claim_all(which, n=8):
        procs = [subprocess.Popen([sys.executable, me, "claim", "--set", which, "--worker", f"T{i}", "--json"],
                                  env=env, stdout=subprocess.PIPE, text=True) for i in range(n)]
        got = []
        for pr in procs:
            out = pr.communicate()[0]
            try:
                d = json.loads(out)
            except json.JSONDecodeError:
                continue
            if "job" in d:
                got.append(d)
        return got

    def fake(path, seed):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        rnd = random.Random(seed)
        Image.new("RGB", (800, 600), (rnd.randint(0, 255), rnd.randint(0, 255), rnd.randint(0, 255))).save(path)

    def check(cond, msg):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + msg)
        ok = ok and cond

    # round 1: 8 concurrent workers on the sample set
    got = claim_all("samples")
    jobs1 = [d["job"] for d in got]
    check(len(jobs1) == len(set(jobs1)), f"8 concurrent claims, no job claimed twice ({len(jobs1)} claimed)")
    check(set(jobs1) == {"LS-01-A", "LS-01-B", "LS-01-C", "GT-01"},
          f"round 1 = LS-01 x3 + GT-01 (got {sorted(jobs1)})")
    rc, out, _ = run("done", "LS-01-A", "--worker", "T0")
    check(rc != 0 and "REFUSED" in (out + _), "done refuses a missing file")
    for i, d in enumerate(got):
        fake(d["save_as"], i)
        run("done", d["job"], "--worker", "T")
    # duplicate image refusal
    shutil.copy(got[0]["save_as"], os.path.join(tmp, "output", "GT", "dup.png"))
    # round 2 before pick: only GT-01b, then PICK NEEDED
    got2 = claim_all("samples")
    check([d["job"] for d in got2] == ["GT-01b"], f"before the pick only GT-01b is ready (got {[d['job'] for d in got2]})")
    shutil.copy(got[0]["save_as"], got2[0]["save_as"])
    rc, out, err = run("done", "GT-01b", "--worker", "T")
    check(rc != 0 and "identical" in (out + err), "done refuses an image already recorded for another job")
    fake(got2[0]["save_as"], 99)
    run("done", "GT-01b", "--worker", "T")
    rc, out, _ = run("claim", "--set", "samples", "--worker", "T9")
    check("PICK NEEDED: LS-01" in out, "claim reports PICK NEEDED for LS-01")
    run("pick", "LS-01", "B")
    got3 = claim_all("samples", 16)
    j3 = sorted(d["job"] for d in got3)
    want3 = sorted([f"{x}-{c}" for x in ("LB-01", "TB-01", "MR-01", "CP-01", "FS-01") for c in "AB"] + ["LS-01R"])
    check(j3 == want3, f"after the pick the S2 jobs are released ({len(j3)} jobs)")
    # stale claim reclaim: every other S2 claim stays live, only LB-01-A's claim is 30+ min old
    with open(os.path.join(tmp, "output", "_claims", "LB-01-A.claim"), "w") as fh:
        json.dump({"worker": "dead", "t": now() - STALE_CLAIM_S - 5}, fh)
    rc, out, _ = run("claim", "--set", "samples", "--worker", "T1", "--json")
    check('"LB-01-A"' in out, "a stale claim (> 30 min) is reclaimed")
    # finish samples and pick every anchor
    for i, d in enumerate(got3):
        fake(d["save_as"], 200 + i)
        run("done", d["job"], "--worker", "T")
    for x in ("LB-01", "TB-01", "MR-01", "CP-01", "FS-01"):
        run("pick", x, "A")
    # full run: claim greedily, verify every claimed job had all parents present at claim time
    plates_tmp = None
    os.environ["BG_ROOT"] = tmp
    global ROOT
    old_root, ROOT = ROOT, tmp
    try:
        plates_tmp = parse_plates()
        violations, done_count, seen = 0, 0, set()
        for rnd_i in range(200):
            batch = claim_all("full", 4)
            if not batch:
                break
            for d in batch:
                pl = plates_tmp[d["plate"]]
                for r in pl["refs"]:
                    if r["target"].startswith("@") and not os.path.exists(ref_path(plates_tmp, r["target"])):
                        violations += 1
                seen.add(d["job"])
                fake(d["save_as"], 1000 + done_count)
                done_count += 1
                run("done", d["job"], "--worker", "T")
        check(violations == 0, "no edit/plate was handed out before its parent existed")
        total_full = len([j for j in jobs_for(plates_tmp, "full")])
        rc, out, _ = run("claim", "--set", "full", "--worker", "T", "--json")
        check('"ALL DONE"' in out, f"full run drains to ALL DONE ({done_count} jobs generated in parallel batches; "
                                   f"{total_full} plates total)")
    finally:
        ROOT = old_root
    shutil.rmtree(tmp, ignore_errors=True)
    print("selftest: OK" if ok else "selftest: FAILED")
    return 0 if ok else 1


# --------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
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
    d.add_argument("--force", action="store_true")
    r = sub.add_parser("release")
    r.add_argument("job")
    pk = sub.add_parser("pick")
    pk.add_argument("plate")
    pk.add_argument("letter")
    s = sub.add_parser("status")
    s.add_argument("--set", choices=["samples", "full"], default="full")
    sh = sub.add_parser("sheet")
    sh.add_argument("--set", choices=["samples", "full"], default="full")
    sh.add_argument("--family", default="")
    sub.add_parser("index")
    u = sub.add_parser("urls")
    u.add_argument("action", choices=["get", "set"])
    u.add_argument("path")
    u.add_argument("url", nargs="?", default="")
    sub.add_parser("selftest")
    a = ap.parse_args()
    fn = {"check": cmd_check, "claim": cmd_claim, "done": cmd_done, "release": cmd_release, "pick": cmd_pick,
          "status": cmd_status, "sheet": cmd_sheet, "index": cmd_index, "urls": cmd_urls,
          "selftest": cmd_selftest}[a.cmd]
    sys.exit(fn(a))


if __name__ == "__main__":
    main()
