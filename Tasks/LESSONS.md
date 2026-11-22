# LESSONS: rules learned from the user's feedback

Every agent reads its own section before working. The master adds a dated rule here after each piece of feedback (raw words go to FEEDBACK.md). Newer rules override older ones and any default in a skill or guide.

## All stages
- 2026-10-27 · Image quality is `high` by default and `xhigh` only for genuinely hard images. `max` is never used without asking ("max is too much").
- 2026-11-04 · All image generation goes through the Batch API, including fixes and the critical path.
- 2026-11-22 · Samples also go through a small batch. No immediate calls until the user explicitly says so.
- 2026-11-04 · After 3 calls an image is accepted as-is: log the defect, never make a 4th call.
- 2026-11-22 · Keep cost low without losing quality: reuse art (zoom crops, library), attach only the references that are needed, use 1K-class sizes.

## Backgrounds (stage 1)
- 2026-10-21 · Reference images carry painted titles, white labels and arrows: tell the model to ignore them, or they leak.
- 2026-10-21 · Never send the spatial authority map to the model. Read it yourself while writing prompts.
- 2026-10-20 · Art direction: a mix of illustration and reality; grand, mystic and magical; real architectural detailing (see `BagroundGenTask/spec/style.txt`).

## Panel art (stage 2)
- 2026-11-22 · Bubbles and captions are HTML overlays. Never paint them; reserve calm empty areas for them.
- Author correction in the CH01 manuscript: all human characters have fair skin.

## Layout (stage 3)
- 2026-11-22 · Follow the patterns of the four sample PDFs (`PdfSheetsGenTask/design/patterns.md`). Colours may vary by page content; the user will ask for colour changes when needed.
- 2026-11-22 · The artifact must show only the page, with no extra information.

## Layout (stage 3), Design Manual V09
- 2026-11-22 · `PdfSheetsGenTask/CHANDRUSH-PAGE-DESIGN-MANUAL-V09.pdf` is the design authority (digest: `design/manual-v09.md`); it overrides patterns.md where they differ. Captions, speech and asides 14/18 pt; subheads Source Sans 3 Semibold 16–19 pt; running line 10–12 pt; gutter colours indigo/teal/aubergine/slate as a sliver on lesson pages; borders derived from a material in the scene, 0.5–1.1 pt; maths colour only with a job (teal tracked, terracotta second role).
- 2026-11-22 · Teaching companions sit on a support from their scene (bench, ledge) with the scenery fading irregularly into the paper; no oval vignettes. Supersedes the 2026-11-22 "vignettes fill their column" rule where they conflict.

## Maths
- 2026-11-22 · Mathematical correctness is mandatory. Minor non-maths mistakes are acceptable.

## Layout (stage 3), learned on the first sample page
- 2026-11-22 · Vignettes must fill their column: use a tall box with `object-fit: cover` and place the bubble over the vignette's calm top edge with a short tail to the mouth, not a small figure under an empty column. (CH01 P039)

## Stage 0 (planning)
- 2026-11-22 · Manuscript equations are Word objects (powers, fractions, roots). Always use `textcheck.py dump/pages` (it converts them to `2²`, `7/4`, `√49`). If you see blanks such as `(i)  −  (ii)`, the source files are stale: re-run `pages`.
- 2026-11-22 · `textcheck page` only checks plan→HTML. Before building, compare every `[Equation]`/`[MathExample]`/`[AnswerLead]` line in `src/Pxxx.txt` against the plan: old P039 silently dropped three factor equations.
