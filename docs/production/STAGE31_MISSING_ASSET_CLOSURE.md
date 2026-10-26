# Stage 31 — Missing Production Asset Closure

## Closed in source
- Hero combat defaults to animation-driven hit windows.
- Dodge gameplay authority now waits for successful animation start.
- Stage30 validator defines required AnimBP/Montages and PBR master assets.
- UE5.7 runner performs C++ build -> asset gate -> final-map gate.
- PBR naming/features are now canonical in a machine-readable binding manifest.

## Still requires Unreal binary authoring
The repository cannot truthfully synthesize final .uasset animation blueprints, montages, materials, texture imports, or the final .umap without Unreal Editor executing against the actual source meshes/textures/animations.

## Acceptance
Do not mark Animation, Materials, Final Map, PIE, or Windows Shipping PASS until the UE5.7 runner succeeds and interactive combat/map QA is recorded.
