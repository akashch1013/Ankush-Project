Run the FULL RUN of the ChandRush Chapter 01 location images through the OpenAI Batch API, which costs 50% less. Work in /home/akasdh/Desktop/Projects/ComicAgent/Tasks/BagroundGenTask and run every command there.

The sample round is approved: S01-B01 and M01-D01. Their prompts (prompts/S01-B01.md, prompts/M01-D01.md) are the quality bar.
Changes I approved after the samples: <write them here, or "none">.

Goal: all 32 Register V10 images approved, annotated and composed in out/final/. Every image must follow its register record exactly and match the masters' look. Spend as few API calls as possible.

Read FLOW.md and PROMPT-GUIDE.md in full first; they are binding. Then run `python3 locgen.py build`, `python3 locgen.py check` and `python3 locgen.py status`. Read the two approved sample prompts and their final images.

Work wave by wave (FLOW.md section 7): wave 1, then 2, then 3. A wave starts only when every record it depends on is approved; later waves attach this run's approved plates as references.

For each wave:
1. Write prompts/<ID>.md for every record of the wave that has none, using the full per-record loop (FLOW.md section 5, steps 1–5).
   - Read every attached image. In waves 2–3 these are the approved plates: name the exact design details the new view must keep, and in state-edit mode list "Change only" precisely.
   - Think hard about screen sides, counts, inscriptions, states and leaks for every record.
   - Run `lint all` and dry-run each prompt; read the composed prompt text once.
2. Run `python3 locgen.py batch build --wave N` and check the listing. Then run `python3 locgen.py batch submit` and `python3 locgen.py batch wait <name>`. Run the wait in the background; it polls and fetches when the batch ends.
3. QC every returned plate strictly, as in the sample round (grid/zoom every CHECKS item):
   - pass: `qc <ID> pass`;
   - small local defect: `fix <ID> "<one precise change>" --queue`;
   - prompt-level problem: revise the prompt, then `qc <ID> fail --regen`.
4. If anything is queued or marked regen, run `batch build --wave N` again, then submit and wait, and repeat QC.
   - Never exceed 3 API calls per record. A record that hits the cap goes on my list; carry on with every record that does not depend on it.
5. Move to the next wave only when this one is approved, apart from records on my list.

After wave 3, for every approved record:
- run `callouts`, place targets from `grid`, run `compose`, and Read the final to check it;
- then run `python3 locgen.py sheet`, `sheet --wave 1/2/3`, `cost` and `status`.

Report:
- sheet paths and anything not approved, with why;
- every fix or regen and its reason;
- total spend split into immediate and batch;
- any register contradictions you hit.

Rules:
- Use only the Batch API. Use immediate `gen` or `fix` only if I approve it for a named record.
- Titles and callouts are only ever added by `compose`; never put them in a prompt.
- Do not edit Ref/. Edit spec/ only to correct a plan error, and tell me.
- If more than a third of a wave fails QC, stop and tell me before spending more.
- Quality is high, or xhigh only where spec/plan.json marks a record hard. You may escalate a high record to xhigh once if it failed on rendering precision (FLOW.md section 3), and tell me. Never use max.
