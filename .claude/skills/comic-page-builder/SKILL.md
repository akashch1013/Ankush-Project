---
name: comic-page-builder
description: Stage 3 of the ChandRush comic pipeline. Builds a precise, editable 12x9 in comic page as self-contained HTML (panels with HTML bubbles/captions, exact teaching text, maths as HTML/SVG tagged data-math) following the approved sample-PDF patterns, then renders it to Tasks/Output/CHxx/CHxx-Pxxx.pdf with pipeline/pagekit.py. Use when the master or user asks to build, lay out, render, re-render or edit comic page sheets.
---

# Stage 3: page sheets

Work from `/home/akasdh/Desktop/Projects/ComicAgent/Tasks`. Read these first:
1. `LESSONS.md`: *All stages*, *Layout*, *Maths*.
2. `PdfSheetsGenTask/design/manual-v09.md` (Design Manual V09 — governs type, colour, edges, companions, proof; view the `manual-v09/mNN.jpg` study pages it cites), then `PdfSheetsGenTask/design/patterns.md`, then Read the sample JPGs it names for your page's pattern (`design/samples/`).
3. `PdfSheetsGenTask/design/components.html` (snippets) and, when needed, `design/base.css`.
4. Your pages in `PdfSheetsGenTask/<CHxx>/pages.json`, plus each page's manuscript slice `PdfSheetsGenTask/<CHxx>/src/Pxxx.txt` (the authority if the plan looks wrong).

## Per page
1. `python3 pipeline/pagekit.py new <CHxx> <Pxxx> --theme <theme>`
2. Add the images:
   - panel art: `pagekit.py img <page_dir> FInalChangesTask/<CHxx>/out/<ID>.png <ID>`;
   - plates and library art the same way;
   - `--png` only for art with transparency.
3. Write the page inside `<div class="page …">`, following the pattern:
   - Use exact text from `pages.json`. Don't rephrase, shorten or add words. Speaker names never print.
   - Bubbles and captions go inside their panel, over the reserved areas. Tails point at the speaker. The reading order matches the plan.
   - Every printed equation or numeric statement carries `data-math` (see `pipeline/mathcheck.py` header). Questions are printed without answers and without `data-math` on the unknown. A deliberately wrong example gets `data-math-expect="false"`.
   - Number lines come from `pagekit.py numberline` (exact), and tables and diagrams are hand-written SVG/HTML with exact values. Never use an image for maths.
   - Exact text on a blank physical card in the art: `.ontext` with a perspective tuned to the card.
   - Zoom panels: `.panel.zoom` with `--z`, `--fx`, `--fy` from the plan.
   - Fill the page purposefully. Nothing may overflow, overlap a face, or sit closer than 10 pt to the frame.
4. Run `python3 pipeline/pagekit.py render <page_dir>`. It runs mathcheck + the asset check, prints the PDF and writes `preview.png`.
5. Run `python3 pipeline/textcheck.py page <page_dir> PdfSheetsGenTask/<CHxx>/pages.json` and fix until "page text OK".
6. **Look at the render.** Read `preview.png` and check:
   - text fit and overflow;
   - bubbles covering faces;
   - tails;
   - alignment;
   - contrast;
   - empty holes;
   - the crop of each panel (faces and the key action visible).

   Fix and re-render until it reads like the samples. If an image is wrong or unusable, report it to the master instead of hiding it.
7. Report per page: the page_dir, the PDF path, the preview path, mathcheck counts, and any issues left for the master.

The artifact is published by the master from the same `index.html`. Keep the page self-contained: only `assets/…` references, no network fonts, and nothing outside the `.page` div except the fit-to-window script from the template.
