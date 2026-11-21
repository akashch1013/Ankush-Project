# 04 · Prompting — writing panel prompts that work first time

A prompt file is the **complete, self-contained work order** for one panel's artwork. The image model sees only the prompt text and the attached images. It knows nothing about the project, the earlier pages or the manuscript, so everything it needs must be in those two things.

## File anatomy (`batch/<id>/prompts/CH01-P0xx-PNyy.md`)

1. **Job card** (YAML between `---` lines). The pipeline reads these fields:
   - `panel_id`, `job_key`, `page`, `panel`, `title`;
   - `queue`: the generation order. Scene anchors come first: the first panel of each location and each character group;
   - `characters`, `frame_pt`;
   - `size`: the legal gpt-image-2 size at about 300 ppi. `fallback_size` and `fallback_rule` cover tools with fixed 3:2, 2:3 or square output;
   - `attachments`: `source` and `role` for each image. **Their order is the order the prompt calls Image 1, Image 2, ….**;
   - `anchors`: earlier panels of the same scene. When approved they are added automatically as the next image;
   - `exceptions` (LOC-EX ids) and `manuscript_note` (source block ids);
   - `review_needed: true` only on drafts. Lint fails until it is removed or set to false.
2. **Attach these images**: a table with each numbered file in `prompts/refs/<panel>/` and its role.
3. **Prompt**: exactly one ```text block. This is what gets pasted or passed to the tool.
4. **Size**: preferred and fallback, with the band to keep key content inside.
5. **Accept only if**: the checklist the reviewer ticks. Any failure triggers one retry, then REVIEW_LATER.
6. **Source**: the text the pipeline will letter (so the writer can reserve space) and the manuscript note, verbatim.

## The prompt lines, in order (Codex imagegen schema)

```text
Use case: illustration-story
Asset type: one graphic-novel panel, artwork only (all lettering is added later); output WxH px (aspect about A:1)
Input images: Image 1: <role>; Image 2: <role>; ...; Image N+1 (only if attached): an approved earlier panel ...
Primary request: <one sentence: what happens in this panel>
Scene/backdrop: <place + the state corrections for this moment>
Subject: <who, where in frame, own-left/right hand use, gaze, expression, props; identity hints; Tez stripe colours>
Style/medium: <the approved look; match the continuity image>
Composition/framing: <camera, frame aspect, where subjects sit, which area stays calm for the caption/balloon, fallback band>
Lighting/mood: <time of day, light sources, mood>
Constraints: <keep identities from sheets; keep architecture; sheets for appearance only, panel for pose/props>
Avoid: <no text/lettering; ignore reference labels and arrows; no crescent sky moon; panel-specific exclusions>
```

**Why this order:** the model weighs early lines most. Who and what come before style. Every line is a visible result, not a production instruction.

## Input images: what to attach and why

| Order | Image | Role wording | Why |
|---|---|---|---|
| 1 | The panel's primary location reference (first named in the manuscript) | "location reference … (architecture, materials, palette)" | Keeps the place recognisable |
| 2 | A continuity image (`design/continuity/…`), or later an approved panel from the same scene | "match its rendering style, lighting and the characters' look; do not copy its composition" | Keeps the soft stylised-3D look of the approved pages, plus details sheets don't show (crescent tickets, Tez's blue painted stripes) |
| 3+ | One character sheet per character, in manuscript order | "<Name> character sheet (identity)" | Faces, hair, outfits |
| last (optional) | Approved anchor panel from this batch | "only if attached: … match its lighting, rendering and the characters' appearance exactly" | Consistency within the scene |

- Keep it to seven images or fewer: web UIs accept around ten, and attention spreads thin.
- The `refs` command numbers the files in this order, so a person can drag them all at once.

## Identity hints

Each character's first mention in **Subject** gets a short card from `design/characters.json`, for example "Navya (two long dark braids, maroon jacket …, tan crossbody pouch)". This anchors which sheet is which name.

Leave out sheet lettering such as the T-shirt slogan and sketchbook words. Story art shows them plain, and lettering would break rule P5.

## State corrections: the most common failure, so be explicit

Write the current state in **Scene/backdrop**, especially where the reference image shows a different one. For this batch:

- The Old Blue Gate's violet light seam is **off** (since p6). The hatch stands **slightly open on darkness**. On p11 the small door is open **wide enough for a child**.
- The empty ring above the gate is an ornament. **Leave it empty** (LOC-EX-11).
- Entry Court: the Lantern Street archway is **dark**, the Bell stand is **empty with a slack rope**, and there is **no Moon Bell anywhere**. Do not add labels or numbers to the map (LOC-EX-10).
- Tez: the stripes are **painted blue**, and the left-shoulder stripe and first flank stripes are **pale grey**. This overrides his sheet. Copy the manuscript sentence for each scene.
- Tara's staff stays exactly as on her sheet. It is part of her costume, and its finial is not the Moon Bell.

## Composition and calm areas

Copy the Director's `compose` sentence from the layout. It already says where the subjects sit and which area stays calm (for example "upper-left 46% × 30% calm for a caption"). Say what the calm area should contain ("dark gate stone or night sky"), so the model has something real to paint there.

## Sizes

- **Preferred:** the frame's aspect at about 300 ppi. Edges are multiples of 16, the ratio is at most 3:1, and the total is at most about 3.7 MP. The pipeline computes this (`legal_gen_size`).
- **Fixed-size tools** produce 1536×1024, 1024×1536 or 1024×1024. Add the line "If you can only make 3:2 images, keep every important element between X% and Y% of the height". The `fallback_rule` in the job card gives X and Y.
- `ingest` accepts any size, and `review` shows exactly what the frame will keep.

## Accept-only-if checklists

Turn each clause of the manuscript's **Static visual** into one checkable line: position, hand, gaze, prop, state. Add "No lettering anywhere" and the calm-area check. List the harmless variations separately, so reviewers don't waste a retry on them.

## Drafting for a new batch

`python -m pipeline prompts draft` builds a near-complete draft per story panel. It takes:
- Camera, Static visual, the stripe sentence and the lighting from the manuscript note;
- the frame and `compose` from the layout;
- the identity cards and location corrections from `design/`.

Then the writer:
1. sets `queue` (anchors first) and adds the continuity image and `anchors`;
2. writes the one-line Primary request and confirms the scene corrections. Every `REVIEW:` marker must go;
3. makes the hands explicit ("own left hand"), trims repeats and completes the checklist;
4. sets `review_needed: false` and runs `prompts lint`.

## What `prompts lint` enforces

- The YAML parses and the required fields are present. The ID and job key match the manuscript.
- Every manuscript reference is attached and every source file exists.
- Each `Image N` is explained, and no image number is mentioned beyond the attachments plus optional anchors.
- No filenames, panel IDs, `[placeholders]`, `TODO` or `REVIEW:` markers are left.
- No printable manuscript sentence appears in the prompt.
- An `Avoid:` line forbids text, the size is legal, and the prompt is under 4200 characters.

## Targeted correction (instead of regenerating)

When the composition and identities are right but one detail is wrong, edit that image. Attach the failed version as Image 1, plus the sheet if identity matters:

```text
Use case: precise-object-edit
Input images: Image 1: the panel to correct; Image 2: <Name> character sheet (identity)
Primary request: change only <the wrong detail> to <the exact visible result>.
Constraints: keep <nearby important feature> fully visible; preserve everything else exactly: characters, faces, pose, location, lighting, colours and composition.
Avoid: any text or lettering; any other change.
```

For example: "change only Tez's stripes from black to blue, keeping the stripe on his left shoulder and the first stripe on each flank behind the front legs pale grey."

## Common failures and the fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Label boxes or arrows copied from the reference | Role not stated | It is already in Avoid; if it persists, make a targeted edit removing them |
| Text or letters in the image (tickets, map, T-shirt) | Model filling empty surfaces | Targeted edit: "remove all lettering, leave surfaces plain" |
| Wrong hand or mirrored pose | Viewer-relative wording | Use "her own left hand", and say where the hand points |
| Characters swapped | Identity cue missing | Put the identity hint at the first mention; check sheet order matches Image numbers |
| Tez with black stripes | The sheet dominates | Targeted edit with the stripe sentence |
| A bell appears on the stand or above the gate | The model "completes" the empty ring | Say "empty" in Scene and Avoid; targeted edit to remove |
| Caption area busy | Calm area not described | Say what fills it ("dark gate stone"), or adjust `frame --focus` |
