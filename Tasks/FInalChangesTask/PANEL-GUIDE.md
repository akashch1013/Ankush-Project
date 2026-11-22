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

## 2. References: which images, in which order
The order is fixed. Declare each image in the prompt by its number:
1. **Image 1 = the background plate** from stage 1, always the *raw* plate (`BagroundGenTask/out/plates/<ID>.png`, `ch02/out/plates/`, `ch03/out/plates/`). Never use the composed `out/final/` version, which has a title band and callouts that would leak.
2. **Image 2…n = one character sheet for every character visible in the panel**, in the order they are named in the prompt:

| Character | Sheet (relative to Tasks/) |
|---|---|
| Ahana | `../Charactors/CHANDRUSH CHARACTERS/AHANA CHARACTER SHEET.png` |
| Navya | `../Charactors/CHANDRUSH CHARACTERS/NAVYA CHARACTER SHEET.png` |
| Vihaan | `../Charactors/CHANDRUSH CHARACTERS/VIHAAN CHARACTER SHEET.png` |
| Tara | `../Charactors/CHANDRUSH CHARACTERS/TARA CHARACTER SHEET.png` |
| Tez (tiger cub) | `../Charactors/CHANDRUSH CHARACTERS/TEZ CHARACTER SHEET.png` |

   A character with no sheet (e.g. Ira, Kabir, Veer, visitors) is described from the manuscript's *Characters visible in this chapter* text. When their first panel is approved, crop a clean full-figure view into `library/characters/<NAME>-ref.png` and use that crop as their reference from then on.
3. **Last, optional: `item:<previous panel>`** when continuity of a held prop, a machine state or a pose matters across consecutive panels. This makes the item wait for that panel's approval (wave 2+).

Do not attach more than 5 images. If 4 or more characters are visible, attach sheets only for the 3 most prominent, and describe the others in words.

## 3. Size and quality
- Match the size to the panel's box (aspect from `pages.json`):

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

## 7. Loop
1. Write the prompt + CHECKS. Run `check` and `dry-run <ID>` once, and read the sent prompt and ref order.
2. Build and submit: the **samples** are the first 2 panels of a new chapter, in their own batch (`batch build <CHxx>-samples P001-1 P001-2`). After the user approves them, run the rest in waves (`batch build <CHxx>-w1 --ready`). Run `batch wait` in the background.
3. QC every image like an art director: Read it, `zoom` faces, hands, counts and inscriptions, and compare with the sheets. Then `qc <ID> pass --note "<what was verified>"`.
4. To fix:
   - A local defect: `fix <ID> "<one precise change: place, wrong state, right state>"` (add `--ref` of the character sheet for identity fixes). Fixes are queued and sent with the next `--ready` batch.
   - A wrong composition: revise the prompt, then `qc <ID> fail --regen`.
5. Cap: at 3 calls → `accept <ID> --note "<defect>"` and move on. Only huge errors (wrong maths/count, wrong character, missing key action) are worth flagging to the master. Minor art flaws are accepted.
