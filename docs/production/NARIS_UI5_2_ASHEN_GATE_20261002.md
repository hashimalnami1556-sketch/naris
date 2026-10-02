# CALL OF NARIS — UI5.2 Ashen Gate integration
Date: 2026-10-02
Engine: Unreal Engine 5.7.4
Main map: /Game/World/Maps/L_AshenGate_Playable_V8

## Implemented on the original project
- In-game HUD: real health, energy, one existing companion, dynamic boss bar, current quest objective progress.
- Coordinates-based boss-direction radar (not an authored terrain map).
- PC combat controls with functional hotkey labels.
- Slate main menu restyled with dark/gold styling and RTL titles; world selector points at V8.
- New V8 game map with 36 stone structures (including 1 portal and 4 guardian monoliths), 8 lights.
- Runtime component material overrides: protagonist BlackIron+AncientGold, wolf AetherBlue+VoidCrystal, BoneBeast PaleBone+BlackIron+BloodEmber.
- Original EntryRestored map retained; broken-black V7 kept for investigation but excluded from packaging.

## Verified
- UI5.1 build/cook/stage/pak/archive succeeded.
- UI5.2 packaged Windows Development build/cook/stage/pak/archive succeeded (ExitCode 0).
- UI5.2 runtime logs: LoadMap V8, NARIS_RELEASE_GATE PASS, NARIS_RUNTIME_READY.

## Limits
- Visual concept supplied by the user is an art/UI reference, not a fully functional 3D model.
- The game currently has 1 wolf companion, not the four playable party characters seen in the concept.
- V8 geometry is playable blockout/guidance art, not photoreal finished AAA architecture.
- Firewall consent remains controlled by Windows/the user; no network access was granted.
- Mouse, save/load, fighting interaction tests and accurate frame-time/GPU profiling remain pending.
- Skeletal Mesh asset-level edits did not persist in the previous attempt; current applied material correction is via runtime MeshComponent::SetMaterial.
