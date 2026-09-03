# Host Tool and Capability Boundary

## Portable core owns

- workflow/routing policy
- authority/provenance rules
- search and Pursuit method
- score semantics
- Positioning/Human Review
- Track/Learn rules
- validation and anti-overclaim behavior

## Host capabilities provide

- current web search/fetch
- canonical job/source retrieval
- company/sponsorship/contact research
- file ingestion
- local file/code execution
- optional connectors/apps
- optional scheduling

The Skill must not assume privileged LinkedIn access or a Roleward production backend.

## Graceful degradation

Without current web access:

- analyze a user-provided JD;
- do not claim fresh discovery, live-link verification, sponsorship verification, or current people research.

Without persistence:

- complete the bounded current task;
- state that cross-session continuity is not being saved.

Without scheduler support:

- expose manual Scan only;
- preserve the same Scan workflow so future scheduled triggers do not require a workflow rewrite.
