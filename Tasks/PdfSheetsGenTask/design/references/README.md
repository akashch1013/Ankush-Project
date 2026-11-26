# Category reference pages

One model page per page category, each made with the normal workflow (plan → brief → panel art → build → math-check → review). They are **design guides, not templates**. The user's words: "every page will have his randomness while keeping structure maintained"; "you will not repeat the same design for the similar type of page."

## How to use them (art-director, page-builder)
1. Read the page's `category` in `pages.json`. If it has none, pick one with the table below; a page that fits two categories takes the one its biggest element belongs to.
2. Open that category's preview here (`<category>-CH01-Pxxx.png`). Open the PDF in `Output/CH01/` only to check a detail.
3. **Copy:**
   - the quality bar
   - the structural principle (the "Structure that stays" column)
   - the shared musts below
4. **Never copy:**
   - its layout grid
   - its ground colour
   - its border ornament
   - its hero placement
5. Before you brief, look at the last two pages built in the same category. The new page must differ from both on at least three of:
   - grid
   - ground colour
   - border motif
   - hero position
   - where the companion enters

## Categories

| Category | A page belongs here when… | Reference | Structure that stays | Must vary |
|---|---|---|---|---|
| `opener` | It opens a chapter, section or new location: one establishing moment, a title, little text. | CH01 P001 | A threshold: one dominant image framed as a gate or arch the reader steps through. Deep ground with subtle gradation. Title and one caption only. Big quiet space. | The gate shape (arch, door, curtain, window, lift gate). Ground hue. Title placement. Which way the cast faces. |
| `action-story` | Story only, driven by physical action or a comic beat; few words. | CH01 P002 | Read in one sweep: a set-up strip, then the pay-off panels. Light or motion carries across the gutter. Balloons on the art. | Strip orientation (wide, tall, diagonal). Panel count 2–5. Where the beat lands. Colour story. |
| `dialogue-story` | Story only, driven by talk: several speakers, many balloons, often around one object. | CH01 P004 | Establish the room, show the object, then the speakers in close crops. Balloons in reading order on the art, tails at mouths. | The object's panel shape. How the crops are arranged. Ground hue. Border motif. |
| `story-maths` | Story panels and teaching blocks share the page. | CH01 P033 | Two voices: the lesson on calm light panes, and the story beside it doing the same maths in the scene. A colour code ties them. | Split direction (column, band, inset). Which voice leads. Ground material. |
| `concept` | Teaching prose that builds an idea; one figure supports it. | CH01 P064 | Prose-led reading field on a light pane inside a border drawn from the plate (frame, arch, recess). One exact figure as hero. Companion as an aside. | Frame type. Column count. Where the figure sits. Companion side. |
| `worked-example` | An example question followed by worked solution steps (Example N, Now you try). | CH01 P076 | Question first, then steps as a ledger the eye walks down. Results on tags or plates. The maths is the picture. | Step device (rails, tags, ribbons, stairs). Accent colours. Page material. |
| `practice-set` | Practice questions or exercise sets, many short items, answers separable. | CH01 P077 | Rhythm: equal question cards on a quiet ground, a rule linking them, answers on covered flaps or a separate strip. | Card count and grid. The rule motif. Whether answers fold, flip or sit in a strip. |
| `diagram-led` | A figure, diagram, table or grid carries the page (a word problem with figures, a big table). | CH01 P043 | One dominant exact SVG figure. The question figure never leaks the answer. Text kept to a side or band. | The figure's surface (mat, board, map, wall). Zone split. Border material. |

Look families:
- **Story categories:** `look-P107-story.png`, the user's own example. Deep graded ground, brass pinstripe border with corner caps, a lantern or plate ornament, a brass-coin folio, tight gutters (6–10 pt), light caption boxes and white balloons on the art.
- **Teaching categories:** the B1 "Ledger Plate" look (`ART-DIRECTION.md`, approved page CH01 P039). Cream reading field, border built from the plate's own materials, manual V09 fonts, sizes and maths colours.

## Shared musts (from LESSONS.md, 2026-11-25)
- Label on the border: `CHAPTER 01 - NUMBERS - PG 001` (chapter number, topic and page change).
- Story balloons and captions sit on the art, never in gutters.
- Never alter or invent background objects to fit the story. Stage the scene inside the plate as painted.
- Read the page before and the page after before planning or building.
- Characters only as on their sheets. Tara is always calm and wise, never animated.
- Aspirational for age 11, never kiddish. Maths exact and tagged (`mathcheck.py`). Text verbatim (`textcheck.py`).
