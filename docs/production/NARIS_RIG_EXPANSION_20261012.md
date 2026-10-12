# NARIS W04 — Rigged Creature/Character Expansion (2026-10-12)

## Evidence and authoritative source
This work extends the 2026-10-12 six-model intake and targets Unreal Engine **5.7**, while respecting the canonical NARIS/W04 production-map and asset-registry approval gates. An owner-deliverable bundle `NARIS_RIG_EXPANSION_20261012.zip` contains the actual GLB binaries, Blender/UE Python tools, SHA256s, Windows PowerShell launcher, logs and rig source. **The binaries are not in GitHub**, because source/provenance and redistribution rights have not been verified for public hosting.

### Material artifacts built and validated OUTSIDE Unreal
- **6 GLB skeletal variants actually generated**: Dragon Ash/Ember (22 bones / 10 embedded animations each); Humanoid Wanderer/Sentinel (18 bones / 9 animations); Beast Marsh/Cinder (18 bones / 7 animations).
- **4 static environment GLBs actually generated** from City 1 and Environmental 1, with two material variants each. Static architecture intentionally remains unrigged.
- Offline validation: **21 Python tests passed**, validating all-weight normalization, joint references, clip timing/unit quaternions, actual motion keys, static-world variants, USDZ SHA256s, and inverses of bind matrices.
- Important repair: inherited humanoid prototype had malformed inverse bind matrices with translation in the wrong matrix row; fixed glTF column-major serialization and detached the skinned mesh from armature root; rest-pose joint binding error reduced from **1.53** to **<0.0001** (matrix norm).
- Dragon still has **954,415 triangles**, so no geometry optimization success is claimed. Blender source generates a *separate* ~110k-triangle LOD1 review FBX when run on a compatible workstation; manual deformation and silhouette QA required.
- Five USDZ humanoids remain **unconverted** until Blender runs. One additional historically supplied `.usdz` proved to be a *bare* USD crate and was preserved as `.usdc` for manual classification.
- UX and gameplay wiring, physics/AI, level navmesh, 60 FPS benchmark, UE PIE/cook/package, and shipping checks are **not executed**.

## Three-zone Unreal editor QA staging
Included script `unreal/naris_ue57_character_world_qa.py` (in the owner bundle) imports Blender FBXs only to:
`/Game/NARIS/W04/CharacterWorldQA`.
It authors the **isolated, non-shipping** level:
`/Game/NARIS/W04/Maps/W04_CharacterWorld_QA_20261012`
with three graybox test areas (Ash Gate / Bell Marsh / Twilight Citadel), review proxies, PlayerStart, area lights and candidate characters/props. This is source for editor-side execution, not an existing `.umap`. The shipping W04 Ashen Forest map is not changed.

## Integration into the real game: required gates
1. Extract the owner bundle to the checked-out worktree or a sibling source directory.
2. Execute `run_windows_ue57.ps1` from the bundle with actual Blender, UnrealEditor, and W04 project paths, optionally `-StageUnreal`.
3. Review `processed-v2/batch_report_v2.json`, `processed-glb/conversion_report.json`, and `reports/ue57_qa_runtime.json`. Failure is never silently treated as approval.
4. Manually review mesh skinning and IK/footslide, autorig correctness, physical collisions, weapon sockets, animation frames/notify windows, mesh LODs and visual originality.
5. Connect imported AnimationSequences to production AnimationBluePrints, AI behaviors, encounters and attack windows, add proper NavigationMesh, test combat and checkpoints in Play In Editor.
6. Perform Windows Development & Shipping build/cook/package, packaged smoke, crash/log QA and 1080p/60 FPS profiling before promotion.

See `data/manifests/NARIS_RIG_EXPANSION_20261012.json` for SHA256 and explicit per-asset status. **Do not silently edit** `data/MASTER_ASSET_REGISTRY.json` status to approved or merge to `main` without engine and rights evidence.
