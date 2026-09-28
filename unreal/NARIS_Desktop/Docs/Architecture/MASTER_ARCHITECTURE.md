# NARIS Master Architecture — Batches 13–20

## Integration rule
GameplayTags + typed components + subsystems are the communication backbone. Direct actor casting is prohibited across feature domains. DataTables/DataAssets carry tuning; code owns invariants; Blueprints own presentation/orchestration.

## Batch 13 — Progression/Economy
Inventory, equipment slots, rarity, deterministic loot, crafting recipes, currency sinks/sources, versioned SaveGame, checkpoint autosave and migration policy.

## Batch 14 — UI/UX
CommonUI-style route stack, HUD, inventory, map, quest journal, codex, settings, accessibility, controller-first navigation, safe-zone and localization-ready layout.

## Batch 15 — Audio
Adaptive music intensity, biome ambience, combat snapshots, VO routing, spatial audio, concurrency and haptic event mapping.

## Batch 16 — VFX/Materials
Niagara registry, pooled transient FX, material parameter collections, impact taxonomy, boss phase FX, weather reactions and destruction budget classes.

## Batch 17 — Online
Replication boundaries are defined without forcing multiplayer into single-player systems: server authority for combat/loot, replicated compact state, dormancy/relevancy policy, session abstraction.

## Batch 18 — Performance/QA
60-fps reference budget (16.67ms), scalable tiers, HLOD/Nanite/streaming policies, PSO warmup, memory budgets, automated data validation, soak tests and profiling gates.

## Batch 19 — Shipping systems
Cinematic hooks, tutorial director, achievements, privacy-conscious analytics event schema, crash breadcrumbs, packaging and release checklist.

## Batch 20 — Master integration
Canonical vertical-slice path: 00_ENTRY → 01_RUINED_PATH → 02_ROOT_TUNNEL → 03_WHISPER_CLEARING → 04_AETHER_SHRINE → 05_BONE_CRYPT → 06_BONE_BEAST_ARENA → 07_POST_BOSS_OVERLOOK → 08_DRAGON_GATE. L_AshenForest_VerticalSlice is the authoritative main map. All critical systems must survive save/reload, streaming, checkpoint restore, boss completion, and the post-boss transition.
