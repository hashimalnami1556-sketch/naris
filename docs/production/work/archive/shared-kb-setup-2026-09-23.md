# Shared KB setup and source repair

Date: 2026-09-23. Status: completed for repository setup and bounded source repairs.
Human decision owner: project owner. Executing agent: Codex (Work Mode; client version unavailable).
Starting commit: 1fe4988. Request: set up shared Codex/Claude knowledge, improve existing work and update the repository.

## Adoption
Existing docs/data/Unreal taxonomy retained. Root AGENTS.md is shared policy; CLAUDE.md imports it. PROJECT_STATE.md routes to current objective, sources, ownership and next action. Existing source owners were read before writes; no empty-directory bootstrap helper was used on the populated repository.

## Repairs
Removed duplicate nested TargetRules definitions and the second NARIS_W04 module registration; retained the root targets and primary game module. Added structural checks and CI regression tests. Fixed zero-count river/settlement generation and rejected nonpositive octave settings. Reconciled the outdated gap register with files actually present. No engine assets were manufactured.

## Validation boundaries
Bootstrap structure: adopted layout, helper check not applicable.
Mechanical lint, regression tests and repository validation: see validation results below.
Semantic route: root guide → state → source owners → active work gives current objective, human owner, next step and workflow without chat history.
Durable update: setup repairs recorded here and current work handed off to the active W04 record.
Codex: files read and updated in this session. Automatic cold-start discovery was not separately tested.
Claude Code: adapter reviewed; actual session and plugin discovery not available, therefore untested.
Cross-agent continuation: file route prepared, no second host execution claimed.
Unreal build/playtest: not run; no suitable engine host available.
Attachments: all announced scratch attachment files were absent. No visual assessment or import claimed.
BioNeMo: available workflows cover biomolecular computation; no relevant game-runtime task identified, no jobs launched.

## Changed artifact groups
Root agent/state/profile files; source routing and work/decision indexes; production gap/status/worldgen docs; Unreal duplicate bootstrap files; Python integrity checker and tests; AssetForge generator and tests; GitHub validation workflows.

## Next action
Follow the active W04 readiness record after pulling the updated repository. Do not infer release readiness from this setup.

## Validation results

- AssetForge: 6 tests passed.
- Unreal static guard: 4 tests passed, including injected duplicate/empty/missing bootstrap failures.
- Repository validator: passed; 33 JSON files parsed and Unreal bootstrap structure checked.
- Sparkore KB lint: 126 Markdown files scanned with the repository profile; no errors or warnings after routing cleanup. One active work record matched; zero decision records is intentional and is not a decision audit. Remote URLs and semantic correctness are outside mechanical lint coverage.
- Diff whitespace validation: passed.
- Host execution boundaries remain as stated above.
