# MR — Square mirror recess, far-left wall alcove (opposite the cube plinth)

Source of truth: `LOCATION-BIBLE.md` §5 and §9. A shallow square brass frame in a WALL ALCOVE, just above the paving, tilted to a canopy gap; never a square set into the street floor. The only allowed letterform in the whole set is the scratched V in MR-05b.

## MR-01 · Mirror alcove, tiles piled crookedly
- family: MR
- slug: alcove-crooked
- kind: base
- parent: —
- set: samples
- anchor: yes
- candidates: 2
- aspect: 4:3
- refs:
  1. @LS-01 — approved Lantern Street master: same street; match its stalls, paving, materials, rendering and darkness
- save: `output/MR/MR-01_alcove-crooked.png`
- beats: 08A A,B,C
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: approved plate of this same dark street; match its stalls, paving, materials, rendering and light.
Primary request: angled view across the dark street towards a shallow wall alcove on the left side of the lane.
Scene/backdrop: a shallow alcove in the blue timber stall wall, with a blue rear wall and an open gap in the canopy above it letting in moonlight. Just above the paving inside it stands a shallow square brass mirror frame about a metre wide, tilted slightly back towards the canopy gap, with a fine inner brass rim. Its square mirror tiles are piled crookedly and overlap inside the frame instead of lying flat. A warm wall lamp on the alcove's left. On the paving beside the alcove, outside the walking lane, a quilted indigo padded tray and a closed opaque wooden crate. On the right side of the frame, the opposite blue stall wall is dappled with scattered broken patches of reflected moonlight.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: eye level, three-quarter angle; frame and tiles readable; clear paving in front for five figures; calm upper area.
Lighting/mood: full-moon night, arches dark, warm lamp on the left, silvery scattered reflections; something broken but fixable.
Avoid: people, animals, figures or reflections of figures; any text, letters or numbers; a square set into the street floor; broken glass; a crescent moon.
```

**Checks**
- Frame stands in a WALL ALCOVE on the left (not in the floor), tilted towards an open canopy gap.
- Tiles crooked and overlapping; scattered moonlight patches on the opposite wall at RIGHT.
- Warm lamp on the alcove's LEFT; padded tray + closed crate beside it, outside the lane.
- No people, text or broken glass.

---

## MR-01b · Frame cleared: empty frame, tiles stacked on the tray
- family: MR
- slug: alcove-empty
- kind: edit
- parent: MR-01
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @MR-01 — the approved plate to change
- save: `output/MR/MR-01b_alcove-empty.png`
- beats: 08A D; 08C A,B,C
- insets: Q07

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved mirror-alcove plate
Primary request: remove every tile from the mirror frame, so the frame is empty, secure and still slightly tilted, showing its bare backing and fine inner brass rim. Stack the square mirror tiles neatly and flat in piles on the quilted padded tray beside the alcove. The scattered light patches on the right-hand wall disappear.
Constraints: keep the camera, alcove, frame, lamp, crate, walls, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers; broken glass; any other change.
```

**Checks**
- Frame EMPTY (bare backing + rim visible); tiles stacked flat on the tray.
- No light patches on the right wall; nothing else changed.

---

## MR-01c · Mirror complete, street restored (golden light)
- family: MR
- slug: alcove-restored
- kind: edit
- parent: MR-01b
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @MR-01b — the approved plate to change
- save: `output/MR/MR-01c_alcove-restored.png`
- beats: 11A B; 11B A,B,C,D,E,F
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved mirror-alcove plate with an empty frame
Primary request: fill the frame with one flat, perfectly even grid of square mirror tiles, nine rows of nine, reflecting one complete full moon as a single unbroken image across the grid. The padded tray beside it is now empty. The whole street is now lit by warm golden light from the repaired lantern arches above, catching the brass frame and inner rim.
Constraints: keep the camera, alcove, frame position and tilt, lamp, crate, walls and composition exactly as in Image 1.
Avoid: people or figures or their reflections; any text, letters or numbers; a split or doubled moon; a crescent moon; any other change.
```

**Checks**
- Flat 9 × 9 grid (count approximate is fine at this distance) reflecting ONE full moon.
- Tray empty; warm golden street light; same camera as MR-01.
- No reflected figures, no text.

---

## MR-02 · Low close-up beside the padded tray
- family: MR
- slug: tray-low
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @MR-01b — approved mirror alcove with the empty frame and tiles on the tray: same objects, materials and light
- save: `output/MR/MR-02_tray-low.png`
- beats: 08B A,B; 08D A
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: approved plate of this same mirror alcove with its empty frame; match its objects, materials and light exactly.
Primary request: low close view on the paving beside the padded tray at the same mirror alcove.
Scene/backdrop: in the foreground, the quilted indigo padded tray with neat flat stacks of square mirror tiles, and one loose tile lying tilted on the paving just beside the tray, its mirror face catching the warm light. Behind: a corner of the empty square brass frame with its fine inner rim, the blue rear wall, and the warm wall lamp on the left.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: low camera near the paving; the loose tile left of centre; clear space on the right for a small seated cub and a crouching figure.
Lighting/mood: warm lamp glow, soft moonlight from the canopy gap; tender and quiet.
Avoid: people, animals, figures or reflections of figures; any text, letters or numbers; broken glass; a crescent moon.
```

**Checks**
- Tray with stacked tiles + ONE loose tile on the paving; frame corner, blue wall, left lamp behind.
- Space on the right for two figures; no reflections, no text.

---

## MR-03 · High three-quarter view, grid almost complete
- family: MR
- slug: grid-one-gap
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @MR-01b — approved mirror alcove: same frame, tilt, lamp, tray, crate and light
- save: `output/MR/MR-03_grid-one-gap.png`
- beats: 08E A
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: approved plate of this same mirror alcove; keep its frame, tilt, lamp, tray, crate and light exactly.
Primary request: high three-quarter view looking down at the same mirror frame from the lane.
Scene/backdrop: inside the brass frame, flat square mirror tiles fill a grid of nine rows of nine, except one empty square at a corner of the grid; the fitted tiles reflect broken pieces of the moonlit sky. The warm lamp on the left; the padded tray beside the alcove holding just one last tile; the closed crate; the paving seam in front.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: high angle; the whole grid inside the frame; space around the frame for three figures checking the rows and one placing the last tile.
Lighting/mood: warm lamp and silvery reflections; the moment before completion.
Avoid: people, animals, figures or reflections of figures; any text, letters or numbers; a complete moon yet; a crescent moon.
```

**Checks**
- Flat grid with exactly ONE empty square at a corner; reflections still broken.
- One tile left on the tray; same frame/lamp/crate geography.
- No reflected figures, no text.

---

## MR-03b · Last tile in: one full moon
- family: MR
- slug: grid-full-moon
- kind: edit
- parent: MR-03
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @MR-03 — the approved plate to change
- save: `output/MR/MR-03b_grid-full-moon.png`
- beats: 08E B
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved high view of the almost complete mirror
Primary request: set the last square tile into the empty square so the nine-by-nine grid is complete and flat; now all the tiles together reflect one complete full moon as a single unbroken image across the grid. The padded tray is now empty.
Constraints: keep the camera, frame, lamp, crate, paving and light exactly as in Image 1.
Avoid: people or figures or their reflections; any text, letters or numbers; a split, doubled or crescent moon; any other change.
```

**Checks**
- Grid complete and flat; ONE continuous full-moon reflection; tray empty.
- Everything else identical to the parent plate; no people, no text.

---

## MR-04 · Low reflection view beside the completed mirror
- family: MR
- slug: reflection-low
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @MR-03b — the completed mirror: same tiles, rim and reflection
  2. @MR-01b — the same alcove at street level: wall, lamp and materials
- save: `output/MR/MR-04_reflection-low.png`
- beats: 08F A,B
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: the completed mirror in this alcove (tiles, rim, reflection). Image 2: the same alcove at street level (wall, lamp, materials).
Primary request: low view at the side of the completed square mirror, close to its frame.
Scene/backdrop: camera low beside the frame; the fine inner brass rim runs across the foreground; the flat grid of fine-seamed mirror tiles fills the middle, reflecting the moonlit canopy edge and a soft clear surface where a face will later be reflected; the blue rear wall and the warm lamp glow at one side; pale paving at the bottom.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: low and intimate; a large clear area of mirror surface in the centre; space in front for a small cub standing and a figure crouching.
Lighting/mood: soft moonlight and warm lamp light; gentle reassurance.
Avoid: people, animals, figures or any reflected figure; any text, letters or numbers; a crescent moon.
```

**Checks**
- Completed fine-seamed mirror, rim in foreground, blue wall + lamp anchors.
- Large clear reflective area; NO reflected figures; no text.

---

## MR-05 · Inner brass rim close-up in restored light (dusty)
- family: MR
- slug: rim-dust
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @MR-01c — approved completed mirror in restored golden light: same frame, rim, tiles and lamp
- save: `output/MR/MR-05_rim-dust.png`
- beats: —
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: approved plate of this same completed mirror in golden light; match its frame, rim, tiles and lamp exactly.
Primary request: close-up of the inner brass rim along one corner of the completed mirror frame.
Scene/backdrop: the polished inner brass rim, coated with a thin film of fine grey dust; one corner of the flat tile grid beside it, reflecting golden light; the warm wall lamp at the left edge; golden arch light raking low across the rim so every speck of dust shows.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: close; the dusty rim runs diagonally through the frame with a clear, evenly dusty stretch in the centre; space at one side for a face bending close.
Lighting/mood: warm golden raking light; a discovery about to happen.
Avoid: people, hands, figures or reflections; any text, letters, numbers or marks in the dust; a crescent moon.
```

**Checks**
- Dusty inner rim, corner of the tile grid, left lamp anchor; golden raking light.
- The dust is unmarked (no letters); no figures.

---

## MR-05b · The scratched V appears in the dust
- family: MR
- slug: rim-v
- kind: edit
- parent: MR-05
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @MR-05 — the approved plate to change
- save: `output/MR/MR-05b_rim-v.png`
- beats: 11A A
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved dusty-rim close-up
Primary request: in the centre of the dusty stretch of the inner brass rim, show one single capital letter V scratched through the dust into the brass, a fine bright scratch caught by the golden light. It looks old and deliberate, not freshly carved.
Constraints: keep the camera, rim, dust, tiles, lamp, lighting and colours exactly as in Image 1.
Avoid: people, hands or figures; any other text, letters, numbers or marks; any other change.
```

**Checks**
- Exactly ONE scratched capital V in the rim dust, caught by golden light.
- No other marks or letters; nothing else changed.
