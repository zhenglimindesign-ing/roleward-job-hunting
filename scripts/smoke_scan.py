#!/usr/bin/env python3
import json
import tempfile
from pathlib import Path

from context_state import AUTH_CONFIRMED, AUTH_SOURCE, apply_extraction, set_field
from opportunity_state import record_decision
from scan_state import (
    SearchBudgetReached,
    build_search_plan,
    finalize_scan,
    hard_constraint_check,
    ingest_candidates,
    log_search,
    start_scan,
)
from state_store import empty_state, load_state, save_state

payload = json.loads(Path('fixtures/_inputs/scan-candidates.json').read_text())
with tempfile.TemporaryDirectory() as td:
    path = Path(td) / 'state.json'
    state = empty_state()
    apply_extraction(state, {
        'source_id': 'src-scan',
        'career_evidence': [{'domain': 'experience', 'statement': 'Led B2B product workflows'}],
        'direction': {'target_roles': ['AI Product Manager']},
        'search_policy': {'geographies': ['Germany', 'Netherlands'], 'authorization_state': 'sponsorship_required'}
    }, AUTH_SOURCE)
    set_field(state, state['search_policy'], 'geographies', ['Germany', 'Netherlands'], authority=AUTH_CONFIRMED, source_ids=[], field_path='search_policy.geographies')
    save_state(path, state)
    state = load_state(path)

    run = start_scan(state, 'manual')
    assert run['trigger'] == 'manual'
    assert run['plan']['coverage_modes'] == ['title_led', 'capability_led', 'adjacent_role']
    assert 'search_budget' not in run['plan']
    log_search(state, run['id'], kind='query', intent='title_led', text='AI Product Manager Germany')
    result = ingest_candidates(state, run['id'], payload['candidates'])
    assert result['candidates'][0]['disposition'] == 'worth_review'
    assert result['candidates'][1]['disposition'] == 'screened_out'
    assert 'outside_confirmed_geography' in result['candidates'][1]['hard_constraint_check']['violations']
    assert result['candidates'][2]['disposition'] == 'verify_first'
    assert 'employability' in result['candidates'][2]['hard_constraint_check']['needs_verification']

    final = finalize_scan(state, run['id'])
    assert len(final['selected_opportunity_ids']) == 2
    assert final['search_summary']['query_count'] == 1
    assert final['search_summary']['query_limit'] is None
    first_opp = final['selected_opportunity_ids'][0]
    decision = record_decision(state, first_opp, 'pursue', 'Strong product ownership and direction fit')
    assert decision['decision'] == 'pursue'
    assert len(state['signals']['decision_observations']) == 1
    save_state(path, state)
    reloaded = load_state(path)
    assert reloaded['scan_runs'][run['id']]['status'] == 'complete'
    assert reloaded['opportunities'][first_opp]['pursuit_decisions'][0]['decision'] == 'pursue'
    print('Scan trigger/hard-constraint/reservoir/decision smoke passed')

# A preferred country is not an allowlist in a confirmed exclusion scope.
state = empty_state()
state['search_policy']['geography'] = {
    'authority': AUTH_CONFIRMED,
    'value': {'mode': 'global_excluding', 'excluded_countries': ['China'],
              'preferred_countries': ['United Arab Emirates']}}
plan = build_search_plan(state)
assert plan['geographies'] == []
assert plan['geography_scope']['preferred_countries'] == ['United Arab Emirates']
for country in ['United Arab Emirates', 'Germany']:
    check = hard_constraint_check(state, {'facts': {'geographies': [country]}})
    assert check['passes']
check = hard_constraint_check(state, {'facts': {'geographies': ['China']}})
assert check['violations'] == ['outside_confirmed_geography']
assert hard_constraint_check(state, {'facts': {'geographies': ['China', 'Germany']}})['passes']
assert hard_constraint_check(state, {'facts': {}})['needs_verification'] == ['employability', 'geography']
state['search_policy']['geography']['authority'] = AUTH_SOURCE
assert build_search_plan(state)['geography_scope'] is None
assert hard_constraint_check(state, {'facts': {'geographies': ['China']}})['passes']
print('Structured geography exclusions and source-authority smoke passed')

# A user-stated per-Scan bound covers every executed search, including verification lookups.
state = empty_state()
state['profile']['direction']['target_roles'] = {'authority': AUTH_CONFIRMED, 'value': ['AI Product Manager']}
state['search_policy']['geography'] = {'authority': AUTH_CONFIRMED, 'value': ['UAE']}
run = start_scan(state, 'manual', max_results=1, max_queries=3, max_sources=2)
assert run['plan']['search_budget'] == {'max_queries': 3, 'max_sources': 2}
assert 'max_results' not in state['search_policy']
for intent in ['title_led', 'capability_led', 'adjacent_role']:
    log_search(state, run['id'], kind='query', intent=intent, text=f'{intent} UAE')
try:
    log_search(state, run['id'], kind='query', intent='verification', text='employer careers page')
    raise AssertionError('a fourth query must exceed the bound of three')
except SearchBudgetReached:
    pass
log_search(state, run['id'], kind='source', intent='verification', text='https://example.com/jobs/1')
summary = finalize_scan(state, run['id'])['search_summary']
assert summary['query_count'] == 3 and summary['query_limit'] == 3
assert summary['query_by_intent'] == {'title_led': 1, 'capability_led': 1, 'adjacent_role': 1}
assert summary['source_count'] == 1 and summary['source_limit'] == 2
try:
    log_search(state, run['id'], kind='query', intent='title_led', text='after completion')
    raise AssertionError('a completed Scan must not accept more searches')
except ValueError:
    pass
print('Scan search-log and per-run bound smoke passed')
