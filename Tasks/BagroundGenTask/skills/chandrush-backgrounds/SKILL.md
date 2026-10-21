---
name: chandrush-backgrounds
description: Generate, continue, review or fix the ChandRush Chapter 01 location images (Draft 02, 27 numbered records CH01_LOC_001-027) with several parallel image workers. A sample round comes first, then the full set. Works with Codex's built-in image_gen (multi-agent) or Claude with the Higgsfield MCP. Use when asked to make CH01 backgrounds, locations or location images, run the sample round or the full run, review or fix records, or re-import a new location draft. Arguments: samples | run [--workers N] | review | fix <ID> "<problem>" | status | import <docx>.
---

# ChandRush CH01 location images: concurrent skill

**Task folder:** `/home/akasdh/Desktop/Projects/ComicAgent/Tasks/BagroundGenTask`. Run every command there.

**The authority is `CH01-LOCATION-IMAGE-GENERATION-DRAFT-02.docx`.** `python3 bg.py import` turns it into:

| File | What it holds |
|---|---|
| `prompts/CH01-LOC-RECORDS.md` | the 27 records: output name, ratio, target size, references with roles, view, visual state, the complete generation prompt and the image checks |
| `LOCATION-BIBLE.md` | the draft's rules, style, geography and detailed locations |
| `geography-guide.png` | the overhead schematic |
| `REUSE.md` | how every other story moment is made from the 27 images by crops and local edits; these are **not** extra jobs |

`records-meta.json` adds only the workflow layer:
- worker lanes, sample anchors and beat coverage;
- the user's **art direction** (`_style_overlay`): an illustration–reality hybrid, grand, mystic and magical, with real architectural detail;
- per-record **clarifications** (`clarify`).

`bg.py` adds the overlay and clarifications to every composed prompt, so all routes send identical text. Never hand-edit the generated files. Edit the draft or the meta file, then re-import.

`bg.py` is the shared queue:

| Command | Purpose |
|---|---|
| `claim` | atomic: hands one ready job to one worker |
| `done` | keeps the native file, upscales it to the target size and frees the claim |
| `release` | gives a job back |
| `pick` | the user accepts a candidate |
| `status` / `sheet` | progress and contact sheets |
| `zoom` | label and count verification |
| `check` | validation |
| `import` | rebuild from the draft |

A record is accepted when `output/CH01_LOC_<ID>.png` exists.

**Why parallel is safe:**
- Every record references only lower IDs, so the draft's ascending order is respected.
- A record is handed out only when all its reference images are accepted.
- Anchors wait for the user's pick.
- `done` refuses a wrong ratio, and refuses an image identical to another job's.

## Modes

| Argument | What you do |
|---|---|
| `samples` | Sample round (below). STOP for the user's picks. |
| `run [--workers N]` | Full run with N workers (default 4); needs the five sample anchors picked. Pauses once for the 024 pick. |
| `review` | Contact sheets, exact-detail pass and consistency pass (below). |
| `fix <ID> "<problem>"` | A targeted edit of that accepted image. Save the native result over `output/CH01_LOC_<ID>.png`, then `python3 bg.py done <ID> --worker fix --force`. |
| `status` | `python3 bg.py status` (and `--set samples`). |
| `import <docx>` | `python3 bg.py import <docx>`, then `check`. Use for a new draft. |

Before any generation, `python3 bg.py check` must print `check: OK`.

## Hard rules (from Draft 02; every worker, every route)

- **Each ID produces one accepted image** under its exact `CH01_LOC_###.png` name. Candidates are only for anchors. Reuse notes are never generated.
- **The old location pack is never an image input.** Attach only the accepted files the job lists, in order. A filename typed in a prompt is not an image.
- **Style-only references** (e.g. 026 ← 024) control rendering, materials and light only. **Parent references** control geography too.
- **State priority:** the record's visual state and prompt win over whatever state a reference shows.
- **No characters, hands, helpers, captions, arrows or watermarks.**
- **Art direction** (every image): grand, mystic and magical, through atmosphere and craftsmanship only.
  - Never light what the record keeps dark.
  - Exactly one full moon; no crescent or halo ring.
  - No words on signs except the requested labels.
  - Working areas stay clear and sharp.
- **Print only the physical labels the record requests, as exact copy.**
  - Verify every label, grid and count with `zoom`.
  - Fix a wrong label with a targeted lettering edit, at most 2 fixes. If it is still wrong, run `done --note "LETTERING: …"`; it is then corrected by hand at page production.
- **Sizes:**
  - Generate at the largest native size in the record's ratio. `done` keeps the native file and upscales proportionately to 3840×2160 (16:9), 3600×2700 (4:3) or 3600×2400 (3:2).
  - Never stretch. Never crop away required equipment; use `--crop` only when nothing required is lost.
- Never edit the source folders, `prompts/` or the draft during a run. Report honestly.

## The worker loop

Every worker receives `skills/chandrush-backgrounds/WORKER-PROMPT.md` with these placeholders filled:

| Placeholder | Value |
|---|---|
| `{WORKER}` | W1, W2, … |
| `{SET}` | samples or full |
| `{PREFER}` | lane |
| `{ROUTE}` | `Codex built-in image_gen` or `Claude + Higgsfield MCP` |

In short, a worker repeats:
1. claim;
2. look at the refs;
3. generate, or edit when the job says `mode: edit`;
4. save the native result to SAVE AS;
5. zoom-check the labels and counts;
6. make at most 2 fixes;
7. run `done`.

It stops on `ALL DONE`, `WAIT` or `PICK NEEDED`.

**Default lanes for the full run (4 workers):**

| Worker | Lane | Records |
|---|---|---|
| W1 | LB | 003–007 |
| W2 | TB, KB, HR | 009–014 |
| W3 | MR | 016–018, 025 |
| W4 | CP, LS, GT, FS | 020–024, 026, 027 |

Lanes are preferences only; idle workers take any ready job. The chains are short:
- 009 → 010 → 011 / 012 → 013 / 014
- 016 → 017 → 018
- 020 → 021 / 022 → 023
- then 024 → 025 / 026 / 027

Expect `WAIT` between waves. When `status` shows ready jobs again, start the workers again.

## Orchestration

### Codex (built-in image_gen, multi-agent enabled)

- Spawn N worker agents with the filled WORKER-PROMPT.
- For each job, the worker:
  1. uses `view_image` on each reference;
  2. calls `image_gen`; for edit jobs this is edit mode on Image 1, which must be loaded with `view_image` first;
  3. runs `cp "<reported savedPath>" "<SAVE AS>"`.

  Each worker copies only its own savedPath, so there are no races.
- **Fallback:** `bash run_codex_workers.sh N [samples|full]` starts separate `codex exec` workers, with logs in `output/_logs/`.

### Claude Code (Higgsfield MCP)

1. **Probe once, at the start of the sample round:**
   - Find the Higgsfield tools and models. Choose **GPT Image 2**, the closest to the ChatGPT look; Nano Banana Pro is the fallback for edits that drift.
   - Find out:
     - how references are passed: file, upload or URL;
     - the aspect parameter and values (16:9, 4:3, 3:2);
     - the largest size or quality option, including any 4K;
     - the edit capability;
     - the result format.
   - Write the recipe and one exact working call to `HIGGSFIELD-NOTES.md`.
   - Cache uploads with `python3 bg.py urls set|get <path> <url>`.
2. **Workers:** N background sub-agents (Agent tool, `run_in_background: true`) with the filled WORKER-PROMPT, route `Claude + Higgsfield MCP`. They download results with `curl` and check them with Read and `bg.py zoom`.
3. **Fallback if sub-agents can't see the MCP:** run the loop yourself.
   1. Claim up to 4 jobs.
   2. Send their generation calls in **one** message, so they run in parallel.
   3. Download, zoom-check and run `done` for each.
   4. Repeat.
4. Never exceed 1 generation + 2 fixes per job; Higgsfield charges credits.

### ChatGPT web (by hand)

Open one tab per lane. In each tab:
1. Run `python3 bg.py claim --worker TAB1 --set …`.
2. Attach the listed accepted images, paste the prompt and generate.
3. Save the download to SAVE AS.
4. Run `python3 bg.py done <JOB> --worker TAB1`.

## Sample round (`samples`)

1. Run `python3 bg.py check`, then `python3 bg.py status --set samples`.
2. **S1:** 3 workers, `{SET}=samples`. Only **001-A/B/C** are ready (the text-only master).
   1. Run `python3 bg.py sheet --set samples`.
   2. Show the user `output/_sheets/SAMPLES.png`, plus the full-size files in `output/_candidates/`.
   3. Ask them to judge 001 against the draft's geography, style and usable space. **STOP** for `pick 001 <letter>`, or for redo notes.
3. **S2:** run the workers again. Now **002, 008, 015 and 019** are ready, ×2 candidates each: the lift street landing, the timing bench, the mirror alcove and the cube plinth, each built from 001.
   1. Build the sheet again.
   2. Have the user check each against 001.
   3. **STOP** for the four picks. Run `python3 bg.py pick <ID> <letter>` for each.
4. Report that the sample round is complete. Do not start the full run until the user says so.

**Redo:**
1. Move the rejected candidates to `output/_candidates/rejected/`, with the user's OK.
2. Add the user's note to `records-meta.json`, or ask whether the draft prompt should change, then re-import.
3. Run `check`, then claim again.

## Full run (`run`)

1. `python3 bg.py status`: no anchors from the sample round may be unpicked.
2. Start N workers with `{SET}=full` and the default lanes.
3. When **024-A/B** (the restored reverse master) exist, `claim` prints `PICK NEEDED: 024`. Make the sheet (`output/_sheets/CANDIDATES.png`) and **STOP** for the user's pick.
4. After `pick 024 <letter>`, run the workers again for 025, 026 and 027.
5. Continue until `claim` prints `ALL DONE`, then run the review.

## Review (`review`, also at the end of every run)

1. `python3 bg.py sheet` makes `output/_sheets/ALL.png` plus one sheet per lane. Open them.
2. **Exact-detail pass.** Zoom-check:
   - 002, 005, 006, 007: labels and values;
   - 008, 009: interval labels, card and counter;
   - 010, 011: labels, the 3 + 5 parts and the packing slip;
   - 012, 013, 014: cartons, cards and the empty fourth clip;
   - 017: the 9 × 9 grid;
   - 019, 020, 021: label order and the 4 × 4 × 4 cube;
   - 025: one V on the lower-right rim.
3. **Consistency pass.** Check the geography against `geography-guide.png`:
   - lift near-left; bench right (timing at the entrance end); mirror opposite the cube;
   - board and handle on the plinth's right; cover at the front-right corner;
   - moonline on the right edge; reverse view swapped on screen.

   Every state edit must keep its parent's camera.
4. At most 2 `fix` edits per failing record; otherwise add an item to `output/REVIEW-NOTES.md`.
5. **Report:** `status` totals, sheet paths, every REVIEW-NOTES item, and anything not verified.

## Files you may write

- `output/**`
- `HIGGSFIELD-NOTES.md`
- `records-meta.json` (only on the user's instruction)
- the generated files, only via `bg.py import`
