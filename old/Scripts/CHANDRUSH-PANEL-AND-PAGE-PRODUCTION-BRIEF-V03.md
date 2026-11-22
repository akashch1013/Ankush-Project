# ChandRush panel creation and page assembly

## Reusable instructions for an AI production model

**Version 03 | 28 September 2026 | Model-neutral production brief**

You are responsible for creating the individual ChandRush panels and assembling them into finished graphic-novel pages yourself, using the image-generation, layout and file-rendering tools available in your environment. This is an execution brief, not merely a request to write prompts or propose a workflow.

**Required sequence: plan the page → create each panel separately → audit and save each panel → assemble the saved panels → inspect and export the complete page → present the batch for review.**

Do not generate a complete multi-panel page as one image. Keep exact text, speech balloons, maths and page furniture independently editable in the source project. Use image generation for illustrations and precise vector/layout tools for exact diagrams and final assembly. The same requirements apply regardless of model, provider, programming language or assembly software.

These instructions consolidate the earlier production rulebooks, the current V04 manuscript and subsequent layout and typography tests. Version 03 replaces the earlier handover briefs for page production. Later explicit user decisions take precedence. Do not treat an old test setting as a permanent rule.

## 1. What you are creating

Create **ChandRush: The Midnight Mela**, a story-led educational graphic novel for approximately 11-12-year-old Grade 6 readers, teaching Cambridge Lower Secondary Mathematics 7 in the manuscript's sequence. Ahana, Vihaan and Navya visit a travelling full-moon fair, where the missing Moon Bell and the repairs connect the story to mathematics. Use the manuscript for the actual events, characters and teaching.

The pages must work as an engaging graphic novel and as clear teaching material. Give meaningful story moments visual importance. Make mathematical explanations easy to follow. Aim for comfortable full-page reading on an iPad or laptop and high-quality physical printing.

Preserve the welcoming opening definition of ChandRush. The reader is part of the **ChandRush Crew**; do not draw an additional child to represent the reader. Do not invent new story events, explanations, jokes, questions or answers during page production.

**Central rule: Each ChandRush page must have a composition suited to its content.** Design assets for their final placed size and role on that page.

## 2. Current decisions and their status

| Item | Instruction and status |
|---|---|
| Chapter 1 source | Use **CH 01 PANELIZED MANUSCRIPT V04.docx** and its production notes. V02 and older rulebooks are historical references. |
| Novel page | **12 × 9 inches, landscape, 4:3; 864 × 648 points; 304.8 × 228.6 mm.** This is the working novel-page format, not the format of this handbook. |
| Composition | Content-specific on every page. Reuse styles and components; choose the geometry for the actual content. |
| Maths typography | **Source Sans 3**, Regular and Semibold. Current working default **14 pt / 18 pt leading**. |
| Dense maths option | **13 pt / 17 pt leading**, after layout improvements and a readability review. This is an allowed exception, not a word-count trigger. |
| Story narration | **Source Serif 4**, Regular and Semibold, **14 pt / 18 pt leading** in the current proofs. |
| Speech | **Source Serif 4, 12 pt / 15 pt leading** is the latest trial. Use it for the current comparison proofs; final book-wide speech-size approval remains open. |
| Page 16 | The approved pilot split is **16A / 16B**. Unsplit 14-point and 13-point proofs are alternatives, not an approved renumbering or replacement. |
| Review batches | Default **5 pages**, maximum **10 pages** per run, followed by review before the next batch. |
| Assembly responsibility | The executing model creates or reuses each panel asset, then assembles the saved components into pages using its available tools. Return the actual assembled pages and editable source. |
| Execution status | Earlier proofs establish design evidence. Verify fonts, rendering and exports in the actual production environment; this brief does not certify an unrun implementation. |
| Print state | Existing RGB, zero-bleed proof exports are review outputs. Final printer specifications and print preflight remain separate. |

The old minimum of 18 pt, the old blanket objection to serif dialogue, ten-page-only batching and older BLOCK/edit/regenerate loops are superseded by the current rules here. The preference for Source Serif 4 is explicit; do not substitute Times New Roman, Helvetica, Arial or an unnamed comic font merely because an older document mentions them.

## 3. Protect the source and separate its fields

Read the entire source page, its panel records, shared assignments, dependency notes, location exceptions and relevant preceding/following continuity before planning it.

- Preserve exact printable narration, dialogue, speaker, headings, questions, numbering, worked steps, answers, symbols, emphasis, table cells and intentional repetitions.
- Preserve panel IDs, content allocation and reading order. A Word sheet is not a graphic-novel page; use the explicit manuscript page and PANEL ID.
- Do not rewrite, shorten, simplify, silently correct, delete, duplicate or move content to solve a layout problem. Ordinary line wrapping can change; intentional equation rows, meaningful breaks and mathematical grouping must survive.
- Keep printable text, visible in-world lettering, diagram specifications, scene directions, reference assignments and controller metadata in separate fields.
- Do not print PRINTABLE/NON-PRINTABLE markers, issue notes, prompts, exception codes, filenames, internal IDs or instructions such as what an after-image should show.
- A NON-PRINTABLE instruction can still require a visible label or diagram. Render the specified label or diagram, not the production sentence describing it.
- Resolve every SHARED VISUAL ASSIGNMENT and PANEL ASSIGNMENT into the receiving panel's complete brief. Do not assume a model has another panel or an earlier chat available.
- Preserve dependencies and cross-page continuations. If the source contains a substantive contradiction, identify the exact source block and refer it for editorial review. Continue independent ready work; do not silently repair the manuscript.

Use the supplied character sheets and selected location files as visual authorities. Use textbooks or older story drafts only for an explicitly assigned verification task, never as replacement copy for V04. Inherited draft names inside V04 do not supersede its current panelisation and automation instructions.

## 4. Plan the complete page before creating artwork

The Page Director must decide the focal point, story/maths balance, reading path, panel dimensions, image crops, exact text areas, diagram areas, balloon positions and styles before generation. Compute the coordinates; do not require the user to design the layout numerically.

Use page types as planning aids:

| Type | Purpose | Direction |
|---|---|---|
| A | Story, opening, reveal or payoff | Image-led; give expression, action and atmosphere adequate space. |
| B | Story plus teaching/application | Balance the actual beats and teaching load. This is the normal mixed-page approach. |
| C | Maths, practice or revision | Clear teaching groups, compact hierarchy, precise diagrams and minimal ornament. |

These are not fixed templates. Two pages of the same type may need different layouts. Do not apply the three-column Page 16 comparison to the rest of the book. Do not use equal rectangles simply because automation makes them convenient.

Story panels may use wide or tall rectangles, insets, restrained diagonal cuts or other shapes when they improve pacing. Dense maths normally needs stable rectangular reading spaces. Keep reading order obvious without temporary panel numbers. Preserve a story interruption even when its surrounding maths is produced together.

Reserve space for the real text and the actual visual requirements. A placeholder rectangle does not prove that faces, a route card, scale ticks or fifteen trays will remain readable. A balloon overlapping artwork occupies visible space; it cannot also be counted as unobstructed space for an important object.

Recover wasted floor, ceiling, margins and decoration before reducing important subjects or type. Preserve necessary space for establishing views, counting demonstrations and gestures. Breathing room is useful; large accidental blank strips beside crowded text are not.

Reusable text styles, colours, header/footer components, diagrams and balloon construction can speed assembly. Do not make every page share identical panel positions, sizes or image counts.

## 5. Page dimensions, margins and capacity

Work in physical dimensions and points. Increasing raster resolution does not create more physical space for words.

For conservative planning, the earlier capacity brief proposed **18 pt outside margins**, a further **24 pt top allowance**, an **828 × 588 pt main composition envelope**, **12-16 pt gutters** and about **8 pt internal text padding**. Treat these as planning guides, not a printer-approved safe area or a mandatory frame grid. Balloon curves and tails need their own allowances. Current proofs use some different allocations.

Keep the running header compact, roughly no more than 5% of page height. Final chapter pages should identify chapter number, chapter name, section and page number from the source. The abbreviated headers on typography proofs do not remove that production requirement. Keep important content clear of trim and binding; use the printer's final safe-area requirements before release.

Measure actual fonts, bold runs, mathematical symbols and usable text widths. Include headings, paragraph gaps, equation rows, table padding and diagrams. A five-row pattern needs five rows even if its word count is low. A table row is sized by its most demanding cell. Do not turn worked steps into a run-on paragraph to save height.

Use this fit sequence:

1. Allocate meaningful artwork and diagrams, then measure exact text.
2. Improve the composition within the approved page: remove waste, rebalance panels, improve line breaks and use available internal space.
3. Try the normal 14-point maths setting.
4. For a genuinely dense maths page, try 13 points with 17-point leading. Keep a consistent maths body size across that page and mark the exception for batch review.
5. If the page still feels crowded or its essential content is hard to read, propose a layout revision or coherent split. Never automatically reduce maths body below 13 points.

There is no universal words-per-page quota. Original Page 16 contains about 485 printable words plus visual requirements. Both unsplit tests fit technically: 14/18 was crowded; 13/17 had more room. The split at 14 points remains the calmer reading option. A zero-overset result proves visibility, not reading comfort.

Do not permanently split, recombine or renumber without the relevant page-boundary decision. Keep the temporary 16A/16B output IDs mapped to the original V04 panel IDs. After approved repagination, update page headers, panel IDs and every dependent cross-reference together using an old-to-new map. Never apply a blind global “add one.”

## 6. Typography and font checks

Use the families and sizes in Section 2. “Source Serif Sans 3” is not the intended font name: the maths family is **Source Sans 3**. Use real Regular and Semibold faces, not synthetic bold or silent substitutes.

- Keep main headings distinct but economical. The tested Page 14 section heading is 26 pt; that is a local hierarchy choice, not a command to make every panel title 26 pt.
- Use a consistent maths body size on each page. Larger display equations or diagram labels may be justified by their structure and final readability; do not reduce all maths to speech size.
- Preserve bold emphasis from the source. Keep equations and their operators together where possible; check for misleading wraps, orphaned signs, isolated headings and broken fractions.
- Make exponents, radicals, decimal points, minus signs, multiplication signs and units unambiguous. Do not replace mathematical minus signs with hyphens or lose superscript meaning during conversion.
- Do not use horizontal squeezing, aggressive negative tracking, illegible line spacing or hidden overflow to make content fit.
- Test at actual print size and at a normal full-page view on the intended tablet/laptop. Screen zoom alone is not a physical-size measurement. For print proofs use Actual size/100%, with Fit/Shrink disabled; use A3 for the full 12 × 9 page or an actual-size selection/tile on A4.

Load the exact four font files into the renderer: SourceSerif4-Regular.ttf, SourceSerif4-Semibold.ttf, SourceSans3-Regular.ttf and SourceSans3-Semibold.ttf. Keep their licences with the source project. Use supplied files when available; do not assume the receiving environment already has them. Register/embed the real fonts directly rather than relying on a machine's default family mapping.

Render a small sample using the approved sizes, bold runs and required symbols, including −, ×, ÷, →, powers and roots. Verify actual font faces, glyphs and embedding in the exported PDF. If a fallback is needed for a missing symbol, name it, preserve the surrounding type style and verify its appearance. Do not silently substitute the whole font family.

Measure and render using the same font files and layout engine. Font availability does not prove that a complete page fits. Recheck each page's final text frames, line breaks and actual PDF output.

## 7. Speech balloons and narration

Build final balloons and lettering as editable assembly elements wherever possible. The story artwork must provide appropriate low-detail space in advance. A blank baked-in balloon is only an explicitly assigned intermediate; exact dialogue is always inserted from the manuscript.

- Use a softly curved, organic silhouette with a clean tail, a white or warm-ivory fill and a thin deep-indigo outline. A restrained gold accent is optional. Avoid sharp rectangular dialogue cards, ornate frames and generic software bubbles.
- Place speech over the illustrated scene in a naturally suitable area. Do not manufacture a blank page strip beside a cropped portrait to house the balloon.
- Keep the artwork continuous beneath the overlay. Moving or removing a balloon should reveal artwork, not a hole. Do not cut away illustration simply because a balloon covers it.
- Fit the balloon to the exact final text, with balanced line lengths and comfortable padding. Reduce its dimensions when smaller lettering permits it; do not leave the same oversized shape around smaller text.
- Make the tail identify the correct speaker. Aim towards the mouth but stop clear of face and hair. Avoid crossing hands, labels, mathematical objects or another speaker.
- Keep faces, gestures, route cards, numbers and important props visible. Check placement after the illustration is fitted to the page.
- Narration is visually distinct from speech and has no speech tail. It may sit in a dedicated reading area or a suitable overlay according to the page composition.
- Preserve printed speaker prefixes if they are classified as printable in the source. Do not silently remove names for comic-book convention.

The early Page 15 proof used portraits beside white speech areas, which made the pictures seem cropped. Later proofs used continuous wide scenes with vector balloons. Background extension is an artwork edit that requires review; it is not a pixel-preserving resize. The latest 12-point speech trial reduced balloon bounds by about 27% relative to the 14-point trial. That percentage is a test result, not a rule for every balloon.

## 8. Make maths pages attractive through teaching design

Plan all maths components for one page together so their teaching hierarchy and styles agree. Build and save each original maths panel as an independently addressable component, with its own panel ID, exact text, diagrams and audit result. One coordinated production job may produce several maths panels in one run; this must not flatten them into one inseparable page image. Place them around story panels in the manuscript's original reading order.

Use warm-ivory reading surfaces, deep-indigo text, pale blue or pale sand for useful groups, and thin muted-gold dividers. Establish hierarchy through subheads, alignment, spacing, consistent worked steps and purposeful colour. Pair corresponding before/after states. Align pattern equations and table columns. Keep questions and their working visually connected.

Do not put streets, scenery, reflections, textured illustrations or large decorative motifs behind ordinary maths. Do not give every small maths panel a huge title and its own ornamental poster frame. Do not interpret “clean” as a pile of identical dull boxes: the teaching structure should determine the visual arrangement.

Build exact number lines, grids, tables, arrows and counting arrangements with deterministic vector/live elements. Keep maths text editable; retain equation source for any scalable equation artwork. Do not rely on a generative image model to spell final labels, calculate answers or draw an exact grid.

Verify calculations and pictures together. Check equal scale intervals, zero alignment, signs, arrow destinations, direction, group membership, row/column counts, highlighted factors and units. Correct arithmetic beside a misleading diagram is not a pass.

Keep distinct examples distinct. Do not borrow numbers from the neighbouring worked example to simplify a visual. Keep unsolved checks unsolved unless their answer is supplied at that point in the source. Do not add an answer because the model can calculate it.

An intentional faulty control or wrong student attempt can be the teaching subject. Preserve that state and its explanation. In particular, do not prematurely turn Page 18's intended **−2, −2, +2, −2** controls into the later corrected four **−2** controls.

## 9. Select location images before writing prompts

Resolve each panel's literal named reference first. Inspect the actual image and the required character sheets; a filename mentioned in text is not an attachment.

1. Record source page/panel ID, literal manuscript filename, selected actual file and version/checksum.
2. Read its SOURCE-USE, SOURCE-ACCEPTANCE, LOCATION REFERENCE EXCEPTION and shared-assignment notes.
3. If several locations are named, use the **first named image as primary architecture/camera reference**, unless a SOURCE-USE note explicitly says otherwise. Give additional references specific roles such as repair state, lighting or neighbouring context.
4. Select the version that matches the panel's stage and required view. The newest or most “corrected” image is not automatically the right story state.
5. Attach those actual files. Do not ask the image model to choose from a folder, attach conflicting states without roles or combine unrelated geography.
6. Record why the selected version is suitable and which source limitations are accepted.

Preserve literal spellings, including **NAYA**, **ANTERN**, **ADJASCENT**, **THRESHHOLD** and supplied double extensions such as **.png.png**. If the asset bank uses a known alternate name, record an explicit mapping. Do not silently rename files, strip suffixes or substitute a similar filename. A missing/ambiguous source leaves the affected job awaiting resolution while independent ready jobs continue.

Use a clearly identified corrected variant where appropriate. An older repair state or an allowed inaccurate background count does not make the base reference unusable. Do not require every background asset to be corrected before production starts.

**Example:** Page 18 uses the faulty-controls state when required. The later corrected-controls scene uses its corrected state. The current bank contains both variants with their literal double-extension filenames. Never “improve” the earlier teaching moment by substituting the later state.

## 10. Location exceptions: what to pass and what to verify

Location images establish identity, architecture, spatial arrangement, materials, palette and continuity. The current panel controls action, time of day, readable labels, maths and repair stage. A reference is not mathematical proof.

For a covered minor mismatch, record **PASS WITH LOCATION EXCEPTION** and continue. Do not zoom into tiny scenery, recount hidden objects, repeatedly regenerate a source image or demand renewed approval for an already accepted limitation.

Readable teaching content and meaningful story states remain accurate. A wrong visible answer, a misleading featured scale or a plainly incorrect counting demonstration requires correction/review. A detail too small to read is not automatically wrong. Do not claim a tiny hidden count was verified.

Carry the applicable exception into each standalone panel brief and audit, including inherited shared visuals. Do not paste the register onto the finished page. Apply the current V04 scope; older notes demanding blanket recounts do not override it.

### Current V04 exception register

- **LOC-EX-01 | Mirror area.** `MIRROR SQUARE REPAIR AREA BEFORE 81 TILES V01.png` and mirror variants: accept approximate raster seams/counts. Do not correct or reject the location because it lacks exactly 81 visible tiles. Before repair: empty frame, loose tiles outside. After repair: completed square with one continuous full-moon reflection. Printed 81 and 9 × 9, and an explicit countable teaching demonstration, remain correct.
- **LOC-EX-02 | Cube bay and handle.** `CUBE LANTERN REPAIR BAY AND STREET LIGHT HANDLE.png`: accept approximate source lantern counts, cube subdivisions, wall-guide and old control/connector details. Preserve bay architecture and follow the panel's stage. Do not count shelf ornaments as repair lanterns. Featured 64 and 4 × 4 × 4 teaching remains exact; a completed cube must read as solid, not a flat illuminated grid.
- **LOC-EX-03 | Reverse street.** `LANTERN-STREET-REVERSE-VIEW-FROM-CUBE-LANTERN-BAY.png`: preserve reverse viewpoint and station order. Do not recount distant mirrors, shutters, ticks or cube units. Follow the panel's foreground state and lighting. The bank also contains a spaced-name variant; use the resolved assignment.
- **LOC-EX-04 | Repaired street.** `LANTERN STREET REPAIRED STATE.png`: do not audit distant counts. Communicate the required success state: lit arches, continuous moonline, completed mirror, solid-looking cube, lowered handle and five white repair lamps when specified. The mirror-count waiver applies here.
- **LOC-EX-05 | Unrepaired street.** `LANTERN STREET UN REPAIRED STATE.png`: distant station details are representative. When featured, the five street-board repair lamps are dark and main arches/moonline are unlit. Ambient wall lamps or reflected highlights do not signify completed repairs.
- **LOC-EX-06 | Lift shaft.** `LANTERN LIF SHAFT & ADJASCENT NUMBER LINE.png` and `LANTERN LIF SHAFT & ADJASCENT NUMBER LINE-AT-MINUS-8.png.png`: source scale alignment may be approximate. In readable teaching views, 0 aligns with the street/car floor, −8 with the storage floor, and integer intervals are equal. Show one car at the panel's stated level; the storage landing is fixed.
- **LOC-EX-07 | Lift close-up.** `LANTERN LIFT STREET LEVEL 0 CLOSE UP.png` and its `-FAULTY-CONTROLS.png.png` / `-CORRECTED-CONTROLS.png.png` variants: preserve cabin/console design. The panel controls gate, cards, four rollers, values and LIFT-lamp state. Featured readable controls must match; minor background details can pass.
- **LOC-EX-08 | Timing drums and kits.** `ANTERN TIMING DRUM REPAIR KIT WORK AREA.png.png` and RESET, REPAIRED, EMPTY-KITS and FILLED-KITS close-ups: source holes, pegs and tiny loose pieces are illustrative. Featured beat labels and kit maths must match. Completed kits should clearly read as 15 equal trays; do not pixel-count partly hidden tiny clips/rings when grouping is clear. Do not introduce a new task from an old source callout.
- **LOC-EX-09 | Shutters.** `TWELVE SUPPLY SHUTTER.png`: an extra/ambiguous source bay or partial crop is acceptable. When the complete labelled set is featured, use **2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 25, 100**. Preserve the relevant crate/shutter labels, routing details and seals.
- **LOC-EX-10 | Entry Court and street board.** `ENTRY COURT.png` with the unrepaired-street entrance board: the court wall map is not the five-lamp repair board. Keep the Moon Bell stand empty. The featured street board has **LIFT, RHYTHM, SHUTTERS, MIRROR, CUBE** in that order, with panel-specific states.
- **LOC-EX-11 | Old Blue Gate.** `OLD BLUE GATE.png`: the overhead ring is an ornament, not the missing Moon Bell. Apply the required hatch, crowd and lighting state. Earlier views are dark; success views may show light through the gate.
- **LOC-EX-12 | Food Street.** `FOOD STREET THRESHHOLD FROM LANTERN STREET.png`: use architecture/counters even if the source is open and orderly. The panel controls shutters and displaced bowls, jars, food and cart. Do not demand a new location merely to change that stage.
- **LOC-EX-13 | Invitations.** `AHANA INVITATION DISCOVERY.png`, `VIHAAN INVITATION DISCOVERY.png`, `NAYA INVITATION DISCOVERY.png`: use their settings; the panel controls late-afternoon-before-moonrise lighting, character, invitation and silver trail. The character is Navya despite the literal NAYA filename.
- **LOC-EX-14 | Mumbai lane.** `THREE SILVER TRAIL MUMBAI LANE.png`: use lane layout and three-way convergence. Apply the panel's early-evening lighting and children. Do not add a visible moon simply because the reference contains one.

## 11. Maintain story-stage and character continuity

Use the actual supplied character sheets for face, age, hair, outfit, proportions and accessories. Do not reconstruct appearance from an old prose memory when the sheet is available. Preserve the approved painterly, semi-realistic style; avoid changing the children into an anime style or exaggerating their eyes. Keep Tez's markings and any story-specific changes tied to the panel.

Show one readable static moment. Specify meaningful hand use, gaze, pointing target and object contact. Do not depict incompatible moments with extra hands, duplicated characters or multiple lift cars. Preserve crate seals and required cards/props. Do not introduce religious motifs or crescent moons. Show a complete full moon or coherent full-moon reflection only where required by the scene.

Stage reminders from V04:

- Before mirror repair: empty frame, loose tiles outside, MIRROR lamp dark. After local repair: completed mirror and local lamp white, while the main street can still be unlit.
- Before cube construction: the manuscript's narrow towers and wall guide. Do not import a completed cube into the earlier stage.
- Page 59 Panel 02 demonstrates the 4 × 4 bottom layer; Panel 03 shows the completed solid-looking cube with CUBE lamp still dark. Do not assume cube completion instantly switches every light on.
- From Page 59 Panel 04 through the pre-switch scenes: five repair lamps white, handle raised, main arches/moonline unlit.
- Page 61: flat track gap and separate joining plate, then fitted plate, then lowered handle. Do not restore an obsolete cylindrical plug/socket in this action.
- Page 62 success: lowered handle, five white repair lamps, lit arches and continuous moonline.
- Timing stages may show blue on/gold off, both off for reset, or both on after repair. Use the panel; never freeze one state across the sequence.

Where a close-up explicitly teaches grouping, request the exact arrangement, such as 15 trays in 3 × 5, each with 3 clips and 5 rings, and the correct bulk-bin state. For covered distant/occluded scenic detail, apply the location exception instead of a microscopic count.

## 12. Choose the smallest appropriate artwork operation

| Operation | Use it when | Requirement |
|---|---|---|
| Use as is | Approved finished artwork already meets the panel | Reuse the actual asset. |
| Crop or proportional resize | Content is correct; framing/placement needs adjustment | Preserve required evidence and aspect ratio. Recheck effective resolution. |
| Minimal edit | A local detail needs correction or a background needs extension | Specify only the change; inspect the result for unwanted changes. |
| New generation | Required action, state, identity or viewpoint is absent | Use the resolved panel brief and actual references. |

A location reference alone is not automatically a finished story panel. Generate each needed story/character scene independently from its resolved panel brief. Reuse an already approved finished panel when it genuinely supplies that same scene.

Do not regenerate correct character artwork for a font, balloon, label or page-layout adjustment. Do not stretch artwork to fit a frame. Crop only inside the planned safe area; never cut off needed hands, a counted group, a scale endpoint or a full-moon reflection. If a wider scene is necessary, an extension is an edit with continuity checks, not a guarantee of unchanged pixels.

## 13. Write short, self-contained image prompts

Keep this handbook with the controller. Send the image model only the relevant resolved panel instructions and actual attachments.

State one task, final aspect ratio, camera, static action, relevant identity/location preservation, critical objects/states and reserved lettering space. Choose these before prompting. Do not offer multiple alternative poses or assume the model understands “the repair bay” without seeing or locating it.

Describe objects spatially: for example, “the glowing stack below the label on the right.” Use the reference's marked region where helpful. If a target cannot be identified confidently, use an annotated selection. Do not claim an object is marked when no marking exists.

For a targeted edit, list only changes and finish with **“Preserve everything else exactly.”** Treat this as a request to verify, not proof of pixel-perfect preservation. Name the character's own right/left hand and exact target when handedness matters. Put teaching-critical requirements early.

Do not include internal routing, exception prose, manuscript history, future export steps or unresolved placeholders in a generation prompt. Do not ask the model to typeset final dialogue or exact maths. Reserve blank surfaces for assembly where that responsibility is explicitly assigned; missing physical teaching objects cannot be excused as later lettering.

## 14. Page identity, borders and editable assembly

Keep page furniture premium and restrained: indigo, warm ivory and muted gold. Story/mixed pages may use controlled variation from the earlier named border family: Moon Bell Loop, Lantern Brackets, Silver Moonline, Old Blue Gate Inlay, Pavilion Hem, Mirror Tile Corners, Cube Lantern Lattice and Star Enamel Corners. These are design directions, not evidence that eight finished border assets are installed.

Maths/practice pages need no full ornamental border. A small corner accent may be used only when it leaves teaching space intact. Avoid heavy frames, repeated decorative stars, large title strips and random styling changes.

Assemble the page from the saved panel packages using precise layout tools. Keep artwork, maths text, equations/diagrams, dialogue, captions, balloons, in-world labels and page furniture separately manageable in the source project. The assembly step places approved artwork and exact content; it does not redraw scenes or rewrite the manuscript.

Use the page plan's coordinates, panel clipping paths, crop transforms and layer order. Artwork sits below its text/balloon overlays. Preserve text size when changing a panel frame: reflow and remeasure text instead of scaling a finished panel containing lettering. Preserve image aspect ratio; never stretch a panel to occupy its allotted space.

Align labels with their actual plaques, bins, shutters or cards, including perspective where needed. Do not leave labels floating beside the wrong object. Remove reference titles, callouts, guide arrows, red markings and temporary production strips. Retain genuine in-world labels required by the manuscript.

For manual previews, an external removable strip may identify the panel. Automated production should track identity through filenames and the manifest. Never bake production IDs into final learner-facing artwork.

## 15. Resolution and print export

Use **at least 300 effective ppi at final placed size** as the working target for continuous-tone story artwork. Record any lower-resolution asset for review; do not claim it meets the target because an export setting says 300. The printer's agreed specification controls final acceptance.

| Raster use | Required pixels at 300 ppi |
|---|---|
| Full 12 × 9-inch page | **3600 × 2700 px**, excluding bleed |
| 6 × 4-inch image | **1800 × 1200 px** |
| 4 × 3-inch image | **1200 × 900 px** |
| Existing 1800 × 1350 full-page preview | **150 ppi** at 12 × 9 inches; review only |

Calculate each axis as pixels divided by placed inches; record effective resolution from the actual image transform after scaling and cropping. Do not divide the entire image's pixels by a smaller crop-frame width and falsely claim higher resolution. A 1024-pixel image placed 6 inches wide is about 171 ppi. Enlarging it or changing its DPI metadata does not recover source detail. Check any upscaled artwork for real visual quality.

Keep text, curves, number lines and diagrams vector/live wherever possible. A PDF does not have one universal page DPI: its raster images have individual effective resolutions, while text/vector elements scale. Rasterising a whole page unnecessarily reduces those advantages. A high-resolution PNG cannot substitute for an editable master.

Current proofs use RGB and zero bleed. Before commercial printing, confirm trim, binding safety, bleed, printer's colour profile, required PDF standard, marks and image requirements. Do not invent a generic CMYK profile or assume zero bleed suits edge-to-edge printing. Extend backgrounds into the required bleed without enlarging or moving essential text towards trim.

Export a vector-preserving PDF at the exact physical page dimensions using the available rendering tools. Confirm page order, individual pages versus spreads, embedded fonts, image compression/downsampling, colour handling and bleed boxes. Keep review annotations and production slugs out of the final output.

If the printer requires PDF/X-4, a specific output intent or other conformance, use a supported conversion/preflight process and verify the result. Do not relabel an ordinary PDF as PDF/X or claim a renderer supports a print standard without checking. Until those requirements are resolved, deliver a clearly identified review PDF and retain the source for the final export.

Reopen and inspect the exported PDF. Check dimensions, crop/trim/bleed boxes, font embedding, image quality, transparency, symbols and actual visible text. Do not assume a correct source project or a successful render operation guarantees an accurate export.

## 16. Create each panel individually, then assemble

The page plan comes first so each panel is designed at the correct size. Actual page assembly follows panel creation and checking. The executing model performs these responsibilities in sequence; separate named roles do not require separate agents.

### 16.1 Plan the page and its panel contracts

Read the source, choose the batch and resolve all page/panel IDs, shared assignments and references. Create the page composition and reserve real text and diagram space before creating expensive artwork. For each panel, record its final frame in points, aspect ratio, target image pixels, exact printable text, diagram specification, character/location references, scene state, exceptions and acceptance checks.

### 16.2 Create and save one panel package per original panel ID

For a story panel, generate or reuse only that panel's illustration, using its complete brief and actual references. For a maths panel, construct its exact text and diagrams with precise text/vector elements. Audit the result, apply the bounded correction policy below, then save the best result and its status before proceeding. Panels may be created in a convenient dependency order; final reading order remains unchanged.

| Package component | Required content |
|---|---|
| Panel identity | Original manuscript panel ID, source version and output-page mapping. |
| Artwork or diagram source | Original story-image file, or editable maths/vector source; preserve original dimensions and asset revision. |
| Exact text | Printable text and emphasis as structured data, with speaker and text role; keep it separate from the raster illustration. |
| Placement data | Frame dimensions, crop/scale, local text/diagram bounds, balloon/tail positions and reserved areas. |
| Audit record | Actual reference files, exception IDs, checks, status, correction count and unresolved items. |
| Panel review | A preview with text/overlays at the planned proportions, used for review; it does not replace the editable components. |

Illustrative filenames are `CH01-P014-PN01-art-v001.png`, `CH01-P014-PN01-panel.json` and `CH01-P014-PN01-review.png`. Use an SVG/vector source for precise diagrams where appropriate. Retain the actual source IDs; these filename examples do not allocate content to a panel.

Final lettering is rendered from the text data. If a panel review already shows dialogue or maths, assemble the original components, not that flattened preview; otherwise text may be duplicated or lose quality. Location references and approved finished panels are different assets. A reference without the required character/action is not a finished story panel.

### 16.3 Audit before accepting the panel into assembly

Compare the individual panel with the original manuscript and its actual references. Check story state, identity, meaningful gestures, exact teaching elements, crop safety and readability at the planned size. Retain the selected asset's filename/checksum so the assembler cannot accidentally use an earlier version.

Use V04's statuses:

| Status | Meaning and action |
|---|---|
| PASS | Intended content and state communicate correctly; no meaningful unresolved issue. Eligible for assembly. |
| PASS WITH LOCATION EXCEPTION | A recorded, scoped reference/background limitation is acceptable. Eligible for assembly; retain the exception in the audit. |
| REVIEW LATER | A meaningful story, identity or readable-teaching issue remains. Keep the better asset and continue independent work. It is not final production approval. |
| TECHNICAL RETRY | No usable asset was produced, for example missing, blank or corrupt output. Diagnose the technical cause. |

For a meaningful generated-panel error, make **at most one automatic correction/edit/regeneration attempt after the initial result**. If it remains wrong, retain the better result, mark REVIEW LATER and continue. Do not use endless edit-then-regenerate cycles or let one visual mismatch halt the chapter.

For this handoff, “approved panel” means an asset eligible for assembly under these statuses or explicitly accepted by the user. Do not claim the user reviewed every panel, and do not ask for separate manual approval after every panel. Present the batch for user review.

### 16.4 Assemble saved panels into the page

Load the page plan and the exact eligible asset revisions. Place panels in their planned frames and original reading order. Draw exact maths, dialogue, narration, balloons, in-world labels and page furniture as separate source elements. Apply the planned crops and clipping masks. Do not ask the image model to redraw the approved panels as a complete page.

A REVIEW LATER panel may appear in a clearly identified review proof, accompanied by its issue record. Do not silently omit it, invent a replacement or label that page final. Independent ready pages continue.

Judge the assembled page as well as the separate panels. Recheck labels, balloon collisions, line breaks, final image sizes, effective ppi and reading rhythm. An individually attractive panel can become unreadable when placed too small.

Repair typography and layout in assembly; repair precise diagrams deterministically; edit a local art fault locally; regenerate only when the underlying scene is wrong. Changing a font or moving a balloon must not trigger a fresh generation of correct character artwork. A new crop or changed frame requires a fit/resolution check, not automatic regeneration.

### 16.5 Run the page audit and deliver the batch

Reopen/render the exported files and complete Section 17's audit. Save a readable full-page preview, the vector-preserving PDF, editable source and issue report. Present five pages by default, no more than ten, then wait for batch feedback before starting the next batch.

An unresolved meaningful error prevents the affected page being called final/print-ready even though other work continues. Setup failures such as unavailable fonts require a technical fix, not repeated image-generation calls.

### 16.6 Execution requirements for any model

1. **Inspect the working inputs.** Confirm the supplied manuscript, location ZIP and character ZIP; preserve the originals. Extract images into separate asset folders and resolve literal filenames. Read DOCX text, runs and tables, including non-printable directions. Do not use textbook PDFs or OCR as substitute manuscript copy.
2. **Check available capabilities.** Verify access to the supplied files, image inspection, image generation/editing, precise layout/vector tools, fonts, PDF export and rendered-page inspection. Use the available image tool for artwork creation/editing. Do not assume a paid API, secret key or separate application is configured. If a required capability is unavailable, state exactly which production step cannot be completed, continue useful independent work and provide a clearly labelled handoff for that step. Do not present prompts, placeholders, planned work or inaccessible reference filenames as finished assets. A model-neutral brief does not give a text-only environment image or export capabilities.
3. **Use a reproducible assembly method.** Choose tools actually available in the receiving environment that support precise placement, editable text, vector diagrams, font embedding and PDF output. This may be a script-driven renderer or another controllable layout system; no particular language or application is required. Keep the layout source, exact text data, font files/licences, asset paths and page geometry together so the same page can be rebuilt. Every method must meet the same physical-size, font, editability and export checks.
4. **Separate content from layout implementation.** Keep page contracts and a panel manifest in structured files. Store original IDs, ordered panel placements, approved asset revisions, text styles, source hashes and audit status. Treat IDs such as 16A/16B as identifiers, not integer-only filenames. Do not use one fixed geometry for all pages.
5. **Use physical units consistently.** The trim page is 864 × 648 points; 72 points equal one inch. Define a single coordinate origin and convert deliberately between image pixels, SVG coordinates and PDF points. For a 300-ppi page preview, render the PDF at 300/72 scale to obtain 3600 × 2700 pixels, excluding bleed. Do not assume one image pixel equals one point.
6. **Prove assembly with a layout-only render.** Measure the selected batch's real text and diagram space before generation. A temporary placeholder render can test fit, but must be labelled as a layout proof. It does not count as completed artwork or final visual approval. Then produce individual panels and assemble the actual assets.
7. **Save and resume.** Write each accepted panel and audit to disk, then reuse it on resume. Cache by source, panel brief, asset revision and settings. When inputs change, rebuild only affected panels/pages. Do not regenerate a completed batch because the session restarted or one caption moved.
8. **Return completed results.** When the required tools are available and the batch is authorised, carry out the assembly, inspect its outputs and deliver them. Include the source project and a short README so another run can reproduce the pages. A plan, prompt or unexecuted script is not a completed page. Do not start a new batch or change manuscript content/pagination without the applicable user decision.

## 17. Audit what was actually produced

Compare with the original manuscript, not just the Director's brief. A brief can omit something, and an audit against that brief alone would repeat the omission.

- **Source coverage:** every required passage, table cell, equation and visible label; no accidental additions, omissions or duplication; correct page/panel/speaker allocation.
- **Maths:** correct signs, answers, powers, roots, scales, arrows, groupings and highlights; distinct examples remain distinct; intentional faulty states remain intentional.
- **Story:** correct identity, location, meaningful gesture, prop, card, gate, repair stage, lamp state and continuity.
- **Layout:** clear reading order, sufficient image area, comfortable type, padding and line spacing; no balloon collisions, clipping or hidden overflow.
- **Technical:** correct physical page size, actual fonts/sizes, missing glyphs, image links, placed-image ppi, export settings and embedded resources.
- **Output:** inspect the PDF/PNG, not merely construction records. Text can exist in a document while remaining overset and invisible.

Inspect essential teaching details closely and then judge the whole page at normal reading size. Do not apply that close inspection to manufacture a failure from exempt tiny scenery. Record what was checked, what is unverified and why an exception applies. Preserve intended repetitions when comparing text; whitespace-normalised extraction alone cannot validate emphasis, tables or diagrams.

## 18. Files, batches and reproducibility

Work in the existing ChandRush production project with isolated versioned run folders. Preserve source files and successful earlier runs. Do not require deletion of the old workflow merely to prevent filename clashes.

Keep a manifest keyed by original panel ID. Record manuscript version/checksum, output page mapping, literal reference and selected version, prompt, artwork revision, dimensions, crop, text styles, effective ppi, exception IDs, audit result and unresolved work. Link approved results to their exact asset, not upload order or a thumbnail guess.

Save progress per panel/page so a run resumes without regenerating passed work. The default batch is five pages and the maximum is ten. Give the user a clear review package and a short next action. The intended workflow should not require manual renaming, copying assets or repeating setup for every page.

When supplying a ZIP, put the launcher/readme directly at ZIP root with **no extra enclosing folder**. Necessary `scripts`, `data`, fonts and other subfolders must remain intact. Never instruct the user to flatten all subfolders.

Deliver an editable source project containing the layout source and any assembly code, structured manuscript text, page contracts, panel manifest, original panel artwork, editable/vector diagrams, font files/licences and a short README. Also deliver individual page PDFs, full-page PNG review images, a batch PDF and machine-readable audits. Build the consolidated chapter PDF from the approved pages when the chapter is complete. Preserve page order and temporary page mappings.

Editable means that text, layout or diagrams can be changed and rerendered without repainting approved artwork. A flattened PNG or PDF alone is not that source project. Clearly distinguish review files from final files and retain the source equations/diagrams.

Keep API keys out of uploads and reports. Report only presence/status, never secret values. A tool-availability check is not a successful page render; a key's presence is not authentication or billing validation. Track actual calls, retries and cost instead of assuming the old illustrative “$0.08 per image” estimate.

## 19. Lessons to carry into every new page

| Test or problem | Lasting instruction |
|---|---|
| Early Page 16 overflow at 18 pt | Measure real text, diagrams and frames; do not infer fit from word count. |
| 16A/16B and unsplit 13/14-point tests | Separate technical fit from comfortable reading and from approval to change pagination. |
| Large balloons despite smaller type | Refit the balloon shape and padding; changing the font alone is insufficient. |
| Page 15 speech beside cropped-looking portraits | Maintain continuous scene artwork beneath editable balloon overlays. |
| Pages 38/40: floor, labels and gestures | Reframe nonessential scenery; keep labels on the right objects and fingers/tails aimed correctly. |
| Page 47: standalone versus placed size | Judge the assembled page, preserve distinct maths examples and apply local fixes rather than redesigning everything. |
| Page 29: kit counts and printed production prose | Separate visible teaching requirements from non-printable directions; use reliable construction for featured grouping. |
| Lift scales | A wrong readable zero/floor relationship changes the teaching; source-reference acceptance does not excuse it in a featured diagram. |
| Repaired-street mirror and cube | Accept the mirror-count waiver in scenery; keep the cube solid-looking and the required overall repair state clear. |
| Font substitutions and proof exports | Check the actual font files used by the renderer and inspect the exported PDF; a successful render operation is insufficient. |
| Individually correct panels in a crowded page | Audit again after assembly; panel approval does not guarantee page readability. |

## 20. Required handoff from a page-creation model

Before creation, produce a short page contract containing: source version; original page/panel IDs; exact printable fields; resolved visual/diagram instructions; literal references and selected variants; applicable exception IDs; layout and reading order; dimensions/crops; fonts/sizes/leading; reserved balloon areas; asset strategy; critical acceptance checks; and required outputs.

After creation, return the actual review files plus a concise report: what was produced, which passages/panels were checked, fonts and dimensions used, fit and resolution results, applicable exceptions, remaining issues, evidence level and next action. Distinguish **planned**, **rendered**, **panel audited**, **assembled-page audited**, **user approved** and **print-ready** accurately. Do not report a stage as complete merely because its script or plan exists.

Final self-check: Have I preserved the source, selected the right state reference, designed this specific page, kept the maths exact and readable, respected the scoped exceptions, preserved approved artwork, inspected the actual export and reported unresolved work honestly?

## Sources and precedence record

Primary production source: **CH 01 PANELIZED MANUSCRIPT V04.docx**, including its execution rules and LOC-EX-01 to LOC-EX-14. Inspected source SHA-256: `6de4c6ff255204e0a2f5bb3fecced3bb454ebd68cbcedf72c6ad863b755df2e8`.

Consolidation inputs: **CHANDRUSH_PAGE_PRODUCTION_RULE_BOOK_V01.docx**; **CHANDRUSH_TEST_PAGE_CREATION_RULEBOOK_V02.docx**; **CHANDRUSH-PAGE-CREATION-RULE-BOOK-UPDATED.md**; **CH01-Location-Exception-Handover-V01.md**; **CH01-Manuscript-Page-Capacity-Brief-V01.md**; the earlier layout-proof record; and the September 28 Source-font, balloon and full-Page-16 comparisons. Older font sizes, source versions, stage assumptions and correction loops are superseded as stated above. This is a consolidated operating guide, not a claim that every earlier chat transcript was exhaustively retrieved.

Use the current printer's specification for the final export. This guide instructs the executing model to create panels and assemble pages using the tools available to it. Revising this guide does not itself modify the manuscript, implement or run the assembler, or approve pending comparison choices.
