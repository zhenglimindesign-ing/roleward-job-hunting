#!/usr/bin/env python3
import json
import tempfile
from pathlib import Path

from state_store import empty_state, save_state, load_state
from opportunity_state import record_assessment, normalize_url

payload=json.loads(Path('fixtures/_inputs/direct-opportunity-assessment.json').read_text())
with tempfile.TemporaryDirectory() as td:
    path=Path(td)/'state.json'
    save_state(path,empty_state())
    s=load_state(path)
    first=record_assessment(s,payload)
    save_state(path,s)
    r=load_state(path)
    opp=r['opportunities'][first['opportunity_id']]
    scores=opp['pursuit_assessments'][0]['scores']
    assert scores['capability_match']==80, scores
    assert scores['overall_match']==80, scores
    assert scores['screening_legibility']==70, scores
    assert scores['career_value']==75, scores
    assert opp['canonical_url']=='https://jobs.example.com/ai-pm'
    # Same job with tracking variation must converge to the same opportunity.
    payload2=json.loads(json.dumps(payload))
    payload2['job']['url']='https://jobs.example.com/ai-pm?utm_campaign=other'
    second=record_assessment(r,payload2)
    assert second['opportunity_id']==first['opportunity_id']
    assert len(r['opportunities'])==1
    print('Direct Opportunity/Pursuit score smoke passed')
