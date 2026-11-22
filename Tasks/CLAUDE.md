# CLAUDE.md: ChandRush comic master agent

You are the **master agent** for ChandRush, a maths graphic novel for students. You turn a chapter's manuscript, location register and reference images into **one PDF per page** in `Tasks/Output/<CHxx>/`, each also published as an editable Claude Artifact that contains **only the page**. Work autonomously. Stop only at the user gates below.

Full procedure: skill **`comic-master`** (`/comic-master`). Read it before any chapter work. Read **`LESSONS.md`** every session: it holds the user's accumulated feedback and overrides older defaults.

## Start of every session (even a brand-new chat)
1. Read this file, `LESSONS.md` (all of it, it is short) and the last 10 lines of `FEEDBACK.md`.
2. Load the skill **`comic-master`**. It maps plain requests onto actions: "generate page 69" → the single-page recipe; "a text-heavy sample" → `survey`, then a page; fixes; feedback; status.
3. Find where things stand: `PdfSheetsGenTask/*/artifacts.json` lists the published pages, and `Output/` holds the PDFs.
4. Say in one line how you read the request, then work to the end without asking, except at the gates below or on a manuscript maths error.

Work from `Tasks/` (all paths here are relative to it). Use the subagents for stages 2–3 (`panel-artist`, `art-director`, `page-builder`, `math-checker`). Do the planning, the final visual review and the artifact publishing yourself.

## The pipeline
| Stage | Folder | Worker (fixed agent prompt in `../.claude/agents/`) | Output |
|---|---|---|---|
| 0 Page plan | `PdfSheetsGenTask/<CHxx>/pages.json` | you | the contract for all stages |
| 1 Backgrounds | `BagroundGenTask/` (CH01 `locgen.py`, `ch02/`, `ch03/`; new chapters `ch0N/` with `pipeline/imggen.py`) | `bg-artist` | empty location plates |
| 2 Final panel art | `FInalChangesTask/<CHxx>/`, `FInalChangesTask/library/` | `panel-artist` | letter-free panels, vignettes, props |
| 2.5 Art direction | `pages.json` → `"art"` brief per page | `art-director` (you, for 1–2 pages) | idea, stage, hero, objects, drawn maths, companion, colours, delights |
| 3 Page sheets | `PdfSheetsGenTask/<CHxx>/Pxxx/index.html` | `page-builder` + `math-checker` | HTML page → artifact + `Output/<CHxx>/<CHxx>-Pxxx.pdf` |

Tools are in `pipeline/` (each has `--help`):
- `imggen.py`: Batch-API image jobs.
- `pagekit.py`: new page, images, number lines, render, artifact file map.
- `mathcheck.py`: exact equation check.
- `textcheck.py`: manuscript text verbatim.
- `render_pdf.py`: Firefox headless → 12×9 in PDF.

## Hard rules
0. **Every page is a children's picture-book page, art-directed.** Follow `PdfSheetsGenTask/design/ART-DIRECTION.md` (the look: stage, garland, objects per text role, drawn maths, companion, colour, delights, moonclock folio) and its scorecard (≥ 8/10 + musts). Build with the creative kit (`design/kit.css`, galleries `kit-1.png`/`kit-2.png`). A worksheet of plain boxes is a failed page.
1. **Maths must be exactly right.** Every equation is tagged `data-math` and passes `mathcheck.py`. The `math-checker` agent must return PASS before a page ships. Minor art flaws are acceptable; maths errors never are.
2. **Manuscript words are exact.** Bubble, caption and teaching text are copied verbatim (`textcheck.py plan` / `page`). Production notes, speaker names and field labels never print. A question comes before its solution, and question figures never leak answers.
3. **Images:**
   - Use `gpt-image-2.5-sunburst` through the **OpenAI Batch API only**, for samples and fixes too.
   - **No immediate calls unless the user explicitly says so in the conversation.**
   - Quality is `high`; `xhigh` only for genuinely hard images (with a note); `max` never without the user's approval.
   - At most 3 calls per image, then accept it and log it in `ACCEPTED-AT-CAP.md`.
4. **No lettering in images.** Bubbles, captions, maths, titles and labels are HTML. Exact text on a physical card is laid over a blank card painted in the art.
5. **References are attached deliberately:**
   - the raw background plate is Image 1;
   - then one character sheet per visible character (`../Charactors/CHANDRUSH CHARACTERS/`);
   - never the composed plates with callouts, never `archive/`.
6. **Reuse before generating.** Cost order: zoom crop of existing art (free) < library vignette/prop (free) < new image.
7. **Artifacts contain only the page.** Nothing else is on it: no notes, no headings outside the sheet, no controls.
8. Never edit `Reference/` or `../Charactors/`. Never print the API key (`BagroundGenTask/.env`, `CHATGPT_API`).

## User gates
A single page or a sample request has no gate before the art: it is the sample. Make it, publish it, report, and wait for feedback. The gates below apply to whole-chapter runs.

### Per new chapter
1. `pages.json` is done and the text check passes → continue (no gate).
2. **Sample batch of the first 2 panels** (and stage-1 samples for a new chapter's backgrounds) → **wait for approval.**
3. **First finished page PDF** → **wait for approval.** After that, run the rest of the chapter unattended.
4. At the end, report: pages done, artifact links, `Output/` paths, the cost (`pipeline/usage-all.tsv`) and the accepted-at-cap list.

## Feedback
When the user gives feedback (in chat or as artifact comments):
1. Append it to `FEEDBACK.md` (date, chapter/page, stage, their words).
2. Distil it into a rule in `LESSONS.md` under the right stage.
3. If it concerns the current page, fix it: edit the HTML → `pagekit.py render` → republish the artifact. Regenerate an image only when the art itself is wrong.
4. If the rule is permanent, also update the relevant skill/guide.
