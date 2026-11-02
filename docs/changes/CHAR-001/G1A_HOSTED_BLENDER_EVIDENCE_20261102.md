# CHAR-001 / G1-A — hosted Blender execution evidence (2026-11-02)

## Actual Blender operation
Executed an **actual Blender 5.2** scene edit in a new **3D Jutsu** workspace:

- Project: https://higgsfield.ai/3d-jutsu/45d935b6-ad56-4ff9-9285-109424b9bfa5
- Revision: **1**
- Operation: `char001-build-11-bone-armature-g1a-v1`, status **succeeded**
- Editable `.blend` committed by Blender runtime, file size **895,064 bytes**, ETag `52e9627a4fc215ae656879315fbdd401`
- Blender-created Armature object: `SK_AshWanderer_Advanced`
- Exactly **11 bones**; **10 deform**, **1 non-deform** (`root`)
- `pelvis` directly under root, disconnected; `jaw` under head, disconnected; other spine/neck chain connected.
- Minimum bone length ~**0.05024945m**; object scale `(1,1,1)`.
- View-only rod and label proxy meshes are in `CHAR001_99_VIEW_ONLY_NOT_EXPORT`; **they are NOT a skinned Ash Wanderer mesh**.
- Two Blender renders (reference skeleton only): operation `render-g1a-front-right-01`, `G1A_FRONT_REFERENCE.png` (1024×900) and `G1A_RIGHT_REFERENCE.png` (1024×900).
- Structural result returned `STRUCTURAL_ARMATURE_PASS_ANATOMY_PENDING`.

**Evidence boundary:** the hosted scene-builder version imports only catalog assets, **NOT the user-supplied `naris_3d_ash_wanderer.glb`**. The authoring scene therefore does **not** contain the approved Ash Wanderer Mesh. Do not treat these rendered views as anatomical alignment evidence or the Blender import/skin pass for the user Mesh.

## Local source continuation
The `Ash_Wanderer_CHAR001_G1A_Execution_v4.zip` supplied in the conversation includes the verified original GLB, a non-destructive Blender 4.x builder, numerical QA and a one-click Windows launcher. Its **9/9 offline unit tests** passed when rerun on 2026-11-02. This local builder has **not** yet been executed inside the user's Blender.

## Gate results
| Gate item | Outcome |
|---|---|
| Actual hosted Blender Armature created | **PASS** |
| 11 bones / 10 deform / root non-deform | **PASS** |
| Parents / Connected flags / identity / minimum length | **PASS (Blender structural query)** |
| Source GLB provenance and 0 skins | **PASS (offline source audit)** |
| Blender source Mesh included in hosted scene | **FAIL / unsupported by connector** |
| Source-specific pelvis / spine / chest / neck / TMJ fit | **PENDING** |
| Front/Right with *actual source Mesh* and Bone Axes | **PENDING** |
| Full 87-bone runtime Skeleton | **NOT STARTED** |
| Unreal UE5.7 import/PIE | **NOT RUN** |
| G1-A overall | **BLOCKED — SOURCE_MESH_FIT_AND_VISUAL_QA** |

## Next authorized action
Open local original source in Blender 4.x via the v4 Windows launcher; create `02_Rig/SK_AshWanderer_Advanced_G1A.blend`, align central joints and Bone Roll with the actual Mesh, produce Front/Right/Outliner captures and pass local structural report. Only then open G1-B.

The 87/83/5 budget is the owner-approved prospective target; the original incompatible 92-bone recovered JSON remains provenance-only. G1-G, G2, G3, G4 and G5 remain untouched.

## Rollback
The hosted Blender scene is isolated from Unreal and the user's computer. GitHub change is documentation-only in `feature/CHAR-001-G1A`, can be reverted without deleting or modifying existing production assets.

## Downloadable workstation handoff v5
The ChatGPT conversation contains `Ash_Wanderer_CHAR001_G1A_Execution_v5.zip` (13,611,194 bytes), SHA-256 `1bce96b6a374711ebc1606ebaf8eb4ddf303a35baf354b6175e8b852a71d7b19`. ZIP integrity PASS, offline unit tests 9/9 PASS. Contains the unchanged source GLB and one-click Windows Blender builder, plus a persistent `.url` shortcut to the actual hosted Blender armature; **hosted `.blend` bytes are not embedded in this ZIP**. Source-specific visual validation remains pending.
