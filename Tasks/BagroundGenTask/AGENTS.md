# AGENTS.md: ChandRush CH01 location images (Register V10)

This folder makes the **32 Chapter 01 location images** defined by `Ref/CH01-LOCATION-IMAGE-REGISTER-V10.docx`. Images come from the OpenAI Images API through `locgen.py`, not from a built-in image tool, so every agent sends the same request.

Read `FLOW.md` and `PROMPT-GUIDE.md` first. The two runs are `KICKOFF-1-SAMPLES.md` and `KICKOFF-2-BATCH.md`. Run every command from this folder; `python3 locgen.py check` must say `check: OK`.

**Hard rules:**
- The register is the authority.
- No people, helpers, animals or hands.
- Paint only physical inscriptions. Titles and callouts come from `compose`.
- Attach only `spec/plan.json` references.
- At most 3 API calls per record.
- Samples first, with the user's approval before the batch run.
- Never edit `Ref/`.
- Never print the key in `.env`.
