# Fonts

The four faces used by every ChandRush page, as specified in Production Brief V03 §6 and measured in the Opening V04 sample:

| File | Used for |
|---|---|
| `SourceSerif4-Regular.ttf` | narration captions (14/16.1 pt) |
| `SourceSerif4-Semibold.ttf` | reader call-outs (16/18.4 pt) |
| `SourceSans3-Regular.ttf` | page numbers (8 pt); maths body (14/18 pt) on later pages |
| `SourceSans3-Semibold.ttf` | speech balloons (14/16.1 pt); maths emphasis |

**Sources** (downloaded 2026-10-11):
- `adobe-fonts/source-serif` release **4.005R** (`source-serif-4.005_Desktop.zip`, folder `TTF/`)
- `adobe-fonts/source-sans` release **3.052R** (`TTF-source-sans-3.052R.zip`)

**Licence:** SIL Open Font License 1.1 (`LICENSE-SourceSerif4.md`, `LICENSE-SourceSans3.md`). Keep the licence files with the fonts.

The pipeline registers and embeds these exact files, so measuring and rendering use the same fonts, and the PDF does not depend on the fonts installed on the machine.
