#!/usr/bin/env python3
import json
import tempfile
from pathlib import Path

from context_state import AUTH_CONFIRMED, AUTH_SOURCE, apply_extraction, set_field
from opportunity_state import record_decision
from scan_state import finalize_scan, ingest_candidates, start_scan
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
    assert run['plan']['coverage_modes'] == ['title_led', 'capability_led']
    result = ingest_candidates(state, run['id'], payload['candidates'])
    assert result['candidates'][0]['disposition'] == 'worth_review'
    assert result['candidates'][1]['disposition'] == 'screened_out'
    assert 'outside_confirmed_geography' in result['candidates'][1]['hard_constraint_check']['violations']
    assert result['candidates'][2]['disposition'] == 'verify_first'
    assert 'employability' in result['candidates'][2]['hard_constraint_check']['needs_verification']

    final = finalize_scan(state, run['id'])
    assert len(final['selected_opportunity_ids']) == 2
    first_opp = final['selected_opportunity_ids'][0]
    decision = record_decision(state, first_opp, 'pursue', 'Strong product ownership and direction fit')
    assert decision['decision'] == 'pursue'
    assert len(state['signals']['decision_observations']) == 1
    save_state(path, state)
    reloaded = load_state(path)
    assert reloaded['scan_runs'][run['id']]['status'] == 'complete'
    assert reloaded['opportunities'][first_opp]['pursuit_decisions'][0]['decision'] == 'pursue'
    print('Scan trigger/hard-constraint/reservoir/decision smoke passed')
