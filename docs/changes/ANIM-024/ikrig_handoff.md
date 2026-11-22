# ANIM-024 — IK source chain handoff (not a runtime approval)

The *actual* source GLBs were checked by SHA256, and their 18-joint bind trees are identical. The source coordinate convention is glTF Y-up, not verified Unreal import coordinates.

## Measured source mapping
| Chain | Start | End | Length (source units) |
|---|---|---|---:|
| Root | root | pelvis | 0.310000002 |
| Spine | pelvis | chest | 0.310000002 |
| Head | neck | head | 0.110000014 |
| LeftArm | upper_arm_L | hand_L | 0.311670118 |
| RightArm | upper_arm_R | hand_R | 0.311670118 |
| LeftLeg | thigh_L | foot_L | 0.265656329 |
| RightLeg | thigh_R | foot_R | 0.265656329 |

Retarget Root is **pelvis**, scene root remains **root**. The source left-side bones have negative source X, right-side positive X; conversion into UE must be inspected, never guessed. There are no toe/ball joints, twist joints, dedicated IK effectors or 87-bone production rig. **This is a prototype 18-joint source-chain map**, not a Manny/Quinn target mapping. The difference between 87 and 18 is 69 joints by count only.

## Source tools (versioned on this branch)
- `tools/assetforge/anim024_ik_chain_contract.py`: parse the two user-provided, SHA-pinned GLBs; reject changed names/parent hierarchy, non-identity bind rotation/scale and broken chains.
- `tools/assetforge/anim024_unreal_ikrig_review.py`: run **DRY RUN** by default. An explicit approved run inside Unreal Engine **5.7** requires `--apply` plus `NARIS_ANIM024_APPROVE_REVIEW=1`. Reads actual imported SkeletalMesh bones and parents through `SkeletonModifier`; refuses existing review asset, mismatched mesh, wrong engine or changed source chains. Will *only* create a NEW review asset at `/Game/NARIS/Generated/Review/ANIM024/IK_NARIS_18J_REVIEW`, once passed, not modify the production hero. No Retargeter/Foot IK Solvers automatically invented.
- `tests/anim024/test_anim024_ik_chain_contract.py`: source-only CI, with real source GLB test explicitly skipped unless `ANIM024_BODY_GLTF` and `ANIM024_PREVIEW_GLTF` are supplied.

The 23-file external `NARIS_ANIM024_IKRIG_18J_PREP_QA.zip` includes an expanded local harness, real source GLB inputs, 37 locally green tests, a 1920px factual bind-skeleton diagram, full JSON source plan, read-only dry-run and Arabic instructions. SHA256: `16922b5200f5b43d7afc8ce44473c4b5b48ef436b0c54e00166274760a79d963` (ZIP CRC PASS).

## Required quality gates — ALL UNEXECUTED inside UE
1. Import the actual corrected hero as a NEW SkeletalMesh without replacing existing assets, with unit/axis/material/skeleton inspection.
2. Enable Python Editor Script/IKRig and required SkeletonModifier modules, use read-only preflight; **do not** run production modifications in bulk.
3. Create Source IK Rig review only after imported mesh signatures pass. Visually inspect pelvis root and 7 retarget chains at rest.
4. Verify actual target IK Rig/SkeletalMesh; then and only then create IK Retargeter and bone mapping. Do not assume Manny/Quinn names or target import.
5. Source/verify *production-authorized* locomotion/combat motion, runtime Montages and hit-window Notifies, Foot IK and animation physics.
6. Run Build Development + BuildCookRun + Project.* + PIE 2-client network, before/after/diff 1920×1080 and FPS/RAM + rollback proof.

No .uasset or EXE created, no real engine run, no Windows device used, no performance metrics measured. This change remains a **draft** and must not be merged into main.

Reference Epic UE 5.7 Python APIs:
- https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/IKRigController?application_version=5.7
- https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/SkeletonModifier?application_version=5.7

**Rollback:** discard external review and revert the isolated ANIM-024 commits, leaving all source art and existing Unreal assets untouched.
