# Stage29 actual review and G1 handoff — 2026-10-27

## Reviewed inputs

Recovered `NARIS_STAGE29_MAP_MATERIAL_ANIMATION_BINDING.zip` (SHA-256 `ec72538b7d19b4422653deac61b2cd9a660d02447e254df06bc17537b96a4f3a`). Its original installer is not in the repository; the guarded replacement is `unreal/NARIS_W04/Content/Python/naris_stage29_place.py`. The received manifest is retained unchanged as `Content/NARIS/W04/Production/Stage29/placements_received.json`.

The package README describes position-only compression to **20% plus centering**. This is not the proposed 0.256 factor. All 136 received scales are `[1,1,1]`; received rotations are retained. The Stage27 original formula/translation has not been independently reconstructed from its source manifest. Do not claim that a world-bounds violation alone proves the cause of invisibility: World Partition source/grid ranges, Data Layers, loaded levels, actor visibility, draw distance, mesh bounds and occlusion need actual engine investigation.

## Source findings

| Check | Received manifest | New review candidate |
|---|---|---|
| Unique placement IDs | 136 | 136, preserved |
| X origin range | -65897.4 to 65762.4 cm | Within canonical centered world and declared zones |
| Y origin range | -5169.4 to 6153.8 cm | Within canonical centered world and declared zones |
| Global XY bounds violations | 0 | 0 |
| Outside assigned canonical zone rectangle | 136 | 0 |
| Manifest Z | All 0 | Preserved as trace seed; actual ground still required |
| Scale | All 1 | Preserved |
| Unreal placement/PIE/collision | Not executed here | Not executed here |

The canonical [LEVEL_LAYOUT](../../../NARIS_MASTER/09_WORLD/Ashen_Forest/LEVEL_LAYOUT.json) is **1600 x 1200 m**, with negative and positive coordinates. Bounds are centered: X +/-80000 cm and Y +/-60000 cm. Substituting `0 <= x,y <= 1600` would reject legitimate negative coordinates, mix meters with centimeters and invent a square map.

The new `placements_corrected.json` is a review-only **zone-cluster translation**, not a second global compression: for each zone, compute the received XY centroid and translate the cluster to the canonical zone center. Local offsets and pairwise distances within each cluster, IDs, source names, rotations, scales and Z are unchanged. `zone_translation_cm` and the received manifest SHA record the operation. Reproduce with `python tools/assets/remap_stage29_zones.py`. This repairs zone assignment; it does not establish encounter design, clearance or collision acceptance.

## Original installer review

| Area | Finding | Replacement behavior |
|---|---|---|
| Existing map protection | PASS: refuses overwrite | Keeps all previous maps; unique per-run map |
| Preflight | FAIL: creates blank map before resolving assets | Validates manifest, all unique keys, materials, collision roles and template before authoring |
| Asset resolution | FAIL: selects first prefix match | Exact unique name, or explicit path override; ambiguity blocks |
| Missing assets | FAIL: skips actors and reports partial success | Any missing source prevents map creation |
| Scale | FAIL: ignores manifest scale | Applies scale explicitly and measures it |
| Ground/pivot | FAIL: uses Z=0 blindly | All traces collected against copied ground before spawning; rotation/scale first, bounds-bottom alignment after |
| Collision | FAIL: no authored/role check | Solid props require authored collision; character-review actors/banner use documented decoration intent |
| Save/error recovery | FAIL: ignores save result and lacks cleanup | Checks save; cleanup restricted to new run copy; unresolved cleanup quarantined in report |
| PIE/visual proof | OPEN | Always unknown until separately reviewed; no automatic G1 PASS |

A missing material slot is a structural failure. A visually magenta/checkered surface may have other causes; material paths alone do not prove successful shader compilation or visual quality. No production material is edited by this pass. The 80 environment MaterialInstance budget is retained as a proposed review budget, not a measured hardware guarantee.

## Running G1

Pull this commit into the canonical checkout. Use the checked-in UE 5.7 W04 project. Save editor work and stop PIE. In Unreal's Python console:

```python
import runpy, unreal
stage29 = runpy.run_path(unreal.Paths.project_dir() + 'Content/Python/naris_stage29_place.py')
preflight = stage29['execute']()  # default read-only; no level creation or actor spawn
```

Read `Saved/TestReports/stage29_g1_<run_id>.json`. Resolve every missing/ambiguous asset, material and authored collision first. Interchange-renamed assets must have exact paths entered in `placement_policy.json`'s `asset_path_overrides`. No fallback mesh, collision hull, floor or animation is fabricated.

For authoring, supply an **existing ground-bearing template** whose terrain matches the intended design. The canonical blockout may be used only after it has actually been authored/inspected; this pass never assumes its existence:

```python
result = stage29['execute'](apply=True, template='/Game/NARIS/W04/Maps/W04_AshenForest_Blockout')
```

Creates `W04_Stage29_Staging_<run_id>`. It does not modify `W04_AshenForest`, bind ABP/Montages, change Stage33 assets, or promote Shipping. A missing ground hit aborts authoring. Ground tracing uses Visibility with simple collision; inspect that channel and slopes/bridges/multi-layer floors. Bounds-bottom adjustment is a conservative starting point, not a substitute for foot/weapon/art pivot inspection. A trace hitting an unintended roof is still a valid trace, so visual traversal is mandatory.

The report stores measured transforms, bounds/material/collision/ground checks and per-element failures. G1 remains blocked/failed until runtime review covers all 136 IDs for the same run, plus visual material checks, streaming/culling, ground traversal and material budget. Editor actor presence is not on-screen PIE visibility; loading every actor at once is not the acceptance condition for a streaming world. Review relevant actors from the intended encounter route. Retain screenshots/logs with the run ID. The pure `decide_g1` function evaluates evidence completeness; it does not authenticate a human-entered report or replace the engine review.

## Separate follow-up gates

- **G1:** placement/materials/role-appropriate collision/terrain/streaming and PIE route inspection. Current status: **BLOCKED — authorized AsusRog offline; no Unreal execution in this session**.
- **G2:** Hero + one nominated combat target, using actual production skeleton/ABP/montage paths. Veil Mother source is not automatically approved as playable or rig-ready. Record root, skeleton/retarget compatibility, PhysicsAsset, sockets, locomotion and manually triggered montage/notifies. GAS fields are N/A pending an explicit architecture migration; do not fail existing component-based code solely for not implementing a proposed GAS design.
- **G3:** actual combat input -> hit window -> one damage application per swing/target -> reaction/hitstop/presentation/telemetry, then performance and edge cases. Use measured timing against authored sequence rate; freeze specifications before testing. Do not mark G2/G3 passed because source tests pass.
- **Stage30/31:** remain gated on actual G3/Combat Matrix evidence. No roster expansion or Motion Matching migration is executed here.

## GAS proposal corrections

The current repository uses `UNarisCombatComponent` and native montage hit-window/impact notifies. No ASC/AttributeSet/GAS migration is implemented by this change. Replacing that path while G1 is unresolved would conflate content failures with a damage-system rewrite.

If GAS is adopted later: choose **one** IncomingDamage writer. A raw additive SetByCaller modifier plus an ExecCalc that also adds final damage can double-apply damage. Carry raw `Data.Damage` on the Spec and let the ExecCalc produce the single meta-attribute output; consume/reset in PostGameplayEffectExecute. Damage execution must not depend on successful activation of an optional hit-reaction ability. Reactions, hitstop and telemetry consume authoritative results; telemetry must not choose critical hits or authoritative damage. Instant damage effects do not provide persistent granted state tags. Mixed replication mode alone does not establish networking ownership, authority or prediction correctness.

Matching bone names/counts alone does not establish compatibility; additional leaf bones do not categorically invalidate retargeting. A universal 60–80-bone requirement is not a quality gate. Foot IK, Motion Warping, upper-body attacks and Motion Matching are design-dependent, not mandatory for every creature. The supplied motion-search timings and proposed per-character budgets are not measurements on this project's target hardware.

References: [Epic World Partition](https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition-in-unreal-engine?application_version=5.7), [Gameplay Effects](https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-effects-for-the-gameplay-ability-system-in-unreal-engine?application_version=5.7), [UE5.7 StaticMeshEditorSubsystem](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/StaticMeshEditorSubsystem?application_version=5.7).

## Local validation

378 CI/unit checks, 6 AssetForge tests, repository validation and Python syntax compilation pass. Eight focused tests include missing-assets -> zero map mutations, all 136 received zone violations, corrected zone membership, translation invariants, duplicate/invalid numeric rejection, ambiguous mesh rejection and stale/partial G1 evidence rejection. These are source tests using a fake Unreal boundary where appropriate; **not Unreal tests**.

## Unattended Windows entry point — 2026-10-27 follow-up

From a current checkout, the following starts a new unattended UE editor process for **read-only preflight** (save/close other editor sessions first):

```powershell
.\tools\windows\Invoke-NarisStage29G1.ps1
```

Specify `-EngineRoot` for a non-default install. The wrapper validates the installed engine major/minor against the project descriptor; it does not install/compile Unreal or fabricate missing editor binaries. Resolve each preflight error before authoring. To author the new review map against an existing inspected terrain template:

```powershell
.\tools\windows\Invoke-NarisStage29G1.ps1 -Apply -TemplateMap /Game/NARIS/W04/Maps/W04_AshenForest_Blockout
```

Each invocation retains its receipt, copied measured report, SHA-256 checksums and editor log in `Saved/TestReports/Stage29Invocation_<id>/`. The separate source report retains its own run ID. A nonzero editor exit, missing receipt, source failure, mismatched report or fewer than 136 measured/saved placements rejects completion. Prior process environment variables are restored. The Python batch bridge also records failure when the placement entry point raises; existing receipts are refused before execution.

A successful command means **preflight completed** or **review authoring completed**, according to the mode. It never means G1 PASS, PIE visibility or G2/G3 success. `-NullRHI` deliberately provides no visual evidence. Retain this invocation directory for diagnosis, then open the authored review map interactively to perform the runtime review.

Validation for this follow-up: 383 local tests and 6 AssetForge tests pass; Python compilation and repository validation pass. PowerShell is not installed in this local execution host; parser validation is assigned to the existing hosted NARIS CI job which parses all `tools/windows/*.ps1`. No Windows/Unreal invocation of this new wrapper has occurred. The prior commit's hosted [NARIS CI](https://github.com/hashimalnami1556-sketch/naris/actions/runs/40518556336), [Content Validation](https://github.com/hashimalnami1556-sketch/naris/actions/runs/40518556322) and [Unreal Validate](https://github.com/hashimalnami1556-sketch/naris/actions/runs/40518556456) completed successfully; their names do not imply an Unreal runtime test.
