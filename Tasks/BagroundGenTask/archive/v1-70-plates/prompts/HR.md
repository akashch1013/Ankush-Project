# HR — Sealed-hook rack, right end of the right-wall bench

Source of truth: `LOCATION-BIBLE.md` §4 (hook rack). Carton labels and team cards stay blank; seals stay intact; no loose hooks; no V here.

## HR-01 · Hook rack medium: four sealed cartons, four team cards
- family: HR
- slug: rack-medium
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @KB-01 — approved kit area of the same bench: same bench, blue wall, lamps and materials (the kit boxes sit at this view's left edge)
- save: `output/HR/HR-01_rack-medium.png`
- beats: 07A A,B,E,F; 07B A; 07D A,B,C
- insets: Q05, Q06

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: the kit area of this same workbench; match its bench, blue wall, lamps and materials exactly.
Primary request: medium view facing the right end of the same long pale workbench, where a brass rack rises against the blue wall.
Scene/backdrop: a brass rack with two uprights and crossbars stands above the bench. On the bench beneath it, four identical sealed cartons in an evenly spaced row, each with a blank paper label and an intact paper quantity seal across its lid. Above each carton, a brass spring clip on the rack holds one blank pale team card. The rack's right brass upright and the pale bench edge are clearly visible. At the left edge, the closed kit boxes of the kit area. A warm work lamp; one clear empty corner of the bench at the left.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: eye level; four cartons and four cards evenly spaced and readable; paving in front clear for five figures and a small cub.
Lighting/mood: warm lamp light on brass and paper, cool darkness beyond; a puzzle with something not quite right.
Avoid: people, animals, figures; any text, letters or numbers on labels or cards; open cartons or loose hooks; any letter V; a crescent moon.
```

**Checks**
- Exactly FOUR sealed cartons with blank labels and INTACT seals.
- Exactly FOUR blank cards, one in a brass clip above each carton.
- Right brass upright + bench edge visible; clear bench corner left; no text, no hooks, no V.

---

## HR-02 · Seal and card clip close-up
- family: HR
- slug: seal-clip
- kind: base
- parent: —
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @HR-01 — approved hook rack: same cartons, seals, clips, cards, upright and light
- save: `output/HR/HR-02_seal-clip.png`
- beats: 07A C,D
- insets: —

```text
Use case: illustration-story
Asset type: empty background plate for a graphic-novel panel; no characters, no lettering; landscape 4:3
Input images: Image 1: approved plate of this same rack; match its cartons, seals, clips, cards and light exactly.
Primary request: close-up of one sealed carton and the clip above it on the same rack.
Scene/backdrop: the front of one carton with its blank paper label and its intact paper quantity seal; directly above, the brass spring clip on the rack holding one blank pale team card; the rack's right brass upright and the pale bench edge frame the view; the neighbouring carton just visible at the side.
Style/medium: cinematic painterly graphic-novel environment, soft stylised-3D finish, as in Image 1.
Composition/framing: seal and card both large and clear; space at the side for a face and a pointing hand.
Lighting/mood: warm lamp light; trust in what is sealed.
Avoid: people, hands, figures; any text, letters or numbers; a broken seal; dust; a crescent moon.
```

**Checks**
- One intact seal + blank label; clip with a blank card above.
- Right upright + bench edge visible; no dust yet; no text.

---

## HR-02b · Card lifted out: black dust under the clip
- family: HR
- slug: seal-clip-dust
- kind: edit
- parent: HR-02
- set: full
- anchor: no
- candidates: 1
- aspect: 4:3
- refs:
  1. @HR-02 — the approved plate to change
- save: `output/HR/HR-02b_seal-clip-dust.png`
- beats: 07C A,B
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the approved seal-and-clip plate
Primary request: remove the team card from the brass clip, leaving the clip's jaws empty and slightly open, and reveal fine black powdery dust under the clip and on the rack behind where the card stood.
Constraints: the carton seal stays intact; keep the camera, carton, label, upright, bench, lighting and colours exactly as in Image 1.
Avoid: people, hands or figures; any text, letters or numbers; any other change.
```

**Checks**
- Clip empty; fine BLACK dust under the clip and on the rack behind it.
- Seal still intact; nothing else changed.
