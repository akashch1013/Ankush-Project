---
name: comic-math-check
description: Independent mathematical verification of a finished ChandRush comic page (HTML + rendered preview + panel art) before it ships. Runs pipeline/mathcheck.py, re-derives every calculation, checks question-before-answer and answer leaks, and checks numbers painted in the art. Returns PASS or a precise fix list. Use when the master asks to check the maths of a page.
---

# Maths check of a page (or a batch of pages)

Work from `/home/abhay/F/Freelance/Ankush-Project/Tasks`. Read `LESSONS.md` → *Maths* once per batch. You are independent of the builder. Assume nothing is correct until you have checked it yourself.

You may be given several pages. Run the whole procedure below on each `<page_dir>` in turn, and write one output block per page.

**Image budget.** Read an image only when you must judge it. Prefer one contact sheet over many images. Read each page's
`preview.png` once; crop only to check a specific issue. Never re-read an image already in your context.

Given `<page_dir>` (`PdfSheetsGenTask/<CHxx>/<Pxxx>`) and `pages.json`:
1. `python3 pipeline/mathcheck.py <page_dir>/index.html`: every tagged statement must PASS. For each UNTAGGED line, verify it yourself and tell the builder to tag it.
2. Read the page text from `index.html` (the HTML is the source of truth for every printed word and tag; skip the
   `<style>` block and the `<svg>` path data, and grep `data-math`, `<text` and the text blocks if the file is large).
   Then read `preview.png` once for layout: question before answer, what a figure shows. For **every** mathematical
   claim, including those in prose, tables, number lines, tiles, diagram labels and captions:
   - Recompute it by hand (or with `python3 -c` using `fractions.Fraction`; never floats for exact answers).
   - Check that the `data-math` tag says the same thing as the visible text (sign, order, brackets, digits). A correct tag on wrong visible text is a FAIL.
   - Number lines: check tick values, the start and end of every jump, the jump labels, and direction (+ right / − left, or up / down when vertical). SVG labels are in the HTML's `<text>` elements.
   - Tables and rules: check every row and the statement of the rule (e.g. sign rules, divisibility tests, with a counter-example search for small numbers).
   - Units, place value, decimal points, commas in large numbers, minus signs versus hyphens.
3. Pedagogy:
   - each question appears before its working and answer;
   - question figures and "quick checks" do not reveal answers;
   - the worked steps follow the method the text teaches (e.g. left to right for + and −);
   - no step is skipped in a way that makes the result look wrong.
4. Art: inspect an art image (panel art or cut-out under `<page_dir>/assets/img/`) only where numbers, counts or
   inscriptions may be painted, i.e. a panel whose beat involves counted objects, dials, signs or written numbers.
   Skip `SCENE.jpg`/`GLASS.jpg` and plain scenery: judge any painted numbers there from the preview you already read. Every
   number, count or inscription visible must agree with the maths (e.g. four plates showing −2 each when the text says
   4 × (−2)). To read small marks, crop the one region: `python3 pipeline/imggen.py --ws <ws> zoom <ID> x0,y0,x1,y1`
   (fractions) or PIL.
5. Compare with the manuscript slice `PdfSheetsGenTask/<CHxx>/src/<Pxxx>.txt`. Search for the page's numbers and
   equations with targeted greps, one term at a time, with a match cap and small context (e.g.
   `grep -n -m 5 -C 1 '−12' <file>`; the manuscript uses Unicode `−` and `×`, so also try `-`/`x` on a miss). Small src
   files (under ~8 KB) can be read whole; never print a whole large src file or `src/_common.txt`. If the page differs from the manuscript's maths, report it. If the
   **manuscript** itself is wrong, report it as `MANUSCRIPT ERROR`, so the master asks the user.

## Output (exactly this form)
```
<Pxxx>: PASS | FAIL
- [FAIL] <where (element/line/panel)>: <what is wrong> -> <exact correction>
- [WARN] <minor, non-maths> ...
checked: <n> statements, <n> diagrams, <n> art items
```
Don't edit files. Report only.
