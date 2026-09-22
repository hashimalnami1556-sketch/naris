# NARIS Web3D Preview v2.0

This branch adds a browser/WebGL preview track for rapid iteration and playtesting.

## Stack
- Three.js
- TypeScript
- Vite
- GLB/glTF 2.0
- Rapier for 3D physics
- DOM HUD/menus

## Architecture rules
- Simulation owns gameplay state.
- Renderer mirrors simulation state; it is not the source of truth.
- Input actions are mapped centrally.
- Assets are referenced through stable manifest keys.
- Final 3D shipping assets use GLB/glTF 2.0.
- HUD and menus stay in DOM to preserve readability and accessibility.

## NARIS role
This is a fast Web preview/playtest branch. It does not replace the Unreal/PC production branch.

## Production gate
Do not claim the preview is a final game until real character/environment GLBs, animation clips, collision, combat hit volumes, audio and performance validation are present.
