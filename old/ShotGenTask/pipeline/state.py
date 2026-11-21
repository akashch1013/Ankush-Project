"""Batch state: which panels have prompts, art versions, approvals and retries.

state.json is the single record of progress, so any agent (or a human) can stop
and resume without regenerating work that already passed.
"""
from __future__ import annotations

import datetime as dt
import json

from .paths import Batch

STATUSES = ("pending", "in_progress", "art_ready", "approved", "review_later")
AUDIT_STATUSES = ("PASS", "PASS_WITH_LOCATION_EXCEPTION", "REVIEW_LATER", "TECHNICAL_RETRY")
MAX_AUTOMATIC_RETRIES = 1  # Production Brief V03 §16.3: at most one automatic correction


def now() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def load(batch: Batch) -> dict:
    if batch.state_file.exists():
        return json.loads(batch.state_file.read_text(encoding="utf-8"))
    return {"batch": batch.id, "panels": {}, "current_panel": None, "current_started_at": None, "log": []}


def save(batch: Batch, state: dict) -> None:
    batch.state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def panel(state: dict, panel_id: str) -> dict:
    return state["panels"].setdefault(panel_id, {
        "status": "pending", "versions": [], "approved_version": None,
        "audit_status": None, "exceptions": [], "notes": "", "retries": 0,
    })


def log(state: dict, message: str) -> None:
    state.setdefault("log", []).append(f"{now()}  {message}")


def approved_art(batch: Batch, state: dict, panel_id: str):
    """Path of the approved art for a panel, or None."""
    p = state["panels"].get(panel_id)
    if not p or not p.get("approved_version"):
        return None
    for v in p["versions"]:
        if v["v"] == p["approved_version"]:
            return batch.root / v["file"]
    return None


def latest_art(batch: Batch, state: dict, panel_id: str):
    p = state["panels"].get(panel_id)
    if not p or not p["versions"]:
        return None
    return batch.root / p["versions"][-1]["file"]
