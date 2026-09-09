"""Check prospective native profiles and historical bindings without scoring."""
from __future__ import annotations

import json
import sys

from prepare import WORK, HISTORY, OWNER, read, write, load, sha, tree, NAME


def preflight():
    """Run native planning/doctor and verify the exact effective runtime delta."""
    owner = load('e8_preflight_owner', OWNER)
    if tree(WORK / 'baseline' / NAME) != tree(HISTORY / 'baseline' / NAME):
        raise ValueError('Continuation changed the historical baseline')
    if sha(WORK / 'enterprise_agent.py') != sha(HISTORY / 'enterprise_agent.py'):
        raise ValueError('Development agent bytes changed')
    rows = []
    for path in sorted((WORK / 'jobs').glob('*.json')):
        original = owner.load_job_template(HISTORY / 'jobs' / path.name)
        current = owner.load_job_template(path)
        original_signature, signature = owner.job_signature(original), owner.job_signature(current)
        if path.name != 'joint-recalculation.json':
            if original_signature != signature:
                raise ValueError('Historical native profile drift: ' + path.name)
        else:
            adjusted = current.model_copy(deep=True)
            adjusted.agents[0].name = original.agents[0].name
            adjusted.agents[0].import_path = original.agents[0].import_path
            adjusted.agents[0].override_timeout_sec = original.agents[0].override_timeout_sec
            if owner.job_signature(adjusted) != original_signature or current.agents[0].override_timeout_sec != 10800:
                raise ValueError('Unexpected retrospective profile delta')
        rows.append({'job': path.name, 'historical_signature': original_signature,
                     'signature': signature, 'same_profile': original_signature == signature})
    config = {'schemaVersion': 1, 'search': {'id': 'enterprise-e8-preflight',
        'baselineSkill': str(WORK / 'baseline' / NAME), 'baselineCandidate': 'baseline',
        'outputDir': str(WORK / 'preflight/unused-native-output'), 'generation': 0},
        'harbor': {'developmentJob': str(WORK / 'jobs/joint-development.json'),
                   'holdoutJob': str(WORK / 'jobs/joint-validation.json'), 'rewardKey': 'reward',
                   'passThreshold': .8, 'requiredRewards': {'evidence_integrity': 1}, 'requiredEnv': []},
        'candidates': [{'id': 'baseline', 'skill': str(WORK / 'baseline' / NAME), 'parents': []}],
        'promotion': {'minimumMeanGain': 0, 'allowCaseRegressions': True, 'requireNoErrors': True}}
    write(WORK / 'preflight/native-config.json', config)
    import subprocess
    probes = []
    for mode in ('dry-run', 'doctor'):
        result = subprocess.run([sys.executable, '-B', str(OWNER), str(WORK / 'preflight/native-config.json'), '--' + mode],
                                capture_output=True, text=True, check=False)
        write(WORK / 'preflight' / (mode + '.json'), {'exit_code': result.returncode,
              'stdout': result.stdout, 'stderr': result.stderr})
        if result.returncode:
            raise RuntimeError('Native preflight failed: ' + mode + ': ' + result.stderr[-1200:])
        probes.append({'mode': mode, 'exit_code': result.returncode})
    if (WORK / 'preflight/unused-native-output').exists():
        raise ValueError('Preflight unexpectedly created native output')
    write(WORK / 'preflight/receipt.json', {'status': 'pass', 'profiles': rows, 'probes': probes,
        'native_trials_dispatched': 0, 'historical_profiles_unchanged': 18,
        'prospective_retrospective_profiles': 1, 'baseline_bytes_unchanged': True,
        'private_validation_released': False})
    print(json.dumps({'status': 'pass', 'native_profiles': 19, 'same_historical_profiles': 18,
                      'native_trials_dispatched': 0}))


if __name__ == '__main__':
    preflight()
