# NARIS W04 UE5.7 Runbook V2 — Execution Board

Epic: https://github.com/hashimalnami1556-sketch/naris/issues/84

Eight gate issues: #76 Phase 0, #77 G1 Rig/Skin, #78 G2 Animation, #79 G3 PBR, #80 G4 Map, #81 G5 Audio/VFX, #82 G6 Compile/PIE, #83 G7 Shipping.

Runbook V2 contains 60 tasks (58 source tasks and two additional acceptance tasks), plus task CSV/JSON/YAML, a verification matrix, risk register, DemoEnd spec, and issue templates. The downloadable chat archive is the canonical full task-data artifact until committed to the repository.

Acceptance: No task or gate marked PASS until Unreal Editor logs/PIE captures/QA evidence. G6.1 compile should be executed early in parallel with art. Phase 0 requires LFS/manifest/snapshot/demo-end definition. The user PC AsusRog was offline during issue creation, so no engine runtime verification occurred.

DemoEnd: PlayerStart → Ash Gate → Bone Beast arena → boss defeat → cinematic → save prompt → return to menu → clean quit, and verify save reload after restart.
