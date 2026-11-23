# ChandRush Studio

A desktop UI application over the ChandRush comic pipeline in `Tasks/`. It drives the Claude Code harness through the [Claude Agent SDK](https://docs.claude.com/en/docs/claude-code/sdk), so `CLAUDE.md`, the `comic-master` skill, the subagents, and your local Claude login work seamlessly. On top of that, it provides a visual board, review gates, and live controls.

---

## Install and first run

Download the AppImage (Linux) or the `.exe` installer (Windows) from the
[Releases page](https://github.com/akashch1013/Ankush-Project/releases). You do **not** need the GitHub repo.

On first launch Studio shows a short setup:
1. **OpenAI API key.** Paste your key (from platform.openai.com/api-keys) and click *Save key*. Studio checks it with OpenAI, stores it encrypted on this computer and gives it to the image pipeline as `OPENAI_API_KEY`. Agents can't read or print it. You can skip this and add, replace or remove the key later in **Settings**.
2. **Workspace.** *Create* copies the starter workspace bundled in the app (pipeline, skills and agents, design kit, character sheets, chapter manuscripts) into a folder such as `~/Documents/ChandRush Studio`. Or choose an existing folder that contains `Tasks/` (a workspace made earlier, or a clone of the repo).

Then open **Doctor** to check the rest:
- **Claude Code CLI**, installed and logged in (`claude auth login`). Studio uses your system's `claude`.
- **Python 3** with Pillow (`pip install pillow`).
- **Firefox** (used by `render_pdf.py`).

On Linux, if unprivileged user namespaces are restricted, start the AppImage with `--no-sandbox`.

## Building from source

```bash
git clone https://github.com/akashch1013/Ankush-Project.git
cd Ankush-Project/studio
npm install
npm run dist:linux   # or dist:win → dist/ChandRush-Studio-<version>-…
```

`scripts/kit.mjs` runs first and copies the git-tracked workspace files into `build/workspace/`, which is packed into the app as `resources/workspace`. Generated plates, archives, `.env` files and the cost log are left out.

Releases are built by `.github/workflows/studio-build.yml` on **every push to `master`** (every merged PR): it takes the next patch version after the newest `studio-v*` tag (or `package.json`'s version when that is higher, so bump it there for a minor or major release), builds Linux and Windows, tags `studio-vX.Y.Z` and publishes the release with generated notes. Pull requests only build. Pushing a `studio-vX.Y.Z` tag by hand still releases that exact version.

## Development & Testing

```bash
cd studio
npm run dev          # development server with hot reload
npm test             # run main-process policy and inline-edit unit tests
npm run typecheck    # run TypeScript typechecking
```

**Environment Requirements:**
- Python 3 + Pillow
- Firefox (`render_pdf.py`)
- An installed, logged-in `claude` CLI. Bundled SDK binaries are excluded from the package; Studio uses your system's `claude`.
- For image batches, save your OpenAI key in Settings (or set `OPENAI_API_KEY` in the environment / `Tasks/BagroundGenTask/.env`).

## What it does
- **Board.** Every manuscript page of a chapter, from `src/`, `pages.json`, previews, `Output/` PDFs and `review.json`. Each page carries a stage chip: in manuscript → planned → built → rendered → maths PASS → awaiting review → approved / changes. You can bulk-approve.
- **New run.**
  - Upload a new chapter: the files are copied into a new `Tasks/Reference/<folder>/` (existing files are never overwritten). The free setup prep (`pipeline/setup_chapter.py`) runs, then a **Setup** session starts the `chapter-setup` agent. That agent maps masters and locations, checks the cast and triages the manuscript maths. Its questions for the author arrive as a review card.
  - Or pick an existing chapter, select pages and choose *full run*, *plan only* or *sample*.
  - Runs are cut into chunks (default 20 pages). Each chunk is a fresh master session started with `/comic-master run …`, and the next chunk starts automatically when the master calls `chunk_done`.
- **Agent panel.** A live timeline of the master: text, tool calls, a subagent tree with per-agent stop, and Stop for the whole session. Sessions are saved and can be resumed. The **desk** session per chapter takes page fixes and feedback.
- **Permissions.** Three presets: pipeline-safe auto (default), ask, or allow all.
  - Always blocked, in every preset: edits to `Reference/` or `Charactors/`, reading or printing the API key (the `.env` file or the environment), immediate image calls, quality `max`.
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
  - `secrets.ts`: the OpenAI key; `workspace.ts`: workspaces from the bundled kit;
  - `review.ts`, `doctor.ts`, `upload.ts`, `tools.ts`.
- `src/preload/`: the IPC bridge.
- `src/renderer/`: the React UI.

Debug: `STUDIO_SHOT=/path.png [STUDIO_SHOT_JS=… STUDIO_SHOT_WAIT=ms]` captures the window after load, then quits.
