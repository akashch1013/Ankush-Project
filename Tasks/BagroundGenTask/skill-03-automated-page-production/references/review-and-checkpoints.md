# Review and checkpoints

## Image gate

Before requesting the next image, inspect the current asset against its exact source brief and approved references. Record identity and proportions, authored action, anatomy, prop owner, location, support/contact, lighting, repair state and intended lettering space. Inspect the intended placement/crop, both at normal page scale and in detail. Check native-pixel effective PPI and actual sharpness. Check figure-plus-scenery integration and the outer vignette edge.

Where exact mathematical evidence is required, verify quantities and geometry explicitly. AI art does not reliably establish counted objects or measured shapes. Use editable native geometry for exact mathematics and inspect its integration with the scene. Do not merely count source blocks.

Record artwork status as candidate, internally-reviewed or author-approved, with approval evidence only for the last state. New generated assets remain candidates even if internal checks pass. Referencing a previous generated asset for continuity does not promote its approval state.

## Page gate

The assembled composition can reveal defects not present in an isolated image: balloon tails crossing hair/hands, inscribed text missing a face's perspective, crops cutting off feet, objects unsupported by scenery, insufficient contrast or an image dominating teaching. Inspect these before export, then inspect the actual InDesign PDF again.

For maths-page scenery, include the region actually extended, remaining open-space purpose, character grounding, boundary treatment and teaching clearance in the existing relevant checklist entries. Revisit the maths-page art-direction reference linked from SKILL.md. Treat a cramped vignette beside unexplained unused space as a composition defect even when the source text and image resolution are correct.

Read all 40 current checklist checks, worked examples and carried-forward lessons at batch start. Reopen the complete checklist after export, revisit the page's source assignments and relevant manual examples, and finish all 40 entries per page. One evolving record is sufficient. Every PASS must identify a specific observation from the current exported page. Cite the current PDF hash/revision at page level and the inspected region or content in each entry. Do not prefill PASS or copy another page's observations.

Allowed statuses:

- PASS: observed requirement met, with concrete evidence.
- NEEDS FIX: observed defect; specify correction and affected dependencies.
- NOT CHECKED: not performed or unavailable; explain precisely. No implied success.
- NOT APPLICABLE: why this page does not contain the condition addressed.

The current checklist is authoritative; do not replace it with 40 invented generic checks. The utility's record format is:

```json
{"checklist_sha256":"actual digest","pages":[{
  "page":92,"pdf":"relative/current-export.pdf","pdf_sha256":"actual digest",
  "checks":[{"id":"A01","requirement":"exact current check text","status":"NOT CHECKED","observation":"","limitation":""}],
  "corrections":[],"unresolved_limitations":[]
}]}
```

Include all 40 actual IDs. For PASS and NOT APPLICABLE, `observation` is mandatory; for NEEDS FIX and NOT CHECKED, fill `limitation`. Actual review must establish truth; schema validation cannot. The validator checks the current PDF bytes and checklist hash, but does not certify the honesty or adequacy of observations.

Review exact text, emphasis, reading order, every calculation, units, answers/blanks, native diagram evidence, author instructions, identity and physical scene continuity. Use automated reports for completeness, dimensions, ordering and resolution; retain visual review. Check the page at normal tablet/laptop size and close detail. A block count, generated contact sheet or render command does not prove anyone inspected the page.

Resolve fixable defects before the next page's artwork. If a required facility is unavailable, finish independent authorised work and mark the page as a qualified/unfinished proof as appropriate. State the missing check at delivery. Do not claim full preflight from an outline export. Keep user approval pending.

## Resumable state and invalidation

After every accepted image and reviewed page, persist a checkpoint alongside the project:

```json
{
  "chapter":"01","requested_pages":[92,93,94,95,96],
  "source_manifest":"qa/source-hashes.json",
  "manual_review_record":"qa/manual-review-record.json",
  "page":92,"state":"export-reviewed",
  "source_revision":"r01","source_sha256":"actual digest",
  "dependencies":{"assets":[],"fonts":[],"styles":[],"assembly":[]},
  "assets":[{"panel":"source panel ID","path":"artwork/file.png","sha256":"actual digest","status":"internally-reviewed","observations":[]}],
  "export_record":"qa/page-export.json","review_record":"qa/page-review.json",
  "continuity":{"pose":"observed","props":"observed ownership","location":"observed","repair_state":"source state"},
  "next_action":"specific unfinished step","author_approval":"pending"
}
```

Use real values; the example is not a ready-made checkpoint. Store durable identifiers or relative paths in portable packages, not just expiring download URLs or scratch paths. Suggested states: sources-verified, planned, artwork-reviewed, assembled, export-pending, export-reviewed, qualified-proof, delivered. Record exact unfinished work on interruption; resume from the last valid checkpoint.

Record export source path/hash/revision, upload asset identifier, job identifier if returned, actual parameters, success/error, download byte count/hash, page ID and PDF path. Keep tool receipts as execution evidence. Redact credentials; signed URLs are transient working references, not durable proof. Timestamp relevant operations.

Hash assets, fonts, styles and assembly dependencies. A shared change invalidates every affected page's export and affected review observations. Preserve unaffected work only with evidence of consistency. For page-specific changes, reuse other pages' exports. After a correction, reinspect adjacent items, transparency, colour and crop as well as the defect itself. Never carry old PASS observations forward when their subject changed.

## Final packaging

Combine the individual InDesign exports in manuscript order after every page reaches its review checkpoint. Check the combined PDF against the individual PDFs without resampling, and visually inspect all page turns. Verify matching editable sources, linked assets and actual source/export revision correspondence. Bundle the existing complete manual-review record and supporting evidence, exact source hashes, asset/register updates, export history and all 40 checks per page.

Keep project records consolidated. Do not add duplicate audits that restate the same evidence. Report actual observed timing when discussing speed; do not promise a percentage reduction without measurements. Never remove important source, image, export or visual review steps merely to finish faster.
