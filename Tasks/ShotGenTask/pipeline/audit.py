"""Audit the exported pages against the manuscript and the rules.

Checks the actual PDF (not the layout files): exact text coverage and order,
nothing non-printable printed, fonts embedded, page size, art status and
effective resolution, balloon tails. Writes output/AUDIT.md and audit.json.
"""
from __future__ import annotations

import json
import re

import pymupdf

from . import state as st
from .design import tokens
from .paths import Batch, rel

ALLOWED_FONTS = {"SourceSerif4-Regular", "SourceSerif4-Semibold", "SourceSans3-Regular", "SourceSans3-Semibold"}
FORBIDDEN = [
    (re.compile(r"CH01-P\d{3}"), "internal panel/page ID"),
    (re.compile(r"V0\d-B\d{4}"), "source block ID"),
    (re.compile(r"\.(png|jpe?g)\b", re.I), "filename"),
    (re.compile(r"\bPRINTABLE\b|NON-PRINTABLE"), "production marker"),
    (re.compile(r"(?m)^\s*Narration\s*$"), "'Narration' role label"),
]


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def audit_page(batch: Batch, page: int, pdf, record: dict | None, state: dict) -> dict:
    T = tokens()
    contract = json.loads(batch.contract_path(page).read_text(encoding="utf-8"))
    res = {"page": page, "page_id": contract["page_id"], "pdf": rel(pdf), "checks": [], "status": None}

    def check(name, ok, detail="", severity="BLOCK"):
        res["checks"].append({"check": name, "result": "PASS" if ok else severity, "detail": detail})

    doc = pymupdf.open(pdf)
    pg = doc[0]
    check("page size 864x648 pt", abs(pg.rect.width - T["page"]["width_pt"]) < 0.5 and abs(pg.rect.height - T["page"]["height_pt"]) < 0.5,
          f"{pg.rect.width:.1f}x{pg.rect.height:.1f}")
    fonts = pg.get_fonts(full=True)
    resource_names = {f[3].split("+")[-1] for f in fonts}
    embedded = {f[3].split("+")[-1] for f in fonts if f[1] != "n/a"}
    used = {s["font"].split("+")[-1] for b in pg.get_text("dict")["blocks"] for ln in b.get("lines", []) for s in ln["spans"]}
    check("text uses only the four Source faces", used <= ALLOWED_FONTS, ", ".join(sorted(used)))
    check("every font used is embedded", used <= embedded, ", ".join(sorted(used - embedded)) or "all embedded")
    check("no unused fonts in the page resources", resource_names <= ALLOWED_FONTS,
          ", ".join(sorted(resource_names - ALLOWED_FONTS)), severity="NOTE")
    text = pg.get_text("text")
    flat = norm(text)
    doc.close()

    # Exact text coverage, order, and nothing extra.
    remaining = flat
    pos = -1
    in_order = True
    for p in contract["panels"]:
        for b in p["printable"]:
            want = norm(b["render_text"])
            count = flat.count(want)
            check(f"text {b['block_id']} ({b['role']}) printed exactly once, word-for-word", count == 1,
                  f"found {count}x: “{b['render_text'][:60]}{'…' if len(b['render_text']) > 60 else ''}”")
            idx = flat.find(want)
            if idx < pos:
                in_order = False
            pos = max(pos, idx)
            remaining = remaining.replace(want, " ", 1)
            if b.get("speaker_prefix_rendered_by_tail"):
                check(f"text {b['block_id']}: speaker prefix '{b['speaker_prefix_rendered_by_tail'].strip()}' not printed "
                      "(tail identifies the speaker)", b["speaker_prefix_rendered_by_tail"].strip() not in flat)
    check("text appears in manuscript reading order", in_order)
    leftover = norm(re.sub(rf"\b{page:02d}\b", " ", remaining, count=1))
    check("no extra text on the page (only the page number)", leftover == "", leftover[:120])
    for rx, label in FORBIDDEN:
        m = rx.search(text)
        check(f"no {label} printed", m is None, m.group(0) if m else "")

    # Art, resolution and balloons from the build record.
    art_states = []
    if record:
        for pr in record["panels"]:
            pid = pr["panel_id"]
            pstate = state["panels"].get(pid, {})
            kind = pr["art_kind"]
            audit_status = pstate.get("audit_status")
            if kind == "approved":
                ok = audit_status in ("PASS", "PASS_WITH_LOCATION_EXCEPTION")
                check(f"{pid}: approved art ({audit_status})", ok,
                      f"v{pstate.get('approved_version')} {', '.join(pstate.get('exceptions') or [])} {pstate.get('notes', '')}".strip(),
                      severity="REVIEW")
                ppi = pr.get("effective_ppi", 0)
                check(f"{pid}: effective resolution >= {T['art']['target_ppi']} ppi", ppi >= T["art"]["target_ppi"] - 0.5,
                      f"{ppi:.0f} ppi", severity="NOTE" if ppi >= T["art"]["review_min_ppi"] else "REVIEW")
            else:
                check(f"{pid}: final art present", False, f"using {kind} art", severity="PROOF")
            art_states.append(kind)
        panel_chars = {p["panel_id"]: " ".join(p["character_references"]).upper() for p in contract["panels"]}
        for t in record["texts"]:
            if t["type"] != "balloon":
                continue
            tail = t.get("tail")
            check(f"balloon {t['block_id']}: has a tail", bool(tail))
            if tail:
                fr = next(p["frame"] for p in record["panels"] if p["panel_id"] == t["panel_id"])
                tip = tail["tip"]
                inside = fr[0] <= tip[0] <= fr[2] and fr[1] <= tip[1] <= fr[3]
                check(f"balloon {t['block_id']}: tail tip inside its panel", inside, f"tip {tip}")
                check(f"balloon {t['block_id']}: tail aimed on the final art (not a layout default)",
                      t.get("tail_source") == "art", t.get("tail_source") or "", severity="PROOF" if "approved" not in art_states else "REVIEW")
            if t.get("speaker"):
                check(f"balloon {t['block_id']}: speaker {t['speaker']} is drawn in this panel",
                      t["speaker"].upper() in panel_chars.get(t["panel_id"], ""))
    else:
        check("build record found", False, "run `python -m pipeline build` first")

    results = [c["result"] for c in res["checks"]]
    if "BLOCK" in results:
        res["status"] = "FAIL"
    elif "PROOF" in results:
        res["status"] = "PROOF (art pending)"
    elif "REVIEW" in results:
        res["status"] = "REVIEW"
    else:
        res["status"] = "PASS"
    return res


def run_audit(batch: Batch, pages: list[int], proof: str | None = None) -> list[dict]:
    state = st.load(batch)
    name = f"CH01-P{pages[0]:03d}-P{pages[-1]:03d}"
    suffix = {"standin": "-STANDIN-PROOF", "placeholder": "-LAYOUT-PROOF", "latest": "-LATEST"}.get(proof, "")
    rec_path = batch.output / f"{name}{suffix}.build.json"
    records = {r["page"]: r for r in json.loads(rec_path.read_text(encoding="utf-8"))} if rec_path.exists() else {}
    pdf_dir = batch.output / "proofs" if proof in ("standin", "placeholder") else batch.pdf_dir
    results = []
    for page in pages:
        pdf = pdf_dir / f"CH01-P{page:03d}{suffix}.pdf"
        if not pdf.exists():
            results.append({"page": page, "page_id": f"CH01-P{page:03d}", "pdf": rel(pdf), "status": "MISSING",
                            "checks": [{"check": "PDF exists", "result": "BLOCK", "detail": "build it first"}]})
            continue
        results.append(audit_page(batch, page, pdf, records.get(page), state))
    out_json = batch.output / f"AUDIT{suffix}.json"
    out_json.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(batch, results, batch.output / f"AUDIT{suffix}.md", suffix)
    return results


def write_markdown(batch: Batch, results: list[dict], out, suffix: str) -> None:
    lines = [f"# Audit — batch {batch.id}{' (' + suffix.strip('-') + ')' if suffix else ''}", "",
             f"Generated {st.now()} by `python -m pipeline audit`. Checks the exported PDFs against "
             "`Scripts/CH01_V07_PANEL_MANIFEST.json` and the rules in `guide/02_RULES.md`.", "",
             "Statuses: **PASS** = ready for user review as final; **REVIEW** = usable proof with a recorded issue; "
             "**PROOF** = stand-in/placeholder art still in place; **FAIL** = text, font or size problem (must fix).", "",
             "| Page | Status | Blocking | Review | Proof | Notes |", "|---|---|---|---|---|---|"]
    for r in results:
        res = [c["result"] for c in r["checks"]]
        notes = [c for c in r["checks"] if c["result"] == "NOTE"]
        lines.append(f"| {r['page_id']} | **{r['status']}** | {res.count('BLOCK')} | {res.count('REVIEW')} | "
                     f"{res.count('PROOF')} | {len(notes)} |")
    for r in results:
        lines += ["", f"## {r['page_id']} — {r['status']}", "", f"File: `{r['pdf']}`", "",
                  "| Result | Check | Detail |", "|---|---|---|"]
        for c in r["checks"]:
            detail = str(c["detail"]).replace("|", "/")
            lines.append(f"| {c['result']} | {c['check']} | {detail} |")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
