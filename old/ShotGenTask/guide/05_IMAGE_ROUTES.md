# 05 · Image routes — three ways to make the panel art

All three routes end the same way: the image lands in `batch/<id>/art/_inbox/`, `ingest` files it as `art/<panel>/<panel>-art-vNNN.png`, and `review` → `approve` | `reject` follows. Mixing routes is fine. For example, Codex makes most panels and a person redoes one in ChatGPT.

| Route | Who drives | Needs | Autonomy |
|---|---|---|---|
| **A · Codex built-in image tool** | Codex agent | Codex signed in with ChatGPT; no API key | Fully autonomous loop |
| **B · Codex image CLI / OpenAI API** | Any agent or script (`pipeline generate --run`) | `OPENAI_API_KEY` set in the environment, network | Fully autonomous, unattended |
| **C · ChatGPT web UI** | A person, helped by `next` and `ingest` | A browser | Semi-manual, about 1 minute of clicking per panel |

---

## Route A — Codex built-in `image_gen` (recommended)

Codex's system skill `imagegen` (`~/.codex/skills/.system/imagegen/SKILL.md`) makes this the default route:
- the built-in `image_gen` tool needs no API key;
- reference images must first be loaded into the conversation with `view_image`;
- the tool saves into `$CODEX_HOME/generated_images/…`, so the result has to be copied into the project.

**Loop for each panel** (this is what `AGENTS.md` tells Codex to do):

1. `python -m pipeline next --codex` prints one self-contained task, or `--json` for the same data as JSON:
   - the absolute paths of the reference images, in order (the optional `APPROVED …` anchor included when it exists);
   - the exact prompt between `-----BEGIN PROMPT-----` / `-----END PROMPT-----`;
   - the size and fallback rule;
   - the checklist and the follow-up commands.

   If a panel already has art waiting, the task is a REVIEW task instead.
2. `view_image` each listed image, in order.
3. Call `image_gen` with the prompt text, unchanged. Ask for the stated size/aspect; if that size isn't possible, follow the fallback rule. In tests, Codex's built-in tool returned 1905×825 for the 2.3:1 frame, which is about 238 ppi placed.
4. `python -m pipeline ingest --from-codex` finds the newest image in `$CODEX_HOME/generated_images/` made since the panel was handed out, copies it in and files it. `--all-new` files every new attempt as a version. Already-filed images are skipped (sha256).
5. If you'd rather copy by hand: put the file in `batch/<id>/art/_inbox/<panel>.png` and run `python -m pipeline ingest --route codex`.
6. `python -m pipeline review --panel <panel>`. Open the overlay with `view_image`, and also look at the full-resolution art.
7. Tick every line of the prompt file's **Accept only if** list:
   - All pass: `python -m pipeline approve --panel <panel>`. Use `--status PASS_WITH_LOCATION_EXCEPTION --exceptions LOC-EX-xx` when a covered location mismatch is the only difference.
   - Something fails: `python -m pipeline reject --panel <panel> --reason "<what failed>"`. Make **one** correction, either a targeted edit of the image with `image_gen` (see `04_PROMPTING.md`) or a regeneration with a fixed prompt. Ingest it as the next version.
   - Still wrong after one correction: approve the better version with `--status REVIEW_LATER --note "<issue>"` and continue.
8. Balloon panels: `python -m pipeline tail --panel <panel> --at U,V`, using U,V just beside the speaker's mouth read from the overlay grid.

Codex follows `skills/chandrush-art-producer/SKILL.md` for this loop, with `AGENTS.md` as the entry point.

## Route B — Codex image CLI / OpenAI API (unattended)

```bash
python -m pipeline generate --panel CH01-P009-PN01           # dry run: prints the exact request, no network
python -m pipeline generate --panel CH01-P009-PN01 --run     # real call (needs OPENAI_API_KEY), then auto-ingest
python -m pipeline generate --run                            # the next pending panel in the queue
```

- This calls Codex's bundled `image_gen.py edit` without changing it. It passes:
  - `--image` for every numbered reference, including the anchor once approved;
  - `--prompt-file`;
  - `--size` with the exact legal size;
  - `--quality high` and `--no-augment`, so the reviewed prompt is used as written.
- Model: `gpt-image-2`, the CLI default. It accepts up to 16 input images and flexible sizes.
- Review, approve and tail steps are the same as Route A, steps 6–8.
- Cost: every call is billed to the API key. Record the number of attempts honestly (the `state.json` log does this).

## Route C — ChatGPT web UI (by hand)

1. `python -m pipeline next`. This copies the prompt to the clipboard, opens `prompts/refs/<panel>/` in Explorer and prints the size.
2. In ChatGPT, start a fresh chat (old chats bias the style). Drag in **all** the numbered images from the folder, in number order. Paste the prompt and send.
3. If ChatGPT offers only 3:2, 2:3 or square, accept it. The prompt already tells it which band to keep key content in.
4. Download the image, then do one of these:
   - save it into `batch/<id>/art/_inbox/` and run `python -m pipeline ingest`; or
   - leave it in Downloads and run `python -m pipeline ingest --downloads`, which picks the newest image saved since `next`.
5. `python -m pipeline review --panel <panel>`: open the overlay PNG, check the list, then approve or reject as in Route A.

Tip: to redo a panel, run `python -m pipeline next --panel <panel>`.

---

## Naming, versions, retries

- Inbox files can have any name. `ingest` decides the panel from:
  1. a panel ID in the file name, else
  2. `--panel`, else
  3. the panel last handed out by `next`.
- Each ingest creates a new version (`v001`, `v002`, …). Nothing is overwritten. `state.json` records the sha256, size, route, prompt hash and time.
- `reject` uses up the one automatic retry. A second `reject` tells you to keep the better version as REVIEW_LATER.
- `approve` of a scene anchor rebuilds the refs folders of the panels that list it, so later prompts get it automatically.

## Troubleshooting

| Problem | Fix |
|---|---|
| `ingest` says it cannot tell which panel | Rename the file to include the panel ID, or pass `--panel` |
| `generate --run` says dry run | `OPENAI_API_KEY` is not set in this shell |
| Codex cannot find the generated file | Look in `$CODEX_HOME/generated_images/` (default `~/.codex/generated_images/`) |
| Art has the wrong aspect | Fine: `review` shows the crop. Adjust with `frame --focus U,V`, or regenerate at the preferred size if key content is lost |
| Low ppi warning | Acceptable for review PDFs. For print, regenerate at the preferred size (Route A or B) |
