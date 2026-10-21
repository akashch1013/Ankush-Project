---
name: chandrush-assembler
description: Assemble approved ChandRush panel art and the exact manuscript text into finished pages in the approved sample look: frames, crops, captions, speech balloons with aimed tails, reader call-outs, borders and page numbers. Export per-page PDFs, a batch review PDF and 300-dpi PNGs, and compare them against the sample. Use whenever ChandRush pages need to be built, rebuilt, previewed, re-cropped, have balloons or captions moved, or be compared with the sample pages.
---

# ChandRush assembler

You put approved components together. You never redraw art and never retype text. Text always comes from the page contract, and art always comes from the approved version in `state.json`.

Design reference: `guide/03_DESIGN_SYSTEM.md`. Procedure: `guide/06_ASSEMBLY_AND_AUDIT.md`.

## Steps

1. **Check readiness.** Run `python -m pipeline status`. Every panel should be approved or review_later, and every balloon tail should be `set`.
2. **Fix crops and tails first.**
   - For each panel, look at `python -m pipeline review --panel <id>`.
   - If a face, hand or key prop is cut, or a text zone covers a face, run `python -m pipeline frame --panel <id> --focus U,V [--zoom z]`.
   - For balloons, run `python -m pipeline tail --panel <id> --at U,V` at a point just beside the mouth.
3. **Build.** Run `python -m pipeline build`. It stops on any layout error: unplaced or doubled text, overflow, overlap, too close to the trim, a missing tail. Fix the layout and rebuild. Never shrink type, squeeze letters or delete words to make things fit.
4. **Look at every page** in `output/png/CH01-P0xx.png` at full-page size. Check that:
   - the reading order is obvious;
   - captions sit on calm art;
   - balloons point to the right speaker;
   - nothing important is cropped.
5. **Compare the look.** Run `python -m pipeline compare --page N --sample M` against the nearest Opening V04 page. If spacing or colour drifted, change `design/tokens.json` for all pages, not one page.
6. **Hand over** to `chandrush-auditor`.

## Moving things

- Edit `at`, `w` or `max_w` in `pages/CH01-P0xx.layout.json`; coordinates are points from the top-left.
- Use the `--zones` flag on `build` to outline every text box while adjusting.
- Changing a crop, font or balloon never needs new art.
