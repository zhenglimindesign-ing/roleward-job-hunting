#!/usr/bin/env python3
from pathlib import Path
import json
import tempfile

from state_store import empty_state, save_state, load_state
from context_state import apply_extraction, set_field, readiness, AUTH_CONFIRMED, AUTH_SOURCE

with tempfile.TemporaryDirectory() as td:
    path=Path(td)/'state.json'
    s=empty_state()
    save_state(path,s)
    s=load_state(path)
    payload={
        'source_id':'src-a',
        'career_evidence':[{'domain':'experience','statement':'Led regulated B2B product workflows'}],
        'direction':{'target_roles':['AI Product Manager']},
        'search_policy':{'geographies':['Germany'],'authorization_state':'not_sure'},
        'preferences':['Prefer product ownership']
    }
    apply_extraction(s,payload,AUTH_SOURCE)
    # Explicit user confirmation supersedes source-level direction.
    set_field(s,s['profile']['direction'],'target_roles',['Senior AI Product Manager'],authority=AUTH_CONFIRMED,source_ids=[],field_path='profile.direction.target_roles')
    # A later source conflict must not overwrite confirmed truth.
    apply_extraction(s,{'source_id':'src-b','direction':{'target_roles':['Implementation Consultant']}},AUTH_SOURCE)
    save_state(path,s)
    r=load_state(path)
    assert r['profile']['direction']['target_roles']['value']==['Senior AI Product Manager']
    assert r['profile']['direction']['target_roles']['authority']==AUTH_CONFIRMED
    assert len(r.get('pending_conflicts',[]))==1
    assert readiness(r)['ready'] is True
    print('Context authority/readiness smoke passed')
