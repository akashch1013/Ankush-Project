# TB — Timing bench, left end of the right-wall bench (the carved bird and two catches)

Source of truth: `LOCATION-BIBLE.md` §4 (timing device) and §9. Blue catch + lamp physically LEFT, gold catch + lamp RIGHT, beat strip between. No timing drums, ever.

## TB-01 · Timing bench medium, both catches down
- family: TB
- slug: bench-medium
- kind: base
- parent: —
- set: samples
- anchor: yes
- candidates: 2
- aspect: 4:3
- refs:
  1. @LS-01 — approved Lantern Street master: same street; match its bench, blue wall, materials, rendering and darkness
- save: `output/TB/TB-01_bench-medium.png`
- beats: 05A A; 05C A,B,C; 05D B,C
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: approved plate of this same dark street; match its pale workbench, blue wall, materials, rendering and light.
Primary request: medium view from the lane facing the left end of the long pale workbench on the right-hand blue wall, where a small timing device stands.
Scene/backdrop: on the pale bench under a warm work lamp: on the left a blue-enamelled brass catch arm with a small blue glass lamp above it; on the right a matching gold-brass catch arm with a small gold glass lamp above it; between them, on a low back panel, a horizontal beat strip of evenly spaced blank marks and a small round counter dial with a blank face; a start-card slot holding one blank pale card. In front, a short brass track runs towards the bench edge; at its back end a small sliding platform carries one carved wooden bird, held at its start by both catch arms. The bench continues to the right towards a padded kit area.
State: both catch arms down; both small lamps unlit; bird at the start.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1; elegant and simple, not dense machinery.
Composition/framing: eye level; device centred and readable; clear paving in front for figures and a handcart; calm upper blue wall.
Lighting/mood: warm work lamp on the device, cool moonlit darkness behind; a small puzzle waiting.
Avoid: people, animals, figures other than the one small carved bird; any text, letters or numbers; timing drums; a second bird; a crescent moon.
```

**Checks**
- BLUE catch + lamp on the LEFT, GOLD catch + lamp on the RIGHT, beat strip between.
- Both arms DOWN, both lamps OFF; one carved bird on its platform at the START of a short track.
- Blank strip, dial and card; no drums; no people or text.

---

## TB-01b · Gold catch up (gold lamp lit), blue down
- family: TB
- slug: bench-medium-gold-up
- kind: edit
- parent: TB-01
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @TB-01 — the approved plate to change
- save: `output/TB/TB-01b_bench-medium-gold-up.png`
- beats: 05B B
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved timing-bench plate
Primary request: change only the right-hand gold catch: its arm is now raised and its small gold lamp glows. The left-hand blue catch stays down with its blue lamp unlit; the bird and its platform stay at the start.
Constraints: keep the camera, bench, device, wall, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers; any other change.
```

**Checks**
- Gold (right) arm up + gold lamp lit; blue (left) down + unlit.
- Bird still at the start; no other change.

---

## TB-01c · Both catches up, platform at its end stop, bird bowing
- family: TB
- slug: bench-medium-bow
- kind: edit
- parent: TB-01
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @TB-01 — the approved plate to change
- save: `output/TB/TB-01c_bench-medium-bow.png`
- beats: 05E C
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved timing-bench plate
Primary request: change only the timing device: both catch arms are raised and both small lamps glow (blue on the left, gold on the right); the sliding platform has moved forward along its short track to the end stop near the bench edge, and the carved bird on it now bows its head forward. No bird remains at the start.
Constraints: keep the camera, bench, wall, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers; a second bird; any other change.
```

**Checks**
- Both arms up, both lamps lit; ONE bird at the END STOP, bowing.
- No ghost bird at the start; no other change.

---

## TB-02 · Timing device close-up, both catches down
- family: TB
- slug: device-close
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @TB-01 — approved timing bench: same device, bird, bench, wall and light
- save: `output/TB/TB-02_device-close.png`
- beats: 05D D
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: approved plate of this same timing device; keep its design, colours and materials exactly.
Primary request: close-up of the same timing device on the pale workbench.
Scene/backdrop: blue-enamelled catch arm with its small blue lamp on the left; gold catch arm with its small gold lamp on the right; between them the beat strip of evenly spaced blank marks and the small round counter dial with a blank face; the start-card slot with one blank card; the short brass track running towards the bench edge, with the sliding platform and the carved wooden bird at its start. The pale bench edge along the bottom, the blue wall behind.
State: both arms down, both lamps unlit.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: the whole device, including the track's end stop, inside the frame; bench edge and blue wall as anchors; space at the top for a caption.
Lighting/mood: warm work lamp light, brass and enamel highlights; patient.
Avoid: people, animals, figures other than the carved bird; any text, letters or numbers on strip, dial or card; timing drums; a crescent moon.
```

**Checks**
- Same device as TB-01, blue LEFT / gold RIGHT, both down and unlit.
- Bird at the start; track end stop visible; bench edge + blue wall anchors.
- No text or numbers.

---

## TB-02b · Blue catch up (blue lamp lit), gold down
- family: TB
- slug: device-blue-up
- kind: edit
- parent: TB-02
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @TB-02 — the approved plate to change
- save: `output/TB/TB-02b_device-blue-up.png`
- beats: 05A B
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved timing-device close-up
Primary request: change only the left-hand blue catch: its arm is now raised and its small blue lamp glows. The right-hand gold catch stays down with its gold lamp unlit; the bird and platform stay at the start.
Constraints: keep the camera, device, bench, wall, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers; any other change.
```

**Checks**
- Blue (left) up + lit; gold (right) down + unlit; bird at the start.
- Everything else identical to the parent plate; no people, no text.

---

## TB-02c · Gold catch up (gold lamp lit), blue down
- family: TB
- slug: device-gold-up
- kind: edit
- parent: TB-02
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @TB-02 — the approved plate to change
- save: `output/TB/TB-02c_device-gold-up.png`
- beats: 05B A
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved timing-device close-up
Primary request: change only the right-hand gold catch: its arm is now raised and its small gold lamp glows. The left-hand blue catch stays down with its blue lamp unlit; the bird and platform stay at the start.
Constraints: keep the camera, device, bench, wall, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers; any other change.
```

**Checks**
- Gold (right) up + lit; blue (left) down + unlit; bird at the start.
- Everything else identical to the parent plate; no people, no text.

---

## TB-02d · Both catches up at the start (the shared beat)
- family: TB
- slug: device-both-up
- kind: edit
- parent: TB-02
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @TB-02 — the approved plate to change
- save: `output/TB/TB-02d_device-both-up.png`
- beats: 05E A
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved timing-device close-up
Primary request: change only the two catches: both arms are now raised together and both small lamps glow, blue on the left and gold on the right. The sliding platform and bird are still at the start, just free to move.
Constraints: keep the camera, device, bench, wall, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers; motion blur; any other change.
```

**Checks**
- Both arms up, both lamps lit; bird still at the start.
- Everything else identical to the parent plate; no people, no text.

---

## TB-02e · Both up, platform at its end stop, bird bowing
- family: TB
- slug: device-bow
- kind: edit
- parent: TB-02
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @TB-02 — the approved plate to change
- save: `output/TB/TB-02e_device-bow.png`
- beats: 05E B
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved timing-device close-up
Primary request: both catch arms are raised and both small lamps glow; the sliding platform has moved forward along the short track to its end stop near the bench edge, and the carved bird on it bows its head forward. No bird remains at the start.
Constraints: keep the camera, device, bench, wall, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers; a second bird or motion trail; any other change.
```

**Checks**
- Both up + lit; ONE bird at the end stop, bowing; nothing at the start.
- Everything else identical to the parent plate; no people, no text.

---

## TB-03 · Overhead bench top beside the start-card slot
- family: TB
- slug: overhead-bench
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @TB-01 — approved timing bench: same bench wood, device and light
- save: `output/TB/TB-03_overhead-bench.png`
- beats: 05D A
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: approved plate of this same timing bench; match its pale wood, brass, colours and light.
Primary request: overhead view looking straight down at the pale bench top beside the same timing device.
Scene/backdrop: along the top edge of the frame, the base of the timing device: the beat strip with blank marks, the start-card slot with one blank card and the feet of the blue and gold catch arms. The rest of the frame is a clean pale wooden bench surface with soft wood grain, lit by warm lamp light: room where two paper sheets will be laid and written on.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: top-down; a large clean empty bench area in the centre and bottom of the frame.
Lighting/mood: warm, even lamp light; quiet concentration.
Avoid: people, hands, figures; any text, letters or numbers; papers or pencils (added later); a crescent moon.
```

**Checks**
- Top-down; device base along the top edge; large clean pale bench area.
- No papers, hands or text.
