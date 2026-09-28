# Batch 10 — World Architecture

## Runtime flow
World Partition -> Zone Registry -> Biome Resolver -> PCG Seed -> Encounter Director -> Dynamic Event Director.

## Rules
- World Partition owns macro streaming; gameplay systems request zones, never raw level names.
- PCG is deterministic from WorldSeed + ZoneID + LayerSeed.
- Biome definitions are data-driven.
- Dungeon generation outputs room graph first, geometry second, encounters third.
- Roads connect settlement anchors using weighted path costs and must not spawn across exclusion volumes.
- Dynamic events use cooldown, rarity, player progression, threat and biome tags.

## Target world layers
1. Terrain/landscape
2. biome dressing
3. traversal/roads
4. settlements
5. dungeon entrances/interiors
6. encounter anchors
7. quest/event anchors
8. audio/VFX atmosphere
9. optimization/HLOD

## Initial NARIS zones
Ashen Forest, Root Tunnels, Whisper Lake, Ash Gate, Bone Beast Arena, Aether Shrine.
