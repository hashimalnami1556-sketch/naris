# NARIS — AAA UI/UX System v1

## Experience pillars
1. Diegetic darkness: UI feels carved from ash/obsidian, never generic sci-fi panels.
2. Combat clarity: health/stamina/aether and threat cues readable in <250 ms.
3. Quiet exploration: HUD collapses when no threat/objective interaction is active.
4. Controller-first: every screen fully navigable by keyboard/mouse/gamepad.
5. RTL-ready: Arabic is first-class; mirrored navigation but numbers/icons preserve semantic direction.

## Visual tokens
- Canvas: #090B0E / elevated #11151A / surface #171C22
- Bone text: #E7E0D4; secondary #A9A49B; disabled #666A6D
- Aether: #63D6CF; danger: #C94C45; corruption: #8A5BB7; rare-gold: #C6A15B
- Corners: 2–6 px, not rounded mobile cards.
- Borders: 1 px low-contrast + selective emissive edge on focus.
- Spacing: 4/8/12/16/24/32/48.
- Type hierarchy: Display 48–72, H1 36, H2 28, Body 18, Meta 14. Arabic line-height 1.35–1.5.
- Motion: 120 ms focus, 180 ms panel, 260 ms modal, 450–700 ms cinematic reveal.

## HUD
- Upper-left: objective only when updated or tracked.
- Lower-left: player vitals. HP primary, Stamina secondary, Aether segmented tertiary.
- Lower-right: contextual weapon/ability glyphs; fade to 35% after 4 sec idle.
- Center: no permanent crosshair in melee. Context reticle appears for lock-on/interact.
- Boss: bottom-center, name + phase sigil + health; no giant opaque box.
- Damage: directional arc + subtle desaturation/vignette; avoid screen-filling red overlays.
- Interaction prompt: anchored near target projection, with safe fallback at lower center.

## Main menu
Cinematic world background, logo upper third, vertical navigation: Continue / New Journey / Chapters / Codex / Settings / Credits / Quit. Continue displays save timestamp, chapter, location and playtime. No blocking splash sequence after first boot.

## Inventory
Three-column layout: category rail / item grid-list / inspected item. 3D preview occupies right 35–40%. Compare mode uses delta arrows and exact stats. Equip, favorite, dismantle are persistent actions. Filters remember last state.

## World map
Full-screen parchment/ash relief map; fog of war, discovered waystones, quests, bosses, settlements. Zoom levels switch label density. Cursor snaps to points only at controller navigation, never mouse.

## Quest journal
Left: chapter/quest hierarchy. Center: objective chain with completed states. Right: lore image/reward/consequences. Track/untrack is one action. Never expose internal quest IDs.

## Settings
Tabs: Gameplay / Controls / Camera / Video / Audio / Accessibility / Language. Live preview for brightness, UI scale, subtitle style, camera shake, color filters. Confirmation countdown only for display-mode changes.

## Accessibility baseline
Subtitle speaker labels, scalable subtitles/UI, high-contrast interactables, hold/toggle choices, aim/lock assistance, camera shake 0–100, motion blur toggle, FOV, color-blind safe semantic shapes, remappable controls, separate dialogue/music/SFX sliders.

## UX state machine
Boot -> Profile/Save validation -> Main Menu -> Loading -> Gameplay.
Gameplay -> Pause overlay (world paused SP) -> Inventory/Map/Quest/Settings.
Death -> short recap -> Retry checkpoint / Return menu.
All destructive actions require explicit confirmation; ordinary navigation never does.
