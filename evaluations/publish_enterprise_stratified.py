"""Publish reviewed E7 aggregates from completed native evidence, without scoring."""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import statistics

REPO = Path(__file__).resolve().parents[1]
WORK = REPO/'tmp/e7'
PRIMARY = {'legacy':'lexical','embeddings':'hybrid','classical':'fusion','adaptive':'adaptive',
           'entity-graph':'fusion','ensemble':'quality','graphify':'search','turso':'lexical-sql'}
ROUTES = {'legacy':('lexical',),'embeddings':('lexical','vector','hybrid'),
          'classical':('bm25','topic','association','fusion'),'adaptive':('adaptive',),
          'entity-graph':('lexical','entity','traversal','fusion'),
          'ensemble':('fast','quality','robust'),'graphify':('search',),'turso':('lexical-sql',)}
METRICS = ('ndcg_at_10','recall_at_10','mrr_at_10','full_qrel_coverage_at_10')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def host(value):
    return Path('C:/'+value[7:]) if os.name=='nt' and value.startswith('/mnt/c/') else Path(value)


def finite(value, lower=0, upper=None):
    if type(value) not in (int,float) or not math.isfinite(value) or value<lower or (upper is not None and value>upper):
        raise ValueError('Invalid native aggregate')
    return value


def elapsed(row):
    if not row or not row.get('started_at') or not row.get('finished_at'):
        return None
    return finite((datetime.fromisoformat(row['finished_at'])-datetime.fromisoformat(row['started_at'])).total_seconds())


def aggregate_group(cases, indices):
    """Average already-scored native case metrics; never rerank or rescore hits."""
    eligible = [cases[index] for index in indices if cases[index] is not None]
    return {'questions':len(indices),'retrieval_eligible':len(eligible),
            **{key:statistics.fmean(finite(row[key],upper=1) for row in eligible) if eligible else None
               for key in METRICS}}


def require_complete_arm(job):
    """Require eight settled successful native trials before publishing an arm."""
    stats = job.get('stats',{})
    if (not job.get('finished_at') or job.get('n_total_trials')!=8
        or stats.get('n_completed_trials')!=8
        or any(stats.get(key)!=0 for key in ('n_running_trials','n_pending_trials',
                                            'n_errored_trials','n_cancelled_trials'))):
        raise ValueError('Final native arm is incomplete or failed')


def require_family_routes(family, diagnostics):
    """Prevent a substituted route from preserving a misleading total count."""
    expected = set(ROUTES[family])
    if set(diagnostics['routes'])!=expected or set(diagnostics['cases'])!=expected:
        raise ValueError('Final routes differ from the declared family contract')


def replay_history(result, strategies, baseline_profile, profile_module, scheduler_module, max_rounds):
    """Replay decisions using existing rewards; never execute or score a trial."""
    outcomes = result['outcomes']
    if not outcomes or outcomes[0]['candidate']!='baseline' or outcomes[0]['score']!=result['baseline_score']:
        raise ValueError('Development history lacks its original baseline')
    state = scheduler_module.Sweep(strategies,'baseline',result['baseline_score'],baseline_profile,
                                   max_rounds=max_rounds)
    cursor = iter(outcomes[1:])
    count = 0
    while proposed := state.next():
        mechanism,variant = proposed
        profile = profile_module.mutate(state.profile,result['family'],variant)
        if not state.claim(profile):
            continue
        observed = next(cursor,None)
        if observed is None or observed['strategy']!=mechanism['id'] or observed['variant']!=variant:
            raise ValueError('Missing or reordered scheduled development outcome')
        improved = state.observe(observed['candidate'],profile,observed['score'],qualified=observed['qualified'])
        if (improved!=observed['improved'] or state.best_id!=observed['best_candidate']
            or state.best_score!=observed['best_score'] or state.failures!=observed['consecutive_failures']):
            raise ValueError('Recorded development decision differs from schedule replay')
        count += 1
    if (next(cursor,None) is not None or count!=result['generation'] or state.events!=result['events']
        or state.profile!=result['profile'] or state.best_id!=result['winner']['id']
        or state.stop_reason!=result['status'] or state.round!=result['rounds']):
        raise ValueError('Terminal development history differs from schedule replay')


def summarize_attempt(outcome, native):
    """Keep failed native objectives separate from measured retrieval quality."""
    qualified = native['qualification']['passed']
    summary = native['summary']
    errors = summary['errorCount']
    observed = summary['observedMeanReward']
    if qualified and (not native['evaluable'] or errors or observed is None
                      or not math.isclose(finite(observed,upper=1),outcome['score'],rel_tol=0,abs_tol=1e-12)):
        raise ValueError('Qualified development attempt lacks an observed error-free score')
    status = ('qualified' if qualified else 'native-execution-error' if errors
              else 'qualification-failed')
    return {**{key:outcome[key] for key in ('candidate','strategy','improved',
            'consecutive_failures','variant') if key in outcome},
            'score':observed if qualified else None,'scheduler_reward':outcome['score'],
            'qualified':qualified,'status':status,'execution_errors':errors}


def audit_development(result,protocol,contract):
    modules = {}
    for name in ('profiles','sweep'):
        relative = 'evaluations/enterprise-stratified-evolution/'+name+'.py'
        path = REPO/relative
        if sha(path)!=contract['source_files'][relative]:
            raise ValueError('Frozen schedule implementation drift')
        spec = importlib.util.spec_from_file_location('e7_report_'+name,path)
        modules[name] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modules[name])
    baseline = read(WORK/'baseline/build-semantic-okf-knowledge-skill/assets/retrieval-profile.json')
    replay_history(result,protocol['strategies'][result['family']],baseline,
                   modules['profiles'],modules['sweep'],protocol['budget']['maximum_outer_rounds'])
    attempts = []
    for outcome in result['outcomes']:
        archive = read(host(outcome['archive']))
        native = next(r for r in archive['candidateResults'] if r['candidateId']==outcome['candidate'])
        if (not archive['promotionEligibleProfile'] or not native['promotionEligibleProvenance']
            or not native['evaluable'] or native['summary']['meanReward']!=outcome['score']
            or native['qualification']['passed']!=outcome.get('qualified',True)):
            raise ValueError('Scheduled outcome differs from qualified native evidence')
        attempt = summarize_attempt(outcome,native)
        directory = host(native['jobDirectory'])
        job = read(directory/'result.json')
        duration = elapsed(job)
        if duration is None:
            raise ValueError('Development job is not complete')
        attempt.update(native_job_seconds=duration,
                       archive_sha256=sha(host(outcome['archive'])),
                       job_result_sha256=sha(directory/'result.json'))
        attempts.append(attempt)
    return attempts


def collect():
    result = read(WORK/'recalculation-result.json')
    selection = read(WORK/'selection.json')
    terminal = read(WORK/'terminal-decision.json')
    if result['status']!='complete' or result['selection_sha256']!=sha(WORK/'selection.json'):
        raise ValueError('Final native comparison lacks an unchanged completed selection')
    if set(result['jobs'])!={'baseline','frozen'}:
        raise ValueError('Final comparison requires exactly the baseline and frozen arms')
    protocol, contract = read(WORK/'protocol.json'), read(WORK/'execution-contract.json')
    if sha(WORK/'protocol.json')!=contract['workspace_files']['protocol.json']:
        raise ValueError('Frozen public metadata protocol changed')
    questions_path = REPO/'evaluations/enterprise-rag-bench/raw/questions.jsonl'
    selected_path = WORK/'development-selection-v2/selected.private.json'
    if (sha(questions_path)!=protocol['development']['questions_sha256']
        or sha(selected_path)!=protocol['development']['selection_sha256']):
        raise ValueError('Frozen public question metadata or subset changed')
    questions = sorted((json.loads(line) for line in questions_path.read_text(encoding='utf-8').splitlines()),
                       key=lambda row:row['question_id'])
    seen = {row['question_id'] for row in read(selected_path)}
    if len(questions)!=500 or len(seen)!=120:
        raise ValueError('Frozen public measurement scope changed')
    public = read(WORK/'development-task-map.json')
    taskmap = {Path(row['task']).name:row['family'] for row in public.values() if row['phase']=='recalculation'}
    groups = defaultdict(list)
    for index,question in enumerate(questions):
        groups[('category',question['question_type'])].append(index)
        for application in set(question['source_types']):
            groups[('application',application)].append(index)
        groups[('exposure','evolution-subset' if question['question_id'] in seen else 'remaining-exposed-questions')].append(index)
    routes, grouped, bindings = [],[],[]
    for arm,directory_value in result['jobs'].items():
        directory = host(directory_value)
        require_complete_arm(read(directory/'result.json'))
        trials = sorted(directory.glob('*/result.json'))
        if len(trials)!=8:
            raise ValueError('Final arm does not contain eight native trials')
        found = set()
        for path in trials:
            trial = read(path)
            family = taskmap[trial['task_name']]
            if family in found or trial.get('exception_info'):
                raise ValueError('Duplicate or failed final native trial')
            found.add(family)
            diagnostics_path = path.parent/'verifier/diagnostics.json'
            diagnostics = read(diagnostics_path)
            require_family_routes(family,diagnostics)
            reward = trial['verifier_result']['rewards']
            if diagnostics['status']!='pass' or diagnostics['question_count']!=500 or reward['evidence_integrity']!=1:
                raise ValueError('Invalid final verifier integrity or question coverage')
            for route,metrics in diagnostics['routes'].items():
                cases = diagnostics['cases'][route]
                if len(cases)!=500 or any((case is None)!= (not bool(q['expected_doc_ids'])) for case,q in zip(cases,questions)):
                    raise ValueError('Native case eligibility or ordering differs from the frozen questions')
                independent = aggregate_group(cases,list(range(500)))
                if independent['retrieval_eligible']!=470 or any(
                    not math.isclose(independent[key],metrics[key],rel_tol=0,abs_tol=1e-12) for key in METRICS):
                    raise ValueError('Native case metrics disagree with the final aggregate')
                row = {'family':family,'arm':arm,'route':route,'primary':PRIMARY[family]==route,
                       'questions':500,'retrieval_eligible':470,
                       **{key:finite(metrics[key],upper=1) for key in METRICS},
                       'query_p95_ms':finite(metrics['p95_ms']),
                       'double_build_seconds':finite(diagnostics['build_seconds']),
                       'knowledge_bytes':finite(diagnostics['knowledge_bytes']),
                       'agent_seconds':elapsed(trial.get('agent_execution')),
                       'trial_seconds':elapsed(trial)}
                if row['primary'] and not math.isclose(reward['reward'],row['ndcg_at_10'],rel_tol=0,abs_tol=1e-12):
                    raise ValueError('Primary native reward differs from its route')
                routes.append(row)
                if row['primary']:
                    grouped.extend({'family':family,'arm':arm,'dimension':kind,'group':name,
                                    **aggregate_group(cases,indices)} for (kind,name),indices in sorted(groups.items()))
            bindings.append({'arm':arm,'family':family,'job_result_sha256':sha(directory/'result.json'),
                'lock_sha256':sha(directory/'lock.json'),'trial_result_sha256':sha(path),
                'diagnostics_sha256':sha(diagnostics_path)})
        if found!=set(PRIMARY):
            raise ValueError('Missing final family')
    if len(routes)!=36:
        raise ValueError('Expected eighteen routes in both arms')
    development = []
    for family in PRIMARY:
        row = read(WORK/'family-results'/(family+'.json'))
        if row['status'] not in ('full-round-without-improvement','outer-round-budget-exhausted'):
            raise ValueError('Family search is not terminal')
        attempts = audit_development(row,protocol,contract)
        development.append({key:row[key] for key in ('family','treatment','status','generation',
            'baseline_score','score','profile','rounds')})
        development[-1]['attempts'] = attempts
        development[-1]['stops'] = [e for e in row['events'] if e['event'] in ('strategy-finished','round-finished')]
    return {'schema_version':'enterprise-stratified-aggregate/1.0','source':'native-harbor',
        'status':'complete','corpus_documents':6000,'questions':500,'retrieval_eligible':470,
        'official_overall_evaluated':False,'public_leaderboard_comparable':False,
        'llm_calls':0,'provider_cost_usd':None,'development':development,'development_history_replayed':True,
        'routes':sorted(routes,key=lambda r:(r['family'],r['arm'],r['route'])),
        'groups':grouped,'bindings':bindings,
        'terminal_decision':{key:terminal[key] for key in ('decision','promoted','private_gate_opened',
            'further_evolution_permitted','families','native_aggregate_gate_passed') if key in terminal},
        'selection_skill_digest':selection['skill_digest'],
        'protocol_sha256':sha(WORK/'protocol.json'),'execution_contract_sha256':sha(WORK/'execution-contract.json'),
        'selection_sha256':sha(WORK/'selection.json'),'terminal_sha256':sha(WORK/'terminal-decision.json'),
        'source_questions_sha256':sha(questions_path)}


def number(value,scale=100):
    return 'N/A' if value is None else f'{value*scale:.2f}'


def paired(rows,dimension=None):
    keys = ['family'] if dimension is None else ['group','family']
    mapping = defaultdict(dict)
    for row in rows:
        if dimension is None and not row.get('primary'):
            continue
        if dimension is not None and row['dimension']!=dimension:
            continue
        key = tuple(row[field] for field in keys)
        if row['arm'] in mapping[key]:
            raise ValueError('Duplicate paired aggregate')
        mapping[key][row['arm']] = row
    if any(set(arms)!={'baseline','frozen'} for arms in mapping.values()):
        raise ValueError('Incomplete paired aggregate')
    return mapping


def group_leaders(rows, dimension):
    """Describe winners within a fixed retrospective contract, retaining ties."""
    groups = defaultdict(list)
    for (group,_),arms in paired(rows,dimension).items():
        groups[group].append(arms['frozen'])
    result = []
    for group,members in sorted(groups.items()):
        counts = {(r['questions'],r['retrieval_eligible']) for r in members}
        if len(counts)!=1:
            raise ValueError('Group families have different question denominators')
        eligible = [r for r in members if r['ndcg_at_10'] is not None]
        score = max(finite(r['ndcg_at_10'],upper=1) for r in eligible) if eligible else None
        result.append({'group':group,'families':sorted(r['family'] for r in eligible
            if math.isclose(r['ndcg_at_10'],score,rel_tol=0,abs_tol=1e-12)),
            'score':score,'questions':members[0]['questions'],'retrieval_eligible':members[0]['retrieval_eligible']})
    return result


def comparison(value):
    return {'schema_version':'final-report-comparison/1.0','report':'README.md',
        'heading':'## Final primary routes',
        'dataset_scope':{'dataset_id':'enterprise-rag-e7-fulltext-500','cohort':'retrospective-all-500',
            'identity_grouping':'6000 reference-enriched full-text documents; one exposed source family',
            'candidate_budget':'Top-10; jointly frozen development profile',
            'metric_contract':'native-verifier-and-execution-sha256:'+value['execution_contract_sha256']},
        'metrics':[{'id':key,'label':label,'unit':unit,'direction':direction,'aggregation':aggregation,
                    'display_precision':2} for key,label,unit,direction,aggregation in
            [('ndcg_at_10','nDCG@10','percent','higher','mean'),
             ('recall_at_10','Recall@10','percent','higher','mean'),
             ('mrr_at_10','MRR@10','percent','higher','mean'),
             ('representative_p95_ms','Query P95 (ms)','ms','lower','percentile_95')]],
        'alternatives':[{'id':row['family']+'-'+row['arm'],
            'label':row['family']+' / '+row['arm']+' / '+row['route'],
            'metrics':{**{key:row[key]*100 for key in METRICS[:3]},
                       'representative_p95_ms':row['query_p95_ms']}}
            for row in value['routes'] if row['primary']]}


def render(value):
    pairs = paired(value['routes'])
    lines = ['# EnterpriseRAG E7: all-family stratified evolution','',
        'Completed native retrieval comparison: **500 questions, 470 with qrels, 6,000 complete documents**. '
        'The corpus is reference-enriched and all questions have prior exposure. This is an internal retrospective '
        'comparison, with no official answer Overall or public leaderboard rank.','',
        '**Terminal bundle decision:** '+value['terminal_decision']['decision']+'. '
        'All eight selections were frozen jointly before the final comparison and any private release.','',
        '[Category comparison](categories.md) · [Application comparison](applications.md) · '
        '[CTA](cta.md) · [All routes](routes.md) · [Development and stopping rules](development.md)','',
        '## Final primary routes','',
        '| Family | Baseline nDCG@10 | Frozen nDCG@10 | Delta pp | Frozen recall@10 | Frozen MRR@10 | Frozen full evidence@10 |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for (family,),arms in sorted(pairs.items(),key=lambda item:-item[1]['frozen']['ndcg_at_10']):
        a,b = arms['baseline'],arms['frozen']
        lines.append(f"| [{family}](skills/{family}.md) | {number(a['ndcg_at_10'])} | {number(b['ndcg_at_10'])} | "
            f"{(b['ndcg_at_10']-a['ndcg_at_10'])*100:+.2f} | {number(b['recall_at_10'])} | "
            f"{number(b['mrr_at_10'])} | {number(b['full_qrel_coverage_at_10'])} |")
    lines += ['', 'All values are percentages except the signed percentage-point delta. The frozen arm is the exact '
        'development selection even when its terminal gate rejects promotion; final results never trigger reselection. '
        'Thirty no-reference questions remain in execution and latency, with no retrieval score.','',
        '![Baseline and frozen primary routes](comparison.svg)','',
        'The [existing full-corpus Classical/Luna experiment](../../../enterprise-classical-full/README.md) '
        'uses 511,962 documents and a separate answer/judge contract. These results do not replace that measurement.','',
        'The [study guide](../../../../../docs/enterprise-stratified-evolution.md) explains sampling, source rendering, '
        'construction/consultation isolation and the one-way gate. Full exact aggregates are in '
        '[aggregate.json](aggregate.json); native artifact hashes are included without raw questions, answers or traces.']
    files = {'README.md':'\n'.join(lines)+'\n'}
    for dimension,filename in (('category','categories.md'),('application','applications.md'),('exposure','exposure.md')):
        lines = ['# '+dimension.title()+' comparison','', '[General report](README.md)','',
            'Metrics average native case scores on eligible questions. Application groups overlap; they are not independent '
            'datasets. The remaining exposed questions are retrospective, not a new holdout.','',
            '## Highest frozen primary route per group','',
            'These descriptive leaders use unrounded scores and retain ties within 1e-12. They do not change selection or promotion.','',
            '| Group | Highest frozen family | nDCG@10 | Eligible questions |',
            '| --- | --- | ---: | ---: |']
        for leader in group_leaders(value['groups'],dimension):
            lines.append(f"| {leader['group']} | {', '.join(leader['families']) or 'N/A'} | "
                         f"{number(leader['score'])} | {leader['retrieval_eligible']} |")
        lines += ['', '## All paired family measurements','',
            '| Group | Family | Questions | Eligible | Baseline nDCG@10 | Frozen nDCG@10 | Delta pp |',
            '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
        for (group,family),arms in sorted(paired(value['groups'],dimension).items()):
            a,b = arms['baseline'],arms['frozen']
            delta = None if b['ndcg_at_10'] is None else b['ndcg_at_10']-a['ndcg_at_10']
            lines.append(f"| {group} | {family} | {b['questions']} | {b['retrieval_eligible']} | "
                f"{number(a['ndcg_at_10'])} | {number(b['ndcg_at_10'])} | {number(delta)} |")
        files[filename]='\n'.join(lines)+'\n'
    lines = ['# Cost, time and quality','', '[General report](README.md)','',
        'Two CPU threads and 6 GiB per agent; at most two concurrent trials. Zero LLM calls. '
        'Embedding inference uses local CPU. Provider cost is N/A, and host CPU costs are not priced. '
        'Build time includes two builds and matched validations. Query P95 is one descriptive pass over all 500 questions.','',
        '| Family | Arm | nDCG@10 | Query P95 ms | Double build s | Agent s | Trial s | Knowledge MiB |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for row in value['routes']:
        if row['primary']:
            lines.append(f"| {row['family']} | {row['arm']} | {number(row['ndcg_at_10'])} | "
                f"{number(row['query_p95_ms'],1)} | {number(row['double_build_seconds'],1)} | "
                f"{number(row['agent_seconds'],1)} | {number(row['trial_seconds'],1)} | {number(row['knowledge_bytes']/2**20,1)} |")
    lines += ['', '## Development work including rejected attempts','',
        'Each original native job is counted once per family, including its baseline and failed candidates. '
        'Summed job elapsed time is a workload measure; overlapping trials mean it is not campaign wall time. '
        'It excludes joint replay, final recalculation, private validation and host staging overhead.','',
        '| Family | Native jobs | Qualified | Execution errors | Summed job seconds |',
        '| --- | ---: | ---: | ---: | ---: |']
    for row in value['development']:
        attempts = row['attempts']
        lines.append(f"| {row['family']} | {len(attempts)} | {sum(a['qualified'] for a in attempts)} | "
            f"{sum(a['execution_errors'] for a in attempts)} | "
            f"{number(sum(a['native_job_seconds'] for a in attempts),1)} |")
    files['cta.md']='\n'.join(lines)+'\n'
    lines = ['# All eighteen routes in both frozen arms','', '[General report](README.md)','',
        'These are diagnostics; the family selection routes were fixed before development.','',
        '| Family | Arm | Route | Primary | nDCG@10 | Recall@10 | MRR@10 | Full evidence@10 |',
        '| --- | --- | --- | --- | ---: | ---: | ---: | ---: |']
    for row in value['routes']:
        lines.append('| '+ ' | '.join([row['family'],row['arm'],row['route'],str(row['primary']),
            *[number(row[key]) for key in METRICS]])+' |')
    files['routes.md']='\n'.join(lines)+'\n'
    lines = ['# Development selection and stopping evidence','', '[General report](README.md)','',
        'Scores use the preregistered category weights on 112 eligible questions from the 120-question subset. '
        'A complete non-improving round establishes a plateau only in the tested finite catalog. '
        'Budget exhaustion is a separate stop reason.','',
        '| Family | Treatment | Baseline nDCG@10 | Retained nDCG@10 | New trials | Rounds | Stop reason |',
        '| --- | --- | ---: | ---: | ---: | ---: | --- |']
    for row in value['development']:
        lines.append(f"| {row['family']} | {row['treatment']} | {number(row['baseline_score'])} | "
                     f"{number(row['score'])} | {row['generation']} | {row['rounds']} | {row['status']} |")
        family_lines = ['# '+row['family']+' evolution','', '[General report](../README.md)','',
            'Treatment: '+row['treatment']+'. Stop: '+row['status']+'.','',
            'Only qualified observations have a retrieval score. An execution error may receive a zero '
            'objective from the native scheduler and count as a miss, but it is not a measured zero nDCG. '
            'The raw scheduler reward remains separately labeled in aggregate.json.','',
            '| Candidate | Mechanism | Weighted nDCG@10 | Native status | Improved | Consecutive misses |',
            '| --- | --- | ---: | --- | --- | ---: |']
        for attempt in row['attempts']:
            family_lines.append(f"| {attempt['candidate']} | {attempt['strategy']} | {number(attempt['score'])} | "
                f"{attempt['status']} | {attempt.get('improved',False)} | {attempt.get('consecutive_failures',0)} |")
        family_lines += ['', 'Exact retained source-generic profile:', '', '```json',
                         json.dumps(row['profile'][row['family']],indent=2,sort_keys=True), '```']
        files['skills/'+row['family']+'.md']='\n'.join(family_lines)+'\n'
    files['development.md']='\n'.join(lines)+'\n'
    return files


def plot(value,output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    pairs = sorted(paired(value['routes']).items(),key=lambda item:item[1]['frozen']['ndcg_at_10'])
    fig,axis = plt.subplots(figsize=(10,6),layout='constrained')
    for offset,arm,color,label in ((-.18,'baseline','#9ba9b7','Baseline'),(.18,'frozen','#126777','Frozen selection')):
        axis.barh([i+offset for i in range(8)],[arms[arm]['ndcg_at_10']*100 for _,arms in pairs],
                  height=.32,color=color,label=label)
    axis.set_yticks(range(8),[key[0] for key,_ in pairs])
    axis.set_xlim(0,100)
    axis.set_xlabel('nDCG@10 (%) · 470 eligible questions')
    axis.set_title('EnterpriseRAG E7 · 6,000 full-text documents\nInternal retrospective comparison')
    axis.legend(loc='lower right')
    fig.savefig(output/'comparison.svg')
    fig.savefig(output/'comparison.png',dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args = parser.parse_args()
    value = collect()
    args.output.mkdir(parents=True,exist_ok=False)
    files = render(value)
    files['aggregate.json']=json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n'
    files['comparison.json']=json.dumps(comparison(value),indent=2,sort_keys=True,allow_nan=False)+'\n'
    for relative,text in files.items():
        path=args.output/relative
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(text,encoding='utf-8',newline='\n')
    plot(value,args.output)
    print(json.dumps({'status':'complete','families':8,'routes':36,'native_trials':16,'files':len(files)+2}))


if __name__=='__main__':
    main()
