# KB — Projector-kit area, centre of the right-wall bench

Source of truth: `LOCATION-BIBLE.md` §4 (projector kits). Labels stay blank (the exact words are added later). The only exact count is KB-02b / KB-02c: 3 lenses + 5 rings.

## KB-01 · Kit bench medium: stock boxes, empty kit boxes, sample board
- family: KB
- slug: kit-bench
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @TB-01 — approved timing bench: the same continuous bench, blue wall, lamps and materials (the timing device sits at this view's left edge)
  2. @LS-01 — approved Lantern Street master: same street and darkness
- save: `output/KB/KB-01_kit-bench.png`
- beats: 06A A,B,C
- insets: Q04

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: the left end of this same workbench (bench, blue wall, lamps, materials); its timing device sits at this view's left edge. Image 2: the same dark street.
Primary request: medium view of the centre of the same long pale workbench: the projector-kit area.
Scene/backdrop: on the bench, two open wooden supply boxes side by side, each with a blank brass label plate on its front: the left one heaped with small round blue glass lenses, the right one heaped with small brass rings that shine gold. Next to them, several shallow empty kit boxes lined with indigo padding, and one blank pale wooden sample board. Fixed to the blue wall above, a short brass lantern-test rail with two empty lamp-head brackets. A warm work lamp. At the far left edge, the timing device; at the far right edge, the first upright of a brass rack.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: eye level; boxes and board readable; a clear spot on the bench between the two supply boxes; paving in front clear for five figures; a dark gap under the bench at floor level.
Lighting/mood: warm lamp light making the rings glow gold and the lenses glint blue; cool darkness beyond; organised and inviting.
Avoid: people, animals, figures; any text, letters or numbers on labels; a finished lantern head; filled kit boxes; a crescent moon.
```

**Checks**
- Two open supply boxes: blue lenses LEFT, brass rings RIGHT; blank label plates.
- Empty padded kit boxes, blank sample board, brass test rail above.
- Timing device at left edge, rack upright at right edge; no finished head; no people or text.

---

## KB-02 · Overhead sample board (empty)
- family: KB
- slug: sample-board
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @KB-01 — approved kit bench: same boxes, board, bench and light
- save: `output/KB/KB-02_sample-board.png`
- beats: —
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: approved plate of this same kit bench; match its boxes, board, wood and light exactly.
Primary request: overhead view looking down at the blank sample board on the same bench.
Scene/backdrop: in the centre, the pale wooden sample board with a soft felt surface, empty. In the top corners, the edges of the two open supply boxes, blue glass lenses on the left and brass rings on the right, each with the corner of a blank brass label plate. Along the bottom, the pale bench edge.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: top-down; board centred with generous empty space; space at the edges for hands.
Lighting/mood: warm even lamp light; precise.
Avoid: people, hands, figures; any text, letters or numbers; loose parts on the board; a crescent moon.
```

**Checks**
- Top-down; empty board centred; box corners top-left (lenses) and top-right (rings).
- No parts on the board; no text.

---

## KB-02b · One sample set: exactly 3 lenses and 5 rings
- family: KB
- slug: sample-set
- kind: edit
- parent: KB-02
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @KB-02 — the approved plate to change
- save: `output/KB/KB-02b_sample-set.png`
- beats: 06B A,B,C
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved overhead sample-board plate
Primary request: lay one sample set on the board: exactly three round blue glass lenses in a row, each with one brass ring beside it (three rings), and, set a little apart, exactly two more brass rings for the supports. Exactly three lenses and five rings in total, all clearly separate and countable.
Constraints: keep the camera, board, supply boxes, bench, lighting and colours exactly as in Image 1.
Avoid: people, hands or figures; any text, letters or numbers; extra parts; any other change.
```

**Checks**
- EXACTLY 3 lenses and 5 rings (3 beside the lenses + 2 apart), all countable.
- Nothing else changed; no text.

---

## KB-02c · Padded sample kit + blank packing sheet
- family: KB
- slug: sample-kit
- kind: edit
- parent: KB-02b
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @KB-02b — the approved plate to change
- save: `output/KB/KB-02c_sample-kit.png`
- beats: 06C A
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved sample-set plate
Primary request: move the three lenses and five rings into one shallow kit box lined with indigo padding, now standing open on the board, each part in its own padded pocket (three lenses, five rings, all visible and countable). Beside it, place one blank pale paper sheet with an ordinary pencil.
Constraints: keep the camera, board, supply boxes, bench, lighting and colours exactly as in Image 1.
Avoid: people, hands or figures; any text, letters, numbers or writing on the sheet; extra parts; any other change.
```

**Checks**
- One open padded kit box with exactly 3 lenses + 5 rings, countable.
- Blank sheet + pencil beside it; no writing.
