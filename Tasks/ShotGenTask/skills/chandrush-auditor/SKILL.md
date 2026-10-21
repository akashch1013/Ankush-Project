---
name: chandrush-auditor
description: Audit exported ChandRush pages against the V07 manuscript and the production rules, then report honestly. Check exact text coverage and order, that nothing non-printable or no speaker prefix is printed, embedded fonts, page size, art approval status, effective ppi and balloon tails; give each page PASS / REVIEW / PROOF / FAIL and write the batch report. Use whenever ChandRush pages are finished, someone asks whether pages are correct, ready, final or print-ready, or before handing a batch to the user.
---

# ChandRush auditor

Your job is to say what is true about the exported files, not what the plan intended. Audit the PDF itself, because text can exist in a project file and still be missing from the export.

## Steps

1. **Run the audit.** Run `python -m pipeline audit`. For proof builds, use `--proof standin|placeholder|latest`. Read `output/AUDIT.md`:
   - **BLOCK:** text, font, size or tail problems. These must be fixed. Send them back to the assembler, or to the director if the layout is at fault.
   - **PROOF:** a panel still uses stand-in art.
   - **REVIEW:** a REVIEW_LATER panel, a tail set on old art, or a resolution below 150 ppi.
   - **NOTE:** information, for example ppi below 300 for review-size art.
2. **Look at every exported PNG yourself.** The audit cannot judge picture content (identity, hands, states). Confirm the reviewer's approvals still hold now the art is on the page with its text.
3. **Run `python -m pipeline status`** for the panel table.
4. **Report to the user**, in this order:
   - which files were produced (batch PDF, page PDFs, PNGs);
   - each page's audit status, using the exact word: PASS, REVIEW, PROOF or FAIL;
   - every REVIEW_LATER panel and its note;
   - the effective ppi range;
   - anything not verified;
   - the one next action.
5. **Stop.** Wait for the user's review before any new batch.

## Wording rules

- Don't call a page final or print-ready on the strength of a command succeeding, a plan or a prompt.
- "PASS" means the batch is ready for the user's review. "Print-ready" also needs the printer's specification (`guide/06_ASSEMBLY_AND_AUDIT.md`).
