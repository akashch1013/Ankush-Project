# AGENTS.md: ChandRush CH01 location images (Codex entry point)

This folder makes the **27 Chapter 01 location images** (`CH01_LOC_001.png` … `CH01_LOC_027.png`) defined by `CH01-LOCATION-IMAGE-GENERATION-DRAFT-02.docx`. Run every command from this folder.

**Read first:**
1. `skills/chandrush-backgrounds/SKILL.md`: how to run, in parallel, samples first;
2. `LOCATION-BIBLE.md` and `geography-guide.png`: the places.

**Your image tool** is the built-in `image_gen`:
1. `view_image` each reference the job lists, in order. Record 001 has none.
2. Call `image_gen` with the job's prompt **verbatim**, at the job's ratio and the largest size. For `mode: edit` jobs, edit Image 1.
3. Copy the **`savedPath` reported for that call** to the job's SAVE AS path.
4. `view_image` the result. Zoom on every label and count with `python3 bg.py zoom <file> x0,y0,x1,y1`, then tick the checks.

**Run in parallel:** spawn worker agents with `skills/chandrush-backgrounds/WORKER-PROMPT.md`, its placeholders filled. If you cannot spawn agents, run `bash run_codex_workers.sh 4 full`, or `3 samples`.

**The queue (`bg.py`):**

| Command | Purpose |
|---|---|
| `python3 bg.py check` | must say `check: OK` |
| `python3 bg.py claim --set samples\|full --worker W1 [--prefer LB]` | get one job |
| `python3 bg.py done <JOB> --worker W1 [--note "..."]` | keeps the native file, makes the 3840/3600-px accepted file |
| `python3 bg.py release <JOB>` | give a job back |
| `python3 bg.py pick <ID> <letter>` | **only** when the user has chosen a candidate |
| `python3 bg.py status [--set samples]` | progress |
| `python3 bg.py sheet [--set samples]` | contact sheets |

**Hard rules:**
- No people, hands or helpers.
- Print only the record's requested physical labels, as exact copy.
- Never attach the old `../../Locations` pack.
- One generation + at most two targeted fixes per job.
- Never pick candidates yourself; stop and show the user the sheet.
- Never start the full run before the user approves the samples.
- Never modify `../../Locations`, `../../Scripts`, `../../Charactors`, `../../Completed Samples`, `prompts/` or the draft.
