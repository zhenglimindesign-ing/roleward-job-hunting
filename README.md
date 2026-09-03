# Roleward Job Hunting

Portable Agent Skill for precision-first job hunting.

> Alpha implementation. Canonical internal product/eval decisions live in the private Roleward repository; this public repository is the distributable implementation surface.

## Product loop

**Understand Me → Precision Scan → Pursuit → Position → Human Review → Application Pack → Track → Learn**

Roleward is designed to reduce wasted job-search effort: fewer opportunities, better decisions, truthful positioning, and conservative learning from real outcomes.

## Alpha target

- Primary internal host: Codex
- Persistence: local structured files
- Current discovery: host web/search capabilities
- Manual Precision Scan is sufficient for Alpha acceptance
- Future scheduled triggers must reuse the same Scan workflow
- No Roleward production backend dependency
- No automatic application or professional-message sending

## Package layout

- `SKILL.md` — portable entrypoint
- `references/` — focused workflow policies
- `scripts/` — deterministic state/eval helpers
- `schemas/` — local Alpha state schema
- `fixtures/` — public synthetic/de-identified eval fixtures
- `state/` — ignored private runtime state
- `sources/` — ignored private source material
- `application-files/` — ignored generated private artifacts

## Bootstrap checks

```bash
python3 scripts/validate_skill.py
python3 scripts/smoke_context.py
python3 scripts/smoke_opportunity.py
python3 scripts/eval_runner.py
python3 scripts/state_store.py --path state/roleward-state.json validate
```

## Current build status

Phase 6 Alpha Build is in progress. The initial foundation plus deterministic context/state and direct-opportunity/Pursuit vertical-slice helpers are implemented locally and are being published here before broader Precision Scan, Positioning/Application, and Track/Learn work.

## Privacy

Do not commit CVs, AI-context exports, job-search history, application artifacts, or local state. The default `.gitignore` excludes those paths.

## License

TBD. No open-source license is implied until one is explicitly added.
