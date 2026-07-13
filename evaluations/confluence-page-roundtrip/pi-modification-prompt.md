Modify the Confluence page workspace in the current directory using the loaded roundtrip-confluence-pages skill.

Requirements:

1. Change the page title to `Confluence Round-Trip Acceptance — Revised` in both editable metadata and the visible page heading.
2. Insert a `Release readiness` section immediately after the Overview section.
3. In that section, add a green `READY` status macro, a three-column table with headers `Owner`, `Area`, and `Decision`, and two data rows.
4. Add a block-appearance Smart Link to `https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-attachment/`.
5. Create `attachments/release-architecture.svg`, a valid standalone SVG diagram with an accessible title and description, and reference it from the new section with an `ac:image` attachment node.
6. Add the global label `roundtrip-validated` while preserving existing labels.
7. Change the page content state to name `Ready` and color `GREEN`.
8. Preserve every pre-existing macro, internal link, Smart Link, task, image reference, attachment file, and unknown attribute.
9. Update ground truth so `Release readiness` and `READY` are required visible text assertions. Preserve the existing visual baseline note.

Edit only files inside this workspace. Do not call the network and do not upload anything.
