# PAGE-DESIGN: the ChandRush page card (current as of 2026-11-25)

This is the one design document the art-director and page-builder read. It merges every decision the user has made so far. ART-DIRECTION.md, patterns.md and manual-v09.md are now background reference only. Where they disagree with this card, this card wins. A `LESSONS.md` rule dated **after 2026-11-25** wins over this card.

## 1. Who it is for, and how it should feel
- **Readers are about 11.** Make it feel like a cool graphic novel crossed with an engineering mission file: brass, glass, blueprint linework, precision dials, field notebooks, lamp-lit night. Never kiddish.
- **Same family as the location plates.** Sample the palette from the page's own plate (`BagroundGenTask/out/plates`):
  - royal-blue planks #234d95, navy shadow #0c1933;
  - lamp gold #f7c684, brass #b3722f;
  - cream marble, warm stone #87634c, moonlight #a6c6f5;
  - a little warning red.

  Take materials from the plate too: royal-blue lacquer with gold pinstripe, brass, cart timber, peacock-teal canopy, the banners' moon and star. Light is painterly: a warm lamp key light, a cool moon rim, specular brass and soft shadows.
- **Design like a real book designer.** That means:
  - a grid;
  - one entry point and a deliberate reading path;
  - shaped whitespace, with no dead holes;
  - images framed with intent;
  - rhythm across spreads (dark story pages, light lesson pages).
- **Banned:**
  - Kiddish: bunting, marigolds, striped awnings, pastel blocks, washi tape, rounded "fun" fonts, emoji or cartoon icons, stickers, paw trails.
  - Off-world: neon cyan, HUD grids, sci-fi glow lines.
  - Worksheet: flat boxes on a flat colour, the same template page after page.

## 2. The fixed system: identical on every page
| Element | Rule |
|---|---|
| Sheet | 864 × 648 pt (12 × 9 in); 36 pt margins; 12 columns of 49.5 pt with 18 pt gutters; 18 pt baseline |
| Running head | `CHAPTER 01 · NUMBERS · PG 00N` in Source Sans 3 SemiBold 10 pt, small caps, tracked 1.6 pt, colour #e2c486 on dark (ink on light). Outer edge: verso left, recto right. A chapter opener puts it at the foot, on the folio line. |
| Folio | Moonclock, bottom centre. Lit fraction = page ÷ last page (CH01: 107). |
| Speech | 14/18 pt Source Sans 3 SemiBold, ink #1d2433 on ivory #FFFDF6. **Only via `pipeline/balloon.py`** (§4). |
| Captions | 14/18 pt Source Serif 4 on cream paper #F7F1E3 with a .6 pt brass #b3722f rule and a soft shadow. Placed on the art. |
| Teaching text | Body ≥ 14/18 pt; subheads Source Sans 3 SemiBold 16–19 pt; dark ink on light paper. Maths colour only with a job (teal = tracked quantity, terracotta = second role). |
| Story field | Deep colour with subtle gradation (the P001 navy is approved) |
| Teaching field | Calm light paper (#F7F1E3 or pale stone). The creativity goes into the border (P039 "Ledger Plate" is approved). Never put text over a busy image. |
| Border | Built from **this page's** location material (cart timber, lift gate brass, Food Street canopy…). Rules .5–1.1 pt, strongest accent at the entry and the finish. |
| Maths | Exact SVG/HTML, every statement tagged `data-math`, question before answer, no maths painted in the art. CH01 lift strip = SVG insert from +2 to −8. |
| Words | Verbatim from the manuscript. No speaker names, no invented words, no production notes. |

## 3. Varied on every page: randomness inside the system
1. Run `python3 pipeline/vary.py <CHxx> <pages> --write`. Each page gets a seeded **variation card**: grid, panel accent, border build, entry corner, field, hero slot, gutter and light link (teaching pages get hero slot, work object, companion entry and answer object). The card never repeats a neighbour's choice.
2. Start from the card. Override an axis only when the page's content calls for it, and write the reason in the brief.
3. Find the page's **idea in its content**, not in decoration. Make the page a place or an object at the fair:
   - P002: the culprit cart handle becomes the border's top arm, its grip right where Tez bumped it;
   - P003: the lift shaft becomes a tall right column.
4. Add **2–3 delights** born from this page's story: light spilling across a gutter, a prop crossing the frame, a material detail in the border. Never repeat a neighbour's delight.
5. Approved references to learn from:
   - P001: arch-gate opener;
   - P107: story page, loved;
   - P039: teaching, Ledger Plate;
   - P002 and P003: the border is the scene's object.

   Learn the principles. Don't copy the layouts.

## 4. Text on the images (balloons and captions)
- Balloons and captions sit **on the panel art**, over its calm, low-detail areas. Never put them over faces, hands, the key prop or a clue, and never in gutters or bands between panels. Gutters are 9–12 pt, and the panels take all the remaining area: art ≥ 70% of a story page.
- **Balloons come only from `pipeline/balloon.py`.** Each balloon body and its tail are one SVG outline, so the join can't break. Write a spec (`text`, `at` or `center`, `tip`, optional `maxw`, `shape`, `bend`, `link`):
  - in a generator, use `from common import bln` and put `{bln(spec)}` in the body;
  - in a hand-built page, use `PAGE_DIR/balloons.json`, then `python3 pipeline/balloon.py PAGE_DIR`.
  - The tool sizes each balloon from the real font. `python3 pipeline/balloon.py --measure "text" --maxw 200` gives the box before you place it.
- **Tails:**
  - the tip stops 4–8 pt short of the speaker's mouth, pointing at it;
  - the tail leaves the side of the balloon nearest the speaker;
  - an off-panel speaker's tail points off the panel edge;
  - consecutive balloons from one speaker are joined with `link` (one beat), never two separate tails.
- **Reading order:** left to right, top to bottom. Place the first speaker's balloon highest and leftmost, and keep balloons in speaking order.

## 5. Layout first, then art (saves calls and crops)
Before any image is generated, the brief fixes for each panel:
- its box in pt, which gives its aspect and image size;
- its text zones in panel fractions: which corner or band each balloon and caption occupies, sized with `--measure`.

The panel-artist writes those zones into the prompt as reserved calm areas, so the art arrives with space where the words go. After the art arrives, letter on the real image, read the page in order, and check it beside its neighbours.

## 6. Scorecard: ship at ≥ 8/10 and every must
**Musts:**
- text verbatim;
- math-checker PASS;
- nothing clipped or overflowing;
- no balloon or caption over a face;
- seamless tails aimed at the speaker;
- running head and folio present;
- nothing banned;
- question before answer.

**Points (1 each):**
1. The idea is born from the content.
2. One clear hero and entry point.
3. A clean reading path.
4. The art is big (story pages: panels ≥ 70% of the sheet).
5. It is in the location's family (palette, materials, light).
6. The border is built from this page's own location.
7. It differs from its neighbours (variation card honoured).
8. There are 2–3 story-born delights.
9. Depth and light: overlap, glow, a break-out.
10. An 11-year-old would think it looks cool.
