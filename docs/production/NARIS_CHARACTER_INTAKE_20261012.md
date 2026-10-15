# W04 character intake — 2026-10-12

This is a **staged source/art intake**, not an Unreal Engine build result.

Six newly supplied models were structurally inspected and given **reserved W04 IDs** in `data/manifests/NARIS_CHARACTER_INTAKE_20261012.json`. Source binary files are in the owner's delivered intake ZIP, not in the public repository (rights unverified).

## Actual generated artifacts

- Dragon: original GLB contains **954,415 triangles and 530,403 vertices**, no skeletal skin. A new GLB prototype was produced with **22 joints**, four skin influences per vertex, and three glTF animation clips (Idle, WingBeat, Roar). Bind-pose/deformation artist QA, optimization and Unreal import remain pending.
- Older Character1 rig prototype: authored skin and weights existed but the mesh node had no `skin:0` binding. A repaired GLB was generated separately.
- USDZ: five source archives validated as USDA/USDC-compatible payload containers. Their conversion, automatic humanoid rigging, FBX export and animation smoke testing require a Blender workstation.
- Source inspection: six of six structural audits passed; eight Python unit tests passed in the intake workspace. No Unreal PIE, packaged smoke or FPS evidence was produced in this session.

## Delivery and execution

Owner receives `NARIS_Character_Intake_20261012.zip` containing complete sources, new rigged dragon GLB, repaired old prototype, audit/manifests, tests, Blender USDZ batch importer/rig/export script, Unreal 5.7 Python skeletal importer and an isolated QA-map builder. Import path **must be** `/Game/NARIS/W04/Maps/W04_CharacterIntake_QA`; production level remains unchanged.

Execute `tools/run_naris_character_intake.ps1` from the downloaded ZIP, passing actual Blender binary, `UnrealEditor-Cmd.exe`, and `unreal/NARIS_W04/NARIS_W04.uproject` paths. The runner first checks source hashes and calls Blender; Unreal Editor import is run only on request.

## Merge / promotion gates

1. Confirm commercial rights and visual originality before any public binary upload.
2. Run Blender import and review geometry, skeletal weights and Idle/Walk/WingBeat/Roar in viewport.
3. Produce reduced topology / LODs, PhysicsAsset, collisions, sockets and validated animation retargeting.
4. Import into UE 5.7 isolated W04 QA map and complete animation + combat + AI integration tests.
5. Profile at target settings; run Cook, Package and game smoke tests.
6. Only then consider production map placement and an approved entry in `data/MASTER_ASSET_REGISTRY.json`.

**Blocker:** Desktop Commander reported AsusRog offline at time of execution. No edits to the actual engine install or packaged game are claimed.

See the supplied intake ZIP for code and complete source-hash records.
