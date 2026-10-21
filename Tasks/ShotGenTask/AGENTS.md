# AGENTS.md — ChandRush Approach1 (read this first)

You are working in `Approach1/`, a self-contained pipeline that turns the ChandRush V07 manuscript into finished graphic-novel pages in the approved sample look. **Image models paint the panel art; code letters and assembles the pages.** Run every command from this folder as `python -m pipeline <command>`.

## Current state

**Batch `P009-P013`** (V07 pages 9–13, 14 story panels) has:
- exact contracts, page briefs, layouts;
- 14 linted prompt files;
- numbered reference packs.

**Only the panel art is missing.** `python -m pipeline status` shows exactly what is next.

## Default task: when asked to "continue", "make the art" or "finish the pages"

1. Make the art with your **built-in `image_gen` tool** (no API key). Repeat until the command prints `ALL PANELS DONE`:
   1. Run `python -m pipeline next --codex`. It prints exactly one task, **GENERATE** or **REVIEW**, with numbered steps:
      - the absolute paths of the reference images to `view_image`, in order;
      - the exact prompt between `-----BEGIN PROMPT-----` and `-----END PROMPT-----`;
      - the panel's checklist and the commands to run next.
   2. For a GENERATE task:
      - `view_image` each listed image in order.
      - Call `image_gen` with the prompt text unchanged, at the stated aspect.
      - Run `python -m pipeline ingest --from-codex`. This copies your newest image from `$CODEX_HOME/generated_images` into the panel's art folder.
      - If the task says images were already generated for this panel, do not generate again. Run `python -m pipeline ingest --from-codex --all-new` instead.
   3. For a REVIEW task:
      - Run `python -m pipeline review --panel <id>`, then `view_image` the overlay and the art.
      - Check every **Accept only if** line, then run `approve`.
      - If a line fails: `reject` with the reason, make one correction, run `ingest --from-codex`, and review again. If it is still wrong, `approve --status REVIEW_LATER --note "..."`.
   4. For the balloon panels (P009-PN02, P010-PN02), after approving: `python -m pipeline tail --panel <id> --at U,V`, at a point just beside the speaker's mouth.

   `python -m pipeline next --json` gives the same task as JSON. The older manual route still works: `next --no-open --no-clipboard`, then copy the image into `art/_inbox/` and run `ingest --route codex`. The full loop with its reasons is in `skills/chandrush-art-producer/SKILL.md`; the copy-paste user prompt is in `MANUAL.md` section 2.
2. Follow `skills/chandrush-assembler/SKILL.md`: run `python -m pipeline build`, then look at every `batch/P009-P013/output/png/*.png`.
3. Follow `skills/chandrush-auditor/SKILL.md`: run `python -m pipeline audit` and `python -m pipeline status`. Then report each page's status using the exact audit word: PASS, REVIEW, PROOF or FAIL. **Stop** and wait for the user.

## Starting the next pages

Use the skills in order:
1. `chandrush-director`: `new-batch`, `extract`, briefs, layouts, `proof`.
2. `chandrush-prompt-writer`: `prompts draft`, edit, `prompts lint`, `refs`.
3. Then the art loop above.

Batches are 5 pages by default, 10 at most. Skip pages that the samples already cover; the list is in `guide/07_ISSUES_AND_DECISIONS.md`.

## Hard rules (the reasons are in `guide/02_RULES.md`)

- Never modify `../Scripts`, `../Charactors`, `../Locations` or `../Completed Samples`. They are read-only sources.
- Never put text, letters or numbers into generated art. Never retype or edit manuscript text; the pipeline letters it from the manifest.
- Never invent story content, props, characters or numbers. If the manuscript is incomplete or contradictory, stop that panel and ask.
- Allow one automatic correction per panel, then REVIEW_LATER. Never regenerate approved art for a layout, font or balloon change.
- Never shrink type, squeeze letters or drop words to make text fit. Fix the layout instead.
- Never edit `~/.codex/skills/.system/imagegen/scripts/image_gen.py`. Never write API keys into files.
- Report honestly. A plan, a prompt or a successful command is not a finished page.

## Where things are

| Need | File |
|---|---|
| Step-by-step pipeline | `guide/01_PIPELINE.md` |
| Rules and conflict resolutions | `guide/02_RULES.md` |
| Look (tokens measured from the sample) | `guide/03_DESIGN_SYSTEM.md`, `design/tokens.json` |
| How to write and fix prompts | `guide/04_PROMPTING.md` |
| Image routes (built-in, API, ChatGPT) | `guide/05_IMAGE_ROUTES.md` |
| Build and audit | `guide/06_ASSEMBLY_AND_AUDIT.md` |
| Decisions, open issues, what's verified | `guide/07_ISSUES_AND_DECISIONS.md` |
| Progress record | `batch/<id>/state.json`, `batch/<id>/output/STATUS.md` |
