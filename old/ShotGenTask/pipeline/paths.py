"""Filesystem locations used by the pipeline.

Everything the pipeline writes lives inside Approach1/. The project's source
folders (Scripts, Charactors, Locations, Completed Samples) are read-only inputs.
"""
from __future__ import annotations

import json
from pathlib import Path

APPROACH = Path(__file__).resolve().parents[1]
PROJECT = APPROACH.parent

SCRIPTS = PROJECT / "Scripts"
CHARACTERS = PROJECT / "Charactors" / "CHANDRUSH CHARACTERS"
LOCATIONS = PROJECT / "Locations" / "CH 01 LOCATIONS"
SAMPLES = PROJECT / "Completed Samples"

MANIFEST = SCRIPTS / "CH01_V07_PANEL_MANIFEST.json"
MANUSCRIPT = SCRIPTS / "CH 01 PANELIZED MANUSCRIPT V07.docx"

DESIGN = APPROACH / "design"
FONTS = APPROACH / "fonts"
BATCHES = APPROACH / "batch"
CONTINUITY = DESIGN / "continuity"

READ_ONLY_ROOTS = (SCRIPTS, CHARACTERS.parent, LOCATIONS.parent, SAMPLES)


class Batch:
    """One production batch, e.g. batch/P009-P013."""

    def __init__(self, batch_id: str):
        self.id = batch_id
        self.root = BATCHES / batch_id
        if not self.root.exists():
            raise SystemExit(f"Batch folder not found: {self.root}")
        cfg = self.root / "batch.json"
        self.config = json.loads(cfg.read_text(encoding="utf-8")) if cfg.exists() else {}
        self.pages = list(self.config.get("pages", []))
        self.pages_dir = self.root / "pages"
        self.prompts_dir = self.root / "prompts"
        self.refs_dir = self.prompts_dir / "refs"
        self.art_dir = self.root / "art"
        self.inbox = self.art_dir / "_inbox"
        self.review_dir = self.art_dir / "_review"
        self.output = self.root / "output"
        self.pdf_dir = self.output / "pdf"
        self.png_dir = self.output / "png"
        self.compare_dir = self.output / "compare"
        self.cache_dir = self.root / ".cache"
        self.state_file = self.root / "state.json"

    def page_id(self, page: int) -> str:
        return f"CH01-P{page:03d}"

    def contract_path(self, page: int) -> Path:
        return self.pages_dir / f"{self.page_id(page)}.contract.json"

    def layout_path(self, page: int) -> Path:
        return self.pages_dir / f"{self.page_id(page)}.layout.json"

    def prompt_path(self, panel_id: str) -> Path:
        return self.prompts_dir / f"{panel_id}.md"

    def panel_art_dir(self, panel_id: str) -> Path:
        return self.art_dir / panel_id

    def ensure_dirs(self) -> None:
        for d in (self.pages_dir, self.prompts_dir, self.refs_dir, self.inbox, self.review_dir,
                  self.pdf_dir, self.png_dir, self.compare_dir, self.cache_dir):
            d.mkdir(parents=True, exist_ok=True)


def default_batch_id() -> str:
    """The only batch folder, or the most recently modified one."""
    batches = [p for p in BATCHES.iterdir() if p.is_dir()] if BATCHES.exists() else []
    if not batches:
        raise SystemExit("No batch folders found under Approach1/batch.")
    batches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return batches[0].name


def rel(path: Path, base: Path = APPROACH) -> str:
    """Path relative to Approach1 (or the project) with forward slashes, for reports."""
    path = Path(path).resolve()
    for root in (base, PROJECT):
        try:
            return path.relative_to(root).as_posix()
        except ValueError:
            continue
    return path.as_posix()
