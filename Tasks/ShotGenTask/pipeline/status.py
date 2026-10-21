"""STATUS.md: one table that says where every panel stands and what to do next."""
from __future__ import annotations

from . import jsonio
from . import state as st
from .paths import Batch, rel
from .prompts import lint, load_contracts, load_jobs


def cmd_status(batch: Batch, quiet: bool = False) -> str:
    state = st.load(batch)
    contracts = load_contracts(batch)
    jobs = load_jobs(batch)
    rows = []
    counts = {}
    next_action = None
    for j in jobs:
        p = state["panels"].get(j.panel_id, {})
        status = p.get("status", "pending")
        counts[status] = counts.get(status, 0) + 1
        problems = lint(batch, j, contracts)
        versions = p.get("versions", [])
        latest = versions[-1] if versions else None
        page = int(j.panel_id[6:9])
        layout = jsonio.read(batch.layout_path(page))
        lp = next(x for x in layout["panels"] if x["panel_id"] == j.panel_id)
        balloons = [i for i in lp.get("text", []) if i.get("type") == "balloon"]
        tail = "—" if not balloons else ("set" if all(b.get("tail_to", {}).get("img") for b in balloons) else "default")
        lint_text = "OK" if not problems else "%d issue(s)" % len(problems)
        art_text = str(len(versions))
        if latest:
            art_text += " (v%d %dx%d)" % (latest["v"], latest["width"], latest["height"])
        state_text = status
        if p.get("approved_version"):
            state_text += " · v%d %s" % (p["approved_version"], p.get("audit_status"))
        rows.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            j.queue, j.panel_id, j.card.get("title", ""), lint_text, art_text, state_text, tail, p.get("retries", 0)))
        if next_action is None and status in ("pending", "in_progress"):
            next_action = f"Make the art for {j.panel_id}: `python -m pipeline next` (Codex: `python -m pipeline next --codex`; see MANUAL.md)."
        if next_action is None and status == "art_ready":
            next_action = f"Review {j.panel_id}: `python -m pipeline review --panel {j.panel_id}`."
    if next_action is None:
        if any(r.startswith("| ") and "| default |" in r for r in rows):
            next_action = "Record balloon tail targets with `python -m pipeline tail`, then build."
        else:
            next_action = "All panels have approved art. Run `python -m pipeline build` then `python -m pipeline audit`."
    summary = ", ".join(f"{k}: {v}" for k, v in sorted(counts.items()))
    md = "\n".join([
        f"# Status — batch {batch.id}", "",
        f"Updated {st.now()} by `python -m pipeline status`.", "",
        f"**Panels:** {len(jobs)} ({summary})  ", f"**Next action:** {next_action}", "",
        "| Queue | Panel | Title | Prompt lint | Art versions | State | Balloon tail | Retries |",
        "|---|---|---|---|---|---|---|---|",
        *rows, "",
        "States: pending → in_progress (prompt handed to an image tool) → art_ready (ingested) → approved / review_later.",
        f"Log of every action: `{rel(batch.state_file)}`.", ""])
    out = batch.output / "STATUS.md"
    out.write_text(md, encoding="utf-8")
    if not quiet:
        print(md)
    return md
