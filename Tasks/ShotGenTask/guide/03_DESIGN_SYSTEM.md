# 03 · Design system — reproducing the sample look in code

Every value here was **measured** from `Completed Samples/pdf/CHANDRUSH-OPENING-V04-STORY-CONTINUITY-REVISION.pdf`, using vector drawings, text spans and fonts read with PyMuPDF. The values are stored in `design/tokens.json`. Change a token there and every page follows. Check the result with `python -m pipeline compare --page N --sample M`.

## Page

| Token | Value | Sample evidence |
|---|---|---|
| Page | 864 × 648 pt (12 × 9 in, landscape 4:3) | every sample page |
| Content area | x 24–840, y 24–618 | frames start at 24 and end at 618 or 840 |
| Gutter | about 20 pt (sample uses 17–23) | p01 frames 289→305, p10 234→254 |
| Frame stroke | 1.1 pt in the theme's accent colour | every framed image |
| Page number | Source Sans 3 Regular 8 pt, right edge at 832, baseline 629 | "01"…"12" |

## Themes (background · accent · caption fill)

The Opening sample is a **colour study**: each page uses one dark background with a matching accent. Use a theme per scene, so neighbouring pages feel related.

| Theme | Background | Accent | Caption fill | Sample | Used for |
|---|---|---|---|---|---|
| `gate_navy` | #0d1c32 | #d7b468 gold | #e1e8ed | p01 | P009 |
| `gate_slate` | #263b49 | #c29a6f copper | #e4e9ec | p10 | P010 |
| `gate_night` | #233143 | #c6bbdd lavender | #e8e3ef | p11 | P011 |
| `court_teal` | #193337 | #bdb994 sage gold | #e1ebe7 | p12 | P012 |
| `court_deepteal` | #163c40 | #bdd3d1 pale teal | #e0ece8 | p02 | P013 |

Other themes in the file, for later scenes: `lane_blue`, `slate_ice`, `indigo_mist`, `plum_copper`, `wine_gold`, `forest_gold`, and the light `sand_double`.

## Borders (outer ornaments)

| Variant | Description | Sample | Rule Book family |
|---|---|---|---|
| `lantern_brackets` | stepped corner brackets with small ring ends | p08 | Lantern Brackets |
| `silver_moonline` | side rules with dot pairs plus top/bottom hairlines | p10 | Silver Moonline |
| `mirror_diamond` | top/bottom rules broken by a centred diamond; side rules | p11 | Mirror Tile Corners |
| `gate_arch` | an arched lintel over the page plus side and bottom rules | p12 | Old Blue Gate Inlay |
| `cube_chamfer` | chamfered corner brackets with a dot | p03 | Cube Lantern Lattice |
| `pavilion_hem` | zig-zag hems top and bottom | p06 | Pavilion Hem |
| `double_frame` | two thin rounded frames (light theme) | p07 | Star Enamel Corners |
| `none` | no ornament | p05, p09 | — |

Never use the crescent-moon border from sample p01/p04 (rule C6).

## Narration caption

- A rounded box with radius 7 pt, filled with the theme's caption colour and a faint paper speckle (as in the sample).
- No outline.
- Text: Source Serif 4 Regular 14 pt, leading 16.1, colour #203345, left-aligned.
- Padding: 5 pt at the sides. The first baseline is 19 pt below the box top, and the box ends 11.5 pt below the last baseline.
- **Width:** `w` in the layout sets the maximum measure. The box shrinks to the longest line, as the sample's boxes do.
- **Placement:** over a calm area of the art, normally about 13–18 pt inside the frame's top corner.

## Speech balloon

- A rounded rectangle with radius 9, fill #fffdf8, outline 0.8 pt in #203345, and round joins at the tail.
- Text: Source Sans 3 Semibold 14 pt, leading 16.1, centred. Lines are balanced: the measure narrows until one more line would be needed, giving the sample's even shapes.
- Padding: 6 pt at the sides, first baseline 18.5 pt down, bottom 8.5 pt below the last baseline.
- **Tail:** a straight wedge 12 pt wide at the base. It leaves through the edge facing the speaker and stops 8 pt before the recorded target point. It is never shorter than 13 pt and never longer than 90 pt.

## Reader call-out

Source Serif 4 Semibold 16 pt, leading 18.4, ivory (#f3ecd9) on dark themes and navy on light ones. It is set straight on the page background, as in sample p07 ("ChandRush Crew, tonight the travelling fair has chosen Mumbai.") and p04.

## Art in frames

- **Cover-fit:** one uniform scale, so the image fills the frame, cropped by it. `focus` [u, v] keeps a chosen image point centred, and `zoom` ≥ 1 tightens the shot.
- **Embedding:** the visible crop is embedded as a high-quality JPEG (quality 93, no chroma subsampling).
- **Effective ppi:** reported per panel. The target is 300 ppi; the generation sizes in the prompts are chosen for it.

## Layout patterns used in this batch (all from the sample's vocabulary)

| Page | Pattern | Why |
|---|---|---|
| P009 | 2×2 with an unequal top row (wide plus tall close-up) | decision and reaction; then two parallel explanations |
| P010 | tall left panel, right column stepping down into an inset with the reader call-out | ends the page by speaking to the reader |
| P011 | two full-width tiers, the lower one taller | the reveal gets the most space |
| P012 | two full-width tiers, the lower one narrower | the group explanation, then a close beat |
| P013 | wide plus narrow on top, full-width bottom | two beats, then the mission statement across the page |

## Do / don't

- **Do** reserve calm areas for text in the prompt, so captions never sit on faces.
- **Do** keep 12 pt or more between any text and the trim. The build checks this.
- **Don't** add decoration while text needs the space. **Don't** give maths panels ornamental poster frames (Rule Book D10).
- **Don't** change token values for one page. If the sample shows a different value, change the token for all pages and rebuild.
