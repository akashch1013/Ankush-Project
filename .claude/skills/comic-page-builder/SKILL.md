---
name: comic-page-builder
description: Stage 3 of the ChandRush comic pipeline. Builds a creative, aspirational (age 11, never kiddish), precise, editable 12x9 in graphic-novel page as self-contained HTML from the page's art-direction brief, using the creative kit (kit.css A3, matched to the location plates: royal lacquer planks, brass, marble, lamp light, VIP passes, field notebook, sealed answers, jharokha windows, pop-out characters, moonset dial) and exact SVG maths illustrations, with HTML bubbles/captions and exact teaching text tagged data-math, then renders it to Tasks/Output/CHxx/CHxx-Pxxx.pdf with pipeline/pagekit.py. Use when the master or user asks to build, lay out, render, re-render or edit comic page sheets.
---

# Stage 3: page sheets (creative build)

Work from `/home/akasdh/Desktop/Projects/ComicAgent/Tasks`. Read first:
1. `PdfSheetsGenTask/design/PAGE-DESIGN.md`: the current look, fixed system, what varies, scorecard. **It governs.**
2. `LESSONS.md`: only rules dated after PAGE-DESIGN's date, plus *Maths*.
3. Your page in `PdfSheetsGenTask/<CHxx>/pages.json`: its `art` brief, `art.variation` card, panel boxes and reserves, plus `src/Pxxx.txt` (the authority if the plan looks wrong).
4. Optional, for kit classes only: `design/kit-1.png`, `kit-2.png`, `kit-gallery-*.html`; `design/manual-v09.md` for maths layout.

## Modes
- **build:** art is ready. Do the whole page.
- **shell:** the art batch is still out. Build the whole page; put a placeholder under each new panel's final asset name (`pagekit.py img <page_dir> <plate> <ID>`), so the swap later is one command. Balloons go at the briefed reserves.
- **letter:** art approved. `pagekit.py img` the real art over the placeholder, then **re-letter on the real image**: move balloons and captions onto its calm areas, tips 4–8 pt short of each mouth. Re-render.
- **fix:** apply the fix list exactly, re-render, re-run textcheck.

## Non-negotiables (user, 2026-11-25)
- Running head on every page: `CHAPTER 01 · NUMBERS · PG 001` (2-digit chapter, 3-digit page).
- **Balloons and captions sit on the panel art** (opaque, calm areas, never over faces/hands/clues), not in gutters. Gutters 9–12 pt, so the images get the area.
- **Balloons only from `pipeline/balloon.py`**: body + tail are one outline, so tails can never look broken. Never hand-draw tails (the old wedge + cover-line tails broke on curved edges).
- Story pages: deep field with subtle gradation. Teaching pages: calm light paper, creativity in the border.
- Every page differs from its neighbours (variation card). The book system (head, folio, type, balloons, margins) never varies.

## Per page
1. `python3 pipeline/pagekit.py new <CHxx> <Pxxx> --theme <stage-class>`. It copies base.css, kit.css and the fonts
   (Source Sans 3, Source Serif 4, Cinzel, Rajdhani, Caveat). Put the stage class on `.page`, e.g. `class="page stage-cinema"`.
2. Add images:
   - panel art: `pagekit.py img <page_dir> FInalChangesTask/<CHxx>/out/<ID>.png <ID>`;
   - library cut-outs: `pagekit.py img <page_dir> FInalChangesTask/library/C-AHANA-LEAN-01.png AHANA --png --max 1200`;
   - plates: `pagekit.py img <page_dir> BagroundGenTask/out/plates/S04-B01.png S04-B01`.
3. **Fit the text first, then the art, then the decoration.**
   - Lay out every printable block in reading order on its object (PAGE-DESIGN §2/§4).
   - Use exact text from `pages.json`. Never add words; speaker names never print.
   - Body 14/18 pt minimum. The hardest fit decides the layout.
4. **Then make it a picture book** (the brief, then your own ideas):
   - the stage on `.page`;
   - one ornament system (deco-frame / jali-band / lightstring / hud / watermark);
   - the hero (art or drawn maths);
   - the companion's entrance (`.jharokha`, `.pop`, `.snap`, or a ledge);
   - the delights;
   - the `.moonclock` folio (`--t` = page / last page; CH01 last page = 107);
   - depth: overlaps, glow, a pop-out, brass mounts;
   - the tests: nothing on the PAGE-DESIGN §1 banned list, and the same family as the page's location plate. Use `pagekit.py backdrop <page_dir> <plate>` for a `.stage-backdrop` page.
5. **Maths illustrations** are hand-written SVG with exact values, drawn as in-world objects in the plates' painterly
   style (PAGE-DESIGN §1–2):
   - brass-and-glass gauges, cut-away lift shafts;
   - the plates' blue lacquered kit boxes with brass corners, velvet pouches;
   - lamp-lit vs moonlit cities, brass number rails.

   Use gradients, a warm key light, a cool moon rim, specular brass and soft shadows. Never flat or cartoon. Number lines can start from `pagekit.py numberline` output and be dressed up.
   - A question's figure shows only the question's data.
   - Every printed equation or numeric statement carries `data-math` (see the `pipeline/mathcheck.py` header). Questions
     print without answers and without `data-math` on the unknown. A deliberately wrong example gets `data-math-expect="false"`.
6. Balloons (speech): **`pipeline/balloon.py` only.**
   - Generator pages: `from common import bln`, then `{bln(spec)}` in the body.
   - Hand-built pages: write `PAGE_DIR/balloons.json`, then run `python3 pipeline/balloon.py PAGE_DIR`. It rewrites the `<!-- BALLOONS -->` block.

   The spec, in reading order:
   ```
   [{"text": "Are you all right?", "at": [116, 294], "tip": [245, 360]},
    {"text": "Yes.", "at": [444, 358]},
    {"text": "The numbers tell us …", "at": [458, 403], "maxw": 190, "link": 1, "tip": [676, 405]}]
   ```
   The tool sizes each box from the real font. `w`/`h` are minimums, `maxw` is the wrap width, `shape` is pill/round/oval, `bend` gives the tail's curve, `link` joins two balloons from the same speaker. Check sizes first with `--measure "text" --maxw 200`. The tool prints overlap and off-sheet warnings.
   - Captions are `.cap` cream paper boxes on the art.
   - Asides are `.say.aside` (Caveat).
   - Narration is `.capnote` or `.letter`.
7. Run `python3 pipeline/pagekit.py render <page_dir>`. It runs mathcheck + the asset check, prints the PDF and writes `preview.png`.
8. Run `python3 pipeline/textcheck.py page <page_dir> PdfSheetsGenTask/<CHxx>/pages.json` and fix until "page text OK".
9. **Look at the render** (`preview.png`) and check:
   - text fit and overflow;
   - bubbles covering faces;
   - tails;
   - contrast;
   - empty holes;
   - crops;
   - masked shapes. `.shadowed`/filters can soften text in the PDF, so keep long text off filtered wrappers.

   Then score the page with the PAGE-DESIGN §6 scorecard. Fix and re-render until **≥ 8/10 with all musts**.
10. Report per page:
    - the page_dir, the PDF path and the preview path;
    - mathcheck counts and the textcheck result;
    - the score;
    - ideas you added;
    - issues for the master.

Practical notes:
- Masks (`.ticket`, `.tag`, `.torn-*`) cut `box-shadow`. For a shadow, wrap the shape in `.shadowed`, but only for short text.
- `.flap` needs `--under:` set to the colour behind it (for the folded corner).
- `.jharokha` needs the `<svg class="defs">` clipPath block once per page (kit-gallery-2).
- Base classes (`.eq`, `.h-sub`) take dark ink automatically inside kit objects. On dark stages they take cream.
- Small SVG shapes with gradient fills (box corners, bands, pouches) print washed-out in poppler-based viewers (`pdftoppm`, Evince, Okular) although MuPDF is fine. Use solid fills for small shapes, keep gradients for large ones, and always judge the render from `preview.png`.

The artifact is published by the master from the same `index.html` (`pagekit.py artifact` inlines base.css + kit.css
+ fonts). Keep the page self-contained: only `assets/…` references, no network fonts, and nothing outside the `.page`
div except the fit-to-window script from the template.
