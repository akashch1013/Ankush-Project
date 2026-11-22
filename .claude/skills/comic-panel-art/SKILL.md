---
name: comic-panel-art
description: Stage 2 of the ChandRush comic pipeline. Makes the final letter-free panel illustrations (background plate + characters + action + props), character vignettes and props for planned pages, attaching the right references (raw background plate first, then each visible character's sheet), through the OpenAI Batch API with pipeline/imggen.py, then QCs, fixes and accepts them. Use when the master or user asks for panel art, final images, characters in scenes, vignettes or props for comic pages.
---

# Stage 2: final panel art

Work from `/home/akasdh/Desktop/Projects/ComicAgent/Tasks`. Read these first, in order:
1. `LESSONS.md`: *All stages*, *Panel art*, *Maths*.
2. `FInalChangesTask/PANEL-GUIDE.md`: binding. It covers references, sizes, the prompt skeleton, maths-in-art rules, CHECKS and the loop.
3. The chapter's `PdfSheetsGenTask/<CHxx>/pages.json` (only your pages).

## Procedure
1. For your pages, list the panels with `art.kind == "new"` and the `spot_art` not already in `FInalChangesTask/library/` (check its `jobs.json`/`out/`).
2. For each item:
   - Look at the background plate and every character sheet you will attach (Read the images).
   - Read the page's manuscript slice `PdfSheetsGenTask/<CHxx>/src/Pxxx.txt` (staging: moment, cast and positions, props and state progression, view), and grep `manuscript.txt` for the characters' appearance and continuity notes.
   - Write `FInalChangesTask/<CHxx>/prompts/<ID>.md` (`## PROMPT`, `## CHECKS`) and add the item to `FInalChangesTask/<CHxx>/jobs.json`. For spot art, use `FInalChangesTask/library/`, which has its own jobs.json with `"project": "chandrush-library"`.
3. `python3 pipeline/imggen.py --ws FInalChangesTask/<CHxx> check`, then `dry-run` one item per kind.
4. Mode **samples**: `batch build <CHxx>-samples <ID1> <ID2>` → `submit` → `wait` (run_in_background). QC both, then report and stop.
5. Mode **full**: `batch build <CHxx>-<range>-w1 --ready` → submit → wait. QC everything. Queue fixes / regens. `--ready` again for wave 2 + fixes. Repeat until every item is approved or accepted. Use unique batch names.
6. QC each image strictly against its CHECKS. Read the image, then `zoom` faces against the sheets, and hands, counts and inscriptions. Make sure the reserved areas are empty and nothing is lettered.
7. Report to the master: per item the status, path (`FInalChangesTask/<CHxx>/out/<ID>.png`), what was verified, accepted defects, and any panel where the art could mislead the maths. Also report the cost (`imggen.py cost`).

Never use an immediate call. Never use `max`. Never make a 4th call on an item.
