# ChandRush art direction (A3 "Lantern Street", adopted 2026-11-22)

**Readers are 11 years old. Every page must feel cool and aspirational for that age, never kiddish**, and still
creative: colour, art, and one or two surprises that belong to that page only.
The user's words:
- *"it is a page of a child's book! this should be creative!! … colours, some art, some unique things!!"*
- *"the layout have become interesting but the graphics have become kiddish for a 11 years old … he should find
  the book cool and aspirational for his age."*
- *"the graphics and colors of the pages should be in same family as the graphics and colors of the location images.
  the illustration style should also match."*

Precedence:
- **This file governs look, colour, devices and creativity.**
- `manual-v09.md` still governs reading comfort: type sizes, contrast, maths glyphs, question-before-answer, proof.
- `patterns.md` grids are optional starting points.

Tools: `kit.css` (built by `kitgen.py`). See every piece in `kit-1.png` and `kit-2.png`, and copy markup from
`kit-gallery-1.html` and `kit-gallery-2.html`. Free art is in `FInalChangesTask/library/README.md`.

---

## 1. The look: "Lantern Street", the page lives inside the location paintings
The crew are young engineers on a secret mission: repair a magical night fair before moonset. The pages look like
**a graphic novel crossed with the crew's mission files**, made from the **same world as the location images**
(`BagroundGenTask/out/plates/`). Open two or three plates before designing a page: the page must feel cut from them.
- **Materials from the plates:**
  - royal-blue painted planks with gold pinstripe trim (the stall walls);
  - brass fittings with warm specular highlights (lamps, rails, box corners);
  - cream marble (counters);
  - warm sandstone, wet stone paving that reflects gold;
  - deep-blue banners carrying a gold full moon and a four-point star;
  - maroon velvet and cushions;
  - ivy.
- **Light from the plates:** warm lamp-gold key light and pools of glow, against cool moonlight from the sky. Colour comes
  from light and metal, not candy fills.
- **Stages:**
  - `stage-planks`: the stall wall;
  - `stage-cinema`: the night lane with lamp glow and moonlight;
  - `stage-blueprint`: engraved gold linework on royal blue;
  - `stage-parchment`: cream marble paper;
  - `stage-backdrop`: the page's **own plate**, softened (`pagekit.py backdrop <page_dir> <plate>`). The strongest match.
- **Objects, valuable and in-world:**
  - mission file cards and VIP passes (marble cream, royal stub, brass foil edge);
  - the field notebook (royal leather cover);
  - sealed answer panels with a brass seal;
  - etched brass plates and nameplates;
  - royal lacquer panels with gold pinstripe;
  - a wax-sealed letter, a cargo tag.
- **Illustration style = the plates' style:** painterly, semi-realistic vector:
  - gradients with a warm key light and a cool moon rim;
  - specular highlights on brass, soft cast shadows, glow halos around lights;
  - reflections on wet or polished surfaces;
  - the plates' materials, never flat monoline as the hero (small icons may be monoline brass, like engraving).
- **Indian grandeur, grown-up:** jharokha windows, arches, banners, brass, Art-Deco/Indo-Saracenic trim.

**Banned:**
- *kiddish:* party bunting/toran flags, cartoon garlands, striped awnings, pastel fills, washi tape, rounded "bubble"
  fonts, cartoon icons with bows, stars, smiles or smoke puffs, paw trails, cute houses;
- *off-world:* neon/cyan HUD glow, holographic foil, sci-fi interfaces, flat corporate infographics, colours that
  appear in no plate.

**Tests:**
- Put the page next to its location plate: same family?
- Would an 11-year-old find it cool, not babyish?

## 2. What went wrong before (don't repeat)
1. The old pipeline made worksheets: flat colour, stacks of plain boxes, no drawn maths (P039 V09, P089–P091 samples).
2. Speaker names were printed in balloons; balloons were rectangles. Painted maths appeared in the art.
3. A1 (earlier today) fixed the creativity but looked **kiddish**: bunting, an awning, pastel tickets, washi tape, a
   rounded font and cartoon gift boxes.
4. A2 fixed the kiddishness but used **off-world** colours (cyan HUD glow, ember haze, holographic foil) and flat
   line-art that did not match the painted locations.
5. Keep A1's *layout ideas* (objects per role, drawn maths, companions, delights) and A2's *grown-up objects*. Take
   colours, materials and light from the plates (A3).

## 3. Colour (sampled from the plates)
Kit variables:

| Role | Variable | Value |
|---|---|---|
| Royal-blue planks | `--royal` | `#234d95` |
| Lacquer gradient | `--lacquer` | `#2a519a` → `#132b62` |
| Navy shadow | `--night` | `#0c1933` |
| Lamp gold | `--brasshi` | `#f7d9a0` (highlight); plate lamp glow `#f7c684` |
| Brass trim | `--brass` | `#d0a050` |
| Copper-brass | `--copper` | `#b3722f` |
| Brass metal | `--metal` | gradient |
| Moonlight | `--ice` | `#a6c6f5` |
| Cream marble | `--ivory` | `#efe4d0` |
| Warm stone | `--stone` | `#87634c` |
| Maroon / wax | `--crimson` | `#9b2230`; warning red `#bd2d1b` sparingly |
| Ink | `--inkc` | `#121a33` |

- Each page's **colour story** is royal + brass, plus lamp gold and/or moonlight carrying the idea (e.g. warm
  lamp-lit city vs moonlit frozen city).
- Reading text: dark ink on cream objects. Ivory on royal/navy is for titles and one-line captions only.
- **Maths colour keeps its job** (V09), in the plate family:
  - royal blue `.mt` (`#1f4f9a`, moonlight `#cfe0fa` on dark panels) = the tracked quantity;
  - copper `.mr` (`#a3561c`) = a second role;
  - operators and `=` stay ink.

## 4. Type
| Role | Face | Size |
|---|---|---|
| Page title | **Cinzel** 700 (`.h-title`, `.nameplate`) | 26–40 pt (`.alt` span for a second colour) |
| Sub-heads ("Example 11", "Now you try", "Check your method") | **Rajdhani** 700 caps, tracked (`.label` + a monoline icon) | 17–20 pt |
| Teaching prose, figure labels | Source Sans 3 | 14/18 pt |
| Narration / captions | Source Serif 4 (`.capnote`, `.letter`) | 14/18 pt |
| Story speech | Source Sans 3 Semibold (`.say`) | 14/18 pt |
| Companion aside to the reader | **Caveat** handwriting (`.say.aside`) | 19/21 pt |
| Display maths | Source Sans 3 Semibold (`.eq`) | 20–28 pt |
| Folio digits, figure readouts | Rajdhani 700 | 10–19 pt |

Never shrink essential text below 14 pt (body) to fit art. Shrink or move the decoration instead.

## 5. One object per text role (consistent all book long)
| Manuscript role | Object (kit class) | Notes |
|---|---|---|
| Question, "Try", "Now you try", "Pause and think" | `.ticket` (VIP pass, icon in `.stub`), `.mcard` (mission file) or `.tag` (cargo/shop problems) | sits **before** its working |
| Worked example / "Let's work it through" | `.ledger` (field notebook) or `.sheet` | `=` aligned in a grid when it carries meaning |
| "Check your method / thinking", answers | `.flap` with a `.seal` (eye/key icon) | after the attempt; separable |
| The one key result or rule | `.plaque` (brass) or `.slate` (glass HUD) | max one per page |
| Narrator opening / reader address | `.letter` (+ `.mounts`, `.wax`) | |
| Story caption | `.capnote` | |
| Speech | `.say` + curved `svg.tail` to the mouth | no speaker names, ever |
| Companion remark to the reader | `.say.aside` (Caveat) | only if the manuscript gives the line |
| Title / heading | `.h-title`, `.nameplate`, `.label` | |
| Folio | `.moonclock` (`--t = page / last page`; CH01: 107) | every page |

## 6. Book furniture (recurring signatures)
1. **The moonset dial** folio on every page: a precision brass dial, with the moon sinking towards the ember moonset mark.
2. **One ornament system per page** (all taken from the plates' trim, banners and lamps), rotated between neighbours:
   - `.deco-frame` (Art-Deco page frame);
   - `.trim-band` (banner moon + star);
   - `.lightstring` (warm bokeh lights);
   - `.rule-orn` dividers;
   - `.hud` corner brackets on the hero;
   - `.emblem` / `.watermark.compass`;
   - `.skyline`.
3. **A companion on most pages**, entering differently each time:
   - `.jharokha` (carved window);
   - `.pop` (steps out of a frame);
   - `.snap` (a photo);
   - leaning on a library ledge.

   Silent unless the manuscript gives an aside.

## 7. Draw the maths, as in-world illustration (painterly, like the plates)
When the content has a picture in it, draw it as an **exact SVG illustration of a thing that could stand in the
plates**, rendered in their style:
- precision gauges in brass and glass on a royal lacquer panel;
- lift shafts in cut-away with brass rails;
- the plates' own blue lacquered kit boxes with brass corner caps;
- velvet pouches with gold cords;
- lamp-lit city silhouettes vs moonlit snowy roofs;
- number lines as brass rails with glowing lamp or moonlight markers.

How to render it:
- `linearGradient`/`radialGradient` fills (light from the lamp side);
- a 1–2 pt specular highlight on brass edges;
- a soft shadow below;
- a glow halo on lights.

Exactness rules (unchanged):
- Every count, length and label is true. Labels use only numbers and words from the manuscript.
- A question's figure shows only the question's data. Anything that reveals the answer sits in or after the working/answer object.
- A countable picture (9 packages) only when the count is the true answer and it sits after the question. The math-checker checks it.
- Decoration never looks countable beside a calculation.
- Production notes (`Production note Vnn`) bind; style them with the kit.

## 8. Story pages
- Cinematic panels (`.frame-panel`, thin brass edge) on a royal/navy stage (or the scene's own softened plate). Vary the shapes:
  - a wide hero;
  - a round inset (`.frame-panel.round`) for a reaction;
  - a `.jharokha` peek;
  - a jagged or angled cut for action.
- On most story pages, a character or prop **breaks a frame** (`.pop`).
- Captions are `.capnote`, away from faces. Speech is `.say`, in speaking order, tails to mouths.

## 9. Creativity is free; keep it that way
The kit, the fonts and the SVG illustrations cost nothing. Art: reuse first (library cut-outs, plates, zoom
crops). A new image only for a specific story moment (panel-artist, Batch API).

## 10. The page brief (`pages.json` → `"art"`), written before building
```json
"art": {
  "idea": "one sentence: the page as a mission moment, object or place at the Midnight Mela",
  "stage": "stage-planks | stage-cinema | stage-backdrop (plate S04-B01)", "ornament": "deco-frame + trim-band along the top",
  "hero": "what the eye lands on first at thumbnail size",
  "objects": {"question": "ticket", "working": "ledger", "answers": "flap", "result": "plaque"},
  "illustrate": "the exact technical illustration, and where it sits",
  "companion": "who, how they enter (jharokha / pop / snap / ledge), where, aside text if any",
  "colour": "royal + brass + lamp gold and/or moonlight; maths royal tracks …",
  "delights": ["2–3 small wordless surprises tied to THIS page, cool not cute"],
  "folio": "moonclock --t 0.364",
  "varies": "how it differs from the previous page"
}
```

## 11. Scorecard (builder self-check; master review). Ship at ≥ 8/10 with all musts.
**Musts (any miss = fix):**
- text verbatim, no invented words;
- maths exact and tagged;
- question before answer;
- body text ≥ 14 pt, dark-on-light;
- nothing clipped or over a face;
- no speaker names;
- **nothing kiddish or off-world (§1 banned list)**;
- **same family as the location plates**.

**Score 1 point each:**
1. A clear **hero** at thumbnail size.
2. A cinematic **stage**.
3. A **colour story** from the plates' light and metal (royal, brass, lamp gold, moonlight), not candy or neon fills.
4. Text sits on **valuable objects** (pass, file, notebook, seal), not plain boxes.
5. The **maths is drawn** as an in-world painterly illustration.
6. A **character** with presence (or, on story pages, a frame-break).
7. **Depth**: overlaps, glow, a pop-out.
8. **2+ delights** specific to this page.
9. **Book furniture**: the moonclock and one ornament system.
10. It **differs from its neighbour**, with no dead hole larger than about 1/8 of the page.

**Would an 11-year-old show this page to a friend?**
