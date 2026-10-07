# NARIS — System / Subsystem Specification (SSS)
Version: 1.0 | UE 5.7

## Architecture
NARIS_W04 is the canonical runtime module. New production systems extend it rather than creating a competing NARIS module.

| Subsystem | Responsibility | Primary contracts | Gate |
|---|---|---|---|
| Runtime/Core | session/state/event orchestration | GameMode, RuntimeSubsystem | compile + smoke |
| Character | hero/enemy skeletal runtime | Character, AnimBP, Skeleton | import + animation smoke |
| Combat | attacks/parry/dodge/damage | combat components/data | automation + encounter |
| RPG | stats/status/loot/items/abilities | DataAssets/components | deterministic tests |
| AI | perception/behavior/boss phases | AIController/BT/data | encounter tests |
| World | streaming/interactions/progression | World Partition/Waystones | traversal smoke |
| Jeddah | georeference/district conversion | manifest + Cesium adapter | plugin + token + map validation |
| Save | persistent versioned state | SaveGame/runtime | round-trip |
| UI | front-end/HUD/menus | UMG/CommonUI contracts | click-through + RTL |
| Localization | EN/AR resources | PO/locres/locmeta | compile + runtime switch |
| VFX | 14 production Niagara systems | Niagara + gameplay cues | asset/type/perf validation |
| Audio | 16 presentation SFX + ambience | MetaSound/Sound assets | cue binding + runtime |
| Cinematics | intro/boss/memories/end | Sequencer/camera/audio | playback smoke |
| Performance | scalability/budgets | profiles/config | 60/30 FPS targets |
| Release | cook/package/release | UAT/manifest | Shipping RC |

## Data ownership
Gameplay tuning lives in DataAssets/tables, not duplicated hard-coded values. Asset IDs are immutable. Source art, generated derivatives and engine assets retain provenance.

## Dependency rules
UI reads gameplay state but does not own combat logic. Save serializes stable state, not transient actors. Jeddah/Cesium is an adapter behind world contracts. Presentation cues are event-driven. Tests use deterministic clocks/random streams.

## Production gates
G0 source/provenance -> G1 compile -> G2 automation -> G3 editor/runtime smoke -> G4 performance -> G5 cook/package -> G6 manifest -> G7 release candidate.
