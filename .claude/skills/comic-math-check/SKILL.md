---
name: comic-math-check
description: Independent mathematical verification of a finished ChandRush comic page (HTML + rendered preview + panel art) before it ships. Runs pipeline/mathcheck.py, re-derives every calculation, checks question-before-answer and answer leaks, and checks numbers painted in the art. Returns PASS or a precise fix list. Use when the master asks to check the maths of a page.
---

# Maths check of a page (or a batch of pages)

Work from the repo's `Tasks/` folder. Read `LESSONS.md` → *Maths* once per batch. You are independent of the builder. Assume nothing is correct until you have checked it yourself.

You may be given several pages. Run the whole procedure below on each `<page_dir>` in turn, and write one output block per page.

Given `<page_dir>` (`PdfSheetsGenTask/<CHxx>/<Pxxx>`) and `pages.json`:
1. `python3 pipeline/mathcheck.py <page_dir>/index.html`: every tagged statement must PASS. For each UNTAGGED line, verify it yourself and tell the builder to tag it.
2. Read the page text (index.html) and the render (`preview.png`). Then, for **every** mathematical claim, including those in prose, tables, number lines, tiles, diagram labels and captions:
   - Recompute it by hand (or with `python3 -c` using `fractions.Fraction`; never floats for exact answers).
   - Check that the `data-math` tag says the same thing as the visible text (sign, order, brackets, digits). A correct tag on wrong visible text is a FAIL.
   - Number lines: check tick values, the start and end of every jump, the jump labels, and direction (+ right / − left, or up / down when vertical).
   - Tables and rules: check every row and the statement of the rule (e.g. sign rules, divisibility tests, with a counter-example search for small numbers).
   - Units, place value, decimal points, commas in large numbers, minus signs versus hyphens.
3. Pedagogy:
   - each question appears before its working and answer;
   - question figures and "quick checks" do not reveal answers;
   - the worked steps follow the method the text teaches (e.g. left to right for + and −);
   - no step is skipped in a way that makes the result look wrong.
4. Art: Read the panel images used on the page. Every number, count or inscription visible in the art must agree with the maths (e.g. four plates showing −2 each when the text says 4 × (−2)). Use `python3 pipeline/imggen.py --ws <ws> zoom <ID> x0,y0,x1,y1` or crop with PIL to read small marks.
5. Compare with the manuscript: read the page's slice `PdfSheetsGenTask/<CHxx>/src/Pxxx.txt`. If the page differs from the manuscript's maths, report it. If the **manuscript** itself is wrong, report it as `MANUSCRIPT ERROR`, so the master asks the user.

## Output (exactly this form)
```
<Pxxx>: PASS | FAIL
- [FAIL] <where (element/line/panel)>: <what is wrong> -> <exact correction>
- [WARN] <minor, non-maths> ...
checked: <n> statements, <n> diagrams, <n> art items
```
Don't edit files. Report only.
