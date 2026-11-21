# CH03 agent guide (binding)

Work from `/home/akasdh/Desktop/Projects/ComicAgent/Tasks/BagroundGenTask`. Tool: `python3 ch03/ch03gen.py` (`--help`; commands: status, brief, lint, gen, fix, batch submit|wait, qc, zoom, compose).
Read first: `PROMPT-GUIDE.md` sections 1-5 and the writing rules (ignore its CH01 "known traps"), `spec/style.txt` (appended automatically), `ch03/rules.txt` (appended automatically), `ch03/work/global-rules.txt` (register's batch rules).
Copy the structure of the approved samples: `ch03/prompts/S01-B01.md` and `ch03/prompts/S06-B01.md`; look at `ch03/out/plates/S01-B01.png` and `S06-B01.png` and the approved plates of your parents.

## Authority
- The register (`ch03/briefs/<ID>.md`, from CH03-LOCATION-IMAGE-REGISTER-V06) is the authority. Manuscript text for context: `ch03/work/manuscript.txt` (grep it; it is huge, never cat it).
- Reference images in `ch03/refs/`: `parade-master.jpg` (= the M01 Parade Ground master; Ch02 render), `rear-passage-master.jpg` (M02), `moon-square-master.jpg` (M03), `costume-bench-ref.jpg`. They carry painted titles, white label boxes and arrows and sometimes a blue arch frame: tell the model to ignore them in every prompt.
- The user ordered dependency-aware generation: a dependent record attaches its approved parent plates (in the order listed by `brief <ID>`, Image 1 first). Describe exactly what each reference contributes and what must NOT leak (other states, wrong framing, labels).
- No people, children, helpers, animals or hands. Callouts name characters (Tara, Ahana, ...) only as standing positions: the plate shows empty floor. The only figure allowed is the flat painted clown picture on the picture stand (S01-B01 design).
- Titles and callouts are never in PROMPT (lint enforces). `compose` adds them.
- Do not put numbers/letters anywhere except the physical inscriptions the register states. Calculations stay concealed: no 36 cm, 40 cm, 150 cm answer unless the register lists it as visible in that record (S03-D04 plan text, S03-D14/D05 fitted 40 cm wheels are shown physically, not as text).

## Maths: avoid errors through the prompt
- Every count: digits and words, shape ("exactly 30 (thirty) ribbons in 3 (three) rows of 10 (ten)"), the total, and "Do not show" near-miss counts. Keep counted groups in a single flat layer with gaps so they can be counted.
- Every inscription: exact string, carrier, location, size at least about one eighth of frame width for a short label, true minus signs, a decimal full stop. Fractions/arrows exactly as in the register (e.g. `BODY 60 cm → 300 cm, ×5`).
- Story maths to keep consistent (never contradict, mostly concealed): pattern SLEEVE 12 cm, JACKET 18 cm; candidate sleeve tag 0.24 m (= 24 cm); original discarded sleeve 36 cm; 30 ribbons shared 2:3 = 12 (two groups of six) and 18 (three groups of six); model body 60 cm, wheel 8 cm, strap path 30 cm (one-fifth scale); real body 300 cm, final wheels 40 cm, final strap 150 cm; the board in Moon Square reads 40; bench raised ~40 degrees; seating board and the arch carry no other counts.
- Proportions: the trolley box rim is ~20 cm above paving (low); the arch casing is waist height for an 11-year-old (~1 m); the elephant wheels are visibly larger after replacement (40 cm vs the original small ones) and the model is a 1:5 copy.
- Design continuity: describe the established design of every repeating fitting (trolley, bench, elephant, stop lever housing, gallery stair, casing) in every record where it is visible, and attach the parent plate when it is prominent.
- Left/right: convert every register side to a SCREEN side for this camera before writing. The bay is physical-right of the Parade Ground from the Food Street threshold; the guest lane is physical-left; the arch is at the far end of the left lane; the near gallery stair is beside the elephant, towards Food Street.

## Loop per record
1. `brief <ID>`; Read every attached image and the parent plates at full size; write `ch03/prompts/<ID>.md` (## PROMPT / ## CHECKS (6-14 items) / ## CALLOUT PLAN); `lint <ID>` until ok; `gen <ID> --dry-run` once and read the sent prompt.
2. A record is only generated after all its `plate:` parents are `approved` in `ch03/state.json` (poll with `status`; sleep with `sleep 60` in short commands while waiting, do not burn calls). Write prompts while waiting.
3. Generate. Immediate `python3 ch03/ch03gen.py gen ID [ID2 ...]` (parallel threads inside one call) is allowed and preferred on the critical path; `batch submit <unique-name> ID ...` + `batch wait <name>` (50% cheaper) when you are not blocking anyone.
4. QC strictly like an art director: Read the plate; `zoom` every count, inscription, state; count items one by one; compare with parents (same design, same states that should persist) and masters (style). Check no label words/arrows/title beam leaked from a reference.
5. Fix one or two local defects with `fix <ID> "<one precise change naming the place, the wrong state and the right state>"`, or revise the prompt and `gen` again. Max 3 API calls per record (state.json counts; never `--force`). Geometry/count errors respond better to `fix` than to regen.
6. At the cap (3 calls): accept as-is per user rule: `qc <ID> pass --note "ACCEPTED AT CALL CAP: <defect>"`, add a line to `ch03/ACCEPTED-AT-CAP.md`, continue. Do not ask for a 4th call. Only accept at the cap; before the cap keep fixing real errors. Minor visual flaws may be ignored; huge mistakes (wrong counts, wrong text, wrong state, wrong side, missing key object, label leak) may not.
7. `qc <ID> pass --note "<what you counted/verified>"`, then write `ch03/callouts/<ID>.json` (format: see `ch03/callouts/S01-B01.json`; box and targets are fractions of the 1024x768 plate, following the register's position words and leader targets; target points must land ON the thing, boxes must not cover anything the register says stays visible), `compose <ID>`, Read the final and adjust.
Never touch another agent's records, `Ref/`, or `spec/`. Do not edit `ch03/records.json` (ask the coordinator; report problems).

## Quality
Set per record in records.json (medium/high/xhigh). Do not change. Never max.

## Report back (short)
Per record: verdict, calls used, maths checks verified (what you counted), final path, anything unresolved or contradictory in the register.
