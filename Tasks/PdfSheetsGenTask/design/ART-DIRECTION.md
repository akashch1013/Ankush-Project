# ChandRush art direction (A1, adopted 2026-11-22)

**This is a children's picture book, not a worksheet.** Every page must make a 10–13-year-old want to look at it
before they read it. It has colour, art and one or two surprises that belong to this page only.
The user's words: *"it is a page of a child's book! this should be creative!! the pages should contain colours, some art, some unique things!!"*

Precedence: **this file governs look, colour, devices and creativity.** `manual-v09.md` still governs reading
comfort (type sizes, contrast, maths glyphs, question-before-answer, proof). Where V09 says "cut decoration" or
"only a sliver of colour", this file wins. `patterns.md` grids are optional starting points, not templates.

Tools: `kit.css` (built by `kitgen.py`). See every piece rendered in `kit-1.png` and `kit-2.png`, and copy markup
from `kit-gallery-1.html` and `kit-gallery-2.html`. Free art is in `FInalChangesTask/library/README.md`.

---

## 1. The book's look: "Moonlit block-print"
The Midnight Mela is a magical Indian night fair. The pages look like a keepsake made at that fair:
- **Stage (the world behind the page):** a deep indigo night with stars and a fair skyline (`stage-night`), or
  indigo cloth with a dabu block print (`stage-dabu`, `stage-dabu-teal`). Use a dusk sky (`stage-dusk`) for reveals and
  warm moments, and cream handmade paper (`stage-paper`, `-cool`) for calm lessons.
- **Reading objects:** cream paper things a child could hold, lying on that stage: tickets, gift tags, the crew
  notebook, lift-up answer flaps, brass plaques, a narrator's scroll.
- **Mela brights as accents:** marigold, rani pink, peacock teal, parrot green and lantern gold, against indigo
  and cream. Brass for fittings.
- **Painted scenes and characters** (the panel art) are the stars. The design frames them and lets them step out
  of their frames.

## 2. What went wrong before (don't repeat)
Assessed on 2026-11-22 from `Completed Samples/` (P011–P015, P027–P031, P087–P091) and the pipeline's own P039:
1. Teaching pages read as textbook worksheets: cream rectangles on a flat dark colour, with the same template three
   pages running (P089–P091). P039 was a flat grey-blue sheet of text boxes.
2. Only navy, teal, aubergine and cream. The fair's festive colours lived in the art only, never in the design.
3. The maths was never drawn: tiles were plain boxes, with no thermometers, gift boxes or lantern number lines.
4. Speaker names were printed in balloons ("AHANA: …"). Balloons were rectangles with wedge tails.
5. Dead space: big empty dark areas (P030), empty cream columns under captions (P012, P088, P091).
6. The same companion pose on the same torn ledge, three pages in a row.
7. Titles were plain serif text. The only book-wide furniture was a tiny page number.
8. Story pages used only rectangles: no panel-shape variety, insets or frame-breaking.
9. Maths was painted into the art (cards reading "4 × (−2) = −8"). Maths is always HTML.

## 3. Colour
Palette (CSS variables from the kit): `--night #0e1838` `--indigo #1d2f6b` `--gold #f2b441` `--marigold #f28c28`
`--yellow #f7c531` `--rani #d63f7a` `--peacock #12807f` `--parrot #6aa84f` `--kite #e0483b` `--sky #8fc7e8`
`--cream #fff7e6` `--brass #c9962e`, with reading ink `--inkc #1c2340`.
- Each page has a **colour story**: one stage and **two accent brights** that carry its idea (e.g. warm
  marigold + icy sky for "hot town vs cold town"). Add the third and fourth brights only in small touches (a garland, the tape).
- Reading text is always dark ink on a light object, or cream on a dark stage for short lines only (titles, one caption).
- **Maths colour keeps its job** (V09): deep teal `.mt` = the tracked or moving quantity; terracotta `.mr` = a second role.
  Operators and `=` stay ink. Decorative colour never sits inside an equation.

## 4. Type (body stays readable; headings get personality)
| Role | Face | Size |
|---|---|---|
| Page title | **Baloo 2 ExtraBold** (`.h-title`, `.sign`, `.ribbon`) | 26–40 pt |
| Sub-heads ("Example 11", "Now you try", "Check your method") | Baloo 2 Bold (`.h-chip` + icon, or `.ribbon`) | 17–20 pt |
| Teaching prose, figure labels | Source Sans 3 | 14/18 pt |
| Narration / captions | Source Serif 4 (`.capnote`, `.scroll`) | 14/18 pt |
| Story speech | Baloo 2 SemiBold (`.say`) | 14.5/18 pt |
| Companion aside to the reader | **Kalam** handwriting (`.say.aside`) | 15/19 pt |
| Display maths | Source Sans 3 Semibold (`.eq`) | 20–28 pt |
Never shrink essential text below 14 pt to fit art. Shrink or move the decoration instead.

## 5. One object per text role (the book's visual language, keep it consistent)
Children learn the code: *a ticket means "your turn"; a flap means "answers, after you try".*
| Manuscript role | Object (kit class) | Notes |
|---|---|---|
| Question, "Try", "Now you try", "Pause and think" | `.ticket` (+ `.stub` icon) or `.tag` for shop/gift problems | sits **before** its working |
| Worked example / "Let's work it through" | `.ledger` (crew notebook) or `.sheet` | equations aligned, `=` in a grid if they carry meaning |
| "Check your method / thinking", answers | `.flap` with a `.pull` tab (eye/key icon) | always after the attempt; separable |
| The one key result or rule | `.plaque` (brass) or `.slate` for a short rule | max one per page |
| Narrator caption / reader address | `.scroll` (opens a section), `.capnote` (in story) | |
| Speech | `.say` + curved `svg.tail` to the mouth | no speaker names, ever |
| Companion remark to reader | `.say.aside` in Kalam | only if the manuscript gives the line |
| Section title | `.h-title`, `.sign` hanging from the garland, or `.ribbon` | |
| Folio | `.moonclock` with `--t = page / last page` (CH01: 107) | **every page**, the book's signature |

## 6. Book furniture (recurring signatures)
1. **Moonset clock folio** on every page (bottom, in a quiet margin). The moon sinks from left to right through the chapter: the race to moonset.
2. **One garland or edge per page**: `.toran` (and `.cool`/`.warm`), `.marigold`, `.lanterns`, `.fairy`, `.awning`
   (stall pages), `.rangoli` corners, or `.dabu-band`. Rotate them; never the same one on two neighbouring pages.
3. **A companion on most pages**, entering in a different way each time:
   - `.jharokha` (carved window, for art that has its own background);
   - `.pop` (a cut-out stepping out over a frame's edge);
   - `.snap` (a taped photo);
   - sitting on a library ledge that fades into the stage.

   A companion is silent unless the manuscript gives an aside.
4. **Tez's paw trail** (`.paws`) may wander across a margin to wherever Tez appears. Use it at most every few pages.

## 7. Draw the maths (the biggest win)
When the manuscript's own content has a picture in it, draw that picture as an **exact SVG illustration**:
thermometers for temperatures, a lift shaft for levels, gift boxes and goodie bags for sharing, lantern strings for
number lines, a balance for equations, tiles as fair tokens.
- Exact: every count, length and label is mathematically true. Labels are only numbers and words already in the manuscript.
- A figure placed with the **question** shows only the question's data. Anything that reveals the answer goes in
  or after the working/answer object.
- A countable picture (9 gift boxes) is allowed **only** when the count is the true answer and it sits after the
  question. The math-checker checks it. Decoration never looks countable near maths (no random dots or tiles beside a sum).
- Production notes (`Production note Vnn`) still bind: follow their constraints, and style them with the kit.

## 8. Story pages
- Panels are framed art (`.frame-panel`) on a dark stage. Vary the shapes: one wide hero, an inset circle
  (`.frame-panel.round`) for a reaction, an arch top for a threshold, a `.jharokha` peek.
- Let one character or prop **break a frame** (`.pop`, or overlap two panels) on most story pages.
- Captions are `.capnote` in a corner, away from faces. Speech is `.say` with a tail to the mouth, in speaking order.
- Use the gutters: the stage shows between panels (stars, garland), so there are no flat colour seams.

## 9. Creativity is free; keep it that way
The kit, the fonts and the SVG illustrations cost nothing. Art: reuse first (the library cut-outs, plates in
`BagroundGenTask/out/plates/`, zoom crops). A new image only when the manuscript needs a specific story moment
(through panel-artist, Batch API).

## 10. The page brief (`pages.json` → `"art"` per page), written before building
```json
"art": {
  "idea": "one sentence: the page as a place or object at the Midnight Mela (e.g. 'Salim's gift-pack stall')",
  "stage": "stage-paper",            "garland": "awning.teal along the top",
  "hero": "what the eye lands on first at thumbnail size",
  "objects": {"question": "tag.pink", "working": "ledger", "answers": "flap", "result": "plaque"},
  "illustrate": "the exact maths picture, and where it sits (with the question / after it)",
  "companion": "who, how they enter (jharokha / pop / snap / ledge), where, aside text if any",
  "colour": "stage + 2 accent brights; maths teal tracks …",
  "delights": ["2–3 small wordless surprises tied to THIS page's content"],
  "folio": "moonclock --t 0.364",
  "varies": "how it differs from the previous page (stage, garland, companion entry, colour)"
}
```

## 11. Creativity scorecard (builder self-check; master review). Ship at ≥ 8/10 with all musts.
**Musts (any miss = fix):**
- text verbatim, no invented words;
- maths exact and tagged;
- question before answer;
- body text ≥ 14 pt with dark-on-light contrast;
- nothing clipped or overlapping a face;
- no speaker names.

**Score 1 point each:**
1. A clear **hero** reads at thumbnail size.
2. A world **stage**, not a flat fill.
3. At least **3 colours** beyond ink/paper, used in harmony.
4. Text sits on **objects** (ticket, notebook, flap…), not plain boxes.
5. The **maths is drawn** where the content allows.
6. A **character with personality** (or, on story pages, a frame-break).
7. **Depth**: something overlaps something: tape, a pop-out, a sign hanging over a sheet.
8. **2+ delights** specific to this page.
9. The **book furniture** is present: moonclock and one garland/edge.
10. It **differs from its neighbour** and has no dead hole larger than about 1/8 of the page.
