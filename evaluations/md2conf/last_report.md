# md2conf-isolated-offline-publishing-compare

Compare safe offline md2conf planning and diagnosis with and without the standalone md2conf skill.

| Prompt | Agent/Config | no-skill | skill |
| --- | --- | ---: | ---: |
| Diagnose package ambiguity, unreleased flags, and invalid source input. | Codex GPT-5.6 Sol | 0% (0/1)<br>tokens avg 95813, sd 0.0<br>time avg 50668 ms, sd 0.0 ms | 100% (1/1)<br>tokens avg 65918, sd 0.0<br>time avg 55566 ms, sd 0.0 ms |
| Plan a directory publication with hierarchy, links, metadata, and assets. | Codex GPT-5.6 Sol | 0% (0/1)<br>tokens avg 12843, sd 0.0<br>time avg 27773 ms, sd 0.0 ms | 100% (1/1)<br>tokens avg 15796, sd 0.0<br>time avg 35745 ms, sd 0.0 ms |
| Plan a single-page publication from an explicitly mapped Markdown source. | Codex GPT-5.6 Sol | 0% (0/1)<br>tokens avg 83746, sd 0.0<br>time avg 75892 ms, sd 0.0 ms | 0% (0/1)<br>tokens avg 71485, sd 0.0<br>time avg 80286 ms, sd 0.0 ms |
| Stop a Markdown publish when native Confluence content must remain authoritative. | Codex GPT-5.6 Sol | 0% (0/1)<br>tokens avg 24513, sd 0.0<br>time avg 15319 ms, sd 0.0 ms | 0% (0/1)<br>tokens avg 48161, sd 0.0<br>time avg 46052 ms, sd 0.0 ms |