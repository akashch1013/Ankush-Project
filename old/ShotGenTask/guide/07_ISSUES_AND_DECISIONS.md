# 07 · Issues and decisions — what is settled, what is open, what was verified

## Decisions

| Date | Decision | By |
|---|---|---|
| 2026-10-11 | Build Approach1 in its own folder; the source folders stay read-only | user |
| 2026-10-11 | Pilot batch = **V07 pages 9–13**, the first five pages no sample covers | user (recommended option) |
| 2026-10-11 | Copy the **Opening V04 PDF look** exactly (dark themed pages, gold-framed art, pale captions, white balloons, Source fonts, page number only) | user |
| 2026-10-11 | Balloons **omit the `SPEAKER:` prefix**; the tail identifies the speaker | user |
| 2026-10-11 | Panel art is made per panel; pages are assembled in code (no whole-page AI images) | Brief V03 + this approach |
| 2026-10-11 | Use the user's approved Opening art (V07 p8) as the continuity anchor for style, characters, the crescent tickets and Tez's blue stripes | this approach |
| 2026-10-11 | Hatch on p9–10 stands slightly open on darkness (matches approved Opening art p12); open wide enough for a child on p11 | Director, from the manuscript and the approved art |

## Which pages the samples already cover

This was checked by matching sample text against the V07 manifest. Two of the files in `Completed Samples/Img/` are named with old page numbers (P018 and P047); their content is V07 p28–29 and p75–76.

| Sample | V07 pages |
|---|---|
| Opening V04 PDF (12 sheets) | 1–8 |
| Five reference pages PDF | 16, 64, 92, 103, 104 |
| Story-maths five pages PDF | 22, 27, 30, 33, 34 (+ part of 21) |
| Text-led five pages PDF | 46, 63, 74, 86 (cube roots), 34 (brackets) |
| `CH01-P018-PREVIEW-300PPI.png` | 28–29 |
| ChatGPT page images | 49–50 (HCF), 60–61 (tests for 25, 100, 8), 62–63 (digit sums, test for 7) |
| `ChandRush_CH01_Page_47_V02.png` | 75–76 |

The next uncovered runs are **14–15**, **17–21** (21 partly), **23–26**, **31–32**, **35–45**, and so on.

## Open issues for later batches (none block pages 9–13)

1. **Missing reference files (26).** These are listed with their candidates in `design/reference_map.json`:
   - three are probably the same file under another name; the author needs to confirm;
   - seven are missing *state variants*: lift faulty/corrected controls, lift at −8, timing-drum reset/repaired/empty/filled kits. These states carry the maths teaching, so they must not be substituted;
   - fourteen are approved-art or vignette files that do not exist yet (`CH01-CHAR-*`, `CH01-FAIR-ARRIVAL-MUMBAI-V01.png`).
2. **Version names in the documents.** The Rule Book names manuscript V02 and Brief V03 names V04, but the delivered manuscript is **V07**; we follow V07. `Scripts/README.txt` mentions `panel_jobs/` and `embedded_diagrams/` folders, which are not present: the three diagrams are inside the DOCX. Design Manual V04 is referenced but not in the project.
3. **Two manuscript details to confirm** (manifest `open_details`):
   - CH01-P050-PN05: the LCM/HCF branch examples are unspecified;
   - CH01-P061-PN01: no failing divisibility-by-8 value is given.
4. **Maths pages need a maths component renderer.** The pipeline already handles text, fonts, layout and audit. Maths panels also need typeset worked steps, tables, number lines and highlights in the style of the story-maths and text-led samples (Source Sans 3 14/18; ivory working surfaces; teal or navy headers). This batch has no maths, so it is not built yet. It is the next engineering step before the first mixed page (e.g. pages 17–21).
5. **Resolution with fixed-size tools.** The ChatGPT web UI usually gives 1536×1024. On a full-width 816-pt frame that is about 135 ppi: fine for review, not for print. Routes A and B can request the preferred sizes (about 270–300 ppi).
6. **Speech font.** Brief V03 marked speech typography as "trial, approval open". We follow the later Opening sample (Source Sans 3 Semibold 14). Changing it is one token in `design/tokens.json`.
7. **Duplicate manuscript.** `CH 01 PANELIZED MANUSCRIPT V07_1.docx` is byte-identical to the V07 file, so it is harmless.

## Verified in this session

- `extract`: the manuscript checksum matches the manifest. 5 contracts, 14 panels, 14 printable blocks, every block hash-checked against the manifest.
- `proof` and `build --mode standin`: all five pages build with no layout errors. Text fits at sample sizes and no glyphs are missing.
- `prompts lint`: all 14 prompt files pass. `refs`: 59 numbered reference links.
- `generate --dry-run`: Codex's `image_gen.py` accepted the request (refs, size 912×1040, prompt file).
- End-to-end smoke test with a test image: `ingest` → `review` overlay → `tail` → `approve` → `build --mode latest` → `audit`. The text checks passed, the prefix was absent, the tail was inside the panel and the speaker was in the panel. The audit correctly reported PROOF for stand-in panels and a NOTE for 271 ppi. All test artefacts were removed afterwards.
- `compare`: our P012 proof, side by side with Opening p12, matches the sample's background, border, frame strokes, caption style and page number.

## Not verified yet (needs the real panel art)

- Generated image quality, character identity, hands and states. Each is checked at `review` time against the prompt's checklist.
- Final balloon-tail positions. They need `tail` on the real art.
- The final PASS audit of pages 9–13.
