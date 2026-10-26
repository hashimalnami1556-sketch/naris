# NARIS Stage 26 — Ashen Forest map candidate and Windows Shipping execution gate

2026-10-26 | Canonical project: `unreal/NARIS_W04/NARIS_W04.uproject` (EngineAssociation 5.7) | W04 map: `/Game/NARIS/W04/Maps/W04_AshenForest`.

## Concrete offline result
Used the existing Stage02 `NARIS_AshenForest_Stage02_Environment.glb` rather than starting a new empty level. Added a contiguous test navigation strip joining all six zones from the repository's `W04_ProductionMapRequirements.json`: Forest Entrance, Broken Shrine, Ruined Bridge, Whisper Lake, Ash Gate, Bone Beast Arena. Original 331 geometry nodes remain and 23 new geometric nodes were added (six zone platforms, five connectors, 12 arena perimeter markers), resulting in a candidate GLB with 354 nodes. Trimesh reload and bounds check passed; SHA256 was recorded in the downloadable local Stage26 report. These prototype navigation planes are not validated gameplay collision.

## NOT COMPLETED
- Candidate is a GLB and **not** an approved `.umap`.
- No Unreal PIE, NavMesh, packaging, performance, 60 FPS or Windows EXE verification occurred.
- Windows remote host `AsusRog` was offline when checked.
- Do not set `shipping_map_validation.status=pass` or `release_candidate.status=pass` based on the offline structural GLB inspection.

## Handoff, without overwriting production
Stage26 deliverable `NARIS_STAGE26_W04_MAP_CANDIDATE_AND_BUILD_GATE.zip` contains the source GLB, rebuilt candidate, repeatable generator, offline validation JSON, a non-destructive UE5 Python importer to `/Game/NARIS/_Import/Stage26_W04`, and Windows PowerShell build launcher that rejects missing project/map/engine and invokes the existing `tools/windows/Invoke-NarisWindowsReleaseCandidate.ps1` fail-closed release pipeline.

### Production readiness checklist
1. Import in quarantine and verify orientation, meters↔centimeters, UVs, materials, Nanite decisions and collision.
2. Author `W04_AshenForest.umap` preserving the required six zones and the seven mandatory gameplay actor labels and four required lighting/nav classes.
3. PIE traversal and boss combat; strict asset, animation, material and map validators must pass based on real engine reports.
4. Invoke canonical Windows BuildCookRun in Shipping, validate resulting `NARIS_W04.exe`, inspect logs and performance traces.
5. Only then promote the map and build to final/release-ready status.

## Scope
Unreal is production master; Blender source assets remain source of truth; Unity/Godot only prototyping, never combined with the Unreal release build.
