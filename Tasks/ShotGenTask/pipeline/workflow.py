"""Image workflow: queue, hand-off to an image tool, ingest, review, approval.

Works the same whether the image comes from Codex's built-in image tool, the
Codex image CLI / OpenAI API, or a person using the ChatGPT web UI:
every image lands in art/_inbox and is filed by `ingest`.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

from . import jsonio
from . import state as st
from .art import cover_fit, review_overlay, sha256_file
from .layout import model_page
from .paths import Batch, rel
from .prompts import build_refs, load_jobs

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}


def queue(batch: Batch):
    return load_jobs(batch)


def find_job(batch: Batch, panel_id: str):
    for j in load_jobs(batch):
        if j.panel_id == panel_id:
            return j
    raise SystemExit(f"No prompt file for {panel_id} in {rel(batch.prompts_dir)}")


def next_job(batch: Batch, state: dict):
    for j in load_jobs(batch):
        p = state["panels"].get(j.panel_id, {})
        if p.get("status", "pending") in ("pending", "in_progress"):
            return j
    return None


def copy_to_clipboard(text: str) -> bool:
    """Unicode-safe clipboard on Windows via PowerShell; returns False elsewhere/on failure."""
    if os.name != "nt":
        return False
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(text)
        tmp = f.name
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
                            f"Set-Clipboard -Value (Get-Content -Raw -Encoding UTF8 '{tmp}')"],
                           capture_output=True, timeout=30)
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False
    finally:
        os.unlink(tmp)


def open_folder(path: Path) -> None:
    if os.name == "nt":
        os.startfile(str(path))  # noqa: S606 (local Explorer window)


# ---------------------------------------------------------------- Codex helpers

def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


def codex_images_since(since_iso: str | None) -> list[Path]:
    """Images saved by Codex's built-in image_gen tool after `since` (oldest first)."""
    root = codex_home() / "generated_images"
    if not root.exists():
        return []
    since = dt.datetime.fromisoformat(since_iso).timestamp() if since_iso else 0
    files = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXT and p.stat().st_mtime >= since]
    return sorted(files, key=lambda p: p.stat().st_mtime)


def checklist(job) -> list[str]:
    """The 'Accept only if' lines of a prompt file."""
    m = re.search(r"## 4\..*?\n(.*?)(?:\n\*\*Accepted variation|\n## )", job.body, re.S)
    return [ln[6:].strip() for ln in m.group(1).splitlines() if ln.startswith("- [ ] ")] if m else []


def has_balloon(batch: Batch, panel_id: str) -> bool:
    layout = jsonio.read(batch.layout_path(int(panel_id[6:9])))
    lp = next(x for x in layout["panels"] if x["panel_id"] == panel_id)
    return any(i.get("type") == "balloon" for i in lp.get("text", []))


def _decision_lines(batch: Batch, job) -> list[str]:
    pid = job.panel_id
    lines = [f"  all checks pass:        python -m pipeline approve --panel {pid}",
             f"  a check fails:          python -m pipeline reject --panel {pid} --reason \"<what failed>\"",
             "                          then fix it ONCE (targeted edit of that image, or regenerate with the same",
             "                          prompt and images), and file it again with: python -m pipeline ingest --from-codex",
             f"  still wrong after 1 fix: python -m pipeline approve --panel {pid} --status REVIEW_LATER --note \"<issue>\""]
    if has_balloon(batch, pid):
        lines += ["  speech balloon panel:   after approving, read U,V just beside the speaker's mouth (clear space,",
                  f"                          not on the face) from the review grid, then: python -m pipeline tail --panel {pid} --at U,V"]
    return lines


def _task_json(batch: Batch, job, task: str, total: int, refs=None, version=None) -> str:
    pid = job.panel_id
    w, h = job.card["size"]
    return json.dumps({
        "task": task, "panel_id": pid, "title": job.card.get("title"), "queue": job.queue, "total": total,
        "size": [w, h], "aspect": round(w / h, 3), "fallback_size": job.card.get("fallback_size"),
        "fallback_rule": job.card.get("fallback_rule"),
        "images": [str(f.resolve()) for f in (refs or [])], "prompt": job.prompt if task == "generate" else None,
        "art_version": version, "checklist": checklist(job), "balloon": has_balloon(batch, pid),
        "commands": {"ingest": "python -m pipeline ingest --from-codex",
                     "review": f"python -m pipeline review --panel {pid}",
                     "approve": f"python -m pipeline approve --panel {pid}",
                     "reject": f"python -m pipeline reject --panel {pid} --reason \"...\"",
                     "review_later": f"python -m pipeline approve --panel {pid} --status REVIEW_LATER --note \"...\"",
                     "tail": f"python -m pipeline tail --panel {pid} --at U,V", "next": "python -m pipeline next --codex"},
    }, indent=2, ensure_ascii=False)


def _emit_review_task(batch: Batch, state: dict, job, total: int, mode: str) -> None:
    v = state["panels"][job.panel_id]["versions"][-1]
    if mode == "json":
        print(_task_json(batch, job, "review", total, version=v["v"]))
        return
    print("=" * 78)
    print(f"CODEX TASK · REVIEW · {job.panel_id} · {job.card.get('title')} · queue {job.queue}/{total}")
    print("=" * 78)
    print(f"This panel already has new art waiting for review: version {v['v']}, {v['width']}x{v['height']},")
    print(f"  {(batch.root / v['file']).resolve()}")
    print()
    print(f"STEP 1 - run:  python -m pipeline review --panel {job.panel_id}")
    print("         then view_image the overlay PNG it prints AND the art PNG above.")
    print("         Accept only if:")
    for c in checklist(job):
        print(f"          - {c}")
    print()
    print("STEP 2 - decide:")
    print("\n".join(_decision_lines(batch, job)))
    print()
    print("Then run:  python -m pipeline next --codex")


def _emit_generate_task(batch: Batch, job, refs: list[Path], total: int) -> None:
    pid = job.panel_id
    w, h = job.card["size"]
    print("=" * 78)
    print(f"CODEX TASK · GENERATE · {pid} · {job.card.get('title')} · queue {job.queue}/{total}")
    print("=" * 78)
    print(f"Size: {w}x{h} px (aspect {w / h:.2f}:1). If your image tool cannot make this exact size, keep this aspect")
    print(f"      ratio; if it can only make 3:2, 2:3 or square images, {job.card.get('fallback_rule')}.")
    print()
    print("STEP 1 - view_image these reference images, in this order (they are Image 1, Image 2, ... in the prompt):")
    for i, f in enumerate(refs, 1):
        print(f"  Image {i}: {f.resolve()}")
    print()
    print("STEP 2 - call image_gen with exactly this prompt (everything between the markers, unchanged):")
    print("-----BEGIN PROMPT-----")
    print(job.prompt)
    print("-----END PROMPT-----")
    print()
    print("STEP 3 - file the image you made (picks your newest image from ~/.codex/generated_images):")
    print("  python -m pipeline ingest --from-codex")
    print(f"  (or copy it to {(batch.inbox / (pid + '.png')).resolve()} and run: python -m pipeline ingest --route codex)")
    print()
    print(f"STEP 4 - check it:  python -m pipeline review --panel {pid}")
    print("         then view_image the overlay PNG it prints AND the art PNG. Accept only if:")
    for c in checklist(job):
        print(f"          - {c}")
    print()
    print("STEP 5 - decide:")
    print("\n".join(_decision_lines(batch, job)))
    print()
    print("Then run:  python -m pipeline next --codex")


# ---------------------------------------------------------------- next

def cmd_next(batch: Batch, panel_id: str | None, clipboard: bool, open_refs: bool, mode: str = "human") -> None:
    """Hand out the next panel. mode: human (clipboard + Explorer), codex (full printed task), json."""
    state = st.load(batch)
    jobs = load_jobs(batch)
    total = len(jobs)
    if mode in ("codex", "json") and not panel_id:
        waiting = [j for j in jobs if state["panels"].get(j.panel_id, {}).get("status") == "art_ready"]
        if waiting:
            _emit_review_task(batch, state, waiting[0], total, mode)
            return
    job = find_job(batch, panel_id) if panel_id else next_job(batch, state)
    if job is None:
        if mode == "json":
            print(json.dumps({"task": "done", "next": ["python -m pipeline build", "python -m pipeline audit"]}))
        else:
            print("ALL PANELS DONE: every panel is approved or marked REVIEW_LATER.")
            print("Next: python -m pipeline build   then   python -m pipeline audit")
        return
    refs = build_refs(batch, job)
    p = st.panel(state, job.panel_id)
    resuming = (p.get("status") == "in_progress" and state.get("current_panel") == job.panel_id
                and state.get("current_started_at"))
    p["status"] = "in_progress"
    state["current_panel"] = job.panel_id
    if not resuming:  # keep the original start so images already made for this panel still count
        state["current_started_at"] = st.now()
    st.log(state, f"next -> {job.panel_id} ({mode}{', resumed' if resuming else ''})")
    st.save(batch, state)
    if mode == "codex":
        known = {v["sha256"] for x in state["panels"].values() for v in x.get("versions", [])}
        waiting = [f for f in codex_images_since(state["current_started_at"]) if sha256_file(f) not in known]
        if waiting:
            print(f"NOTE: {len(waiting)} image(s) were already generated for {job.panel_id} since it was handed out "
                  f"({state['current_started_at']}) but not filed yet.")
            print("      Do not generate again: run `python -m pipeline ingest --from-codex --all-new`, then review them.")
            print()
        _emit_generate_task(batch, job, refs, total)
        return
    if mode == "json":
        print(_task_json(batch, job, "generate", total, refs))
        return
    w, h = job.card["size"]
    fw, fh = job.card["fallback_size"]
    print(f"NEXT PANEL  {job.panel_id} · {job.card['title']}   (queue #{job.queue})")
    print(f"Prompt file {rel(job.path)}")
    print(f"Size        {w}x{h} (fixed-size tools: {fw}x{fh}; {job.card['fallback_rule']})")
    print("Attach, in this order:")
    for i, f in enumerate(refs, 1):
        print(f"  Image {i}: {rel(f)}")
    if clipboard and copy_to_clipboard(job.prompt + "\n"):
        print("The prompt is on your clipboard.")
    else:
        print("Prompt (copy it from the ```text block in the prompt file).")
    if open_refs:
        open_folder(refs[0].parent)
    print(f"Then save the image into {rel(batch.inbox)} (any name) and run:  python -m pipeline ingest")


# ---------------------------------------------------------------- ingest

def _downloads_candidates(since_iso: str | None) -> list[Path]:
    dl = Path.home() / "Downloads"
    if not dl.exists():
        return []
    since = dt.datetime.fromisoformat(since_iso).timestamp() if since_iso else 0
    files = [p for p in dl.iterdir() if p.suffix.lower() in IMAGE_EXT and p.stat().st_mtime >= since]
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)


def cmd_ingest(batch: Batch, panel_id: str | None, file: str | None, downloads: bool, route: str, note: str,
               from_codex: bool = False, all_new: bool = False) -> list[str]:
    state = st.load(batch)
    jobs = {j.panel_id: j for j in load_jobs(batch)}
    if from_codex:
        target = panel_id or state.get("current_panel")
        if not target:
            raise SystemExit("No panel is in progress. Run `python -m pipeline next --codex` first, or pass --panel.")
        known = {v["sha256"] for p in state["panels"].values() for v in p.get("versions", [])}
        fresh = [p for p in codex_images_since(state.get("current_started_at")) if sha256_file(p) not in known]
        if not fresh:
            raise SystemExit(f"No new image in {codex_home() / 'generated_images'} since this panel was handed out "
                             f"({state.get('current_started_at')}). Generate it first, or copy it into "
                             f"{rel(batch.inbox)} and run `python -m pipeline ingest --route codex`.")
        chosen = fresh if all_new else fresh[-1:]
        if len(fresh) > 1 and not all_new:
            print(f"Note: {len(fresh)} new Codex images found; filing the newest. Use --all-new to file all of them as versions.")
        candidates = []
        for i, src in enumerate(chosen, 1):
            dst = batch.inbox / f"{target}-codex-{dt.datetime.fromtimestamp(src.stat().st_mtime):%H%M%S}-{i}{src.suffix.lower()}"
            shutil.copy2(src, dst)
            candidates.append(dst)
        panel_id, route = target, "codex"
        note = note or "Codex built-in image_gen: " + ", ".join(p.name for p in chosen)
    elif file:
        candidates = [Path(file)]
    elif downloads:
        candidates = _downloads_candidates(state.get("current_started_at"))[:1]
        if not candidates:
            raise SystemExit("No new image in Downloads since `next` was run.")
    else:
        candidates = sorted([p for p in batch.inbox.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXT],
                            key=lambda p: p.stat().st_mtime)
    if not candidates:
        raise SystemExit(f"Nothing to ingest: {rel(batch.inbox)} is empty.")
    done = []
    for src in candidates:
        target = panel_id
        if not target:
            matches = [pid for pid in jobs if pid in src.name]
            if len(matches) == 1:
                target = matches[0]
            elif len(candidates) == 1 and state.get("current_panel"):
                target = state["current_panel"]
            else:
                print(f"SKIPPED {src.name}: cannot tell which panel it is. Rename it to include the panel ID "
                      f"(e.g. CH01-P009-PN01.png) or pass --panel.")
                continue
        if target not in jobs:
            raise SystemExit(f"{target} is not a panel of batch {batch.id}")
        p = st.panel(state, target)
        v = len(p["versions"]) + 1
        dest_dir = batch.panel_art_dir(target)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"{target}-art-v{v:03d}.png"
        with Image.open(src) as im:
            im.load()
            w, h = im.size
            if src.suffix.lower() == ".png":
                shutil.copy2(src, dest)
            else:
                im.convert("RGB").save(dest, "PNG")
        from .manifest import sha256_text
        p["versions"].append({
            "v": v, "file": dest.relative_to(batch.root).as_posix(), "sha256": sha256_file(dest),
            "width": w, "height": h, "route": route, "source_name": src.name,
            "prompt_sha256": sha256_text(jobs[target].prompt), "ingested_at": st.now(), "note": note or "",
        })
        p["status"] = "art_ready"
        if state.get("current_panel") == target:
            state["current_panel"] = None
        st.log(state, f"ingest {src.name} -> {target} v{v} ({w}x{h}, {route})")
        if src.parent.resolve() == batch.inbox.resolve():
            processed = batch.inbox / "_processed"
            processed.mkdir(exist_ok=True)
            shutil.move(str(src), processed / f"{dt.datetime.now():%Y%m%d-%H%M%S}-{src.name}")
        print(f"Filed {src.name} -> {rel(dest)}  ({w}x{h}, version {v})")
        done.append(target)
    st.save(batch, state)
    for t in done:
        print(f"Next: python -m pipeline review --panel {t}")
    return done


# ---------------------------------------------------------------- review

def cmd_review(batch: Batch, panel_id: str, version: int | None) -> Path:
    state = st.load(batch)
    p = state["panels"].get(panel_id)
    if not p or not p["versions"]:
        raise SystemExit(f"{panel_id} has no art yet. Run `next` / `ingest` first.")
    ver = next((x for x in p["versions"] if x["v"] == version), None) if version else p["versions"][-1]
    if ver is None:
        raise SystemExit(f"{panel_id} has no version {version}")
    art = batch.root / ver["file"]
    page = int(panel_id[6:9])
    layout = jsonio.read(batch.layout_path(page))
    lp = next(x for x in layout["panels"] if x["panel_id"] == panel_id)
    model = model_page(batch, page, mode="placeholder")
    pm = next(x for x in model.panels if x.panel_id == panel_id)
    with Image.open(art) as im:
        iw, ih = im.size
    cfg = lp.get("art", {})
    placement = cover_fit(tuple(lp["frame"]), iw, ih, cfg.get("focus", [0.5, 0.5]), cfg.get("zoom", 1.0))
    zones = [{"box": t.box, "label": t.type} for t in pm.texts if t.type in ("caption", "balloon")]
    tails = []
    for item in lp.get("text", []):
        if item.get("type") == "balloon":
            tt = item.get("tail_to", {})
            if tt.get("img"):
                tails.append({"u": tt["img"][0], "v": tt["img"][1], "label": "tail target"})
            elif tt.get("page"):
                u, v = placement.page_to_img(*tt["page"])
                tails.append({"u": u, "v": v, "label": "default tail target (set yours)"})
    out = batch.review_dir / f"{panel_id}-v{ver['v']:03d}-review.png"
    review_overlay(art, placement, zones, tails, out)
    vis = placement.visible_norm()
    print(f"{panel_id} v{ver['v']}: {iw}x{ih} px, effective {placement.ppi:.0f} ppi in a "
          f"{lp['frame'][2] - lp['frame'][0]}x{lp['frame'][3] - lp['frame'][1]} pt frame")
    print(f"Visible part of the image: x {vis[0]:.2f}-{vis[2]:.2f}, y {vis[1]:.2f}-{vis[3]:.2f} (gold box)")
    print(f"Overlay: {rel(out)}  (cyan = reserved text zones, magenta = tail target, grid = 0..1 coordinates)")
    print("Check the prompt file's 'Accept only if' list, then run one of:")
    print(f"  python -m pipeline approve --panel {panel_id}            # PASS")
    print(f"  python -m pipeline reject  --panel {panel_id} --reason \"...\"   # one retry allowed")
    if any(i.get("type") == "balloon" for i in lp.get("text", [])):
        print(f"  python -m pipeline tail    --panel {panel_id} --at U,V     # point beside the speaker's mouth")
    print(f"  python -m pipeline frame   --panel {panel_id} --focus U,V [--zoom 1.1]   # adjust the crop")
    return out


# ---------------------------------------------------------------- approve / reject

def cmd_approve(batch: Batch, panel_id: str, version: int | None, status: str, exceptions: list[str], note: str):
    state = st.load(batch)
    p = st.panel(state, panel_id)
    if not p["versions"]:
        raise SystemExit(f"{panel_id} has no art to approve.")
    v = version or p["versions"][-1]["v"]
    if not any(x["v"] == v for x in p["versions"]):
        raise SystemExit(f"{panel_id} has no version {v}")
    if status not in st.AUDIT_STATUSES:
        raise SystemExit(f"status must be one of {st.AUDIT_STATUSES}")
    p["approved_version"] = v
    p["audit_status"] = status
    p["status"] = "review_later" if status == "REVIEW_LATER" else "approved"
    p["exceptions"] = exceptions
    p["notes"] = note or p.get("notes", "")
    st.log(state, f"approve {panel_id} v{v} {status} {exceptions} {note}")
    st.save(batch, state)
    print(f"{panel_id}: version {v} -> {status}")
    page = int(panel_id[6:9])
    layout = jsonio.read(batch.layout_path(page))
    lp = next(x for x in layout["panels"] if x["panel_id"] == panel_id)
    if any(i.get("type") == "balloon" and not i.get("tail_to", {}).get("img") for i in lp.get("text", [])):
        print(f"Reminder: set the balloon tail on this art:  python -m pipeline tail --panel {panel_id} --at U,V")
    # Refresh the reference packs of panels that use this one as an anchor.
    for j in load_jobs(batch):
        if panel_id in (j.card.get("anchors") or []):
            build_refs(batch, j)
            print(f"  anchor added to refs of {j.panel_id}")


def cmd_reject(batch: Batch, panel_id: str, version: int | None, reason: str):
    state = st.load(batch)
    p = st.panel(state, panel_id)
    if not p["versions"]:
        raise SystemExit(f"{panel_id} has no art to reject.")
    v = version or p["versions"][-1]["v"]
    for x in p["versions"]:
        if x["v"] == v:
            x["rejected"] = reason
    p["retries"] = p.get("retries", 0) + 1
    st.log(state, f"reject {panel_id} v{v}: {reason}")
    if p["retries"] > st.MAX_AUTOMATIC_RETRIES:
        p["status"] = "art_ready"
        print(f"{panel_id}: retry budget used ({st.MAX_AUTOMATIC_RETRIES} automatic correction). Keep the better "
              f"version and continue:\n  python -m pipeline approve --panel {panel_id} --version N --status REVIEW_LATER "
              f"--note \"<what is still wrong>\"")
    else:
        p["status"] = "pending"
        # Keep this panel 'current' so the corrected image is picked up by `ingest --from-codex` / `--downloads`.
        state["current_panel"] = panel_id
        state["current_started_at"] = st.now()
        print(f"{panel_id}: v{v} rejected ({reason}). One correction attempt is allowed: make a targeted edit of v{v} "
              f"or regenerate with the same prompt and images, then file it with `python -m pipeline ingest --from-codex` "
              f"(or `ingest`), and review again.")
    st.save(batch, state)


# ---------------------------------------------------------------- tail / frame

def cmd_tail(batch: Batch, panel_id: str, uv: tuple[float, float], block: str | None):
    state = st.load(batch)
    art = st.approved_art(batch, state, panel_id) or st.latest_art(batch, state, panel_id)
    if not art:
        raise SystemExit(f"{panel_id} has no art; tail targets are recorded on the actual image.")
    page = int(panel_id[6:9])
    path = batch.layout_path(page)
    layout = jsonio.read(path)
    lp = next(x for x in layout["panels"] if x["panel_id"] == panel_id)
    balloons = [i for i in lp.get("text", []) if i.get("type") == "balloon" and (block is None or i["block"] == block)]
    if len(balloons) != 1:
        raise SystemExit(f"{panel_id}: found {len(balloons)} balloons; pass --block to choose one.")
    b = balloons[0]
    b.setdefault("tail_to", {})
    b["tail_to"]["img"] = [round(uv[0], 4), round(uv[1], 4)]
    b["tail_to"]["art_sha256"] = sha256_file(art)
    jsonio.write(path, layout)
    print(f"{panel_id}: tail of {b['block']} now aims at image point {uv} on {rel(art)}")


def cmd_frame(batch: Batch, panel_id: str, focus, zoom):
    page = int(panel_id[6:9])
    path = batch.layout_path(page)
    layout = jsonio.read(path)
    lp = next(x for x in layout["panels"] if x["panel_id"] == panel_id)
    art = lp.setdefault("art", {})
    if focus:
        art["focus"] = [round(focus[0], 3), round(focus[1], 3)]
    if zoom:
        art["zoom"] = round(zoom, 3)
    jsonio.write(path, layout)
    print(f"{panel_id}: focus {art.get('focus')}, zoom {art.get('zoom', 1.0)}. Re-run `review` to check the crop.")
