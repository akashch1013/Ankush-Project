# CLAUDE.md: ChandRush CH01 location images (Claude entry point)

This folder makes the **27 Chapter 01 location images** defined by `CH01-LOCATION-IMAGE-GENERATION-DRAFT-02.docx`.

The skill is `/chandrush-backgrounds`, registered from the ComicAgent root. Its full text is `skills/chandrush-backgrounds/SKILL.md`. Read it, and `LOCATION-BIBLE.md` with `geography-guide.png`, before generating.

**Image route: the Higgsfield MCP.** Claude Code has no built-in image generator.
- In the sample round, probe Higgsfield once and write the recipe to `HIGGSFIELD-NOTES.md`:
  - tools and models (use **GPT Image 2**);
  - how references are passed;
  - aspect values 16:9, 4:3 and 3:2;
  - the largest size;
  - edit support;
  - the result format.
- Workers download each result with `curl` to the job's SAVE AS path. They open it with Read, zoom-check every label and count (`python3 bg.py zoom`), then run `python3 bg.py done`. `done` keeps the native file and upscales to the target size.

**Parallel:**
- Spawn background sub-agents (Agent tool), each with `skills/chandrush-backgrounds/WORKER-PROMPT.md`, its placeholders filled, `{ROUTE}` = `Claude + Higgsfield MCP`.
- If sub-agents can't see the Higgsfield tools: claim 4 jobs and send their 4 generation calls in one message.

**Queue:** `python3 bg.py check | claim | done | release | pick | status | sheet | zoom | import`.

**Hard rules:**
- No characters or hands.
- Print only the requested physical labels, as exact copy.
- Never attach the old location pack.
- One generation + at most two fixes per job.
- Never pick candidates yourself, and never start the full run before the user approves the samples.
- Never edit the source folders or the generated prompt files by hand.
