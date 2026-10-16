# NARIS v2 Integration Plan

## 1. Runtime boundaries
- Canonical gameplay data remains engine-neutral JSON.
- Unreal/PC is the production runtime.
- Web3D is the fast preview, QA and asset-validation runtime.

## 2. Immediate implementation order
1. Load Ashen Vessel GLB from manifest.
2. Add chase camera and action map.
3. Add Rapier character collider.
4. Add Bone Beast collider + attack telegraphs.
5. Wire Energy + Resonance + Poise.
6. Add Memory Crystal pickup and quest event.
7. Add Ash Gate interaction.
8. Add Celestial Wolf reveal.
9. Add Ash Giant boss gate.
10. Add end-of-demo screen and playtest telemetry.

## 3. Definition of playable
The build is playable only when:
- menu -> game -> boss -> demo end works without manual scene loading;
- movement/collision/combat/quest/save all pass smoke tests;
- no required asset reference is missing;
- performance budget is measured, not assumed.

## 4. Asset policy
No empty placeholder binary files. Missing production assets are declared as required in the manifest.
