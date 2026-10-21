# HIGGSFIELD-NOTES: recipe for the Higgsfield MCP route

**Status:** not probed yet. The first Claude run of `/chandrush-backgrounds samples` fills this in before any worker starts. Every worker then follows it exactly.

## To record

| Item | Value |
|---|---|
| MCP server / connector | |
| Image tool name(s) | |
| Model for new views | GPT Image 2 (preferred): exact id = |
| Model for state edits (007, 009, 013, 016, 020, 023) | GPT Image 2, or Nano Banana Pro if edits drift: exact id = |
| How reference images are passed | local path / upload tool → URL / URL only |
| Max reference images per call (records use up to 3) | |
| Aspect parameter name and values used | 16:9 = , 4:3 = , 3:2 = |
| Largest size / quality option (4K?) | |
| Result format | URL / job to poll / asset id → URL |
| Credits per image (observed) | |

## One exact example call (copy of a call that worked)

```text
(to be filled in)
```

## Uploaded reference URLs

Accepted images are uploaded once. Use the native file under `output/native/`, which is smaller than the upscaled one. Cache the URLs with `python3 bg.py urls set <path> <url>` and look them up with `python3 bg.py urls get <path>`; the cache lives in `output/_uploads.json`.

**Expected credits:** 27 records + 7 extra anchor candidates (001 ×3; 002, 008, 015, 019, 024 ×2) + fixes ≈ 40–50 generations.
