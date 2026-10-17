# CALL OF NARIS — Production Status

**Snapshot:** 2026-10-01
**Canonical repository engine association:** Unreal Engine 5.7 (`unreal/NARIS_W04/NARIS_W04.uproject`; verified from the checked-in descriptor, not a successful build)  
**Primary target:** Windows PC  
**Primary vertical slice:** W04 — Ashen Forest  
**Release gate:** Internal playtest only

### 2026-10-16 P15 combat-source package correction

The inspected input is `NARIS_P15_DELIVERY_20261016.zip` (combat plugin/import/build tooling), not the similarly named P15 animation archive. Its repaired source is isolated in [source/p15-combat](../source/p15-combat/README.md). It preserves W04 gameplay, avoids the duplicate reflected component name, and adds shared portable combat rules, montage-owned hit-window source, server-side weapon tracing, fail-closed import/preflight and fresh Windows package checks. Local behavioral evidence is recorded in that package's `Reports/`.

These results do not close Unreal gates. No local Unreal installation is available, and AsusRog was reported **offline** on 2026-10-16. UHT/UBT, actual import, animation/collision/PIE networking, packaged Windows gameplay and performance remain unexecuted in this repair. The P15 plugin is not automatically attached to W04 actors or enabled in the canonical project; P16/P17/P18 acceptance is unchanged.

### 2026-10-17 actual GLB intake

The newly available five GLBs were inspected from bytes. The Character1 prototype's Skin was unreferenced by its mesh; its inverse-bind data also failed a conservative rest-pose check once attached. A separate repaired source binds Skin 0 and rebuilds the matrices without replacing vertex, texture, weight or animation bytes. The [P15 source package](../source/p15-combat/README.md) now pins all eight uploaded inputs and the exact five active GLBs, runs the hashed source gate before engine compilation/import, and retains audit/CPU evidence. The malformed-extension USD source is preserved with an extension-corrected USDC copy; no USD semantic verification is claimed.

95 delivery tests and the existing repository suites passed locally. The character still has 18 joints and one idle clip. This is a source repair, not a completed rig/art/animation quality gate or a playable encounter. AsusRog remains offline at the new host check; Unreal and Windows gameplay gates stay open.

## Repository baseline

P15 montage lifecycle continuation (2026-10-17): accepted playback now precedes stamina/defense commitment; interruption cancels combat effects while retaining recovery. Native setup diagnostics and a read-only map-configuration gate now precede packaging. 135 delivery tests passed, including 44 compiled portable C++ cases and 21 mocked map-gate cases. This is source/portable verification only; UHT/UBT, actual Editor map validation, authored motion and gameplay gates remain open while the engine host is offline. See the [P15 integration instructions](../source/p15-combat/README.md).

- Canonical branch: `main`
- Asset registry: `data/MASTER_ASSET_REGISTRY.json`
- Production pipeline: `docs/MASTER_PRODUCTION_PIPELINE.md`
- Repository governance: `docs/REPOSITORY_MAP.md`
- Unreal bootstrap: `unreal/NARIS_W04/NARIS_W04.uproject`
- Master integration: `docs/production/NARIS_MASTER_INTEGRATION_v1_9.md`
- AssetForge world generator: `tools/assetforge/world_generator.py`
- Blender master authoring scaffold: `tools/blender/NARIS_Blender_Master_Builder_v1_0.py`

## Integration status

| Layer | Status | Canonical role |
|---|---|---|
| v1.3 | Integrated as design baseline | Visual identity, branding, color system |
| v1.4 | Contracted into Unreal path | Combat, energy, abilities, poise |
| v1.5 | Contracted into Unreal path | Quests, inventory, dialogue, interaction |
| v1.6 | Contracted into Unreal path | Companion, crafting, map, AI director |
| v1.7 | Contracted into Unreal path | Boss, cinematic, localization, settings, build/QA |
| v1.8 | Consolidated | GameRoot, demo loop, save slots, achievements |
| v1.9 | Active | Master merge, PC packaging, playtest, validation |

Earlier Godot-oriented packages remain useful as design/system provenance, but **Unreal Engine W04 is the canonical implementation target**.

The Blender Master Builder v1.0 is checked-in authoring source, not runtime evidence. Generated prototype geometry, rigs, LODs, collision proxies and manifests must still pass the canonical registry, Blender exchange schema, Unreal import, technical budgets and QA gates before promotion.

## Active production focus — W04 Ashen Forest

### Playable loop

1. Main Menu
2. Intro cinematic
3. Wake Area
4. Movement/combat tutorial
5. Memory Crystal pickup
6. Naris First Whisper dialogue
7. Ash Gate interaction
8. Celestial Wolf encounter/link
9. Bone Beast boss encounter
10. Demo End screen

### Runtime systems required for acceptance

- Third-person player controller
- Enhanced Input
- camera + lock-on
- health / poise / stagger / execution
- five-essence runtime
- weapon hit detection
- companion commands + Echo Link
- quest/inventory/dialogue state
- checkpoint/save/load
- boss phase controller
- UMG HUD
- audio buses
- localization (EN/AR)
- Windows packaging
- automated smoke/validation tests

## World / AssetForge layer

A deterministic world-data generator is now part of the repository.

Current output layers:

- heightmap
- 99-biome catalog and biome grid
- river guide splines
- settlement points
- road guide splines
- streaming chunk metadata

The generator is engine-neutral; Unreal remains authoritative for final Landscape, PCG, splines, World Partition and authored gameplay spaces.

## Art status

The registry still intentionally distinguishes concept/blockout from release-ready assets.

Priority final-art replacements:

- Ashen Vessel final production model
- Celestial Wolf final production model
- Bone Beast final boss model
- Ashen Forest modular kit
- final HUD/UI
- final weapon set
- final Niagara VFX
- production animation set
- music/SFX/voiceover

## Gate policy

`concept`, `brief`, and `blockout` do **not** mean production-ready.

An asset can enter `approved` only after:

1. Visual approval
2. Technical-art validation
3. Engine integration
4. collision/LOD validation
5. performance validation
6. gameplay validation where applicable
7. QA sign-off
8. registry update

## Public demo gate

Public distribution remains disabled until all blocking conditions pass:

- W04 loop playable end-to-end
- no blocking crashes
- input + controller profile stable
- save/load round-trip verified
- boss encounter completable
- EN/AR text pass complete
- Windows package validated
- performance budget accepted
- asset licensing/provenance recorded
- QA release checklist green

## Next production pass

1. Finish Unreal player/companion/boss actor wiring.
2. Import AssetForge W04 world data into PCG/Landscape test tooling.
3. Build one complete W04 level rather than disconnected test scenes.
4. Replace combat placeholders with real montages/hit windows.
5. Complete UMG HUD and menu flow.
6. Add Windows Development/Shipping build automation.
7. Run 10–15 minute internal playtest and log defects.
8. Promote only verified assets/statuses in the master registry.

## Shared knowledge and source repair — 2026-09-23

The shared agent entry point is [AGENTS.md](../AGENTS.md), with current work in [PROJECT_STATE.md](../PROJECT_STATE.md). Duplicate Unreal target definitions and module registration were removed, static guards were added, and AssetForge zero-count behavior was repaired. Repository validation and 10 Python tests pass locally. No Unreal compilation, Claude Code session, editor playtest or Windows package was executed here. See the [updated gap register](PROJECT_GAP_REGISTER.md).

## Brand and namespace policy
- Product/display name: **NARSIC**.
- Technical namespace: **NARIS**.
- Existing IDs/modules/paths remain `NARIS_*` until an explicit migration is approved and validated.
- Dashboard/wallpaper copy is English-only; game localization remains an independent EN/AR runtime feature.

## Live production progress surface
- Data: `data/PRODUCTION_PROGRESS.json`
- UX contract: `docs/production/NARSIC_LIVE_PROGRESS_DASHBOARD.md`
- Renderer: `tools/dashboard/render_progress_dashboard.py`
- Current phase: **Vertical Slice**
- ASUS ROG host at sync time: **online**
- Host connectivity is not build or playtest evidence.


## AAA UI / art / presentation pass — 2026-10-01

The repository now includes a unified image-led modernization target for UI/UX, characters, environments and supporting runtime systems. This pass is canonical design/implementation guidance, not an assertion that final Unreal assets are already production-approved.

Current additions:
- AAA UI/UX screen and interaction contract with Arabic RTL and accessibility requirements.
- Character/environment art bible covering silhouette, materials, LOD, animation, lighting, VFX and audio presentation.
- Runtime modernization targets for combat, AI, save, streaming and performance.
- Unreal implementation map for CommonUI-style screen stacks and gameplay subsystem boundaries.
- Visual acceptance gates and one master visual reference under `generated_designs/ui/`.

Next engine gate: implement these contracts in the W04 Unreal runtime, replace placeholders with production assets, and validate 60 fps, save/load, input, RTL and boss readability before promotion to approved/release.

## Verified workstation evidence — 2026-10-03

Direct inspection of the online **AsusRog** workstation established additional production evidence:

- Unreal project `Game/NARIS_UE57/NARIS.uproject` targets **EngineAssociation 5.7**.
- `/Game/NARIS/Maps/L_AshMap_Assembly` exists as an **8-zone assembly blockout**.
- Environment Pass 01 reports **128 rocks, 10 ruins, 40 spires and 8 art placements** with status `built`.
- Unreal imported assets include the Tripo material payload and `deep_repaired_model`.
- The 2026-10-03 editor log shows modular placement, `NARIS_PLACE_PASS03_OK`, validation of **20 assets**, normal editor shutdown and **0 shaders left to compile**.
- A source-control checkout warning occurred for `L_AshMap_Assembly`, but Unreal subsequently saved the package to `Content/NARIS/Maps/L_AshMap_Assembly.umap`.
- The Unity project currently reports **6000.3.14f1** and contains Menu V2/UI refinement compile artifacts and reports dated 2026-10-03.

This closes the old assumption that no editor execution evidence exists. It does **not** close packaged gameplay, production-map acceptance, performance, or Shipping gates.

## W04 ProductionPass04 — 2026-10-03

Executed directly on **AsusRog** against Unreal Engine 5.7 and `/Game/NARIS/Maps/L_AshMap_Assembly`.

- Added a dedicated `production_pass04.py` production-layout pass.
- Placed **29 modular production actors** across Broken Causeway, Aether Shrine, Ash Gate and the Eclipse Citadel approach.
- The pass reported **0 missing modular assets**.
- The map was saved and `Reports/production-pass04.json` was emitted with status `production_layout_pass`.
- This improves the map from the earlier blockout/modular state, but does not yet close the remaining BasicShapes cleanup, materials, traversal/collision, packaged gameplay or performance gates.

## Engine baseline reconciliation — 2026-10-14

- The checked-in W04 `.uproject` currently declares `EngineAssociation: 5.7`. Earlier `5.4` and `5.4+` references in historical notes are stale baseline descriptions, not instructions to downgrade.
- The workstation's `Game/NARIS_UE57/NARIS.uproject` and repository's `unreal/NARIS_W04/NARIS_W04.uproject` are distinct project paths; their content equivalence has **not** been established. Do not overwrite either without a manifest/diff and backup.
- Documentation and descriptor inspection are **source-level checks only**. UnrealBuildTool compilation, editor map validation, packaged Windows smoke, save/load, boss completion, EN/AR UI and 60 FPS acceptance remain open until independently evidenced.
- Next required evidence: Windows build logs with engine path/version, artifact hashes, W04 map and asset registry audit, packaged smoke results, crash logs and measured frame-time statistics.
