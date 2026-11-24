---
name: comic-backgrounds
description: Stage 1 of the ChandRush comic pipeline. Makes empty location background plates for any chapter from its location register through the OpenAI Batch API (pipeline/imggen.py), samples first as a small batch. Use when the master or user asks for backgrounds/locations/plates of a new chapter or for a missing view. For CH01 Register V10 specifically, the older chandrush-backgrounds skill and locgen.py also exist.
---

# Stage 1: background plates

Work from `/home/abhay/F/Freelance/Ankush-Project/Tasks`. Read `LESSONS.md` (*All stages*, *Backgrounds*) first.

## Done already
- CH01: `BagroundGenTask/out/plates/` (32 approved, `locgen.py`).
- CH02: `BagroundGenTask/ch02/out/plates/` (24 approved).
- CH03: `BagroundGenTask/ch03/out/plates/` (23 approved).

Don't regenerate these. To change one of them, use that chapter's own runner and its batch commands only (`locgen.py fix --queue` + `batch`, `ch0Xgen.py batch submit`), never their immediate `gen`/`fix`.

## A new chapter (or a missing view)
1. Workspace `BagroundGenTask/ch0N/`:
   - `jobs.json` in the imggen schema (`python3 pipeline/imggen.py --help`), with `"project": "chandrush-ch0N-bg"`, `"size": "1024x768"`, `"quality": "high"`;
   - `prompts/<ID>.md`;
   - `briefs/` (register text per record, from `pipeline/textcheck.py dump`).
2. Prompts follow **`BagroundGenTask/PROMPT-GUIDE.md` sections 1–3**, the binding schema and writing rules:
   - the register is the authority;
   - no people, animals or hands;
   - physical inscriptions only, exact, true minus signs;
   - counts in digits and words;
   - screen sides resolved;
   - every reference image declared with "use / ignore".

   Paste the shared look from `BagroundGenTask/spec/style.txt` at the end of every PROMPT, and paste or adapt `BagroundGenTask/ch03/rules.txt` as the rules block. `## CHECKS` needs ≥ 6 items.
3. References:
   - the register's master images from `Reference/<chapter>/`, converted as attached;
   - for dependent views, `item:<parent>` (makes waves).

   Never attach spatial maps or diagram sheets (read them yourself, once, when a record needs them), and never anything in `archive/`. Master images are attached by `refs`; you don't need to Read them to attach them. Read one only when you must judge something specific about it.
   The briefs and the register are text: read only the records you are writing, never the whole `register.txt`.
4. Run `check`, then `dry-run` one item and read it.
5. **Sample batch**: the 2 most representative masters (`batch build ch0N-samples <ID> <ID>`, `submit`, wait). Report them to the master and **stop for the user's approval**.
6. Full run: `batch build ch0N-w1 --ready` → submit → wait, then QC.
   **Waiting:** start ONE `python3 pipeline/imggen.py --ws BagroundGenTask/ch0N batch wait <name>` with `run_in_background`, then end your turn; its completion notification wakes you (it fetches the results itself). Never poll with `sleep`, `pgrep`, `until`, `timeout`, Monitor loops or repeated `batch status`. Then `--ready` again for the next wave (and the queued fixes). Repeat until every item is approved or accepted.
7. QC from one QC/contact sheet of the batch's new plates: use the sheet the fetch prints if there is one, otherwise `montage -label '%t' BagroundGenTask/ch0N/out/<ID1>.png … -geometry 768x+8+8 -tile 3x BagroundGenTask/ch0N/batches/<batch>/qc.jpg` and Read that one file. `zoom` only plates that look wrong and the counts and inscriptions a CHECK needs. Never re-read an image already in your context; after a fix wave, QC only the re-generated/fixed plates. Then:
   - `qc <ID> pass --note "<verified>"`; or
   - `fix <ID> "<one precise change>"` (queued); or
   - revise the prompt + `qc <ID> fail --regen`.

   At 3 calls: `accept <ID> --note`.
8. Report: ids approved/accepted, plate paths, defects, and the cost (`imggen.py cost`).

No title bands or callouts are needed for the comic. The page uses the raw plate (`out/<ID>.png`).
