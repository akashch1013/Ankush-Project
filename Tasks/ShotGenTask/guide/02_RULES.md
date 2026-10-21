# 02 · Rules — one de-conflicted list

This chapter merges three sources: the V07 manifest's global rules, Production Brief V03 and Rule Book V01, plus the decisions made for this approach. Where they disagree, the table at the end says which one wins and why.

Rule IDs are for briefs and reports only. They are never printed on a page.

## S · Source and text

- **S1. The manuscript is the only source of reader-facing words.** The authority is `CH 01 PANELIZED MANUSCRIPT V07.docx`, read through `CH01_V07_PANEL_MANIFEST.json`. The pipeline copies text from there, so do not retype it.
- **S2. Print text exactly.** Wording, punctuation, numbering, intended repetitions and emphasis must not change. Line breaks may change.
- **S3. Keep printable and production text apart.** These are never printed: focus lines, IDs, locators, filenames, notes, "PRINTABLE / NON-PRINTABLE" markers and the six `Narration` role labels.
- **S4. Speaker prefixes.** Balloons print the spoken words without the exact `SPEAKER: ` prefix, and the tail identifies the speaker. This is the user's decision of 2026-10-11, matching every sample page. The audit checks that the prefix is absent and that the speaker is drawn in that panel.
- **S5. Preserve page and panel boundaries.** Keep each panel on its page and in reading order. Never merge, split, move or renumber without the user's decision.
- **S6. Never invent content:** no extra events, jokes, questions, answers, symbols or numbers. If a direction is incomplete (the manifest's `open_details`), stop that panel and ask.
- **S7. Stop on conflicts.** If the text, the maths or the visual directions contradict each other, report the exact block and stop that panel. Continue independent work.
- **S8. One revision at a time.** Use the V07 panel IDs (`V07/CH01-P###-PN##`). Old V02/V04/V06 page numbers are historical only.

## R · References

- **R1. Look at the actual images.** Open every reference before writing a prompt; a filename is not an inspection.
- **R2. Keep literal filenames,** misspellings included: `ANTERN`, `NAYA`, `ADJASCENT`, `THRESHHOLD`, `.png.png`. Map a different file only through `design/reference_map.json`, with a reason, and only after the user confirms.
- **R3. The first named location is the primary architecture reference.** Extra references get explicit roles.
- **R4. References carry production marks.** Label boxes, pointer lines and arrows are annotations. Tell the image model to ignore them.
- **R5. A reference may be in the wrong state for this panel.** Lamps lit or dark, hatch open or closed, controls faulty or fixed. Preserve the design and state the correction (see `design/locations.json`). Never freeze an incorrect state.
- **R6. Apply the location exception register** (LOC-EX-01…14, in `design/locations.json`). A covered minor mismatch is a PASS WITH LOCATION EXCEPTION, not a regeneration.
- **R7. Use continuity anchors.** Approved art from earlier pages and panels (`design/continuity/`, plus approved panels listed in `anchors:`) is the best guide to rendering style and character look. Give each one the role "match style and characters, not composition".

## C · Story continuity

- **C1. Character sheets govern identity:** face, age, hair, outfit, colours, props. The panel governs pose, hand use, gaze, expression and state.
- **C2. Name the hand.** Always "her own left hand", "his own right forepaw". Never viewer-left or viewer-right.
- **C3. One readable moment per panel.** No sequences in a still, no extra hands, no duplicated characters.
- **C4. Track states across panels and pages:**
  - gate light, hatch, tickets and marks;
  - the empty Bell stand and its rope;
  - lamps lit or dark;
  - Tez's stripe colours, which are set per scene in the manuscript.
- **C5. The reader is never drawn.** The ChandRush Crew is the reader.
- **C6. The moon and religious symbols.** Any visible sky moon is one complete full moon, never a crescent. No religious motifs. The silver crescent-shaped invitation tickets are story props, not moons.
- **C7. No added characters as a quota.** Show exactly who the panel names. Crowds only where the manuscript has them.
- **C8. Told, not shown.** When narration describes things not in the scene (the thief, the sabotage, faulty magic), do not draw them.

## P · Prompts

- **P1. Use Codex's imagegen schema** (`04_PROMPTING.md`): Use case, Asset type, Input images, Primary request, Scene/backdrop, Subject, Style/medium, Composition/framing, Lighting/mood, Constraints, Avoid.
- **P2. Self-contained.** No "see previous panel" and no project jargon the model cannot see. Images are named by index and role.
- **P3. Put the critical facts first,** in Subject: who, where, which hand, which state. Style details come later.
- **P4. Describe visible results** ("eyes lowered to the empty mount"), not intentions ("show worry correctly").
- **P5. No text in images.** All lettering is added by the pipeline. Every Avoid line forbids text, and the lint enforces it.
- **P6. Reserve calm areas** for the captions and balloons that the layout places on the art.
- **P7. Ask for the frame's own aspect ratio and size** (legal gpt-image-2 sizes), with a central-band rule for fixed-size tools.
- **P8. Use a few targeted exclusions,** not long lists of unrelated things.
- **P9. Keep the manuscript's wording for the action.** Do not add props, creatures or beats it does not mention.
- **P10. Run `prompts lint` before spending a generation.**

## A · Art acceptance and corrections

- **A1. Check the important things first:** identity, action and hand, required objects and states, no lettering. Style comes after.
- **A2. Statuses.**
  - **BLOCK-level** (wrong character, action, state or count, text in the image, cropped key content): regenerate once.
  - **FIX-level** (tail position, crop, balloon placement): fix in assembly, never by regenerating.
  - **Harmless variation:** accept it and note it.
- **A3. Choose the smallest fix:**
  - local defect: a targeted edit of that image, ending "Preserve everything else exactly";
  - wrong construction: regenerate with a corrected prompt;
  - lettering, crop or balloon problems: assembly.
- **A4. One automatic correction per panel.** After that, approve the better version as REVIEW_LATER with a note, and continue.
- **A5. Never regenerate approved art** for a font, balloon, caption or layout change.
- **A6. Find out why the prompt failed** (missing, vague, contradicted or buried requirement) and fix the prompt file, not just the image.
- **A7. Report honestly.** Do not claim a count, hand or detail was checked if it was not visible.
- **A8. Versions are immutable.** A new attempt is a new `vNNN`; the record keeps what changed.

## L · Layout and typography (story pages)

- **L1. Page size:** 12 × 9 in landscape, 864 × 648 pt.
  - margins: 24 pt (bottom content edge 618 pt);
  - gutters: about 20 pt;
  - page number: 8 pt, bottom right.
- **L2. Each page gets a composition suited to its content.** Reuse styles, not geometry.
- **L3. Give the meaningful beat the larger panel** (for example, the reveal in P011).
- **L4. Plan the real text first** (`proof`). Recover space before considering anything else.
- **L5. Story type sizes** (measured from the Opening V04 sample):

  | Element | Font and size |
  |---|---|
  | Narration | Source Serif 4 Regular 14/16.1 |
  | Speech | Source Sans 3 Semibold 14/16.1 |
  | Reader call-out | Source Serif 4 Semibold 16/18.4 |

- **L6. Maths pages** use Source Sans 3 at 14/18, or 13/17 for genuinely dense pages, never smaller (Brief V03 §5). There is no maths renderer yet; see `07`.
- **L7. Never shrink, squeeze, hyphenate-to-fit or hide overflow.** The build fails instead.
- **L8. Never stretch art.** Cover-fit with a focus point, crop inside safe areas, and keep faces, hands and key objects in frame.
- **L9. Borders and themes come from the sample's study set.** Record them per page; never pick them at random.
- **L10. Prologue pages carry the page number only,** as in the Opening sample. Chapter pages add compact chapter, section and page metadata (Rule Book D11), styled like the text-led sample.

## B · Captions and balloons

- **B1. Captions** are pale rounded boxes (radius 7 pt, 5 pt side padding) over calm art, at least about 13 pt inside the frame.
- **B2. Balloons** are ivory (#fffdf8) with a 0.8 pt navy outline, radius 9, centred, balanced lines. The tail is short and straight.
- **B3. Tails** point towards the speaker's mouth and stop before the face. Set the target on the real art (`tail`). The default target is only for proofs.
- **B4. Keep artwork continuous under balloons.** Never cut holes or add blank strips.
- **B5. Keep faces, hands, tickets and key props visible.** Move or resize the box rather than covering them.
- **B6. Reader call-outs** sit on the page background, in ivory on dark themes.

## X · Assembly and export

- **X1. Assemble from the saved components:** art, exact text and vector furniture. Never ask an image model to redraw a finished page.
- **X2. Fonts are embedded.** Text stays real text in the PDF, which is how the audit reads it.
- **X3. 300 ppi at placed size is the target.** Lower values are reported, never hidden. Upscaling does not add detail.
- **X4. Review exports are RGB with no bleed.** Final print settings come from the printer (trim, bleed, colour, PDF/X).
- **X5. Re-open the exported PDF and PNG and look at them.** A successful command is not a visual check.
- **X6. Keep proofs clearly marked.** Stand-in and placeholder art carries a raster label and the audit says PROOF.

## Q · Audit and reporting

- **Q1. Audit the exported PDF against the manuscript,** not against the layout or the brief.
- **Q2. Page status** is PASS / REVIEW / PROOF / FAIL, exactly as `audit` reports it.
- **Q3. Report** what was produced, what passed, what is REVIEW_LATER and why, the effective ppi, and what was not verified.
- **Q4. Batches** are 5 pages by default and 10 at most. Then wait for the user's review.
- **Q5. Track** generations, retries and manual interventions (`state.json` log).
- **Q6. Do not start the next batch,** or change content or pagination, without the user.

## F · Files

- **F1. Never modify** `Scripts/`, `Charactors/`, `Locations/` or `Completed Samples/`.
- **F2. Name files by ID:** `art/<panel>/<panel>-art-vNNN.png`, `output/pdf/CH01-P0xx.pdf`. Match assets by ID, never by upload order.
- **F3. `state.json` is the progress record.** `.cache/` is disposable.
- **F4. Keep secrets out.** Never write API keys into files or reports.

## Conflicts resolved

| Topic | Sources disagree | Resolution | Why |
|---|---|---|---|
| Manuscript version | Rule Book cites V02, Brief cites V04, folder has V07 | **V07** | It is the file provided, and its checksum matches the manifest |
| Minimum type size | Rule Book D02: 18 pt; Brief V03: 14 pt maths; sample: 14 pt narration | **14 pt** (13 pt only for dense maths) | The Brief supersedes the Rule Book, and the sample confirms it |
| Speech type | Brief: Source Serif 4 12/15 ("latest trial, not approved"); Opening sample (1 Oct): Source Sans 3 Semibold 14 | **Sample** | The user chose "copy the Opening PDF look exactly"; the sample is the later decision |
| Speaker prefixes | V07 rules: keep the source prefix; samples: hidden | **Hidden; tail identifies the speaker** | User decision, 2026-10-11 |
| Page metadata | Rule Book D11: header on every page; Opening sample: page number only | **Page number only on prologue pages**; full header from Chapter 1 pages | Prologue pages are not chapter pages, and that is what the sample does |
| Balloon tails | Rule Book: aim at the mouth; sample: short straight tails | **Short straight tail aimed at a point beside the mouth** | Satisfies both |
| Whole-page AI images | Some samples (P029–P047 PNGs) were whole-page generations; Brief V03 forbids them | **Per-panel art + code assembly** | Exact text, editability, and the Brief rule; the look is reproduced in code |
| Crescent shapes | Rules ban crescent moons; the story's invitations are silver crescents | **Sky moon always full; crescent tickets allowed** | The tickets are approved story props (Opening art) |
| Retry loop | Rule Book J-rules: bounded retries; Brief V03: max one automatic retry | **One** | Brief V03 supersedes |
