"""Optional unattended route: call Codex's bundled image CLI (gpt-image-2) for a panel.

Uses ~/.codex/skills/.system/imagegen/scripts/image_gen.py exactly as shipped
(never modified). Needs OPENAI_API_KEY and network for real calls; --dry-run
prints the request without either. Codex users can instead use the built-in
image_gen tool, which needs no key (see AGENTS.md).
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from .paths import Batch, rel
from .prompts import build_refs
from .workflow import cmd_ingest, find_job


def image_gen_script() -> Path:
    home = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    return home / "skills" / ".system" / "imagegen" / "scripts" / "image_gen.py"


def build_command(batch: Batch, panel_id: str, quality: str, dry_run: bool) -> tuple[list[str], Path]:
    job = find_job(batch, panel_id)
    refs = build_refs(batch, job)
    prompt_file = batch.cache_dir / f"prompt-{panel_id}.txt"
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    prompt_file.write_text(job.prompt + "\n", encoding="utf-8")
    out = batch.inbox / f"{panel_id}.png"
    w, h = job.card["size"]
    cmd = [sys.executable, str(image_gen_script()), "edit"]
    for r in refs:
        cmd += ["--image", str(r)]
    cmd += ["--prompt-file", str(prompt_file), "--size", f"{w}x{h}", "--quality", quality,
            "--no-augment", "--out", str(out)]
    if dry_run:
        cmd.append("--dry-run")
    return cmd, out


def cmd_generate(batch: Batch, panel_id: str, quality: str, run: bool) -> None:
    script = image_gen_script()
    if not script.exists():
        raise SystemExit(f"Codex image CLI not found at {script}. Use the Codex built-in tool or the web UI route.")
    live = run and bool(os.environ.get("OPENAI_API_KEY"))
    if run and not live:
        print("OPENAI_API_KEY is not set, so this is a dry run. Set the key in your environment to generate for real.")
    cmd, out = build_command(batch, panel_id, quality, dry_run=not live)
    print("Command:\n  " + " ".join(f'"{c}"' if " " in c else c for c in cmd))
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout.strip()[-3000:])
    if r.returncode != 0:
        print(r.stderr.strip()[-2000:])
        raise SystemExit(f"image_gen.py exited with {r.returncode}")
    if live:
        if out.exists():
            cmd_ingest(batch, panel_id, str(out), False, "api", f"gpt-image-2 quality={quality}")
        else:
            raise SystemExit(f"Expected output {rel(out)} was not written.")
