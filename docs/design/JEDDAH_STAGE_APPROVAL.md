# JEDDAH — مدينة جدة | Stage Design Adoption

**Change ID:** LEVEL-001  
**Owner decision:** APPROVED FOR INCLUSION — 2026-11-21  
**Target:** CALL OF NARIS, Unreal Engine 5.7, multiplayer 3D  
**Production state:** DESIGN_APPROVED / RUNTIME_UNVERIFIED  
**Issue:** https://github.com/hashimalnami1556-sketch/naris/issues/112

## Binding decision
The *previously designed Jeddah map* is approved as **one standalone game stage**, without replacement, deletion or repurposing of any canonical existing level. This is acceptance of the prior map concept, **not** approval of an invented redesign or a claim that it has been imported or packaged.

## Provenance and interpretation
- Prior conversation references an `L_Jeddah_Cesium_Prototype` (~303 actors reported historically) mixing Ash content and Cesium; that historical description does **not** verify a finished, independent Jeddah city level.
- Repository searches returned no indexed source matches for `Jeddah` or `L_Jeddah_Cesium_Prototype` on `main` at the adoption date.
- `City 1.glb` and `Environmental 1.glb` are general candidate assets, **not evidence** that their geometry faithfully models Jeddah.
- Original map references, geometry, districts, landmark selection, exact layout and any licensing require source verification before art production. No neighborhoods, major buildings or landmarks are assumed here.

## Stage contract (planned; not implemented)
- Display name: **JEDDAH — مدينة جدة**; English `Jeddah`; Arabic `جدة`.
- World-map classification: standalone urban stage / playable location.
- Story sequence index: pending reconciliation with the canonical World Map and previous Jeddah design; no forced replacement of Ash Gate, Ashen Forest, Bell Marsh or Twilight Citadel.
- Unreal content namespace *proposed*, subject to repository registry review: `/Game/NARIS/Levels/Jeddah/` and `L_Jeddah_City`. This is **a target naming proposal**, not a file path proven to exist.
- Preserve recognizable elements and proportions **only when traceable to the actual prior design/source**. Artistic lighting/post-process must remain consistent with NARIS's approved fantasy visual language; city geometry fidelity and game art direction are separate dimensions.
- Stage access: validated inter-level transition/return and checkpoint persistence, once implemented. Multi-client join/leave/respawn tests are required before gameplay promotion.

## Implementation order and gates
1. Locate original Jeddah concept/model/package and compare against the historical reference; inventory every source asset and rights/license.
2. Record original bounds, real world-to-Unreal transform, coordinate frames, scale and source timestamps; use centimeters inside Unreal (1 UE unit = 1 cm).
3. Author standalone blockout; preserve existing canonical stages, separate development-only prototype and production map.
4. Import assets via approved Unreal pipeline. Evaluate World Partition and HLOD for large regions and Nanite/LODs based on measured geometry/performance; none are automatic sign-offs.
5. Author material instances, PBR resources, collisions, NavMesh, player starts, landmarks confirmed by source, and required stage travel interactions.
6. Verify persistence/migrations if save schema changes; EN/AR text + RTL, A11y, server+2 clients for network/gameplay changes.
7. Under `LEVEL-001` or implementation follow-up ID capture before_gameplay/ui/debug/perf and after_* with identical Seed/resolution/quality; produce montage diff and motion GIF when required.
8. Run Development build, BuildCookRun, Project.* automation, packaged smoke, console log and target-device -benchmark -fpschart; log ΔFPS, ΔMem, ΔSize and rollback.
9. Only after gates pass promote the new map into the game's level registry and release sequence via a separate PR.

## Production budgets (targets; not current measurements)
- Desktop average FPS ≥60 (minimum 45); frame time ≤16.6 ms target.
- Minimum-spec FPS ≥30 (minimum 25); RAM ≤6 GB target, VRAM ≤4 GB target.
- Net tick target 30 Hz, 8 concurrent clients target. Reassess city streaming and active client cost with profiling.

## Exclusions and nonclaims
- This acceptance does not assert that `L_Jeddah_Cesium_Prototype.umap`, Cesium datasets, streamed tiles, photos, or an original-city 3D mesh are accessible.
- No building/POI/road/cultural content is added without the prior approved reference.
- No edits to existing maps, main runtime startup map, map registry, saving, shipping configuration or level selection are included here.
- No before/after shots, Unreal tests, build result, performance or multiplayer verification are claimed in this documentation-only change.

## Acceptance checklist
- [x] Owner approved independent stage concept
- [x] Preservation/no-replacement rule documented
- [ ] Original city map source acquired and verified
- [ ] Licensed source assets inventoried
- [ ] Scene authored and saved as a production `.umap`
- [ ] Gameplay + travel + network validated
- [ ] Before/after/diff/GIF evidence and performance report
- [ ] Windows Development and Shipping gates passed

**Related baseline:** [LEVEL-001 baseline](../changes/LEVEL-001/baseline.md).  
**Epic documentation:** https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition-in-unreal-engine
