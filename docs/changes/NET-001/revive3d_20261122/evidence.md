# NET-001 — Revive hardening evidence 2026-11-22

Local branch: feature/NET-001-revive-height; baseline HEAD db60d6b
Project: C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57

Implemented actual source changes in 2 files: server-only alive check, true 3D DistSquared, LOS visibility trace, zero-health target reject, 0.25s attempt throttle, 2s success cooldown.
Preserved 260cm revive range and 40 percent health recovery. No arbitrary minimum revive distance.
Added four new C++ Automation tests for downed reviver, dead target, wall obstruction and cooldown.

Static contract RED before fix: 5 failed / 1 passed.
Static contract GREEN after fix: 6 passed / 0 failed. This is source inspection, not compiled C++ proof.
Unreal Engine compilation, new C++ tests, two-client replication, packaged BuildCookRun and after HUD visual evidence: NOT RUN.
Prior 17/17 Unreal tests from 2026-11-21 predate this code change and do NOT validate the new change.
Current C: free space at last check approx 13.58 GiB, below mandatory 30 GiB safety gate.

Patch: NET001_hardening_20261122_MINIMAL_VERIFIED.patch; three-file backup: C:\dev\NARIS_NET001_SAFETY_20261122

SHA-256 before / after:
- Source/NARIS/Multiplayer/NarisCoopCharacter.h: 0ed7d9b8d848b7f98353ef7709a676731aae4f3fb6808f7df975566594087d25 -> 9f5205c5695330ccc064f32b1a4df734548a8553e82af7def2699ae8453bcd9b
- Source/NARIS/Multiplayer/NarisCoopCharacter.cpp: 382f5749df1d361ad48a70c16c192422107e603af2b733c8a04192727f0fcc86 -> fa55b840ae197ce743fab5d0f1a803841c646a46c662065bc0d3c121475f16b6
- Source/NARIS/Tests/NarisCoopTests.cpp: a60d52ffcb38ee2f140f11478fd7331bf916ccd6c29d26d35b6e3b34862ac435 -> bfadc732d4c0845423303739ebfee608276ba858ac165381f3ec9f2723b40709

Rollback: restore only the backed up three original files to corresponding project paths, then rebuild and rerun tests.
Git staging/commit/PR/merge: NOT DONE. Many source/content files are preexisting untracked; no broad staging or ignore changes permitted.
Closing NET-001 still requires 2 rendered clients + server, revival/LOS/cooldown gameplay tests, build/cook, before/after and performance evidence.

Portable patch verification: git apply --check exit 0, then applied on pristine safety copies; source content matched all 3 files after normalizing CRLF/LF. Prior patches NET001_hardening_20261122.patch and NET001_hardening_20261122_CRLF.patch are superseded and should NOT be used.

[executed on device: AsusRog (81c43ddb-199e-4bc1-9944-e3faf018908f)]

## CI truthfulness

This review branch contains a standalone patch and evidence; it does not contain a verified complete Unreal project source tree. C++ compilation and UE Automation require the local UE5.7 project and a clean project integration check. No automatic merge is permitted.
