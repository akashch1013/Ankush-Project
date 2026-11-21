# FLOW: ChandRush CH01 location images (Register V10)

This is the procedure for making the **32 location images** in `Ref/CH01-LOCATION-IMAGE-REGISTER-V10.docx`. The tool is `locgen.py`. Run every command from this folder.

The flow has two rounds:
1. **Sample round:** 1–2 plates through immediate API calls. The user approves the look.
2. **Full run:** every other record through the OpenAI **Batch API**, which costs 50% less, one batch per wave.

---

## 1. Sources and what each one decides

| Source | Decides | Sent to the image model? |
|---|---|---|
| `Ref/CH01-LOCATION-IMAGE-REGISTER-V10.docx` | **The authority** for each record: camera, construction, state, appearance, exact title, exact callouts and the output filename | No. It is turned into prompt text |
| `Ref/CH01-SPATIAL-AUTHORITY-MAP-FINAL.png` | Position, adjacency, direction and levels | **Never.** It is a text diagram that the model would copy. The agent reads it while writing prompts |
| `Ref/Cube plinth beneath lantern towers.png` | **Lantern Street master from Entry Court** (the filename is misleading) | Yes, as `master:lantern` |
| `Ref/Old blue gate, frontal night view.png` | **Old Blue Gate exterior master** | Yes, as `master:gate` |
| `Ref/Intact Brass Bowl by Wheel.png` | **Food Street master from Lantern Street** | Yes, as `master:food` |
| `Ref/CH01-PANELIZED-MANUSCRIPT-V02.docx` | Supporting story and location context. **The register wins any conflict** | No. Its location text goes into each brief |
| `spec/plan.json` | The references attached to each record (in order), its wave and its mode | n/a |
| `spec/style.txt`, `spec/rules.txt` | The shared look and the production rules | Yes, appended to **every** prompt by the script |

Never use the old `../../Locations` pack, the WhatsApp sheets or anything in `archive/`. The three masters and this run's approved plates are the only images that go to the model.

## 2. What one image is

`out/final/<register filename>.png`, 1024 px wide, has two parts:
- **Scenic frame:** 1024×768 (4:3), made by `gpt-image-2.5-sunburst`. It contains only the scene and its *physical* inscriptions, such as `START`, `−8`, `45 BLUE GLASS LENSES` or the five indicator labels.
- **Clarity pass:** before drawing, `compose` applies a free local-contrast and sharpening pass to remove the model's slight haze. The raw plate in `out/plates/` stays untouched and is what later records use as a reference. Use `--no-clarity` to skip it.
- **Title band and callouts:** added by `compose`. The register's exact two-line title goes in a slim ivory band **above** the frame. The register's exact callouts are drawn as small dark-indigo text on ivory with fine short leader lines.

The image model therefore never paints a title, a callout, an arrow or any other non-physical lettering. This has four effects:
- Lettering is exact by construction.
- No API call is ever spent fixing a typo in a label.
- Every plate stays clean, so it can be reused as a reference or an edit base for later records.
- The typography is the same across all 32 images.

## 3. API settings (decided; do not change without the user)

| Setting | Value | Why |
|---|---|---|
| Model | `gpt-image-2.5-sunburst` | OpenAI's precision variant of GPT Image 2.5, made for exact edits and detail. Flare is faster but looser. |
| Endpoint | `/v1/images/edits` | Every record has at least one reference image. References are sent as JPEG data URLs in `images: [{image_url}]`. The immediate path and the batch path send the **same JSON body**, so the samples are a true test of the batch. |
| Quality | `high`; `xhigh` for 8 hard records | The Images API has no separate reasoning setting for this model; `quality` is its effort dial (low → medium → high → xhigh → max). **`high`** is the default. **`xhigh`** is set per record in `spec/plan.json`, only where dense exact inscriptions or exact counts make it genuinely hard: S01-B01, S01-D02, S01-D03, S01-D04, S05-B01, S06-D02, S07-B01, S07-D01. **`max` is never used without the user's approval** (`--allow-max`). It costs about 4× `high` (4,815 output tokens per image, measured) and took 2–17 minutes per call in the sample round. |
| Size | `1024x768` | 1K, 4:3. Both edges are multiples of 16 and the size is within the model's pixel limits. |
| n | 1 | One candidate per call. Quality comes from the prompt, not from rolling dice. |
| Call cap | 3 per record | One generation plus at most two fixes or regenerations. After that, stop and ask the user. |

**Where the reasoning happens:**
- Claude (Opus at xhigh effort) does the thinking about the image while writing each prompt.
- The image model works at `high`, or at `xhigh` for the records listed above.
- Routing through the Responses API with a GPT reasoning model was rejected. That model rewrites the prompt (`revised_prompt`), which breaks exact inscriptions, and its reasoning tokens add cost.

**Escalation (only when it is really hard):**
- If a record at `high` fails QC *because of rendering precision*, such as garbled small inscriptions or a miscounted grid that the prompt states clearly, its regeneration may go to `xhigh` once. Set `"quality": "xhigh"` on that record in `spec/plan.json` and tell the user.
- Prompt problems are fixed in the prompt, never by raising the quality.
- `max` only with the user's explicit approval.

**Measured and expected cost (1024×768):**

| Quality | Output tokens | Immediate | Batch |
|---|---|---|---|
| `high` | ~1,200 (measured in the v2 tests) | ~$0.06 | ~$0.03 |
| `xhigh` | not measured yet; estimated ~2,500 | ~$0.10 | ~$0.05 |
| `max` | 4,815 (measured in the samples) | ~$0.17 | ~$0.08 |

- The remaining 30 records by batch come to about **$1–1.5**, fixes included.
- `python3 locgen.py cost` reports the actual figures.

## 4. The waves

Later views must reuse the exact designs established by earlier ones: the lift controller, the bird device, the mirror frame, the cube station. So a record can attach **this run's approved plate** of another record. `spec/plan.json` declares these dependencies.

| Wave | Needs | Records |
|---|---|---|
| 1 | masters only | M01-D01, M01-D04, S01-B01, S03-B01, S04-B01, S05-B01, S06-B01, S07-B01, M02-D01, M03-D01 |
| 2 | approved wave-1 plates | S01-D02, S01-D03, S02-B01, S03-D01, S04-D01, S04-D02, S05-D01, S06-D01, S06-D02, S07-D01, S07-D02, S07-D04 |
| 3 | approved wave-2 plates | M01-D02, M01-D03, S01-D01, S01-D04, S01-D05, S02-D01, S03-D02, S06-D03, S06-D04, S07-D03 |

**Modes:**
- `derive`: a new camera on the same place, built from the references.
- `state-edit`: the **same camera** as Image 1 with only the state changed. The register gives these pairs identical camera text:
  - S01-D03 → S01-D04
  - S02-B01 → S02-D01
  - S03-D01 → S03-D02
  - S06-B01 → S06-D01
  - S07-B01 → S07-D01

## 5. Per-record loop (every record, both rounds)

1. **Find the data.** Run `python3 locgen.py brief <ID>`. The brief has:
   - the register record verbatim;
   - the exact title and callouts, which you must **not** put in the prompt;
   - the references to attach, in order, each with its role;
   - the records that will later reuse this plate;
   - the register's global rules;
   - the manuscript's location text.
2. **Look at everything.** Read every attached reference image, and for plates read the approved plate itself. Read the spatial map. Optionally `grep -n` in `work/manuscript.md` for the record's scenes.
3. **Think before writing.**
   - Convert every physical left or right into a screen position *for this camera*. Check it against the map.
   - List every count, on/off state, physical inscription and absent object.
   - Decide what each reference contributes and what must **not** leak from it, such as annotation words, other states or the wrong framing.
   - Check what earlier and later states must not appear.
4. **Write `prompts/<ID>.md`** following `PROMPT-GUIDE.md`. It has three sections:
   - `## PROMPT`: sent verbatim, with `spec/style.txt` and `spec/rules.txt` appended;
   - `## CHECKS`: the QC list;
   - `## CALLOUT PLAN`.
5. **Validate.** Run `python3 locgen.py lint <ID>` until it says ok. Then run `python3 locgen.py gen <ID> --dry-run` and read `out/tmp/<ID>-gen-prompt.txt` once, end to end, as the model will see it.
6. **Generate.**
   - Sample round: `python3 locgen.py gen <ID> [<ID2>]`. Two records run in parallel.
   - Full run: `batch build|submit|wait` (see section 7).
7. **QC like a strict art director.**
   - Read the plate.
   - Use `grid <ID>` and `zoom <ID> x0,y0,x1,y1` on every inscription, count and state in CHECKS.
   - Compare with the references for continuity and with the masters for style.
8. **Verdict:**
   - **Pass:** `qc <ID> pass`. The plate becomes `work/refs/plate-<ID>.jpg` for later waves.
   - **Fix:** one to two local defects on a correct composition, such as a wrong digit, a lamp on that should be off, an extra object or a stray letter. Run `fix <ID> "<one precise change>"` (immediate) or add `--queue` (batch). Name the location, the wrong state and the right state in the instruction.
   - **Regen:** the camera or layout is wrong, a side is swapped, the design contradicts the register, the style misses the masters, or there are more than two defects. Revise the prompt first, then `qc <ID> fail --regen` and generate again.
   - Text in the title band or callouts is **never** a reason for an API call.
9. **Annotate.**
   - Run `callouts <ID>`, which writes `callouts/<ID>.json` with the register's text and suggested box regions.
   - Read `grid <ID>` and set every `targets` point. Follow the register's wording exactly: a callout "to" a thing ends on it; one "beside" a thing ends next to it. Adjust each `box` so leaders stay short and nothing the register says must remain visible is covered.
   - Run `compose <ID>` and Read the final image. Repeat until it is right.

## 6. Sample round (immediate API)

- **Records:** `S01-B01` and `M01-D01`, from `plan.json → samples`.
  - S01-B01 tests close detail, many physical inscriptions and three callouts. It is also the design anchor for 5 later records.
  - M01-D01 tests fidelity to the Lantern Street master in a wider view.
- **Steps:** run `build` and `check`, then the per-record loop for both. Make one `gen` call with both IDs, then QC, fixes if needed, `qc pass`, callouts and compose. Finish with `sheet --samples` and `cost`.
- **Then stop.** Report to the user and wait. Don't start the batch run. Don't generate any other record.

## 7. Full run (Batch API, 50% off)

For each wave (1, then 2, then 3):
1. Write and lint prompts for every record in the wave that has none (`status` lists them). Read the approved sample prompts first; they set the quality bar.
2. Run `batch build --wave N`. It includes records with status `todo` or `regen` whose dependencies are approved, plus queued fixes. Check the listing.
3. Run `batch submit`.
4. Run `batch wait <name>` **in the background**. It polls every 60 s and fetches when the batch ends. Batches usually finish well within the 24 h window.
5. QC every new plate (section 5, steps 7–8). Queue fixes with `fix --queue`, and mark prompt-level failures `qc fail --regen` after revising the prompt.
6. Run `batch build --wave N` again for the fixes and regens. Repeat until the wave is approved.
   - A record that hits the call cap goes on the report for the user. Records that depend on it stay blocked; everything else continues.
7. Move on to the next wave. Its references are this wave's approved plates.

After wave 3:
- Annotate and compose every approved record.
- Run `sheet` (all), `cost` and `status`.
- Report to the user.

**Immediate `gen` during the full run:** allowed only when the user approves it for a specific record.

## 8. Commands

```
python3 locgen.py build                          # parse sources -> work/records.json, work/briefs/, work/refs/
python3 locgen.py check                          # must say: check: OK
python3 locgen.py brief S01-B01                  # all the data for one record
python3 locgen.py lint S01-B01 | lint all        # prompt validation (errors block spending)
python3 locgen.py gen S01-B01 M01-D01 [--dry-run]
python3 locgen.py fix S01-B01 "The last-change window shows a dash; make it blank." [--queue]
python3 locgen.py qc S01-B01 pass | fail --note "..." [--regen]
python3 locgen.py batch build --wave 2 | submit | wait | status | fetch | cancel | list
python3 locgen.py grid S01-B01 | zoom S01-B01 0.6,0.2,0.9,0.5
python3 locgen.py callouts S01-B01 ; python3 locgen.py compose S01-B01
python3 locgen.py status | sheet --samples | sheet --wave 2 | sheet | cost
```

## 9. Files

| Path | What it is | Who writes it |
|---|---|---|
| `prompts/<ID>.md` | PROMPT / CHECKS / CALLOUT PLAN | the agent |
| `callouts/<ID>.json` | callout boxes and leader targets | the agent (skeleton from `callouts`) |
| `out/plates/<ID>.png` | current scenic frame. Earlier versions are in `out/plates/history/` | locgen |
| `out/final/<filename>.png` | **deliverable** | `compose` |
| `out/state.json`, `out/usage.tsv` | status, attempts, tokens and cost per call | locgen |
| `out/batches/<name>/` | manifest, sent prompts, batch object, results | locgen |
| `out/sheets/` | contact sheets | `sheet` |
| `work/` | rebuilt by `build`: records, briefs, manuscript text, JPEG references | locgen |

## 10. Hard rules

- The register is the authority. Follow each record as written, and report any contradiction you find to the user instead of improvising.
- No people, helpers, animals or hands in any plate. The callouts mark where characters go later.
- Only physical inscriptions are painted. They must be exact, letter for letter, with true minus signs (−).
- Nothing is attached except the plan's references. Never attach the spatial map or the old location pack.
- At most 3 API calls per record without the user's approval. `n` is always 1.
- Never start the full run before the user approves the samples.
- Never edit `Ref/`. Edit `spec/` only to fix a plan error, and tell the user.
