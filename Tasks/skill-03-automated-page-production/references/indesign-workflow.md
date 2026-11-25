# InDesign placement and export

## Build the package for one designed page

Use one UTF-8 JSON plan per page. Keep it beside its packaged linked assets. Use the current edition's page size and reading direction. Use points with the origin at the top left of the trimmed page, x increasing right and y down. All boxes are `[x,y,width,height]`. Margin, bleed and inset arrays are `[top,left,bottom,right]`. Give art, diagram, balloon shape, lettering and page furniture meaningful separate layers as applicable. Layers are listed back to front. Items are drawn in listed order within each layer. The chronological reading order belongs in the design brief and source mapping.

Include in the accompanying scene brief the original location title/file, crop or derived-camera instructions, the actors and scene state, the final artwork file, the reason for the panel shape and which exact manuscript blocks it owns. A single composite illustration can hold its finished characters and location, while lettering, balloons and any instructional marks remain independently editable.

For the whole page, include the manual section or visual example guiding the composition and the master or sub-location that supplied the palette and motif. In the existing `swatches` field, give the actual RGB or CMYK values used in the design, including derived reading tints. Apply the named swatches to background fills, borders, embellishments and maths strokes or fills as appropriate. Use the same values and colour meanings in linked vector diagrams. Keep the reference notes and colour samples in the working brief.

### Placement plan

| Field | Meaning |
| --- | --- |
| `page` | `id` as text and trim `size:[width,height]` in points. Optional `margins` and `bleed` as above (zero if omitted). Set optional `blend_space` to RGB or CMYK when the edition specifies transparency blending. Set `intentional_blank:true` for a page with no objects. For PDF export set `pdf_preset` to the exact installed preset matching the edition. |
| `layers` | Unique names, back to front. |
| `swatches` | Named RGB triples (0–255) or CMYK quadruples (0–100). Omit fill or stroke for transparency. Paint the designed background with a page-sized shape if it will be visible. |
| `styles` | Named paragraph styles with exact `family`, `face`, `size`, `leading` and swatch `color`. Optional `align` of left, center or right and `space_after` in points. Use the actual project's font roles. |
| `items` | Each has a unique `id`, `panel` (or a page-level identifier), `layer` and `kind`. Use `source` for manuscript or figure ownership. Use `box` for every kind except path. |

| Kind | What InDesign receives |
| --- | --- |
| `image` | Relative `file` under the package, `fit` of cover or contain, optional `focus:[x,y]` from 0 to 1 and `zoom` of 1 or greater. Focus aligns the available overflow or spare space, from left/top to right/bottom. Link the actual final panel art or a checked vector. Supply `asset_page` for a specific page of a linked PDF (one-based, default 1). For a precisely prescribed source window record its pixel rectangle and prepare that exact view as a derivative, with the original retained. |
| `shape` | A `shape` of rectangle or ellipse with optional `fill`, `stroke`, stroke `weight` and rectangle corner `radius`. Give each caption or balloon its own body or use a closed path with an integrated tail. |
| `path` | Page-space `points`, optional `closed`, `fill`, `stroke` and `weight`. Use straight points `[x,y]` or Bézier nodes `[[leftX,leftY],[anchorX,anchorY],[rightX,rightY]]`. Use for a balloon outline and tail, axis, tick, diagram or rule. |
| `text` | `role`, `source`, `style`, exact `text`, `box` and optional `inset`. Preserve paragraph breaks with newlines. For styled spans supply `runs` whose text concatenates exactly to the block. A run may set another named `style`, `position` of superscript/subscript/normal, `no_break` or `underline`. The frame remains live. For spoken dialogue use role `speech`, add `speaker` and the shape/path ID in `tail`. Use `tailless:true` in place of a tail only when the assigned treatment calls for it. |

A small example of the plan shape follows. Use the current edition’s dimensions and fonts, and replace the illustrative swatches with the palette chosen from the project sources.

```json
{
  "page": {"id":"sample", "size":[420,540], "margins":[24,24,24,24]},
  "layers": ["Background","Lettering"],
  "swatches": {"PaperTint":[246,245,239], "Ink":[31,43,51]},
  "styles": {"Narration":{"family":"Arial","face":"Regular","size":14,"leading":18,"color":"Ink"}},
  "items": [
    {"id":"field","panel":"page","kind":"shape","layer":"Background","shape":"rectangle","box":[0,0,420,540],"fill":"PaperTint"},
    {"id":"words","panel":"a","kind":"text","layer":"Lettering","role":"caption","source":"paragraph-1","style":"Narration","text":"Sample caption.","box":[24,30,310,50]}
  ]
}
```

## Assemble and export

Run `python scripts/indesign_handoff.py path/to/plan.json` from the skill directory. This validates the plan and linked files and writes `plan-place.jsx` beside it, using the actual plan's stem. Use `--check` to validate only. Use `--idml` to also create the linked, editable IDML immediately for live text, native paths or shapes and ordinary JPEG, PNG or TIFF placements. For a remote renderer that cannot access external links, add `--embed-images` to build a separate self-contained export copy from the same plan. Keep the matching linked IDML as the editable source. Let the generated JSX place supplied PDF/SVG or orientation-tagged art using native Adobe import. For a multi-image source other than PDF, supply a single selected view. The script contains the exact placements and copy. If an established runner uses another schema, map these fields to its accepted inputs and verify the result.

Run the generated JSX using a verified Adobe InDesign execution route or the desktop Scripts panel. Move the whole handoff folder together. The JSX makes a new result directory for each attempt and builds the linked INDD and IDML. It checks actual font availability, links, exact placed text and overset and records its observations. It exports a PDF when the plan names a valid edition preset and the checks pass. For an edition specified by output settings instead of an installed preset, use those settings in the verified project export route. Flag precisely which native checks or exports are pending when only a desktop handoff or interim proof is feasible. A connector that only renders an existing IDML needs the actual editable document, linked resources or a verified self-contained export copy, and its own supported input format.

Existing project builders may import `scripts/native_idml.py` and `scripts/type_paths.py` to reproduce their configured IDMLs. They have their own geometry and font conventions. Use the plan-based runner for new assignments with other settings, or adapt an existing project builder explicitly. An outline proof requires a matching live-text source. Inspect complex glyphs and line breaks in the Adobe export.

## Verify the proof

Open the exported PDF at reading size. Verify the page order, intended trim/bleed, colour, links, live fonts, overset, mathematical notation and lettering clearance. Inspect a batch page by page. `scripts/production.py` provides `hash`, `image`, `pdf`, `review-template`, `review-check` and `merge`. See each command's help. Pass the edition's expected trim, box and resolution criteria as applicable. Keep individual native export evidence before combining pages. Distinguish an interim reading proof from the final Adobe export.
