# Approach1 — ChandRush pages, made (almost) automatically

> **How to use it, step by step, plus a ready-to-send Codex prompt: see [`MANUAL.md`](MANUAL.md).**

This folder holds everything needed to turn the V07 manuscript into finished ChandRush pages that look like your **Opening V04** sample, with the story text word-for-word from the script.

It is set up for **V07 pages 9–13**, the first five pages that no sample covers. That is 14 story panels at the Old Blue Gate and in Entry Court.

## What is ready, and what is left

| Ready | Left to do |
|---|---|
| Exact text for every panel, pulled from the manifest and checksum-verified | **The 14 panel images** (one per prompt) |
| A "page understanding" brief for each page (`batch/P009-P013/pages/*.brief.md`) | Approve them and aim the two speech-balloon tails |
| Page layouts that fit the real text at the sample's font sizes | `build` + `audit`, then your review |
| **14 prompt files** with numbered reference images (`batch/P009-P013/prompts/`) | |
| A pipeline that files the images, assembles the pages, exports PDF and PNG, and audits them | |
| Guidelines and skills that a coding agent follows on its own (`AGENTS.md`, `guide/`, `skills/`) | |

To preview the pages before any art exists, open `batch/P009-P013/output/proofs/`:
- `*-LAYOUT-PROOF.png`: grey boxes with the real text;
- `*-STANDIN-PROOF.png`: location images standing in for the art.

## Make the 14 images — pick one way

### A) Let Codex do everything (recommended, no API key)

Open Codex **in this `Approach1` folder** and say:

> Follow AGENTS.md and make the art for batch P009-P013, then build and audit the pages.

Codex uses its built-in image tool for each panel in queue order. It checks each image against that panel's checklist, approves it or retries once, then builds and audits the pages and reports back.

### B) ChatGPT in the browser (by hand, about a minute per panel)

```bash
cd Approach1
python -m pipeline next        # copies the prompt to your clipboard and opens the panel's image folder
```

1. In a **new** ChatGPT chat, drag in all the numbered images from the folder that opened, paste the prompt and send.
2. Download the image, then run `python -m pipeline ingest --downloads`, or save it into `batch/P009-P013/art/_inbox/` and run `python -m pipeline ingest`.
3. Run `python -m pipeline review --panel <panel id>` and open the overlay PNG it names in `art/_review/`.
4. If it matches the prompt file's **Accept only if** list, run `python -m pipeline approve --panel <panel id>`. Otherwise run `python -m pipeline reject --panel <panel id> --reason "..."` and try once more.
5. Repeat `next` until `python -m pipeline status` says every panel is approved.

### C) Fully unattended with an OpenAI API key

Set `OPENAI_API_KEY` in your environment, then run `python -m pipeline generate --run` once per panel. Each image is filed automatically; review and approve as in B, steps 3–4.

## Build the pages

```bash
python -m pipeline tail --panel CH01-P009-PN02 --at U,V     # aim Vihaan's balloon (U,V from the review grid, beside his mouth)
python -m pipeline tail --panel CH01-P010-PN02 --at U,V     # aim Tez's balloon
python -m pipeline build                                     # pages -> PDF + 300-dpi PNG
python -m pipeline audit                                     # checks text, fonts, art status, tails
```

Then look at:
- `batch/P009-P013/output/CH01-P009-P013-REVIEW.pdf`: the five pages, for your review;
- `batch/P009-P013/output/png/`: each page at 3600×2700;
- `batch/P009-P013/output/AUDIT.md` and `STATUS.md`.

## Folder map

```
Approach1/
  README.md, AGENTS.md, CLAUDE.md     start here (people / Codex / Claude Code)
  guide/        00-07  the full automation guidelines (pipeline, rules, design, prompting, routes, audit, issues)
  skills/       5 agent skills: director, prompt-writer, art-producer, assembler, auditor
  design/       tokens.json (look measured from the sample), characters.json, locations.json,
                reference_map.json, continuity/ (your approved Opening art used as style anchors)
  fonts/        Source Serif 4 + Source Sans 3 (OFL)
  pipeline/     the Python code (python -m pipeline --help)
  batch/P009-P013/
    pages/      contracts (exact text), briefs (understanding), layouts
    prompts/    14 prompt files, QUEUE.md, refs/<panel>/ numbered reference images
    art/        _inbox/ (drop images here), one folder per panel with versions, _review/ overlays
    output/     proofs/, pdf/, png/, REVIEW pdf, AUDIT.md, STATUS.md, compare/
```

Your original folders (`Scripts`, `Charactors`, `Locations`, `Completed Samples`) are only read, never changed.

## Decisions taken with you (2026-10-11)

- **Pages:** 9–13.
- **Look:** the Opening V04 PDF.
- **Balloons:** show the spoken words without the `NAME:` prefix; the tail shows who speaks.

Other choices, open questions and what was tested are in `guide/07_ISSUES_AND_DECISIONS.md`.
