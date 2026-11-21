---
name: chandrush-art-producer
description: Produce, file, check and approve the panel artwork for ChandRush pages, one panel at a time. Use Codex's built-in image_gen tool (no API key), Codex's image CLI or OpenAI API, or a person's ChatGPT downloads; ingest each image into versioned panel art; review it against the panel's checklist with an overlay of crop, text zones and grid; approve, reject with one retry, or keep as REVIEW_LATER. Use whenever ChandRush panel images need to be generated, imported from ChatGPT or Downloads, checked, approved or redone.
---

# ChandRush art producer

Your goal is a correct, approved image for every story panel in the batch's queue. "Correct" means it satisfies the prompt file's **Accept only if** list. Pretty is not enough: a wrong hand, a bell on the empty stand or lettering in the art fails the panel.

The route details are in `guide/05_IMAGE_ROUTES.md`. Commands run from `Approach1/` as `python -m pipeline ...`.

## Loop (repeat until `next --codex` prints ALL PANELS DONE)

1. **Get the task.** Run `python -m pipeline next --codex`, or `--json` for a machine-readable version. It prints one task:
   - **GENERATE**: the reference images to view (absolute paths, in order), the exact prompt between BEGIN/END markers, the size, the checklist and the follow-up commands.
   - **REVIEW**: a panel whose art is waiting for a decision. Reviews always come first, so nothing is left unreviewed.

   People using ChatGPT run plain `next`, which copies the prompt and opens the image folder.
2. **Generate.**
   - **Codex built-in route:** `view_image` every listed image, in order. Call `image_gen` with the prompt text unchanged, at the stated aspect.
   - **API route:** run `python -m pipeline generate --panel <panel> --run` (needs `OPENAI_API_KEY`). It files the image by itself.
3. **Ingest.**
   - Codex: `python -m pipeline ingest --from-codex` takes the newest image from `~/.codex/generated_images`. Add `--all-new` to file several attempts.
   - Others: `ingest --downloads`, or `ingest` for files in `art/_inbox`.

   Each image becomes a new version `art/<panel>/<panel>-art-vNNN.png`. Nothing is overwritten. If `next --codex` says images were already generated for the panel, file them instead of generating again.
4. **Review.** Run `python -m pipeline review --panel <panel>`. Look at the overlay in `art/_review/` (gold box = the part the page shows, cyan = reserved text areas, magenta = tail target) and at the full art.
5. **Judge against the checklist**, in this order:
   1. identity;
   2. action and hands;
   3. required objects and states;
   4. no lettering;
   5. calm text areas;
   6. style.
6. **Decide.**
   - **All pass:** run `python -m pipeline approve --panel <panel>`. Use `--status PASS_WITH_LOCATION_EXCEPTION --exceptions LOC-EX-xx` when only a covered location detail differs.
   - **Any fail:** run `python -m pipeline reject --panel <panel> --reason "<what>"`. Then make **one** correction: a targeted edit of that image for a local fault, or a regeneration with a fixed prompt for a wrong construction. Ingest it.
   - **Still failing after one correction:** run `python -m pipeline approve --panel <panel> --version <best> --status REVIEW_LATER --note "<issue>"` and move on. Do not loop.
7. **Balloon panels.** Read U,V just beside the speaker's mouth (in clear space, not on the face) from the overlay grid. Run `python -m pipeline tail --panel <panel> --at U,V`. If the crop hides something important, run `python -m pipeline frame --panel <panel> --focus U,V`.

## Why the order matters

The queue puts scene anchors first. Approving one copies it into the reference folders of the later panels that list it, so they inherit its lighting and character look.

## Report

After the loop, run `python -m pipeline status`. Report each panel's state honestly, including REVIEW_LATER notes and how many generations each panel took.
