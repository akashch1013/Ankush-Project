---
name: chandrush-director
description: Plan ChandRush graphic-novel pages before any art is made. Choose the next batch, extract exact page contracts from the V07 manifest, read every panel and inspect its reference images, write the page brief (story beat, continuity state, keep/ignore/correct for each reference), and lay out frames and caption/balloon positions that are proven to fit. Use whenever someone wants to start new ChandRush pages, plan or lay out a page, decide panel sizes, check what a page needs, or continue the comic to the next pages, even if they only say "do the next five pages".
---

# ChandRush page director

You decide what each page contains and where everything goes, so that later steps (prompts, art, assembly) only execute decisions. Mistakes here are cheap to fix. Mistakes found after image generation are expensive.

Work in `Approach1/`. Commands are `python -m pipeline ...`. Background: `guide/00_OVERVIEW.md`, `guide/02_RULES.md`, `guide/03_DESIGN_SYSTEM.md`.

## Steps

1. **Pick the batch.**
   - Default 5 pages, never more than 10.
   - Skip pages the samples already cover (table in `guide/07_ISSUES_AND_DECISIONS.md`) unless the user asks.
   - Run `python -m pipeline new-batch --pages 14-18`.
2. **Extract.** Run `python -m pipeline --batch <id> extract`. Stop and ask the user if:
   - the checksum does not match;
   - a reference is missing (see `design/reference_map.json`; never substitute a different state);
   - a panel has an open detail.
3. **Understand each page.**
   - Read the contract's page notes and every panel's printable blocks and visual note in full.
   - Open each reference image, and the previous pages' approved art, and look at them.
   - Write `pages/CH01-P0xx.brief.md`, following `batch/P009-P013/pages/CH01-P009.brief.md`.
   - Be concrete about states that change between pages (gate light, hatch, lamps, Tez's stripes, props, which hand). These are what image models get wrong.
4. **Lay out each page** in `pages/CH01-P0xx.layout.json`. Copy the closest example from `batch/P009-P013/pages/` and change it.
   - Give the meaningful beat the larger frame.
   - Size each frame so its caption covers at most about a third of it.
   - Write a `compose` sentence saying where the subjects sit and which area stays calm for text.
   - Pick a `theme` and `border` from `design/tokens.json`. Keep scenes consistent and vary borders across pages, like the sample.
   - Add a caption, balloon or reader item for every printable block. The build refuses to run if a block is missing or doubled.
5. **Prove it.** Run `python -m pipeline proof` (grey, text boxes outlined), then `python -m pipeline build --mode standin --dpi 110`. Open the PNGs in `output/proofs/` and look at them. Fix any ERROR by changing frames or measures, never by shrinking type.

## Done when

- Every page has a contract, a brief and a layout.
- The proof builds without errors.
- You can say in one sentence per page what the reader should notice first.

Hand over to `chandrush-prompt-writer`.
