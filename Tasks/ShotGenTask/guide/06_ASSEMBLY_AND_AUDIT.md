# 06 · Assembly and audit — from approved art to checked pages

## Build modes

| Command | Uses | Output | Purpose |
|---|---|---|---|
| `python -m pipeline proof` | grey placeholders; text boxes outlined | `output/proofs/*-LAYOUT-PROOF.*` (150 dpi) | prove the text fits before any art exists |
| `python -m pipeline build --mode standin` | location images as darkened, labelled stand-ins | `output/proofs/*-STANDIN-PROOF.*` | preview composition and caption placement |
| `python -m pipeline build --mode latest` | approved art, else the newest unapproved version, else stand-ins | `output/pdf/*-LATEST.pdf`, `output/png/*-LATEST.png` | check art in place while still reviewing |
| `python -m pipeline build` (final) | approved art; stand-ins only where none is approved | `output/pdf/CH01-P0xx.pdf`, `output/CH01-P0xx-P0yy-REVIEW.pdf`, `output/png/*.png` at 300 dpi, contact sheet | the batch for user review |

- Every build writes `output/<name>.build.json`. It records, per panel, the art file and its sha256, the visible crop in pixels and the effective ppi. Per text item it records the lines, the box and the tail geometry. The audit reads this file.
- The build stops on errors: text not placed, placed twice, overflowing, overlapping or too close to the trim; layout and manuscript panel order disagreeing; a missing tail target. `--force` writes the files anyway, for inspection only.

## Fine-tuning after the art arrives

| Need | Command |
|---|---|
| See the crop, the reserved text zones, the tail target and a 0–1 grid on the art | `python -m pipeline review --panel <id>` |
| Keep a different part of the image centred, or tighten the shot | `python -m pipeline frame --panel <id> --focus 0.55,0.40 --zoom 1.1` |
| Aim a balloon tail | `python -m pipeline tail --panel <id> --at 0.62,0.38` |
| Move a caption or balloon | edit `at` / `w` / `max_w` in `pages/CH01-P0xx.layout.json`, then `build` |
| Compare with the sample look | `python -m pipeline compare --page 12 --sample 12` |

The tail target is a point in clear space **just beside** the speaker's mouth. The tail stops 8 pt short of it, so it never touches the face. Each target records the sha256 of the art it was set on. If the art is replaced, the build warns until you set it again.

## What `audit` checks (on the exported PDF)

| Check | Severity if it fails |
|---|---|
| Page is exactly 864 × 648 pt | BLOCK |
| Text uses only the four Source fonts, all embedded | BLOCK |
| Every printable block appears **exactly once**, word-for-word, in manuscript order | BLOCK |
| Speaker prefixes are not printed (balloons) | BLOCK |
| No extra text besides the page number | BLOCK |
| Nothing non-printable printed (panel IDs, block IDs, filenames, markers, "Narration" labels) | BLOCK |
| Each balloon has a tail whose tip lies inside its panel, and the named speaker is drawn in that panel | BLOCK |
| Tail aimed on the final art, not a layout default | PROOF while art is pending, REVIEW otherwise |
| Every panel has approved art with PASS or PASS_WITH_LOCATION_EXCEPTION | PROOF (stand-in) / REVIEW (REVIEW_LATER) |
| Effective resolution ≥ 300 ppi | NOTE (≥150) / REVIEW (<150) |
| Unused fonts in the page resources | NOTE |

Page status:
- **FAIL** if anything is BLOCK;
- else **PROOF** if any stand-in art remains;
- else **REVIEW** if any REVIEW item;
- else **PASS**.

Results go to `output/AUDIT.md` and `output/AUDIT.json`. Proof builds are audited with `audit --proof standin|placeholder|latest`.

The audit cannot judge picture content: identity, hands, states. That is done by eye at `review` time, against the prompt's checklist, and it is recorded by `approve`.

## Deliverables of a finished batch

- `output/CH01-P0xx-P0yy-REVIEW.pdf`, the batch PDF for the user, plus `output/pdf/CH01-P0xx.pdf` per page.
- `output/png/CH01-P0xx.png`: 3600 × 2700 previews at 300 dpi.
- `output/CH01-P0xx-P0yy-CONTACT-SHEET.png`
- `output/AUDIT.md`, `output/STATUS.md`, `state.json` (the complete record) and `*.build.json`.
- The editable source: `pages/*.contract.json`, `*.layout.json`, `art/**`, `design/`, `fonts/` and `pipeline/`. Any page rebuilds with one command.

## Print notes (not done yet, and that is intentional)

- Review exports are RGB, zero bleed, with fonts embedded and text and vectors kept live.
- Effective image resolution is reported per panel. Raster art made at the preferred sizes lands at about 270–300 ppi.
- Before printing, get the printer's specification: trim, bleed, safe area, colour profile and PDF standard (e.g. PDF/X-4). Then add a print export. Never relabel an ordinary PDF as PDF/X.
