## 2026-11-19 — ANIM-024: real repository animation + target-skeleton preflight (draft)
- **Why:** real target SkeletalMesh/IKRig unavailable and W04 animation manifest names alone cannot prove AnimMontages exist. Previous external JSON `is_unreal_editor_capture` flag could imply false live-engine verification.
- **What:** inspected live 907-entry GitHub tree and W04 manifest; 10 expected montage paths, zero checked-in matching `.uasset` files (not proof of absence on the user's PC). No IK Rig or IK Retargeter `.uasset` checked in. `PythonScriptPlugin` explicitly enabled; `IKRig` and `MeshModelingToolset` not explicitly enabled in `.uproject` (not proof they are inactive). Added `anim024_target_preflight.py` read-only actual-editor SkeletonModifier capture/manual 7-chain ancestry gate; `anim024_repo_readiness.py` expected Montage file inventory; preserved original source rig and art untouched.
- **TDD:** RED missing-module test and JSON-editor-claim spoof regression; GREEN GitHub run 44444969246: **66 tests** discovered, **64 pass**, **2 skipped** real-GLB integrations not available in CI. New guard will *never* mark external snapshot data as verified inside UE.
- **Runtime/Perf:** NOT RUN: UE editor, target import, IK Rig/Retargeter, real Montage/Notifies, PIE, build/cook, server + two clients, FPS/memory and engine before/after.
- **Risk/Rollback:** Source 18-joint review mapping is not production 87-bone rig. UE target IDs/axes/scale and actual plugin availability unknown. PR #110 stays draft; revert target preflight utilities/docs to rollback; no game assets modified.

## 2026-11-19 — ANIM-024: actual 18-joint source IK retarget chain plan, editor-only installer (draft)
- **Why:** after the seven non-shipping preview motions, Unreal IK Rig chain selection still lacked an evidenced source skeleton map. Guessing bone names and UE coordinate conversion would risk a broken Retargeter.
- **What:** verified two SHA-pinned original-derived GLBs with identical 18-joint bind trees, mapped seven source Retarget Chains with pelvis as retarget root (Root / Spine / Head / LeftArm / RightArm / LeftLeg / RightLeg), and checked bilateral chain lengths (arm 0.311670118, leg 0.265656329 source units, matching left/right). The 18-joint prototype lacks toe/twist/IK bones; the 87-bone runtime target remains unfulfilled by 69 joints by count.
- **Tools:** added `anim024_ik_chain_contract.py` for strict source-hash/parent validation, `anim024_unreal_ikrig_review.py` for UE5.7 **dry run by default**. Installer has explicit env opt-in, exact imported skeleton check, no-overwrite review path, and does not auto-author target rigs/retargeters/solvers. Extended handoff includes real-source diagram/JSON and a portable harness.
- **Tests/Evidence:** local extended handoff **37/37** tests (real GLBs and mocked Unreal API) passed, external 23-file ZIP SHA256 `16922b5200f5b43d7afc8ce44473c4b5b48ef436b0c54e00166274760a79d963`, CRC PASS. GitHub source CI last verified 38 discovered, 2 real-GLB integrations skipped. See `docs/changes/ANIM-024/ik_source_review.json`, `ikrig_handoff.md`.
- **Perf/Runtime:** NONE — no live Unreal Editor, .uasset, imported target mesh, IK Retargeter, gameplay network or FPS evidence. Before/after visual is a CPU bind-skeleton diagram, NOT UE gameplay screenshot.
- **Risks/Rollback:** source-space Y-up is not confirmed UE space, no production-approved motion or 87-bone final rig. Keep PR #110 draft; discard separate review outputs or revert branch without changing source art or project main.

## 2026-11-18 — ANIM-024: additive non-shipping seven-clip source preview + fail-closed coverage
- **Why:** original 18-joint hero GLB has only a chest-rotation Idle, while gameplay APIs require locomotion, combat, dodge and death. Existing filename-only coverage could falsely count DEV_ONLY clips as production.
- **What:** preserve the CHAR-023 swordless skinned source (SHA256 2fc95a46ba69f23c4365390bea277f185bc83e187286140d56d22aa080e0780d) and original Idle; add seven explicitly DEV_ONLY glTF curves in a separate GLB (Walk, Run, LightAttack, Dodge, Block, Jump, Death). All original geometry/skin/nodes/materials/texture bytes untouched. Output SHA256 b5dc669cb81b81f93f3b7c2131446437823d0d5ae1cc5a4be85d47d2eb1a0015. Added source-real CPU before/after and four-second MP4 preview; no Unreal screenshots.
- **Tests:** local source-based 14/14 green; independent trimesh load works; GitHub RED 44393657820 caught false-positive DEV coverage and source fix at 37243e5cd6aa60c7e6a42e779065d081f6d2395d; GREEN run 44394276179. CI source tests 19 with one real-user GLB integration explicitly skipped.
- **Performance:** not measured. Foot joint coordinate range during generated in-place cycles 0.2905/0.4193 source units for Walk/Run; these are not measured ground slide. Source animation used exclusively for technical prototyping, not shipping.
- **Risk/Rollback:** no authored high-quality animation, retargeter, attack notifies, Foot IK, runtime montage, network, PIE, cook, engine screenshots. Keep draft PR #110, do not merge and do not spawn sword twice. Rollback discards preview GLB and tool/doc commits without touching original project assets.

## 2026-11-18 — ANIM-024: source animation coverage audit (draft)
- **Why:** source GLB files lack the required locomotion/combat clips; retargeting without verified source motion would produce misleading readiness claims.
- **What:** inspect four original GLB files by SHA256, verify clip/channel/node names, and add fail-closed named-clip coverage audit. The corrected hero and rigged prototype have one chest-only Idle clip each; Character 1/3 have no skins or animations. Missing Walk/Run/Attack/Dodge/Block/Death.
- **Tests:** local RED missing module -> 5/5 GREEN including actual user hero GLB; GitHub source tests PASS, real user GLB integration skipped on CI (not committed). See docs/changes/ANIM-024/coverage_report.json.
- **Perf:** not measured; no UE engine, content or gameplay modification.
- **Risk/Rollback:** named clips are minimum only; UE IK Rig, Retargeter, BlendSpace, Montages, Foot IK, gameplay, network, build and before/after gates remain open. Revert audit branch, leave source untouched. Draft PR #110.

## 2026-11-18 — CHAR-023 continuation: source Idle skin deformation and virtual hand socket (review only)
- **Why:** the original weapon has strong leg weights. A 0.223 source-unit distance from hand_L bone to grip is not itself proof of misalignment; the correct question is how the weapon follows hand pose.
- **What:** additive source-pinned CPU glTF skin evaluation against rigid hand-relative attachment across the only actual Idle clip (chest rotation at 0, 0.75, 1.5 seconds), and separate synthetic wrist turns (0/90/180/270/360 degrees). Source GLB, independent original-texture weapon/body review assets and game code unchanged.
- **Evidence:** 2,940 edges of candidate sword geometry. At Idle 0.75 seconds, original max individual-edge strain 30.17809% (mean 0.74642%, p95 3.39897%) vs virtual rigid max 2.81e-12 percent; predicted sword pose difference mean 0.00997170, max 0.0160604 **source units**. This is geometry/math, not an Unreal screenshot or production animation.
- **Tests:** GitHub RED 44388350504 proved missing module; GREEN 44388945249 22/22 synthetic tests, 2 actual-GLB classes skipped because binary absent from CI. Locally 12 synthetic + 4 user-GLB integration tests passed. Independent handoff ZIP SHA256 8f6b6f4f172186458620a2e783f408e7ea6a3c9a8ff7ce095040bbe40d248205; CRC PASS.
- **Risks/Rollback:** suspected weapon segmentation near hand/cloak, source to Unreal axis/units unverified, no actual socket, attack/walk/run montage, gameplay/network, build, FPS or collision test. Keep draft PR and revert only additional review artifacts as needed. Original files untouched.

## 2026-11-18 — CHAR-023: preserve original weapon visuals, add detached rigid review candidate
- **Why:** actual source blade vertices inherit ~31.34% thigh_L, 24.16% calf_L, 20.52% foot_L but only ~1.13% hand_L skin weight on average; this is not a stable independent hand-mounted weapon.
- **What:** pinned-SHA GLB review tool partitions original 49,886 triangles into hero 48,052 / guard 592 / blade 1,242, then exports independent rigid sword with original normal/UV/PBR JPEGs, and derived original-skin hero with candidate sword faces excluded. Source GLB, rest geometry, skins, original Idle and three embedded texture byte hashes preserved. In static rest pose CPU, actual exported hero+sword GLBs reassemble with max source vertex deviation 7.45e-9 and 0 differing raster pixels in two views.
- **Tests:** TDD red missing module then 10/10 synthetic tests green; 9/9 real GLB integration tests green locally, three output GLBs load in trimesh. GitHub tests only source/synthetic; actual user GLB remains in external handoff ZIP.
- **Risks:** guard segmentation review required; proposed grip has 0.223 source-unit gap from hand_L origin. No UE Socket/animation/net/build/cloth/perf certification. Never spawn original skinned sword and detached candidate simultaneously.
- **Rollback:** discard independent review files or revert draft PR, leave original art untouched. Details: docs/changes/CHAR-023/{baseline.md,qa_report.json}.

## 2026-11-15 — CHAR-022: mesh-derived attachment review
- Why: shoulder-radius trial found zero pins. Use actual shared body/cape boundary vertex IDs and torso skin weights rather than moving bones or expanding a radius blindly.
- What: additive geodesic Max Distance review profile; 105 candidate review vertices / 100 unique original indices, one eligible component (8,425 vertices / 16,554 faces); unanchored lower component (1,634 vertices / 2,960 faces) remains on original skinning, no render geometry deleted. Original GLB and prior review hashes unchanged.
- Evidence: 10/10 local synthetic tests; active index-topology zero defects in measured categories; original mapping and OBJ roundtrip verified; max face corner error 8.57e-10 source units. Original Idle keys evaluated on CPU only. External 16-file ZIP contains OBJ, CSV, mappings, full reproducible runner and comparison; not a production asset.
- Risk / rollback: chest height 0.67, torso weight cutoff 0.5, geodesic fade 0.20 and max movement 0.12 source units are review assumptions. Candidate attachment gate passes, actual garment coverage, seam dynamics, Chaos Cloth, collisions, UE build/network/perf untested. Do not import CSV blindly or merge. Discard separate output to revert.

## 2026-11-14 — CHAR-022: simulation-only manifold repair and attachment audit
- **Why:** previous cape review had 20 nonmanifold edges, 65 branching boundary vertices and 1 winding conflict.
- **What:** add manifold_review.py, exact face/vertex lineage; remove 55 faces incident to nonmanifold edges, split disconnected vertex fans, propagate winding, prune 79 faces in small isolated components. Review-only OBJ: 19,648 -> 19,514 faces, 2 large components retained; all three index-topology defect counts now zero. Original GLB, approved appearance, textures, skin and animations untouched.
- **Next gate executed:** actual 18-joint source shoulder locations; provisional pin radius 0.04 source units yields 0 pinned vertices across both components. Pin gate FAIL; nearest distances 0.2415064 / 0.1494546. Four provisional rest-pose thigh/calf capsule checks: 0 candidate vertices inside, minimum clearance 0.00712628 source units. No actual triangle/dynamic cloth collision proof.
- **Tests/evidence:** 12 local synthetic tests passed; pinned real asset mapping and OBJ roundtrip passed; max coordinate deviation 5e-10 source units. Dedicated CI extended. External ZIP and comparison not committed as shipping binary.
- **Risk / rollback:** topology-only success is not cloth approval. Seam duplicates may share positions; do not re-weld, fill holes or assign weights blindly. 100-face cutoff and pin/capsule dimensions are assistant-selected review settings. Keep PR draft; discard review OBJ to revert; UE import/build/network/perf not executed.

## 2026-11-14 — CHAR-022: additive cloth topology review and test coverage
- **Why:** actual cape candidate has 20 welded vertex-connected components, 22 duplicate faces, 33 nonmanifold edges and 70 branching boundary vertices.
- **What:** separate review-only OBJ, source-to-candidate face/vertex mapping, deterministic quantized welding and duplicate/small-island removal; 19,731 -> 19,648 triangles, 20 -> 2 components, duplicates 22 -> 0, nonmanifold 33 -> 20. No original GLB, texture, skin, design or animation changed.
- **Evidence:** 8/8 synthetic tests locally green; actual pinned GLB, mapping and OBJ roundtrip independently checked. Dedicated GitHub workflow added. Output and rear-projection comparison in external handoff, not shipping assets.
- **Risk / decision:** 100-face island cutoff and 1e-6 source-unit weld grid chosen for review only, not art approval. 20 nonmanifold edges, 65 branching boundary vertices and 1 orientation conflict remain. No Cloth, pin weights, collision, UE import or performance approval. Windows runner 43535171786 queued at check; no engine proof. Rollback: discard review mesh; preserve original render source. PR #108 remains draft.

## 2026-11-14 — ENV-020: Windows execution recovery
- Confirmed Shellway has no paired host in current account; alternate remote connectors unavailable. Existing UE5.7.4 source fixes inspected; strengthened ENV-020 regression contract.
- Added host-verified isolated AsusRog W04 Development build/launch workflow; real GitHub run 43535171786 queued. No engine execution or game launch proven.
- Fixed UI016 YAML block-scalar syntax; independent UI016 and NARIS Unreal Validate runs 43535256743 and 43535256778 both passed. Production project and art untouched. Keep PR #108 draft.

## 2026-11-14 — CHAR-022: conservative cape candidate section
- **Why:** the repaired hero is one welded connected component, not separate cape/body/weapon objects.
- **What:** partition existing triangles into two review primitives, using posterior burgundy texture and vertex coordinates. 19,731 cape-candidate triangles + 30,155 remaining triangles = 49,886. All 32,373 original vertex attributes, original material, texture, 18-joint skin and Idle unchanged. 872 shared boundary vertex indices.
- **Evidence:** 8/8 local regression tests PASS; output ZIP CRC PASS. Actual mesh preview and exact face IDs distributed in external handoff. No change to appearance intended; candidate mask is not production cloth.
- **Risks / rollback:** possible seam/upper-arm misclassification, incomplete collar and dark fabric. Do not assign cloth until reviewed. Return to original SkinFixed GLB. No UE import, cloth collision, FPS, BuildCookRun or network tested; PR #108 stays draft.

## 2026-11-13 — CHAR-022: repair original prototype skin binding
- **Why:** original 18-joint GLB had skin weights and an animation, but no mesh-to-skin assignment and incorrect inverse-bind matrix storage.
- **What:** separate corrected GLB assigns skin 0, corrects all 18 bind matrices, removes inherited mesh offset; all original geometry, weights, texture bytes and animation data preserved.
- **Evidence:** 10/10 local tests pass, maximum bind identity residual 0.9100000262 -> 1.1175870895e-8; original Idle keyframe CPU deformation 0 -> 0.0246787155m max. 21,911 vertices move >0.1mm. Offline preview only; no UE screenshot.
- **Performance:** FPS/RAM/VRAM not measured. Actual Unreal import, cape collision, sockets, Retarget, IK, network, build/cook and packaged runtime NOT RUN. No production rig claim.
- **Rollback:** retain byte-identical original GLB, revert source branch; no map or existing engine asset overwritten.

## 2026-11-09 — UI-019: avoid cloning save arrays each open-menu frame
- **Why:** Native UMG refresh was invoking by-value `Runtime->GetState()` every tick, copying save-state inventory/quest/waystone collections.
- **What:** Add C++-only `const FNarisSaveState& GetStateView() const`, consume synchronously from UMG as `const FNarisSaveState&`; keep the BlueprintPure by-value snapshot API exactly unchanged.
- **Evidence:** RED workflow 42566278277 proved two failing source tests before fix; GREEN 42566353585 ran 51/51 combined UI016–UI019 source tests successfully.
- **Performance:** one per-refresh snapshot copy removed in code; **no FPS, frame-time or memory measurements** because Unreal host remains unpaired.
- **Release risk and rollback:** Do not retain reference after call or across state mutation. Revert header plus menu callsite if needed. Draft PR #106; main unchanged, engine Build/Cook/PIE/network/A11y gates still pending.

## 2026-11-09 — UI-018: correct native UMG Inventory page compile blocker
- **Why:** `NarisSystemMenuWidget.cpp` used `bInventoryPage` twice but never declared it; prior source-only tests missed this C++ compile error.
- **What:** Minimal one-scope `const bool bInventoryPage = Controller->GetPauseMenuPage() == ENarisPauseMenuPage::Inventory;` declaration in `RefreshInterface`. No changes to original art, SVG, network, gameplay save schema or map.
- **Evidence:** GitHub Actions RED (2/4 new checks failed, run 42565855915) before fix; GREEN (47/47 targeted UI016+UI017+UI018 checks PASS, run 42565926629) after fix. Actual UE5.7 compiler, PIE, 2-client network, BuildCookRun, perf and before/after/diff remain **NOT RUN**.
- **Rollback:** Revert one local variable declaration. Feature PR #105 remains draft, no main merge.

## 2026-11-08 — UI-017: six live HUD icons and viewport collision correction
- **Why:** six previously approved original SVG icons were not wired into the live combat Canvas HUD; after adding icons, 800×600 and 1024×768 boss encounters exposed an overlapping quest card.
- **What:** Actual `ANarisHUD` C++ draws six source-derived textures from existing stable icon paths and live combat state. The objective card now fits horizontal safe margins and moves below an *active* boss bar on narrow viewports; the owner-approved 1920×1080 placement remains unchanged.
- **Evidence:** GitHub red: responsive contract failed 3 cases before the collision fix. Green: NARIS Unreal Validate with UI017 contract suite PASS (26/26); `docs/changes/UI-017/responsive_geometry_matrix.csv` contains 16 viewport/boss states, 4 computed overlaps before and 0 after.
- **Performance:** FPS Δ: not measured; RAM Δ: not measured; package size Δ: not measured. No Unreal host authorized.
- **Test/merge status:** C++ editor compile, PIE, screenshot before/after/diff, 2-client networking, BuildCookRun, RTL/A11y and actual Windows EXE NOT RUN; **feature PR #104 remains draft; do not merge**.
- **Rollback:** Revert UI017 feature source and layout commits; retain original source SVG, approved screenshots, maps and save data.

## 2026-11-08 — UI-017: six original SVG icons in active W04 combat HUD
- **Why:** UI-016 connected six Texture2D icons to native menus but actual `ANarisHUD` gameplay meters and objective had no icon bindings.
- **What:** one-time six-icon loading from stable source-approved paths; actual health, resonance, energy, action hints and quest UI show original PNG alpha derived from SVG; maintain real component values and input mapping; optional missing texture leaves original text/values. New read-only editor asset audit rejects 256px dimension/class/missing-asset errors.
- **Evidence:** reproduced missing implementation in CI RED, then source HUD patch and 19 new UI017 contracts + 17 UI016 regression tests (36 total); NARIS Unreal Validate PASS in GitHub.
- **Release blocker:** no UE5.7 Editor compilation, PIE/UMG visual screenshot, 2-client network, before/after/diff, performance or Windows BuildCookRun. No main merge.
- **Rollback:** revert isolated UI-017 commit only; do not modify original user art or project maps.
- **Tracking:** `docs/changes/UI-017/baseline.md`; PR #104.

# NARIS development changelog (source changes; not shipping releases)

## 2026-11-08 — UI-016: six original SVG → native UMG image bindings
- **Why:** WORLD-015 imported six PNG textures only as unused assets; the clickable native UMG menu still displayed text-symbol placeholders.
- **What:** Added real `UImage` icons to menu buttons, stable six-Texture2D resolver, selectable tint and text fallback; original mouse/gamepad handlers and Arabic/English labels remain. Added pinned source-image hash importer, protected PowerShell run command, and icon directory cook configuration.
- **Evidence:** 17/17 UI-016 GitHub static/import security tests PASS, 15 approved SVG/PNG/image hash checks PASS in independently extractable binary kit, tamper test PASS.
- **Not verified:** UE5.7 C++ compile, .uasset import, PIE visual/RTL, screenshots, actual FPS/VRAM, network and Windows BuildCookRun. **Draft only; no main merge.**
- **Rollback:** Revert UI-016 feature changes, review and remove only stage-specific imported icon assets after checking dependencies. Preserve original art and maps.
- **Links:** Pull request #103; `docs/changes/UI-016/baseline.md`; `docs/changes/UI-016/qa_report.json`.

