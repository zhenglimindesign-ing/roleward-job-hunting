#!/usr/bin/env python3
from pathlib import Path
import json
import tempfile

from state_store import empty_state, save_state, load_state
from context_state import add_source, apply_extraction, set_field, readiness, review_markdown, AUTH_CONFIRMED, AUTH_SOURCE

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

# Verbatim user wording travels with normalized evidence and must match the source.
s=empty_state()
said='参与过客户调研与产品指标迭代。我独立做过一个 LLM 原型。'
src=add_source(s,source_type='user_statement',label='chat',local_path=None,quote=said)
apply_extraction(s,{'source_id':src,'career_evidence':[
    {'domain':'research','statement':'Participated in customer research and product-metric iteration.','source_quote':'参与过客户调研与产品指标迭代'}]},AUTH_CONFIRMED)
assert s['profile']['sources'][0]['quote']==said
assert s['profile']['career_evidence'][0]['source_quote']=='参与过客户调研与产品指标迭代'
assert '| Participated in customer research and product-metric iteration. | 参与过客户调研与产品指标迭代 | Confirmed |' in review_markdown(s)
try:
    apply_extraction(s,{'source_id':src,'career_evidence':[
        {'domain':'research','statement':'Led customer research.','source_quote':'主导客户调研'}]},AUTH_CONFIRMED)
    raise AssertionError('a source_quote absent from the source wording must be rejected')
except ValueError as exc:
    assert 'verbatim' in str(exc)
print('Context source-wording smoke passed')
