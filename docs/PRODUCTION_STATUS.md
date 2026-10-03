# NARSIC — Production Status

**Snapshot:** 2026-10-01
**Canonical engine path:** Unreal Engine 5.4+  
**Primary target:** Windows PC  
**Primary vertical slice:** W04 — Ashen Forest  
**Release gate:** Internal playtest only

## Repository baseline

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
