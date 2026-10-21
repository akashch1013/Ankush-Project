# LS — Lantern Street (wides, entrance, lane, arches, restored views)

Source of truth for geography: `LOCATION-BIBLE.md` §1–2, §9.

## LS-01 · Lantern Street master wide, dark
- family: LS
- slug: master-dark
- kind: base
- parent: —
- set: samples
- anchor: yes
- candidates: 3
- aspect: 16:9
- refs:
  1. `../../Locations/CH 01 LOCATIONS/LANTERN STREET UN REPAIRED STATE.png` — older Lantern Street art: use its rendering quality, building scale and night mood only; ignore its layout, machines and labels
- save: `output/LS/LS-01_master-dark.png`
- beats: 01A A
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 16:9
Input images: Image 1: older art of this street; use only its rendering, building scale and moonlit mood; ignore its layout, drums, shutters, floor frame, centre track and label boxes.
Primary request: wide establishing view of dark Lantern Street from just inside the Entry Court archway, looking down the long lane.
Scene/backdrop: broad pale stone paving between blue-painted timber stalls with closed shutters, indigo frames and brass fittings. Tall indigo lantern arches span the lane at intervals; their lantern heads are dark. Near left: a lift shaft recessed behind a brass lattice gate, a blue-and-brass control stand with a warm wall lamp to its right, and an empty handcart parked against the stalls. Along the whole right wall: one long pale workbench under small work lamps. Farther: a shallow wall alcove on the left; opposite it, under a small indigo canopy, a low square plinth beside a dark panel of five tiny lamps and a tall lever. A thin unlit silver track runs along the right edge of the paving. The lane bends gently right; tall closed shutters fill the bend.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish; grandeur from scale and depth, not tiny machinery.
Composition/framing: eye level, framed by the dark arch edge; lower-centre paving clear with a soft warm lamp pool; calm sky on top; far details too small to read.
Lighting/mood: one full moon, cool moonlight on roofs, only small work lamps lit; wonder held back by darkness.
Avoid: people, animals, figures, silhouettes; any text, letters, numbers or signs; drums, numbered shutters, floor squares; a bell; a crescent moon; religious symbols.
```

**Checks**
- Lift recess with brass gate near LEFT; long pale bench along the RIGHT wall; silver track at the RIGHT edge of the paving.
- Tall indigo arches cross the lane and are DARK; work lamps are the only lit lights.
- Far end: alcove on the left, small canopy plinth + lamp panel + lever on the right, closed shutters in the bend.
- Pale paving and blue timber stalls (not dark cobbles); one full moon if the moon shows.
- No people, no text or labels, no drums, numbered shutters or floor squares.
- Lower-centre paving clear; top band calm.

---

## LS-01R · Lantern Street master wide, restored (bonus for later chapters)
- family: LS
- slug: master-restored
- kind: edit
- parent: LS-01
- set: samples
- anchor: no
- candidates: 1
- aspect: 16:9
- refs:
  1. @LS-01 — the approved dark Lantern Street master plate to change
- save: `output/LS/LS-01R_master-restored.png`
- beats: —
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved dark Lantern Street plate
Primary request: show this same street after its repair. Every tall indigo arch now glows with warm golden lantern light; the thin silver track along the right edge of the paving shines as one continuous line of light; the five tiny lamps on the far right wall panel glow white; the lever beside them is pulled down; the far plinth holds one solid softly glowing cube of small lanterns; the far left alcove holds a complete square mirror catching the moonlight.
Constraints: keep the camera, architecture, layout, stalls, closed far shutters, parked handcart and sky exactly as in Image 1. Warm golden light now fills the street; cool moonlight stays on the roofs.
Avoid: people, animals or figures; any text, letters or numbers; any other change.
```

**Checks**
- Same camera and layout as LS-01 (overlay-identical apart from light).
- Arches golden, silver track continuous, far lamps white, lever down, cube and mirror complete.
- Far shutters still closed; no people, no text.

---

## LS-02 · Low entrance view with the parked cart
- family: LS
- slug: entrance-cart-low
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @LS-01 — approved Lantern Street master: the same street; match materials, palette, rendering and darkness
- save: `output/LS/LS-02_entrance-cart-low.png`
- beats: 01B A,B,C
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: approved plate of this same dark street; match its materials, palette, rendering and light exactly.
Primary request: low view along the entrance paving of the same dark street, camera at the eye height of a small animal.
Scene/backdrop: pale stone paving leads ahead into darkness. On the left, the blue timber wall of the goods-lift bay with the edge of its brass lattice gate. One tall dark indigo lantern arch spans the view ahead. In the near foreground on the left, the same empty wooden handcart is parked against the stall wall, outside the walking route; its long wooden handle sticks out into the lane at knee height, caught in a soft warm pool of lamp light on the paving.
State: arches dark; the thin silver track along the right edge of the paving is unlit.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: low camera; the handle prominent left of centre; clear paving in the centre and right for four standing figures and a small cub; dark arch and night sky calm at the top.
Lighting/mood: full-moon night; warm pool of hand-lamp light low on the paving; cool moonlight edges; quiet, a little comic.
Avoid: people, animals, figures; any text, letters or numbers; a second cart; a bell; a crescent moon.
```

**Checks**
- Lift-bay wall and gate edge on the LEFT; one dark arch ahead.
- Empty handcart against the left wall, handle projecting into a warm lamp pool.
- Centre/right paving clear; no people or text.

---

## LS-03 · Lane medium from the lift bay towards the bench
- family: LS
- slug: lane-to-bench
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 16:9
- refs:
  1. @LS-01 — approved Lantern Street master: same street, materials, palette and darkness
  2. @LB-01c — approved lift bay with its gate open: the near-left corner of this view
- save: `output/LS/LS-03_lane-to-bench.png`
- beats: 04D A,B,C,D
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 16:9
Input images: Image 1: approved plate of this same dark street (materials, palette, rendering). Image 2: the goods-lift bay seen in this view's near-left corner.
Primary request: medium-wide view from the paving beside the goods-lift bay, looking across and down the dark street towards the long pale workbench on the right-hand wall.
Scene/backdrop: near left edge, a slice of the lift bay's blue wall and open brass gate. Across the lane, the continuous pale workbench runs along the blue right wall under small warm work lamps, its objects small and indistinct. Far down the lane on the right, a small blue wall panel with a row of five tiny round lamps: the first lamp glows white, the other four are dark; a tall lever stands beside it. Tall indigo arches overhead, all dark.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: eye level; clear paving in the foreground for a group of figures and a handcart; the far lamp panel small but readable as a landmark; dark arch tops and sky calm at the top.
Lighting/mood: full-moon night, small warm work lamps, cool moonlight; anticipation.
Avoid: people, animals, figures; any text, letters or numbers; lit arches; a crescent moon; religious symbols.
```

**Checks**
- Lift bay corner at near LEFT, bench along the RIGHT wall.
- Far right panel: exactly the first of five tiny lamps white, four dark; lever beside it.
- Arches dark; foreground clear; no people or text.

---

## LS-04 · Along the bench towards a dark lantern arch (crew zone)
- family: LS
- slug: bench-to-arch
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @KB-01 — approved projector-kit area of the same bench: match bench, wall, boxes and light
  2. @LS-01 — approved Lantern Street master: same street and arches
- save: `output/LS/LS-04_bench-to-arch.png`
- beats: 06D A; 07E A
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: the kit area of this same workbench (bench, wall, boxes, light). Image 2: the same street and its arches.
Primary request: view along the long pale workbench on the right-hand blue wall towards a nearby tall indigo lantern arch where repair crews are about to work.
Scene/backdrop: right foreground, the end of the kit area with several closed shallow kit boxes stacked neatly. Just beyond, a tall indigo arch spans the lane; on its crossbeam hang dark lantern projector heads made of blue glass lenses in brass rings; two wooden ladders lean against the arch posts and some brass support brackets hang loose, not yet fastened. Dark stalls continue down the lane.
State: arches and lantern heads unlit.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: eye level; clear paving in the foreground for a handover between figures; the arch's upper half clearly visible for workers added later; calm sky in the upper left.
Lighting/mood: full-moon night, warm work lamps on the bench, cool moonlight on the arch; busy expectation.
Avoid: people, animals, figures; any text, letters or numbers; lit lanterns; a crescent moon.
```

**Checks**
- Bench + stacked closed kit boxes on the RIGHT; one tall dark arch beyond.
- Projector heads (blue lenses in brass rings) on the arch, unlit; ladders; loose brackets.
- No people or text; foreground clear.

---

## LS-04b · Lantern supports secured (still dark)
- family: LS
- slug: bench-to-arch-secured
- kind: edit
- parent: LS-04
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @LS-04 — the approved plate to change
- save: `output/LS/LS-04b_bench-to-arch-secured.png`
- beats: 07E B
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved plate
Primary request: change only the arch fittings: every lantern projector head on the arch is now fully mounted, and every brass support bracket is fastened firmly to the arch with hooks; the ladders are gone and the stacked kit boxes on the bench are gone. The arch and its lanterns stay dark and unlit.
Constraints: keep the camera, architecture, bench, wall, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers; lit lanterns; any other change.
```

**Checks**
- Same camera as LS-04; brackets fastened, heads mounted, ladders gone.
- Arch still DARK; no people or text.

---

## LS-06 · Restored street, reverse wide from the cube end
- family: LS
- slug: reverse-restored
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 16:9
- refs:
  1. @LS-01 — approved master of the same street seen from the entrance: this view looks back the opposite way
  2. @MR-01c — the completed mirror alcove (near right in this view)
  3. @CP-01e — the completed cube plinth, lamp panel and lowered lever (near left in this view)
- save: `output/LS/LS-06_reverse-restored.png`
- beats: 10J A
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 16:9
Input images: Image 1: this same street seen from its entrance; this view looks back the opposite way. Image 2: the mirror alcove, near right here. Image 3: the cube plinth, near left here.
Primary request: the repaired street seen from its far end beside the cube plinth, looking back towards the Entry Court archway: the first full success view.
Scene/backdrop: because we look back, the long pale workbench (right wall in Image 1) now runs down the LEFT side of the frame and the alcove side is on the RIGHT. Near left: the low square plinth under its indigo canopy holding one solid, softly glowing cube of small lanterns, the wall panel with five white lamps and the lever pulled down. Near right: the shallow square mirror in its alcove, complete, reflecting the full moon. Far right: the goods-lift bay. Far end: the archway.
State: every tall indigo arch glows warm gold; the thin silver track along the bench-side edge of the paving shines continuously.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: eye-level wide; clear paving near the centre for a small group; calm sky at the top.
Lighting/mood: golden arch light fills the street, cool moonlight on roofs and mirror; joy and relief.
Avoid: people, animals, figures; any text, letters or numbers; swapping the two sides; a crescent moon; religious symbols.
```

**Checks**
- Reverse view: bench on screen-LEFT, mirror alcove on screen-RIGHT, archway at the far end.
- Arches GOLD, silver track lit along the bench-side edge, five white lamps, lever down.
- Complete glowing cube and complete mirror visible near the camera.
- No people or text.

---

## LS-07 · Restored street towards the still-closed far shutters
- family: LS
- slug: towards-shutters-restored
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 16:9
- refs:
  1. @LS-06 — the restored street: match its golden light and materials exactly
  2. @LS-01 — the same street from the entrance: the far bend and its tall shutters
- save: `output/LS/LS-07_towards-shutters-restored.png`
- beats: 11D A,B
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 16:9
Input images: Image 1: the repaired street (golden light, materials). Image 2: the same street; its far bend with tall shutters is where this view looks.
Primary request: medium view from beside the mirror alcove looking down the repaired street towards the far bend.
Scene/backdrop: golden-lit blue timber stalls on both sides; at the right edge, the corner of the indigo canopy over the cube plinth; the lane bends gently right ahead, where tall rolling shutters stay CLOSED across the end of the street, lit warmly by the arches. The thin silver track along the right edge of the paving glows.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: eye level; clear paving in the foreground for a group facing different ways; the closed shutters clearly readable as the end of the street; calm upper area.
Lighting/mood: warm golden arch light, cool moonlight on roofs; a hopeful pause just before a surprise.
Avoid: people, animals, figures; any text, letters or numbers; open shutters; a crescent moon.
```

**Checks**
- Restored golden light, glowing silver track.
- Tall far shutters CLOSED.
- Plinth canopy corner at the RIGHT edge; foreground clear; no people or text.

---

## LS-08 · Blue stall wall in golden light (bird-shadow wall)
- family: LS
- slug: shadow-wall-restored
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @LS-06 — the restored street: match its golden light, stalls and materials
- save: `output/LS/LS-08_shadow-wall-restored.png`
- beats: 10J B,C,D,E
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: the repaired street; match its golden light, stalls and materials exactly.
Primary request: medium view of a plain blue-painted timber stall wall on the mirror side of the repaired street, near its far end.
Scene/backdrop: a broad smooth blue timber stall front with closed shutters to one side; pale paving at its foot; a glimpse of a golden-lit indigo arch overhead; at the frame edge, across the lane, the corner of the indigo canopy over the plinth.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: eye level; a large clear, evenly lit area of blue wall at chest-to-head height (a hand shadow will be cast there later); clear paving in front for five figures, one small.
Lighting/mood: warm golden arch light from above, gentle moonlight; celebration.
Avoid: people, animals, figures, shadows of figures; any text, letters or numbers; posters or signs on the wall; a crescent moon.
```

**Checks**
- Large clear blue wall area at chest-to-head height, no posters or shadows.
- Golden restored light; paving clear; no people or text.
