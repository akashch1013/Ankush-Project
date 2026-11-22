# ChandRush page patterns (from the four approved sample PDFs)

> **Design Manual V09 governs (2026-11-22).** Read `manual-v09.md` first. Use the layouts below as starting grids only; where they disagree with V09 (type sizes, captions/bubbles 14/18 pt, gutter colours, edges, companions, maths colour), V09 wins.

The sheet is 864 × 648 pt (12 × 9 in, landscape). Coordinates are in pt: `left, top, width, height`. `samples/*.jpg` are renders of the approved pages. **Open the sample named for a pattern before building a page with it**, and copy its proportions, spacing and hierarchy. Snippets for each pattern are in `components.html`.

Choose the pattern from the page's content (master's `pages.json` → `pattern`). Vary patterns and themes between neighbouring pages; don't use the same pattern 3 times in a row.

## Story pages (no teaching)
| ID | Use for | Layout | Samples |
|---|---|---|---|
| **S1 hero+2** | a key moment, then two follow-up details | hero panel `20,20,824,400`; two panels below, split ≈ 1/3 : 2/3 (`20,432,262,196` + `294,432,550,196`). A detail panel may be a `.panel.zoom` crop of the hero art | opening-01, -02, -03 |
| **S2 stack** | two wide beats in sequence | two full-width panels `20,20,824,296` and `20,328,824,300`; a one-line caption band may sit between them | opening-07, -09 |
| **S3 tall+stack** | a character entrance (tall figure) + two smaller beats | left column: two stacked panels `20,20,250,300` + `20,330,250,298`; right tall panel `282,20,562,608` | opening-10 |
| **S4 grid** | 3–4 quick beats or dialogue exchange | 1 wide top `20,20,824,300` + 2 bottom `20,330,407,298` + `437,330,407,298`; or 2×2 | opening-11, -12 |
| **S5 opener** | chapter opener / reveal | kicker + big serif title at top (`36,24`), hero art `36,110,792,470` in a thin gold frame, one caption | ref-1, opening-05 |
| **S6 question** | end-of-sequence prompt to the reader | wide panel top 55%, then a serif question heading and short text with a small inset panel at right | opening-04 |

Story captions: pale `.cap` boxes in a panel corner, away from faces, ≤ 60 words per box. Bubbles: `.bubble` near the speaker, tail toward the mouth; the reading order follows the speaking order, left→right, top→bottom.

## Story + maths pages
| ID | Use for | Layout | Samples |
|---|---|---|---|
| **M1 panel-top** | a story beat that introduces the maths | title `30,18`; wide panel `30,60,804,300` (caption + bubble + optional `.overlay` with a mini diagram); below: teaching in two columns `30,378,804,250` | storymath-1, -2 |
| **M2 panel+inset** | the maths on a physical object | title; panel `30,60,804,300`; below-left an inset detail panel (`.panel.zoom` of the same art) `30,378,330,110` with a caption under it; teaching on the right `400,378,434,250` | storymath-3 |
| **M3 side** | dialogue-heavy maths reasoning | tall panel left `30,60,420,568` with captions/bubbles at the bottom; teaching column right `470,60,364,568` ending with a highlighted result (`.eq.hl`) and tiles/badges | storymath-4 |
| **M4 panel+example** | the story resolves; a worked comparison | title; panel `30,60,804,300`; below-left: teaching text and paired examples (`.eq` lines with a left rule); below-right: small inset panel | storymath-5, P018 preview |

## Text-led teaching pages (paper themes)
| ID | Use for | Layout | Samples |
|---|---|---|---|
| **T1 vignette** | explanation + one character aside | `.runhead` top; title `36,48`; teaching `36,100,520,520`; character `.vignette` right `600,150,220,300` with a `.bubble` above it (the aside text) | textled-2, -3, -5, ref-3 |
| **T2 split** | a big idea with a hero prop | left paper area `0,0,560,648` with title + teaching; right `.side-dark` band `560,0,304,648` with a prop (bell/lantern/moon) and a character vignette with a bubble | textled-1 |
| **T3 worked example** | step-by-step calculation | title; dark `.bar` "Calculate: …"; `.steps` timeline (Step 1…4 with working); final `.answer` box; vignette right with an aside | ref-4 |
| **T4 reference table** | summaries, rules, lists of tests | title + one-line intro; dark rounded `.card` holding `table.tbl` with `.pill` numbers; vignette right with an aside | ref-3 |
| **T5 open book** | revision / exercise sets / lists of results | title; open-book art (`library/X-BOOK-*`) `120,110,640,500` with text placed on `.leaf` left and right; a small prop (bell) top-right | ref-5, textled-3 |
| **T6 diagrams** | geometry / measurement questions | title + question text; a row of exact SVG diagrams with dimension labels and blanks; "Step-by-step solution" list below; vignette right | ref-2 |
| **T7 brackets/rules** | rule lists with numbered steps | full-width dark band at the top holding two contrasting expressions; numbered `.numdot` rules below; vignette or prop at the right | textled-4 |

Paper pages use `.runhead`: `CHANDRUSH: THE MIDNIGHT MELA` · `CHAPTER n · TOPIC` · `PAGE nn`. Add one edge motif (`.edge.dash`, `.edge.stub`, `.edge.bunting`, `.edge.tick`) and vary it between pages.

## Typography and spacing rules (all patterns)
- Body 14 pt on 18 pt (`--body`). Captions, bubbles and asides 14/18 pt (V09). 13/17 pt only as a recorded exception.
- Chapter titles 24–36 pt Source Serif 4 Semibold; subheads 16–19 pt Source Sans 3 Semibold. Maths display 20–30 pt (`.eq`).
- Use at most 3 text sizes in the teaching area. Keep line length ≤ 75 characters (use `.cols` for wide areas).
- Keep 20–36 pt outer margins, and leave ≥ 10 pt between blocks. Nothing may overflow or touch the frame. Fill space with purpose: extend scenery or enlarge art rather than leaving a dead hole.
- Use true maths typography: `−` (U+2212), `×`, `÷`, superscripts with `<sup>`, thin non-breaking spaces where needed, and fractions as stacked `<span class="frac">` or `a/b` as the manuscript prints them. Wrap every equation in `data-math` (exact) and keep `.m` (no line breaks inside maths).
- A question always comes before its working and answer in the reading order. A question figure never shows the answer.
- Colours come from the theme variables. To recolour a page, change only the theme class or the `--` variables.

## Theme choice
| Content | Themes |
|---|---|
| Night story scenes (most ChandRush locations) | `theme-navy`, `theme-teal`, `theme-plum`, `theme-slate` |
| Warm reveal / fair-wide moments | `theme-ochre` frame around dark art |
| Text-led teaching | `theme-paper`, `theme-sage`, `theme-lilac`, `theme-mist`, `theme-blush` |

Pick the theme that best matches the dominant art colours of the page's panels. When the user asks for a colour change, record it in LESSONS.md and apply it to all later pages of that kind.
