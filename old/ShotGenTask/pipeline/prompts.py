"""Panel prompt files: parse, lint, and build per-panel reference packs.

A prompt file (prompts/CH01-P0xx-PNyy.md) has a YAML job card between '---'
lines, a human-readable guide, and exactly one ```text block: the prompt that
is pasted into ChatGPT or passed to Codex's image tool. Attachments are listed
in the job card in the order the prompt calls them Image 1, Image 2, ...
"""
from __future__ import annotations

import json
import os
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import state as st
from .paths import APPROACH, Batch

PROMPT_BLOCK = re.compile(r"```text\n(.*?)\n```", re.S)
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
REQUIRED = ("panel_id", "job_key", "page", "panel", "title", "queue", "size", "fallback_size", "attachments")


@dataclass
class PromptJob:
    path: Path
    card: dict
    prompt: str
    body: str
    problems: list = field(default_factory=list)

    @property
    def panel_id(self) -> str:
        return self.card.get("panel_id", self.path.stem)

    @property
    def queue(self) -> int:
        return int(self.card.get("queue", 999))

    def attachment_files(self, batch: Batch) -> list[Path]:
        """Files in prompts/refs/<panel>/ in prompt order (Image 1, Image 2, ...)."""
        return [batch.refs_dir / self.panel_id / f"{i} - {Path(a['source']).name}"
                for i, a in enumerate(self.card.get("attachments", []), 1)]


def parse(path: Path) -> PromptJob:
    text = path.read_text(encoding="utf-8")
    m = FRONT_MATTER.match(text)
    card, problems = {}, []
    if not m:
        problems.append("missing YAML job card between --- lines at the top")
    else:
        try:
            card = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError as exc:
            problems.append(f"job card is not valid YAML: {exc}")
    blocks = PROMPT_BLOCK.findall(text)
    if len(blocks) != 1:
        problems.append(f"expected exactly one ```text prompt block, found {len(blocks)}")
    return PromptJob(path, card, blocks[0].strip() if blocks else "", text, problems)


def load_jobs(batch: Batch) -> list[PromptJob]:
    jobs = [parse(p) for p in sorted(batch.prompts_dir.glob("CH01-P*-PN*.md"))]
    return sorted(jobs, key=lambda j: j.queue)


def _legal_size(w: int, h: int) -> list[str]:
    issues = []
    if w % 16 or h % 16:
        issues.append("edges must be multiples of 16")
    if max(w, h) > 3840:
        issues.append("max edge 3840")
    if max(w, h) / min(w, h) > 3.0 + 1e-9:
        issues.append("ratio must be <= 3:1")
    if not 655_360 <= w * h <= 8_294_400:
        issues.append("total pixels out of range")
    return issues


def lint(batch: Batch, job: PromptJob, contracts: dict) -> list[str]:
    """Return a list of problems (empty list = PASS)."""
    problems = list(job.problems)
    card = job.card
    for key in REQUIRED:
        if key not in card:
            problems.append(f"job card missing '{key}'")
    pid = job.panel_id
    if job.path.stem != pid:
        problems.append(f"file name {job.path.name} does not match panel_id {pid}")
    panel = None
    for c in contracts.values():
        for p in c["panels"]:
            if p["panel_id"] == pid:
                panel = p
    if panel is None:
        problems.append(f"{pid} is not in this batch's contracts")
        return problems
    if card.get("job_key") != panel["job_key"]:
        problems.append(f"job_key {card.get('job_key')} != manuscript {panel['job_key']}")
    if "size" in card:
        problems += [f"size {card['size']}: {i}" for i in _legal_size(*card["size"])]
    # Attachments: every manuscript reference must be attached, and every file must exist.
    attached_sources = []
    for i, a in enumerate(card.get("attachments", []), 1):
        src = APPROACH / a.get("source", "")
        if not a.get("source") or not src.exists():
            problems.append(f"attachment {i} source not found: {a.get('source')}")
        if not a.get("role"):
            problems.append(f"attachment {i} has no role")
        attached_sources.append(Path(a.get("source", "")).name)
    for ref in panel["resolved_references"]:
        if ref["path"] and Path(ref["path"]).name not in attached_sources:
            problems.append(f"manuscript reference '{ref['literal']}' is not attached")
        if ref["status"] == "missing":
            problems.append(f"manuscript reference '{ref['literal']}' is missing from the asset folders")
    if card.get("review_needed"):
        problems.append("draft not reviewed yet (set review_needed: false after checking it)")
    # Prompt content rules.
    p = job.prompt
    if not p:
        return problems
    if "REVIEW:" in p:
        problems.append("prompt still contains 'REVIEW:' markers from the draft")
    for label in ("Use case:", "Input images:", "Primary request:", "Composition/framing:", "Avoid:"):
        if label not in p:
            problems.append(f"prompt lacks the '{label}' line")
    if "text" not in p.split("Avoid:", 1)[-1].lower():
        problems.append("Avoid line must forbid text/lettering in the image")
    n_attach = len(card.get("attachments", []))
    n_optional = len(card.get("anchors", []) or [])
    mentioned = [int(x) for x in re.findall(r"Image (\d+)", p)]
    if mentioned and max(mentioned) > n_attach + n_optional:
        problems.append(f"prompt mentions Image {max(mentioned)} but only {n_attach} (+{n_optional} optional) attached")
    for i in range(1, n_attach + 1):
        if i not in mentioned:
            problems.append(f"prompt never says what Image {i} is for")
    if re.search(r"\.(png|jpe?g|webp)\b", p, re.I):
        problems.append("prompt contains a filename; describe images by index instead")
    if re.search(r"CH01-P\d{3}", p):
        problems.append("prompt contains an internal panel ID")
    if re.search(r"\[[^\]]*\]|\bTODO\b|\bTBD\b|<[^>]+>", p):
        problems.append("prompt contains an unresolved placeholder")
    for b in panel["printable"]:
        for sentence in re.split(r"(?<=[.!?])\s+", b["render_text"]):
            if len(sentence) > 25 and sentence in p:
                problems.append(f"prompt contains printable manuscript text ('{sentence[:40]}...'); text is added by the pipeline")
    if len(p) > 4200:
        problems.append(f"prompt is {len(p)} characters; keep it under 4200")
    return problems


def build_refs(batch: Batch, job: PromptJob) -> list[Path]:
    """Hard-link (or copy) attachments into prompts/refs/<panel>/ as '1 - name', '2 - name', ...
    Adds approved anchor panels from this batch as the final optional images."""
    out_dir = batch.refs_dir / job.panel_id
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    made = []
    for a, dst in zip(job.card.get("attachments", []), job.attachment_files(batch)):
        _link(APPROACH / a["source"], dst)
        made.append(dst)
    state = st.load(batch)
    n = len(made)
    for anchor in job.card.get("anchors", []) or []:
        art = st.approved_art(batch, state, anchor)
        if art and art.exists():
            n += 1
            dst = out_dir / f"{n} - APPROVED {anchor}{art.suffix}"
            _link(art, dst)
            made.append(dst)
    return made


def _link(src: Path, dst: Path) -> None:
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def write_queue_md(batch: Batch) -> Path:
    """prompts/QUEUE.md: the generation order with each panel's images and size."""
    state = st.load(batch)
    rows = []
    for j in load_jobs(batch):
        p = state["panels"].get(j.panel_id, {})
        w, h = j.card.get("size", ["?", "?"])
        anchors = ", ".join(j.card.get("anchors") or []) or "—"
        rows.append(f"| {j.queue} | [{j.panel_id}]({j.path.name}) | {j.card.get('title', '')} | "
                    f"{len(j.card.get('attachments', []))} | {anchors} | {w}×{h} | {p.get('status', 'pending')} |")
    text = "\n".join([
        f"# Generation queue — batch {batch.id}", "",
        "Make the panels in this order. Scene anchors come first (the first panel at each location and of each "
        "character group); once an anchor is approved it is added automatically to the refs folder of the later "
        "panels that list it, so every later panel can match its lighting and character look.", "",
        "| # | Panel | Title | Images | Anchor (optional extra image) | Size | State |",
        "|---|---|---|---|---|---|---|", *rows, "",
        "Refresh this table with `python -m pipeline refs` (or see `output/STATUS.md`).", ""])
    out = batch.prompts_dir / "QUEUE.md"
    out.write_text(text, encoding="utf-8")
    return out


# ---------------------------------------------------------------- drafting (future batches)

AVOID_BASE = ("any text, letters, numbers, captions, speech balloons, sound effects, logos or watermarks (no writing on "
              "clothes, tickets, banners, the sketchbook or the map); the white label boxes, pointer lines and arrows "
              "drawn on Image 1 (annotations, not part of the place); a crescent moon in the sky (any visible moon is one "
              "complete full moon); religious symbols")


def _note_parts(note: str) -> dict:
    """Split a manuscript visual note into its labelled parts."""
    parts = {}
    for key, nxt in (("Location", "Location reference"), ("Camera", "Static visual"),
                     ("Static visual", "Character-sheet references"), ("Scene-specific stripe colours", "Style:")):
        m = re.search(rf"{re.escape(key)}:\s*(.*?)(?=\s*{re.escape(nxt)}|$)", note, re.S)
        if m:
            parts[key] = m.group(1).strip().rstrip(".") + "."
    static = parts.get("Static visual", "")
    if "Use the sheets" in static:
        static = static.split("Use the sheets")[0].strip()
    parts["Static visual"] = static
    m = re.search(r"((?:Night|Late afternoon|Early evening|Evening|Moonrise|Dawn)[^.]*\.)", static)
    parts["Lighting"] = m.group(1) if m else ""
    return parts


def draft_prompt(batch: Batch, contract: dict, cp: dict, lp: dict, queue: int) -> str:
    """A complete first draft that a prompt writer must review (lint fails until review_needed is false
    and every 'REVIEW:' marker is replaced)."""
    from .art import fallback_size, legal_gen_size
    from .paths import DESIGN, PROJECT
    chars = json.loads((DESIGN / "characters.json").read_text(encoding="utf-8"))
    locs = json.loads((DESIGN / "locations.json").read_text(encoding="utf-8"))["locations"]
    note = " ".join(n["text"] for n in cp["visual_notes"])
    parts = _note_parts(note)
    x0, y0, x1, y1 = lp["frame"]
    w, h = x1 - x0, y1 - y0
    gen, fb = legal_gen_size(w, h), fallback_size(w, h)
    attachments, roles, names = [], [], []
    for ref in cp["resolved_references"]:
        if not ref["path"]:
            continue
        src = os.path.relpath(PROJECT / ref["path"], APPROACH).replace("\\", "/")
        if ref["kind"] == "location":
            info = locs.get(Path(ref["path"]).name, {})
            attachments.append({"source": src, "role": "location"})
            roles.append(f"location reference: {info.get('name', Path(ref['path']).stem.title())} (architecture, materials, palette)")
        else:
            name = next((k for k, v in chars.items() if not k.startswith("_") and v["sheet"] == Path(ref["path"]).name), None)
            attachments.append({"source": src, "role": f"identity: {name}"})
            roles.append(f"{name} character sheet (identity)")
            names.append(name)
    subject = parts.get("Static visual", "")
    for n in names:
        subject = re.sub(rf"\b{n}\b", chars[n]["card"], subject, count=1)
    if parts.get("Scene-specific stripe colours"):
        subject += " Tez's markings in this scene: " + parts["Scene-specific stripe colours"]
    # Manuscript sentences sometimes name files; the image model should only hear "Image N" or "the sheet".
    subject = re.sub(r"[A-Z][A-Z &'-]* CHARACTER SHEET\.png", "the character sheet", subject)
    subject = re.sub(r"\S[^.;]*?\.png(\.png)?", "the reference image", subject)
    corrections = " ".join(c for ref in cp["resolved_references"] if ref["kind"] == "location" and ref["path"]
                           for c in locs.get(Path(ref["path"]).name, {}).get("corrections", []))
    exceptions = sorted({e for ref in cp["resolved_references"] if ref["kind"] == "location" and ref["path"]
                         for e in locs.get(Path(ref["path"]).name, {}).get("exceptions", [])})
    inputs = "; ".join(f"Image {i}: {r}" for i, r in enumerate(roles, 1))
    prompt = "\n".join([
        "Use case: illustration-story",
        f"Asset type: one graphic-novel panel, artwork only (all lettering is added later); output {gen[0]}x{gen[1]} px "
        f"(aspect about {w / h:.2f}:1)",
        f"Input images: {inputs}",
        "Primary request: REVIEW: one sentence saying what this panel shows.",
        f"Scene/backdrop: {parts.get('Location', '')} REVIEW: check these reference corrections still apply: {corrections or 'none'}",
        f"Subject: {subject}",
        "Style/medium: cinematic painterly graphic-novel illustration with a soft stylised-3D finish, matching the approved "
        "earlier panels; semi-realistic proportions and natural eye size exactly as in the character sheets.",
        f"Composition/framing: {parts.get('Camera', '')} {lp.get('compose', '')}",
        f"Lighting/mood: {parts.get('Lighting', '')}",
        "Constraints: keep each character's face, age, hair, outfit colours and accessories exactly as in their sheet; keep "
        "the architecture of Image 1. Use the sheets for appearance only; use this panel's pose, expression and props.",
        f"Avoid: {AVOID_BASE}; extra main characters.",
    ])
    card = {"panel_id": cp["panel_id"], "job_key": cp["job_key"], "page": contract["page"], "panel": cp["panel_number"],
            "title": cp["focus"], "queue": queue, "review_needed": True, "characters": names,
            "frame_pt": lp["frame"], "size": list(gen), "fallback_size": list(fb),
            "attachments": attachments, "anchors": [], "exceptions": exceptions,
            "manuscript_note": [n["block_id"] for n in cp["visual_notes"]]}
    yml = yaml.safe_dump(card, sort_keys=False, allow_unicode=True, width=1000, default_flow_style=None)
    checks = [s.strip() for s in re.split(r"(?<=[.;])\s+", parts.get("Static visual", "")) if len(s.strip()) > 3]
    text_lines = "\n".join(f"- **{b['role']}** `{b['block_id']}`: “{b['render_text']}”" for b in cp["printable"])
    notes = "\n\n".join(f"> `{n['block_id']}` {n['text']}" for n in cp["visual_notes"])
    return f"""---
{yml.rstrip()}
---

# {cp['panel_id']} · {cp['focus']}

> DRAFT made by `python -m pipeline prompts draft`. Review it against the manuscript note and the page brief,
> add a continuity image (an approved earlier panel) where useful, replace every `REVIEW:` marker, set
> `review_needed: false`, then run `python -m pipeline prompts lint`.

## 1. Attach these images, in this order

Numbered copies appear in `prompts/refs/{cp['panel_id']}/` after `python -m pipeline refs`.

## 2. Prompt (copy everything in the box)

```text
{prompt}
```

## 3. Size

- **Preferred:** {gen[0]}×{gen[1]} px. **Fixed-size tools:** {fb[0]}×{fb[1]}.

## 4. Accept only if (any failure = regenerate once, then REVIEW LATER)

{chr(10).join('- [ ] ' + c for c in checks)}
- [ ] No lettering anywhere; reserved text areas calm.

## 5. Source (non-printable; for checking only)

{text_lines}

{notes}
"""


def cmd_draft(batch: Batch, pages: list[int], force: bool) -> list[Path]:
    from . import jsonio
    made = []
    queue = 1 + max([j.queue for j in load_jobs(batch)] or [0])
    for page in pages:
        contract = json.loads(batch.contract_path(page).read_text(encoding="utf-8"))
        layout = jsonio.read(batch.layout_path(page))
        lps = {p["panel_id"]: p for p in layout["panels"]}
        for cp in contract["panels"]:
            if not cp["visual_notes"]:
                continue  # maths/text panels are typeset, not generated
            out = batch.prompt_path(cp["panel_id"])
            if out.exists() and not force:
                print(f"skip {out.name} (exists; use --force to overwrite)")
                continue
            out.write_text(draft_prompt(batch, contract, cp, lps[cp["panel_id"]], queue), encoding="utf-8")
            queue += 1
            made.append(out)
            print(f"drafted {out.name}")
    return made


def load_contracts(batch: Batch) -> dict:
    out = {}
    for page in batch.pages:
        path = batch.contract_path(page)
        if path.exists():
            out[page] = json.loads(path.read_text(encoding="utf-8"))
    return out
