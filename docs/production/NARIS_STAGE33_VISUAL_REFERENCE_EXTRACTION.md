# Stage 33 — Complete visual reference extraction register

Source: ten user-supplied CALL OF NARIS concept sheets, including Ashen Wastes, Ashen Forest, ten world biomes, Time Gates and Zayum.

Offline extraction verified:
- 10 original source images retained in downloadable delivery archive.
- 114 annotated panel crops and 549 rectangular sub-panel cells, total 663 PNG crops.
- 238 named asset/system requirements across 15 categories.
- CSV/JSON records contain source filename, pixel bounding box, category, crop path, and **game_ready_3d=false**.

Categories: characters; creatures/bosses; weapons; worlds; architecture; nature; props/interactables; materials; animation; VFX; UI; gameplay systems; time gates; Zayum.

Canonical asset targets: Ashen Vessel, Marsh Seer, Castle Warden, Translucent Hero, Celestial Wolf, Bone Hound, Aether Serpent, Ash Giant, Mist Guardian, Veil Mother, Gate Guardian, Naris Dragon, Zayum Chimera. World W01–W10 plus Ashen Wastes and Time Gates. Environment modular walls, stairs, ramps, bridges, gates, columns, torch kits, chests, vegetation, ground tile variants and PBR maps.

**Delivery:** `NARIS_STAGE33_ALL_REFERENCE_EXTRACTION.zip` supplied in the conversation. Binary concept imagery is not committed to GitHub to avoid repository bloat and because image licenses/provenance and LFS storage need confirmation.

**Honest limitations:** Panels and cell crops are 2D concept references, not segmented meshes, not Blender source, not glTF, not UE maps, not 4K textures or verified animation rigs. No guarantee every tiny illustrated object is individually isolated. The user must not be told this makes a game-ready asset library. AsusRog desktop was offline and Unreal was not run.

**Production acceptance gate:** source mesh and rig, texture and UV, collisions, LODs, animation/AI/interaction implementation, Unreal import, PIE test, map traversal and Windows shipping build must all be verified before asset status changes from `concept_reference` to `game_ready`.
