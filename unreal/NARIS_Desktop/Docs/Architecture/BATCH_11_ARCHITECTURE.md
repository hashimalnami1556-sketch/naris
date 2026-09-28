# Batch 11 Architecture

## Runtime flow
World Partition -> WorldSubsystem -> EnvironmentDirector -> Weather/DayNight -> PCG zone rules -> Roads/Settlements/Dungeons -> Encounter Director.

## Systems
- Terrain profiles: biome-driven height/noise/erosion metadata.
- River network: spline descriptors, width/depth/flow, biome constraints.
- Road network: weighted graph edges between POIs/settlements/fast-travel nodes.
- Settlement generator: deterministic layout seeds and district budgets.
- Dungeon runtime: deterministic archetype/seed/depth and encounter hooks.
- Environment Director: normalized time-of-day, weather state and intensity.
- Fast Travel: unlockable nodes with zone IDs and world transforms.
- Optimization: World Partition + Data Layers + HLOD; Nanite/Lumen policy per asset class.

## Integration contract
Combat and AI remain authoritative for damage/encounters. Batch 11 only emits world/environment events and requests encounter activation; it never duplicates combat state.
