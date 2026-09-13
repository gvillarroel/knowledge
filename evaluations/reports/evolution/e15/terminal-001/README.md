# EnterpriseRAG: final measured table and campaign closure

Date: 2026-09-13. **The campaign is closed with an incomplete requested evaluation.**
E14 is terminal. E15's independent preparation review rejected activation because
the optimizer's actual tool identity could read private verifier inputs. All
four planned E15 stages are now stopped. No E15 native trial, benchmark model
call, candidate selection, all-500 comparison, or private release occurred.

[Applications and categories](groups.md) · [Cost, time and quality](cta.md) ·
[Full-precision aggregate and evidence bindings](aggregate.json) ·
[Independent safe review](independent-review.json)

## Final retained development comparison

The following are the last qualified **E14 development observations**, preserved
from their original reports. The workload contains **120 stratified questions,
112 questions with retrieval references, and 6,000 complete documents**, with
an eligible population weight of 470. They were not recalculated by E15.

| Family | nDCG@10 ×100 | Recall@10 ×100 | MRR@10 ×100 | Terminal status |
| --- | ---: | ---: | ---: | --- |
| Legacy | 72.38 | 81.99 | 71.51 | Qualified observation; finite catalog closed |
| Turso | 72.38 | 81.99 | 71.51 | Qualified observation; finite catalog closed |
| Adaptive | 66.21 | 74.02 | 67.37 | Qualified observation; finite catalog closed |
| Graphify | 63.72 | 81.79 | 60.45 | Qualified observation; finite catalog closed |
| Embeddings | 63.51 | 80.82 | 61.59 | Qualified observation; finite catalog closed |
| Classical | 62.10 | 64.17 | 66.38 | Qualified observation; finite catalog closed |
| Entity Graph | Unavailable | Unavailable | Unavailable | E14 timeout; E15 first measurement unexecuted |
| Ensemble | Unavailable | Unavailable | Unavailable | E14 memory failure; E15 first measurement unexecuted |

Legacy and Turso tie at full precision. Unavailable results are missing
measurements, not zeroes. The family primary routes remain the predeclared
routes; this report does not substitute a better secondary route after seeing
results. The scores measure retrieval, not generated-answer correctness.

The [original comparison](../../e14/graphify-generation-016-001/comparison.md)
owns the paired group evidence. The [final Graphify observation](../../e14/graphify-generation-024-001/README.md)
retains that comparison unchanged and records the later catalog stop. The
[existing heatmap](../../e14/application-heatmap-016/README.md) visualizes the same values.

## What completed and what did not

| Obligation | Final state |
| --- | --- |
| Qualified family development results | Six of eight available |
| Finite catalog closure | Six closed; two stopped before qualification |
| Two prospective E15 first measurements | 0 of 2; identities remain unconsumed |
| Paired all-eight joint replay | 0 of 16 trials |
| Whole-bundle freeze | 0 of 1 |
| Paired all-500 recalculation | 0 of 16 trials |
| Independent private acceptance | 0 of 32 trials; no release |
| Canonical skill promotion from E15 | None |
| Organizer lifecycle | Four stopped stages; 11 verified ledger events; no next action |

The proposal ledger preserves **140 / 585 claims**. Closed families retain 272
unused, nontransferable slots. Entity Graph and Ensemble had 173 unexecuted
slots when E15 was rejected. Their hypotheses were not exhausted. Two historical
fitness gaps in closed families also remain disclosed; finite catalog closure
does not establish that all possible knowledge-generation strategies were tried.

## Separate complete full-corpus results

The earlier Classical run covers **511,962 physical documents and all 500 public
questions**. It is a different retrieval treatment and corpus from the development
table above, and it is not the missing E15 comparison.

| Historical treatment | Metric | Result | Completion |
| --- | --- | ---: | --- |
| Classical / BM25 | Retrieval nDCG@10 ×100 | 59.03 | 500 queries; quality on 470 with original references |
| Classical / Luna / Luna judge | Internal answer Overall | 48.33 / 100 | 500 answers and 500 first-evaluable judgments |

The [full-corpus retrieval report](../../../enterprise-classical-full/README.md)
and [Luna answer audit](../../../enterprise-classical-full/luna.md) preserve their
exact methodology, recovery lineage and costs. The Luna answer score is internal;
it does not establish a public leaderboard position or a controlled comparison
against submissions scored by another judge. The historical GPT-5.4 answer arm
remains incomplete after provider quota errors.

## Why E15 was rejected

An independent curator verified an ordinary-tool read-open of a private verifier
input and inherited workspace permissions. Historical ledger nonrelease and
container probes do not establish that the optimizer was denied host access.
This is a preparation failure, not a measured private quality failure or a claim
that the private portfolio was scored or consumed. The other five prospective
review controls were left uncompleted after the terminal access failure.

The maintained organizer contract requires an isolated evaluator context or
service. [ADR 0164](../../../../../.specs/adr/0164-close-e15-after-independent-preparation-rejection.md)
records the exact rule and terminal handling. Each legal `planned -> stopped`
transition binds the independent receipt and closure decision by path and digest;
the original ledger prefix remains unchanged. The stopped `publish` stage is
the planned accepted-candidate publication, distinct from this closure report.

## Correction to the earlier preflight claim

The previous preflight did pass 18 unit tests and owner dry-run/doctor checks
for four configurations. It did not prove a complete executable campaign.
The prepared adapter covered the two first measurements; the remaining catalog,
joint replay, freeze, all-500 and acceptance driver was missing. The review also
found unresolved cross-process allocation, admission-to-dispatch, exact binding,
and qualification-stop responsibilities. [Public source findings](public-runtime-findings.md)
document each issue. Original preflight aggregate bytes and real diagnostic
results remain preserved; their implied execution-readiness conclusion is superseded.

## Useful retained findings

- Legacy and Turso share the highest observed overall retrieval score. Legacy
  has the shortest measured agent and build time among the six retained rows;
  timings are descriptive and host costs are unpriced.
- Different applications have different leaders: Embeddings for Confluence and
  Slack, Classical for Fireflies and Linear, Graphify for GitHub and Google
  Drive, and Legacy/Turso for Gmail, HubSpot and Jira. No application router
  or automatic skill chooser was evaluated by this comparison.
- Family composition must transfer only the intended family subtree and exact
  profile. Unrelated changes inherited from another candidate must be excluded.
  This composition check alone does not qualify an assembled skill bundle.
- Software parity, configuration checks and private-data eligibility are
  separate from completed retrieval measurements and final acceptance.

A future attempt needs a new study, enforced evaluator/optimizer separation,
actual denied-access evidence, and fresh private data when past nonexposure
cannot be established. It also needs a complete audited public controller.
There is no pending E15 activation or automatic restart, and no unvalidated
E15 candidate has been installed as a canonical skill.

## Repository verification and navigation

`python scripts/check_coverage.py --threshold 80` passed with **1,697 tests,
373 subtests and 90.5% total application coverage**. The organizer verifies all
11 ledger events, two dataset locks and four stopped stages. Dataset payloads,
private review details, candidate trees and native traces remain ignored.

[By skill](../../../skills/README.md) · [All datasets and report hub](../../../README.md) ·
[Family history](../../../../../docs/enterprise-family-report-index.md) ·
[E15 overview](../README.md) · [Historical preflight](../executable-preflight-001/README.md)
