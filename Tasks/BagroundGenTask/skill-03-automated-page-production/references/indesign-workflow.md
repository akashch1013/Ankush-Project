# Native InDesign production

## Route and fonts

The verified workflow constructs native IDML objects and has Adobe InDesign open and export the IDML. Native IDML construction is not itself an InDesign export. Discover the current tools by name/description; do not assume yesterday's tool or access remains available. Retain actual operation receipts, source hashes and results. Use a small existing-page export to establish a changed route before artwork.

The known Adobe connector route is `adobe_asset_openai_file_upload` followed by `adobe_document_render_layout`. Read the current schemas before calling. Upload the absolute local IDML/INDD path; omit an Adobe destination unless the user specifies it. Take the actual returned asset URL as `documentSourceUrl`. For a one-page file, use pageRange `1-1`, outputMediaType `application/pdf`, colorSpace `RGB`, resolution `300`, quality `maximum`, useDocumentBleeds `false`, createSeparateFiles `false`. Wait for or resume the existing request according to the connector. Never issue duplicate in-flight exports.

Save a current page source only after its artwork and pre-export composition review. Upload each revision once. A failed download should first be retried from the existing export URL. Record the reported length when available and actual length/hash; opening a partial download is not acceptance. Verify each PDF has one 864 × 648 pt page and matching media/trim/bleed boxes. Preserve valid unaffected exports.

The V05 baseline roles are Source Sans 3 for teaching and mathematics, Source Serif 4 Semibold for headings, Source Sans 3 Semibold for story speech, and Source Serif 4 Regular for narration/asides. Verify against the current approved manual. Locate the exact approved font files in the project or preceding editable delivery package: SourceSans3-Regular.otf, SourceSans3-Semibold.otf, SourceSerif4-Regular.otf, SourceSerif4-Semibold.otf and DejaVuSans.ttf for a required missing maths glyph. Pass their directory explicitly to the helper. Verify their hashes and preserve the accompanying licenses in delivered source packages. Do not substitute fonts if these inputs are missing. A replacement approved manual may require additional fonts or capabilities; extend the helper rather than substituting silently.

## Native helper

Requirements: Python, lxml, Pillow and fontTools; PDF utilities additionally use PyMuPDF. Import `Book` and `C` from `scripts/native_idml.py`. `type_paths.py` is its glyph-path dependency. `assets/idml-template` contains blank native structure; it supplies no story content or page layout. Do not use a previous page-specific layout script as the generic design for all pages.

```python
from native_idml import Book
book = Book(outline=False, artwork_dir=project_artwork, font_dir=project_fonts,
            document_name=document_name, report_dir=qa_directory)
book.newpage(page_number)
# Add exact source content at positions from this page's reviewed plan.
# book.text(text, x, y, width, height, size=14, font='Source Sans 3',
#           runs=exact_source_runs, label=source_block_id)
# book.image(filename, x, y, width, height, fit='contain', panel=panel_id)
book.save(editable_idml_path)
```

Coordinates and type sizes are in points on an 864 × 648 pt page. The caller supplies every content item and layout. Methods: `box`, `image`, `text`, `path`, `ring`, `star`. Add custom native vector geometry for exact mathematics; do not generate counted or precisely labelled diagrams as raster art. Use separate native objects for illustrations, lettering, diagrams, inscriptions, balloons and furniture; add named layers in the project assembly code where useful.

`text` accepts exact runs with `text`, optional `font`, `bold` and `no_break`. The helper checks unsupported italic/underline/vertical alignment and missing glyphs instead of dropping them. It is not a general Word/MathML renderer. For unimplemented source styling, fractions, scripts, rotated/perspective inscription text or complex geometry, implement the required native objects explicitly and verify them in InDesign. Do not simplify manuscript notation to fit the helper. Use 14 pt or larger for essential material; require explicit page permission for 13 pt.

`image` supports contain/cover without stretch, focal_x/focal_y and an optional top crop; inspect the actual final crop. A top crop anchors the remaining image at the frame top. It embeds native pixels and records effective PPI. Package the original linked assets as well. Images keep their existing transparency. Inspect transparency and colours in the actual export.

`outline=False` produces live editable stories. `outline=True` adds native glyph outlines and keeps nonprinting live text objects. If the server cannot render the required fonts reliably, build both variants from the same source strings, runs, coordinates, assets and font files. Export the outline variant through InDesign; deliver the corresponding live-text variant and clearly identify both. This is a disclosed font-rendering accommodation, not live-text preflight. Verify correspondence after each edit. Retain actual native font/overset results when available; otherwise mark those required checks NOT CHECKED. Do not label an outlined export as proof that the live document has no missing fonts or overset.

The helper's text-fit report is a calculated local guard. InDesign shaping, kerning and line composition can differ; inspect the real export. Static Fonts.xml status values are metadata, not an installed-font test. Never reuse a computed report as a visual PASS.

## Utility commands

Run `python scripts/production.py --help` and subcommand help for arguments. Output reports are JSON. Relative manifest paths resolve against the manifest file's directory.

- `hash FILE...`: exact file digests and byte counts.
- `image FILE --width-pt W --height-pt H --fit contain|cover [--crop X Y W H]`: resolution after the actual pixel crop. No resampling.
- `pdf FILE [--pages N] [--reported-bytes N] [--render-dir DIR]`: page geometry, opening/rendering and raster placement report. This does not certify all colour-space usage or design quality.
- `review-template CHECKLIST --pages 92 93 --out FILE`: extract the 40 current check IDs; initialise every status as NOT CHECKED.
- `review-check FILE --checklist CHECKLIST`: validate check coverage, evidence fields and current PDF hashes. Report unresolved checks; never infer PASS from a report's existence.
- `merge MANIFEST --out FILE`: copy verified page objects without rasterising; require PDF, source and receipt hashes, ordered page IDs and matching source PDFs. Compare rendered pixels, raster image data and boxes before accepting the combined result. This verifies packaging, not content or approval.

Example merge manifest:

```json
{"pages":[{"page":92,"pdf":"exports/P092.pdf","pdf_sha256":"actual digest","source":"source/P092-EXPORT.idml","source_sha256":"actual digest","receipt":"qa/P092-export.json","receipt_sha256":"actual digest"}]}
```

For a retained export from a larger source revision, independently prove that all relevant per-page content, images, fonts, styles and code dependencies are unchanged. Keep the original exported-source hash and the equivalence evidence; do not replace it with the hash of a file Adobe never opened. Prefer independent page documents to avoid this ambiguity.
