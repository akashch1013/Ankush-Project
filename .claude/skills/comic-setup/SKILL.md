---
name: comic-setup
description: Stage −1 of the ChandRush comic pipeline. Turns a chapter folder the author dropped into Tasks/Reference/ (panelized manuscript .docx, location register .docx, reference images) into a ready workspace for every other agent. It splits the manuscript into pages, indexes the cast, locations and register records, maps master images and manuscript locations to register records, triages the manuscript maths pre-scan, scaffolds the background and panel workspaces, and writes PdfSheetsGenTask/<CHxx>/chapter.json + SETUP-REPORT.md. Free: no image calls. Use when the author adds a chapter, gives a new manuscript/register version, or asks to "set up chapter N". Arguments: [CHxx | Reference folder name] (none = every new or stale chapter).
---

# Stage −1: chapter setup

Work from the repo's `Tasks/` folder. Tool: `python3 pipeline/setup_chapter.py` (`--help`). You make **no image calls** and never edit `Reference/` or `../Charactors/`.

## What the author gives
A folder in `Reference/` (any name without the word "old", e.g. `Chap4/`) holding:
- `CHxx-PANELIZED-MANUSCRIPT-Vnn.docx` (required; the chapter id comes from this file name);
- `CHxx-LOCATION-IMAGE-REGISTER-Vnn.docx` (needed for backgrounds);
- reference images (masters of the register, maps, props).

A new version is a new file in the same folder (`…-V03.docx`). The highest version wins.

## Procedure
1. `setup_chapter.py scan` shows every chapter folder and its state: `new`, `stale` (a new version arrived), `needs-agent` or `ready`. With no argument, set up every `new` and `stale` chapter, one at a time.
2. `setup_chapter.py prep <CHxx|folder>`. It is free and idempotent. It writes, under `PdfSheetsGenTask/<CHxx>/`:
   - `manuscript.txt`, `register.txt`, `src/Pxxx.txt` (one per manuscript page), `survey.txt`;
   - `index.json` (per page: panels, speakers, characters, location groups);
   - `mathscan.txt` (every arithmetic statement in reader text, evaluated exactly);
   - `pages.json` header (only if missing);
   - `chapter.json`, the manifest.

   It also scaffolds `FInalChangesTask/<CHxx>/jobs.json`, and `BagroundGenTask/ch0N/` (jobs.json + one brief per register record) when the chapter has no plates yet. Read its printed summary, then `setup_chapter.py check <CHxx>` for the open items.
   Never `cat` `chapter.json`, `manuscript.txt` or `index.json` whole. Use `python3 -c` / `grep` for the fields you need.
3. **Masters** (status `masters`). For each master in `chapter.json → register.masters` (name + identity text), Read the reference images in `sources.images` and pick the one that shows it. Record it with `setup_chapter.py master <CHxx> "<name>" "<image path>"`. Maps, diagram sheets and prop photos are not masters; list them in the report as "read-only references, never sent to the image model". If a master has no image, `mark` it with a note. For a chapter whose plates are all approved this is bookkeeping, so keep it quick.
4. **Locations** (status `locations`). For each group in `chapter.json → locations` (e.g. `CH02 L03` "Food Street — Packing Bench…"), pick the register records that show that place (the register's `# Image index`: id, view, master). Record them with `setup_chapter.py locate <CHxx> "<group>" <ID> [<ID> …]`. A group may map to several records (states/views of one place); the master later picks one per panel.
   - If the manuscript has no location ids (CH01 style), group by `[SceneHeading]`: `locate <CHxx> "Scene 03 …" <IDs>`, or `mark <CHxx> locations "<why>"`.
   - A group with no matching record means a missing view: list it in the report as **needs a new plate** (bg-artist).
5. **Characters** (status `characters`). `chapter.json → cast` lists every name with its sheet (or none), pages and speaking lines. For each speaker without a sheet:
   - background roles (helpers, assistants, "girl in green") are painted from the manuscript's description, with no sheet. Note it.
   - a named recurring character (several pages) needs a reference sheet. **Ask the author** in the report, quoting the manuscript's appearance description (grep `manuscript.txt`). Never create files in `Charactors/`.

   Then `mark <CHxx> characters "<decision per name>"`.
6. **Maths** (status `maths`). For every `FAIL` line in `mathscan.txt`, read the line in `src/Pxxx.txt` and classify it:
   - **deliberate**: a wrong claim the text asks students to correct, or an "incorrect argument";
   - **artefact**: the scan cut the statement (words, a ratio, a leading sign, units such as £1.50 = 150p);
   - **manuscript error**: the maths really is wrong. Quote it exactly with its page.

   Also skim the `SKIP` lines that look like answers. Never "fix" the manuscript. Errors go to the author, and those pages are blocked until answered. Then `mark <CHxx> maths "<n deliberate, n artefact, errors: P0xx …>"`.
7. **New version** (`chapter.json → changes`, `CHANGES.md`): if pages that are already built or planned changed, list them. They must be re-planned (`pages.json` entry), rebuilt and re-checked. If `pages.json` already has pages, update `sources.manuscript`/`register` to the new files and run `python3 pipeline/textcheck.py plan PdfSheetsGenTask/<CHxx>/pages.json`. Report every mismatch with its page (the master re-plans those pages; you don't).
8. **Backgrounds** (only if `status.plates` is not ok). In `BagroundGenTask/ch0N/jobs.json`, set each item's `refs` to its master image (from step 3, path relative to `Tasks/`; `item:<parent>` for records the register says derive from another record). Then run `python3 pipeline/imggen.py --ws BagroundGenTask/ch0N check`. Missing prompts are expected, since the bg-artist writes them. Name the 2 most representative masters as the sample pair for the bg-artist.
9. Write `PdfSheetsGenTask/<CHxx>/SETUP-REPORT.md` (short, overwrite it):
   ```
   # CHxx setup: <date> (<manuscript file>, <register file>)
   Pages: N (kinds) · Records: N (plates n/N) · Cast: … · Maths scan: n hold, n flagged
   ## Needs the author        (questions, manuscript maths errors, missing character sheets; or "nothing")
   ## Needs new art           (missing plates/views → bg-artist sample pair; or "none")
   ## Changed pages           (new version only)
   ## Decisions               (masters, location map, characters, maths triage: one line each)
   ## Next                    (e.g. "/comic-master plan CHxx" or "bg-artist samples L01_A L03_C first")
   ```
10. `setup_chapter.py mark <CHxx> agent_review "<one line>"`, then `check <CHxx>`. It is `ready` once every item is ok. Items that wait on the author stay open: say so.

## Report (to the master or the user)
Paste the "Needs the author", "Needs new art" and "Next" sections of SETUP-REPORT.md, plus the `check` output. Keep it under 20 lines.
