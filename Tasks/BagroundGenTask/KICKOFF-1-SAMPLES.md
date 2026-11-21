Run the SAMPLE ROUND of the ChandRush Chapter 01 location images. Work in /home/akasdh/Desktop/Projects/ComicAgent/Tasks/BagroundGenTask and run every command there.

Goal: make 2 sample images (S01-B01 Street level lift bay, M01-D01 Low entrance cart view) that follow Location Image Register V10 exactly and match the supplied masters' look. I will judge these before we spend anything on the full run.

Before writing anything, read FLOW.md and PROMPT-GUIDE.md in full. They are binding. Then run `python3 locgen.py build` and `python3 locgen.py check`; check must say OK.

For each sample, do the per-record loop in FLOW.md section 5:
1. Run `python3 locgen.py brief <ID>`. Then Read every image the brief tells you to attach, the original masters in Ref/, and Ref/CH01-SPATIAL-AUTHORITY-MAP-FINAL.png. Grep work/manuscript.md for the scenes that use this place if it helps.
2. Think hard before writing:
   - Convert every physical left/right into screen positions for this exact camera, and check each against the map.
   - List every count, every on/off state, every physical inscription (exact characters, true minus signs) and everything that must be absent.
   - Decide what each reference contributes and what must not leak from it: its painted title, its annotation words and arrows, other states, its framing.
3. Write prompts/<ID>.md using the PROMPT-GUIDE skeleton, with PROMPT, CHECKS and CALLOUT PLAN sections. Never put the title or the callout texts in PROMPT.
4. Run `python3 locgen.py lint <ID>` until it says ok. Then run `python3 locgen.py gen <ID> --dry-run` and read out/tmp/<ID>-gen-prompt.txt once, end to end, as the model will see it. Tighten anything vague or contradictory.

Generate both samples in one immediate call: `python3 locgen.py gen S01-B01 M01-D01`. The settings are fixed in spec/plan.json: gpt-image-2.5-sunburst, 1024x768, n=1, at each record's quality (high, or xhigh where the plan marks it). Never use max without my approval.

Then QC each plate like a strict art director:
- Read the plate at full size.
- Use `grid` and `zoom` on every item in its CHECKS: inscriptions letter by letter, counts, lamp states, sides, the clear areas the callouts need, and continuity with the master.
- Verdict, per FLOW.md section 5.8:
  - pass: `qc <ID> pass`;
  - fix: one or two local defects, one precise `fix` each;
  - regen: revise the prompt, then `qc <ID> fail --regen` and run `gen` again.
- Never go past 3 API calls for a record without asking me.

For each approved plate, run `callouts <ID>`. Place every target from the `grid` image, following the register's wording. Then run `compose <ID>`, Read the final and adjust until each leader points at the right place and no box covers anything the register says must stay visible.

Finish with `python3 locgen.py sheet --samples` and `python3 locgen.py cost`. Then STOP and report:
- the sheet path and both final image paths;
- for each record: its verdict, the CHECKS results, calls used, and the real tokens and cost per image;
- anything in the register or masters you found contradictory;
- what you would change in PROMPT-GUIDE.md or spec/style.txt before the batch run. Propose these changes; don't apply them.

Do not generate any other record. Do not start the batch run.
