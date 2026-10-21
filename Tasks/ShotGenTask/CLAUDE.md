# CLAUDE.md — ChandRush Approach1

Read `AGENTS.md` first; it is the shared entry point for every coding agent. The workflow, hard rules and file map there apply unchanged.

Notes for Claude Code:

- Claude Code has no built-in image generator. You can run every stage except making the panel art:
  - extract, briefs, layouts, proofs;
  - prompts, lint and refs;
  - ingest, review (open the overlay PNGs with the Read tool), approve, tail and frame;
  - build, compare and audit.
- For the art itself, use one of these routes from `guide/05_IMAGE_ROUTES.md`:
  - Codex's built-in tool, via `AGENTS.md`;
  - `python -m pipeline generate --run`, if the user has set `OPENAI_API_KEY`;
  - the user's ChatGPT downloads plus `python -m pipeline ingest --downloads`.
- The skills in `skills/*/SKILL.md` are plain instructions. Read the one for the stage you are doing.
