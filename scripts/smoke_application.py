#!/usr/bin/env python3
import tempfile
from pathlib import Path

from application_state import record_artifact, record_positioning_draft, review_positioning
from context_state import AUTH_CONFIRMED, add_career_evidence
from opportunity_state import upsert_opportunity
from state_store import empty_state, load_state, save_state

with tempfile.TemporaryDirectory() as td:
    state_path = Path(td) / 'state.json'
    artifact_path = Path(td) / 'resume.txt'
    artifact_path.write_text('Synthetic resume artifact', encoding='utf-8')
    state = empty_state()
    evidence_id = add_career_evidence(
        state,
        domain='experience',
        statement='Led complex B2B workflow products',
        authority=AUTH_CONFIRMED,
        source_ids=[],
    )
    opp_id, _ = upsert_opportunity(state, {
        'company': 'Example AI',
        'title': 'Senior Product Manager, AI Platform',
        'url': 'https://jobs.example.com/ai-pm',
        'text': 'Own AI platform direction.',
        'live_status': 'verified_live',
    })
    draft = record_positioning_draft(state, opp_id, {
        'thesis': 'B2B platform leader with a credible AI transition',
        'proof_points': [evidence_id],
        'credibility_gaps': ['Formal AI platform ownership is adjacent rather than direct'],
    })
    try:
        record_artifact(state, opp_id, 'resume', {
            'local_path': str(artifact_path),
            'claims': [{'text': 'Led complex B2B workflow products', 'evidence_ids': [evidence_id]}],
        })
        raise AssertionError('artifact should require reviewed positioning')
    except ValueError as exc:
        assert 'reviewed Positioning' in str(exc)

    reviewed = review_positioning(state, opp_id, draft['id'])
    artifact = record_artifact(state, opp_id, 'resume', {
        'local_path': str(artifact_path),
        'claims': [{'text': 'Led complex B2B workflow products', 'evidence_ids': [evidence_id]}],
    })
    assert artifact['positioning_revision_id'] == reviewed['id']
    assert artifact['evidence_ids'] == [evidence_id]
    try:
        record_artifact(state, opp_id, 'contact_shortlist', {
            'contacts': [{'name': str(i)} for i in range(4)],
            'claims': [],
        })
        raise AssertionError('contact shortlist should cap at 3')
    except ValueError as exc:
        assert 'at most 3 contacts' in str(exc)

    save_state(state_path, state)
    reloaded = load_state(state_path)
    assert len(reloaded['opportunities'][opp_id]['positioning_revisions']) == 2
    assert len(reloaded['opportunities'][opp_id]['application_artifacts']) == 1
    print('Positioning review/artifact provenance smoke passed')
