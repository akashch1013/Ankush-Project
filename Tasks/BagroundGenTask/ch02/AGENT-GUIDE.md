# CH02 agent guide (binding)

Work from `/home/akasdh/Desktop/Projects/ComicAgent/Tasks/BagroundGenTask`. Tool: `python3 ch02/ch02gen.py` (see its `--help`).
Read first: `PROMPT-GUIDE.md` (sections 1–5 and the writing rules; ignore its CH01-specific "known traps"), `spec/style.txt`, `spec/rules.txt` (appended automatically).
Look at: the three approved samples' prompts `ch02/prompts/L02_B.md`, `L03_D.md`, `L05_A.md` (copy their structure) and the approved plates in `ch02/out/plates/`.

## Authority
- The register (`ch02/briefs/<ID>.md`, from CH02-LOCATION-IMAGE-REGISTER-V04) is the authority. Manuscript text for context: `ch02/work/manuscript.txt` (grep it).
- **User rule (overrides the register):** no numbers or letters on any jug, urn or bottle. Levels are shown only by unlabelled tick marks; the liquid level must still sit at the exact value.
- No people, children, helpers, animals or hands. Callouts mention them; the plate shows only the empty floor.
- Titles and callouts are never in PROMPT (lint enforces). `compose` adds them.

## Dependencies
- `brief <ID>` lists the attachments in order. Image 1 is the approved parent plate when the record has one; describe exactly what to keep from it (design of fittings, materials, camera if state-edit) and what changes.
- Dependents are generated only after their parent is `qc pass`. Do it wave by wave within your group.

## Maths: avoid errors through the prompt
- Every count is written as digits and words, with the grid shape ("exactly 20 (twenty) packs in 4 (four) rows of 5 (five)"), plus the total, plus "Do not show" the near-miss counts (19/21).
- Every physical inscription is listed with its exact string, carrier, location and size (at least about one fifteenth of the frame width). Fractions use a clean bar. Decimals use a full stop.
- Sample-round failures: the model added an 8th weight to a row of 7, made a 5×5 grid as 4×5, and put liquid levels at the wrong ticks. So state rows × columns, keep counted groups in single flat layers with clear gaps, and give each level as a position between named ticks ("exactly at the third of four ticks").
- Check consistency with the story maths: 25+15=40 → 20/20 → 12/12 (24 left); 7×¼=7/4=1¾ kg; one full dosa = 1/6 kg, so the stop is set at ⅙ kg; trial charge 2/15 kg; ¾ L = 0.75 L; trolley lower shelf MAXIMUM LOAD 4.5 kg, tray 0.5 kg.

## Loop per record
1. `brief <ID>`; Read every attached image; write `ch02/prompts/<ID>.md` (## PROMPT / ## CHECKS / ## CALLOUT PLAN); `lint <ID>` until ok.
2. Generate through the Batch API: `batch submit <unique-name> ID ID ...` then `batch wait <name>` (run wait with run_in_background and wait for it to finish; batches usually finish in minutes).
3. QC each plate strictly: Read it, `zoom` every count, inscription, level and state, and count items one by one.
4. Fix one or two local defects with a batch fix: `batch submit <name> "ID=<one precise change>"`, or regenerate after revising the prompt. Max 3 API calls per record (state.json counts them). Never use --force. If still wrong after 3, stop and report it.
5. `qc <ID> pass`, then write `ch02/callouts/<ID>.json` (format: see `ch02/callouts/L03_D.json`; box and targets are fractions of the 1024×768 plate, following the register's position words and leader targets) and `compose <ID>`. Read the final. No leader or box may cover what the register says must stay visible.

## Quality
Set per record in records.json: xhigh only for dense counts/inscriptions, high for normal, medium for simple views. Do not change it. Never use max.

## Report back
Per record: verdict, calls used, maths checks verified (with what you counted), final path, and anything unresolved or contradictory in the register.
