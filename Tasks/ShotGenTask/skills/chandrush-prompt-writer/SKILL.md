---
name: chandrush-prompt-writer
description: Write and check the image prompts for ChandRush story panels, one self-contained prompt file per panel with the right reference images in the right order, the exact story state, identity hints, calm areas for lettering, the correct size, and an accept-only-if checklist. Use whenever panel prompts must be created, fixed, reviewed or linted, when art keeps coming out wrong and the prompt needs repair, or when someone asks for "the prompts folder" for ChandRush pages.
---

# ChandRush prompt writer

A prompt file is the complete work order for one panel's artwork. The image model sees only the prompt text and the attached images. Anything it needs to know must be in one of those two places, stated as a visible result.

Read `guide/04_PROMPTING.md` once. It covers anatomy, image order, state corrections, sizes, common failures and the targeted-edit template. The 14 files in `batch/P009-P013/prompts/` are reviewed examples.

## Steps

1. **Draft.** Run `python -m pipeline --batch <id> prompts draft`. It builds a near-complete draft per story panel from the manuscript note, the layout `compose` line, `design/characters.json` and `design/locations.json`. Panels with no visual note (maths/text) get no prompt: they are typeset, not painted.
2. **Edit each draft against the page brief.**
   - **Queue:** set `queue` so scene anchors come first (the first panel at each location and of each character group).
   - **Continuity image:** add it as Image 2 (`design/continuity/…` or an approved panel), with the role "match style and characters, not composition".
   - **Anchors:** list `anchors` (approved earlier panels of the same scene). Add the optional last-image line to *Input images*.
   - **Primary request:** one sentence.
   - **Scene:** state every correction where the reference shows a different state (lights, doors, empty stand, map without text).
   - **Subject:** name hands as "own left/right". Put the identity hint at each character's first mention. Copy Tez's stripe sentence for that scene.
   - **Checklist:** turn each clause of the manuscript's *Static visual* into one "Accept only if" line. List harmless variations separately.
   - **Size:** keep the frame's aspect (the draft computes the legal size) and the fallback band.
   - Set `review_needed: false`.
3. **Lint.** Run `python -m pipeline prompts lint` until it reports `All N prompt files pass.`
4. **Build reference packs.** Run `python -m pipeline refs`. This creates `prompts/refs/<panel>/` with numbered images and `prompts/QUEUE.md`.

## Guardrails

- **No lettering in images.** All text is added by the pipeline, so never put manuscript sentences in a prompt. The lint checks this.
- **No new content.** No extra props, creatures, characters or story beats. Describe what the manuscript describes.
- **Keep it short and complete:** about 2,000–3,500 characters, critical facts first.

## When art comes back wrong

Find the cause in the prompt: was the requirement absent, vague, contradicted or buried? Fix the prompt file, then either make one targeted edit or regenerate once (`guide/04_PROMPTING.md`, "Targeted correction"). Don't just retry the same words.
