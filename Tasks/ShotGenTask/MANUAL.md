# MANUAL — how to use Approach1

This manual covers everything you need to make the ChandRush pages, in one file. Run every command from inside the `Approach1` folder:

```
cd "C:\Users\Akash Chaudhari\Desktop\Projects\ComicAgent\Approach1"
```

There are 14 panel images to make (pages 9–13). The pipeline does everything else: text, balloons, layout, PDF and checks.

---

## 0. Fastest way (30 seconds of your time)

1. Open **Codex** in the `Approach1` folder.
2. Paste the **Codex prompt** from section 2, below, and send it.
3. When Codex finishes, open `batch\P009-P013\output\CH01-P009-P013-REVIEW.pdf`.

---

## 1. One-time setup

```
pip install -r requirements.txt
python -m pipeline status
```

If `status` prints a table, you're ready. The fonts are already in `fonts/`.

---

## 2. Option A — Codex does everything (recommended)

Codex uses its **built-in image tool**, so no API key is needed. Codex gets each task by running `python -m pipeline next --codex`. That command prints, for one panel:
- the reference images to look at;
- the **exact prompt**;
- the checklist;
- the next commands to run.

`python -m pipeline ingest --from-codex` then takes the image Codex just made from `~/.codex/generated_images` and puts it in the right place.

### Codex prompt (copy everything in the box and send it to Codex)

```text
You are working in C:\Users\Akash Chaudhari\Desktop\Projects\ComicAgent\Approach1.
Read AGENTS.md first. Then finish batch P009-P013 by yourself; only ask me if something is truly blocked.

Repeat this loop until the command prints "ALL PANELS DONE":

1. Run:  python -m pipeline next --codex
   It prints ONE task, either GENERATE or REVIEW, with numbered steps. Do exactly what it says.
   - GENERATE:
     a) view_image every reference image it lists, in the order given (Image 1, Image 2, ...).
     b) Call your built-in image_gen tool with the exact text between -----BEGIN PROMPT----- and -----END PROMPT-----, unchanged, at the aspect ratio it states.
     c) Run:  python -m pipeline ingest --from-codex
     If it says images were already generated for this panel, do not generate again; run
     python -m pipeline ingest --from-codex --all-new
   - REVIEW:
     Run  python -m pipeline review --panel <ID>
     view_image the overlay PNG it prints and the art PNG, then check every "Accept only if" line honestly.

2. Decide:
   - Everything passes:  python -m pipeline approve --panel <ID>
   - Something fails:  python -m pipeline reject --panel <ID> --reason "<what failed>"
     Fix it ONCE: make a targeted edit of that image with image_gen, or regenerate with the same prompt and images. Then run
     python -m pipeline ingest --from-codex  and review again.
   - Still wrong after one fix:
     python -m pipeline approve --panel <ID> --version <best version> --status REVIEW_LATER --note "<what is wrong>"
   - Speech-balloon panels (CH01-P009-PN02 and CH01-P010-PN02), after approving:
     read U,V just beside the speaker's mouth (clear space, not on the face) from the review grid, then run
     python -m pipeline tail --panel <ID> --at U,V

3. Run  python -m pipeline next --codex  again.

When all 14 panels are done:
- Run  python -m pipeline build
- view_image every page in batch\P009-P013\output\png\.
  If a face, hand or important object is cut off, run  python -m pipeline frame --panel <ID> --focus U,V , then build again.
- Run  python -m pipeline audit  and  python -m pipeline status
- Report to me:
  - each page's audit status (PASS / REVIEW / PROOF / FAIL);
  - any REVIEW_LATER panels and why;
  - the path of batch\P009-P013\output\CH01-P009-P013-REVIEW.pdf

Rules:
- Never put any text, letters or numbers in the images.
- Never edit ..\Scripts, ..\Charactors, ..\Locations or ..\Completed Samples.
- Never change manuscript text.
- At most one correction per panel.
- Never modify ~/.codex/skills/.system/imagegen/scripts/image_gen.py.
```

### What Codex will be doing (you can run these yourself to watch)

| Step | Command |
|---|---|
| Get the next task (images, prompt, checklist) | `python -m pipeline next --codex` |
| The same task as JSON, for scripts | `python -m pipeline next --json` |
| File the image Codex just made | `python -m pipeline ingest --from-codex` (add `--all-new` to file several attempts as versions) |
| Check it | `python -m pipeline review --panel CH01-P009-PN01`, then open `batch\P009-P013\art\_review\…-review.png` |
| Accept or reject it | `approve` / `reject` (see section 6) |

---

## 3. Option B — Codex, one panel at a time (you stay in control)

Use this when you want to approve each panel yourself. Send Codex a single-panel message:

```text
In C:\Users\Akash Chaudhari\Desktop\Projects\ComicAgent\Approach1 run:  python -m pipeline next --codex
Do only STEP 1 to STEP 3 of the task it prints: view the images, generate with image_gen, then run
python -m pipeline ingest --from-codex
Then stop and tell me the review command.
```

Then run `review` yourself, look at the overlay, and `approve` or `reject` (section 6).

---

## 4. Option C — You, with ChatGPT in the browser

| Step | Do this |
|---|---|
| 1 | `python -m pipeline next`: the prompt is copied to your clipboard and the panel's image folder opens |
| 2 | In a **new** ChatGPT chat, drag in **all** the numbered images from that folder, in number order. Paste the prompt and send |
| 3 | Download the image ChatGPT makes |
| 4 | `python -m pipeline ingest --downloads`, which takes the newest image from your Downloads folder. Or save it into `batch\P009-P013\art\_inbox\` and run `python -m pipeline ingest` |
| 5 | `python -m pipeline review --panel <ID>`, open the overlay PNG, then `approve` or `reject` (section 6) |
| 6 | Repeat from step 1 until `python -m pipeline status` shows no `pending` panels |

The prompt files themselves are in `batch\P009-P013\prompts\`, if you'd rather copy from them directly. `QUEUE.md` there gives the order.

---

## 5. Option D — fully unattended with an OpenAI API key

Set `OPENAI_API_KEY` in your environment, then for each panel run:

```
python -m pipeline generate --run          # makes the next pending panel with gpt-image-2 and files it
python -m pipeline review --panel <ID>
python -m pipeline approve --panel <ID>
```

Without a key, `python -m pipeline generate` prints the exact request (a dry run) and spends nothing.

---

## 6. Check, fix and finish

### Reading the review overlay (`art\_review\<ID>-vNNN-review.png`)

- **Gold box:** the part of the image that will show on the page.
- **Cyan boxes:** where captions and balloons will go. Nothing important should be under them.
- **Magenta circle:** where the balloon tail points.
- **Grid:** 0.0 to 1.0 coordinates, used for `tail --at U,V` and `frame --focus U,V`.

### Decide

| Situation | Command |
|---|---|
| Everything on the checklist is right | `python -m pipeline approve --panel <ID>` |
| Only a known location detail differs (e.g. the shape of a lamp) | `python -m pipeline approve --panel <ID> --status PASS_WITH_LOCATION_EXCEPTION --exceptions LOC-EX-11` |
| Something is wrong (wrong hand, text in the image, missing object…) | `python -m pipeline reject --panel <ID> --reason "..."`, then make **one** new or edited image and `ingest` it |
| Still wrong after that one fix | `python -m pipeline approve --panel <ID> --version N --status REVIEW_LATER --note "..."` |
| Pick a different version | add `--version N` to `approve` or `review` |
| Redo a panel later | `python -m pipeline next --panel <ID>` (or `next --codex --panel <ID>`) |

### Aim the two speech balloons

Do this after approving `CH01-P009-PN02` (Vihaan) and `CH01-P010-PN02` (Tez):

```
python -m pipeline tail --panel CH01-P009-PN02 --at 0.55,0.40     # use your own U,V from the grid
python -m pipeline tail --panel CH01-P010-PN02 --at 0.60,0.45
```

### Fix a crop (head or hand cut off)

```
python -m pipeline frame --panel <ID> --focus 0.5,0.4 --zoom 1.0
```

### Build and check the pages

```
python -m pipeline build      # PDFs + 300-dpi PNGs
python -m pipeline audit      # writes output\AUDIT.md
python -m pipeline status     # writes output\STATUS.md
```

Audit status per page:
- **PASS:** ready for your review.
- **REVIEW:** usable, with a noted issue.
- **PROOF:** some art is still missing.
- **FAIL:** a text, font or size problem.

### Your results (`batch\P009-P013\output\`)

| File | What it is |
|---|---|
| `CH01-P009-P013-REVIEW.pdf` | all five pages, for review |
| `pdf\CH01-P0xx.pdf` | one PDF per page |
| `png\CH01-P0xx.png` | each page at 3600×2700 |
| `CH01-P009-P013-CONTACT-SHEET.png` | all five pages on one image |
| `AUDIT.md`, `STATUS.md` | the checks and the progress table |
| `proofs\` | previews made before the art existed |

---

## 7. Making the next pages

```
python -m pipeline new-batch --pages 14-18
python -m pipeline --batch P014-P018 extract
```

Then ask Codex:

> Read AGENTS.md and skills/chandrush-director/SKILL.md and skills/chandrush-prompt-writer/SKILL.md. Prepare batch P014-P018: write the page briefs and layouts, run `proof`, run `prompts draft`, then edit and lint the prompts and run `refs`. After that, run the art loop from MANUAL.md section 2.

Note: pages with worked maths need the maths renderer, which is not built yet (`guide/07_ISSUES_AND_DECISIONS.md`). Story-only pages work now.

---

## 8. Command cheat-sheet

| Command | What it does |
|---|---|
| `status` | progress table and the next action |
| `next` / `next --codex` / `next --json` | hand out the next panel (person / Codex / script) |
| `ingest` · `--downloads` · `--from-codex [--all-new]` · `--file X` | file a new image as the next version of a panel |
| `review --panel ID [--version N]` | overlay of crop, text areas, tail point and grid |
| `approve --panel ID [--version N] [--status …] [--note …]` | accept an image |
| `reject --panel ID --reason "…"` | reject (one retry allowed) |
| `tail --panel ID --at U,V` | aim a speech-balloon tail |
| `frame --panel ID --focus U,V [--zoom Z]` | change the crop |
| `build [--mode final\|latest\|standin\|placeholder]` | make the pages |
| `audit` | check the exported pages against the script |
| `compare --page 12 --sample 12` | side-by-side with your Opening sample |
| `prompts lint\|list\|show --panel ID\|draft` | check, list, print or draft prompts |
| `refs` | rebuild the numbered reference-image folders and QUEUE.md |
| `generate [--panel ID] [--run]` | API route (dry run without `--run` or a key) |
| `proof` | grey layout proof |
| `new-batch --pages A-B`, `extract` | start new pages |

Add `--help` to any command for its options. Add `--batch <name>` when you have more than one batch.

---

## 9. Troubleshooting

| Problem | Fix |
|---|---|
| `ingest --from-codex` finds nothing | Codex saved the image somewhere else, or before `next` was run. Copy it into `batch\P009-P013\art\_inbox\` and run `python -m pipeline ingest --route codex` |
| `ingest` cannot tell which panel an image is | Rename it to include the panel ID (e.g. `CH01-P009-PN01.png`) or add `--panel ID` |
| The image has words or letters in it | `reject`, then a targeted edit: "remove all lettering, keep everything else exactly" |
| Wrong character, hand or pose | `reject` with the reason, then regenerate once |
| Tez has black stripes | `reject`, then edit: "make Tez's stripes blue; the left-shoulder stripe and the first stripe on each flank pale grey" |
| A balloon tail points the wrong way | `tail --panel ID --at U,V` with a better point, then `build` |
| Low ppi note in the audit | Fine for review; for print, regenerate at the preferred size given in the prompt |
| Start again for one panel | `next --panel ID`; old versions are kept, and new ones become v2, v3, … |

---

## 10. What is where

| Folder or file | Contents |
|---|---|
| `MANUAL.md` | this manual |
| `README.md` | the short overview |
| `AGENTS.md` | Codex's instructions |
| `CLAUDE.md` | Claude Code's instructions |
| `guide/` | the full guidelines: pipeline, rules, design, prompting, image routes, audit, issues |
| `skills/` | five agent skills (director, prompt-writer, art-producer, assembler, auditor) |
| `design/` | the look measured from your sample, character and location notes, continuity images |
| `batch/P009-P013/pages/` | exact text (contracts), page briefs, layouts |
| `batch/P009-P013/prompts/` | 14 prompt files, `QUEUE.md`, `refs/<panel>/` numbered images |
| `batch/P009-P013/art/` | `_inbox/` (drop zone), one folder per panel (all versions), `_review/` overlays |
| `batch/P009-P013/output/` | the finished pages and reports |

Your original folders (`Scripts`, `Charactors`, `Locations`, `Completed Samples`) are only read, never changed.
