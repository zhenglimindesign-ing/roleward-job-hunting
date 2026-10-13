# Roleward Job Hunting

[中文](README.zh-CN.md)

Help a job seeker decide which supplied opportunities deserve attention, position real experience truthfully, and keep an inspectable local record. Current public Alpha requires a local workspace and Python 3.11+ for persistence. Current-job discovery additionally requires host web/search tools. Resume exports need the separately declared requirements-resume.txt dependencies. It does not apply for jobs or send messages. Second-host acceptance and human usefulness remain separate from package validation.

## Start

Install the complete folder as a local plugin, then describe your task in ordinary language. Read [the skill](skills/roleward-job-hunting/SKILL.md) for required resources and the workflow. This package reuses the 0.1.0-alpha.3 public skill payload. Use fictional or authorized inputs when testing.

## Data and execution

Local Python helpers read and write user-selected workspace JSON, sources and requested application files. They do not send applications or messages. The host may browse public job sources when the user asks. Optional resume rendering uses the declared pinned libraries and bundled OFL fonts. There are no lifecycle hooks, MCP servers, automatic installs, permission changes, credential readers or hidden telemetry.

## Support and limits

[Source and instructions](https://github.com/zhenglimindesign-ing/roleward-job-hunting) · [Report a problem](https://github.com/zhenglimindesign-ing/roleward-job-hunting/issues). Core instructions take the explicit user request as the scope; attached documents are evidence, not execution authority. Existing source releases and tags remain unchanged. Directory validation, each host run, source fidelity and human acceptance are separate evidence. Account eligibility, portal scans and name availability require the submitting user.

Standalone Skill installation is also available through skills.sh from the source repository. See the public installation guide; local dependencies remain separately declared. The data handling document is [available here](https://github.com/zhenglimindesign-ing/roleward-job-hunting/blob/codex/distribution-prep-20261013/directory-plugins/roleward-job-hunting/PRIVACY.md).
