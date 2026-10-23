# NARIS P21 Scene Contract (2026-10-23)

Status: **29/29 local Python tests PASS; Unreal runtime UNVERIFIED**.

## Scope
- Read-only GLB scene-graph validation of four P18 Ash Gate greybox layers.
- Check node-to-mesh, child and scene references; reject missing scenes and primitives.
- Combined gate validates SHA-256 and declared player/boss spawn locations.
- Updated staging script in the separately delivered P21 ZIP uses a fresh /Game/NARIS/Maps/LV_AshGate_P21 level, rejects existing asset destination, and adds boss/checkpoint reference markers.
- GLB layer mesh counts: Ground 25; Architecture 36; Foliage 219; Props 77.
- Local ZIP artifact: NARIS_P21_Scene_Contract_20261023.zip.

## Remaining release blockers
Unreal Editor 5.7 actual import and PIE, navmesh, collision, scale, rigging, animations, materials/LOD, FPS and packaged Windows executable. This is not a production approval.

## Repository note
The production baseline remains canonical W04 Ashen Forest; the P21 Ash Gate greybox is experimental. Binary GLB files are in the separately delivered archive, not committed to GitHub. The repository tool below expects P20 stage_gate.py and four GLBs with stage_layout.json in an extracted package.
