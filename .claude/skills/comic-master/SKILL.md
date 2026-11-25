---
name: comic-master
description: Master agent for the ChandRush maths comic. Turns a chapter's panelized manuscript, location register and character references into finished, creatively art-directed graphic-novel pages (Tasks/Output/CHxx/CHxx-Pxxx.pdf). Any number of pages is produced in one parallel run, delivered together as ONE combined PDF plus ONE artifact showing every requested page. It runs the bg-artist, panel-artist, art-director, page-builder, math-checker and production-assistant subagents, with one Batch-API image batch per wave for all pages. Also records user feedback into LESSONS.md. Use when asked to make, continue, check, fix or give feedback on comic pages or chapters. Arguments: page <CHxx> <Pxxx>[-Pyyy] | sample <story|story+math|math-heavy|text-heavy|teaching> [CHxx] | plan <CHxx> [pages] | run <CHxx> [pages] | status <CHxx> | fix <CHxx> <Pxxx> "<problem>" | feedback "<text>". Plain-language requests ("generate page no 69", "make pages 6 to 10", "make a text heavy sample", "change the colour of page 39 to teal") map onto these.
---

# ChandRush master agent

Work from `/home/akasdh/Desktop/Projects/ComicAgent/Tasks`. At the start of every session, read:
- `CLAUDE.md` (hard rules);
- `LESSONS.md`;
- the last 10 lines of `FEEDBACK.md`;
- `HANDOFF.md`.

The look is defined by **`PdfSheetsGenTask/design/PAGE-DESIGN.md`**: one card that holds every user decision. Workers read that card, not the old stack of design documents.

**The user writes one plain line. You turn it into finished pages.** Say your reading in one line ("Reading this as: CH01 P006–P010, full production run"), then work to the end without asking, except on a manuscript maths error or a whole-chapter gate.

## Request map
| User says | Action |
|---|---|
| "generate page 69", "pages 40 to 45", "next 5 pages", "P006-P010" | **run** `<CHxx> <pages>`: the production run below (1 page or 50, same recipe) |
| "a text heavy sample", "a story sample", "a math heavy page" | **sample**: `textcheck.py survey … --kind <kind>`, pick the best showcase page not yet built, then **run** it |
| "do chapter 2", "continue the chapter" | **plan** + **run** with the two chapter gates (CLAUDE.md) |
| "change colour / move bubble / typo on page 39" | **fix** |
| "from now on …", "I don't like …", "always …" | **feedback** (and fix the current pages if it applies) |
| "ok / approved / looks good" | continue past the gate; log the approval in FEEDBACK.md |
| "where are we", "cost so far" | **status** |

- Chapter missing? Use the last one worked on (`artifacts.json`, the end of FEEDBACK.md).
- Page ids are the manuscript's ids (`CH01-PAGE069` → `P069`). Never renumber.
- A page that already exists is rebuilt or fixed in place.

## The production run (any number of pages): parallel by design
Time is spent waiting on the image batch. Plan so everything else happens **during** that wait, and send every image of every page in **one batch per wave**.

```
lane A (you)            1 plan ─ 2 briefs ─────────────── 4 batch w1 ── 6 batch w2/w3 ─────── 9 review ─ 10 deliver
lane B (panel-artists)                  3 prompts (∥) ─────────────── 5 QC (∥) ─ fixes ─┘
lane C (page-builders)                                  5' shells (∥, while w1 runs) ── 7 letter on real art (∥)
lane D (math-checkers)                                                                   8 check each page (∥)
```

1. **Plan (you).**
   - If `src/` is missing, run stage-0 source prep (below).
   - Write or replace a `pages.json` entry for **every** requested page (`references/pages-schema.md`; manuscript pagination is the authority).
   - Run `textcheck.py plan` until it passes, and recompute every equation. A manuscript maths error → stop and ask.
   - Run `python3 pipeline/vary.py <CHxx> <pages> --write`. This gives each page its seeded variation card: the randomness inside the fixed system.
   - Read the pages before and after for continuity.
2. **Briefs (layout first).**
   - For 1–2 pages, write the `art` brief yourself.
   - Otherwise spawn **art-director** agents (≤ 6 pages each) **in one message**.
   - Every brief fixes each panel's `box` and text `reserve` (sized with `balloon.py --measure`), lists the new-art panels and spot art, and uses reuse/zoom/plate wherever it can.
3. **Prompts (parallel).** Collect every `kind: new` item across all pages.
   - **≤ 8 images in total:** one **panel-artist**, mode `full`.
   - **More than 8:** **panel-artist** agents by scene (≤ 8 items each), mode `prompts`, all spawned in one message. Each writes the prompts, attaches refs with `pipeline/cast.py` (plate + every visible character's sheet from `CHANDRUSH CHARACTERS/` + the height chart) and lints them. It does not submit.
4. **One combined batch (you).**
   - Run `imggen.py --ws FInalChangesTask/<CHxx> batch build <CHxx>-<run>-w1 --ready`. Every ready item of every page goes in this one batch; lint FAILs are refused automatically.
   - Then `submit`, then `batch wait` with `run_in_background`. Don't poll.
5. **While the batch runs:**
   - Spawn **page-builder** agents (≤ 3 pages each), mode `shell`, in one message. They build the full pages with placeholder art under the final asset names.
   - Pages with no new art go straight to build + letter.
   - When the batch is fetched, resume each panel-artist with **SendMessage** (mode `qc`). They pass items, queue fixes or regen.
6. **Waves 2–3 (you).** Run one combined `--ready` batch for all fixes and wave-2 items. That makes 3 calls per image at most, a cap enforced in code. After the 3rd call, an item is accepted and logged.
7. **Letter on the real art.** As soon as **one page's** art is all approved, resume that page's page-builder with SendMessage (mode `letter`): swap, re-letter, render. Pages flow independently. Don't wait for the slowest page.
8. **Maths.** Spawn one **math-checker** per rendered page, in parallel. On FAIL, send the list to that page's builder with SendMessage, and repeat until PASS.
9. **Review (you).**
   - Run `python3 pipeline/pagekit.py set <CHxx> <pages>` and read the single `contact.png`.
   - Open a page's `preview.png` only where something looks wrong.
   - Check against the PAGE-DESIGN scorecard: musts + ≥ 8/10, varied neighbours, seamless tails, text on the art, no faces covered.
   - For more than 6 pages, spawn **art-director** mode `review` on the contact sheet.
   - Send fix lists to the builders with SendMessage.
10. **Deliver.**
    - `pagekit.py set` writes **one combined PDF** (`Output/<CHxx>/<CHxx>-<first>-<last>.pdf`, lossless join) and **one artifact** showing every requested page. Publish it with the printed arguments. Call the Artifact tool's `quickstart` once per session first.
    - A single-page request also gets its page artifact (`pagekit.py artifact`). For multi-page runs, make per-page artifacts only if the user asks. An existing page artifact is republished to its URL.
    - Record the URLs in `artifacts.json` (set entries under `"SET-<first>-<last>"`), update `HANDOFF.md`, then report.

Spawn prompts, the model per worker, and the SendMessage resume pattern are in **`references/spawn-prompts.md`**. Use those templates: they give each worker the moment, the freedom and the contract, which gets the most creative output.

### Token and time budget
- Workers read `PAGE-DESIGN.md` + their skill + only the LESSONS rules dated after the card. Give paths, never pasted content. Ask for reports of ≤ 15 lines.
- Use **sonnet** for low-reasoning work: math-checker, production-assistant, and page-builder with `model: "sonnet"` for mechanical fixes. Use **opus** for briefs, prompts, visual QC, page design and lettering.
- Continue an agent (SendMessage) instead of spawning a new one whenever it already holds the context.
- Reuse first: zoom crops, library cut-outs and plates are free. Never send a batch per page.

## Report (end of every run)
```
CH01 Pages 6–10: <one line per page: content · idea>
Set:       https://claude.ai/artifact/…  (all pages in one view; private)
PDF:       Tasks/Output/CH01/CH01-P006-P010.pdf  (+ one PDF per page in the same folder)
Checks:    textcheck OK ×5 · math-checker PASS ×5 · scorecard 8–9/10
Art:       12 new images in 2 batches (w1 12, w2 3 fixes) · 1 accepted-at-cap (P008-2: …)
Cost:      $x.xx this run (pipeline/usage-all.tsv)
Notes:     judgement calls, anything the user should look at
```

## Stage 0: source prep and planning (you)
1. Prepare the sources:
   - `python3 pipeline/textcheck.py dump "<manuscript docx>" PdfSheetsGenTask/<CHxx>/manuscript.txt`;
   - the same for the register (`register.txt`);
   - `textcheck.py pages "<manuscript docx>" PdfSheetsGenTask/<CHxx>/src/`, which writes one file per page plus `_common.txt` (read that once);
   - `textcheck.py survey PdfSheetsGenTask/<CHxx>/src`.

   Read one `src/Pxxx.txt` at a time, never the whole dump. Inputs are in `Reference/<chapter folder>/`: `Chap1 Corrected` (CH01, manuscript V06), `Chap 2`, `Chap3`.
2. One `pages.json` page per manuscript page, with its panels in order:
   - **print fields:** `CaptionCopy`, `DialogueCopy`, `SurfaceCopy`, `Equation`, `WorkedStep`, `Question`, `MathExample`, `AnswerLead`, `Caption`, `TeacherBridge`;
   - **staging, never printed:** everything labelled production, metadata or context.
3. Map each panel to an approved plate (`BagroundGenTask/out/plates/`, `ch02/`, `ch03/`). List characters, action, props and states; the text reserves come in step 2.
4. Teaching-only pages still get life: a companion with an existing `asides` line, or a silent library cut-out. Never invent dialogue. Figures named by a `Production note Vnn` are HTML/SVG diagrams, not images.

## Backgrounds (bg-artist)
CH01–CH03 plates are all approved; skip this stage unless a view is missing. For a new chapter, spawn **bg-artist** with the register and record list. Its 2-plate sample batch → user gate → full batch.

## fix <CHxx> <Pxxx> "<problem>"
- **Text, layout, colour, balloon or maths:** the page's builder edits the generator or `index.html` (spawn with `model: "sonnet"` if it is mechanical), then `pagekit.py render`. If maths changed, run math-checker. Republish the page (and the set it belongs to, if any).
- **Art:** `imggen.py fix <ID> "<one precise change>"`, then a batch. Respect the cap: the 4th call doesn't exist. Then swap, re-render and republish.
- **Artifact comments:** read them with ArtifactComments. Each comment is a fix request plus feedback.

## feedback "<text>"
1. Append it to `FEEDBACK.md` (date · page · stage · their words).
2. Add a dated rule to `LESSONS.md` under the right stage.
3. If it changes the look, **edit `PAGE-DESIGN.md`** too (keep it the single current card) and bump its date.
4. Apply it to the current pages.
5. Workflow preferences also go to memory.

## status <CHxx>
Report:
- pages planned / art approved / rendered / math PASS / published (`pages.json`, `imggen.py status`, `Output/`, `artifacts.json`);
- cost (`pipeline/usage-all.tsv`);
- anything waiting on the user;
- any batch still out (`imggen.py batch list`).

## Tools (each has `--help`; all in `Tasks/pipeline/`)
| Tool | What it does |
|---|---|
| `imggen.py` | Batch-API images. `--ready` = all pages in one batch. Lint enforced, 3-call hard cap. |
| `promptlint.py` | Free pre-flight check of prompts |
| `cast.py` | Ref lists and `Image n` lines from `CHANDRUSH CHARACTERS/` |
| `vary.py` | Per-page variation cards |
| `balloon.py` | Seamless balloons (one outline body + tail; sized from the real font) |
| `pagekit.py` | `new`, `img`, `render`, `artifact`, `set` (combined PDF + one artifact for many pages + contact sheet) |
| `textcheck.py` | Exact manuscript text |
| `mathcheck.py` | Exact equations |
