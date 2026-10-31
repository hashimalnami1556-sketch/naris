# G0-001 — Source skeleton baseline (2026-10-31)

**Gate: BLOCKED / NOT PRODUCTION APPROVED.** Inspected available original GLB JSON chunks, not an Unreal runtime session.

| File | Skins | Joints | Animations | Classification |
|---|---:|---:|---:|---|
| Character1_NARIS_Rigged_Prototype.glb | 1 | 18 | 1 | PROTOTYPE ONLY |
| Character 1.glb | 0 | 0 | 0 | Static mesh, rig absent |
| Character 3.glb | 0 | 0 | 0 | Static mesh, rig absent |
| Environmental 1.glb | 0 | 0 | 0 | Environment static mesh |
| City 1.glb | 0 | 0 | 0 | Environment static mesh |

Prototype joints: `root, pelvis, spine, chest, neck, head, upper_arm_L, lower_arm_L, hand_L, upper_arm_R, lower_arm_R, hand_R, thigh_L, calf_L, foot_L, thigh_R, calf_R, foot_R`.

The **92-joint Ash Wanderer design is a specification**, not a verified production skin. Neither of the two other character GLBs contains a skeleton. No source/target production Skeleton pair is yet available to check chain mapping or retarget poses.

**Environment baseline:** HEAD/build, seed, resolution, quality, frame time, FPS and memory have not been recorded from the editor. UE5 before/after captures, BuildCookRun, Automation Tests, network test and benchmarks are **not run**. AsusRog device is offline.

**Next required work:** inspect actual source and target Skeleton paths and bone hierarchy; bind 92-joint rig non-destructively to the original Ash Wanderer mesh, weight paint, set up source/target IK Rigs and IK Retargeter, check walk/run and deformation; collect screenshots and full quality-gate evidence before marking G0 complete.

**Risk:** prototype mislabeled as ready; incorrect retarget mapping; overwriting original art.
**Rollback:** restore added documents; preserve original GLB/FBX/USDZ untouched and tracked by Git LFS.

**Supporting local artifact:** `NARIS_DESIGN_PILLARS_G0_001.zip` contains a machine-readable GLB audit JSON and CSV.
