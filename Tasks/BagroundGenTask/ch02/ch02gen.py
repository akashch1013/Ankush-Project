#!/usr/bin/env python3
"""ch02gen.py: ChandRush CH02 location plates (Register V04), reusing locgen.py's API, clarity and typography.
Run from the BagroundGenTask folder:  python3 ch02/ch02gen.py <cmd>

  status                         every record: wave, status, calls, refs
  brief ID                       register text for the record (ch02/briefs/ID.md) + its refs
  lint ID...                     prompt checks (blocks spend)
  gen ID... [--dry-run]          immediate /images/edits call(s) (single re-runs only)
  fix ID "change" [--batch NAME] targeted edit of the current plate (immediate, or queued into a batch)
  batch submit NAME ID...        build + submit one Batch API job (50% off) for these records' gen
  batch wait NAME                poll every 60 s until done, then fetch plates into out/plates/
  qc ID pass|fail [--note ..]    record the verdict; an approved plate may be attached by dependents
  compose ID                     title band + callouts from callouts/ID.json -> out/final/<filename>
  zoom ID x0,y0,x1,y1 [--scale 2] crop (fractions) to out/zoom/ID.png for inspection

Cap: 3 API calls per record (gen + fixes), counted in state.json; --force only with the user's approval.
"""
import argparse, base64, json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import locgen as L  # noqa: E402

RECS = json.load(open(os.path.join(HERE, "records.json")))
STATE_P = os.path.join(HERE, "state.json")
CAP = 3


def q(*a):
    return os.path.join(HERE, *a)


def state():
    return json.load(open(STATE_P))


def save_state(st):
    tmp = STATE_P + ".tmp"
    json.dump(st, open(tmp, "w"), indent=1)
    os.replace(tmp, STATE_P)


def update_state(fn):
    """Read-modify-write with a lock file, since several agents share state.json."""
    lock = STATE_P + ".lock"
    for _ in range(600):
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL)
            os.close(fd)
            break
        except FileExistsError:
            time.sleep(0.1)
    try:
        st = state()
        fn(st)
        save_state(st)
    finally:
        os.remove(lock)


def ref_path(ref):
    kind, name = ref.split(":")
    return q("out", "plates", f"{name}.png") if kind == "plate" else q(RECS["masters"][name])


def sections(rid):
    text = open(q("prompts", f"{rid}.md")).read()
    body = text.split("## PROMPT", 1)[1].split("## CHECKS", 1)[0].strip()
    checks = text.split("## CHECKS", 1)[1].split("## CALLOUT PLAN", 1)[0] if "## CHECKS" in text else ""
    return body, checks


def lint(rid):
    errs = []
    r = RECS["records"][rid]
    if not os.path.exists(q("prompts", f"{rid}.md")):
        return ["no prompt file"]
    body, checks = sections(rid)
    for t in r["title"] + r["callouts"]:
        if t in body:
            errs.append(f"title/callout text '{t}' appears in PROMPT")
    n = len(r["refs"])
    for i in range(1, n + 1):
        if f"Image {i}" not in body:
            errs.append(f"Image {i} not described")
    if f"Image {n + 1}" in body:
        errs.append(f"mentions Image {n + 1} but only {n} attached")
    if "4:3" not in body:
        errs.append("no 4:3")
    if "Physical inscriptions" not in body:
        errs.append("no 'Physical inscriptions' line")
    if checks.count("\n- ") < 5:
        errs.append("CHECKS has fewer than 5 items")
    if r["mode"] == "state-edit" and "Change only" not in body:
        errs.append("state-edit prompt lacks 'Change only'")
    if len(body) > 24000:
        errs.append("prompt too long")
    st = state()
    for ref in r["refs"]:
        if ref.startswith("plate:") and st[ref[6:]]["status"] != "approved":
            errs.append(f"{ref} not approved yet")
    return errs


def full_prompt(rid):
    body, _ = sections(rid)
    style = open(L.p("spec", "style.txt")).read().strip()
    rules = open(L.p("spec", "rules.txt")).read().strip()
    return body + "\n\n" + style + "\n\n" + rules


def job(rid, instruction=None):
    r = RECS["records"][rid]
    if instruction:
        prompt = L.FIX.format(rid=rid, view=r["title"][1], instruction=instruction).replace("Chapter 01", "Chapter 02") \
            + "\n\n" + open(L.p("spec", "rules.txt")).read().strip()
        imgs = [q("out", "plates", f"{rid}.png")]
    else:
        prompt, imgs = full_prompt(rid), [ref_path(x) for x in r["refs"]]
    body = {"model": RECS["model"], "prompt": prompt, "size": RECS["size"], "quality": r["quality"], "n": 1,
            "output_format": "png", "images": [{"image_url": L.data_url(i)} for i in imgs]}
    return body


def guard(rid, force):
    if force:
        return
    c = state()[rid]["calls"]
    if c >= CAP:
        sys.exit(f"{rid}: {c} calls used, cap {CAP}. Ask the user before more (then --force).")


def store(rid, b64, usage, kind, via, secs=0):
    out = q("out", "plates", f"{rid}.png")
    os.makedirs(q("out", "plates", "history"), exist_ok=True)
    if os.path.exists(out):
        os.rename(out, q("out", "plates", "history", f"{rid}-{int(time.time())}.png"))
    open(out, "wb").write(base64.b64decode(b64))
    usd = L.estimate(usage, "batch" if via.startswith("batch") else "sync")

    def f(st):
        st[rid]["calls"] += 1
        st[rid]["status"] = "review"
        st[rid].setdefault("log", []).append(f"{L.now()} {kind} via {via} ${usd:.3f}")
    update_state(f)
    with open(q("out", "usage.tsv"), "a") as fh:
        fh.write(f"{L.now()}\t{rid}\t{kind}\t{via}\t{json.dumps(usage)}\t{usd}\t{secs}\n")
    return out, usd


def cmd_gen(a, instruction=None):
    for rid in a.ids:
        if not instruction:
            e = lint(rid)
            if e:
                sys.exit(f"{rid} lint: " + "; ".join(e))
        guard(rid, a.force)
    if a.dry_run:
        for rid in a.ids:
            open(q("out", f"{rid}-prompt.txt"), "w").write(job(rid)["prompt"])
            print(rid, "->", q("out", f"{rid}-prompt.txt"))
        return
    key = L.load_key()

    def go(rid):
        t0 = time.time()
        try:
            res = L.api(key, "POST", "/images/edits", job(rid, instruction))
        except RuntimeError as e:
            return f"{rid} FAILED {e}"
        b64 = (res.get("data") or [{}])[0].get("b64_json")
        if not b64:
            return f"{rid} FAILED no image"
        out, usd = store(rid, b64, res.get("usage", {}), "fix" if instruction else "gen", "sync", round(time.time() - t0))
        return f"{rid} ok {out} ${usd:.3f}"
    with ThreadPoolExecutor(len(a.ids)) as ex:
        for m in ex.map(go, a.ids):
            print(m)


def bdir(name):
    return q("out", "batches", name)


def cmd_batch(a):
    if a.action == "submit":
        bd = bdir(a.name)
        os.makedirs(bd, exist_ok=False)
        lines, man = [], []
        for item in a.ids:
            rid, _, instr = item.partition("=")
            if not instr:
                e = lint(rid)
                if e:
                    sys.exit(f"{rid} lint: " + "; ".join(e))
            guard(rid, a.force)
            body = job(rid, instr or None)
            cid = f"{rid}~{'fix' if instr else 'gen'}~{state()[rid]['calls'] + 1}"
            lines.append(json.dumps({"custom_id": cid, "method": "POST", "url": "/v1/images/edits", "body": body}))
            man.append(cid)
            open(os.path.join(bd, f"{rid}-prompt.txt"), "w").write(body["prompt"])
        open(os.path.join(bd, "requests.jsonl"), "w").write("\n".join(lines) + "\n")
        key = L.load_key()
        up = L.api(key, "POST", "/files", {"purpose": "batch"},
                   files=[("file", os.path.join(bd, "requests.jsonl"), "application/jsonl")])
        b = L.api(key, "POST", "/batches", {"input_file_id": up["id"], "endpoint": "/v1/images/edits",
                                            "completion_window": "24h",
                                            "metadata": {"project": "chandrush-ch02", "batch": a.name}})
        json.dump({"batch": b, "jobs": man}, open(os.path.join(bd, "batch.json"), "w"), indent=1)

        def f(st):
            for cid in man:
                st[cid.split("~")[0]]["status"] = "queued"
        update_state(f)
        print(f"submitted {a.name}: {b['id']} {b['status']} jobs={man}")
        return
    if a.action == "wait":
        bd = bdir(a.name)
        info = json.load(open(os.path.join(bd, "batch.json")))
        key = L.load_key()
        while True:
            b = L.api(key, "GET", f"/batches/{info['batch']['id']}")
            c = b.get("request_counts") or {}
            print(f"{L.now()} {a.name}: {b['status']} {c.get('completed', 0)}/{c.get('total', 0)} failed {c.get('failed', 0)}", flush=True)
            if b["status"] in L.TERMINAL:
                break
            time.sleep(60)
        info["batch"] = b
        json.dump(info, open(os.path.join(bd, "batch.json"), "w"), indent=1)
        seen = set()
        for fid in (b.get("output_file_id"), b.get("error_file_id")):
            if not fid:
                continue
            for line in L.api(key, "GET", f"/files/{fid}/content", raw=True).decode().splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                cid = row["custom_id"]
                rid, kind = cid.split("~")[:2]
                seen.add(cid)
                resp = row.get("response") or {}
                body = resp.get("body") or {}
                b64 = (body.get("data") or [{}])[0].get("b64_json") if resp.get("status_code") == 200 else None
                if b64:
                    out, usd = store(rid, b64, body.get("usage") or {}, kind, "batch:" + a.name)
                    print(f"OK   {cid} -> {out} ${usd:.3f}")
                else:
                    print(f"FAIL {cid}: {json.dumps(row.get('error') or body.get('error') or resp)[:300]}")

                    def f(st, rid=rid):
                        st[rid]["status"] = "todo"
                    update_state(f)
        for cid in info["jobs"]:
            if cid not in seen:
                print("MISS", cid)
        return
    sys.exit("batch submit|wait")


def cmd_qc(a):
    def f(st):
        st[a.id]["status"] = "approved" if a.verdict == "pass" else "failed"
        st[a.id].setdefault("log", []).append(f"{L.now()} qc {a.verdict} {a.note or ''}")
    update_state(f)
    print(a.id, a.verdict)


def cmd_status(a):
    st = state()
    for rid, r in sorted(RECS["records"].items(), key=lambda kv: (kv[1]["wave"], kv[0])):
        s = st[rid]
        print(f"w{r['wave']} {rid:6} {s['status']:9} calls {s['calls']}  {r['quality']:6} {r['mode']:10} {', '.join(r['refs'])}")


def cmd_brief(a):
    r = RECS["records"][a.id]
    print(open(q("briefs", f"{a.id}.md")).read())
    print("\nATTACH (in order):")
    for i, ref in enumerate(r["refs"], 1):
        print(f"  Image {i}: {ref} -> {os.path.relpath(ref_path(ref), os.getcwd())}")
    print(f"mode {r['mode']}  quality {r['quality']}  wave {r['wave']}")
    print("TITLE (compose only):", r["title"]); print("CALLOUTS (compose only):", r["callouts"])


def cmd_zoom(a):
    from PIL import Image
    im = Image.open(q("out", "plates", f"{a.id}.png"))
    w, h = im.size
    x0, y0, x1, y1 = [float(v) for v in a.box.split(",")]
    c = im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
    c = c.resize((int(c.width * a.scale), int(c.height * a.scale)))
    os.makedirs(q("out", "zoom"), exist_ok=True)
    out = q("out", "zoom", f"{a.id}.png")
    c.save(out)
    print(out)


def cmd_compose(a):
    from PIL import Image, ImageDraw
    r = RECS["records"][a.id]
    plate = L.clarity(Image.open(q("out", "plates", f"{a.id}.png")).convert("RGB"))
    spec = json.load(open(q("callouts", f"{a.id}.json")))
    assert sorted(c["text"] for c in spec["callouts"]) == sorted(r["callouts"]), "callout texts differ from register"
    w, h = plate.size
    s = w / 1024
    dr = ImageDraw.Draw(plate)
    f = L.font("callout", round(14 * s))
    padx, pady = round(7 * s), round(4 * s)
    boxes = []
    for c in spec["callouts"]:
        tw = dr.textlength(c["text"], font=f)
        asc, desc = f.getmetrics()
        bw, bh = tw + 2 * padx, asc + desc + 2 * pady
        cx = min(max(c["box"][0] * w, 6 + bw / 2), w - 6 - bw / 2)
        cy = min(max(c["box"][1] * h, 6 + bh / 2), h - 6 - bh / 2)
        box = (cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2)
        boxes.append((c, box))
        for tx, ty in c["targets"]:
            tx, ty = tx * w, ty * h
            ex, ey = min(max(tx, box[0]), box[2]), min(max(ty, box[1]), box[3])
            dr.line([(ex, ey), (tx, ty)], fill=L.IVORY, width=4)
            dr.line([(ex, ey), (tx, ty)], fill=L.INDIGO, width=2)
            dr.ellipse([tx - 4, ty - 4, tx + 4, ty + 4], fill=L.IVORY)
            dr.ellipse([tx - 3, ty - 3, tx + 3, ty + 3], fill=L.INDIGO)
    for c, box in boxes:
        dr.rounded_rectangle(box, radius=3, fill=L.IVORY, outline=L.INDIGO, width=1)
        dr.text((box[0] + padx, box[1] + pady), c["text"], font=f, fill=L.INDIGO)
    band = round(84 * s)
    canvas = Image.new("RGB", (w, h + band), L.IVORY)
    canvas.paste(plate, (0, band))
    cd = ImageDraw.Draw(canvas)
    sizes, tracking = (round(17 * s), round(25 * s)), (round(2.2 * s), round(1.2 * s))
    fonts = [L.font("title", sizes[0]), L.font("title", sizes[1])]
    for i in (0, 1):
        while L.tracked_width(cd, r["title"][i], fonts[i], tracking[i]) > w - 48 * s and fonts[i].size > 10:
            fonts[i] = L.font("title", fonts[i].size - 1)
        tw = L.tracked_width(cd, r["title"][i], fonts[i], tracking[i])
        L.draw_tracked(cd, ((w - tw) / 2, [14, 40][i] * s), r["title"][i], fonts[i], L.INDIGO, tracking[i])
    cd.rectangle([0, band - 2, w, band], fill=L.BRASS)
    os.makedirs(q("out", "final"), exist_ok=True)
    out = q("out", "final", r["filename"])
    canvas.save(out)
    print(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen"); g.add_argument("ids", nargs="+"); g.add_argument("--dry-run", action="store_true"); g.add_argument("--force", action="store_true")
    fx = sub.add_parser("fix"); fx.add_argument("id"); fx.add_argument("instruction"); fx.add_argument("--force", action="store_true")
    b = sub.add_parser("batch"); b.add_argument("action"); b.add_argument("name"); b.add_argument("ids", nargs="*", help="ID or ID=fix instruction"); b.add_argument("--force", action="store_true")
    qc = sub.add_parser("qc"); qc.add_argument("id"); qc.add_argument("verdict", choices=["pass", "fail"]); qc.add_argument("--note")
    sub.add_parser("status")
    br = sub.add_parser("brief"); br.add_argument("id")
    li = sub.add_parser("lint"); li.add_argument("ids", nargs="+")
    z = sub.add_parser("zoom"); z.add_argument("id"); z.add_argument("box"); z.add_argument("--scale", type=float, default=2)
    c = sub.add_parser("compose"); c.add_argument("id")
    a = ap.parse_args()
    if a.cmd == "gen":
        cmd_gen(a)
    elif a.cmd == "fix":
        a.ids, a.dry_run = [a.id], False
        cmd_gen(a, a.instruction)
    elif a.cmd == "batch":
        cmd_batch(a)
    elif a.cmd == "qc":
        cmd_qc(a)
    elif a.cmd == "status":
        cmd_status(a)
    elif a.cmd == "brief":
        cmd_brief(a)
    elif a.cmd == "lint":
        for rid in a.ids:
            e = lint(rid)
            print(rid, "ok" if not e else "ERR " + "; ".join(e))
    elif a.cmd == "zoom":
        cmd_zoom(a)
    else:
        cmd_compose(a)


if __name__ == "__main__":
    main()
