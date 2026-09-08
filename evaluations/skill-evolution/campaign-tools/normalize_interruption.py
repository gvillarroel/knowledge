"""Normalize the interrupted generation without replay, scoring or archive creation."""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / 'evaluations/skill-evolution'))
from prepare_experiment import sha, tree, write_json, wsl_path
from run_search import HARBOR_PYTHON, assert_frozen

state = assert_frozen()
if state['validationRelease'] or state['holdoutRelease'] or state['stages']['evolve']['status'] != 'running':
    raise ValueError('Only unopened active development may be normalized')
generation = ROOT / 'pareto/development/generation-001'
if (generation / 'pareto-archive.json').exists():
    raise ValueError('Use the complete generation reporter for a native archive')
destination = ROOT / 'native-reports/interrupted-generation-001'
if destination.exists():
    raise ValueError('Preserve the first interrupted snapshot')
profiles = ('baseline', 'neural-expand', 'neural-titles', 'neural-bm25', 'expand-titles')
jobs = [generation / 'harbor-jobs' / ('knowledge-retrieval-e5-g001-development-' + name) for name in profiles]
before = {str(job): tree(job) for job in jobs}
expected = [32, 32, 32, 32, 31]
for index, job in enumerate(jobs):
    data = json.loads((job / 'result.json').read_text())
    if data['n_total_trials'] != 32 or data['stats']['n_completed_trials'] != expected[index]:
        raise ValueError('Interrupted source completion changed')
    if (data['finished_at'] is not None) != (index < 4):
        raise ValueError('Unexpected native terminal state')
destination.mkdir()
reporter = '/mnt/c/Users/villa/.codex/skills/harbor-run-results/scripts/report_harbor_jobs.py'
for label, sources, flags in (('complete-profiles', jobs[:4], ['--compare']),
                              ('incomplete-profile', jobs[4:], ['--allow-incomplete'])):
    argv = ['wsl', '-d', 'Ubuntu', '--exec', 'env', 'PYTHONDONTWRITEBYTECODE=1',
            'TMPDIR=' + wsl_path(ROOT / 'host-cache/tmp'), HARBOR_PYTHON, '-B', reporter,
            *map(wsl_path, sources), *flags, '--reward-key', 'reward', '--pass-threshold', '0.8',
            '--output-dir', wsl_path(destination / label), '--title', 'Interrupted e5 generation: ' + label]
    with (destination / (label + '.log')).open('xb') as stream:
        result = subprocess.run(argv, stdout=stream, stderr=subprocess.STDOUT, check=False)
    if result.returncode:
        raise ValueError('Native report failed; preserve its diagnostic log')
if any(tree(Path(path)) != commitment for path, commitment in before.items()):
    raise ValueError('Native sources changed during reporting')
write_json(destination / 'receipt.json', {'status': 'native-interruption-snapshot', 'source_trees': before,
    'report_sha256': {label: sha(destination / label / 'final-report.json') for label in ('complete-profiles', 'incomplete-profile')},
    'completed_trials': 159, 'expected_trials': 160, 'missing_trials': 1,
    'native_jobs_started': 0, 'native_archive_created': False, 'validation_used': False,
    'source_unchanged': True, 'launcher_sha256': sha(Path(__file__))})
print(json.dumps({'status': 'native-interruption-snapshot', 'completed_trials': 159, 'missing_trials': 1,
                  'receipt_sha256': sha(destination / 'receipt.json')}))
