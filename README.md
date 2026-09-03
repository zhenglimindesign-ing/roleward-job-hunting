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
- Future scheduled triggers reuse the same Scan workflow
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
python3 scripts/smoke_scan.py
python3 scripts/smoke_application.py
python3 scripts/smoke_learn.py
python3 scripts/smoke_eval.py
python3 scripts/eval_runner.py
```

## Current build status

Phase 6 Alpha Build is in progress.

Implemented so far:

- Agent Skill entrypoint and focused policy references;
- local structured persistence and authority/provenance rules;
- Structured Context Review and First Scan readiness;
- direct-Opportunity identity, immutable source snapshots, score arithmetic, and Pursuit assessment persistence;
- trigger-agnostic `manual | scheduled` Scan-run contract;
- deterministic confirmed hard-constraint checks;
- Opportunity reservoir/discovery persistence;
- user Pursuit decision stored separately from system recommendation;
- Positioning revision + Human Review gate + artifact provenance;
- application/outcome history and conservative Learn signal lifecycle;
- executable deterministic eval fixtures and monotonicity/dimension-separation checks.

Host-driven broad Precision Scan judgment, the frozen real/private benchmark, baseline comparison, and real dogfood remain in progress.

## Privacy

Do not commit CVs, AI-context exports, job-search history, application artifacts, or local state. The default `.gitignore` excludes those paths.

## License

TBD. No open-source license is implied until one is explicitly added.
