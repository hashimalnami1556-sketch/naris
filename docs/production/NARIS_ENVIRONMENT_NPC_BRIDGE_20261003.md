# NARIS W04 — Environment-to-NPC Runtime Integration

## Engine routing
Primary shipping path is **Unreal Engine W04** under `unreal/NARIS_W04`. The supplied `WaterSystem.cs`, `WeatherEnvironmentIntegrator.cs`, `MountainGenerator.cs`, and quest generation scripts are **Unity prototypes**, not Unreal-compatible source. They are not copied into `Source/NARIS_W04`.

## Implemented this pass
`ANarisDailyNPC` can be placed or subclassed as a Blueprint character:
- daily schedule entries with [start,end) game-hour windows, including overnight intervals;
- optional navigation destination actors per activity;
- timer updates every 2 seconds by default, no actor Tick;
- shelter override during storms using an explicit weather bridge call;
- Blueprint event `OnActivityChanged` for animation and audio presentation;
- single quest offering integrated with existing `UNarisRuntimeSubsystem`; no repeated quests and no automatic completion.

## Example in Ashen Forest
NPC ID `WaystoneKeeper_01`
- 06:00–09:00 Work → `BP_MorningCampMarker`
- 09:00–18:00 Trade → `BP_WaystoneMarketMarker`
- 18:00–22:00 Patrol → `BP_GateMarker`
- 22:00–06:00 Rest → `BP_KeeperShelterMarker`
- Weather override: `SetStormActive(true)` uses `StormShelter`.
- QuestToOffer: `Quest.W04.CorruptedHeart` (if not active or completed).

The time-of-day fallback derives hours from world elapsed seconds and `GameDayDurationSeconds` (default 1800s); it is not yet wired to an authoritative saved world clock. Call `SetWorldHour` from the actual clock when integrated. Weather requires explicit calls to `SetStormActive` from the weather subsystem. An AI navmesh and reachable destination actors are required for movement. No NPC is auto-spawned into the map by this pass.

## Defects identified in supplied Unity pseudocode (not engine-tested)
1. `UnderwaterCamera.cs` uses `ColorFog`, which is not a standard URP Volume override; `EventBus` is not imported and no `cam` null guard exists.
2. `WaterBody.ContainsPoint` uses local X/Z bounds while `SurfaceY` assumes translation-only water height; rotated/scaled water geometry and mesh size can disagree.
3. `RiverFlow` directly `CharacterController.Move` during trigger callbacks while `PlayerSwimming` also moves the same controller; use one movement authority.
4. `MountainGenerator` references `TerrainAutoPainter` without a definition, and `CaveGenerator` refers to another namespace without an import.
5. `CaveGenerator` does not carve terrain holes; `SetHeights` on unchanged values creates no entrance. Modifying a built-in cylinder's shared mesh normals can affect instances; make a generated mesh copy.
6. `EnvironmentQuestTriggers` sets `oneTime=false` after firing, but never tests whether it has fired; events can repeat every entry.
7. `AutoQuestSpawner` creates quests for each enemy instance rather than each archetype; IDs collide, repeated `GenerateAllQuests` adds duplicates, and count claims are not tested.
8. Normal/AO/roughness derived solely from albedo are *approximations*, not physically measured PBR. API credentials must remain outside git; 4K output requires verified image dimensions.
9. Starting every particle, shadow, dynamic light, and NPC in every zone regardless of player distance will exceed frame budgets.

## Production gates still required
- Blend authored meshes/materials/animations with the NPC Blueprint.
- Place NPCs and route destinations in the map, with NavMeshBoundsVolume.
- Wire weather and saved world clock to the NPC calls.
- Bind interaction input and UI dialogue/subtitle widget to `InteractNPC`.
- Run UE C++ compile, editor level-play and packaged-build smoke tests.
- Add Water Body Ocean/Lake/River via Unreal Water plugin and physical swimming movement separately.
- Heightmaps: World Partition Landscape + PCG + HLOD; caves need modeled interiors or true terrain-hole mask.
