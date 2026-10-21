# ChandRush Chapter 01: location images (Draft 02 workflow)

This folder makes the **27 location images** defined by **`CH01-LOCATION-IMAGE-GENERATION-DRAFT-02.docx`**, `CH01_LOC_001.png` … `CH01_LOC_027.png`. They cover Lantern Street and its working areas, the Old Blue Gate and the Food Street threshold. Every other story moment (all **142 visual beats** and **11 insets**) is made from these 27 at page stage by crops and small local edits; see `REUSE.md` and `RECORDS.md`. Several workers run **in parallel**, and **you approve samples first**.

| Step | What happens | Your part |
|---|---|---|
| S1 | **001** Lantern Street master: 3 candidates, text-only | pick 1 |
| S2 | **002** lift landing, **008** timing bench, **015** mirror alcove, **019** cube plinth: 2 candidates each, built from 001 | pick 4 |
| Run | the other 22 records, 4 workers at once | pick **024** (restored reverse master) when asked |
| Review | contact sheets, zoom-check of every label and count, at most 2 fixes per record | a quick look |

## Kickoff prompts: copy one box and send it

### Codex: sample round
```text
Work in /home/akasdh/Desktop/Projects/ComicAgent/Tasks/BagroundGenTask. Read AGENTS.md and skills/chandrush-backgrounds/SKILL.md.
Run the SAMPLE round only:
1) python3 bg.py check; stop if it reports errors.
2) Spawn 3 worker agents W1-W3, each given the text of skills/chandrush-backgrounds/WORKER-PROMPT.md with {WORKER}=W1..W3, {SET}=samples, {PREFER} empty, {ROUTE}=Codex built-in image_gen. They loop until claim says WAIT, PICK NEEDED or ALL DONE.
3) Run python3 bg.py sheet --set samples, show me output/_sheets/SAMPLES.png and STOP for my pick (e.g. "pick 001 B"). Run python3 bg.py pick <ID> <letter>, then repeat step 2 for the next sample jobs (002, 008, 015, 019) and STOP again for my four picks.
Never pick candidates yourself. Never attach the old ../../Locations images. Do not start the full run.
```

### Codex: full run (after your sample picks)
```text
Work in /home/akasdh/Desktop/Projects/ComicAgent/Tasks/BagroundGenTask. Read AGENTS.md and skills/chandrush-backgrounds/SKILL.md. The samples are approved.
Run the FULL set with 4 parallel worker agents using skills/chandrush-backgrounds/WORKER-PROMPT.md with {SET}=full, {ROUTE}=Codex built-in image_gen and these lanes: W1 {PREFER}=LB, W2 {PREFER}=TB,KB,HR, W3 {PREFER}=MR, W4 {PREFER}=CP,LS,GT,FS. Restart workers that stop on WAIT while python3 bg.py status still shows ready jobs.
When claim prints PICK NEEDED: 024, run python3 bg.py sheet, show me output/_sheets/CANDIDATES.png and STOP for my pick; after it, continue until ALL DONE.
Then review: python3 bg.py sheet, zoom-check every label and count listed in SKILL.md, make at most two targeted fixes per failing record, and report the totals, the REVIEW-NOTES.md items and the sheet paths.
(If you cannot spawn agents: bash run_codex_workers.sh 4 full)
```

### Claude Code + Higgsfield MCP
Start Claude Code from the **ComicAgent** folder, with Higgsfield connected:
`claude mcp add --transport http higgsfield https://mcp.higgsfield.ai/mcp`, or connect it under claude.ai Settings → Connectors.

Sample round:
```text
/chandrush-backgrounds samples
```
After your picks:
```text
/chandrush-backgrounds run --workers 4
```
If the skill doesn't load, paste this instead:
```text
Read /home/akasdh/Desktop/Projects/ComicAgent/Tasks/BagroundGenTask/CLAUDE.md and skills/chandrush-backgrounds/SKILL.md there. Using the Higgsfield MCP (GPT Image 2), first probe its tools and write HIGGSFIELD-NOTES.md, then run the SAMPLE round with 3 parallel worker sub-agents (WORKER-PROMPT.md, {SET}=samples, {ROUTE}=Claude + Higgsfield MCP). Show me output/_sheets/SAMPLES.png and wait for my picks. Do not start the full run.
```

### ChatGPT web (by hand, several tabs at once)
Use the same opening message in every tab:
```text
I will send location-image prompts one at a time, each with any reference images. For each, make exactly one image at the stated ratio and the largest size. Show no people, hands or figures, and no captions, arrows or watermarks. Print only the physical labels my prompt asks for, exactly as written. Use each reference image only in its stated role.
```
Then, for each image:
1. Run `python3 bg.py claim --set samples --worker TAB1` (later `--set full --prefer LB`, and so on).
2. Attach the listed images in order and paste the prompt.
3. Save the download to SAVE AS.
4. Run `python3 bg.py done <JOB> --worker TAB1`.

## Art direction for every image (your decision, 2026-10-20)

Every prompt now carries the same **art-direction overlay**, the `_style_overlay` in `records-meta.json`:
- an **illustration–reality hybrid**: photographic materials and real architectural construction, with an illustrator's composition and warmth;
- **grand, mystic and magical**: tall detailed architecture, deep layered space, moonlit haze, drifting silver-gold motes, a vast starry sky.

It is added at run time by `bg.py`, so it reaches every route (Codex, Higgsfield, API, ChatGPT) and survives re-importing a new draft. Change the wording there once and every future image follows.

**Guardrails built into the overlay:**
- Magic is atmosphere and craftsmanship only. It never lights an arch, track or indicator the record keeps dark.
- No words on signs except the record's labels.
- Exactly one full moon.
- Working areas stay clear and sharp.
- The Mumbai street outside the Gate stays ordinary.

**Per-record clarifications** (`clarify` in `records-meta.json`) fill gaps that a real output exposed. For example, 001: the square low mirror, the empty cart and a canopy against the wall.

## What Draft 02 changed in this workflow (2026-10-20)

Draft 02 is now the authority. It replaces three earlier decisions:

| Topic | Before | Now (Draft 02) |
|---|---|---|
| Image set | 70 plates, with every state pre-made | **27 records**; other states and crops are local edits at page stage (`REUSE.md`) |
| Lettering | all labels blank | **Exact physical labels printed** where a record asks (START/HOLD/CANCEL LAST CHANGE, lift scale +3…−8, wheel values, `45 BLUE GLASS LENSES`, `348 HOOKS`…, worker cards, `LIFT RHYTHM SUPPLIES MIRROR CUBE`, packing slip). Zoom-check every label; fix with a lettering edit. |
| Old Blue Gate | old image cleaned up | **V16 Gate** (026): weathered timber doors, service door in the left leaf, equipment door beyond the left pier, planter left, bench right, round glowing ornament |
| References | old pack used for style | **old pack excluded**; 001 is text-only and later images reference accepted records |
| Bench order | rack nearest the entrance | **timing nearest the entrance**, then kits, then hook rack (`geography-guide.png`) |
| Sizes | native output | native kept in `output/native/`; accepted file upscaled to **3840×2160 / 3600×2700 / 3600×2400** |

To switch any of these back, tell the agent; for the Gate, the archived v1 prompt still exists in `archive/`.

## Known source issue (for the author's Draft 03)

The draft's close views describe the bench **facing the right wall** with timing on the *left* and the rack on the *right* (008, 010, 012). In strict geometry, facing the right wall puts the entrance end on your *right*, so the schematic (timing at the entrance end) and the close-view wording are mirror images.

The workflow follows each record exactly as written. In 001 and 024 the bench details are too small to read, so the clash won't show. The author may want to align one or the other in the next draft.

## What's where

| File | What it is |
|---|---|
| `CH01-LOCATION-IMAGE-GENERATION-DRAFT-02.docx` | **the authority**: style, rules, locations, the 27 records, reuse notes |
| `prompts/CH01-LOC-RECORDS.md` | the 27 records imported from the draft (generated; don't hand-edit) |
| `LOCATION-BIBLE.md`, `geography-guide.png` | the draft's rules, style, geography and location descriptions (generated) |
| `REUSE.md` | how every other story moment is made from the 27 images (generated) |
| `RECORDS.md` | table of the 27 records + the beat → record map (`bg.py index`) |
| `records-meta.json` | workflow layer only: lanes, sample anchors, beats served |
| `bg.py` | import · check · claim · done · release · pick · status · sheet · index · zoom · urls · selftest |
| `skills/chandrush-backgrounds/` | the concurrent skill (`SKILL.md`) and the worker prompt (`WORKER-PROMPT.md`) |
| `run_codex_workers.sh` | starts N `codex exec` workers in parallel (fallback for multi-agent) |
| `output/CH01_LOC_###.png` | accepted images at the target size |
| `output/native/` | native generations (kept, per the draft) |
| `output/_candidates/`, `_sheets/`, `_logs/`, `_ledger.tsv` | candidates, contact sheets and zooms, worker logs, record of who made what with which references |
| `output/REVIEW-NOTES.md` | anything accepted with a known issue (`LETTERING:` = fix by hand at page stage) |
| `HIGGSFIELD-NOTES.md` | the Higgsfield recipe recorded in the sample round |
| `archive/v1-70-plates/` | the previous 70-plate workflow (kept for reference) |

## Useful commands

```bash
python3 bg.py check                 # must say check: OK
python3 bg.py status --set samples  # sample-round progress
python3 bg.py status                # full-run progress per lane
python3 bg.py sheet --set samples   # output/_sheets/SAMPLES.png
python3 bg.py sheet                 # ALL.png + one sheet per lane (+ CANDIDATES.png when a pick is due)
python3 bg.py zoom output/CH01_LOC_012.png 0.1,0.3,0.9,0.7   # check labels at full resolution
python3 bg.py import CH01-LOCATION-IMAGE-GENERATION-DRAFT-03.docx   # when a new draft arrives (then: check, index)
python3 bg.py selftest              # proves parallel claims, gates and sizing work (scratch copy)
```

**Credits:** about 40–50 generations in total, counting 27 records, 7 extra anchor candidates and fixes.
