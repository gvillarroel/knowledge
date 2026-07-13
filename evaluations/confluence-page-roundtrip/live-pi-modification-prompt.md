Modify the real Confluence page workspace in the current directory using the loaded `roundtrip-confluence-pages` skill.

This is a live acceptance specimen. Edit only files inside this workspace. Do not call the network and do not upload anything.

Requirements:

1. Change the page title in `page.meta.json` to `Confluence Round-Trip Live Acceptance — Luna Revision 2026-07-12`.
2. Preserve every pre-existing table, macro, internal link, task, unknown attribute, namespace-qualified node, and read-only representation file.
3. Insert a new `Release readiness` section in `page.storage.xml` before the final stray `/table` paragraph.
4. The section must contain:
   - an `info` panel whose visible text explains that the page was edited locally and round-tripped through Confluence storage format;
   - a green `READY` status macro;
   - a three-column table with headers `Owner`, `Capability`, and `Verification`, plus two non-empty data rows;
   - a block-appearance Smart Link to `https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-attachment/`;
   - a dynamic internal `ri:page` link to `Confluence Round-Trip Link Target 2026-07-12`;
   - an `ac:image` node referencing the attachment `live-system-context.png`, with an alt-text parameter describing the Confluence round-trip architecture.
5. Keep the existing `Verificado` content state unchanged.
6. Add the labels `roundtrip-validated` and `luna-edited`, preserving any existing labels.
7. Do not edit `page.adf.json`, `page.view.html`, `page.restrictions.json`, or `manifest.json`; they are evidence/read-only files and the upload workflow will refresh them after remote verification.
8. Do not edit `ground-truth.json`; the deterministic `capture-gt` command will regenerate it after your edits.
9. The result must remain valid Confluence storage XML when wrapped in the standard Confluence namespace container.

Before finishing, review your diff and ensure the new image reference exactly matches the existing local file `attachments/live-system-context.png`.
