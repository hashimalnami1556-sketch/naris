# NARIS shared agent guide

This guide is shared by Codex and Claude Code. Start at the repository root.

## Startup and source ownership
1. Read [current state](PROJECT_STATE.md).
2. Read [source ownership](docs/production/knowledge-sources.md).
3. Read the active work record linked from current state, then only the relevant canonical files.
4. Before editing, refresh the checkout and reread claimed files. Record the executing agent and scope in the work record. Claims are advisory; serialize overlapping edits and never overwrite another agent's changes.

## Project rules
- Keep Unreal/W04 and Windows PC as the current implementation path. Browser slices are prototypes, not proof of Unreal readiness.
- Follow [repository governance](docs/REPOSITORY_MAP.md) and [production gates](docs/PRODUCTION_STATUS.md).
- A specification, generated reference, static check, engine build and playtest are different evidence. Never promote one into another.
- Preserve asset IDs and provenance. Do not fabricate missing images, engine assets, test results or approvals.
- Keep canonical notes in English; retain Arabic localization and communicate with the owner in Arabic.
- Keep secrets and unrelated personal material out of this public repository.
- Use existing canonical documents; link to numeric registries instead of duplicating their values.

## Workflows
Resolve installed skills through each host's discovery, without copying plugin files or cache paths.
- KB setup: `sparkore-core:kb-bootstrap`.
- Durable knowledge edits: `sparkore-core:knowledge-steward`.
- KB hygiene: `sparkore-core:kb-maintenance`.
- Design versus implementation checks: `sparkore-core:runtime-audit`.
- Browser prototype work: Game Studio, only when that prototype is in scope.
- BioNeMo is a biomolecular research toolkit; no current NARIS task requires its scientific pipelines.

## Validation and handoff
Run `python tools/ci/validate_naris.py` and `python -m unittest discover -s tools/assetforge -v` for relevant changes. Unreal compilation and playtesting require an actual Unreal installation; report them separately.

Persist completed work, evidence, blockers, changed files and the next action before handoff. Keep production readiness in its canonical status document. Move completed work records to `docs/production/work/archive/`; retain open follow-up work in the active record. Local clients must pull the latest commit before continuing. Shared Git history is not automatic live synchronization.
