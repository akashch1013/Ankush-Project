---
name: comic-panel-art
description: Stage 2 of the ChandRush comic pipeline. Makes the final letter-free panel illustrations (background plate + characters + action + props), character vignettes and props for planned pages, attaching the right references (raw background plate first, then each visible character's sheet), through the OpenAI Batch API with pipeline/imggen.py, then QCs, fixes and accepts them. Use when the master or user asks for panel art, final images, characters in scenes, vignettes or props for comic pages.
---

# Stage 2: final panel art

Work from the repo's `Tasks/` folder. Read these first, in order:
1. `LESSONS.md`: *All stages*, *Panel art*, *Maths*.
2. `FInalChangesTask/PANEL-GUIDE.md`: binding. It covers references, sizes, the prompt skeleton, maths-in-art rules, CHECKS and the loop.
3. The chapter's `PdfSheetsGenTask/<CHxx>/pages.json` (only your pages).

## Non-negotiables (user, 2026-11-25)
- **The plate's geometry is fixed.** Never add, move, re-angle or reshape a background object (cart, handle, gate, controller) to make a beat work. Stage the characters inside the given plate so the beat happens naturally there; keep the plate's camera direction unless the brief says otherwise.
- **Continuity:** before writing a prompt, look at the previous and next pages' images (`out/`) and plan positions, props and states so nothing jumps.
- **Characters exactly from their sheets.** Attach the sheet of every visible named character, background figures included; never re-imagine from the manuscript description. Tara is always calm and wise (sheet expressions), never animated.
- Reserve calm areas for balloons and captions **inside** the art, exactly where the page brief's `reserve` puts them: they are laid on the image, not in gutters.
- **References from `Tasks/CHANDRUSH CHARACTERS/` via `python3 pipeline/cast.py refs <plate> <names…>`**: plate first, then EVERY visible character's sheet, then the height chart (2+ characters). Never the old `Charactors/` paths.
- **3 calls per image, hard limit** (enforced in imggen.py). Write it right the first time: PANEL-GUIDE §7 checklist, then `promptlint.py` (batch build refuses lint FAILs).

## Modes
- `full`: write, lint, ONE batch for all your items, wait, QC, ONE fix batch per wave.
- `prompts`: write + lint only; mark ready; the master sends one combined batch for every page.
- `qc`: QC the fetched items, queue fixes or regen; don't submit.
- `samples`: the first 2 panels of a new chapter as their own batch; QC and stop.

## Procedure
1. For your pages, list the panels with `art.kind == "new"` and the `spot_art` not already in `FInalChangesTask/library/` (check its `jobs.json`/`out/`).
2. For each item:
   - Look at the background plate and every character sheet you will attach (Read the images).
   - Read the page's manuscript slice `PdfSheetsGenTask/<CHxx>/src/Pxxx.txt` (staging: moment, cast and positions, props and state progression, view), and grep `manuscript.txt` for the characters' appearance and continuity notes.
   - Write `FInalChangesTask/<CHxx>/prompts/<ID>.md` (`## PROMPT`, `## CHECKS`) and add the item to `FInalChangesTask/<CHxx>/jobs.json`. For spot art, use `FInalChangesTask/library/`, which has its own jobs.json with `"project": "chandrush-library"`.
3. `python3 pipeline/imggen.py --ws FInalChangesTask/<CHxx> check`, then `python3 pipeline/promptlint.py --ws FInalChangesTask/<CHxx> <ids>` until there is no FAIL, then `dry-run` one item per kind.
4. Mode **samples**: `batch build <CHxx>-samples <ID1> <ID2>` → `submit` → `wait` (run_in_background). QC both, then report and stop.
5. Mode **full**: `batch build <CHxx>-<range>-w1 --ready` (every ready item of every page in ONE batch) → submit → wait in the background. QC everything. Queue fixes or regens. `--ready` again builds ONE wave-2 batch with all the fixes and wave-2 items. Stop at the 3-call cap. Use unique batch names. In mode **prompts**, stop after step 3 (prompts + lint) and report the ready ids.
6. QC each image strictly against its CHECKS. Read the image, then `zoom` faces against the sheets, and hands, counts and inscriptions. Make sure the reserved areas are empty and nothing is lettered.
7. Report to the master: per item the status, path (`FInalChangesTask/<CHxx>/out/<ID>.png`), what was verified, accepted defects, and any panel where the art could mislead the maths. Also report the cost (`imggen.py cost`).

Never use an immediate call. Never use `max`. Never make a 4th call on an item.
