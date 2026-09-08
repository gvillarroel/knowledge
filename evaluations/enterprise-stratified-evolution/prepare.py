"""Prepare E7 controls and native execution scaffolds in a new private root."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from dataset import digest as sha, write_new
from profiles import FAMILIES, CONSTRUCTION, baseline_profile, inventory

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
WORK = REPO/'tmp/e7'
OLD = REPO/'tmp/e5'  # Read-only pinned model cache; never a dispatch destination.
NAME = 'build-semantic-okf-knowledge-skill'
ORGANIZER = REPO.parent/'skill-arena/skills/harbor-organize-evaluations/scripts/manage_harbor_evaluations.py'
OWNER = (Path('C:/Users/villa/.codex/skills/harbor-reflective-pareto-search/scripts/harbor_reflective_pareto.py')
         if os.name == 'nt' else Path('/mnt/c/Users/villa/.codex/skills/harbor-reflective-pareto-search/scripts/harbor_reflective_pareto.py'))
HPY = '/home/villa/.local/share/uv/tools/harbor/bin/python'
IMAGE_TAG = 'semantic-okf-harbor-runtime:2.0'
IMAGE = 'sha256:bcd2b2b57b968ff8b4976bedf8c5ddf7b7e2ff41c341f7a13a05ae4df2ffc9d8'
MODES = {'legacy':['lexical'],'embeddings':['lexical','vector','hybrid'],
         'classical':['bm25','topic','association','fusion'],'adaptive':['adaptive'],
         'entity-graph':['lexical','entity','traversal','fusion'],
         'ensemble':['fast','quality','robust'],'graphify':['search'],'turso':['lexical-sql']}
PRIMARY = {'legacy':'lexical','embeddings':'hybrid','classical':'fusion','adaptive':'adaptive',
           'entity-graph':'fusion','ensemble':'quality','graphify':'search','turso':'lexical-sql'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    write_new(path,value)


def tree(root):
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink() or getattr(path,'is_junction',lambda:False)():
            raise ValueError('Linked artifact')
        if path.is_file():
            result[path.relative_to(root).as_posix()] = sha(path)
    return result


def posix(path):
    path = path.resolve()
    return '/mnt/'+path.drive[0].lower()+'/'+path.as_posix().split(':/',1)[1] if os.name == 'nt' else str(path)


def command(argv,log):
    log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('xb') as stream:
        result = subprocess.run(argv,stdout=stream,stderr=subprocess.STDOUT,check=False)
    if result.returncode:
        raise RuntimeError('Command failed; inspect '+str(log))


def linux(argv):
    result = subprocess.run((['wsl','-d','Ubuntu','--exec'] if os.name == 'nt' else [])+argv,
                            capture_output=True,check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors='replace')[-2000:])
    return result.stdout.decode().strip()


def organize(action,*args):
    logs = WORK/'logs/organizer'
    number = len(list(logs.glob('*.log'))) if logs.exists() else 0
    command([sys.executable,'-B',str(ORGANIZER),action,str(WORK/'study'),*map(str,args)],logs/f'{number:03d}-{action}.log')


def setup():
    """Create shared reviewed bytes; no queries are scored and no gate is opened."""
    baseline = WORK/'baseline'/NAME
    shutil.copytree(REPO/'skills'/NAME,baseline)
    shutil.copyfile(HERE/'profiles.py',baseline/'scripts/apply_retrieval_profile.py')
    write(baseline/'assets/retrieval-profile.json',baseline_profile())
    reference = ('# Explicit experimental retrieval profile\n\n'
                 'Read `assets/retrieval-profile.json` before construction or consultation.\n'
                 'For plan-based families run `scripts/apply_retrieval_profile.py --family FAMILY\n'
                 '--input PLAN.json --output PROFILED.json`, then use the exact matched builder and validator.\n\n'
                 'Legacy and Turso search settings apply the helper\'s record BM25 projection; Graphify settings\n'
                 'apply native traversal depth and optional lexical reciprocal-rank fusion. Empty search\n'
                 'settings preserve the original route. Treat these as consultation changes.\n\n'
                 'Never combine a builder and consultant mutation within one family treatment. Preserve the\n'
                 'authoritative body, exact record identities, immutable evidence and physical citations.\n'
                 'Pinned learned models must be available offline; no silent fallback is allowed.\n'
                 'The profile is experimental until its declared independent acceptance gate passes.\n')
    (baseline/'references/retrieval-profile.md').write_text(reference,encoding='utf-8',newline='\n')
    skill = baseline/'SKILL.md'
    skill.write_text(skill.read_text(encoding='utf-8')+'\nRead [the explicit profile](references/retrieval-profile.md) before using this experimental package.\n',encoding='utf-8',newline='\n')
    runtime = WORK/'runtime'
    runtime.mkdir()
    # Reuse the previously reviewed native construction/search interface;
    # the only execution-shape change is the supported packed concept layout.
    prior_path = REPO/'evaluations/enterprise-evolution/prepare.py'
    spec = importlib.util.spec_from_file_location('e7_prior_bridge_source',prior_path)
    prior = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prior)
    bridge = prior.make_bridge().replace('args.extend([str(target), "--output-format", "json"])',
                                         'args.extend([str(target), "--concept-layout", "source-packed-v1", "--output-format", "json"])')
    (runtime/'bridge.py').write_text(bridge,encoding='utf-8',newline='\n')
    helpers = REPO/'evaluations/private-book-strategy-comparison/scripts'
    for name in ('prepare_strategy_bundles.py','evaluate_all_routes.py'):
        shutil.copyfile(helpers/name,runtime/name)
    shutil.copyfile(REPO/'evaluations/semantic-okf-embeddings/scripts/compare_retrieval.py',runtime/'legacy_comparator.py')
    agent = (REPO/'evaluations/skill-evolution/native_agent.py').read_text(encoding='utf-8')
    agent = agent.replace('return "skill-retrieval"','return "enterprise-stratified-retrieval"').replace('return "1.0.0"','return "3.0.0"')
    (WORK/'enterprise_agent.py').write_text(agent,encoding='utf-8',newline='\n')
    source = (REPO/'evaluations/skill-evolution/verifier.py').read_text(encoding='utf-8')
    source = source.replace('vector.append(evaluator.metrics(hits, question["relevant"]))',
                            'vector.append(evaluator.metrics(hits, question["relevant"]) if question["relevant"] else None)')
    source = source.replace('aggregates[mode] = {key: statistics.fmean(row[key] for row in vector) for key in vector[0]}',
        '''eligible = [(row, question.get("weight", 1.0)) for row, question in zip(vector, questions) if row is not None]
        if not eligible or any(type(weight) not in (int, float) or not math.isfinite(weight) or weight <= 0 for _, weight in eligible):
            raise ValueError("Invalid retrieval eligibility or sampling weights")
        aggregates[mode] = {key: sum(row[key]*weight for row, weight in eligible)/sum(weight for _, weight in eligible) for key in eligible[0][0]}''')
    (runtime/'verifier.py').write_text(source,encoding='utf-8',newline='\n')
    selection = read(WORK/'development-selection-v2/summary.redacted.json')
    corpus = read(WORK/'corpus/summary.redacted.json')
    protocol = {'schema_version':'enterprise-stratified-evolution/1.0','id':'enterprise-e7',
                'controller':'harbor-reflective-pareto-search','families':list(FAMILIES),
                'development':selection,'corpus':corpus,
                'strategies':{family:inventory(family) for family in FAMILIES},
                'treatments':{family:'construction' if family in CONSTRUCTION else 'consultation' for family in FAMILIES},
                'failure_rule':'Three consecutive unique evaluable misses per mechanism; strict weighted nDCG@10 gain > 1e-12 resets the streak. Duplicate configurations are skipped. Repeat the catalog after any improving round, retaining all previously evaluated profiles. Stop on a complete round without improvement, or explicitly label five-round budget exhaustion. External failures stop the affected execution without fitness.',
                'budget':{'maximum_new_candidates':5*sum(len(s['variants']) for f in FAMILIES for s in inventory(f)),
                          'maximum_new_candidates_per_round':sum(len(s['variants']) for f in FAMILIES for s in inventory(f)),
                          'maximum_outer_rounds':5,
                          'baseline_trials':8,'joint_development_trials':16,'validation_trials':32,
                          'final_retrieval_trials':16,'native_attempts':1,'native_retries':0,'family_workers':2,'llm_calls':0},
                'selection':'Choose each qualified family incumbent by weighted development nDCG@10, strict gain, preserving the earlier incumbent on ties. Combine all eight configurations, re-evaluate the complete merged bundle against the unchanged baseline on all development tasks, and freeze that exact bundle jointly before one validation release.',
                'stage_order':['family evolution and joint development replay','freeze exact joint candidate',
                               'retrospective all-500 baseline/candidate recalculation without reselection',
                               'single reserved transfer gate','aggregate publication'],
                'development_task_registry':'Sixteen task roots in one Enterprise independence group: eight 120-question evolution tasks and eight all-500 recalculation tasks. Evolution jobs use only the former; final jobs use only the latter after joint freezing. All final outcomes are excluded from same-study reselection.',
                'validation':'One terminal retrieval-only transfer pilot: 12 questions and 985 documents in each of two reserved source groups, all eight families. Mean paired gain across both source groups must be nonnegative separately for every family, with exact evidence integrity and no errors in all 32 trials. Accept or reject the entire merged bundle once. No feedback-driven same-study mutation or per-family replacement. No additional holdout.',
                'final_recalculation':'All 500 exposed Enterprise questions, the same fixed 6000-document full-text corpus, all eight unchanged baselines and frozen family selections. Thirty no-reference questions excluded only from retrieval denominators. Internal retrospective retrieval comparison; no official Overall or full-corpus ranking claim. Existing full-corpus Classical/Luna results remain distinct.',
                'independence':'Enterprise is one development source family; four measurement blocks do not increase independence. Validation has two source families and supports only a descriptive transfer pilot.',
                'loading':'Native deterministic skill staging and exact helper execution; no language-model skill-selection claim.',
                'baseline_files':tree(baseline),'runtime_files':tree(runtime),'agent_sha256':sha(WORK/'enterprise_agent.py')}
    write(WORK/'protocol.json',protocol)
    print(json.dumps({'status':'scaffold-prepared-not-sealed','families':8,'maximum_candidates':protocol['budget']['maximum_new_candidates']}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['setup'])
    parser.parse_args()
    setup()


if __name__ == '__main__':
    main()
