# GT — Old Blue Gate exterior (scene 11C cutaway)

User decision (2026-10-20): **keep the old Gate image unchanged in design.** Only remove its production labels, apply the story state (violet seam off since the prologue, small door shut) and, for 11C, let the empty ring ornament brighten. No V16 bench/planter is added. Crowd, Ira, Kabir and the green Gate helper are added at panel stage.

## GT-01 · Old Blue Gate, cleaned (labels removed, seam off)
- family: GT
- slug: gate-clean
- kind: edit
- parent: OLD BLUE GATE.png
- set: samples
- anchor: no
- candidates: 1
- aspect: 16:9
- refs:
  1. `../../Locations/CH 01 LOCATIONS/OLD BLUE GATE.png` — the approved Old Blue Gate location art: the image to clean
- save: `output/GT/GT-01_gate-clean.png`
- beats: —
- insets: —

```text
Use case: precise-object-edit
Asset type: the same picture as a clean background plate; same size and framing; landscape 16:9
Input images: Image 1: the approved Old Blue Gate location art
Primary request: remove every white label box together with its words, every thin pointer line and the arrow on the road, and repaint those areas to match what is behind them (sky, ring, gate, stone, paving). Switch off the violet light seam down the middle of the gate and around its arch, so the gate leaves are dark blue like the rest of the gate. Keep the small emergency door at the lower right closed.
Constraints: keep the gate design, the empty ring ornament above it, ivy, banners, street lamps, scooters, buildings, full moon, lighting and composition exactly as they are.
Avoid: people or figures; any text, letters, numbers or labels; violet glow; any other change.
```

**Checks**
- All label boxes, words, pointer lines and the arrow GONE, with clean repainting behind them.
- Violet seam OFF (gate dark); small door at lower right CLOSED.
- Design, ring ornament, scooters, lamps and moon unchanged.

---

## GT-01b · The empty ring ornament brightens (11C)
- family: GT
- slug: gate-ring-glow
- kind: edit
- parent: GT-01
- set: samples
- anchor: no
- candidates: 1
- aspect: 16:9
- refs:
  1. @GT-01 — the cleaned Gate plate to change
- save: `output/GT/GT-01b_gate-ring-glow.png`
- beats: 11C A,B
- insets: —

```text
Use case: precise-object-edit
Asset type: the same background plate, same size and framing
Input images: Image 1: the cleaned Old Blue Gate plate
Primary request: change only the empty ring ornament above the gate: it now glows softly with a cool silver-gold moonlight sheen, as if beginning to brighten, with a faint halo around it. The gate leaves stay closed and dark; the small door stays shut.
Constraints: keep the camera, gate, lane, lamps, scooters, buildings, full moon, lighting and colours exactly as in Image 1.
Avoid: people or figures; any text, letters or numbers; a bell in the ring; violet light on the gate; any other change.
```

**Checks**
- Ring ornament glowing softly (still an EMPTY ring, no bell).
- Gate still closed and dark, small door shut; nothing else changed.
