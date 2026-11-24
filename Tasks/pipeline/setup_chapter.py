#!/usr/bin/env python3
"""setup_chapter.py: turn an author's chapter folder in Reference/ into a ready workspace (free, no image calls).

The author drops a folder into Tasks/Reference/ (like "Chap 2/") holding
  CHxx-PANELIZED-MANUSCRIPT-Vnn.docx, CHxx-LOCATION-IMAGE-REGISTER-Vnn.docx and reference images.
This tool does every mechanical step. The chapter-setup agent does the judgement steps on top (see the
comic-setup skill), then every other agent starts from PdfSheetsGenTask/<CHxx>/chapter.json.

  scan [-v]                  every chapter folder in Reference/: chapter id, setup state
                             (new | ready | needs-agent | stale: the author gave a new version) and manuscript
                             (-v: also the register and image count)
  prep (CHxx | FOLDER) [--force] [-v]
                             dump manuscript + register, split pages into src/, survey, page index,
                             register records + plate status, cast + character sheets, manuscript
                             maths pre-scan, pages.json header, background workspace scaffold (when the
                             chapter has no plates yet), and chapter.json. Re-running after the author
                             gives a new version lists the changed pages (CHANGES.md). Idempotent.
                             -v also echoes the textcheck dump/pages lines.
  check CHxx [-v]            readiness checklist from chapter.json (exit 1 while anything is open);
                             prints the open items only (-v: every item)

Recording the setup agent's decisions (kept across re-preps until the author gives a new version):
  master CHxx "<register master name>" <image path>   which reference image is that master
  locate CHxx "<CH02 L03>" <record id> ...           manuscript location group -> register records
  mark CHxx <status key> "<note>"                    close an item (characters, maths, agent_review, ...)
                                                     with what was decided; the note goes to chapter.json notes

Outputs (all under Tasks/, never inside Reference/):
  PdfSheetsGenTask/<CHxx>/chapter.json   the manifest every agent reads first
  PdfSheetsGenTask/<CHxx>/manuscript.txt, register.txt, src/Pxxx.txt, survey.txt, index.json, mathscan.txt
  PdfSheetsGenTask/<CHxx>/pages.json     header only, if it did not exist
  BagroundGenTask/ch0N/                  jobs.json + briefs/ + prompts/ + refs/ (only for a chapter without plates)
  FInalChangesTask/<CHxx>/               jobs.json skeleton for panel art
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime

TASKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(TASKS, "pipeline"))
import mathcheck  # noqa: E402

REF = os.path.join(TASKS, "Reference")
SHEETS = "Charactors/CHANDRUSH CHARACTERS"     # relative to Tasks/
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")
# CH01 predates the per-chapter layout; its plates live at the top of BagroundGenTask.
LEGACY_PLATES = {"CH01": ("BagroundGenTask/", "BagroundGenTask/out/plates/")}


def rel(p):
    return os.path.relpath(p, TASKS)


def sha1(path):
    with open(path, "rb") as fh:
        return hashlib.sha1(fh.read()).hexdigest()[:12]


def version(name):
    m = re.search(r"-V(\d+)", name, re.I)
    return int(m.group(1)) if m else 0


def run(*args):
    r = subprocess.run([sys.executable, os.path.join(TASKS, "pipeline", "textcheck.py"), *args],
                       cwd=TASKS, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"textcheck {args[0]} failed:\n{r.stdout}{r.stderr}")
    return r.stdout


# ---------- Reference folders ----------
def folders():
    """{chapter: [folder info, ...]} for every non-'old' folder in Reference/ holding a CHxx manuscript."""
    out = defaultdict(list)
    if not os.path.isdir(REF):
        return out
    for d in sorted(os.listdir(REF)):
        full = os.path.join(REF, d)
        if not os.path.isdir(full) or re.search(r"\bold\b", d, re.I):
            continue
        files = sorted(f for f in os.listdir(full) if not f.startswith((".", "~")))
        ms = [f for f in files if re.match(r"CH\d{2}-.*MANUSCRIPT.*\.docx$", f, re.I)]
        if not ms:
            continue
        ch = ms[0][:4].upper()
        reg = [f for f in files if re.match(r"CH\d{2}-.*REGISTER.*\.docx$", f, re.I)]
        out[ch].append({
            "dir": d,
            "manuscript": max(ms, key=version),
            "register": max(reg, key=version) if reg else None,
            "others": [f for f in files if f.lower().endswith(".docx") and f not in ms + reg],
            "images": [f for f in files if f.lower().endswith(IMG_EXT)],
        })
    return out


def find(target):
    fs = folders()
    if re.fullmatch(r"(?i)ch\d{1,2}", target):
        ch = "CH" + target[2:].zfill(2)
        if not fs.get(ch):
            sys.exit(f"No folder in Reference/ holds a {ch}-*MANUSCRIPT*.docx")
        if len(fs[ch]) > 1:
            sys.exit(f"{ch} is in several folders ({', '.join(f['dir'] for f in fs[ch])}); pass the folder name")
        return ch, fs[ch][0]
    for ch, lst in fs.items():
        for f in lst:
            if f["dir"] == target.rstrip("/").split("/")[-1]:
                return ch, f
    sys.exit(f"Reference/{target}: no CHxx-*MANUSCRIPT*.docx found")


# ---------- register ----------
def parse_register(path):
    lines = open(path, encoding="utf-8").read().splitlines()
    masters, index, records = [], [], {}
    sec, cur = None, None
    for l in lines:
        if l.startswith("#"):
            h = l.lstrip("#").strip()
            sec = h.lower()
            cur = None
            m = re.match(r"(\d{2})\s+(.*)", h)
            if l.startswith("# ") and m:
                cur = {"n": int(m.group(1)), "title": m.group(2), "lines": [l]}
                records[cur["n"]] = cur
            continue
        if cur is not None:
            cur["lines"].append(l)
            m = re.match(r"Location\s+(\S+)", l)
            if m and "id" not in cur:
                cur["id"] = m.group(1)
            m = re.match(r"Filename\s+(\S+)", l)
            if m:
                cur["filename"] = m.group(1)
            continue
        if not l.startswith("|"):
            continue
        cells = [c.strip() for c in l.strip("|").split("|")]
        if sec == "master references" and cells[0] != "Reference name":
            masters.append({"name": cells[0], "identity": cells[1] if len(cells) > 1 else "", "image": None})
        elif sec == "image index" and cells[0] != "ID":
            index.append({"id": cells[0], "title": cells[1] if len(cells) > 1 else "",
                          "master": cells[2] if len(cells) > 2 else ""})
    by_id = {r.get("id"): r for r in records.values() if r.get("id")}
    out = []
    for i, e in enumerate(index):
        r = by_id.get(e["id"]) or records.get(i + 1) or {}
        out.append({**e, "filename": r.get("filename"), "brief": "\n".join(r.get("lines", []))})
    return masters, out


# ---------- manuscript pages ----------
SPEAKER = re.compile(r"Speaker:\s*([^|\]]+?)\s*(?:\||$)")
LOCREF = re.compile(r"Location (CH\d{2} [A-Z]\d{2}[A-Z0-9_-]*)\b(?: ([A-Z][^;\n\]—]*— [^;\n\].]+?)(?= geography|;|\.|$))?")
PANEL = re.compile(r"\[PanelizationHeading\] PANEL|\[GraphicPanelId\]|PANEL\s+\d{2}\b")
EQ_TAGS = ("[Equation]", "[WorkedStep]")


def page_index(src_dir, cast):
    idx, speakers_all, groups = {}, Counter(), {}   # groups: id -> Counter of names seen
    for f in sorted(os.listdir(src_dir)):
        if not re.fullmatch(r"P\d{3}\.txt", f):
            continue
        t = open(os.path.join(src_dir, f), encoding="utf-8").read()
        sp = sorted({re.split(r"\s+(?:to|in|from|\()\s*|,", s.strip())[0] for s in SPEAKER.findall(t) if s.strip()})
        speakers_all.update(sp)
        locs = []
        for m in LOCREF.finditer(t):
            g = m.group(1)
            if g not in locs:
                locs.append(g)
            name = (m.group(2) or "").strip()
            groups.setdefault(g, Counter())
            if name and len(name) < 90:
                groups[g][name] += 1
        idx[f[:4]] = {"panels": len(re.findall(r"\[PanelizationHeading\] PANEL", t)) or len(PANEL.findall(t)),
                      "speakers": sp, "locations": locs, "sha": hashlib.sha1(t.encode()).hexdigest()[:10]}
    groups = {g: (c.most_common(1)[0][0] if c else "") for g, c in groups.items()}
    names = sorted(set(cast) | set(speakers_all))
    for p, e in idx.items():
        t = open(os.path.join(src_dir, p + ".txt"), encoding="utf-8").read()
        e["characters"] = [n for n in names if re.search(rf"\b{re.escape(n)}\b", t)]
    return idx, speakers_all, groups


REL_CH = "=<>≤≥≠≈"
MATH_RUN = re.compile(r"[\d(√∛][\d\s\u00a0.()+\-−×÷*/^²³√∛%]*?(?:\s*[=<>≤≥≠≈]\s*[\d(√∛−\-][\d\s.()+\-−×÷*/^²³√∛%]*)+")
SKIP_LINE = re.compile(r"^\[(?:[A-Za-z]*Meta[A-Za-z]*|ProductionNote|PGLabel|PGContext|PaginationSourceLabel)\]")


def book_notation(seg):
    """Printed fractions are single numbers: 6 ÷ 2/3 means 6 ÷ (2/3); 1 2/9 is the mixed number 1 + 2/9."""
    seg = re.sub(r"(?<![\d/)])(\d+)[ \u00a0\u2009\u202f](\d+)/(\d+)(?![\d(])", r"(\1+\2/\3)", seg)
    return re.sub(r"(?<![\d/).])(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)(?![\d(.])", r"(\1/\2)", seg)


def maths_scan(src_dir):
    """Every arithmetic statement in reader text (tagged lines, prose and table cells) is evaluated exactly."""
    rows, n_ok, seen = [], 0, set()
    for f in sorted(os.listdir(src_dir)):
        if not re.fullmatch(r"P\d{3}\.txt", f):
            continue
        for l in open(os.path.join(src_dir, f), encoding="utf-8"):
            if SKIP_LINE.match(l):
                continue
            l = re.sub(r"(?<=\d),(?=\d{3}\b)", "", l)            # 1,000 -> 1000
            for m in MATH_RUN.finditer(l):
                seg = m.group(0).strip().rstrip(".,")
                head = l[:m.start()].rstrip()
                if head[-1:] in "−-" and not re.search(r"[\w)]\s*[−-]$", head):
                    seg, head = "−" + seg, head[:-1].rstrip()          # a leading minus sign
                before, after = head[-1:], l[m.end():].lstrip()[:1]
                if before in ":×÷+*/=<>" or after in (":", "…") or l[m.end():].lstrip().startswith("..."):
                    continue            # ratio chains, statements cut off by words, truncated decimals
                if not re.search(r"\d", seg) or (f, seg) in seen:
                    continue
                if re.match(r"\s*(remainder|rem\b|r\s*\d)", l[m.end():]):
                    continue            # "11 ÷ 4 = 2 remainder 3": division with remainder
                seen.add((f, seg))
                try:
                    ok, _ = mathcheck.evaluate(book_notation(seg))
                except Exception:
                    rows.append((f[:4], "SKIP", seg))
                    continue
                if ok:
                    n_ok += 1
                else:
                    rows.append((f[:4], "FAIL", seg))
    return n_ok, rows


# ---------- workspaces ----------
def bg_workspace(ch, records):
    if ch in LEGACY_PLATES:
        return LEGACY_PLATES[ch]
    n = int(ch[2:])
    return f"BagroundGenTask/ch{n:02d}/", f"BagroundGenTask/ch{n:02d}/out/plates/"


def scaffold_bg(ch, ws, records):
    """Only for a chapter without any plates: jobs.json + briefs; the bg-artist writes prompts."""
    full = os.path.join(TASKS, ws)
    for d in ("briefs", "prompts", "refs"):
        os.makedirs(os.path.join(full, d), exist_ok=True)
    for r in records:
        bp = os.path.join(full, "briefs", r["id"] + ".md")
        if not os.path.exists(bp):
            open(bp, "w", encoding="utf-8").write(r["brief"] + "\n")
    jp = os.path.join(full, "jobs.json")
    jobs = json.load(open(jp)) if os.path.exists(jp) else {
        "project": f"chandrush-{ch.lower()}-bg", "model": "gpt-image-2.5-sunburst",
        "quality": "high", "size": "1024x768", "max_calls": 3, "items": {}}
    for r in records:
        jobs["items"].setdefault(r["id"], {"prompt": f"prompts/{r['id']}.md", "refs": [],
                                           "note": f"master: {r['master']}"})
    json.dump(jobs, open(jp, "w"), indent=2, ensure_ascii=False)


def scaffold_panels(ch):
    full = os.path.join(TASKS, "FInalChangesTask", ch)
    os.makedirs(os.path.join(full, "prompts"), exist_ok=True)
    jp = os.path.join(full, "jobs.json")
    if not os.path.exists(jp):
        json.dump({"project": f"chandrush-{ch.lower()}-panels", "model": "gpt-image-2.5-sunburst",
                   "quality": "high", "size": "1536x1024", "max_calls": 3, "items": {}},
                  open(jp, "w"), indent=2)


# ---------- prep ----------
def cmd_prep(target, force=False, verbose=False):
    ch, f = find(target)
    out = os.path.join(TASKS, "PdfSheetsGenTask", ch)
    os.makedirs(out, exist_ok=True)
    mpath = os.path.join(TASKS, "PdfSheetsGenTask", ch, "chapter.json")
    old = json.load(open(mpath)) if os.path.exists(mpath) else {}
    refdir = f"Reference/{f['dir']}"
    ms = f"{refdir}/{f['manuscript']}"
    rg = f"{refdir}/{f['register']}" if f["register"] else None
    src_sha = {"manuscript": sha1(os.path.join(TASKS, ms)), "register": sha1(os.path.join(TASKS, rg)) if rg else None}
    same = old.get("sources", {}).get("sha") == src_sha and os.path.isdir(os.path.join(out, "src"))
    log = []

    old_idx = old.get("pages", {}).get("index_sha", {})
    if not same or force:
        echo = [run("dump", ms, f"PdfSheetsGenTask/{ch}/manuscript.txt").strip()]
        if rg:
            echo.append(run("dump", rg, f"PdfSheetsGenTask/{ch}/register.txt").strip())
        src = os.path.join(out, "src")
        if os.path.isdir(src):
            shutil.rmtree(src)      # stale pages of an older version must not survive
        echo.append(run("pages", ms, f"PdfSheetsGenTask/{ch}/src/").strip())
        if verbose:
            print("\n".join(echo))
        survey = run("survey", f"PdfSheetsGenTask/{ch}/src", "--verbose")      # survey.txt keeps every row
        open(os.path.join(out, "survey.txt"), "w", encoding="utf-8").write(survey)
    else:
        log.append("sources unchanged: kept manuscript.txt, register.txt and src/")

    # register
    masters, records = parse_register(os.path.join(out, "register.txt")) if rg else ([], [])
    old_masters = {m["name"]: m.get("image") for m in old.get("register", {}).get("masters", [])}
    for m in masters:
        m["image"] = old_masters.get(m["name"])
    ws, plates = bg_workspace(ch, records)
    have = sum(1 for r in records if os.path.exists(os.path.join(TASKS, plates, r["id"] + ".png")))
    for r in records:
        p = os.path.join(plates, r["id"] + ".png")
        r["plate"] = p if os.path.exists(os.path.join(TASKS, p)) else None
        r.pop("brief")
    if records and have == 0:
        _, recs_full = parse_register(os.path.join(out, "register.txt"))
        scaffold_bg(ch, ws, recs_full)
        log.append(f"no plates yet: scaffolded {ws} (jobs.json + {len(recs_full)} briefs) for the bg-artist")
    scaffold_panels(ch)

    # cast
    sheets = {}
    sd = os.path.join(TASKS, "..", SHEETS)
    if not os.path.isdir(sd):
        sd = os.path.join(TASKS, SHEETS)
    for s in sorted(os.listdir(sd)) if os.path.isdir(sd) else []:
        m = re.match(r"(.+?) CHARACTER SHEET", s, re.I)
        if m and s.lower().endswith(IMG_EXT):
            sheets[m.group(1).title()] = os.path.relpath(os.path.join(sd, s), TASKS)
    idx, speakers, groups = page_index(os.path.join(out, "src"), sheets)
    json.dump(idx, open(os.path.join(out, "index.json"), "w"), indent=1, ensure_ascii=False)
    pages_per = Counter(c for e in idx.values() for c in e["characters"])
    cast = {n: {"sheet": sheets.get(n), "pages": pages_per[n], "speaks": speakers.get(n, 0)}
            for n in sorted(set(sheets) | set(speakers))}
    old_loc = old.get("locations", {})
    locations = {g: {"name": groups.get(g, ""), "pages": [p for p, e in idx.items() if g in e["locations"]],
                     "records": old_loc.get(g, {}).get("records", [])} for g in sorted(groups)}
    for g, v in old_loc.items():          # groups the agent added (e.g. scene groups for a manuscript without ids)
        if g not in locations and same:
            locations[g] = v

    # maths pre-scan
    n_ok, rows = maths_scan(os.path.join(out, "src"))
    with open(os.path.join(out, "mathscan.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"# manuscript maths pre-scan: {n_ok} statements hold. FAIL = evaluates false: a manuscript error,"
                 f" a deliberate mistake shown to students, or a scan artefact (words cut the statement). Read each in src/Pxxx.txt. SKIP = not evaluable\n")
        for p, k, s in rows:
            fh.write(f"{p}\t{k}\t{s}\n")
    fails = [r for r in rows if r[1] == "FAIL"]

    # changes between versions
    changes = None
    if old_idx and not same:
        new_sha = {p: e["sha"] for p, e in idx.items()}
        built = {d for d in os.listdir(out) if re.fullmatch(r"P\d{3}", d) and
                 os.path.exists(os.path.join(out, d, "index.html"))}
        changed = sorted(p for p in new_sha if p in old_idx and old_idx[p] != new_sha[p])
        changes = {"from": old.get("sources", {}).get("manuscript"), "to": ms,
                   "changed": changed, "added": sorted(set(new_sha) - set(old_idx)),
                   "removed": sorted(set(old_idx) - set(new_sha)),
                   "built_and_changed": sorted(set(changed) & built), "at": datetime.now().isoformat(timespec="seconds")}
        with open(os.path.join(out, "CHANGES.md"), "a", encoding="utf-8") as fh:
            fh.write(f"\n## {changes['at']}: {changes['from']} → {ms}\n")
            for k in ("changed", "added", "removed", "built_and_changed"):
                fh.write(f"- {k}: {', '.join(changes[k]) or 'none'}\n")
        log.append(f"new version: {len(changed)} pages changed, {len(changes['built_and_changed'])} of them already"
                   f" built ({', '.join(changes['built_and_changed']) or 'none'}): see CHANGES.md")

    # pages.json header
    pj = os.path.join(out, "pages.json")
    if not os.path.exists(pj):
        n = int(ch[2:])
        json.dump({"chapter": ch, "book": "ChandRush: The Midnight Mela", "chapter_label": f"Chapter {n}",
                   "sources": {"manuscript": ms, "register": rg, "plates": plates}, "pages": []},
                  open(pj, "w"), indent=2, ensure_ascii=False)
        log.append("wrote pages.json header (no pages yet; the master plans them)")
    else:
        plan = json.load(open(pj))
        if plan.get("sources", {}).get("manuscript") not in (None, ms):
            log.append(f"pages.json still names {plan['sources']['manuscript']}: the master must update"
                       f" sources.manuscript to {ms} and re-run textcheck plan")

    kinds = Counter(l.split()[1] for l in open(os.path.join(out, "survey.txt"), encoding="utf-8")
                    if re.match(r"P\d{3}\s", l) and len(l.split()) > 1)
    unsheeted = [n for n, c in cast.items() if not c["sheet"] and c["speaks"]]
    resolved = old.get("resolved", {}) if same else {}
    status = {
        "sources": "ok",
        "register": "ok" if records else ("missing register docx" if not rg else "no records parsed"),
        "plates": "ok" if records and have == len(records) else f"{have}/{len(records)} approved → bg-artist",
        "masters": "ok" if masters and all(m["image"] for m in masters) else "agent: match each master to an image",
        "locations": "ok" if locations and all(v["records"] for v in locations.values()) else
                     "agent: map manuscript locations to register records",
        "characters": "ok" if not unsheeted else "no sheet for speaking: " + ", ".join(unsheeted),
        "maths": "ok" if not fails else f"agent: {len(fails)} FAIL lines in mathscan.txt",
        "agent_review": "todo",
    }
    for k, note in resolved.items():
        if k in status:
            status[k] = "ok"
    manifest = {
        "chapter": ch, "prepared": datetime.now().isoformat(timespec="seconds"),
        "reference_dir": refdir,
        "sources": {"manuscript": ms, "register": rg, "sha": src_sha,
                    "versions": {"manuscript": version(f["manuscript"]),
                                 "register": version(f["register"]) if f["register"] else None},
                    "images": [f"{refdir}/{i}" for i in f["images"]],
                    "other_docs": [f"{refdir}/{o}" for o in f["others"]]},
        "files": {k: f"PdfSheetsGenTask/{ch}/{v}" for k, v in
                  {"manuscript_txt": "manuscript.txt", "register_txt": "register.txt", "src": "src/",
                   "survey": "survey.txt", "index": "index.json", "mathscan": "mathscan.txt",
                   "pages": "pages.json", "review": "review.json", "artifacts": "artifacts.json"}.items()},
        "workspaces": {"backgrounds": ws, "plates": plates, "panels": f"FInalChangesTask/{ch}/",
                       "library": "FInalChangesTask/library/", "output": f"Output/{ch}/"},
        "pages": {"count": len(idx), "first": min(idx, default=None), "last": max(idx, default=None),
                  "kinds": dict(kinds), "index_sha": {p: e["sha"] for p, e in idx.items()}},
        "register": {"masters": masters, "records": records},
        "locations": locations,
        "cast": cast,
        "status": status,
        "resolved": resolved,
        "changes": changes or old.get("changes"),
        "notes": old.get("notes", []),
    }
    json.dump(manifest, open(mpath, "w"), indent=1, ensure_ascii=False)

    print(f"{chr(10) if verbose else ''}{ch} from {refdir}: {len(idx)} pages ({', '.join(f'{v} {k}' for k, v in kinds.items())}), "
          f"{len(records)} register records, plates {have}/{len(records)}")
    print(f"cast: " + ", ".join(f"{n}{'' if c['sheet'] else ' (NO SHEET)'}" for n, c in cast.items()))
    print(f"maths pre-scan: {n_ok} hold, {len(fails)} FAIL, {len(rows) - len(fails)} SKIP (mathscan.txt)")
    for l in log:
        print("· " + l)
    print(f"→ {rel(mpath)}")
    return manifest


# ---------- scan / check ----------
def state(ch, f):
    mp = os.path.join(TASKS, "PdfSheetsGenTask", ch, "chapter.json")
    if not os.path.exists(mp):
        return "new"
    m = json.load(open(mp))
    ms = f"Reference/{f['dir']}/{f['manuscript']}"
    rg = f"Reference/{f['dir']}/{f['register']}" if f["register"] else None
    sha = {"manuscript": sha1(os.path.join(TASKS, ms)), "register": sha1(os.path.join(TASKS, rg)) if rg else None}
    if m["sources"]["sha"] != sha or m["sources"]["manuscript"] != ms:
        return "stale"
    return "ready" if all(v == "ok" for v in m["status"].values()) else "needs-agent"


def cmd_scan(verbose=False):
    fs = folders()
    if not fs:
        print("Reference/ has no chapter folders")
    for ch in sorted(fs):
        for f in fs[ch]:
            print(f"{ch}  {state(ch, f):<11}  Reference/{f['dir']}/  {f['manuscript']}"
                  + (f"  {f['register'] or '(no register)'}  {len(f['images'])} images" if verbose else ""))


def cmd_check(ch, verbose=False):
    ch = "CH" + ch[2:].zfill(2)
    mp = os.path.join(TASKS, "PdfSheetsGenTask", ch, "chapter.json")
    if not os.path.exists(mp):
        sys.exit(f"{ch}: not set up. Run: python3 pipeline/setup_chapter.py prep {ch}")
    m = json.load(open(mp))
    _, f = find(ch)
    st = state(ch, f)
    print(f"{ch}: {st}  ({m['reference_dir']}, prepared {m['prepared']})")
    done = [k for k, v in m["status"].items() if v == "ok"]
    for k, v in m["status"].items():
        if verbose or v != "ok":
            print(f"  [{'x' if v == 'ok' else ' '}] {k:<13} {v}")
    if not verbose and done:
        print(f"  {len(done)}/{len(m['status'])} ok: {', '.join(done)}")
    sys.exit(0 if st == "ready" else 1)


def load(ch):
    ch = "CH" + ch[2:].zfill(2)
    mp = os.path.join(TASKS, "PdfSheetsGenTask", ch, "chapter.json")
    if not os.path.exists(mp):
        sys.exit(f"{ch}: not set up. Run: python3 pipeline/setup_chapter.py prep {ch}")
    return mp, json.load(open(mp))


def save(mp, m):
    json.dump(m, open(mp, "w"), indent=1, ensure_ascii=False)


def cmd_master(ch, name, image):
    mp, m = load(ch)
    if not os.path.exists(os.path.join(TASKS, image)):
        sys.exit(f"{image}: no such file (paths are relative to Tasks/)")
    hit = [x for x in m["register"]["masters"] if x["name"].lower() == name.lower()]
    if not hit:
        sys.exit("unknown master; the register names: " + "; ".join(x["name"] for x in m["register"]["masters"]))
    hit[0]["image"] = image
    if all(x["image"] for x in m["register"]["masters"]):
        m["status"]["masters"] = "ok"
    save(mp, m)
    print(f"{hit[0]['name']} → {image}")


def cmd_locate(ch, group, ids):
    mp, m = load(ch)
    known = {r["id"] for r in m["register"]["records"]}
    bad = [i for i in ids if i not in known]
    if bad:
        sys.exit(f"not register records: {', '.join(bad)}")
    if group not in m["locations"]:
        m["locations"][group] = {"name": "", "pages": [], "records": []}
    m["locations"][group]["records"] = ids
    if all(v["records"] for v in m["locations"].values()):
        m["status"]["locations"] = "ok"
    save(mp, m)
    print(f"{group} → {', '.join(ids)}")


def cmd_mark(ch, key, note):
    mp, m = load(ch)
    if key not in m["status"]:
        sys.exit(f"keys: {', '.join(m['status'])}")
    m["status"][key] = "ok"
    m.setdefault("resolved", {})[key] = note
    if key != "agent_review":
        m.setdefault("notes", []).append(f"{key}: {note}")
    save(mp, m)
    print(f"{key}: ok ({note})")


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        return
    verbose = False
    if a[0] in ("scan", "prep", "check"):
        verbose = "-v" in a or "--verbose" in a
        a = [x for x in a if x not in ("-v", "--verbose")]
    if a[0] == "scan":
        cmd_scan(verbose)
    elif a[0] == "prep" and len(a) > 1:
        cmd_prep(a[1], force="--force" in a, verbose=verbose)
    elif a[0] == "master" and len(a) == 4:
        cmd_master(*a[1:])
    elif a[0] == "locate" and len(a) > 3:
        cmd_locate(a[1], a[2], a[3:])
    elif a[0] == "mark" and len(a) == 4:
        cmd_mark(*a[1:])
    elif a[0] == "check" and len(a) > 1:
        cmd_check(a[1], verbose)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
