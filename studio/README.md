# ChandRush Studio

A desktop UI application over the ChandRush comic pipeline in `Tasks/`. It drives the Claude Code harness through the [Claude Agent SDK](https://docs.claude.com/en/docs/claude-code/sdk), so `CLAUDE.md`, the `comic-master` skill, the subagents, and your local Claude login work seamlessly. On top of that, it provides a visual board, review gates, and live controls.

---

## Building the AppImage from GitHub

Follow these steps to clone the repository and build the Linux executable AppImage (`studio/dist/ChandRush Studio-0.1.0.AppImage`):

### 1. Prerequisites
Ensure your system has the following installed:
- **Node.js**: v20 or higher (with `npm`)
- **Git**
- **Python 3** with Pillow (`pip install pillow`)
- **Firefox** (required for `render_pdf.py`)
- **Claude CLI**: installed and authenticated (`claude login`). Studio uses your local Claude CLI installation.

### 2. Clone the Repository
Clone the project repository from GitHub and switch to the project branch:

```bash
git clone https://github.com/akashch1013/Ankush-Project.git
cd Ankush-Project
git checkout token-efficient-runs
```

### 3. Navigate to the Studio Directory
```bash
cd studio
```

### 4. Install Dependencies
```bash
npm install
```

### 5. Build the Linux AppImage
Run the distribution build script:
```bash
npm run dist:linux
```

This runs:
1. `electron-vite build` to bundle main, preload, and React renderer assets.
2. `electron-builder --linux AppImage` to package the app into a standalone AppImage.

### 6. Output Binary Location
Once the build completes, the executable AppImage will be generated at:
```text
/home/abhay/F/Freelance/Ankush-Project/studio/dist/ChandRush Studio-0.1.0.AppImage
```
(Relative to the repository root: `studio/dist/ChandRush Studio-0.1.0.AppImage`)

### 7. Run the AppImage
Grant executable permissions (if not already set) and run the AppImage:

```bash
chmod +x "dist/ChandRush Studio-0.1.0.AppImage"
./"dist/ChandRush Studio-0.1.0.AppImage"
```

> **Note:** If running on a system or environment where unprivileged user namespaces are restricted, launch with `--no-sandbox`:
> ```bash
> ./"dist/ChandRush Studio-0.1.0.AppImage" --no-sandbox
> ```

---

## Development & Testing

```bash
cd studio
npm run dev          # development server with hot reload
npm test             # run main-process policy and inline-edit unit tests
npm run typecheck    # run TypeScript typechecking
```

The first time it runs, it opens on **Settings**. Select the repo folder containing `Tasks/`, then check **Doctor**.

**Environment Requirements:**
- Python 3 + Pillow
- Firefox (`render_pdf.py`)
- An installed, logged-in `claude` CLI. Bundled SDK binaries are excluded from the package; Studio uses your system's `claude`.
- For image batches, set `OPENAI_API_KEY` in your environment or in `Tasks/BagroundGenTask/.env`.

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
