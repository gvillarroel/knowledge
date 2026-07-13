# roundtrip-confluence-pages-isolated-planning-compare

Compare offline loss-aware Confluence planning with and without the standalone roundtrip-confluence-pages skill.

| Prompt | Agent/Config | no-skill | skill |
| --- | --- | ---: | ---: |
| Generalize the workflow to a small reviewed batch with throttling. | Codex GPT-5.6 Sol | 0% (0/1)<br>tokens avg 12561, sd 0.0<br>time avg 22863 ms, sd 0.0 ms | 100% (1/1)<br>tokens avg 236167, sd 0.0<br>time avg 108942 ms, sd 0.0 ms |
| Plan a safe edit of a page with dynamic and attachment-backed content. | Codex GPT-5.6 Sol | 0% (0/1)<br>tokens avg 12070, sd 0.0<br>time avg 30853 ms, sd 0.0 ms | 100% (1/1)<br>tokens avg 42623, sd 0.0<br>time avg 65068 ms, sd 0.0 ms |
| Plan an attachment replacement with metadata preservation. | Codex GPT-5.6 Sol | 0% (0/1)<br>tokens avg 12268, sd 0.0<br>time avg 10458 ms, sd 0.0 ms | 100% (1/1)<br>tokens avg 17601, sd 0.0<br>time avg 23217 ms, sd 0.0 ms |
| Recover safely when the remote page changes after download. | Codex GPT-5.6 Sol | 0% (0/1)<br>tokens avg 12319, sd 0.0<br>time avg 13064 ms, sd 0.0 ms | 0% (0/1)<br>tokens avg 17136, sd 0.0<br>time avg 18509 ms, sd 0.0 ms |