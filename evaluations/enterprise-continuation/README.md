# EnterpriseRAG prospective continuation controls

These entrypoints implement E8, the prospectively registered continuation after
the original E7 host interruption. They preserve E7's immutable controls and
native evidence. Read the [operating guide](../../docs/enterprise-continuation.md)
and [ADR 0130](../../.specs/adr/0130-continue-interrupted-enterprise-search-prospectively.md)
before using them. Existing output paths are not restart commands.

`prepare.py` creates a historical-input manifest and an unchanged baseline.
`initialize.py jobs` versions only the paired all-500 execution profile;
`initialize.py register` uses the independent curator's exclusive guard and
registers the original task roots with new downstream stages. `preflight.py`
uses the native owner for planning and environment checks without scoring.
`seal.py contract` binds code, inherited controls, jobs and reviewed prerequisites;
`seal.py seal --review <private-review-directory>` requires the new independent
review before activation.

`run.py` asks the native Pareto owner to revalidate all 66 complete original jobs,
then measures the four previously unstarted baselines before further mutation.
It reconstructs inherited sweep positions and permanently reserves the two
incomplete original profiles. A failure stops its family while independent
families continue. `native.py` retains the original owner's realization, staging
and analysis interface. Neither component defines a new scorer.

`finalize.py` retains the exact all-eight joint replay, digest freeze, paired
all-500 comparison and one-way private acceptance. `pipeline.py` supervises those
phases once, with zero automatic retries. `launch.py` supplies WSL and local
cache paths. All raw artifacts remain under ignored `tmp/e8/`.

`origins.json` records source commitments for copied E7 helpers. E8's execution
seal also binds the original profile catalog and scheduler imported read-only
from `enterprise-stratified-evolution/`. The source E7 files are never edited.
