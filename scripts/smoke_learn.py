#!/usr/bin/env python3
import tempfile
from pathlib import Path

from learn_state import confirm_preference, record_outcome, record_preference_observation
from opportunity_state import upsert_opportunity
from state_store import empty_state, load_state, save_state

with tempfile.TemporaryDirectory() as td:
    path = Path(td) / 'state.json'
    state = empty_state()
    opps = []
    for index in range(1, 4):
        opp_id, _ = upsert_opportunity(state, {
            'company': f'Example {index}',
            'title': 'AI Product Manager',
            'url': f'https://jobs.example.com/{index}',
            'text': f'AI product role {index}',
            'live_status': 'verified_live',
        })
        opps.append(opp_id)

    unknown = record_outcome(
        state,
        opps[0],
        status='rejected',
        reason=None,
        reason_authority='unknown',
    )
    assert unknown['reason'] is None
    assert len(state['signals']['learned_signals']) == 0

    first = record_outcome(
        state,
        opps[1],
        status='rejected',
        reason='Role does not sponsor',
        reason_authority='confirmed',
        signal_key='sponsorship_blocker',
    )
    signal = state['signals']['learned_signals'][0]
    assert signal['strength'] == 'weak_observation'
    record_outcome(
        state,
        opps[2],
        status='rejected',
        reason='Role does not sponsor',
        reason_authority='confirmed',
        signal_key='sponsorship_blocker',
    )
    assert signal['strength'] == 'emerging_pattern'
    assert first['learned_signal_id'] == signal['id']

    inferred = None
    for opp_id in opps:
        result = record_preference_observation(
            state,
            opp_id,
            signal_key='prefer_product_ownership',
            statement='Prefer stronger product ownership over implementation-heavy delivery',
        )
        inferred = result['inferred_signal']
    assert inferred is not None
    assert inferred['strength'] == 'emerging_pattern'
    assert inferred['status'] == 'unconfirmed'
    assert not state['profile']['preferences']

    confirmed = confirm_preference(state, inferred['id'])
    assert confirmed['preference_id']
    assert state['profile']['preferences'][0]['authority'] == 'confirmed_truth'
    assert inferred['status'] == 'confirmed_by_user'

    save_state(path, state)
    reloaded = load_state(path)
    assert reloaded['signals']['learned_signals'][0]['strength'] == 'emerging_pattern'
    assert reloaded['profile']['preferences'][0]['authority'] == 'confirmed_truth'
    print('Track/outcome/conservative Learn smoke passed')
