# v2: rewritten prompts for 001, 002, 008, 010 (2026-10-21)

New prompts for four records, written from scratch, each in two versions. Images are generated at 1K through the OpenAI Images API (`gpt-image-2.5-sunburst`, quality high).

| Version | Content from | Images attached |
|---|---|---|
| `noref` | Draft 02 only (`../CH01-LOCATION-IMAGE-GENERATION-DRAFT-02.docx`) | none |
| `ref` | Draft 02 + reference images | 2 per job, see below |

Both versions carry the same written **style study** of the reference set (old Locations pack, the WhatsApp sheets and the finished comic pages). The text-only prompts therefore aim at the same look without seeing it.

## Jobs

| Job | Record | Size | Image 1 | Image 2 |
|---|---|---|---|---|
| 001-noref | Lantern Street initial master | 1280×720 | — | — |
| 001-ref | 〃 | 1280×720 | old pack: Lantern Street unrepaired (look only, **not** layout) | finished page 47: character-free street crop |
| 002-noref | Goods lift street landing | 1024×768 | — | — |
| 002-ref | 〃 | 1024×768 | old pack: lift street level 0 (parent design, state changed) | WhatsApp: lift shaft number line (numeral style) |
| 008-noref | Timing bench held platform | 1024×768 | — | — |
| 008-ref | 〃 | 1024×768 | WhatsApp: timing drums close-up (finish, blue/gold coding only) | WhatsApp: drums + repair-kit area (setting) |
| 010-noref | Projector kit bench before packing | 1024×768 | — | — |
| 010-ref | 〃 | 1024×768 | finished page (Sep 18): kit-bench crop (bench + stock-box design) | WhatsApp: drums + repair-kit area (setting) |

`jobs.json` lists every job, its prompt file and each reference's source file. The prompts are `prompts/<job>.txt`, sent verbatim, ready to paste into ChatGPT with the same images attached in the same order.

## Content rules the prompts keep

- **Draft 02 decides what is in the picture:**
  - a carved bird on a sliding platform, not timing drums;
  - blue glass **lenses**, not clips;
  - a low leaning square mirror in a wall alcove, not a floor square;
  - no numbered supply shutters in 001;
  - the exact labels each record asks for.
- **The reference images show the older designs.** Each `ref` prompt says which parts to borrow (finish, palette, materials, construction family) and which to leave out (drums, CLIPS labels, the floor mirror, all callout boxes and title banners).
- **The old Locations pack is attached in the `ref` jobs** at the user's request (2026-10-21). The Draft 02 queue (`bg.py`) still excludes it.

## Style study (in every prompt)

- **Rendering:** fantasy environment concept art that is mostly photoreal in materials and light, with storybook idealisation. Forms are clean, orderly and slightly glossy.
- **Materials:** polished and cast brass with bright specular edges; navy-painted timber and iron with rivets and edge banding; chipped blue-grey dressed stone; indigo banners with gold eight-point stars, crescent moons and fringe.
- **Colour and contrast:** ultramarine, cobalt and navy against amber, honey-gold and brass. Strong warm/cool contrast, saturated but never neon. Deep shadows that still show detail.
- **Light:** warm lanterns with soft bloom; wet-look paving with long gold reflections; one big full moon in a starry sky.
- **Richness:** dense ornament on frames and upper edges; floors and work surfaces stay open and crisp.

## First results (2026-10-21, 1K, total ≈ $0.40)

`out/SHEET.png` shows text-only on the left and with refs on the right. The 002 labels were zoom-checked; the other labels read correctly at native 1K.

| Job | Verdict | What to fix if chosen |
|---|---|---|
| 001-noref | layout right: lift + empty cart near-left, one continuous bench right, alcove mirror, cube canopy, moonline + cover, plain shutters | arch lanterns are **lit** (must be dark); light board shows ~3 lamps and sits at the bench's near end instead of just before the canopy |
| 001-ref | layout right, arch lanterns dark, closest to the old pack's look | light board again at the near end; lane runs straight (no bend) |
| 002-noref | every label and numeral correct (+3…−8, pointer at 0, START / HOLD / CANCEL LAST CHANGE), blank window, red lamps, closed cover | none |
| 002-ref | labels correct, richer ref finish | hinged door leaves folded open beside the gate (leaked from Image 1); no visible last-change window |
| 008-noref | one bird at the rear, guide inside the bench edge, 4 BEATS / 6 BEATS, card 6, counter 0 | catch lamps are clear glass, not blue/gold; catches sit beside the platform rather than visibly blocking it |
| 008-ref | all record points met; no drums leaked; strongest of the pair | none significant |
| 010-noref | exact labels, real lenses, empty kit, blank board, test rail, timing lamps far left, rack far right | **crescent moon** in the window (must be one full moon, or no sky) |
| 010-ref | exact labels, lenses, no trays leaked from Image 1 | bird not clearly bowed at the forward stop |

## Run

```bash
python3 v2/gen.py --dry-run          # show every request, spend nothing
python3 v2/gen.py 002-ref            # one job (an older result is kept as out/<job>.prevN.png)
python3 v2/gen.py --workers 4        # all eight, four at a time
python3 v2/gen.py --sheet            # rebuild out/SHEET.png (no-ref | ref, one row per record)
python3 v2/gen.py 001-noref --preset 2k   # same prompt at 2K once a version is chosen
```

The cost is logged in `out/usage.tsv`; a 1K image costs about $0.03–0.05.
