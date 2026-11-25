#!/usr/bin/env python3
"""cast.py: the character references to attach to an image call, in the right order (paths relative to Tasks/).

  python3 pipeline/cast.py list                         every character, its sheet and identity line
  python3 pipeline/cast.py refs PLATE Ahana Tez Tara    -> JSON list for jobs.json "refs":
                                                         [plate, one sheet per character (in the order given),
                                                          the matching height chart LAST when 2+ characters]
  python3 pipeline/cast.py refs PLATE Ahana --prev item:P002-1   (append a previous approved panel for continuity)
  python3 pipeline/cast.py lines Ahana Tez              the 'Image n: character sheet of …' lines for the prompt

Source: Tasks/CHANDRUSH CHARACTERS/ (read-only). Map: pipeline/cast.json.
"""
import json, os, sys
PIPE = os.path.dirname(os.path.abspath(__file__))
TASKS = os.path.dirname(PIPE)
C = json.load(open(os.path.join(PIPE, "cast.json"), encoding="utf-8"))
F = C["folder"]


def find(name):
    for k, v in C["characters"].items():
        if k.lower() == name.lower() or k.lower().startswith(name.lower()):
            return k, v
    sys.exit(f"unknown character '{name}'. Known: " + ", ".join(C["characters"]))


def refs(plate, names, prev=None, heights=True):
    out = [plate] if plate else []
    groups = []
    for n in names:
        k, v = find(n)
        p = f"{F}/{v['sheet']}"
        if p not in out:
            out.append(p)
        groups.append(v["heights"])
    if heights and len(names) >= 2:
        g = max(set(groups), key=groups.count)
        out.append(f"{F}/{C['heights'][g]}")
    if prev:
        out.append(prev)
    for p in out:
        if not p.startswith("item:") and not os.path.exists(os.path.join(TASKS, p)):
            sys.exit(f"missing reference file: {p}")
    return out


def lines(names, start=2, heights=True):
    rows, i = [], start
    for n in names:
        k, v = find(n)
        rows.append(f"- Image {i}: character sheet of {k}. Use ONLY for identity: {v['id']}. Ignore the sheet's layout, "
                    f"turnaround poses, background, swatches, icons and every piece of text.")
        i += 1
    if heights and len(names) >= 2:
        rows.append(f"- Image {i}: height chart. Use ONLY for the characters' relative heights and proportions; "
                    f"ignore its line-up, white background and labels.")
    return "\n".join(rows)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
    elif a[0] == "list":
        for k, v in C["characters"].items():
            print(f"{k:24} {F}/{v['sheet']}\n{'':24} {v['id']}")
    elif a[0] == "refs":
        prev = a[a.index("--prev") + 1] if "--prev" in a else None
        names = [x for x in a[2:] if x not in ("--prev", prev)]
        print(json.dumps(refs(a[1], names, prev), ensure_ascii=False, indent=1))
    elif a[0] == "lines":
        print(lines(a[1:]))
