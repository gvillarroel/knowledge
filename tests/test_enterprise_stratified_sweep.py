"""Exercise repeat-round scheduling and the stricter joint acceptance boundary."""
import copy
import importlib.util
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]/'evaluations/enterprise-stratified-evolution'


def load(name):
    # These are executable tools with sibling imports. Isolate their short
    # module names so collection cannot redirect other evaluation test suites.
    before = sys.modules.copy()
    sys.path.insert(0,str(HERE))
    try:
        for key in ('prepare','profiles','dataset','run','sweep'):
            sys.modules.pop(key,None)
        spec = importlib.util.spec_from_file_location('e7_test_'+name,HERE/(name+'.py'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(HERE))
        for key in ('prepare','profiles','dataset','run','sweep'):
            sys.modules.pop(key,None)
            if key in before:
                sys.modules[key] = before[key]


SCHEDULER, PROFILES, FINAL, CORPUS = (load(name) for name in ('sweep','profiles','finalize','corpus'))


def test_later_gain_reopens_earlier_mechanism_until_a_complete_plateau():
    schedule = SCHEDULER.Sweep([
        {'id':'x','variants':[1,2]}, {'id':'y','variants':[1]}],
        'baseline',.5,{'x':0,'y':0})
    calls = []
    while proposed := schedule.next():
        strategy,value = proposed
        profile = copy.deepcopy(schedule.profile)
        profile[strategy['id']] = value
        if not schedule.claim(profile):
            continue
        score = .5 if profile['y']==0 else .6+.1*profile['x']
        calls.append((schedule.round,profile,score))
        schedule.observe(str(len(calls)),profile,score)
    assert schedule.round == 3
    assert schedule.best_score == pytest.approx(.8)
    assert schedule.profile == {'x':2,'y':1}
    assert schedule.stop_reason == 'full-round-without-improvement'
    assert any(round_number==2 and profile['x']==2 for round_number,profile,_ in calls)
    events = copy.deepcopy(schedule.events)
    assert schedule.next() is None and schedule.events == events


def test_three_misses_switch_mechanism_and_a_success_resets_the_streak():
    schedule = SCHEDULER.Sweep([{'id':'a','variants':list(range(9))},
                                {'id':'b','variants':[1]}],'baseline',.5,{})
    for index,score in enumerate((.4,.4,.6,.5,.5,.5)):
        assert schedule.next()[0]['id']=='a'
        schedule.observe(str(index),{'x':index},score)
    assert schedule.next()[0]['id']=='b'
    event = next(e for e in schedule.events if e['event']=='strategy-finished')
    assert event['reason']=='three-consecutive-failures'
    assert event['unused_variants']==3


def test_budget_exhaustion_does_not_claim_plateau():
    schedule = SCHEDULER.Sweep([{'id':'a','variants':[1]}],'baseline',.5,{},max_rounds=1)
    schedule.next()
    schedule.observe('winner',{'a':1},.6)
    assert schedule.next() is None
    assert schedule.stop_reason=='outer-round-budget-exhausted'
    assert schedule.events[-1]['improved'] is True


def test_duplicate_profiles_do_not_count_as_misses_or_execute_twice():
    schedule = SCHEDULER.Sweep([], 'baseline',.5,{'x':1})
    assert not schedule.claim({'x':1})
    assert schedule.claim({'x':2})
    assert not schedule.claim({'x':2})
    assert schedule.failures==0


def test_execution_error_cannot_become_semantic_zero():
    schedule = SCHEDULER.Sweep([], 'baseline',.5,{})
    with pytest.raises(RuntimeError,match='Non-evaluable'):
        schedule.observe('missing',{},None,evaluable=False)
    assert schedule.failures==0 and schedule.best_score==.5


def gate_fixture():
    metadata = {}
    cases = []
    for family in PROFILES.FAMILIES:
        for group in ('first','second'):
            name = family+'-'+group
            metadata[name] = {'task':'/opaque/'+name,'family':family,'source_group':group}
            cases.append({'taskName':name,'evaluable':True,'delta':.02})
    return {'perCase':cases,'promoted':True,'baselineQualified':True,'candidateQualified':True},metadata


def test_joint_gate_rejects_one_regressing_family_despite_positive_overall_mean():
    native,metadata = gate_fixture()
    for row in native['perCase'][:2]:
        row['delta'] = -.01
    assert sum(r['delta'] for r in native['perCase'])>0
    accepted,rows = FINAL.family_gate(native,metadata)
    assert not accepted and sum(row['accepted'] for row in rows)==7


def test_gate_uses_two_source_mean_but_never_waives_native_integrity():
    native,metadata = gate_fixture()
    native['perCase'][0]['delta'] = -.02
    assert FINAL.family_gate(native,metadata)[0]
    native['baselineQualified'] = False
    assert not FINAL.family_gate(native,metadata)[0]
    native['baselineQualified'] = True
    native['perCase'][0]['evaluable'] = False
    assert not FINAL.family_gate(native,metadata)[0]


def test_missing_or_duplicate_source_cells_cannot_pass():
    native,metadata = gate_fixture()
    native['perCase'].pop()
    with pytest.raises(ValueError,match='coverage'):
        FINAL.family_gate(native,metadata)
    native,metadata = gate_fixture()
    first_family = PROFILES.FAMILIES[0]
    for row in metadata.values():
        if row['family']==first_family:
            row['source_group']='same'
    with pytest.raises(ValueError,match='source group'):
        FINAL.family_gate(native,metadata)


def test_inventory_has_closed_treatment_scope_and_117_variants_per_round():
    assert sum(len(s['variants']) for f in PROFILES.FAMILIES for s in PROFILES.inventory(f))==117
    base = PROFILES.baseline_profile()
    for family in PROFILES.FAMILIES:
        for strategy in PROFILES.inventory(family):
            for variant in strategy['variants']:
                changed = PROFILES.mutate(base,family,variant)
                assert all(changed[f]==base[f] for f in PROFILES.FAMILIES if f!=family)
                untouched = 'search' if family in PROFILES.CONSTRUCTION else 'plan'
                assert changed[family][untouched]==base[family][untouched]


def test_source_rendering_preserves_all_characters_except_declared_line_separators():
    value = 'Alpha\u0085Beta\u2028Gamma\u2029Delta\t\r\n\u00a0\u4e2d\U0001f642'
    expected = 'Alpha\nBeta\nGamma\nDelta\t\r\n\u00a0\u4e2d\U0001f642'
    assert CORPUS.render_text(value)==expected
    assert CORPUS.render_text(expected)==expected
