# Prompts for batch P009-P013

There is one file per story panel: 14 panels on V07 pages 9–13. Work through them in the order given in **`QUEUE.md`**. Scene anchors come first, so the later panels can match them.

## Each file contains

1. **Job card** (top, between `---` lines): the panel ID, queue number, the preferred image size, the attachments in order, and an optional anchor panel. The pipeline reads this.
2. **Attach these images, in this order.** The numbered copies are in `refs/<panel>/`: `1 - …`, `2 - …`. Drag them in that order.
3. **Prompt.** Copy everything inside the box. It says what each image is for, so the order matters.
4. **Size.** The preferred size, and the band to keep important content inside if your tool only makes 3:2 or square images.
5. **Accept only if.** Tick every line before approving the image.
6. **Source.** The manuscript text that will be lettered onto the panel later (never put it in the image) and the manuscript's own visual direction, for checking.

## Quick use

| You are using | Do this |
|---|---|
| ChatGPT in a browser | `python -m pipeline next` → drag in the images from the folder that opens → paste → download → `python -m pipeline ingest --downloads` |
| Codex | "Follow AGENTS.md and make the art" (Codex uses its built-in image tool) |
| OpenAI API key | `python -m pipeline generate --run` |

After each image: `python -m pipeline review --panel <id>`, then `approve` or `reject`.

## Rules the prompts follow

- **No lettering in the art.** Every caption and speech balloon is added by the page builder from the exact script text.
- **The reference images carry annotations** (white label boxes and arrows) that must not be copied. Every prompt says so.
- **The state of the scene comes from the manuscript, not the reference image.** That covers the dark gate, the half-open hatch, the empty Bell stand with its slack rope, the dark Lantern Street archway and Tez's blue and pale-grey stripes.

Check every prompt file with `python -m pipeline prompts lint`.
