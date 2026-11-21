# Sources and continuity

## Source authority

The known Chapter 01 baseline is CH-01-PANELIZED-MANUSCRIPT-V10.docx, CHANDRUSH-PAGE-DESIGN-MANUAL-V05.pdf (54 pages), CHANDRUSH-PAGE-PRODUCTION-CHECKS-V02.txt (40 checks), and ChandRush-V10-Design-Support.zip. Use a later version only when clearly author-approved. V02 supersedes older checklists inside support archives. Treat this baseline as discovery guidance, not evidence that local files have these contents.

Read the actual manuscript for content, page/panel assignments, source order and story state. Later explicit author corrections apply only within their stated scope. Use manual examples for design, never to introduce teaching or dialogue. Read the support instructions, manifest, source hashes, panel briefs, asset register, diagrams and review requirements. Refresh stale derived data without rewriting the manuscript.

Record per source: relative path or durable file identifier, exact filename, version, SHA-256, observed approval evidence and purpose. Compare ZIP manifest hashes to actual manuscript/manual hashes. Archive supplied originals unchanged. Inspect DOCX runs, numbering definitions, tables, equations and source diagrams when plain-text extraction omits information. Do not infer missing numbering from paragraph text alone. Preserve emphasis and symbols, including minus versus hyphen, multiplication, powers, roots, fractions and units.

Use stable source block IDs to map every learner-facing block and required visual to a page/panel and placed object. Keep production directions in the source inventory but off finished pages. Record intentional blanks. Check exact strings/runs against native source objects; if PDF text is outlined, supplement visual comparison with live-story inspection. Text extraction alone cannot verify mathematical diagrams or an outlined PDF.

## Reusable manual review

Save the complete full-review record, its supporting evidence, and a section/example index. Example structure (values must be observed, never prefilled):

```json
{
  "filename": "actual manual filename",
  "version": "actual version",
  "sha256": "actual digest",
  "page_count": 54,
  "full_review_completed": true,
  "reviewed_at": "actual date",
  "evidence_files": ["relative/path/to/full-review-evidence.json"],
  "sections": [{"title": "actual heading", "pages": [1, 2]}],
  "visual_examples": [{"pages": [2], "description": "observed example", "inspection": "specific observation"}],
  "reviewed_pages": [{"page": 1, "text_reviewed": true, "visuals_reviewed": true, "observation": "specific observation"}]
}
```

The short example does not represent a completed review. Record every actual page and example. If the complete review cannot be verified, review the entire current approved manual again. A matching filename, summary or unsubstantiated boolean is insufficient. On hash match plus verifiable full evidence, reuse that review and inspect the current pages' applicable sections and examples. Record those batch-specific revisits separately without duplicating the entire manual commentary.

## Continuity and author approval

Inspect approved masters at useful resolution. Record distinguishing features, costume, proportions, staff/bell and other prop ownership, current location and lighting. Use the latest approved preceding page; if only an unapproved proof is available, label it and compare its state to the manuscript. Do not silently call it approved or invent a missing approval.

Carry forward reusable general preferences: expand scenery into suitable unused space; give important story scenes prominence; vary meaningful poses; make books recognisable; vary fair-related devices and corners. Preserve open teaching layouts when density requires them. Prior requests for a particular page or character scene are not blanket permission to add those images everywhere.

No new witty quotes, story events or repair-state changes. An optional character, prop or decorative object must be supported by the manuscript/manual and relevant author instructions; it cannot change the teaching or imply a new action. Check inscriptions against the actual owner and physical surface.
