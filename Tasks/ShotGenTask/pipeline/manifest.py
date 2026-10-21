"""Read the V07 panel manifest and write exact page contracts.

A page contract separates what the reader sees (printable blocks, exact text)
from everything else (visual notes, reference filenames, role labels, locators).
Printable text is copied byte-for-byte from the manifest; nothing is rewritten.
"""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path

from .paths import CHARACTERS, DESIGN, LOCATIONS, MANIFEST, MANUSCRIPT, rel

PRINTABLE_ROLES = {
    "narration", "dialogue", "reader_interaction", "heading", "teaching_text",
    "source_diagram_text", "table", "embedded_diagram",
}
NON_PRINTABLE_ROLES = {"source_role_label"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@lru_cache(maxsize=1)
def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def manifest_pages() -> dict[int, dict]:
    return {p["graphic_novel_page"]: p for p in load_manifest()["pages"]}


@lru_cache(maxsize=1)
def reference_map() -> dict:
    path = DESIGN / "reference_map.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def resolve_reference(literal: str) -> dict:
    """Find the actual file for a literal manuscript filename. Never guesses:
    only exact names or explicit entries in design/reference_map.json."""
    for folder, kind in ((LOCATIONS, "location"), (CHARACTERS, "character")):
        candidate = folder / literal
        if candidate.exists():
            return {"literal": literal, "kind": kind, "path": rel(candidate), "status": "found"}
    mapped = reference_map().get("mappings", {}).get(literal)
    if mapped and mapped.get("file"):
        for folder, kind in ((LOCATIONS, "location"), (CHARACTERS, "character")):
            candidate = folder / mapped["file"]
            if candidate.exists():
                return {"literal": literal, "kind": kind, "path": rel(candidate),
                        "status": mapped.get("status", "mapped"), "reason": mapped.get("reason", "")}
    return {"literal": literal, "kind": "unknown", "path": None, "status": "missing"}


def split_references(values: list[str]) -> list[str]:
    out: list[str] = []
    for value in values:
        out.extend(part.strip() for part in value.split(";") if part.strip())
    return out


def render_text(block: dict) -> tuple[str, str | None]:
    """Text as printed on the page. Dialogue drops the exact 'SPEAKER: ' prefix
    (user decision 2026-10-11: the balloon tail identifies the speaker)."""
    text = block.get("text") or ""
    speaker = block.get("speaker")
    if block.get("role") == "dialogue" and speaker:
        prefix = f"{speaker.upper()}: "
        if text.startswith(prefix):
            return text[len(prefix):], prefix
    return text, None


def build_contract(page_number: int) -> dict:
    m = load_manifest()
    pages = manifest_pages()
    if page_number not in pages:
        raise SystemExit(f"Page {page_number} is not in the manifest.")
    page = pages[page_number]
    panels = []
    for pn in page["panels"]:
        printable, non_printable = [], []
        for b in pn["content_blocks"]:
            entry = {
                "block_id": b["source_block_id"],
                "role": b["role"],
                "kind": b["kind"],
                "style": b.get("style"),
                "text": b.get("text"),
                "text_sha256": sha256_text(b.get("text") or ""),
                "source_xml_sha256": b.get("source_xml_sha256"),
            }
            if b.get("speaker"):
                entry["speaker"] = b["speaker"]
            if b["role"] in NON_PRINTABLE_ROLES:
                entry["why_not_printed"] = "Source role label (manifest: NON-PRINTABLE — SOURCE ROLE LABEL)."
                non_printable.append(entry)
                continue
            printed, prefix = render_text(b)
            entry["render_text"] = printed
            if prefix:
                entry["speaker_prefix_rendered_by_tail"] = prefix
            entry["runs"] = b.get("runs", [])
            if b.get("math_ooxml"):
                entry["math_ooxml"] = b["math_ooxml"]
            if b.get("rows"):
                entry["rows"] = b["rows"]
            printable.append(entry)
        refs = split_references(pn.get("location_references", [])) + split_references(pn.get("character_references", []))
        panels.append({
            "panel_id": pn["panel_id"],
            "job_key": pn["job_key"],
            "panel_number": pn["panel_number"],
            "panel_type": pn["panel_type"],
            "focus": pn["focus"],
            "location_references": split_references(pn.get("location_references", [])),
            "character_references": split_references(pn.get("character_references", [])),
            "resolved_references": [resolve_reference(r) for r in refs],
            "locked_approved_artwork": pn.get("locked_approved_artwork"),
            "printable": printable,
            "non_printable": non_printable,
            "visual_notes": [{"block_id": n["source_block_id"], "text": n["text"]} for n in pn.get("assigned_source_notes", [])],
            "panelisation_notes": pn.get("panelisation_notes", []),
            "open_detail_ids": pn.get("open_detail_ids", []),
        })
    return {
        "schema": "approach1.page_contract.v1",
        "page_id": page["page_id"],
        "page": page_number,
        "revision": page["revision"],
        "book_name": m.get("book_name"),
        "chapter_identity": page.get("chapter_identity"),
        "page_purpose": page.get("page_purpose"),
        "manifest_file": rel(MANIFEST),
        "manifest_sha256": sha256_file(MANIFEST),
        "manuscript_file": rel(MANUSCRIPT),
        "manuscript_sha256_expected": m.get("manuscript_sha256"),
        "page_notes": [{"block_id": n["source_block_id"], "text": n["text"]} for n in page.get("page_common_notes", [])],
        "shared_notes": page.get("shared_source_notes", []),
        "panels": panels,
    }


def verify_manuscript() -> dict:
    """Confirm the DOCX on disk is the one the manifest was built from."""
    expected = load_manifest().get("manuscript_sha256")
    actual = sha256_file(MANUSCRIPT) if MANUSCRIPT.exists() else None
    return {"file": rel(MANUSCRIPT), "expected": expected, "actual": actual, "match": expected == actual}


def check_contract(contract: dict) -> list[str]:
    """Re-read the manifest and confirm every printable block is identical."""
    problems = []
    pages = manifest_pages()
    page = pages[contract["page"]]
    source = {b["source_block_id"]: b for pn in page["panels"] for b in pn["content_blocks"]}
    for panel in contract["panels"]:
        for entry in panel["printable"]:
            src = source.get(entry["block_id"])
            if src is None:
                problems.append(f"{panel['panel_id']}: block {entry['block_id']} not in manifest")
            elif sha256_text(src.get("text") or "") != entry["text_sha256"] or src.get("text") != entry["text"]:
                problems.append(f"{panel['panel_id']}: block {entry['block_id']} text differs from manifest")
    return problems
