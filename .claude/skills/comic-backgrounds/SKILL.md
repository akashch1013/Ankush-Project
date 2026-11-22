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

   Never attach spatial maps or diagram sheets (read them yourself), and never anything in `archive/`.
4. Run `check`, then `dry-run` one item and read it.
5. **Sample batch**: the 2 most representative masters (`batch build ch0N-samples <ID> <ID>`, `submit`, `wait` in the background). Report them to the master and **stop for the user's approval**.
6. Full run: `batch build ch0N-w1 --ready` → submit → wait, then QC. Then `--ready` again for the next wave (and the queued fixes). Repeat until every item is approved or accepted.
7. QC: Read each plate, and `zoom` counts and inscriptions. Then:
   - `qc <ID> pass --note "<verified>"`; or
   - `fix <ID> "<one precise change>"` (queued); or
   - revise the prompt + `qc <ID> fail --regen`.

   At 3 calls: `accept <ID> --note`.
8. Report: ids approved/accepted, plate paths, defects, and the cost (`imggen.py cost`).

No title bands or callouts are needed for the comic. The page uses the raw plate (`out/<ID>.png`).
