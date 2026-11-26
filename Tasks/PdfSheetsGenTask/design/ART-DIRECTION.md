# ChandRush art direction: A4 "Step Inside" (2026-11-22)

> **2026-11-23 · User-approved look: B1 "Ledger Plate" (CH01 P039).** Reading text sits on calm light shapes (warm paper #F7F1E3 / ivory), never on dark glass or a busy scene; fonts, sizes and maths colours follow manual V09; the page's creativity goes into a border built from the location plate's materials (manual pp.15–16). Story pages use the same family with the location's own materials. Where this file (A4) disagrees, B1 + LESSONS.md win.


> **2026-11-26 · Category reference pages:** `design/references/README.md` has one model page per category (opener, action-story, dialogue-story, story-maths, concept, worked-example, practice-set, diagram-led; `pages.json` → `category`). Open the one for your page before you brief or build. Copy its quality bar and structure, never its layout; similar pages must not repeat a design. Story categories follow the user's look example `references/look-P107-story.png`.

This file governs how a page **looks**. `manual-v09.md` still governs type sizes, maths tagging and proofing.
Kit: `design/kit.css`. Reference pages: `CH01/P005` (teaching opener) and `CH01/P039` (worked example plus "Now you try").
Copy markup from their `index.html`. Archived looks: `design/archive-a3/` (A3 "Lantern Street": paper objects on a dark stage).

## The user's needs (verbatim, in order)
1. "It is a page of a child's book! It should be creative: colours, some art, some unique things."
2. "The graphics have become kiddish for an 11-year-old. We need graphics that are aspirational for an 11-year-old. He should find the book cool and aspirational for his age."
3. "The graphics and colours of the pages should be in the same family as the graphics and colours of the location images. The illustration style should also match."
4. "Try a completely different design! According to my needs."

## 1. The idea: the page IS the place
A3 put paper cards on a flat dark stage, and the location paintings appeared only as small cut-outs. A4 turns that around.
- **World:** the page's own location plate fills the whole sheet, crisp and full-bleed, like a still from a film.
  It is graded for the story, and characters stand inside it.
- **Glass:** every block of reading sits on a pane of glass cut from that same picture. The pane shows the scene behind it, blurred and tinted. It has no paper, frame, corner ornaments or icons. A lamp-gold hairline runs along its top edge.
- **Light:** maths figures are drawn as brass and lamplight on top of the world: gauges, number lines, and counted objects cut from the art itself.
- **Type:** film-poster titles (Big Shoulders Display 800, caps, 52–60 pt) with lamp glow. Section cues are tracked caps with a brass dash.

Why this works for an 11-year-old: it looks like a film poster or a premium game screen, never a worksheet, and it is literally the location art.

## 2. Make the world (free: no image calls)
```
python3 pipeline/pagekit.py scene  PdfSheetsGenTask/CH01/P039 BagroundGenTask/out/plates/S04-B01.png --mirror --blank 246,272,392,340 --blank 524,302,698,383
python3 pipeline/pagekit.py cutout PdfSheetsGenTask/CH01/P039 BagroundGenTask/out/plates/S04-B01.png PACK --poly "772,288 969,318 ..."
```
- `scene` makes `SCENE.jpg` (the world) and `GLASS.jpg` (the same picture blurred, for the panes).
  - `--blank` wipes painted words and numbers (in plate pixels), so no stray numbers or answers show.
  - `--mirror` flips the plate so its busy part sits under the reading panes and its open, light part stays visible.
  - `--crop` zooms in.
- `cutout` lifts a character or prop out of existing art along a traced outline. To trace, view a gridded zoom of the source. Use it:
  - to stand a character in the scene at a believable scale;
  - to repeat a painted object as a counted set (P039's nine packs are one box from S04-B01, nine times).
- **Story grades are allowed and encouraged.** P005 turns one street half frozen (cold grade, frost, snow) and half lamp-warm (script: `design/a4-tools/p005_scene.py`; page generators for both samples are in `design/a4-tools/`). Keep the plate's palette: the grade shifts warmth, never hue family.
- The art stays painterly. Never place flat vector scenery, cartoon icons or clip-art over it.

## 3. Page anatomy (864 × 648 pt)
| Layer | Markup | Rule |
|---|---|---|
| world | `<div class="scene"><img src="assets/img/SCENE.jpg"> <i class="shade-top"> <i class="vignette"> (<i class="shade-bottom">)</div>` | always full-bleed |
| light | `<i class="bloom">` / `.bloom.moon` over lamps and the moon | 1–2 per page |
| title | `<h1 class="marquee">` (+ `<span class="ice">`) | top-left over the shade, 52–60 pt |
| folio | `<div class="folio">` + moon-phase SVG + 2-digit page number, top-right | the moon waxes as the chapter goes on: lit fraction = page / last page (CH01 last = 108) |
| reading | `.glass` panes (below) | 4–6 panes, gutters 10–14 pt, edges 20–26 pt from the trim |
| people | `.actor` (cut-out PNG) standing in the scene, cropped by the trim or on a surface | at least one character per teaching page |
| speech | `.say` (Caveat) with the curved `svg.tail` | only manuscript bubbles and asides |

## 4. Glass by role (same role, same glass, all book long)
| Text role | Glass | Notes |
|---|---|---|
| narrator welcome / bridge caption | `.glass.frost` or default, `p.voice` (Source Serif 4 italic) | a `.rule-brass` separates it from teaching prose in the same pane |
| teaching prose | default dark glass (or `.frost` on a cold scene) | Source Sans 3 14/18 |
| question, example question, "Now you try" | `.glass.marble` (light, ink text) | the reader's task is always the light pane |
| "Pause and think" | default glass with an inline `.cue.run` | |
| worked steps, "Check your …" answers | default dark glass, `.lift` for the main one | the answer pane always comes after (below or right of) its question |
| figures inside answers | inline SVG in the pane | answer-only labels live here only |

Every pane needs `--x`/`--y` equal to its `left`/`top`, so the blurred world lines up:
`<div class="glass marble" style="left:262pt; top:20pt; width:512pt; height:110pt; --x:262pt; --y:20pt"><img class="under" src="assets/img/GLASS.jpg" alt="">…</div>`

## 5. Colour (sampled from the plates)
| Use | Colour |
|---|---|
| night / dark glass | #0a1428, rgba(14,28,62,.8) |
| royal lacquer | #234d95 |
| brass, highlight | #d6a64e, #f6dca0 |
| lamp gold (warm, tracked quantity on dark glass `.mt`) | #f7c684 / #f5c86a |
| moonlight (cold, second role on dark glass `.mr`) | #cfe0fa |
| marble glass | #f3ebdc |
| ice | #d7e7fb |
| ink on light glass | #121a33; `.mt` #1f4f9a and `.mr` #a3561c on light glass |

A page may re-map `.mt`/`.mr` when the story has a natural pair (P005: Sarah's cold temperatures are moonlight, Sam's warm ones are lamp gold). Operators stay in the text colour.

## 6. Maths drawn in the world
- Draw figures as exact SVG: brass lines, glass, lamp and moon colours, solid fills for small shapes.
- Better still, use counted cut-outs from the art. Counts must be exact and countable at a glance: rows of 3, no hidden items.
- Question figures show only the question's data. Results appear only in answer panes.
- Examples: P005's brass gauge, −15…15, with tags at 12°C and −12°C. P039's nine packs on the marble counter, plus one pack's exact contents (19 pencils, 3 erasers, 7 pens) and seven velvet pouches.

## 7. Banned
- **Kiddish:** bunting, marigolds, striped awnings, pastel blocks, washi tape, rounded "fun" fonts, emoji-style icons, cartoon suns and snowflakes, stickers.
- **Off-world:** neon cyan, HUD grids, sci-fi glow lines.
- **Worksheet:** flat cards on a flat colour, the same template page after page, empty slabs.
- **A3 leftovers:** paper tickets, tags, ledgers, flaps, ornament frames, jharokha windows, light strings.

## 8. Unique things (2–3 per page, from that page's story)
Examples:
- P005: the street freezes from right to left, snow falls only on Sarah's side, and rime creeps in at the corner of the frost glass.
- P039: the nine packs stand on the bench under the lamp, the bench's own white bird watches them, and Tez sits on the counter edge.
- Never repeat the same delight on neighbouring pages.

## 9. The brief (pages.json `"art"`)
Write the brief as JSON with these fields:
`{"idea", "scene": {"plate", "grade", "mirror", "blank": [...], "crop"}, "panes": {role: glass}, "hero", "illustrate", "cast", "colour", "delights": [...], "folio", "varies"}`

## 10. Scorecard (ship at 8/10 or better, and every must)
**Musts:**
- the world is the page's own plate, full-bleed;
- nothing on the §7 list;
- maths PASS;
- text verbatim;
- questions before answers;
- no painted numbers that conflict with the maths.

**Scored (1 point each):**
1. The first glance reads as a film still or game screen, not a worksheet.
2. The world stays visible on at least 35% of the page.
3. A character is in the scene at a believable scale.
4. The maths is drawn, not only written.
5. The title has impact.
6. The glass roles are consistent.
7. There are 2–3 page-specific delights.
8. The colour story is clear (warm against cold, or tracked against second).
9. Nothing is cramped (≥ 10 pt gutters, no text within 20 pt of the trim).
10. It differs from its neighbours.
