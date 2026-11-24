---
name: comic-panel-art
description: Stage 2 of the ChandRush comic pipeline. Makes the final letter-free panel illustrations (background plate + characters + action + props), character vignettes and props for planned pages, attaching the right references (raw background plate first, then each visible character's sheet), through the OpenAI Batch API with pipeline/imggen.py, then QCs, fixes and accepts them. Use when the master or user asks for panel art, final images, characters in scenes, vignettes or props for comic pages.
---

# Stage 2: final panel art

Work from `/home/abhay/F/Freelance/Ankush-Project/Tasks` (every path below is relative to it). Read these first, in order:
1. `LESSONS.md`: *All stages*, *Panel art*, *Maths*.
2. `FInalChangesTask/PANEL-GUIDE.md`: binding. It covers references, sizes, the prompt skeleton, maths-in-art rules, CHECKS and the loop.
3. Only your pages' entries of `PdfSheetsGenTask/<CHxx>/pages.json`, never the whole file:
   `python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(json.dumps([p for p in d['pages'] if p['page'] in sys.argv[2:]],indent=1))" PdfSheetsGenTask/<CHxx>/pages.json P039 P040`

**Character sheets** are `Charactors/CHANDRUSH CHARACTERS/<NAME> CHARACTER SHEET.png` for AHANA, NAVYA, TARA, TEZ, VIHAAN (e.g. `Charactors/CHANDRUSH CHARACTERS/AHANA CHARACTER SHEET.png`). Write refs in `jobs.json` exactly like that. There is no `Charactors` folder above `Tasks/`; if a path in another file points there, use this one instead. `ls "Charactors/CHANDRUSH CHARACTERS"` once if unsure, never retry a missing path.

**Image budget.** Read an image only when you must judge it. Prefer one contact sheet over many images. Never re-read an image already in your context.
- Plates and character sheets are *attached* to the request by `jobs.json` refs; you do not need to Read them to attach them. Read a plate only when you must judge something specific (free space, screen sides, where a prop sits), and a sheet only when you must judge an identity detail the manuscript text doesn't give. At most once each per session.

## Procedure
1. For your pages, list the panels with `art.kind == "new"` and the `spot_art` not already in `FInalChangesTask/library/` (check its `jobs.json`/`out/` by name, without opening the images).
2. For each item:
   - Read the page's manuscript slice `PdfSheetsGenTask/<CHxx>/src/Pxxx.txt` (staging: moment, cast and positions, props and state progression, view).
   - For appearance and continuity, grep `manuscript.txt` narrowly (it is large): `grep -n -m 5 -i "<name or prop>" PdfSheetsGenTask/<CHxx>/manuscript.txt | cut -c1-300`. Never Read or `cat` it whole.
   - Write `FInalChangesTask/<CHxx>/prompts/<ID>.md` (`## PROMPT`, `## CHECKS`) and add the item to `FInalChangesTask/<CHxx>/jobs.json`. For spot art, use `FInalChangesTask/library/`, which has its own jobs.json with `"project": "chandrush-library"`.
3. `python3 pipeline/imggen.py --ws FInalChangesTask/<CHxx> check`, then `dry-run` one item per kind.
4. Mode **samples**: `batch build <CHxx>-samples <ID1> <ID2>` → `submit` → wait (below). QC both, then report and stop.
5. Mode **full**: `batch build <CHxx>-<range>-w1 --ready` → submit → wait. QC everything. Queue fixes / regens. `--ready` again for wave 2 + fixes. Repeat until every item is approved or accepted. Use unique batch names.
6. **Waiting.** Start ONE `python3 pipeline/imggen.py --ws FInalChangesTask/<CHxx> batch wait <name>` with `run_in_background`, then end your turn; its completion notification wakes you (it fetches the results itself). Never poll with `sleep`, `pgrep`, `until`, `timeout`, Monitor loops or repeated `batch status`.
7. **QC** each new image strictly against its CHECKS:
   - Look at the batch's new outputs on one QC/contact sheet: use the sheet the fetch prints if there is one, otherwise make it with `montage -label '%t' FInalChangesTask/<CHxx>/out/<ID1>.png FInalChangesTask/<CHxx>/out/<ID2>.png … -geometry 768x+8+8 -tile 3x FInalChangesTask/<CHxx>/batches/<batch>/qc.jpg` and Read that one file.
   - `zoom` only the items or details that look wrong or that a CHECK needs close up (faces vs the sheet, hands, counts, inscriptions, reserved empty areas, no lettering). Don't open each full image as well.
   - After a fix wave, QC only the re-generated/fixed items; approved items are not re-checked.
8. Report to the master: per item the status, path (`FInalChangesTask/<CHxx>/out/<ID>.png`), what was verified, accepted defects, and any panel where the art could mislead the maths. Also report the cost (`imggen.py cost`).

Never use an immediate call. Quality `high`; never use `max`. Never make a 4th call on an item: at 3 calls, `accept <ID> --note "<defect>"`.
