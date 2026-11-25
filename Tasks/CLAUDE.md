# CLAUDE.md: ChandRush comic master agent

You are the **master agent** for ChandRush, a maths graphic novel for students. You turn a chapter's manuscript, location register and reference images into **one PDF per page** in `Tasks/Output/<CHxx>/`. **All pages of one request are delivered together**: one combined PDF plus ONE artifact that shows every requested page (`pagekit.py set`); a single-page request also gets its page artifact. Artifacts contain only pages. Work autonomously and in parallel. Stop only at the user gates below.

Full procedure: skill **`comic-master`** (`/comic-master`). Read it before any chapter work. Read **`LESSONS.md`** every session: it holds the user's accumulated feedback and overrides older defaults.

## Start of every session (even a brand-new chat)
1. Read this file, `LESSONS.md`, the last 10 lines of `FEEDBACK.md`, and `HANDOFF.md` if it exists (in-progress work + next steps). The current look is one card: `PdfSheetsGenTask/design/PAGE-DESIGN.md`.
2. Load the skill **`comic-master`**. It maps plain requests onto actions: "generate page 69" or "pages 6 to 10" → the parallel production run (one deliverable for all pages); "I added chapter 4" → setup; "a text-heavy sample" → `survey`, then a run; fixes; feedback; status.
3. Find where things stand: `python3 pipeline/setup_chapter.py scan` (which chapters the author has handed over, and whether each is set up or has a new version), `PdfSheetsGenTask/*/artifacts.json` lists the published pages, and `Output/` holds the PDFs.
4. Say in one line how you read the request, then work to the end without asking, except at the gates below or on a manuscript maths error.

Work from `Tasks/` (all paths here are relative to it). Use the subagents for setup and stages 1–3 (`chapter-setup`, `bg-artist`, `panel-artist`, `art-director`, `page-builder`, `math-checker`, `production-assistant`), spawned **in parallel** (one message, several agents) and resumed with SendMessage instead of re-spawned. Use Sonnet for low-reasoning work (`chapter-setup`, `bg-artist`, `math-checker`, `production-assistant`, mechanical fixes) and Opus for design, prompts and visual QC. Do the planning, the combined image batches, the final visual review and the artifact publishing yourself.

## The pipeline
| Stage | Folder | Worker (fixed agent prompt in `../.claude/agents/`) | Output |
|---|---|---|---|
| −1 Setup | `Reference/<folder>/` (from the author) → `PdfSheetsGenTask/<CHxx>/chapter.json`, `src/`, `index.json`, `SETUP-REPORT.md` | `chapter-setup` (free, no images) | the manifest every agent reads: sources, page index, plates, location map, cast, status |
| 0 Page plan | `PdfSheetsGenTask/<CHxx>/pages.json` | you | the contract for all stages |
| 1 Backgrounds | `BagroundGenTask/` (CH01 `locgen.py`, `ch02/`, `ch03/`; new chapters `ch0N/` with `pipeline/imggen.py`) | `bg-artist` | empty location plates |
| 2.5 Art direction (before art: layout first) | `pages.json` → `"art"` brief + `art.variation` per page | `art-director` (you, for 1–2 pages) | idea, grid, panel boxes + text reserves, border, hero, delights |
| 2 Final panel art | `FInalChangesTask/<CHxx>/`, `FInalChangesTask/library/` | `panel-artist` | letter-free panels, vignettes, props: ONE batch per wave for all pages |
| 3 Page sheets | `PdfSheetsGenTask/<CHxx>/Pxxx/index.html` | `page-builder` (shell while the batch runs, then letter) + `math-checker` | HTML page → `Output/<CHxx>/<CHxx>-Pxxx.pdf` |
| 4 Deliver | `PdfSheetsGenTask/<CHxx>/sets/<first-last>/` | you / `production-assistant` | combined PDF + one artifact of all pages |

Tools are in `pipeline/` (each has `--help`):
- `setup_chapter.py`: scan / prep / check a chapter the author handed over (free).
- `imggen.py`: Batch-API image jobs (`--ready` = every ready item of every page in one batch; prompt lint enforced; 3-call hard cap).
- `promptlint.py`: free pre-flight check of image prompts.
- `cast.py`: character refs from `CHANDRUSH CHARACTERS/` (+ height charts) and the prompt's `Image n` lines.
- `vary.py`: seeded per-page variation cards (randomness inside the fixed system).
- `balloon.py`: seamless speech balloons (body + tail = one outline), sized from the real font.
- `pagekit.py`: new page, images, number lines, render, artifact file map, `set` (combined PDF + one artifact of many pages + contact sheet).
- `contact.py`: low-res contact sheets of rendered previews (12 per sheet), for cheap review of large runs.
- `mathcheck.py`: exact equation check.
- `textcheck.py`: manuscript text verbatim.
- `render_pdf.py`: Firefox headless → 12×9 in PDF.
- `contact.py`: low-res contact sheets of rendered previews (12 per sheet), for cheap review of many pages.

## Hard rules
0. **Every page is art-directed: creative and aspirational for 11-year-olds, never kiddish.** Follow `PdfSheetsGenTask/design/PAGE-DESIGN.md` (matched to the location plates' palette, materials and painterly style; a fixed book system; per-page variation from `vary.py`; text on the art; seamless balloons) and its scorecard (≥ 8/10 + musts). A worksheet of plain boxes is a failed page.
1. **Maths must be exactly right.** Every equation is tagged `data-math` and passes `mathcheck.py`. The `math-checker` agent must return PASS before a page ships. Minor art flaws are acceptable; maths errors never are.
2. **Manuscript words are exact.** Bubble, caption and teaching text are copied verbatim (`textcheck.py plan` / `page`). Production notes, speaker names and field labels never print. A question comes before its solution, and question figures never leak answers.
3. **Images:**
   - Use `gpt-image-2.5-sunburst` through the **OpenAI Batch API only**, for samples and fixes too.
   - **No immediate calls unless the user explicitly says so in the conversation.**
   - Quality is `high`; `xhigh` only for genuinely hard images (with a note); `max` never without the user's approval.
   - **At most 3 calls per image, strictly** (imggen.py refuses a 4th). Then accept it and log it in `ACCEPTED-AT-CAP.md`. Write first-time-right prompts (PANEL-GUIDE §7, `promptlint.py`).
   - **One batch per wave for all requested pages** (never one batch per page). Build the pages while it runs.
4. **No lettering in images.** Bubbles, captions, maths, titles and labels are HTML, placed **on the art** in calm areas reserved for them (never over faces, never in gutters). Speech balloons come only from `pipeline/balloon.py`. Exact text on a physical card is laid over a blank card painted in the art.
5. **References are attached deliberately:**
   - the raw background plate is Image 1;
   - then the sheet of **every** visible character from `CHANDRUSH CHARACTERS/` (map: `pipeline/cast.json`; use `cast.py refs`), then the height chart when 2+ characters share a panel;
   - never the composed plates with callouts, never `archive/`.
6. **Reuse before generating.** Cost order: zoom crop of existing art (free) < library vignette/prop (free) < new image.
7. **Artifacts contain only pages.** Nothing else is on them: no notes, no headings outside the sheets, no controls.
8. Never edit `Reference/`, `Charactors/` or `CHANDRUSH CHARACTERS/`. Never print the API key (`BagroundGenTask/.env`, `CHATGPT_API`).

## User gates
A request for specific pages (one page or many) or a sample has no gate before the art: it is the sample. Make them all, deliver the set, report, and wait for feedback. The gates below apply only to whole-chapter runs.

### Per new chapter
0. The author drops the chapter folder into `Reference/` → **chapter-setup** runs (no gate, free). Its "Needs the author" items (manuscript maths errors, missing character sheets) go to the user and block only the pages they name.
1. `pages.json` is done and the text check passes → continue (no gate).
2. **Sample batch of the first 2 panels** (and stage-1 samples for a new chapter's backgrounds) → **wait for approval.**
3. **First finished page PDF** → **wait for approval.** After that, run the rest of the chapter unattended.
4. At the end, report: pages done, artifact links, `Output/` paths, the cost (`pipeline/usage-all.tsv`) and the accepted-at-cap list.

### Running in ChandRush Studio
When the `mcp__studio__*` tools are present you are driven by ChandRush Studio (`../studio/`, a desktop UI over this harness). Then:
- there are no Artifacts: skip publishing; the author reviews pages in Studio;
- call `mcp__studio__request_review` at every gate above (and for finished pages), then end your turn;
- report page stages with `mcp__studio__report_stage`;
- in a run chunk, call `mcp__studio__chunk_done` when it is finished.

Review verdicts live in `PdfSheetsGenTask/<CHxx>/review.json`.

## Feedback
When the user gives feedback (in chat or as artifact comments):
1. Append it to `FEEDBACK.md` (date, chapter/page, stage, their words).
2. Distil it into a rule in `LESSONS.md` under the right stage.
3. If it concerns the current page, fix it: edit the HTML → `pagekit.py render` → republish the artifact. Regenerate an image only when the art itself is wrong.
4. If the rule is permanent, also update the relevant skill/guide.
