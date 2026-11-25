# PANEL GUIDE: stage 2, final panel art (characters in their scenes)

Stage 2 turns each planned panel into one finished, letter-free illustration: the approved **background plate** plus the **characters, action and props** of that visual beat. Bubbles, captions, maths and labels are **never painted**. The page builder adds them as HTML. Read `Tasks/LESSONS.md`, section *Panel art*, first.

Tool: `python3 Tasks/pipeline/imggen.py --ws FInalChangesTask/<CHxx> ...` (Batch API only; `--help` for commands).

## 1. Workspace per chapter
```
FInalChangesTask/<CHxx>/
  jobs.json             one item per art asset (see imggen.py SCHEMA)
  prompts/<ID>.md       ## PROMPT / ## CHECKS (6–12 items)
  out/<ID>.png          current image; out/history/ earlier attempts
  ACCEPTED-AT-CAP.md    accepted defects (call cap reached)
FInalChangesTask/library/   chapter-independent spot art (props, character vignettes) reused across pages
```
Item IDs:
- `P007-2` is page 7, panel 2.
- `V-TEZ-03` is a character vignette.
- `X-BELL-01` is a prop.

**Before making an item, check that it isn't a reuse.** A zoomed detail panel can be cut from an existing image with the `.panel.zoom` CSS, and `library/` may already hold the prop or vignette. Reuse is free.

## 2. References: which images, in which order (user, 2026-11-25)
Character references live in **`Tasks/CHANDRUSH CHARACTERS/`** (read-only). The newer sheets' filenames don't say who is on them, so always use the map in `pipeline/cast.json` (`python3 pipeline/cast.py list`). The order is fixed. Declare every image in the prompt as `Image n:`.
1. **Image 1 = the raw background plate** (`BagroundGenTask/out/plates/<ID>.png`, `ch02/out/plates/`, `ch03/out/plates/`). Never use `out/final/` (title band, callouts) or `archive/`.
2. **Image 2…n = the sheet of EVERY visible named character**, background figures included, in the order the prompt names them. The cast is Ahana, Vihaan, Navya, Tara, Tez, Kabir, Ira, Pip, Veer, Veer (clown disguise), the wooden clown, the wooden fair helpers, the wooden kitchen helpers and the supporting cast. Never describe a character instead of attaching their sheet.
3. **Then the height chart** (`size reference … + tara.png`) whenever 2+ characters share the panel, so relative heights stay right.
4. **Last, optional: `item:<previous panel>`** for continuity of a held prop, machine state or pose (the item then waits for that panel: wave 2).

Get the refs list and the matching `Image n` lines from the tool, never by hand:
```
python3 pipeline/cast.py refs BagroundGenTask/out/plates/M01-D01.png Ahana Tez Tara      # -> jobs.json "refs"
python3 pipeline/cast.py lines Ahana Tez Tara                                             # -> the Image 2..n prompt lines
```
Up to 10 images per call is fine. Identity is worth more than the extra input tokens.

## 3. Size and quality
- Match the size to the panel's box. The box comes from the page's art brief, which is fixed **before** any art (PAGE-DESIGN §5), so generate at the panel's own aspect and keep cropping small:

| Panel aspect (w/h) | Size |
|---|---|
| ≥ 1.8 (wide strip) | `1536x768` |
| 1.2 – 1.8 | `1536x1024` (hero panels ≥ half the page width), else `1024x768` |
| 0.8 – 1.2 | `1024x1024` |
| < 0.8 (tall) | `1024x1536` |

  The page crops with `object-fit: cover`. Keep the essential action inside the central 80%.
- Spot art (vignettes, props): `1024x1024`.
- **Quality `high`.** `xhigh` only with a `note` in jobs.json: dense exact counts the story depends on, or 4+ interacting characters. Never `max` without the user. Escalate to `xhigh` only after a `high` result failed on *rendering precision* (not a prompt problem), and say so in the report.

## 4. Prompt skeleton (`## PROMPT`)
```
Use case: ChandRush <chapter> comic panel <ID>, visual beat <beat id>: <one sentence: who does what, where>.
Asset: one <W:H> <landscape/portrait> graphic-novel panel illustration, no lettering of any kind.
Input images:
- Image 1: approved background plate <rec id> (<place>). Keep its architecture, materials, light and every object exactly; the camera may <stay identical | move closer to … | lower to child eye height>. Ignore nothing; it carries no labels.
- Image 2: character sheet of <Name>. Use ONLY for identity: face, hair, skin tone, body proportions, outfit and colours. Ignore the sheet's layout, turnaround poses, background, labels and any text.
- Image 3: ...
Characters and action (one character per numbered item):
1. <Name>: <screen position (screen-left third / centre / right), distance (foreground/midground), scale (head height ≈ x% of frame)>, <pose and gesture from the beat, which hand does what>, <gaze target>, <expression>. Holding: <prop or "nothing">.
2. ...
Props and states at this moment (exact): <numbered list; counts in digits and words; what is NOT there yet>.
Physical inscriptions (render exactly, nothing else): <only short real-world markings already in the plate or 1–3 characters the beat needs, e.g. "−2" on each plate> | none.
Reserved empty areas for lettering (keep calm, low-detail background; no face, hand or key prop inside): <upper-left ≈ 35% wide × 28% high> ; <upper-right …>.
Composition: <reading direction; speaker order left→right matches bubble order; nearest faces fully visible, not cut by frame edge>.
Style: match Image 1's finish exactly: premium semi-realistic painterly 2.5D graphic-novel illustration; characters drawn in the same finish as the ChandRush character sheets, grounded with crisp contact shadows, lit by the scene's lamps and moonlight.
Do not show: any speech bubble, caption, title, label, arrow, watermark or signature; extra characters; <wrong states, duplicate props, mirrored outfits>.
```
The skeleton is reused for spot art: "Asset: one square character vignette of <Name> <pose>, standing in a softly lit fragment of <place>, the figure fully inside the central 70%, the surroundings fading to <page colour> towards the edges". For props: "one square still-life illustration of <prop> on a plain flat <page colour> background, centred, nothing else".

## 5. Maths in art: avoid errors by design
- **Long or exact maths never goes in the image.** If a card, board, plaque or screen must show an equation or a number with more than 3 characters, paint it **blank** ("a blank cream card with a thin brass rim, face turned to camera, flat and uncreased"). The page builder lays the exact text over it with a CSS perspective transform.
- Short physical markings (`−2`, `+4`, `6`, `START`) may be painted. Write them as digits and words with true minus signs, as the background PROMPT-GUIDE §3 rules require.
- Countable groups the maths depends on (e.g. four plates of −2): use "exactly 4 (four) …, in one row, evenly spaced, each fully visible". The CHECKS list must count them.
- Never let the art contradict the page's maths. CHECKS must name every number/count on the page that the art shows.

## 6. CHECKS (`## CHECKS`, 6–12 items)
Always include:
- identity vs each sheet (face, hair, outfit colours);
- the number of characters;
- hands and limbs (5 fingers, no extra arms);
- left/right positions;
- held props and their owners;
- reserved areas empty;
- no lettering apart from the listed inscriptions;
- every count and inscription, exactly;
- continuity with the previous panel (same outfit details, same machine state).

## 7. First-time-right prompts (each image has only 3 calls)
Before marking an item ready, check every point:
1. **Stage it in the plate.** Look at the plate. Every object keeps its exact shape, position and orientation. Decide where each character must stand so the beat happens there. Say "screen-left/right" for sides and hands.
2. **Continuity.** Look at the previous and next panels' images (`out/`): same outfits, held props, machine states and positions.
3. **Identity.** Attach every visible character's sheet (cast.py) plus the height chart. Tara is always calm and wise, never animated. All humans have fair skin (CH01 author note).
4. **Words space.** Copy the page brief's text zones into "Reserved empty areas" with panel fractions. Those areas stay calm and low-detail: no face, hand or key prop inside.
5. **Counts and states.** Write "exactly N (word)" for counted things, and what is NOT there yet.
6. **No lettering** of any kind. Blank cards or plates where exact text will be overlaid.
7. **CHECKS (6–12)**, one per risk above.
8. Run `python3 pipeline/promptlint.py --ws FInalChangesTask/<CHxx> <IDs>` (free). `batch build` refuses any item that FAILs the lint.

## 8. Loop: one batch per wave for ALL requested pages
1. Write every prompt for every requested page first: all pages, all panels, all spot art. Lint them.
2. **One combined batch per wave:** `batch build <CHxx>-<run>-w1 --ready` takes every ready item of every page in one batch. Submit it, then run `batch wait` in the background.
   - Items that reference another item (`item:`) wait for wave 2.
   - Text-only (no-ref) spot art uses another endpoint, so it goes in its own small batch submitted at the same time.
   - Never submit one batch per page.
3. **QC** every image like an art director:
   - Read it.
   - `zoom` faces against the sheets, then hands, counts and inscriptions.
   - Confirm the reserved areas are empty and nothing is lettered.
   - Then record the verdict: `qc <ID> pass --note "<what was verified>"`.
4. **Fixes:**
   - A local defect: `fix <ID> "<one precise change: place, wrong state, right state>"` (add `--ref` of the sheet for identity).
   - A wrong composition: rewrite the prompt, then `qc <ID> fail --regen`.

   Then **one combined wave-2 batch** (`--ready`) carries every fix and every wave-2 item together. Wave 3 the same way.
5. **Hard cap of 3 calls per image** (enforced in imggen.py: nothing allows a 4th). After the 3rd result, pass it or `accept <ID> --note "<defect>"`.
   - Minor art flaws are accepted.
   - Flag to the master only wrong maths or counts, a wrong character, or a missing key action.
