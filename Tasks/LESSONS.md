# LESSONS: rules learned from the user's feedback

Print only your part (Common + sections naming your role), from `Tasks/`:
`awk -v r=page-builder '/^## /{p=($0~/^## Common/||index($0,r))} p' LESSONS.md`
Roles: master, chapter-setup, bg-artist, panel-artist, art-director, page-builder, math-checker. Old section names follow the `·`.

Master: after feedback (raw words to FEEDBACK.md) add a dated rule under the section it governs, or a new `## <roles> · <stage>`. Newer rules override older ones and any skill or guide default.

## Common · All stages, Maths
- 2026-10-27 / 11-04 / 11-22 · Images (see `CLAUDE.md` rule 3): `high`; `xhigh` only when hard; never `max` without asking ("max is too much"). Batch API for everything, incl. fixes, samples (small batch) and the critical path; no immediate calls until the user says so. After 3 calls accept as-is, log the defect, no 4th call.
- 2026-11-22 · Keep cost low without losing quality: reuse art (zoom crops, library), attach only the references that are needed, use 1K-class sizes.
- 2026-11-22 · Mathematical correctness is mandatory. Minor non-maths mistakes are acceptable.
- 2026-11-24 · Token budget. Caps: page-builder ≤ 4 renders/page; ≤ 2 maths-fix rounds; ≤ 1 review-fix round; at a cap, stop and report what's left for the user. Read an image only when you must judge it. Prefer one contact sheet over many images. After a render, read `preview.png` once; crop only to check a specific issue. Never re-read an image already in your context.

## master, chapter-setup · Stage 0 (planning)
- 2026-11-23 · CH01 source is **manuscript V06** (`Reference/Chap1 Corrected/CH01-PANELIZED-MANUSCRIPT-V06.docx`); `src/` and `manuscript.txt` were regenerated from it.

## master, chapter-setup, page-builder, math-checker · Maths
- 2026-11-22 · Manuscript equations are Word objects (powers, fractions, roots). Always use `textcheck.py dump/pages` (it converts them to `2²`, `7/4`, `√49`). If you see blanks such as `(i)  −  (ii)`, the source files are stale: re-run `pages`.
- 2026-11-22 · `textcheck page` only checks plan→HTML. Before building, compare every `[Equation]`/`[MathExample]`/`[AnswerLead]` line in `src/Pxxx.txt` against the plan: old P039 silently dropped three factor equations.

## bg-artist · Backgrounds (stage 1)
- 2026-10-21 · Reference images carry painted titles, white labels and arrows: tell the model to ignore them, or they leak.
- 2026-10-21 · Never send the spatial authority map to the model. Read it yourself while writing prompts.
- 2026-10-20 · Art direction: a mix of illustration and reality; grand, mystic and magical; real architectural detailing (see `BagroundGenTask/spec/style.txt`).

## panel-artist · Panel art (stage 2)
- 2026-11-22 · Bubbles/captions are HTML (rule 4): reserve calm empty areas for them.
- Author correction in the CH01 manuscript: all human characters have fair skin.

## master, panel-artist, art-director, page-builder · Continuity and characters (stage 0–3)
- 2026-11-25 · **Never alter the structure of a background object to fit the story.** (CH01 P002: a new cart handle appeared just so Tez could bump into it.) Study the plate first, then stage the action inside the plate as it is: same carts, walls, arches and positions in every panel. Pick the view/crop where the action naturally happens.
- 2026-11-25 · **Always read the page before and the page after** (`src/`) before planning, briefing or painting a page: no continuity jumps in props, positions, lighting state or who is present.
- 2026-11-25 · **Characters only as on their character sheet** (attach the sheet; never re-imagine a character from the page's description). Tara's expression is always a calm, wise old lady: never animated or cartoon-surprised.
- 2026-11-25 · CH01 P001: the street is behind the characters and Tez, with Tez on the line of the parked cart's handle so he can walk into it naturally on P002.

## master, art-director, page-builder · Art direction (stage 2.5 + 3): governs the look
- 2026-11-23 · **B1 "Ledger Plate" (CH01 P039) is approved** ("The latest sample was good"). It is the reference look: manual V09 type/colour on calm light reading shapes, with the creativity in a page border made from the location plate's materials. Teaching pages copy P039's markup; story pages keep the same type and border family, re-materialed for their own location (e.g. Food Street: peacock-teal gutters, canopy seam, brass bracket, hanging lantern), and put captions/speech on light matte boxes/balloons. This supersedes ART-DIRECTION A4's full-bleed world + dark glass for the reading areas.
- 2026-11-23 · **Pure-maths / teaching-only pages: calm light field, decorated border.** No busy or dark background behind text (no backdrop plate, no glass over scenery). Text sits on a flat light paper shade (#F7F1E3 warm cream). The creativity moves to the **page border**: a band built from the location plate's materials (royal-blue lacquer with gold pinstripe, brass kit-box corner caps, brass rail/lantern bracket arm, the banners' moon + star medallion), constructed per manual V09 pp.15–16 (rules 0.5–1.1 pt, strongest accent at entry and finish). Fonts, sizes and maths colours follow manual V09 exactly (Source Sans 3 / Source Serif 4, 14/18 body, 16–19 subheads, teal HCF / terracotta second role) — no display fonts or Caveat on these pages. No countable decoration near the evidence. (CH01 P039 B1)
- 2026-11-22 · **Page graphics, colours and illustration style match the location images** (from the A3 era, now archived in `design/archive-a3/`; the rule still holds). Colours are sampled from `BagroundGenTask/out/plates`: royal-blue planks #234d95, navy shadow #0c1933, lamp gold #f7c684, brass #b3722f, cream marble, warm stone #87634c, moonlight #a6c6f5, a little warning red. Materials come from the plates too: royal-blue lacquered wood with gold pinstripe, brass with warm highlights, cream marble, the banners' gold moon and star. Illustrations are painterly and semi-realistic, like the plates: gradients, warm lamp key light, cool moon rim, specular brass, soft shadows. No flat line-art heroes, no cyan or neon, no holographic foil. Use the page's own plate as a softened backdrop when it helps (`pagekit.py backdrop`).
- 2026-11-22 · **Audience is 11 years old: graphics must be aspirational and cool, never kiddish.** Keep the creative layouts (objects per role, drawn maths, companions, delights). Make the look feel older: a graphic novel + engineering + mission-file aesthetic. That means brass and glass, jali lattice, blueprint linework, VIP passes, a Moleskine-style notebook, precision dials, and monoline technical infographics, in cinematic midnight with brass/cyan/ember light. Banned as kiddish: party bunting, cartoon garlands, striped awnings, pastel fills, washi tape, rounded "bubble" fonts (Baloo), cartoon icons with bows/stars/smoke, paw trails, cute houses. Supersedes the A1 mela-brights look (ART-DIRECTION A2).
- 2026-11-22 · "It is a page of a child's book! It should be creative: colours, some art, some unique things." → hard rule 0 (ART-DIRECTION.md, `design/kit.css`, scorecard ≥ 8/10 + musts): a stage, objects per role, drawn maths, a companion with a new entrance, 2–3 page-specific delights, the moonclock folio; A1 "moonlit block-print" graphics retired. This **overrides** V09's restraint on decoration and colour ("cut decoration", "only a sliver of gutter colour", "no oval… ") and the "follow the sample PDF patterns exactly" rule. V09 still governs type sizes, maths layout and proof.
- 2026-11-22 · The user wants **new creativity, not copies** of the old samples. Find each page's idea in its content (temperatures → two towns and a thermometer; sharing → a gift stall), never in generic decoration.
- 2026-11-22 · Same text role, same object, all book long: ticket/mcard/tag = question, ledger = worked steps, flap = answers, plaque/slate = the key result, letter/capnote = narration, `.say.aside` in Caveat = a companion remark. No speaker names printed. No maths painted in art.

## master, art-director, page-builder · Layout (stage 3), Design Manual V09
- 2026-11-25 · **Page label on every page:** `CHAPTER 01 - NUMBERS - PG 001` (chapter number 2 digits, chapter topic in caps, page 3 digits), small tracked caps in the border/folio area.
- 2026-11-25 · **Story pages: balloons and captions sit on the art, not in the gutters.** Keep gutters tight (6–10 pt) so the panels get the area; never widen a gap to hold a dialogue box. Keep boxes off faces.
- 2026-11-25 · **Chapter/scene openers:** a gate/arch effect framing the page is good (feeling of the start of the story); background colour deep with subtle gradation.
- 2026-11-25 · **Category reference pages** live in `PdfSheetsGenTask/design/references/` (one per page category, see its README). Open the one matching the page's `category` before briefing or building: copy its quality bar and structure, never its exact layout; similar pages must not repeat a design.
- 2026-11-22 · `PdfSheetsGenTask/CHANDRUSH-PAGE-DESIGN-MANUAL-V09.pdf` is the design authority (digest: `design/manual-v09.md`); it overrides patterns.md where they differ. Captions, speech and asides 14/18 pt; subheads Source Sans 3 Semibold 16–19 pt; running line 10–12 pt; gutter colours indigo/teal/aubergine/slate as a sliver on lesson pages; borders derived from a material in the scene, 0.5–1.1 pt; maths colour only with a job (teal tracked, terracotta second role).
- 2026-11-22 · Teaching companions sit on a support from their scene (bench, ledge) with the scenery fading irregularly into the paper; no oval vignettes. (Still true: other entrances such as jharokha/pop/snap are now also allowed by ART-DIRECTION.md.) Supersedes the "vignettes fill their column" rule below where they conflict.
- 2026-11-22 · (V09-era, first sample page) Vignettes must fill their column: use a tall box with `object-fit: cover` and place the bubble over the vignette's calm top edge with a short tail to the mouth, not a small figure under an empty column. (CH01 P039)
- 2026-11-22 · (superseded by Art direction above) Follow the patterns of the four sample PDFs (`PdfSheetsGenTask/design/patterns.md`). Colours may vary by page content; the user will ask for colour changes when needed.
- 2026-11-22 · The artifact shows only the page, nothing else (rule 7).
