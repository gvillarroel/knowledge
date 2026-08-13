---
name: consult-semantic-okf-tika-mallet-bounded
description: Produce one bounded, deterministic, extractive JSON answer from an immutable Semantic OKF snapshot indexed with Apache Tika 4.0.0-beta-1 and Java MALLET 2.1.0. Use for time- or context-limited evaluation questions that require source-diverse exact evidence and must not permit exploratory snapshot reads, follow-up searches, handwritten evidence identities, or iterative answer repair.
---

# Produce a bounded Tika/MALLET Semantic OKF answer

Use the bundled compiler as a sealed consultation interface. It validates the
snapshot, runs three to five independent searches, fuses their rankings, keeps one
passage per source, builds source-grounded extractive claims, validates first-use
evidence order, writes one new JSON file outside the snapshot, and prints that same
JSON.

## Standalone read-only boundary

Use only this skill package and the supplied immutable snapshot. Do not import
or execute sibling skills or repository helpers. The compiler may write only
the caller-declared new output outside the snapshot; it never builds, repairs,
refreshes, or mutates knowledge.

## Closed workflow

1. Read only this `SKILL.md`. Do not read the bundled scripts or any other skill
   file.
2. Do not list, search, grep, or read `/knowledge` directly. Do not run `find`,
   `rg`, `grep`, `ls`, `cat`, or a general file-reading tool against the snapshot.
3. Install the pinned dependency:

   ```bash
   python -m pip install -r scripts/requirements.txt
   ```

4. Run exactly one compiler invocation. Supply the question verbatim, three to
   five distinct broad retrieval queries, the task's declared minimum independent
   source count, and at most two additional sources:

   ```bash
   python -B scripts/bounded_answer.py /knowledge \
     --question-id QUESTION_ID \
     --question "VERBATIM QUESTION" \
     --query "BROAD QUERY ONE" \
     --query "BROAD QUERY TWO" \
     --query "BROAD QUERY THREE" \
     --mode fusion --top-k 6 \
     --minimum-sources MINIMUM \
     --max-sources MAXIMUM \
     --output /tmp/QUESTION_ID-final.json
   ```

5. Return the compiler's JSON stdout unchanged. Do not open the output file,
   inspect intermediate state, revise prose, validate again, or invoke another
   command. A compiler error is terminal; return the caller's declared null answer
   without additional snapshot access.

The compiler treats BM25, MALLET topics, PPMI associations, and reciprocal-rank
fusion only as discovery signals. Its evidence rows come from the validated
authoritative OKF ledger and retain exact source, record, path, locator, and hash
identities. It refuses linked snapshots, unsafe outputs, overwrites, malformed
indexes, insufficient source diversity, or evidence-order drift.
It accepts record-per-file and source-packed physical Markdown layouts without
changing any logical evidence identity or compiler output.
