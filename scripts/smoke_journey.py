#!/usr/bin/env python3
"""Synthetic CLI journey. Every step is a fresh process, not a model-quality eval."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    work = ROOT/'work'; work.mkdir(exist_ok=True)
    calls = 0
    with tempfile.TemporaryDirectory(prefix='journey-', dir=work) as td:
        workspace = Path(td)
        def run(script, *args, expected=0, parse=True):
            nonlocal calls
            calls += 1
            result = subprocess.run([sys.executable, '-B', str(ROOT/'scripts'/script), *args],
                                    cwd=workspace, capture_output=True, text=True)
            assert result.returncode == expected, (script, args, result.stdout, result.stderr)
            return json.loads(result.stdout) if parse and expected == 0 else result.stdout + result.stderr
        def save(name, payload):
            path = workspace/name; path.write_text(json.dumps(payload)); return str(path)
        def state():
            return run('state_store.py', 'show')
        def unchanged_after_failure(script, *args):
            path = workspace/'state/roleward-state.json'; before = path.read_bytes()
            run(script, *args, expected=1)
            assert path.read_bytes() == before

        run('state_store.py', 'init', parse=False)
        assert not run('context_state.py', 'readiness')['ready']
        context = {'career_evidence':[{'domain':'experience','statement':'Owned synthetic enterprise workflows'}],
                   'direction':{'target_roles':['Product Manager']},
                   'search_policy':{'geographies':['Germany'],'authorization_state':'not_sure'}}
        run('context_state.py', 'apply-extraction', '--input', save('context.json', context))
        assert run('context_state.py', 'readiness')['ready']
        run('context_state.py', 'confirm-field', '--field', 'search_policy.geographies', '--value-json', '["Germany"]', parse=False)
        review = run('context_state.py', 'review', parse=False)
        assert 'Source-backed' in review and 'Confirmed' in review
        saved = state(); evidence = saved['profile']['career_evidence'][0]['id']
        evidence_authority = saved['profile']['career_evidence'][0]['authority']
        conflict = {'search_policy':{'geographies':['Singapore']}}
        run('context_state.py', 'apply-extraction', '--input', save('conflict.json', conflict))
        assert state()['search_policy']['geographies']['value'] == ['Germany']

        scan = run('scan_state.py', 'start')
        candidates = json.loads((ROOT/'fixtures/_inputs/scan-candidates.json').read_text())
        run('scan_state.py', 'ingest', '--scan-id', scan['id'], '--input', save('candidates.json', candidates))
        finished = run('scan_state.py', 'finalize', '--scan-id', scan['id'])
        assert len(finished['selected_opportunity_ids']) == 1
        payload = json.loads((ROOT/'fixtures/_inputs/direct-opportunity-assessment.json').read_text())
        assessed = run('opportunity_state.py', 'assess', '--input', save('assessment.json', payload))
        opp_id = assessed['opportunity_id']
        assert opp_id == finished['selected_opportunity_ids'][0]
        original_assessment = assessed['assessment']
        run('opportunity_state.py', 'decision', '--opportunity-id', opp_id, '--decision', 'pursue', '--reason', 'Synthetic user choice')
        assert len(state()['opportunities'][opp_id]['pursuit_decisions']) == 1

        content = {'thesis':'Synthetic workflow hire case','proof_points':[evidence],'credibility_gaps':['Independent AI only']}
        draft = run('application_state.py', 'position', '--opportunity-id', opp_id, '--input', save('position.json', content))
        artifact_path = workspace/'resume.txt'; artifact_path.write_text('Owned synthetic enterprise workflows.\n')
        artifact = {'local_path':str(artifact_path),'claims':[{'text':'Owned synthetic enterprise workflows','evidence_ids':[evidence]}]}
        artifact_input = save('artifact.json', artifact)
        unchanged_after_failure('application_state.py', 'artifact', '--opportunity-id', opp_id, '--type', 'resume', '--input', artifact_input)
        # This is a synthetic test event, not approval of any real user's positioning.
        reviewed = run('application_state.py', 'review-positioning', '--opportunity-id', opp_id, '--revision-id', draft['id'])
        recorded = run('application_state.py', 'artifact', '--opportunity-id', opp_id, '--type', 'resume', '--input', artifact_input)
        assert recorded['sha256'] == hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        assert recorded['positioning_revision_id'] == reviewed['id']
        rejected = {'claims':[{'text':'Invented credential','evidence_ids':['missing-id']}]}
        unchanged_after_failure('application_state.py','artifact','--opportunity-id',opp_id,'--type','resume','--input',save('invalid.json',rejected))
        run('application_state.py','artifact','--opportunity-id',opp_id,'--type','contact_shortlist','--input',save('contacts.json',{'contacts':[]}))

        payload['job']['text'] += ' Updated requirement: own customer discovery.'
        revised = run('opportunity_state.py', 'assess', '--input', save('updated-assessment.json',payload))
        assert revised['opportunity_id'] == opp_id
        unchanged_after_failure('application_state.py','artifact','--opportunity-id',opp_id,'--type','resume','--input',artifact_input)
        fresh = run('application_state.py','position','--opportunity-id',opp_id,'--input',save('fresh-position.json',content))
        run('application_state.py','review-positioning','--opportunity-id',opp_id,'--revision-id',fresh['id'])
        run('application_state.py','artifact','--opportunity-id',opp_id,'--type','resume','--input',artifact_input)
        run('learn_state.py','status','--opportunity-id',opp_id,'--status','applied')
        run('learn_state.py','outcome','--opportunity-id',opp_id,'--status','rejected','--reason-authority','unknown')
        final = state(); opp = final['opportunities'][opp_id]
        assert opp['pursuit_assessments'][0] == original_assessment
        assert opp['application_artifacts'][0] == recorded
        assert opp['application']['outcomes'][-1]['reason'] is None
        assert not final['signals']['learned_signals'] and not final['profile']['preferences']
        assert final['profile']['career_evidence'][0]['authority'] == evidence_authority
        run('state_store.py','validate',parse=False)
        persisted = (workspace/'state/roleward-state.json').read_bytes()
        run('state_store.py','init',expected=2,parse=False)
        assert (workspace/'state/roleward-state.json').read_bytes() == persisted
    print(json.dumps({'result':'passed','fresh_process_steps':calls,
          'scope':'Synthetic deterministic CLI lifecycle and disk continuity; no live search, semantic model evaluation, real user approval or application.'}))


if __name__ == '__main__':
    main()
