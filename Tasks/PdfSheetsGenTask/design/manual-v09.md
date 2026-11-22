# ChandRush Page Design Manual V09: rules for page builders

Source: `PdfSheetsGenTask/CHANDRUSH-PAGE-DESIGN-MANUAL-V09.pdf` (32 pp). Renders of its key study pages: `manual-v09/mNN.jpg` (NN = manual page). **This digest overrides `patterns.md` wherever they disagree** (adopted 2026-11-22). The pattern layouts (S/M/T ids) remain the starting grid; V09 decides type, colour, edges, companions and proof.

## 0. Order of work (manual p2, p28–29)
1. List every printable block in order (A03): headings, questions, prose, every equation line, blanks, asides, silent beats. Compare against `src/Pxxx.txt`, not only `pages.json`.
2. Mark the focal action or mathematical relationship; decide where the eye enters and where it goes after the last line (F03).
3. **Fit the actual text at reading size first**, then art, then decoration. Hardest fit (longest calc/table) decides the layout. Recover space from decoration, art crop or column shape, never by shrinking type.
4. Write a 4–6 line page brief in the page's `pages.json` `notes` (`design:` purpose, chosen layout + rejected challenger and why, gutter tone, edge motif + source, companion support/fade, colour key).

## 1. Type (manual p12, p18) — 864 × 648 pt page
| Role | Font | Size / leading |
|---|---|---|
| Narration, captions | Source Serif 4 Regular | 14 / 18 pt |
| Story speech | Source Sans 3 Semibold | 14 / 18 pt |
| Teaching prose, figure labels | Source Sans 3 Regular (Semibold for hierarchy) | 14 / 18 pt |
| Detached companion remark (aside to reader) | Source Serif 4 Regular | 14 / 18 pt |
| Chapter title | Source Serif 4 Semibold | 24–36 pt |
| Subheads ("Example 11", "Now you try") | Source Sans 3 Semibold | 16–19 pt |
| Display maths | sans, compatible maths glyphs | 20–30 pt (inline maths in prose = body size) |
| Running line (book · chapter · folio) | Source Sans 3 Semibold | 10–12 pt, on a quiet patch |
- 13/17 pt only with an explicit recorded exception. Never smaller for essential text.
- Outer clearance 24–32 pt for essential text; 8–14 pt between major units.
- Left-aligned prose, ragged right. Never break inside a maths group, name or unit (`.m` / `white-space: nowrap`).

## 2. Colour and gutters (p13, p24)
- Gutter colours (one per continuous exchange; change only at a place/mood/teaching transition): midnight indigo `#122A45`, peacock teal `#245857`, aubergine `#46364F`, blue slate `#384961`. Pair with warm paper (`#F7F1E3`-ish) or cool paper (`#E9EEF0`-ish).
- Busy lesson pages: only a **sliver** of gutter colour shows (a band or framing edge). Bright opener: paper/art may run to the edge.
- Reading ink is dark on a matte light field. No patterned or multicolour seams between panels.
- Maths colour has a job: deep teal (`#1F6F6B`-ish) for the moving/compared/tracked quantity, terracotta or hatched amber (`#B5603A`) for a second role. Operators, signs, fraction bars, equals stay dark ink. Must read in greyscale. Colour never reveals an answer early.

## 3. Panel edges (p14)
- Straight or softly rounded frames for independent moments / several speech turns.
- Arch entering from one side for a threshold, reveal or change of place (words below the crown).
- Open / feathered edge for a pause or a scenic companion: focal edge crisp, outer scenery dissolves into the **exact** field colour.
- Story art across the whole page + opaque near-frontal ivory/pale-sage maths panel over low-detail scenery, when one instant dominates and the maths is short.
- Book / board / card as the boundary when the object naturally groups the material.
- At thumbnail size the frame must not be the first thing noticed.

## 4. Borders and embellishment (p15–16)
- Derive the mark from a material in this scene (mirror bevel, lantern bracket, kit-box brass corner, notebook binding, canopy seam, timber joint, clock bezel, sash). Reduce to a few marks.
- Opening: arm along the top margin. Dialogue strip: short return. Dense worksheet: one corner joint is enough.
- Rules 0.5–1.1 pt, brass/silver/local colour. Strongest accent where the reader enters or finishes. Break the rule near a caption, folio, hand or figure.
- Nothing decorative may look countable (tiles, ticks, grid lines) near evidence. Cover-test: if the page reads better without it, cut it.
- Vary motif, occupied edge, gutter tone, panel shape and companion position between neighbouring pages; record them in the page brief.

## 5. Balloons and captions (p18)
- One balloon family. Ordinary reply: compact oval / soft lozenge, warm ivory. Measured explanation: wider flatter shoulder. Quiet aside: softer oval, pale tint drawn from surroundings, short clean tail. Lively interjection: tighter silhouette.
- Internal padding ≈ 4.5 pt speech, 5 pt narration box. Dark ink, fine continuous outline, short tail ending in clear space before the mouth. Near-white fills only (ivory near lamps, pale grey-blue near cool walls). No permanent per-character tint.
- Narration: pale matte tailless box, serif. First utterance first in the eye path; tails never cross.

## 6. Teaching pages with a companion (p19–20, p26)
- Build the lesson first; keep each worked group whole. The attempt ("Now you try") gets a distinct entrance and room to begin; its supplied solution sits in a **separable lower/side block** read after the attempt.
- The character gets a place to stand, lean, sit or peek **with the scenery entering the paper**: keep contact (bench, ledge, step) and cast shadow, figure opaque, outside of the setting fading **irregularly** into the paper colour. Not an oval vignette, not a floating cut-out.
- Positions: below the last item (on a ledge entering the lower margin), at a free outside edge, in an open upper corner, or for dense steps a small grounded figure at the end.
- A companion aside goes at its assigned completed boundary (after the unit), tail to the mouth, set in Source Serif 4 Regular. Paws, tails, light and props stay away from answer fields.

## 7. Mixed pages (p21) and objects (p22–23)
- Stack (scene band → bridge → teaching) when the clue is panoramic or the teaching needs width; side by side when actors need height and the text fits a shorter measure; full-page scene + opaque panel when the maths is short.
- Book/tablet/board/ticket/job card only when the object helps reading; text on a near-frontal plane, clear of folds/clips/screws; no invented labels, prices, icons.

## 8. Worked maths layout (p25)
- Preserve starting expression, each transformation and its reason. Align `=` signs when they carry meaning (use a grid: label | lhs | = | rhs).
- A result band can close a worked unit. Comparisons: equal-weight headings, aligned steps.

## 9. Proof (p30–32): record results in the page report
Read at fit-page size: start at the title/opening gesture, read all words in order, attempt the question. Then check: every printable block present (A03); type roles (E02); equation glyphs, signs, alignment (D01–D02); tails to speakers (C06); figure contact/fade/clearance (C07); feathered edge merges with exact paper tint (F09); nothing clipped.
