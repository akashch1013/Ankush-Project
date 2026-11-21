# 00 · Overview — how Approach1 makes ChandRush pages

Approach1 turns the approved manuscript into finished graphic-novel pages. A coding agent (Codex or Claude Code) can run most of it alone, and a person can step in at any point. It is built and tested on **V07 pages 9–13**, the first five pages that no sample covers. Every command also works for later batches.

## The one idea that makes it work

**The image model paints; the code letters.**

- Image generation is used only for each panel's illustration, with no text in it.
- Everything readers read is drawn by code, straight from the manifest: narration, dialogue, reader call-outs and page numbers. So the words are always exactly the script's words, in the sample's fonts and sizes.
- Everything else is assembled by code too: frames, crops, balloons, borders, colours.

That is why the pages can look like the samples while the story stays word-for-word.

## Pipeline at a glance

```
 Scripts/CH01_V07_PANEL_MANIFEST.json ──extract──▶ pages/*.contract.json   (exact printable text, notes, refs)
                                                     │
            Director ───────────────────────────────▶ pages/*.brief.md       (story, continuity, references)
                                                     pages/*.layout.json     (frames, caption/balloon spots)
                                                     │  proof (grey) / build --mode standin
            Prompt writer ──────────────────────────▶ prompts/*.md           (one per story panel) + lint + refs
                                                     │
            Art producer ─ next ▶ image tool ─▶ art/_inbox ─ingest▶ art/<panel>/vNNN.png ─review▶ approve | reject
                           (Codex built-in │ Codex CLI/API │ ChatGPT web UI)        └─ tail / frame (fine-tune)
                                                     │
            Assembler ── build ─────────────────────▶ output/pdf/*.pdf, output/png/*.png, *-REVIEW.pdf
            Auditor ──── audit ─────────────────────▶ output/AUDIT.md (+ .json), output/STATUS.md
```

## Roles, skills and commands

| Role | What it decides | Skill | Main commands |
|---|---|---|---|
| Director | Which pages, what each panel shows, page layout, reserved text areas | `skills/chandrush-director` | `new-batch`, `extract`, `proof`, `build --mode standin` |
| Prompt writer | Short, complete, self-contained image prompts with the right references | `skills/chandrush-prompt-writer` | `prompts draft`, `prompts lint`, `refs` |
| Art producer | Getting each panel's art made, checked and approved | `skills/chandrush-art-producer` | `next`, `generate`, `ingest`, `review`, `approve`, `reject` |
| Assembler | Crops, balloon tails, page assembly and export | `skills/chandrush-assembler` | `tail`, `frame`, `build`, `compare` |
| Auditor | Whether the exported pages are true to the script and the rules | `skills/chandrush-auditor` | `audit`, `status` |

One agent can play every role in sequence. The roles are a checklist, not separate programs.

## Order of authority (highest first)

1. **The user's explicit decisions**, recorded in `batch/<id>/batch.json` and `07_ISSUES_AND_DECISIONS.md`.
2. **The V07 manuscript**, i.e. `Scripts/CH 01 PANELIZED MANUSCRIPT V07.docx` via its manifest. Text, panel order, scene directions and reference names.
3. **The approved sample pages** for the look: Opening V04 for story pages, plus the text-led and story-maths PDFs and P018/P047 for maths pages.
4. **Production Brief V03** (`Scripts/CHANDRUSH-PANEL-AND-PAGE-PRODUCTION-BRIEF-V03.md`).
5. **Rule Book V01** (`Scripts/CHANDRUSH_PAGE_PRODUCTION_RULE_BOOK_V01.md`), where it is not superseded.

`02_RULES.md` merges these into one list and records each conflict and how it was resolved.

## Statuses you will see

| Where | Values |
|---|---|
| Panel art (`approve`) | **PASS**, **PASS_WITH_LOCATION_EXCEPTION**, **REVIEW_LATER** (best attempt kept, issue recorded) |
| Panel progress (`status`) | pending → in_progress → art_ready → approved / review_later |
| Exported page (`audit`) | **PASS** (final-ready for user review), **REVIEW** (usable, issue recorded), **PROOF** (stand-in art still in place), **FAIL** (text, font or size problem) |

Never call a page final or print-ready unless the audit says PASS **and** the user has reviewed it. Print-ready also needs the printer's specification (`06_ASSEMBLY_AND_AUDIT.md`).

## Read next

- `01_PIPELINE.md`: every stage with inputs, commands, outputs and done-criteria.
- `05_IMAGE_ROUTES.md`: the three ways to make the art (Codex alone, API, ChatGPT by hand).
