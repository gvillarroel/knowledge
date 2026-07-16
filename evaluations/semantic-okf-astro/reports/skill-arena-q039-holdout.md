# Frozen q039 Ensemble Holdout

Accepted run `2026-07-16T11-59-44-962Z-compare` (`eval-jIy-2026-07-16T11:59:52`) is the only completed live evaluation. The config, prompt, bundle, runner, and treatment skill were frozen before execution and the skill was not changed after inspecting the result.

| Profile | Contract | Evidence valid | Required docs | Exact spans | Atomic claims | Negatives | Latency |
|---|---:|---:|---:|---:|---:|---:|---:|
| `knowledge-only-control` | yes | 3/3 (pass) | 100% | 100% | 100% | 100% | 75842 ms |
| `ensemble-consult-treatment` | yes | 3/3 (pass) | 67% | 75% | 80% | 100% | 162166 ms |

Control 100%, treatment 100%, delta 0 percentage points. The treatment passes the frozen response-contract and evidence-validity gates, but the control also passes. This is contract-level no-regression evidence, not evidence of superiority or exact ground-truth sufficiency parity.

Both answers distinguish processed module deduplication from unprocessed inline scripts, constrain `data-astro-rerun` to intentional repeatable work, use Astro navigation lifecycle events, and guard or clean up persistent global listeners.
The strict evaluator-owned evidence audit is narrower than that manual facet audit. The treatment covers 2/3 required pages, 3/4 exact spans, 4/5 atomic claim groups, and both important negatives because it cites the authoritative Astro transitions module instead of the required directives-reference span. This is valid alternative evidence, but it does not receive exact-span credit.

## Integrity bindings

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| holdout_config | 6410 | `6fe54755b1165c5e147255f431e088e19639bf7b61ded7df19827be80c20054e` |
| holdout_manifest | 2680 | `f4052b587a8767dfa3a6549a693d8b48d3cb82a7541c42ac1562e1652f3f4a59` |
| prompt_coverage | 444 | `5fca2ca7f682aaac10a5b62a07d94e16057d7dd029330b6345344b31f3f3f68c` |
| promptfoo_results | 51277 | `e19850e9cdf89b6b578a1a2de4032e0c49dcde4e6c139465596bfc7f8fba7856` |
| promptfoo_config | 10632 | `4a8af58d33dee1e8d4ca5f83d9e5b6adc87560db22aed66930a3bb44953b089d` |
| skill_arena_summary | 36233 | `da5e80d8df65973d86c57be4686860951c905f62ae9b4f2ce8457adf7683cc70` |
| authoritative_records | 3455749 | `ef87105fe99c64683f21848810e82166ff54633095a28ab1cfa681984262cf0b` |
| source_crosswalk | 438819 | `c09e952254e5f2a4673ec0864bb09be333d8e914a1d0c46284e33953296cb783` |
| hard_answer_ground_truth | 58514 | `c265b1f232a7a8b44ff652a45782a4998ad8fbe72ac9004a5283a06b1539557d` |

## Exact parsed answers

### knowledge-only-control

```json
{
  "question_id": "q039",
  "answer": {
    "summary": "With ClientRouter, treat scripts as either once-only modules or navigation-time inline code. Keep initialization idempotent and choose lifecycle hooks according to whether it targets persistent or replaced DOM.",
    "claims": [
      {
        "statement": "Astro processes attribute-free scripts (apart from src) as bundled TypeScript modules, automatically makes them type=\"module\", bundles imports, and deduplicates component scripts per page. Under ClientRouter, bundled module scripts execute only once; later transitions ignore them even when present again.",
        "evidence_indices": [
          0
        ]
      },
      {
        "statement": "Inline scripts are a separate contract: is:inline leaves code unprocessed and exactly where authored, and inline elements are not deduplicated, so component instances can duplicate execution. Inline code can re-execute when revisiting a page; data-astro-rerun forces an inline script to execute after every transition. Any script attribute implicitly makes the script inline, so data-astro-rerun is unavailable to processed modules.",
        "evidence_indices": [
          0,
          1
        ]
      },
      {
        "statement": "For navigation-time initialization, use Astro lifecycle events rather than DOMContentLoaded. Events occur in order: astro:before-preparation, astro:after-preparation, astro:before-swap, astro:after-swap, then astro:page-load. After the swap, Astro executes new scripts, and astro:page-load fires at navigation completion; it fires on the initial prerendered page and subsequent forward or backward navigations.",
        "evidence_indices": [
          0
        ]
      },
      {
        "statement": "Because window is preserved across transitions, persistent global state and global listener installation must be guarded by a window sentinel (or equivalent idempotence check) so revisited/rerun inline code cannot register the same persistent listener repeatedly. Page-local handlers that target replaced DOM should instead be attached from astro:page-load and made safe for repeated setup.",
        "evidence_indices": [
          0
        ]
      }
    ]
  },
  "evidence": [
    {
      "source_id": "astro-doc-39e56439264bac6b",
      "record_id": "sources/mdx/guides/client-side-scripts",
      "concept_path": "concepts/astro-doc-39e56439264bac6b/sources-mdx-guides-client-side-scripts-fd26b88d3f.md",
      "source_path": "sources/mdx/guides/client-side-scripts.mdx",
      "record_sha256": "6b5168e85cacfe35442d51f14441908cd2b568b760e0eff46370dfdd51e27d04",
      "locator": {
        "kind": "record"
      },
      "text_sha256": "6005f2ad5bfdfb05a4f239899fdd5f8c333454f050781b7b06d7b7a378a1d93c"
    },
    {
      "source_id": "astro-doc-4effbbdbfc72e2bc",
      "record_id": "sources/mdx/reference/directives-reference",
      "concept_path": "concepts/astro-doc-4effbbdbfc72e2bc/sources-mdx-reference-directives-reference-ee8120f3db.md",
      "source_path": "sources/mdx/reference/directives-reference.mdx",
      "record_sha256": "60f7c17ee18edc6294307977abc7811d5efc47fea49bf638d924712d56daea4f",
      "locator": {
        "kind": "record"
      },
      "text_sha256": "4fa58142469ab25e244f408e34f0733fce259ef9dba035e01261828c5be50674"
    },
    {
      "source_id": "astro-doc-2a9b61ab94420eaa",
      "record_id": "sources/mdx/guides/view-transitions",
      "concept_path": "concepts/astro-doc-2a9b61ab94420eaa/sources-mdx-guides-view-transitions-3f0328ca64.md",
      "source_path": "sources/mdx/guides/view-transitions.mdx",
      "record_sha256": "eb24a05cc6004b8e177277a0efc03535679107df65b0ce141f3c98969b89cf5a",
      "locator": {
        "kind": "record"
      },
      "text_sha256": "9182c5295dda1a5ab1a867367187f4d563b06257d30b2497ff6636d46390ed83"
    }
  ]
}
```

### ensemble-consult-treatment

```json
{
  "question_id": "q039",
  "answer": {
    "summary": "With ClientRouter, treat Astro scripts as two distinct classes. A normal component script is processed as a module: Astro bundles imports, emits type=module behavior, deduplicates the component script when the component is used repeatedly, and may inline small output. That is a build-time inclusion guarantee, not a promise that page-specific initialization will run on every client-side navigation. An explicitly inline script is different: is:inline prevents bundling and processing. Moreover, adding any script attribute implicitly makes it inline, so data-astro-rerun belongs to that unprocessed class. Use data-astro-rerun only when the inline body must execute after every transition; otherwise a script already present in the current document is not executed again. For navigation-aware initialization, replace DOMContentLoaded with Astro’s lifecycle mechanism, specifically astro:page-load, so the setup runs on initial load and after client-side navigation. Finally, separate persistent global infrastructure from page-local setup: install a global listener behind a stable once-only guard (or remove it before re-adding), and keep DOM binding and teardown in the page-load handler. This contract prevents duplicate global registrations while still allowing each newly swapped page to initialize. It also makes intentional reruns explicit rather than relying on whether Astro retained, replaced, or recognized a script.",
    "claims": [
      {
        "statement": "Processed component scripts are bundled as modules, deduplicated when their component is used multiple times on a page, and may be automatically inlined when small.",
        "evidence_indices": [
          0
        ]
      },
      {
        "statement": "is:inline and script attributes select unprocessed inline behavior; data-astro-rerun forces such an inline script to execute after every transition, while scripts already present and not flagged are not executed again.",
        "evidence_indices": [
          1,
          2
        ]
      },
      {
        "statement": "Navigation-aware initialization should use Astro lifecycle events, replacing DOMContentLoaded with astro:page-load for execution on every page load during client-side navigation.",
        "evidence_indices": [
          1
        ]
      },
      {
        "statement": "Persistent global listener installation should be guarded as one-time infrastructure, while page-local event binding belongs in the navigation lifecycle handler.",
        "evidence_indices": [
          1,
          0
        ]
      }
    ]
  },
  "evidence": [
    {
      "source_id": "astro-doc-39e56439264bac6b",
      "record_id": "sources/mdx/guides/client-side-scripts",
      "concept_path": "concepts/astro-doc-39e56439264bac6b/sources-mdx-guides-client-side-scripts-fd26b88d3f.md",
      "source_path": "sources/mdx/guides/client-side-scripts.mdx",
      "record_sha256": "6b5168e85cacfe35442d51f14441908cd2b568b760e0eff46370dfdd51e27d04",
      "locator": {
        "end": 10087,
        "fragment": null,
        "kind": "character-range",
        "start": 0,
        "target": "record-body"
      },
      "text_sha256": "6005f2ad5bfdfb05a4f239899fdd5f8c333454f050781b7b06d7b7a378a1d93c"
    },
    {
      "source_id": "astro-doc-2a9b61ab94420eaa",
      "record_id": "sources/mdx/guides/view-transitions",
      "concept_path": "concepts/astro-doc-2a9b61ab94420eaa/sources-mdx-guides-view-transitions-3f0328ca64.md",
      "source_path": "sources/mdx/guides/view-transitions.mdx",
      "record_sha256": "eb24a05cc6004b8e177277a0efc03535679107df65b0ce141f3c98969b89cf5a",
      "locator": {
        "end": 38104,
        "fragment": null,
        "kind": "character-range",
        "start": 0,
        "target": "record-body"
      },
      "text_sha256": "9182c5295dda1a5ab1a867367187f4d563b06257d30b2497ff6636d46390ed83"
    },
    {
      "source_id": "astro-doc-c2224d9dcde099a5",
      "record_id": "sources/mdx/reference/modules/astro-transitions",
      "concept_path": "concepts/astro-doc-c2224d9dcde099a5/sources-mdx-reference-modules-astro-transitions-5aab131a08.md",
      "source_path": "sources/mdx/reference/modules/astro-transitions.mdx",
      "record_sha256": "96dc4aa58614cb2c48f95810dafc7e92b6c784c29fbe84cd804fb5fcb8ad3ed4",
      "locator": {
        "end": 17913,
        "fragment": null,
        "kind": "character-range",
        "start": 0,
        "target": "record-body"
      },
      "text_sha256": "c3989633051cb76e1da81a26dc35fbc4c55996f878d802a108da9a7117ad3116"
    }
  ]
}
```

## Append-only execution traces

| Run | Accepted | Live started | Live completed | Classification |
|---|---:|---:|---:|---|
| `2026-07-16T11-53-25-376Z-compare` | no | no | no | incomplete preflight; no model evaluation |
| `2026-07-16T11-53-54-729Z-compare` | no | no | no | preflight dry-run; no model evaluation |
| `2026-07-16T11-55-49-877Z-compare` | no | no | no | preflight dry-run; no model evaluation |
| `2026-07-16T11-59-44-962Z-compare` | yes | yes | yes | accepted completed live holdout |

Promptfoo contract scoring and authoritative evidence validity are separate gates. Every evidence row above was reconstructed from the frozen ledger and crosswalk. No MCP runtime participated.
