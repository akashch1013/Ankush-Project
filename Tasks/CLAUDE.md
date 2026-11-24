# ChandRush: shared rules for every agent

ChandRush is a maths graphic novel for 11-year-olds. Each manuscript page becomes one 12×9 in PDF in `Output/<CHxx>/` (plus a page-only Artifact). Paths here are relative to `Tasks/`.

This file is loaded automatically: don't re-read it. Your role's procedure is in your agent prompt and skill; the master's (planning, spawning, gates, review, publishing, feedback, Studio) is the `comic-master` skill. User feedback rules: `LESSONS.md`. Print only your part with the command at its top.

## Where things are
- `Reference/<folder>/`: the author's manuscript, location register, reference images (read-only).
- `Charactors/CHANDRUSH CHARACTERS/`: character sheets (read-only).
- `PdfSheetsGenTask/<CHxx>/`: `chapter.json` (manifest: every path), `src/Pxxx.txt`, `index.json`, `pages.json` (the plan), `Pxxx/index.html` + `preview.png`, `artifacts.json`, `review.json`.
- `PdfSheetsGenTask/design/`: `ART-DIRECTION.md` (A4 "Step Inside" + approved B1 note), `kit.css`, `base.css`, `manual-v09.md`, `patterns.md`. Old A3 kit is archived in `design/archive-a3/`.
- `BagroundGenTask/`: stage-1 location plates (`out/plates/`, `ch02/`, `ch03/`).
- `FInalChangesTask/<CHxx>/`, `FInalChangesTask/library/`: stage-2 panel art, reusable vignettes/props; `PANEL-GUIDE.md`.
- `pipeline/` (each has `--help`): `setup_chapter.py`, `imggen.py` (Batch images), `pagekit.py` (build/render/artifact), `mathcheck.py`, `textcheck.py`, `render_pdf.py`, `contact.py` (contact sheets); cost in `usage-all.tsv`.
- `FEEDBACK.md`: the user's raw words (master appends).

## Hard rules
0. Every page is art-directed per `PdfSheetsGenTask/design/ART-DIRECTION.md` and its scorecard (≥ 8/10 + musts): creative and aspirational for 11-year-olds, never kiddish, never a worksheet of plain boxes.
1. Maths is exactly right: every equation tagged `data-math`, passes `mathcheck.py`, math-checker PASS before shipping. Minor art flaws are acceptable; maths errors never.
2. Manuscript words are verbatim (`textcheck.py`). Production notes, speaker names and field labels never print. A question precedes its solution; question figures never leak answers.
3. Images: `gpt-image-2.5-sunburst` via the OpenAI Batch API only (samples and fixes too). No immediate calls unless the user says so in this conversation. Quality `high`; `xhigh` only for genuinely hard images (with a note); `max` never without the user. At most 3 calls per image, then accept and log in `ACCEPTED-AT-CAP.md`.
4. No lettering in images: bubbles, captions, maths, titles, labels are HTML. Exact text on a physical card goes over a blank painted card.
5. References: raw background plate is Image 1, then one sheet per visible character from `Charactors/CHANDRUSH CHARACTERS/`; never composed plates with callouts, never `archive/`.
6. Reuse before generating: zoom crop (free) < library vignette/prop (free) < new image.
7. Artifacts contain only the page: no notes, headings or controls.
8. Never edit `Reference/` or `Charactors/`. Never print the API key (`BagroundGenTask/.env`, `CHATGPT_API`).

## Gates (whole-chapter runs only)
A single page or sample request has no gate: it is the sample. A chapter run waits for the user after the 2-panel sample batch (and new-chapter background samples) and after the first finished page; details in `comic-master`.
