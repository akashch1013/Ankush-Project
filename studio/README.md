# ChandRush Studio

A small desktop app over the ChandRush comic pipeline in `Tasks/`. It drives the same Claude Code harness through the [Claude Agent SDK](https://docs.claude.com/en/docs/claude-code/sdk), so `CLAUDE.md`, the `comic-master` skill, the subagents and your login all work unchanged. On top of that it adds a board, review gates and controls.

## Run
```bash
cd studio
npm install
npm run dev          # development (hot reload)
npm run dist:linux   # dist/ChandRush Studio-<v>.AppImage
npm test             # policy + inline-edit unit tests
```
The first time it runs, it opens on **Settings**. Pick the repo folder that contains `Tasks/`, then check **Doctor**.

**Needs:**
- Python 3 + Pillow;
- Firefox (`render_pdf.py`);
- an installed, logged-in `claude` CLI. The bundled SDK binaries are left out of the package; Studio uses yours.

For image batches, the OpenAI key must be in `Tasks/BagroundGenTask/.env` or in `OPENAI_API_KEY`.

## What it does
- **Board.** Every manuscript page of a chapter, from `src/`, `pages.json`, previews, `Output/` PDFs and `review.json`. Each page carries a stage chip: in manuscript → planned → built → rendered → maths PASS → awaiting review → approved / changes. You can bulk-approve.
- **New run.**
  - Upload a new chapter: the files are copied into a new `Tasks/Reference/<folder>/`, existing files are never overwritten, and the free stage-0 split runs.
  - Or pick an existing chapter, select pages and choose *full run*, *plan only* or *sample*.
  - Runs are cut into chunks (default 20 pages). Each chunk is a fresh master session started with `/comic-master run …`, and the next chunk starts automatically when the master calls `chunk_done`.
- **Agent panel.** A live timeline of the master: text, tool calls, a subagent tree with per-agent stop, and Stop for the whole session. Sessions are saved and can be resumed. The **desk** session per chapter takes page fixes and feedback.
- **Permissions.** Three presets: pipeline-safe auto (default), ask, or allow all.
  - Always blocked, in every preset: edits to `Reference/` or `Charactors/`, reading the API key, immediate image calls, quality `max`.
  - Paid `imggen.py batch submit` always shows a **Spend approval** card.
- **Gates.** The master calls `mcp__studio__request_review`, and a gate card appears. Approving or requesting changes writes `review.json` and a `FEEDBACK.md` line, then resumes the agent.
- **Edit a page:**
  1. *Ask agent to fix* (`/comic-master fix …`).
  2. *Inline text edit*: click text on the live page, then Save. This makes targeted edits to `index.html`, runs `pagekit render` and `textcheck page`, and logs to FEEDBACK.md. No agent is involved.
  3. *Edit image*: click an image, describe the change, and it goes to the agent as an `imggen fix` (batch, with a spend card).
  4. *Rules & feedback*: add a permanent rule with `/comic-master feedback …`, and see the LESSONS.md / FEEDBACK.md diff.

## Not available here
**Claude Artifacts.** The Artifact tool exists only in interactive Claude Code. The SDK and `claude -p` can't see it, so Studio itself is the review surface. To publish a page as an artifact, run that step in an interactive `claude` session.

## Layout
- `src/main/`: the Electron main process:
  - `agent.ts`: SDK sessions, studio MCP tools, runs;
  - `policy.ts`: permissions;
  - `state.ts`: board state and file watching;
  - `inline.ts`: HTML edits;
  - `review.ts`, `doctor.ts`, `upload.ts`, `tools.ts`.
- `src/preload/`: the IPC bridge.
- `src/renderer/`: the React UI.

Debug: `STUDIO_SHOT=/path.png [STUDIO_SHOT_JS=… STUDIO_SHOT_WAIT=ms]` captures the window after load, then quits.
