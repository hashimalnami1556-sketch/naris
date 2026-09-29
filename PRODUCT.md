# CALL OF NARIS — Product Context

<!-- impeccable:product-schema 1 -->

Updated: 2026-09-29. Scope: player-facing game UI. This is a concise routing record; linked canonical owners retain authority for their facts and specifications.

## Platform

Windows PC, native Unreal game. The [project descriptor](unreal/NARIS_W04/NARIS_W04.uproject) selects Unreal Engine 5.4. Browser slices are prototypes, not the shipping runtime. Do not map this product to web/iOS/Android merely to satisfy a design-tool default.

## Users and Purpose

Players explore, fight and progress through the dark-fantasy action RPG described in the [project baseline](README.md). UI supports starting/resuming, understanding combat state, interacting with the world, progression, settings and save/load. Arabic and English are required; see the [W04 HUD contract](unreal/NARIS_W04/Content/NARIS/W04/UI/W04_HUD_Implementation_Spec.md).

## Product Boundaries

- Initial acceptance scope is W04 — Ashen Forest on Windows. The [production status](docs/PRODUCTION_STATUS.md) owns the playable sequence and release gates.
- [NARIS Toolkit product design](docs/PRODUCT_DESIGN_NARIS.md) describes an artist/technical-artist production workbench inside Blender. It is a separate UI surface, not the player HUD.
- [UI System](NARIS_MASTER/14_UI_UX/UI_SYSTEM.md) owns the menu/screen inventory.
- [Current work](PROJECT_STATE.md) owns implementation handoff and blockers; this record does not duplicate volatile readiness counts.

## Capabilities and Constraints

The [W04 HUD implementation spec](unreal/NARIS_W04/Content/NARIS/W04/UI/W04_HUD_Implementation_Spec.md) owns runtime bindings, HUD states and accessibility requirements. The [Unreal source](unreal/NARIS_W04/Source/NARIS_W04/) is implementation evidence, not playtest evidence. A UI is not complete until connected to runtime state and save/load.

Preserve the Unreal/W04 baseline. Engine migration is a separate change requiring build evidence. Generated images and supplied GLB models remain references or candidates until registered and validated through the [production pipeline](docs/MASTER_PRODUCTION_PIPELINE.md). Asset IDs and current fields belong to the [master registry](data/MASTER_ASSET_REGISTRY.json).

## Brand Commitments

Use CALL OF NARIS and the established identity in [README](README.md). Preserve the NARIS color hierarchy and gameplay readability required by the UI System. This initialization does not select a new palette, typography, logo or visual world, and does not merge unrelated game projects.

## Product Principles

1. Keep critical combat information readable while preserving the playfield.
2. Connect visible UI state to actual gameplay state; do not represent decorative mockups as implemented systems.
3. Keep English/Arabic localization and accessibility in the implementation scope.
4. Distinguish design, source code, static checks, engine builds and playtests.
5. Keep one canonical owner per fact and preserve asset provenance.

## Accessibility and Inclusion

Follow the W04 HUD spec for Arabic RTL, English localization, subtitle toggle, text scaling, reduced motion, high contrast and controller remapping. Source-level availability does not close Arabic visual/RTL QA or controller usability gates.

## Evidence and Open Decisions

- Repository documentation and the Unreal descriptor establish scope and engine selection.
- This context pass does not establish an Unreal build, engine import, playable demo or measured performance result.
- Production blockers remain in [W04 readiness](docs/production/work/active/w04-readiness.md); do not close them based on this document.
- User testing, target-hardware measurements and final visual acceptance remain governed by the production gates.
- New UI proposals must distinguish suggestions from accepted product decisions.

## Maintenance

Begin with [AGENTS](AGENTS.md), [current work](PROJECT_STATE.md) and [source ownership](docs/production/knowledge-sources.md). Update canonical owners first and keep this record concise. Canonical notes are English; preserve localized Arabic strings and communicate with the owner in Arabic.
