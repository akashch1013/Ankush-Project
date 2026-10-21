# CP — Cube plinth, readiness board, down-pull handle and moonline joint (right side, opposite the mirror)

Source of truth: `LOCATION-BIBLE.md` §6 and §9. Board order (left→right) LIFT, RHYTHM, SUPPLIES, MIRROR, CUBE — labels stay blank; only the lamp states change. The joint is a flat square brass cover in the paving: never a socket, box or second switch.

## CP-01 · Cube plinth medium: uneven towers, frame raised, four lamps white
- family: CP
- slug: plinth-towers
- kind: base
- parent: —
- set: samples
- anchor: yes
- candidates: 2
- aspect: 4:3
- refs:
  1. @LS-01 — approved Lantern Street master: same street; match its stalls, paving, canopy, materials, rendering and darkness
- save: `output/CP/CP-01_plinth-towers.png`
- beats: 09A A,B,C,D; 09B A,B
- insets: Q08, Q09

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: approved plate of this same dark street; match its stalls, paving, materials, rendering and light.
Primary request: medium view from the lane facing a low square plinth on the right-hand side of the dark street, under a small indigo canopy.
Scene/backdrop: a knee-high square plinth of pale stone with brass edging, under an indigo canopy on slim posts. Four slim brass rods rise from its corners; a square brass top frame rides high on them, unable to close. On the plinth, small palm-sized lantern cubes (brass edges, frosted glass) stand in thin, uneven towers of different heights. To the plinth's right, on the blue wall, a panel of five small round lamps in a row, each above a blank brass label plate: the first four glow white, the fifth is dark. Beside it, a tall brass down-pull lever handle in the raised position. In the paving at the plinth's front-right corner, a flat square brass cover lies flush over a thin unlit silver track running along the paving's edge.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1; elegant, not dense machinery.
Composition/framing: eye level; plinth centre, panel and handle right, floor cover visible; paving clear in front for five figures; calm canopy and sky at the top.
Lighting/mood: arches dark; warm work lamp and the four white lamps; unlit lanterns; an unfinished puzzle.
Avoid: people, animals, figures; any text, letters or numbers on plates; an enclosed workshop bay; a cylindrical socket or floor box; a guide drawing; a crescent moon.
```

**Checks**
- Low plinth under an indigo canopy; brass corner rods; top frame stuck HIGH; thin uneven lantern towers.
- Panel on the plinth's RIGHT: five lamps, FIRST FOUR white, FIFTH dark; blank plates; lever RAISED.
- Flat square brass cover flush at the front-right corner over an unlit silver track.
- No bay/socket/box, no people, no text.

---

## CP-01b · Three solid layers, the fourth being placed
- family: CP
- slug: plinth-layers
- kind: edit
- parent: CP-01
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @CP-01 — the approved plate to change
- save: `output/CP/CP-01b_plinth-layers.png`
- beats: 09B C
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved cube-plinth plate
Primary request: rebuild only the lantern cubes on the plinth: three complete, flat, solid layers stacked neatly, each layer four cubes by four, with a fourth layer only partly placed on top (about half its cubes). No thin towers remain. The top frame stays raised on its rods.
Constraints: keep the camera, plinth, canopy, lamp panel (four white, fifth dark), lever, floor cover, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers; any other change.
```

**Checks**
- Three solid 4 × 4 layers + a partial fourth (distant count may be approximate).
- Frame still raised; panel still four white + fifth dark.

---

## CP-01c · Cube complete, top frame fastened (fifth lamp still dark)
- family: CP
- slug: plinth-cube-complete
- kind: edit
- parent: CP-01b
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @CP-01b — the approved plate to change
- save: `output/CP/CP-01c_plinth-cube-complete.png`
- beats: 09C A
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved cube-plinth plate
Primary request: complete the fourth layer so the lantern cubes form one solid cube, four by four by four, with straight even sides; lower the square brass top frame along its corner rods until it sits flush on top of the cube, fastened. The fifth lamp on the panel stays dark.
Constraints: keep the camera, plinth, canopy, lamp panel, lever (raised), floor cover, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers; any other change.
```

**Checks**
- One SOLID 4 × 4 × 4 cube; top frame lowered flush on it.
- Panel still four white + fifth dark; lever raised.

---

## CP-01d · All five readiness lamps white (lever raised)
- family: CP
- slug: plinth-all-white
- kind: edit
- parent: CP-01c
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @CP-01c — the approved plate to change
- save: `output/CP/CP-01d_plinth-all-white.png`
- beats: 09C B; 10A A,B; 10B A; 10H B
- insets: Q10, Q11

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved cube-plinth plate
Primary request: change only the fifth lamp on the wall panel: it now glows white, so all five lamps glow white. Nothing else lights up: the arches and the silver track stay dark.
Constraints: keep the camera, cube, frame, lever (raised), floor cover, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers; lit arches; any other change.
```

**Checks**
- All FIVE lamps white; lever still raised; track and arches still dark.
- Everything else identical to the parent plate; no people, no text.

---

## CP-01e · Lever pulled down (street still dark)
- family: CP
- slug: plinth-lever-down
- kind: edit
- parent: CP-01d
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @CP-01d — the approved plate to change
- save: `output/CP/CP-01e_plinth-lever-down.png`
- beats: 10D A,B
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved cube-plinth plate
Primary request: change only the tall brass lever handle beside the panel: it is now pulled fully down. All five lamps stay white; the silver track and the arches stay dark.
Constraints: keep the camera, cube, frame, panel, floor cover, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers; lit arches; any other change.
```

**Checks**
- Lever fully DOWN; five lamps white; still dark street.
- Everything else identical to the parent plate; no people, no text.

---

## CP-02 · Readiness board insert, all lamps dark
- family: CP
- slug: board-dark
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @CP-01 — approved cube plinth: the same wall panel, lamps, plates, lever and canopy
- save: `output/CP/CP-02_board-dark.png`
- beats: —
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel insert; no characters, no lettering; landscape 4:3
Input images: Image 1: approved plate of this same wall panel beside the cube plinth; match its design, brass, blue wall and light exactly.
Primary request: close-up insert of the readiness panel on the blue wall.
Scene/backdrop: the blue wall panel with five small round lamps evenly spaced in one horizontal row, each with its own blank brass label plate directly below it; the top of the tall brass lever handle at the right edge; a slice of the indigo canopy post at the left edge.
State: all five lamps dark (unlit glass).
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: straight-on; all five lamps and plates large, evenly spaced and fully inside the frame; equal margins.
Lighting/mood: dim warm work light; waiting.
Avoid: people, hands, figures; any text, letters, numbers or symbols on the plates; a crescent moon.
```

**Checks**
- Exactly FIVE round lamps in a row, each with a BLANK plate below; all dark.
- Lever top at right edge, canopy post at left edge.

---

## CP-02a · Board: first lamp white
- family: CP
- slug: board-1
- kind: edit
- parent: CP-02
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @CP-02 — the approved plate to change
- save: `output/CP/CP-02a_board-1.png`
- beats: 04C B
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved readiness-panel plate
Primary request: change only the lamps: the first lamp from the left now glows bright white; the other four stay dark.
Constraints: keep the camera, panel, plates, lever, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers; any other change.
```

**Checks**
- Only lamp 1 (leftmost) white; lamps 2–5 dark.
- Everything else identical to the parent plate; no people, no text.

---

## CP-02b · Board: first two lamps white
- family: CP
- slug: board-2
- kind: edit
- parent: CP-02
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @CP-02 — the approved plate to change
- save: `output/CP/CP-02b_board-2.png`
- beats: 05E D
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved readiness-panel plate
Primary request: change only the lamps: the first two lamps from the left now glow bright white; the other three stay dark.
Constraints: keep the camera, panel, plates, lever, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers; any other change.
```

**Checks**
- Lamps 1–2 white; lamps 3–5 dark.
- Everything else identical to the parent plate; no people, no text.

---

## CP-02c · Board: first three lamps white
- family: CP
- slug: board-3
- kind: edit
- parent: CP-02
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @CP-02 — the approved plate to change
- save: `output/CP/CP-02c_board-3.png`
- beats: 07E B
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved readiness-panel plate
Primary request: change only the lamps: the first three lamps from the left now glow bright white; the last two stay dark.
Constraints: keep the camera, panel, plates, lever, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers; any other change.
```

**Checks**
- Lamps 1–3 white; lamps 4–5 dark.
- Everything else identical to the parent plate; no people, no text.

---

## CP-02d · Board: first four lamps white
- family: CP
- slug: board-4
- kind: edit
- parent: CP-02
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @CP-02 — the approved plate to change
- save: `output/CP/CP-02d_board-4.png`
- beats: 08F C
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved readiness-panel plate
Primary request: change only the lamps: the first four lamps from the left now glow bright white; only the last (rightmost) lamp stays dark.
Constraints: keep the camera, panel, plates, lever, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers; any other change.
```

**Checks**
- Lamps 1–4 white; lamp 5 dark.
- Everything else identical to the parent plate; no people, no text.

---

## CP-02e · Board: all five lamps white
- family: CP
- slug: board-5
- kind: edit
- parent: CP-02
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @CP-02 — the approved plate to change
- save: `output/CP/CP-02e_board-5.png`
- beats: 09C B
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved readiness-panel plate
Primary request: change only the lamps: all five lamps now glow bright white.
Constraints: keep the camera, panel, plates, lever, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers; any other change.
```

**Checks**
- All five lamps white.
- Everything else identical to the parent plate; no people, no text.

---

## CP-03 · Lever down beside five white lamps, dark arch beyond
- family: CP
- slug: lever-dark-arch
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @CP-01e — approved plinth with all five lamps white and the lever pulled down: same lever, panel, canopy and light
- save: `output/CP/CP-03_lever-dark-arch.png`
- beats: 10C A,B,C
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: approved plate of this same lever, panel and canopy; match their design, materials and light exactly.
Primary request: view from beside the tall brass lever handle, looking up past it to a lantern arch over the street.
Scene/backdrop: in the foreground, the brass lever handle pulled fully down; beside it the wall panel with all five lamps glowing white above their blank plates; at the frame side, the edge of the indigo canopy and the complete lantern cube. Beyond and above, a tall indigo lantern arch spans the street, completely dark against the moonlit sky.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: slightly low angle; room around the handle for a hand still resting on it and for a figure at the left looking up; the dark arch clearly readable in the upper half.
Lighting/mood: five white lamps and warm work light near, the arch dark and silent; a disappointing pause.
Avoid: people, hands, figures; any text, letters or numbers; lit arches; sparks or broken bulbs; a crescent moon.
```

**Checks**
- Lever DOWN; five lamps white; tall arch DARK above.
- No sparks or effects; no people or text.

---

## CP-04 · Low view along the moonline to the crooked brass cover
- family: CP
- slug: moonline-cover-crooked
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @CP-01e — approved plinth with the complete cube, five white lamps and the lever down: same objects, floor cover and light
- save: `output/CP/CP-04_moonline-cover-crooked.png`
- beats: 10D C; 10E A
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: approved plate of this same plinth; match its cube, panel, lever, floor cover, materials and light exactly.
Primary request: low view along the thin silver track set in the paving, towards the front-right corner of the cube plinth.
Scene/backdrop: camera low on the pale paving; the narrow unlit silver track runs from the foreground to a flat square brass cover set in the paving at the plinth's corner; the cover sits slightly crooked, one edge raised. Above: the indigo canopy post, the lever pulled down, the panel with five white lamps, and the complete lantern cube on the plinth.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: very low angle; track leading the eye to the cover; space beside the track for a kneeling figure and for a lamp held low.
Lighting/mood: dark street, warm low light along the paving; a clue on the ground.
Avoid: people, hands, figures; any text, letters or numbers; a socket, box or second switch; a lit track; a crescent moon.
```

**Checks**
- Unlit silver track leading to a FLAT square brass cover sitting CROOKED at the plinth corner.
- Lever down and five white lamps above; no socket/box; no people or text.

---

## CP-04b · Cover lifted off, recess open
- family: CP
- slug: moonline-cover-open
- kind: edit
- parent: CP-04
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @CP-04 — the approved plate to change
- save: `output/CP/CP-04b_moonline-cover-open.png`
- beats: 10G A
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved low moonline plate
Primary request: lift the square brass cover off and lay it flat on the paving beside the opening, clear of the track, exposing a small dark square recess in the paving where the silver track runs in from both sides.
Constraints: keep the camera, track, plinth, lever (down), lamps, lighting and colours exactly as in Image 1.
Avoid: people, hands or figures; any text, letters or numbers; any other change.
```

**Checks**
- Cover lying flat BESIDE an open square recess; track runs into it.
- Everything else unchanged.

---

## CP-04c · Cover flush, the moonline glowing through
- family: CP
- slug: moonline-glowing
- kind: edit
- parent: CP-04
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @CP-04 — the approved plate to change
- save: `output/CP/CP-04c_moonline-glowing.png`
- beats: 10I A
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved low moonline plate
Primary request: the brass cover now sits perfectly flat and flush in the paving, and the thin silver track glows with one bright, continuous line of silvery light running from the foreground past the cover; a first warm golden glow begins to spill from above.
Constraints: the lever stays pulled down and the five lamps stay white; keep the camera, plinth, cube, lighting direction and colours otherwise as in Image 1.
Avoid: people, hands or figures; any text, letters or numbers; a break in the light line; any other change.
```

**Checks**
- Cover FLUSH; the track lit as one CONTINUOUS line past it.
- Lever down; five white lamps; no people or text.

---

## CP-05 · Open joint: two disconnected track ends, screws, black dust
- family: CP
- slug: joint-open
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @CP-04b — approved view of the same open recess: match its paving, track, cover and light
- save: `output/CP/CP-05_joint-open.png`
- beats: 10F A,B
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: approved plate of this same open recess; match its paving, track, cover, materials and light exactly.
Primary request: low close-up looking into the small open recess in the paving beneath the lifted brass cover.
Scene/backdrop: inside the shallow square recess, the two ends of the silver track have been pulled apart with a clear gap between them; two or three small brass screws lie loose; fine black dust fills the empty screw holes. The plinth's stone corner and a paving seam frame the recess; the lifted cover lies flat at the edge of the frame.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: close and low; the gap and the dusty screw holes sharp at the centre; warm lamp light coming in from one side; space at the edge for a worried face.
Lighting/mood: warm lamp light in a dark street; evidence of deliberate damage, quiet worry.
Avoid: people, hands, figures; any text, letters or numbers; wires, sockets or switches; sparks; a crescent moon.
```

**Checks**
- Two DISCONNECTED track ends with a clear gap; loose screws; BLACK dust in the holes.
- Plinth corner + paving seam anchors; no wires/switches; no text.

---

## CP-05b · Joint rejoined
- family: CP
- slug: joint-rejoined
- kind: edit
- parent: CP-05
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @CP-05 — the approved plate to change
- save: `output/CP/CP-05b_joint-rejoined.png`
- beats: 10H A
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved open-joint close-up
Primary request: join the two silver track ends end to end so the gap is closed, and screw them down firmly with the small brass screws; a little black dust remains around the screw heads. The lifted brass cover still lies at the edge, ready to go back.
Constraints: keep the camera, recess, paving, plinth corner, lighting and colours exactly as in Image 1.
Avoid: people, hands or figures; any text, letters or numbers; any other change.
```

**Checks**
- Track ends JOINED and screwed; gap closed; traces of dust remain.
- Everything else identical to the parent plate; no people, no text.
