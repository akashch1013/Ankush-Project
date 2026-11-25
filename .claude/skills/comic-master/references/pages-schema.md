# pages.json: the page plan (contract between all stages)

`Tasks/PdfSheetsGenTask/<CHxx>/pages.json`. All paths are relative to `Tasks/`. Boxes are in pt on the 864×648 sheet.

```json
{
  "chapter": "CH02",
  "book": "ChandRush: The Midnight Mela",
  "chapter_label": "Chapter 2 · <topic>",
  "sources": {
    "manuscript": "Reference/Chap 2/CH02-PANELIZED-MANUSCRIPT-V01.docx",
    "register": "Reference/Chap 2/CH02-LOCATION-IMAGE-REGISTER-V04.docx",
    "plates": "BagroundGenTask/ch02/out/plates/"
  },
  "pages": [
    {
      "page": "P001",
      "pattern": "M1 (optional starting grid from patterns.md)",
      "theme": "stage-night (the kit stage class on .page)",
      "title": "Exact heading if the page has one (teaching heading or story title from the manuscript)",
      "purpose": "story: … / teaching: … (one line, for the builder)",
      "beats": ["CH02 01A A", "CH02 01A B"],
      "panels": [
        {
          "id": "P001-1",
          "beat": "CH02 01A A",
          "box": [30, 60, 804, 300],
          "art": {"kind": "new", "item": "P001-1"},
          "background": {"record": "L02_B", "plate": "BagroundGenTask/ch02/out/plates/L02_B.png",
                         "camera": "same as plate | closer on the bench | lower, child eye height"},
          "characters": [
            {"name": "Ahana", "position": "screen-left, midground", "action": "points at the second tray with her right hand",
             "gaze": "the tray", "expression": "curious", "holding": "sketchbook (left arm)"}
          ],
          "props_state": ["upper carrier: 4 × 4 = 16 cup places, all empty", "snack tray removed"],
          "painted_text": ["MAXIMUM LOAD 4.5 kg"],
          "overlay_text": [{"text": "4 × (−2) = −8", "on": "blank cream card in Vihaan's hand"}],
          "reserve": [{"for": "caption", "where": "upper-left", "w": 0.32, "h": 0.30},
                      {"for": "bubble", "where": "upper-right", "w": 0.30, "h": 0.22}],
          "captions": ["Exact CAPTION TEXT paragraph(s), verbatim"],
          "bubbles": [{"speaker": "Vihaan", "text": "Exact Dialogue Copy, verbatim", "where": "upper-right", "tail_to": "Vihaan's mouth",
                       "link": "previous balloon of the same speaker in this beat (optional)"}]
        },
        {"id": "P001-2", "beat": "CH02 01A B", "box": [30, 378, 330, 110],
         "art": {"kind": "zoom", "of": "P001-1", "focus": [0.62, 0.58], "z": 2.4}},
        {"id": "P001-3", "beat": "…", "box": [400, 378, 434, 250],
         "art": {"kind": "reuse", "image": "FInalChangesTask/CH01/out/P018-1.png"}}
      ],
      "teaching": [
        {"block": "T2.1A", "heading": "Exact teaching heading",
         "text": ["Exact paragraph 1", "Exact paragraph 2"],
         "equations": ["3 + 4 − 6 = 7 − 6 = 1"],
         "diagrams": [{"type": "numberline", "args": "--from 0 --to 8 --jump 3:7:+4 --jump 7:1:-6"},
                      {"type": "table", "rows": [["Signs", "Example", "Product sign"], ["…"]]}],
         "questions": ["Exact question text (printed without its answer)"],
         "answers_on_page": false}
      ],
      "asides": [{"speaker": "Tez", "text": "Exact side quote", "art": "library:V-TEZ-02"}],
      "spot_art": [{"item": "V-TEZ-02", "kind": "vignette", "desc": "Tez sitting, paws together, sly grin, Lantern Street fragment"}],
      "notes": "anything the builder must know (continuity, what must not be shown yet)",
      "art": {"idea": "…", "stage": "…", "ornament": "…", "hero": "…", "objects": {}, "illustrate": "…",
              "companion": "…", "colour": "…", "delights": ["…"], "folio": "moonclock --t 0.364", "varies": "…",
              "variation": {"kind": "story", "grid": "…", "border_build": "…", "field": "…", "…": "written by pipeline/vary.py --write"}}
    }
  ]
}
```

Rules:
- `art` (top level of a page, not `panels[].art`) is the art-direction brief: see `PdfSheetsGenTask/design/PAGE-DESIGN.md`. `art.variation` comes from `pipeline/vary.py --write`. The art-director (or the master for 1–2 pages) writes the brief before any art is made.
- **Layout first:** each panel's `box` and `reserve` are final **before** the panel art is generated, because the image is made at that aspect with calm areas where the words go. Size each text block with `python3 pipeline/balloon.py --measure "<text>" --maxw <w>` (a caption is about the same size + 4 pt) and turn it into a `reserve` fraction of the panel.
- `panels[].art.kind`:
  - `new`: panel-artist makes item `art.item` in `FInalChangesTask/<CHxx>/`.
  - `zoom`: a crop of another panel's art, made with CSS (free).
  - `reuse`: an existing image.
  - `plate`: the background plate alone (an empty location shot, free).
- Every string in `captions`, `bubbles[].text`, `teaching[].heading/text/questions` and `asides[].text` must pass `textcheck.py plan`. Copy them exactly. Split long caption groups only at paragraph breaks.
- `equations` lists every equation the page will print. The builder tags each one with `data-math`, and the math-checker verifies them.
- `reserve` areas are fractions of the panel. They must cover where the bubbles and captions will sit.
- `painted_text` holds only short physical markings (≤ 3 characters or the plate's existing inscriptions). Everything longer goes in `overlay_text` (HTML over a blank surface).
