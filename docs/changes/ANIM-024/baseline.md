# ANIM-024 — Source animation coverage baseline
Date: 2026-11-18. Parent branch: feature/CHAR-023-rigid-weapon-review. Scope: source-only, no UE changes.

## Actual original file audit
Four user-provided GLB assets inspected by parsing glTF JSON chunks:
- CHAR-022 skin-fixed hero, SHA256 a9389d433d31886c1d4273e6acda0950ca6657fac20338063b9bb643ca95fdd9: 1 skin, 1 clip `A_Character1_Idle`, 1 rotation channel targeting `chest`. Walk, Run, Attack, Dodge, Block, Death absent.
- `Character1_NARIS_Rigged_Prototype.glb`: 1 skin, 1 clip `A_Character1_Idle`, 1 rotation channel targeting `chest`.
- `Character 1.glb`: no skin and no animation.
- `Character 3.glb`: no skin and no animation.

The audit requires named clips Idle, Walk, Run, Attack, Dodge, Block, Death. Name presence alone is a **minimum content check, not proof** of skeletal coverage, retargeting, root motion, foot IK or runtime playability. All four sources fail minimum coverage. No animation has been generated or retargeted. Do not silently create placeholder clips or mark ready.

## TDD and evidence
Local RED: ModuleNotFoundError: anim024_audit before implementation. GREEN: 5/5 unit tests including the real user-supplied CHAR-022 GLB, with pinned source. For GitHub CI the real-asset test must skip explicitly if `NARIS_ANIM024_SOURCE` is not set; original GLB remains external, not checked in. Source-only JSON evidence and Python reproducibility script provided in chat handoff.

## Next actual production tasks
1. Verify UE5.7 character Skeleton, bone hierarchy, bind pose, import scale and rotation; compare with target Manny/Quinn if retargeting to UE assets.
2. Acquire/licensed original source locomotion and combat animation clips; validate names, source rigs, licensing and original style. Do not invent gameplay animations.
3. Create IK Rig source/target and IK Retargeter in UE; map pelvis, spine, arms, legs and head; validate retarget root and foot contacts.
4. Author animation blueprint / locomotion BlendSpace and Montages with root-motion policy, Foot IK, combat cancel windows and replicated gameplay.
5. Run UE actual before/after 1920x1080, BuildCookRun, automation Project.*, server+2 clients, FPS and memory; no merge until green.

## Gate status
- Offline file inventory and missing-clip detection: PASS.
- UE import/retarget/animation preview/PIE: NOT_RUN.
- Combat/replication/build/performance: NOT_RUN.
- Release and merge: BLOCKED.

Rollback: revert documentation and audit utility; original GLB and UE project remain untouched.

## 2026-11-18 continuation — additive DEV-only motion test pack
A pinned derived *swordless* CHAR-023 hero source was inspected, SHA256 `2fc95a46ba69f23c4365390bea277f185bc83e187286140d56d22aa080e0780d`. It has the original 18-joint skeleton, original skin and `A_Character1_Idle` unchanged. Added `tools/assetforge/anim024_dev_motion.py` producing a **separate, non-shipping** GLB with 7 deterministic technical demonstration clips (`Walk, Run, LightAttack, Dodge, Block, Jump, Death`) in addition to the original Idle. Source graphics, textures, nodes, skin, Idle metadata and the original binary payload prefix remain byte-for-byte identical. Output GLB SHA256 `b5dc669cb81b81f93f3b7c2131446437823d0d5ae1cc5a4be85d47d2eb1a0015`.

Every new clip is marked `extras.naris_dev_only=true` and `extras.production_approved=false`. Locomotion is in-place. There are **no** root-motion gameplay commands, authored combat notifies, actual foot IK, finished combat movements, network simulation, Unreal asset imports or runtime screenshots. The 4-second MP4 and seven-row Before/After PNG are CPU skinning previews of the *actual derived GLB*, not AI renders or Unreal screenshots.

The source-foot-joint coordinate ranges during the generated cycles were **0.2905 source units for Walk and 0.4193 for Run** for each side. These are motion extents, **not confirmed sliding**; contact phase, slope adaptation, and gameplay speed matching remain untested. Treat these curves only as technical placeholders with potential unacceptable aesthetics and foot slide.

### TDD, regression and CI
- Local RED: missing `anim024_dev_motion`, then GREEN **13/13** on original-asset-derived GLB and procedures. New RED test detected a dangerous coverage false-positive: old `anim024_audit.py` counted clips named `DEV_ONLY_Walk` as production. GitHub RED run [44393657820](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44393657820) reproduced the failure.
- Fixed coverage: any `DEV_ONLY_` prefix or `extras.naris_dev_only=true` or `extras.production_approved=false` is excluded from production-readiness counts. Local final **14/14** tests PASS. GitHub CI includes **19 tests, with 1 user-GLB integration test skipped** (original binary not in repository), [green run 44394276179](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44394276179).
- Independent `trimesh` loader parsed the new GLB, containing 8 named clips. New source renderer `render_anim024.py` provides real CPU before/after and a 4-second software MP4; original art appearance is the input, not replaced.
- External complete handoff ZIP: `NARIS_ANIM024_DEV_MOTION_PREVIEW_AND_QA.zip`, 6,937,536 bytes, SHA256 `5d23b8004fa797d6a2f891c460c2e1fc8f7f5b5e763e1d3b4ce633391a9d687b`, 15 files, CRC PASS. Includes the user original derivative GLB, new generated GLB, Python tools/tests, original-vs-DEV artwork storyboard, 4-second MP4, SHA256 manifest and Arabic README. Binary assets and media remain outside the GitHub repo to avoid LFS/rights and CI issues.

### Explicit non-approval and rollback
No licensed production motion has been sourced. Do **not** use these procedural preview clips as the shipping Walk/Run/Attack/Dodge/Block/Jump/Death, do **not** assign their success to `main`, and do not assume glTF glb directly imports into UE5.7 as a working Animation Sequence without actual editor test. Real animation sourcing, retargeting, BlendSpace, Montages, Notifies, foot placement, anti-sliding checks, network gameplay, 1920x1080 before/after/diff, build/cook and performance gates remain **NOT RUN**. Keep PR #110 draft. Rollback: discard the derived review GLB and source-only tooling; original UE assets unchanged.
