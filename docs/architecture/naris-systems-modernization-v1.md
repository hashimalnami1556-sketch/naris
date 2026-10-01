# NARIS — Systems Modernization v1

## Runtime architecture
GameInstance subsystem: profile/session/save orchestration.
World subsystems: encounters, streaming, dynamic events, audio state, VFX budget.
Player components: attributes, combat, targeting, interaction, inventory, progression.
AI: StateTree/Behavior Tree blackboard contract, perception, combat slots, threat/aggro, navigation recovery.
UI: CommonUI-style screen stack with input routing; widgets consume view-model data, never own gameplay state.

## Combat quality bar
Input buffering 120–180 ms; cancel windows data-driven; hit stop 35–70 ms by impact class; camera impulse capped; animation notifies own hit windows; traces are server/authority-ready; damage event includes source, type, poise, impulse, tags. Dodge has explicit invulnerability window and stamina cost. Lock-on prioritizes angle/distance/visibility and recovers cleanly after target death.

## AI quality bar
Idle/patrol/investigate/engage/search/return; coordinated melee slots; ranged repositioning; anti-stuck timeout; perception memory; boss phase transitions are data assets, not hard-coded branches. Debug overlay exposes state, target, distance, path and cooldowns.

## Save system
Versioned save schema; atomic temp-write then replace; checksum; autosave reason; 3 rolling autosave slots; manual slots; migration hooks; never save raw actor pointers. Persist quest state, inventory, progression, discovered map, world consequences, checkpoint and settings separately where appropriate.

## Loading/streaming
Async loading screen with progress stages; World Partition/HLOD policy; shader warm-up/PSO strategy; no synchronous asset loads in combat path. Soft references for noncritical content.

## Performance targets
PC target: 60 fps frame budget 16.67 ms. Game thread <=5.5 ms, render thread <=5.5 ms, GPU <=14.5 ms typical gameplay. 1% low monitored. Scalability tiers for shadows/GI/reflections/foliage/VFX. UI avoids per-frame bindings and expensive blur stacks.

## Telemetry/QA
Runtime log categories: Boot, Save, Input, Combat, AI, Quest, Streaming, UI. Automated smoke flow: boot -> direct play -> move -> attack -> kill -> pickup -> checkpoint -> save -> load -> pause -> settings -> resume.
