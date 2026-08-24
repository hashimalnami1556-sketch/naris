# NARIS — GAME STUDIO PLAYABLE SLICE

Runtime: vanilla Three.js + Vite.
Asset contract: GLB/glTF 2.0 for browser runtime.

Simulation is separated from rendering:
- core/GameState: saveable game state
- core/Input: explicit input mapping
- game/*: player, lava hazard, boss
- render/*: Three.js scene/camera/renderer
- ui/*: DOM HUD

This slice intentionally uses procedural placeholder geometry until production Blender meshes are exported. The asset library remains the source of truth for production art.
