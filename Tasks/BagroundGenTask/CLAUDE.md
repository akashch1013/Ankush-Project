# CLAUDE.md: ChandRush CH01 location images (Register V10)

This folder makes the **32 Chapter 01 location images** defined by `Ref/CH01-LOCATION-IMAGE-REGISTER-V10.docx`. They are generated through the OpenAI Images API (`gpt-image-2.5-sunburst`, quality `high`, or `xhigh` for the hard records marked in `spec/plan.json`, 1024×768; never `max` without the user's approval) with `locgen.py`.

Read `FLOW.md` (the procedure) and `PROMPT-GUIDE.md` (how to write each prompt) before doing anything. Kickoff prompts:
- `KICKOFF-1-SAMPLES.md`: sample round, immediate API.
- `KICKOFF-2-BATCH.md`: full run, Batch API.

**Hard rules:**
- The register is the authority.
- No people, helpers, animals or hands.
- Paint only physical inscriptions, exactly. Titles and callouts are added by `compose`, never by the model.
- Attach only the plan's references. Never the spatial map, the old Locations pack or anything in `archive/`.
- At most 3 API calls per record without the user's approval.
- Samples first; never start the batch run before the user approves them.
- Never edit `Ref/`.
- The API key is in `.env` (`CHATGPT_API`). Never print it.

`archive/` holds the retired Draft 02 (27 records) and v1 (70 plates) workflows. Don't use them.
