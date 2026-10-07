# NARIS — Software Requirements Specification (SRS)
Version: 1.0 | Target: UE 5.7 | Canonical project: unreal/NARIS_W04/NARIS_W04.uproject

## Product
Third-person Action RPG / Dark Fantasy / Souls-like. Production target is Unreal Engine 5.7; Blender is the source DCC. Unity/Godot are prototype/reference only.

## Functional requirements
SRS-F-001 Front end: Main Menu, New Game, Continue, Settings, Controls, Quit.
SRS-F-002 Player: movement, camera, sprint, dodge, attack, parry, lock-on and interaction.
SRS-F-003 Combat: health, stamina/essence, damage, poise/stagger, status effects and death.
SRS-F-004 RPG: stats, deterministic modifiers, equipment, weapons, abilities, loot, inventory, crafting and skill progression.
SRS-F-005 AI: enemy perception, combat states, packs, bosses and phase transitions.
SRS-F-006 World: exploration, Waystones, collectibles, Memory Crystals, Ash Gate, secrets and streaming.
SRS-F-007 Jeddah: georeferenced production world with district anchors; Cesium integration only after verified plugin/token configuration.
SRS-F-008 Save: versioned save/load, autosave and progression restoration.
SRS-F-009 UI: HUD, boss HUD, inventory, equipment, map, journal, crafting, skill tree, pause/save-load.
SRS-F-010 Localization: English + Arabic RTL, subtitles and compiled localization resources.
SRS-F-011 Presentation: Niagara, MetaSounds/SFX, camera shakes and Sequencer cinematics.
SRS-F-012 Release: Win64 Shipping cook/package and runtime smoke.

## Non-functional requirements
SRS-NF-001 60 FPS production target; 30 FPS scalability fallback.
SRS-NF-002 World Partition/HLOD for large-world content.
SRS-NF-003 Nanite/Lumen where appropriate and measured.
SRS-NF-004 No secrets/tokens committed.
SRS-NF-005 Binary art/Unreal assets governed by Git LFS.
SRS-NF-006 Accessibility: remappable controls, subtitles, readable UI and scalable settings.
SRS-NF-007 Build + Test + Manifest is the acceptance gate.
SRS-NF-008 Concepts/blockouts/placeholders are never reported as production-ready runtime evidence.

## Acceptance
Every requirement must map to implementation evidence and at least one automated/manual verification record. Shipping RC requires compile, cook, package, runtime smoke, performance profile and QA manifest.
