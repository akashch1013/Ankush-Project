---
name: comic-page-builder
description: Stage 3 of the ChandRush comic pipeline. Builds a creative, aspirational (age 11, never kiddish), precise, editable 12x9 in graphic-novel page as self-contained HTML from the page's art-direction brief, in the current look (ART-DIRECTION.md A4 plus the approved B1 reference page CH01/P039), with exact SVG maths illustrations, HTML speech and captions and exact teaching text tagged data-math, then renders it to Tasks/Output/CHxx/CHxx-Pxxx.pdf with pipeline/pagekit.py. Use when the master or user asks to build, lay out, render, re-render or edit comic page sheets.
---

# Stage 3: page sheets (creative build)

Work from `/home/abhay/F/Freelance/Ankush-Project/Tasks`. Read only what this page needs, once:
1. `LESSONS.md`: *All stages*, *Art direction*, *Layout*, *Maths*. Newest entries win: B1 "Ledger Plate" (CH01 P039)
   is the approved look.
2. `PdfSheetsGenTask/design/ART-DIRECTION.md` (the A4 look, ~9 KB): §3 anatomy, §4 glass by role, §5 colour,
   §6 maths, §7 banned, §10 scorecard. Read the brief format (§9) only if the brief is unclear.
3. Your page's entry in `pages.json`, especially its `"art"` brief. Print just that entry, never the whole file:
   `python3 -c "import json,sys; e=next((p for p in json.load(open(sys.argv[1]))['pages'] if p['page']==sys.argv[2]),None); print(json.dumps(e,ensure_ascii=False,indent=1) if e else 'page not found')" PdfSheetsGenTask/<CHxx>/pages.json <Pxxx>`
4. `PdfSheetsGenTask/<CHxx>/src/<Pxxx>.txt`: the authority when the plan looks wrong. The `pages.json` entry already
   holds the exact text, so open src only to check a beat. If it is over ~8 KB, don't read it whole: `grep -n -m 5` the
   phrase or heading you need, then `sed -n` that line range. Line tags differ by chapter (list them with
   `grep -oE '^\[[A-Za-z]+\]' <file> | sort | uniq -c`) and printable text can be untagged, so never filter on tags
   alone. Never read `src/_common.txt` whole.
5. **One** reference page: `PdfSheetsGenTask/CH01/P039/index.html` (B1, approved: its inline `<style>` block plus the
   blocks you need). Use `PdfSheetsGenTask/CH01/P005/index.html` instead only when the brief asks for a full-bleed A4
   scene with glass panes.
6. Only as needed: the kit `design/kit.css` (~8 KB, A4; grep the class you need, never edit it by hand), and the
   `design/manual-v09.md` section you need (§1 type, §5 balloons, §8 worked maths, §9 proof).

Do not read anything in `design/archive-a3/` (the old A3 "Lantern Street" kit, galleries and the 94 KB kit.css): it is
archived and must not be copied.

**Image budget.** Read an image only when you must judge it. Prefer one contact sheet over many images. After a render,
read `preview.png` once; crop only to check a specific issue. Never re-read an image already in your context.

## Per page
1. `python3 pipeline/pagekit.py new <CHxx> <Pxxx> --theme <class>`: the class goes on `.page` (`ledger` as in P039, or
   `a4` as in P005). It copies base.css, kit.css and the fonts.
2. Add images:
   - panel art: `pagekit.py img <page_dir> FInalChangesTask/<CHxx>/out/<ID>.png <ID>`;
   - library cut-outs: `pagekit.py img <page_dir> FInalChangesTask/library/C-AHANA-LEAN-01.png AHANA --png --max 1200`;
   - plates: `pagekit.py img <page_dir> BagroundGenTask/out/plates/S04-B01.png S04-B01`;
   - a full-bleed world and its glass: `pagekit.py scene <page_dir> <plate> [--mirror] [--blank x0,y0,x1,y1] [--crop ...]`;
     a counted prop or character lifted from art: `pagekit.py cutout <page_dir> <src> <NAME> --poly "x,y x,y ..."` (ART-DIRECTION §2).
3. **Fit the text first, then the art, then the decoration.**
   - Lay out every printable block in reading order on the shape its role takes (ART-DIRECTION §4; B1: light reading shapes).
   - Use exact text from `pages.json`. Never add words; speaker names never print.
   - Body 14/18 pt minimum. The hardest fit decides the layout.
4. **Then make it a picture book** (the brief, then your own ideas): the border or world from the page's own location
   plate, the hero (art or drawn maths), at least one character in the scene, 2–3 page-specific delights (ART-DIRECTION §8),
   the folio as in the reference page. Nothing on the ART-DIRECTION §7 banned list, and the same family as the page's
   location plate.
5. **Maths illustrations** are hand-written SVG with exact values, drawn as in-world objects (ART-DIRECTION §6): brass lines,
   glass, lamp and moon colours, or exact counted cut-outs from the art. Never flat or cartoon. Number lines can start from
   `pagekit.py numberline` output.
   - A question's figure shows only the question's data.
   - Every printed equation or numeric statement carries `data-math` (see the `pipeline/mathcheck.py` header). Questions
     print without answers and without `data-math` on the unknown. A deliberately wrong example gets `data-math-expect="false"`.
6. Speech: `.say` with the curved `svg.tail` pointing at the mouth, copied from the reference page; narration as in the
   reference page. Only manuscript bubbles and asides.
7. `python3 pipeline/pagekit.py render <page_dir>`. It runs mathcheck + the asset check, prints the PDF and writes `preview.png`.
8. `python3 pipeline/textcheck.py page <page_dir> PdfSheetsGenTask/<CHxx>/pages.json`; fix until "page text OK" (text
   fixes need no extra look at the preview).
9. **Look at the render** (`preview.png`, once per render) and check text fit and overflow, speech covering faces, tails,
   contrast, empty holes, crops and masked shapes. Filters can soften text in the PDF, so keep long text off filtered
   wrappers. Score the page with ART-DIRECTION §10. Fix and re-render until **≥ 8/10 with all musts**.
   **Cap: at most 4 renders per page.** Batch all fixes you can see into each re-render. When the cap is hit, stop and
   report the remaining issues for the user.
10. Report per page:
    - the page_dir, the PDF path and the preview path;
    - mathcheck counts and the textcheck result;
    - the score and the number of renders used;
    - ideas you added;
    - issues for the master (including anything left at the cap).

When fixing from a math-check or review list: fix every item, then re-render once. At most 2 maths-fix rounds and 1
review-fix round per page; then stop and report what remains.

Practical notes:
- Glass panes need `--x`/`--y` equal to their `left`/`top` (ART-DIRECTION §4).
- `.eq` uses dark ink (base.css) and inherits the pane's text colour inside `.glass`; `.ledger` styles live in P039's
  inline `<style>`, so copy that block.
- Small SVG shapes with gradient fills (box corners, bands, pouches) print washed-out in poppler-based viewers (`pdftoppm`,
  Evince, Okular) although MuPDF is fine. Use solid fills for small shapes, keep gradients for large ones, and judge the
  render from `preview.png`.

The artifact is published by the master from the same `index.html` (`pagekit.py artifact` inlines base.css + kit.css
+ fonts). Keep the page self-contained: only `assets/…` references, no network fonts, and nothing outside the `.page`
div except the fit-to-window script from the template.
