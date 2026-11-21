# ChandRush CH01 location images: Register V10

These are the 32 location reference images of `Ref/CH01-LOCATION-IMAGE-REGISTER-V10.docx`. Each is 4:3 at 1K, with the register's exact two-line title in an ivory band above the scenic frame and its exact callouts. Every image uses the filename the register gives it.

```
Ref/ (authority)        register V10 · spatial map · 3 masters · panelized manuscript
   │  python3 locgen.py build
   ▼
work/briefs/<ID>.md     all the data for one record + its references (masters or approved plates)
   │  agent (Claude Opus, xhigh) studies it and writes prompts/<ID>.md      ← PROMPT-GUIDE.md
   ▼  lint → dry-run
gpt-image-2.5-sunburst  /v1/images/edits · quality high (xhigh for 8 hard records) · 1024x768 · refs as data URLs
   │  samples: `gen` (immediate)   ·   full run: `batch build/submit/wait` (50% off), wave 1 → 2 → 3
   ▼
out/plates/<ID>.png     clean scenic frame → QC (grid/zoom vs CHECKS) → pass | fix | regen
   │  callouts/<ID>.json + compose
   ▼
out/final/<register filename>.png   title band + callouts, exact text
```

| Start here | |
|---|---|
| `FLOW.md` | the procedure: sources, settings, waves, QC, commands, rules |
| `PROMPT-GUIDE.md` | prompt skeletons, writing rules, per-family traps |
| `KICKOFF-1-SAMPLES.md` | prompt for a new Claude session: the sample round |
| `KICKOFF-2-BATCH.md` | prompt for a new Claude session: the full run through the Batch API |
| `spec/plan.json` | references, waves and modes per record; model settings |
| `spec/style.txt`, `spec/rules.txt` | appended to every prompt |
| `locgen.py` | the tool (`python3 locgen.py -h`) |

The earlier workflows are in `archive/`: Draft 02 with 27 records, and v1 with 70 plates. They are kept for history only.
