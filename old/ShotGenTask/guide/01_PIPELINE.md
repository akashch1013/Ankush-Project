# 01 · Pipeline — every stage, step by step

Run all commands from the `Approach1/` folder, as `python -m pipeline <command>`. Add `--batch <id>` when more than one batch folder exists; the default is the most recently changed one. `python -m pipeline <command> --help` lists every option.

Each stage below gives its inputs, commands, outputs, the condition for **Done when**, and what to do **If it fails**. Work through the stages in order. They are restartable: rerunning a stage never destroys approved art.

---

## Stage 0 · Setup (once per machine)

- **Needs:** Python 3.10 or newer and `pip install -r requirements.txt` (reportlab, pymupdf, pillow, numpy, pyyaml).
- **Fonts:** the four OFL font files are already in `fonts/`.
- **Check:** `python -m pipeline status` prints a table.
- **If it fails:** a missing module means installing the requirements. A missing font means re-downloading it, as described in `fonts/README.md`.

## Stage 1 · Choose and create a batch (Director)

- **Rule:** default 5 pages, never more than 10 (Brief V03). Skip pages that the user's samples already cover, unless the user asks for a redo. The coverage list is in `07_ISSUES_AND_DECISIONS.md`.
- **Command:** `python -m pipeline new-batch --pages 14-18`. This creates `batch/P014-P018/` with `batch.json`.
- **Done when:** the folder exists and `batch.json` records the pages and any user decisions for this batch.

## Stage 2 · Extract exact page contracts

- **Command:** `python -m pipeline extract`
- **What it does:**
  - checks the manuscript DOCX checksum against the manifest;
  - writes `pages/CH01-P0xx.contract.json` with every printable block (exact text, role, speaker, runs) kept apart from non-printable notes, references and role labels;
  - resolves every literal reference filename.
- **Done when:** it prints `MATCHES`, every page is listed, and no `PROBLEMS`.
- **If it fails:**
  - **checksum mismatch:** the manuscript changed. Stop and ask the user which version is authoritative.
  - **`MISSING refs`:** see `design/reference_map.json`. Never substitute a different state or scene silently. Ask the user, or leave that panel waiting while the others continue.
  - **open details** (the manifest's `open_details`, e.g. P050-PN05, P061-PN01): do not invent numbers. Ask.

## Stage 3 · Understand each page (Director)

Read the whole contract: page notes, every panel's printable blocks and its full visual note. Then open each reference image and look at it. Open the previous pages' approved art too, for continuity. Write `pages/CH01-P0xx.brief.md`, using the five briefs in `batch/P009-P013/pages/` as the template. Each brief covers:

- the story beat and reading flow;
- the exact text table;
- the continuity state: who is where, which hand holds what, light and repair states, anything that changed since the last page;
- a reference table of **keep / ignore / correct**;
- the layout intent;
- the risks to watch.

**Done when:** a reader of the brief alone could check a generated panel without the manuscript.

**Why:** prompts and reviews go wrong when the panel's state (hatch open or closed, lamps lit or dark, which hand) is guessed. The brief settles it once.

## Stage 4 · Direct the page layout and prove the text fits

1. Write `pages/CH01-P0xx.layout.json`. Copy a similar page from this batch and change it. The fields are:
   - `theme` and `border`: from `design/tokens.json`;
   - for each panel: `frame` [x0, y0, x1, y1] in points within the 24–840 × 24–618 content area, `art.focus` and `art.zoom`, and `compose`, a plain sentence for the prompt writer saying where subjects go and which area stays calm;
   - `text` items:
     - `caption` takes `block`, `at` [x, y], `w` (the max width) and an optional `anchor` (tl, tr, bl, br, tc, bc, c);
     - `balloon` takes `block`, `at`, `max_w` and `tail_to.page` (a default target);
     - `reader` takes `block`, `at` and `w`.
2. `python -m pipeline proof`. This is a grey layout proof with text boxes outlined. Open `output/proofs/*.png`.
3. `python -m pipeline build --mode standin --dpi 110` previews composition using the location images.

- **Done when:** the build prints no `ERROR`, captions sit at least about 13 pt inside their frames as in the sample, and the page has an obvious reading order.
- **If it fails:** an overflow, overlap or unplaced block is a layout problem. Enlarge the frame or the caption measure, or rebalance the panels. Never shrink type or cut words (`02_RULES.md` T-rules).

## Stage 5 · Write the panel prompts (Prompt writer)

- `python -m pipeline prompts draft` creates a first draft per story panel from the manuscript note, layout and identity cards.
- Edit every draft (`04_PROMPTING.md`):
  - set the queue order, with scene anchors first;
  - add a continuity image and `anchors`;
  - fix the scene corrections;
  - write the one-line primary request;
  - complete the acceptance list;
  - set `review_needed: false`.
- `python -m pipeline prompts lint`, then `python -m pipeline refs`. The second command builds the numbered `prompts/refs/<panel>/` folders and `prompts/QUEUE.md`.
- **Done when:** lint prints `All N prompt files pass.`

## Stage 6 · Make the art (Art producer)

Pick the route in `05_IMAGE_ROUTES.md`: Codex built-in tool, Codex CLI/API, or the ChatGPT web UI. Whatever the route, each panel follows the same loop:

```
next  ─▶ generate with the listed images, in order ─▶ save into art/_inbox ─▶ ingest ─▶ review
      ─▶ approve (PASS / PASS_WITH_LOCATION_EXCEPTION)  or  reject (one automatic retry) ─▶ REVIEW_LATER if still wrong
```

- **Done when:** `python -m pipeline status` shows every panel as approved or review_later.
- **Budget:** at most **one** automatic correction per panel. After that, keep the better version as REVIEW_LATER and move on (Brief V03 §16.3). Approving a scene anchor automatically adds it to the refs of the later panels that use it.

## Stage 7 · Fine-tune crops and balloon tails (Assembler)

- For every panel with a balloon, open its review overlay (`art/_review/<panel>-vNNN-review.png`). Read the U,V point just beside the speaker's mouth, in clear space and not on the face. Run `python -m pipeline tail --panel <id> --at U,V`.
- If a head, hand or key object is cropped, or a text zone covers a face, run `python -m pipeline frame --panel <id> --focus U,V [--zoom 1.1]`. Then run `review` again.
- **Done when:** `status` shows the balloon tail as `set` for every balloon panel.

## Stage 8 · Build the pages

- **Command:** `python -m pipeline build`
- **Outputs:**
  - `output/pdf/CH01-P0xx.pdf` per page;
  - `output/CH01-P0xx-P0yy-REVIEW.pdf` for the batch;
  - `output/png/*.png` at 300 dpi, 3600×2700;
  - a contact sheet and `*.build.json`, which records art versions, crops, ppi and tail geometry.
- Look at every PNG at full-page size, then compare one page against the sample: `python -m pipeline compare --page 12 --sample 12`.
- **Done when:** the build has no errors and each page reads clearly at full-page view.

## Stage 9 · Audit and report

- **Command:** `python -m pipeline audit`. This writes `output/AUDIT.md`; then run `python -m pipeline status`.
- Report to the user:
  - what was produced;
  - which pages PASS, are REVIEW or are PROOF;
  - every REVIEW_LATER panel and why;
  - effective ppi;
  - what was not verified.
- Use the exact status words. A plan, a prompt or a script is not a finished page.
- **Then stop.** Wait for the user's review of the batch before starting the next one.

## Resuming

All progress lives in `batch/<id>/state.json`: versions, approvals, retries and a log. Rerunning `status` shows exactly where to continue. `.cache/` can be deleted at any time.
