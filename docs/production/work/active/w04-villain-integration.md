---
status: active
last_updated: 2026-10-12
---
# NARIS W04 villain-runtime integration (development only)

Owner decision: integrate the conversation-approved NARIS villain visual direction as playable enemies, without overwriting the established Bone Beast milestone.

Executing agent: ChatGPT / GitHub connector, independent feature branch `feature/w04-naris-villain-runtime-20261012`.

## Actual source changes

- Native `ANarisVillainCharacter` extends `ACharacter`, so movement uses the established `AIModule`/NavigationSystem dependencies and AI controllers.
- The existing `UNarisCombatComponent` makes the new enemies targetable and damageable through the existing hero lock-on and attack routing; death is emitted as a multicast event.
- Seven configurations: AshWretch, BronzeSentinel, BellWraith, DrownedKnight, ChainedGiant, AshGatekeeper, EclipseReaver.
- Patrol / chase / melee windup / one-hit commitment / recovery / stagger / death, optional 50% HP second phase.
- Blueprint animation hooks expose state, attack, damage, second phase, death; production requires real SkeletalMesh + animation montage notifies.
- `W04_VillainEncounterRoster.json` and idempotent Unreal editor authoring script place them in the W04 **Blockout** only. The Bone Beast remains a separate actor and quest encounter.
- Visible cube is deliberately a *development proxy*. It disappears when a skeletal mesh is provided. A generated concept sheet does not qualify as a `.uasset`, `.umap`, skeletal rig or validated GLB.

## Apply on the registered Windows Unreal 5.7 host (when online)

1. Update this branch or check out the PR; preserve any uncommitted local maps/meshes.
2. Build `NARIS_W04Editor` against the installed engine. The checked-in `NARIS_W04.uproject` descriptor currently selects **UE 5.7**. Some older repository status documents still mention UE 5.4; verify the local engine/build rather than relying on stale text.
3. Run `naris_author_w04_production_blockout.py` in Unreal Editor if the blockout map does not exist.
4. Run the villain authoring step (5) to create development **NavMeshBoundsVolume** regions. Then build/inspect navigation (press P to visualize) and fix any zero-brush or unwalkable volumes. Navigation cannot function without valid bounds and surfaces.
5. Run `naris_author_w04_villains.py` from the Unreal Python console; it places the roster, creates labeled development navigation volumes when their brush supports it, and avoids duplicate actor labels. Alternatively use the launcher `tools/windows/Invoke-NarisW04VillainIntegration.ps1 -RepoRoot <repository-path>` to build and author both scripts.
6. PIE: verify enemy patrol, player detection, navmesh chase, attack hit, parry/dodge via hero damage, stagger, death, lock-on and phase changes.
7. Import independently approved Tripo/Blender assets as SkeletalMesh, author skin weights/physics/sockets, animation blueprint, melee montages and impact notifies; disable `bUseTimedSmokeAttackImpact` once reliable impact notifies work. Bind Blueprint implementations for animation and VFX/audio cues.
8. Run engine compile, cook and packaged playtest. Leave Shipping gate closed until technical-art, rights/provenance, rig, montage, navmesh, performance, save/respawn and QA evidence pass.

## Verification

Static test: `python -m unittest tools/ci/test_villain_encounter_contract.py -v`.
This asserts source and manifest contracts only. This pass did **not** build Unreal, playtest Windows, convert images to rigged 3D assets, or commit art binaries. Remote AsusRog host is offline as of this session.

## Open blockers

- Full production-grade original character sculpt/retopology/UVs/skeleton/skin weights.
- Approved mesh and material imports for seven archetypes.
- Animation montage assets and notify-driven impacts; preview timed hits must not be Shipping acceptance evidence.
- Authored/verified navigation bounds, map-save evidence, engine build and PC gameplay QA.
- A visual/provenance review is still needed for the characters' originality and licenses before public release.

Next action: reconnect AsusRog; validate the branch on the installed engine; then promote verified assets and encounters to the canonical registry and production map through existing approval gates.
