# Master agent prompts

Open Claude Code in `ComicAgent/` or `ComicAgent/Tasks/`. Both folders load the master instructions automatically (`CLAUDE.md`, then the `comic-master` skill). A short request is usually enough. Paste the **master prompt** at the start of a new chat when you want to be sure everything is followed.

---

## Master prompt (paste once at the start of a new chat, then add your request)

```
You are the ChandRush master agent. Before anything else, read Tasks/CLAUDE.md, Tasks/LESSONS.md
and the end of Tasks/FEEDBACK.md, and load the comic-master skill. Follow them exactly:

- Pages follow the manuscript's own page ids (page 69 = CH01-PAGE069 → P069). One PDF per page in
  Tasks/Output/<CHxx>/. All pages of a request are delivered together: one combined PDF + ONE private
  artifact showing every requested page (pagekit.py set).
- Design: PdfSheetsGenTask/design/PAGE-DESIGN.md (one card with every decision so far). Every page is creative
  and aspirational for 11-year-olds (never kiddish), in the location plates' family, with a fixed book system and
  per-page randomness from pipeline/vary.py. Text sits ON the art (never hiding faces); balloons only from
  pipeline/balloon.py (seamless tails). The art-director writes each brief, layout first; score ≥ 8/10.
- Text is copied word for word from the manuscript (textcheck must pass). Production notes never print.
  Questions come before answers.
- Maths must be exactly right: every equation tagged data-math, mathcheck 0 failures, and the math-checker
  agent returns PASS before a page ships.
- Images: OpenAI Batch API only, ONE batch per wave for all requested pages, quality high (xhigh only for
  really hard images, max never without asking), no immediate calls, strictly at most 3 calls per image then
  accept. Character refs from Tasks/CHANDRUSH CHARACTERS (pipeline/cast.py) + height chart. Prompts pass
  promptlint before they cost a call. Reuse art before making new art. Bubbles and captions are HTML, never painted.
- Work in parallel: art-director (briefs), panel-artist (prompts/QC), page-builder (shells while the batch runs,
  then letter on the real art), math-checker (Sonnet) per page, production-assistant (Sonnet) for mechanical jobs.
  You plan, run the combined batches, review the contact sheet, publish and report.
- Any feedback I give: log it in FEEDBACK.md, add a rule to LESSONS.md, fix the current page, and
  apply it to every future page.
- When done, report: PDF path, artifact link, checks, cost. Don't start other pages unless I ask.

Request: <write it here>
```

---

## Handing over a chapter (author)
1. Make a folder in `Tasks/Reference/`, e.g. `Chap4/` (not containing the word "old"). In ChandRush Studio use **New run → Upload a new chapter**, which does this for you.
2. Put in it:
   - `CH04-PANELIZED-MANUSCRIPT-V01.docx`: the file name must start with the chapter id;
   - `CH04-LOCATION-IMAGE-REGISTER-V01.docx`;
   - the reference images (register masters, maps, props).
3. Say `I added chapter 4` (or `/comic-master setup CH04`). The **setup agent** prepares everything for free, with no images: the pages, cast, locations, plates, background workspace and a maths pre-scan. It then lists what it needs from you in `PdfSheetsGenTask/CH04/SETUP-REPORT.md`.
4. A corrected version: add the new file (`…-V02.docx`) to the same folder and say `new manuscript version for chapter 4`. Setup lists the pages that changed, including ones already built.

Check what is set up: `python3 pipeline/setup_chapter.py scan`.

---

## Requests (one line each; the chapter defaults to the one you worked on last)

| What you want | Type |
|---|---|
| New chapter / new version | `I added chapter 4` · `New manuscript version for chapter 2` |
| One page | `Generate page 69 of chapter 1` |
| A few pages (one combined PDF + one artifact with all of them) | `Generate pages 40 to 45 of chapter 1` |
| Sample by type | `Generate a text heavy sample page from chapter 2` · `a story sample` · `a math heavy sample` · `a story + maths sample` |
| Whole chapter | `Do chapter 2` (plans every page, a 2-panel art sample for approval, the first page for approval, then the rest) |
| Approve | `Approved, continue` |
| Fix a page | `Page 39: move Tez's bubble to the left and make the answer box bigger` |
| Colour | `Page 39: use the sage theme` · `All teaching pages in chapter 2: lighter colours` |
| Art problem | `Page 12: Ahana has the wrong hair; fix the picture` (a batch fix call on that image only) |
| Feedback for the future | `From now on: put the question box on the left, and use bigger handwriting font for asides` |
| Status / cost | `Status of chapter 1` · `How much have we spent?` |
| Allow faster images (costs 2×) | `You may use immediate calls for this page` |

### Slash forms (same thing, more exact)
```
/comic-master setup CH04
/comic-master page CH01 P069
/comic-master page CH01 P040-P045
/comic-master sample text-heavy CH02
/comic-master plan CH02
/comic-master run CH02 P001-P010
/comic-master fix CH01 P039 "the bubble covers Tez's ear; move it up 20pt"
/comic-master feedback "text-led pages: use the sage theme more, and make the quick-check box bigger"
/comic-master status CH01
```

### Commenting on an artifact
Comment directly on the page artifact, then tell the master: `Read my comments on page 39 and fix them`.
Each comment becomes a fix plus a lesson for future pages.
