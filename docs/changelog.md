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

