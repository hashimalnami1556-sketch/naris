# ENV-020 — AsusRog engine execution gate

Date: 2026-11-14. Scope: W04 validation checkout only. Existing production project is not overwritten.

## Observed access
Shellway list_devices and hostname execution: no computer connected to the account used by this conversation.
Remote Desktop Commander: linked account authorization rejected.
Remote Arc: no paired computer. HopToDesk: no devices.
No Windows path or running engine process was read from AsusRog in this session.

## Repository evidence
- Existing fix c325e86691657b9c355edd84e05dddce96ccd1c5 records UE5.7.4 MakePanel Padding shadowing; verified source uses InPadding in declaration and definition. That commit predates this session's edits; no compiler transcript was available to this session.
- Existing ENV-020 source regression suite strengthened (0e4da8dc958bfd31b1ce84d89add44a890c3282b); duplicate temporary UI-018 test removed (dc796dfce65d667fb6885626a6f61e66e95d6316). NARIS Unreal Validate 43535048757 SUCCESS, 54 UI016–UI019 and ENV-020 cases total.
- Dedicated Windows workflow added at cf79d20ba4d03c6f2e39897e925f3831e5a49ed1. Push run 43535171786 is QUEUED, no runner/job started at last query. Host check requires COMPUTERNAME AsusRog; exact candidate SHA; UE 5.7; clean isolated runner checkout. Uses existing guarded W04 Development compile/bootstrap helper. If runner session 0, build only; interactive launch otherwise. A DEV smoke map is not the production map. Process may close when runner exits. No asset replacement or main merge.
- UI016 standalone workflow failed before job creation because its echo command was written as a YAML plain scalar containing colon-space. Fix 0af8c751f95fe3a23d0dc6e23cc440d2adaf0a67 uses a block scalar. UI016 run 43535256743 SUCCESS and NARIS Unreal Validate run 43535256778 SUCCESS.

## Required gate still open
Real Windows Development build, game startup, UE import, real cape/weapon/IK/Cloth QA, screenshots before/after/diff, Project.* automation, server + two clients, FPS/RAM/VRAM, BuildCookRun and packaged EXE: not verified. Do not merge or claim release approval.
A queued GitHub run is not proof that AsusRog is reachable. Runner must be registered to this repo, online, and execute the host-verified job. Shellway may be rechecked once paired to the same connected account.

## Rollback
Revert workflow and test-only changes; no production assets changed. Dedicated runner checkout can be retained for diagnostics. Existing PR #108 remains draft.
