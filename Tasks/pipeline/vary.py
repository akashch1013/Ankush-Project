#!/usr/bin/env python3
"""vary.py: controlled randomness for page design. Every page feels new; the book system stays fixed.

  python3 pipeline/vary.py CH01 P006 [P007 ...] [--write]     one variation card per page
  python3 pipeline/vary.py CH01 P006-P012 --write              (range ok)

For each page it reads pages.json (kind, panel count, location) and the cards of the 2 pages before and after,
then draws one option per design axis with a seeded RNG (same page -> same card, so reruns are stable), never
repeating a neighbour's choice on the same axis. --write stores it as pages.json -> page["art"]["variation"].

The card is the art-director's/page-builder's STARTING POINT, not a cage: keep it unless the page's content clearly
calls for something else, and then say why in the brief. FIXED for every page (never varied): running head,
moonclock folio, V09 type sizes, balloon/caption objects (pipeline/balloon.py), 36 pt margins, the location's palette
and materials, exact maths.
"""
import json
import os
import random
import re
import sys

PIPE = os.path.dirname(os.path.abspath(__file__))
TASKS = os.path.dirname(PIPE)

STORY_GRIDS = {
    1: ["full-bleed splash inside the frame", "arch/gate-framed splash (opener-style)", "splash + one small inset close-up (zoom crop of the same art)"],
    2: ["two stacked wide bands", "two tall side-by-side panels", "big panel + inset panel breaking its corner", "wide band over a tall-narrow + wide pair"],
    3: ["wide letterbox over two", "two over a wide payoff", "tall left + two stacked right", "three tall vertical strips", "L-shape: tall left, wide top-right, small bottom-right"],
    4: ["wide top + three below", "2x2 with unequal columns (60/40)", "three across a tall right column (shaft-style)", "Z-path: wide, two, wide", "tall left column + three stacked right"],
    5: ["wide top + two + two", "two + wide middle + two", "tall hero left + four right (2x2)", "staircase: panels step down diagonally"],
    6: ["3 tiers of two, middle tier offset", "wide top + 2x2 + wide bottom strip", "tall hero right + five left"],
}
AXES_STORY = {
    "panel_accent": ["none: clean rectangles", "one panel with an arched (jharokha) top", "one bevelled corner on the hero panel",
                     "one circular inset close-up", "one slanted gutter between two panels", "a character or prop breaks one panel border"],
    "border_build": ["top arm from the entry corner + a finish piece bottom-right", "entry corner block + finish corner cap (two pieces only)",
                     "side rail on the outer edge with one hanging object", "full hairline frame + one heavy entry block",
                     "broken frame: the border stops where the art pushes through"],
    "entry_corner": ["top-left", "top-right", "top-centre"],
    "field": ["midnight navy, subtle radial lift", "royal-blue lacquer, vertical grain gradient", "aubergine dusk", "peacock-teal night",
              "slate blue with warm lamp bloom at one corner"],
    "hero_slot": ["the largest panel opens the page", "the largest panel is the payoff (last)", "the hero sits centre, others orbit it"],
    "gutter": ["9 pt", "10 pt", "12 pt"],
    "light_link": ["lamp glow spills across one gutter", "moonlight rim on the border on the moon side", "one warm light source repeated in the border"],
}
AXES_TEACH = {
    "hero_slot": ["maths picture as a full-width band on top", "maths picture as a tall left column", "maths picture centred, text wraps both sides",
                  "maths picture bottom-right as the payoff"],
    "work_object": ["ledger sheet with ruled columns", "field-notebook page", "etched brass plate", "blueprint card with brass corners"],
    "companion_entry": ["on a ledge from the scene", "framed in a jharokha window", "popping out over a panel edge", "snapped into a corner bracket",
                        "silent (no aside on this page)"],
    "border_build": ["band from the location's material on two sides", "corner caps + one rail", "full frame with one ornament at the entry",
                     "top band only, heavy, with the moon medallion"],
    "field": ["warm cream #F7F1E3", "pale moonlit stone", "parchment with a faint blueprint grid"],
    "answer_object": ["sealed flap", "turned card", "brass shutter", "folded corner"],
}


def page_range(spec):
    out = []
    for part in spec.split(","):
        part = part.strip().upper()
        if "-" in part and part.count("P") == 2:
            a, b = part.split("-")
            out += [f"P{n:03d}" for n in range(int(a[1:]), int(b[1:]) + 1)]
        elif part:
            out.append(part)
    return out


def kind_of(pg):
    """story | mixed | teaching, from the pattern id (S/M/T in design/patterns.md) or the content."""
    m = re.search(r"(?:^|grid\s+|\b)([SMT])\d\b", str(pg.get("pattern") or ""))
    if m:
        return {"S": "story", "M": "mixed", "T": "teaching"}[m.group(1)]
    has_t, n = bool(pg.get("teaching")), len(pg.get("panels") or [])
    return "teaching" if has_t and n <= 1 else "mixed" if has_t else "story"


def card(ch, pid, pg, neighbours):
    rng = random.Random(f"{ch}-{pid}-chandrush")
    k = kind_of(pg)
    n = max(1, min(6, len(pg.get("panels") or []) or 1))
    if k == "teaching":
        axes = dict(AXES_TEACH)
    elif k == "mixed":   # story panels + a teaching unit: a grid, the maths hero and its objects, the story's border
        axes = {"grid": STORY_GRIDS[n], **{a: AXES_TEACH[a] for a in ("hero_slot", "work_object", "companion_entry", "answer_object")},
                **{a: AXES_STORY[a] for a in ("border_build", "field", "gutter")}}
    else:
        axes = {"grid": STORY_GRIDS[n], **AXES_STORY}
    out = {"kind": k}
    for axis, opts in axes.items():
        used = {nb.get(axis) for nb in neighbours if nb}
        pool = [o for o in opts if o not in used] or opts
        out[axis] = rng.choice(pool)
    out["fixed"] = "running head, moonclock folio, V09 type, balloon.py balloons, 36pt margins, location palette+materials"
    return out


def main():
    a = sys.argv[1:]
    if len(a) < 2 or a[0] in ("-h", "--help"):
        print(__doc__)
        return
    ch, write = a[0].upper(), "--write" in a
    want = []
    for x in a[1:]:
        if x != "--write":
            want += page_range(x)
    pj = os.path.join(TASKS, "PdfSheetsGenTask", ch, "pages.json")
    data = json.load(open(pj, encoding="utf-8"))
    pages = data["pages"] if isinstance(data, dict) else data
    by = {p.get("page") or p.get("id"): p for p in pages}
    order = sorted(by)
    for pid in want:
        pg = by.get(pid)
        if pg is None:
            print(f"{pid}: not in pages.json (plan it first)")
            continue
        i = order.index(pid)
        nb = [((by[order[j]].get("art") or {}).get("variation") or {}) for j in range(max(0, i - 2), min(len(order), i + 3)) if j != i]
        c = card(ch, pid, pg, nb)
        print(pid, json.dumps(c, ensure_ascii=False, indent=1))
        if write:
            pg.setdefault("art", {})
            if isinstance(pg["art"], dict):
                pg["art"]["variation"] = c
    if write:
        json.dump(data, open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"written to {pj}")


if __name__ == "__main__":
    main()
