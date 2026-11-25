# Spawn prompts: how the master briefs each worker

Every worker already has a fixed prompt (`.claude/agents/<name>.md`) and a skill, so they know the rules. A spawn prompt only has to give them what is **specific to this job**, and make it vivid enough that the model aims high. Give paths, never pasted file contents. Ask for a short report.

Each spawn prompt has five parts:
1. **Job:** chapter, pages, mode and paths.
2. **The moment:** one or two sentences on what the reader should feel on these pages.
3. **Freedom:** what the worker may invent.
4. **Fixed:** only this run's specifics. Don't restate the rules.
5. **Report:** the contract.

Spawn independent workers **in one message** (several Agent calls) so they run in parallel. To continue a worker that already holds the context, use **SendMessage to the same agent** instead of spawning a fresh one. It skips re-reading every document.

## Models (cost/speed)
| Worker | Model | Why |
|---|---|---|
| art-director | opus | creative judgement |
| panel-artist | opus | staging prompts + visual QC |
| page-builder (build/shell/letter) | opus | design + vision |
| page-builder (mechanical fix: swap art, move a balloon by N pt, text typo) | `model: "sonnet"` override | low reasoning |
| math-checker | sonnet (default in its file) | exact checks, scripted; one spawn checks up to 10 pages |
| chapter-setup, bg-artist | sonnet (default in their files) | scripted prep / register-driven plates |
| production-assistant | sonnet (default in its file) | render, set, publish prep, status, batch fetch |

## art-director, mode brief
```
Mode: brief. Chapter <CHxx>, pages <Pxxx-Pyyy>. pages.json: Tasks/PdfSheetsGenTask/<CHxx>/pages.json
(each page already has art.variation from vary.py; neighbours' briefs are in the same file).
The moment: <e.g. "the crew enters the dead street; P006 is quiet dread, P007 the first spark of the mystery">.
Freedom: choose each page's idea, hero, grid within the variation card, border from the location's own materials,
2–3 delights. Surprise me: no two pages may feel like the same template, while the book system stays fixed.
Layout first: finalise every panel's box (pt) and text reserves (use balloon.py --measure) before art is made,
and list exactly which panels need new art (kind new) vs zoom/reuse/plate.
Report (≤ 12 lines): one line per page: idea · hero · grid · border · delights · new-art ids.
```

## panel-artist, mode prompts (big runs; the master submits the combined batch)
```
Mode: prompts. Chapter <CHxx>, items <P006-1, P006-2, P007-1 …> (scene: <name>). pages.json: <path>.
The moment: <what the reader must feel/see in these panels>.
Write prompts + CHECKS for every item, add them to FInalChangesTask/<CHxx>/jobs.json with refs from
pipeline/cast.py (plate, every visible character's sheet, height chart), run promptlint until no FAIL.
Do NOT build or submit a batch: the master sends one combined batch for all pages.
Report: item ids ready, any lint warnings you kept and why, any panel you think is risky.
```
Then **mode qc** (resume the same agent with SendMessage when the batch is fetched):
```
Batch <name> is fetched. QC your items <ids> against their CHECKS (Read + zoom), qc pass / queue fix / --regen.
Do NOT submit; I send one combined wave-2 batch. Report: per item pass | fix queued (what) | regen | accepted-at-cap.
```

## panel-artist, mode full (small runs, ≤ 8 new images in total)
```
Mode: full. Chapter <CHxx>, items <ids>. pages.json: <path>. Write, lint, ONE batch for all of them, wait in the
background, QC, one combined fix batch per wave, at most 3 calls per image. Report per item + cost.
```

## page-builder, mode shell (runs WHILE the art batch is out)
```
Mode: shell. Chapter <CHxx>, pages <P006, P007>. pages.json: <path>. Final art is not back yet.
Build each page completely from its brief: grid at the briefed boxes, border from this location, captions, maths SVG,
running head, folio, and balloons via balloon.py at the briefed reserves. For each new-art panel place a placeholder
under its final asset name (pagekit.py img <page_dir> <plate> <ID>), so the swap later is one command.
The moment: <…>. Freedom: everything the brief leaves open; beat the brief if you can.
Render once, fix layout. Report: page dirs, open questions, score.
```
Then **mode letter** (resume the same agent with SendMessage once a page's art is approved):
```
Art for <P006> is approved: FInalChangesTask/<CHxx>/out/<ids>.png (QC notes: imggen.py status).
Swap it in (pagekit.py img), then re-letter on the REAL art: balloons on calm areas, tails 4–8 pt short of
each mouth, captions off faces. Render, run textcheck, score ≥ 8/10. Report: preview path + score + issues.
```

## math-checker
```
Check <CHxx> <P006 P007 P008 …> (up to 10): PdfSheetsGenTask/<CHxx>/<Pxxx>/ (index.html, preview.png).
Return one block per page (PASS or fix list), then `batch: <n> PASS, <n> FAIL`.
```
One spawn per group of ≤ 10 pages; several groups in one message.

## production-assistant
```
Task: <e.g. "pages P006–P010 of CH01 are final: build the set (pagekit.py set CH01 P006-P010), artifact files for
each page if asked, update artifacts.json, and report the publish arguments + contact sheet path">.
```
