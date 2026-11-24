---
name: chandrush-backgrounds
description: 'Make, continue, review or fix the ChandRush Chapter 01 location images defined by Location Image Register V10 (32 records such as S01-B01 and M01-D01, 4:3 at 1K, with title band and callouts). Generation goes through the OpenAI Images API (gpt-image-2.5-sunburst) with locgen.py, samples first as a small Batch API run (no immediate calls unless the user explicitly asks), then the full run through the OpenAI Batch API in dependency waves. Use when asked to make CH01 backgrounds, locations or location images, run the samples or the batch, check status, QC, fix or compose records. Arguments: samples | batch | status | fix <ID> "<problem>".'
---

# ChandRush CH01 location images (Register V10)

**Task folder:** `/home/abhay/F/Freelance/Ankush-Project/Tasks/BagroundGenTask`. Run every command there.

Read `FLOW.md` and `PROMPT-GUIDE.md` there first; they are binding. **Override (user, 2026-11-22): no immediate calls at all unless the user explicitly says so. Samples, fixes and re-runs all go through `locgen.py batch` (fixes via `fix --queue`). Ignore any immediate `gen` instruction in FLOW.md or KICKOFF-1.**

**Token budget (overrides FLOW.md where they differ).** Read an image only when you must judge it. Prefer one contact sheet over many images. Never re-read an image already in your context.
- Reference images are attached by `locgen.py`; you don't need to Read them to attach them. Read one (or the spatial map) only for the specific thing the record needs, once.
- Read `locgen.py brief <ID>` for the records you are writing, not the whole register or manuscript; `grep -n -m 5` the manuscript if needed.
- Wait with ONE `python3 locgen.py batch wait <name>` started with `run_in_background`, then end your turn; its completion notification wakes you. Never poll with `sleep`, `pgrep`, `until`, `timeout`, Monitor loops or repeated `batch status`.
- QC from `python3 locgen.py sheet <ID…>` (one contact sheet of the new plates, `out/sheets/`); `zoom` only what looks wrong or what a CHECK needs. After a fix wave, QC only the re-generated/fixed records.

Then act on the argument:

| Argument | Do |
|---|---|
| `samples` | Follow `KICKOFF-1-SAMPLES.md` exactly, then stop for the user's verdict. |
| `batch` | Only after the user approved the samples: follow `KICKOFF-2-BATCH.md`. |
| `status` | Run `python3 locgen.py status` and `python3 locgen.py cost`, and summarise what is approved, in review, queued or blocked, and what is ready next. |
| `fix <ID> "<problem>"` | Zoom-check just the problem area. Choose `fix` (local) or a prompt revision with `qc fail --regen`, as FLOW.md section 5.8 describes. Use `--queue` unless the user asked for an immediate call. Respect the 3-call cap. |
