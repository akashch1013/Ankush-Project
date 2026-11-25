#!/usr/bin/env python3
"""promptlint.py: free pre-flight check of panel prompts BEFORE they cost a call (stage 2).

  python3 pipeline/promptlint.py --ws FInalChangesTask/CH01 [ID ...]     (default: every todo/regen item)

`imggen.py batch build` runs the same checks on every gen item and refuses an item with a FAIL.
Each image has 3 calls in total, so the first prompt has to be right. The lint catches the mistakes that cost
calls in CH01:
  FAIL  plate is not Image 1 / a composed or archived plate is attached / an old character path (../Charactors/)
  FAIL  a named cast member appears in the prompt with no sheet attached, or a sheet is attached with no "Image n" line
  FAIL  the prompt doesn't declare every attached image as "Image n", or declares more images than are attached
  FAIL  no "no lettering" clause, or no reserved empty areas for the balloons
  FAIL  fewer than 6 CHECKS
  WARN  Tara is in the panel and the prompt doesn't say calm/wise; LEFT/RIGHT hands without screen-left/right;
        2+ characters with no height chart; no "exactly" for countable props; no geometry lock on the plate
"""
import json
import os
import re
import sys

PIPE = os.path.dirname(os.path.abspath(__file__))
TASKS = os.path.dirname(PIPE)
CAST = json.load(open(os.path.join(PIPE, "cast.json"), encoding="utf-8"))
SHEET2NAME = {v["sheet"]: k for k, v in CAST["characters"].items()}     # by file name (folder checked separately)
HEIGHTS = set(CAST["heights"].values())
# words that name a cast member in a prompt (first word of the cast key, plus helpers)
NAME_WORDS = {"Ahana": "Ahana", "Vihaan": "Vihaan", "Navya": "Navya", "Tara": "Tara", "Tez": "Tez", "Kabir": "Kabir",
              "Ira": "Ira", "Pip": "Pip", "Veer": "Veer"}


def split(text):
    m = re.search(r"##\s*PROMPT\s*\n(.*?)(?=\n##\s|\Z)", text, re.S)
    c = re.search(r"##\s*CHECKS\s*\n(.*?)(?=\n##\s|\Z)", text, re.S)
    return (m.group(1) if m else ""), (c.group(1) if c else "")


def lint_item(ws_dir, rid, item):
    fails, warns = [], []
    refs = item.get("refs", [])
    spot = rid.startswith(("V-", "X-", "C-"))
    try:
        text = open(os.path.join(ws_dir, item.get("prompt", f"prompts/{rid}.md")), encoding="utf-8").read()
    except OSError:
        return [f"no prompt file"], []
    prompt, checks = split(text)
    files = [r for r in refs if not r.startswith("item:")]
    if not spot:
        if not files or "plates/" not in files[0]:
            fails.append("Image 1 must be the raw background plate (…/out/plates/<ID>.png)")
    for r in files:
        if "out/final" in r or "archive/" in r:
            fails.append(f"composed/archived plate attached: {r} (callouts and titles leak)")
        if "Charactors/" in r:
            fails.append(f"old character path {r}: use '{CAST['folder']}/…' (pipeline/cast.py refs)")
        if not os.path.exists(os.path.join(TASKS, r)):
            fails.append(f"missing reference file {r}")
    attached = {SHEET2NAME[os.path.basename(r)] for r in files if os.path.basename(r) in SHEET2NAME}
    has_heights = any(os.path.basename(r) in HEIGHTS for r in files)
    # cast named in the prompt's action section vs sheets attached
    action = prompt.split("Characters and action", 1)[-1] if "Characters and action" in prompt else prompt
    named = {k for w, k in NAME_WORDS.items() if re.search(rf"\b{w}\b", action)}
    attached_first = {a.split()[0] for a in attached}
    for n in sorted(named - attached_first):
        if re.search(rf"\b{n}\b[^.\n]{{0,60}}(off[- ]panel|out of (frame|shot)|not visible|not shown)", action, re.I):
            continue
        fails.append(f"{n} is in the action but their sheet is not attached ({CAST['folder']}/…)")
    for a in sorted(attached_first - named):
        warns.append(f"{a}'s sheet is attached but {a} is not in 'Characters and action'")
    # every attached image declared, none extra
    n_imgs = len(refs)
    declared = {int(x) for x in re.findall(r"Image\s+(\d+)\s*:", prompt)}
    want = set(range(1, n_imgs + 1))
    if want - declared:
        fails.append(f"attached images not declared in the prompt: Image {sorted(want - declared)}")
    if declared - want:
        fails.append(f"prompt declares Image {sorted(declared - want)} but only {n_imgs} are attached")
    low = prompt.lower()
    if not re.search(r"no letter|no lettering|no text|any speech bubble|no words", low):
        fails.append("no 'no lettering' clause (bubbles/captions/labels must never be painted)")
    if not spot and not re.search(r"reserved|reserve|calm (empty )?area|kept? (calm|empty)", low):
        fails.append("no reserved calm areas for the balloons/captions (they sit ON the art)")
    n_checks = len(re.findall(r"^\s*(?:\d+[.)]|[-*])\s+\S", checks, re.M))
    if n_checks < 6:
        fails.append(f"only {n_checks} CHECKS (need 6–12: identity, count, hands, sides, props, reserves, lettering, continuity)")
    if "Tara" in named and not re.search(r"\bcalm|\bwise|composed|serene", low):
        warns.append("Tara is in the panel: state her calm, wise expression (never animated)")
    if re.search(r"\b(LEFT|RIGHT|left|right) (hand|paw|arm)\b", prompt) and "screen-" not in low:
        warns.append("hands named LEFT/RIGHT without 'screen-left/right': say which side of the picture")
    if len(named) >= 2 and not has_heights:
        warns.append("2+ characters but no height chart attached (pipeline/cast.py refs adds it)")
    if not spot and not re.search(r"keep (its|the) (architecture|geometry)|exact shape|do not (move|alter|add)|only geometry|unchanged", low):
        warns.append("no geometry lock on the plate ('keep every object's exact shape, position and orientation')")
    if re.search(r"\b(two|three|four|five|six|seven|eight|nine|ten|\d+)\s+\w+s\b", action) and "exactly" not in low:
        warns.append("countable props without 'exactly N (word)'")
    return fails, warns


def lint_ws(ws_dir, ids=None, quiet=False):
    jobs = json.load(open(os.path.join(ws_dir, "jobs.json"), encoding="utf-8"))
    st_p = os.path.join(ws_dir, "state.json")
    st = json.load(open(st_p, encoding="utf-8")) if os.path.exists(st_p) else {"items": {}}
    if not ids:
        ids = [r for r in jobs["items"] if st["items"].get(r, {}).get("status", "todo") in ("todo", "regen")]
    bad = 0
    for rid in ids:
        f, w = lint_item(ws_dir, rid, jobs["items"][rid])
        if f:
            bad += 1
        if not quiet or f:
            print(f"{'FAIL' if f else 'OK  '} {rid}")
        for x in f:
            print(f"     FAIL {x}")
        for x in w:
            print(f"     warn {x}")
    return bad


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or "--ws" not in a:
        print(__doc__)
        sys.exit(0)
    ws = a[a.index("--ws") + 1]
    ws = ws if os.path.isabs(ws) else os.path.join(TASKS, ws) if not os.path.exists(ws) else ws
    ids = [x for x in a if x not in ("--ws", a[a.index("--ws") + 1])]
    sys.exit(1 if lint_ws(ws, ids) else 0)
