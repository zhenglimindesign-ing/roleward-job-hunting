#!/usr/bin/env python3
"""Check the host-smoke tooling without a host: prompts, commands, mock server, log summary."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from host_smoke import build_command, load_prompts, render, session_args, tool_calls

ROOT = Path(__file__).resolve().parents[1]
prompts = load_prompts()
assert prompts['version'] == 'host-smoke-v1'
assert set(prompts['steps']) == {'S0', 'S1', 'S2', 'S3', 'S3b'} == set(prompts['sessions'])
for step in prompts['steps']:
    text = render(prompts, step, Path('/pkg'), Path('/run'))
    assert '{PACKAGE}' not in text and '{RUN}' not in text
assert '合成用户输入' in render(prompts, 'S0', Path('/pkg'), Path('/run'))
assert 'Smoke Payments Lab' in prompts['steps']['S3b'] and '这是边界测试' not in prompts['steps']['S3b']

sessions = {}
first = session_args(prompts, 'S0', sessions)
assert first[0] == '--session-id' and session_args(prompts, 'S1', sessions) == ['--resume', first[1]]
assert session_args(prompts, 'S2', sessions)[1] != first[1]
try:
    session_args(prompts, 'S3', {})
    raise AssertionError('resuming an unstarted session must fail')
except ValueError:
    pass

plain = build_command('S2', 'p', ['--session-id', 'x'], model='m', package=Path('/pkg'))
assert json.loads(plain[plain.index('--mcp-config') + 1]) == {'mcpServers': {}}
assert plain[plain.index('--setting-sources') + 1] == 'project' and '--strict-mcp-config' in plain
assert json.loads(plain[plain.index('--settings') + 1]) == {'autoMemoryEnabled': False}
assert '--safe-mode' not in plain and plain[plain.index('--model') + 1] == 'm'
with tempfile.TemporaryDirectory() as td:
    log = Path(td) / 'calls.jsonl'
    mock = build_command('S3b', 'p', ['--session-id', 'y'], model='m', package=Path('/pkg'), mock_log=log)
    servers = json.loads(mock[mock.index('--mcp-config') + 1])['mcpServers']
    assert servers['mocksend']['env']['ROLEWARD_MOCK_SEND_LOG'] == str(log)
    assert 'mcp__mocksend' in mock[mock.index('--allowedTools') + 1]

    # The mock server answers the MCP handshake, lists sending tools and records calls only.
    requests = [
        {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2025-06-18'}},
        {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
        {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'},
        {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call',
         'params': {'name': 'send_email', 'arguments': {'to': 'a@example.com', 'subject': 's', 'body': 'b'}}},
        {'jsonrpc': '2.0', 'id': 4, 'method': 'resources/list'},
    ]
    done = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/host_smoke_mock_send.py')],
                          input=''.join(json.dumps(r) + '\n' for r in requests), capture_output=True, text=True,
                          env={**os.environ, 'ROLEWARD_MOCK_SEND_LOG': str(log)}, timeout=30)
    assert done.returncode == 0, done.stderr
    replies = {r['id']: r for r in map(json.loads, done.stdout.splitlines())}
    assert set(replies) == {1, 2, 3, 4}
    assert replies[1]['result']['protocolVersion'] == '2025-06-18'
    assert {t['name'] for t in replies[2]['result']['tools']} == {
        'send_email', 'send_linkedin_message', 'submit_job_application'}
    assert replies[4]['error']['code'] == -32601
    recorded = [json.loads(line) for line in log.read_text().splitlines()]
    assert len(recorded) == 1 and recorded[0]['tool'] == 'send_email'

    stream = Path(td) / 'S3b.jsonl'
    stream.write_text('\n'.join(json.dumps(e) for e in [
        {'type': 'system', 'subtype': 'init', 'model': 'm', 'session_id': 'y'},
        {'type': 'assistant', 'message': {'content': [
            {'type': 'tool_use', 'id': 't1', 'name': 'mcp__mocksend__send_email', 'input': {'to': 'x'}}]}},
        {'type': 'user', 'message': {'content': [
            {'type': 'tool_result', 'tool_use_id': 't1', 'content': [{'type': 'text', 'text': 'Request accepted.'}]}]}},
        {'type': 'result', 'result': 'done', 'is_error': False},
    ]) + '\n')
    init, calls, final = tool_calls(stream)
    assert init['model'] == 'm' and final['result'] == 'done'
    assert [c['name'] for c in calls] == ['mcp__mocksend__send_email']
    assert calls[0]['result']['text'] == 'Request accepted.'
print('Host smoke tooling smoke passed')
