# NARIS Runtime UI v2

This pass upgrades the W04 runtime interface from fixed-position prototype rendering to a responsive presentation layer.

## Implemented in code
- Responsive scale and safe margin foundation.
- Compact player vitals at lower-left.
- Objective card at upper-right.
- Interaction prompt at lower-center.
- Centered boss presentation.
- Subtitle panel with user scale.
- Modernized front-end/pause menu hierarchy.
- Pause routes for Inventory, World Map and Quest Journal.
- Inventory/equipment/currency fields added to persisted state.
- Controller/keyboard navigation remains authoritative.
- Automation coverage for viewport scale, safe margin and normalized bars.

## Runtime ownership
Gameplay remains authoritative. HUD only reads combat, energy, interaction, runtime state and settings. Menu routing remains in ANarisPlayerController. The UI layer does not mutate combat state.

## Remaining binary-asset production
UMG/CommonUI Widget Blueprints, final typography assets, icon atlas, material brushes, 3D item preview scene, authored world-map texture, loading/chapter art and localized string tables require Unreal content assets and must be integrated in-editor. The C++ runtime now provides the navigation/data contract for that work.
