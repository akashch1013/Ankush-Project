# LB — Goods-lift bay, controller, shaft and lower store

Source of truth: `LOCATION-BIBLE.md` §3 and §9 (car positions, gate, panel, warnings). One car, one supply cart, always.

## LB-01 · Lift bay, street-side medium (car at street level, gate shut)
- family: LB
- slug: street-side
- kind: base
- parent: —
- set: samples
- anchor: yes
- candidates: 2
- aspect: 4:3
- refs:
  1. @LS-01 — approved Lantern Street master: same street; match its materials, palette, rendering and darkness
  2. `../../Locations/CH 01 LOCATIONS/LANTERN LIFT STREET LEVEL 0 CLOSE UP.png` — older lift art: controller and shaft design ideas only; ignore its hinged doors, numbers and labels
- save: `output/LB/LB-01_street-side.png`
- beats: 01C A; 01D B,C; 02B D
- insets: Q02

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: approved plate of this same dark street (materials, palette, rendering, light). Image 2: older lift art; use only its controller and shaft design ideas; ignore its hinged doors, numbers and labels.
Primary request: street-side medium view of the goods-lift bay recessed into the blue left wall of the dark street.
Scene/backdrop: centre-left, a tall narrow lift shaft set into the blue timber wall, closed at street level by a folding brass lattice safety gate; behind it one small empty open-cage goods car (brass frame, timber floor) stands level with the street. A flush blank brass mark is set in the paving at the gate. At the shaft's right edge, a vertical indigo enamel strip with evenly spaced blank brass ticks above and below a bolder tick at street level. Centre-right, a waist-high blue-and-brass controller on the paving: a top rail with card slots, a narrow shelf, three blank brass push buttons and a small dark display window; two small unlit red lamps on its face; below them a closed hinged lower panel. One warm brass wall lamp above the controller.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1; brass and blue enamel, not dense machinery.
Composition/framing: eye level; clear pale paving in front of the gate and controller for five figures; calm upper wall.
Lighting/mood: full-moon night; the warm wall lamp lights the controller; cool moonlight edges; the street beyond stays dark.
Avoid: people, animals, figures; any text, letters or numbers (ticks, buttons and mark stay blank); a second car; hinged lift doors; a crescent moon.
```

**Checks**
- Shaft centre-left behind a brass LATTICE gate (not doors); one empty car level with the street.
- Indigo strip with blank equal ticks at the shaft's right edge; controller to its right; warm lamp above.
- Two small red lamps OFF; lower panel CLOSED.
- No people, no text or numbers; paving in front clear.

---

## LB-01b · Lower panel open, two red warnings lit
- family: LB
- slug: street-side-panel-open
- kind: edit
- parent: LB-01
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @LB-01 — the approved plate to change
- save: `output/LB/LB-01b_street-side-panel-open.png`
- beats: 04A B,C
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved lift-bay plate
Primary request: change only the controller. Its hinged lower panel now hangs open, showing four equal brass correction wheels in a row with blank windows and a small blank brass plate above them; the two small red lamps on the controller face now glow bright red.
Constraints: the safety gate stays shut and the car stays level with the street; keep the camera, architecture, every other object, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers on wheels or plate; any other change.
```

**Checks**
- Lower panel open: exactly four equal blank wheels + blank plate.
- Both red lamps glowing; gate still shut; car level at street.
- Everything else identical to LB-01; no text.

---

## LB-01c · Safety gate open, warnings off
- family: LB
- slug: street-side-gate-open
- kind: edit
- parent: LB-01
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @LB-01 — the approved plate to change
- save: `output/LB/LB-01c_street-side-gate-open.png`
- beats: 04C A
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved lift-bay plate
Primary request: change only the brass lattice safety gate: it is now folded fully open, leaving the empty car's timber floor exactly level with the street paving as one smooth threshold. The two small red lamps stay off and the lower panel stays closed.
Constraints: keep the camera, architecture, controller, lamp, every other object, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers; any other change.
```

**Checks**
- Gate folded fully OPEN; car floor flush with paving.
- Red lamps off; panel closed; no text.

---

## LB-02 · Across the controller towards the shut gate
- family: LB
- slug: across-controller
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @LB-01 — approved lift bay: same gate, car, strip, controller, lamp and materials
- save: `output/LB/LB-02_across-controller.png`
- beats: 01E A; 02B A,B,C
- insets: Q03

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: approved plate of this same lift bay; keep its gate, car, strip, controller, lamp and materials exactly.
Primary request: medium view from beside the controller, looking across its top rail towards the closed brass safety gate.
Scene/backdrop: right foreground, the controller's top rail: a row of card slots, three blank brass push buttons, a small dark display window, and a narrow shelf with six or seven blank pale movement cards lying loose on it. Behind, on the left, the closed brass lattice gate with the small empty car standing level with the street, the vertical indigo strip of blank ticks beside the shaft, and the warm wall lamp above.
State: car at street level; gate shut; red lamps off; lower panel closed.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: shoulder height; shelf and cards clear in the lower right; open space between controller and gate for figures standing at the controller.
Lighting/mood: warm lamp light on brass and cards, cool moonlit darkness beyond; focused.
Avoid: people, animals, figures; any text, letters or numbers on cards, buttons or strip; a second car; a crescent moon.
```

**Checks**
- Controller rail + loose BLANK cards in the foreground right; gate + car behind left.
- Car level with street, gate shut; no text on cards/buttons.
- Space for figures; no people.

---

## LB-03 · Controller and position strip, close three-quarter
- family: LB
- slug: controller-strip
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @LB-01 — approved lift bay: same strip, controller, gate and lamp
  2. `../../Locations/CH 01 LOCATIONS/LANTERN LIFT STREET LEVEL 0 CLOSE UP.png` — older lift art: strip-beside-shaft and console design only; ignore its numbers and labels
- save: `output/LB/LB-03_controller-strip.png`
- beats: 02A A,B,C
- insets: Q01

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: approved plate of this same lift bay; keep its design and materials. Image 2: older lift art; use only the idea of a strip beside the shaft and the console design; ignore its numbers and labels.
Primary request: close three-quarter view of the lift controller and the vertical position strip beside the shaft.
Scene/backdrop: the indigo enamel strip runs down the wall at the shaft's edge, with evenly spaced blank brass ticks above and below a bolder blank tick at street level, continuing down out of frame. To its right, the blue-and-brass controller: top rail with card slots, three blank buttons, a small dark window, the closed lower panel. A slice of the brass lattice gate on the left; the warm wall lamp glowing at upper right.
State: car at street level behind the gate; red lamps off.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: strip visible top to bottom of the frame; clear space in front of the strip for a hand tracing it and for faces at the right.
Lighting/mood: warm lamp light, brass highlights, cool darkness at the edges; curious.
Avoid: people, animals, figures; any text, letters or numbers on the strip or controller; a crescent moon.
```

**Checks**
- Strip with EQUAL blank ticks, bolder tick at street level; no numbers.
- Controller to the strip's right; gate slice left; warm lamp.
- No people or text.

---

## LB-04 · Down the shaft through the guard, car at −5
- family: LB
- slug: shaft-car-minus5
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 3:4
- refs:
  1. @LB-01 — approved lift bay: same gate, strip, car and materials
  2. `../../Locations/CH 01 LOCATIONS/LANTERN LIF SHAFT & ADJASCENT NUMBER LINE.png` — older shaft art: shaft depth and lower platform idea only; ignore its numbers, labels and crates
- save: `output/LB/LB-04_shaft-car-minus5.png`
- beats: 02C A; 03B A; 03E A
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; portrait 3:4
Input images: Image 1: approved plate of this same lift bay (gate, strip, car, materials). Image 2: older shaft art; use only the shaft depth and lower platform idea; ignore its numbers, labels and crates.
Primary request: view from the street looking steeply down into the same lift shaft through the bars of the brass guard.
Scene/backdrop: brass guard bars cross the top of the frame; the edge of the blue-and-brass controller at the near right. The shaft drops away, the indigo strip of equal blank ticks running down its side: one bolder tick at street level, eight equal intervals down to a bolder tick at the lower store. At the bottom, the store landing: warm hanging lamp, brass rail, timber wall. The single small open-cage car hangs stopped with its floor level with the fifth tick below street level (five of eight intervals down); its empty timber floor is visible from above.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: steep downward view; car and lower landing both clearly visible; space on the landing for a figure and a cart.
Lighting/mood: warm lamps above and below, cool shadows in the shaft; suspense.
Avoid: people, animals, figures; any text, letters or numbers on the strip; a second car or ghost car; falling objects; a crescent moon.
```

**Checks**
- ONE car only, floor at the 5th of 8 equal ticks below street level.
- Guard bars at top, controller edge near right, lower landing with lamp at bottom.
- Blank ticks, no numbers; no people.

---

## LB-04b · Same view, car at −3
- family: LB
- slug: shaft-car-minus3
- kind: edit
- parent: LB-04
- set: full
- anchor: no
- candidates: 1
- aspect: 3:4
- refs:
  1. @LB-04 — the approved plate to change
- save: `output/LB/LB-04b_shaft-car-minus3.png`
- beats: 03A A; 03E C
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved shaft plate
Primary request: move only the lift car higher up the shaft, so its floor is level with the third tick below street level (three of the eight equal intervals down). Fill the space where it was with plain shaft wall and the continuing strip. Exactly one car remains.
Constraints: keep the camera, guard bars, strip, ticks, landing, lamps, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers; a second car; any other change.
```

**Checks**
- ONE car at the 3rd tick below street level; no ghost at the old position.
- Everything else identical to LB-04.

---

## LB-05 · Steep view down to the −8 store landing
- family: LB
- slug: shaft-to-store
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 3:4
- refs:
  1. @LB-01 — approved lift bay: same materials and guard
  2. `../../Locations/CH 01 LOCATIONS/LANTERN LIF SHAFT & ADJASCENT NUMBER LINE.png` — older shaft art: shaft depth and storage platform idea only; ignore its numbers and labels
- save: `output/LB/LB-05_shaft-to-store.png`
- beats: 01D A
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; portrait 3:4
Input images: Image 1: approved plate of this same lift bay (materials, guard). Image 2: older shaft art; use only the shaft depth and storage platform idea; ignore its numbers and labels.
Primary request: steep guarded view down the same lift shaft to the lower store landing far below.
Scene/backdrop: brass guard bars across the top of the frame; shaft walls with the indigo strip of equal blank ticks running down. At the bottom, the store landing: pale timber floor, brass safety rail, a closed sliding lower gate at the shaft, a timber store wall, a warm hanging lamp and a blank flush mark plate at the landing edge. On the landing stands a wooden handcart loaded with closed supply boxes, beside a small metal box mounted on the wall. No lift car in view.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: steep downward view; the landing, cart and metal box clearly readable; space beside the cart for one standing figure.
Lighting/mood: warm store lamp far below, cool shadowed shaft; mystery.
Avoid: people, animals, figures; any text, letters or numbers; a lift car; a crescent moon.
```

**Checks**
- Landing at the bottom: rail, closed lower gate, timber wall, warm lamp, loaded handcart, metal wall box.
- No car visible; blank ticks; no people or text.

---

## LB-06 · Lower landing, car arrived flush at −8, lower gate shut
- family: LB
- slug: store-car-arrived
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @LB-05 — approved view of the same store landing from above: same rail, gate, wall, lamp and cart
  2. @LB-01 — approved lift bay: the same car design
- save: `output/LB/LB-06_store-car-arrived.png`
- beats: 02D A; 02E A
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: the same store landing seen from above (rail, gate, wall, lamp, cart). Image 2: the same lift car design.
Primary request: medium view standing on the lower store landing, facing the lift car that has just arrived at the bottom of the shaft.
Scene/backdrop: the single small open-cage goods car stands with its timber floor exactly flush with the landing; between landing and car, a closed brass sliding lower gate. Around it: the timber store wall, the warm hanging store lamp, a blank flush mark plate at the landing edge, a brass safety rail, the dim shaft rising above. The loaded wooden handcart stands on the landing to one side, outside the gate.
State: empty car; lower gate closed.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: eye level on the landing; car interior visible through the gate; clear landing in front of the gate for a figure pushing the cart.
Lighting/mood: warm store lamp, cool shaft shadows; workmanlike calm.
Avoid: people, animals, figures; any text, letters or numbers; a second car; a crescent moon.
```

**Checks**
- Car floor FLUSH with the landing; lower gate CLOSED.
- Store lamp, timber wall, mark plate (blank), loaded cart outside the gate.
- No people or text.

---

## LB-06b · Lower gate slid open
- family: LB
- slug: store-gate-open
- kind: edit
- parent: LB-06
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @LB-06 — the approved plate to change
- save: `output/LB/LB-06b_store-gate-open.png`
- beats: 02D B
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved store-landing plate
Primary request: change only the lower brass gate: slide it fully open, so the car floor and the landing form one level threshold. Move the loaded handcart so it stands squarely in front of the open car, ready to roll in.
Constraints: keep the camera, car, walls, lamp, rail, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers; any other change.
```

**Checks**
- Lower gate fully OPEN; level threshold; cart lined up in front of the car.
- Everything else identical; no text.

---

## LB-07 · Controller top rail close-up
- family: LB
- slug: top-rail
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @LB-01 — approved lift bay: same controller design and materials
  2. `../../Locations/CH 01 LOCATIONS/LANTERN LIFT STREET LEVEL 0 CLOSE UP.png` — older lift art: console detailing only; ignore its numbers and labels
- save: `output/LB/LB-07_top-rail.png`
- beats: 03D A,B,C,D; 03E B; 03F A
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: approved plate of this same controller (design, materials). Image 2: older lift art; use only its console detailing; ignore its numbers and labels.
Primary request: close-up of the top rail of the same lift controller.
Scene/backdrop: blue enamel casing with brass trim; a row of card slots, one blank pale card standing in the first slot; a narrow shelf with a few loose blank cards; three round brass push buttons with blank caps in a row; a small dark rectangular display window beside them, blank. One brass guard bar at the left edge; the warm wall lamp's reflection gleaming on the brass.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: buttons, window and slots fully visible and unobstructed; space above the shelf for hands reaching in.
Lighting/mood: warm lamp light, rich brass highlights, dark surroundings; careful attention.
Avoid: people, animals, figures; any text, letters, numbers or symbols on buttons, window or cards; a crescent moon.
```

**Checks**
- Slots (one card standing), shelf with loose cards, three blank buttons, blank dark window.
- Guard bar at left edge; warm reflections; no text anywhere.

---

## LB-07b · Card slot opened: a thin hidden card behind
- family: LB
- slug: top-rail-hidden-card
- kind: edit
- parent: LB-07
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @LB-07 — the approved plate to change
- save: `output/LB/LB-07b_top-rail-hidden-card.png`
- beats: 03C A
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved controller close-up
Primary request: change only the first card slot: its small brass front flap is now opened, revealing a second, thinner pale blank card hidden directly behind the first card.
Constraints: both cards stay in the slot; keep the camera, buttons, window, shelf, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers on the cards; any other change.
```

**Checks**
- First slot open; a thinner second blank card visible behind the first.
- Both cards still in the slot; no text.

---

## LB-08 · Low view: car floor level with the paving at street level
- family: LB
- slug: car-level-low
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @LB-01 — approved lift bay: same gate, car, mark and materials
- save: `output/LB/LB-08_car-level-low.png`
- beats: 03G A
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: approved plate of this same lift bay; keep its gate, car, mark and materials exactly.
Primary request: low street-side view across the paving to the threshold of the same lift.
Scene/backdrop: camera low near the pale paving; in the foreground the flush blank brass level mark at the gate; the closed brass lattice gate; through its bars the car's timber floor exactly level with the street paving. Inside the car stands the wooden handcart loaded with supply boxes, its wheels strapped down. A corner of the controller at the right edge.
State: car at street level; gate shut and locked.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: the line where car floor meets paving is the clear focus; space to the left of the gate for a crouching figure holding a lamp low.
Lighting/mood: warm lamp light glancing along the paving, cool shadows; a puzzle: level, yet locked.
Avoid: people, animals, figures; any text, letters or numbers; a second car; a crescent moon.
```

**Checks**
- Car floor exactly LEVEL with the paving behind the CLOSED gate.
- Loaded cart strapped inside the car; blank level mark; no people or text.

---

## LB-09 · Opened lower panel: four wheels, two red warnings
- family: LB
- slug: lower-panel
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @LB-01b — approved lift bay with the lower panel open and red lamps lit: same design
  2. `../../Locations/CH 01 LOCATIONS/LANTERN LIFT STREET LEVEL 0 CLOSE UP.png` — older lift art: wheel and console detailing only; ignore its numbers and labels
- save: `output/LB/LB-09_lower-panel.png`
- beats: 04A A; 04B A,B
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: approved plate of this same controller with its lower panel open (design, materials). Image 2: older lift art; use only its wheel and console detailing; ignore numbers and labels.
Primary request: close three-quarter view of the opened lower panel of the same lift controller.
Scene/backdrop: the hinged cover swung open; inside, four equal brass correction wheels in one evenly spaced row, each with a blank window; a blank fixed brass plate above them; the two small red lamps glowing bright red on the controller face above. Behind, a strip of the closed brass gate and the level pale paving.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: all four wheels fully visible; space at the left for a hand holding the cover and at the bottom for a crouching figure.
Lighting/mood: red warning glow mixed with warm lamp light; a careful repair.
Avoid: people, animals, figures; any text, letters or numbers on wheels or plate; a crescent moon.
```

**Checks**
- Exactly FOUR equal wheels with blank windows; blank plate above.
- Both red lamps glowing; gate strip and level paving behind.
- No text or numbers; no people.
