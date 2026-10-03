# NARIS W04 — Unreal-native Water Runtime

## Implemented
- `ANarisWaterVolume`: swimmable overlap volume with surface height, directional current, optional hazard DPS and attachable surface mesh.
- `UNarisSwimmingComponent`: breath, underwater detection, drowning, current response and vertical swim control.
- `ANarisHeroCharacter`: owns the swimming component and routes `SwimVertical`; Dodge is suppressed while swimming.
- HUD: contextual Breath meter appears only underwater and turns danger-colored at low breath.
- Localization: EN/AR Breath label.
- Input: Space/RT ascend, LeftCtrl/LT descend.

## Authoring
Create a Blueprint subclass such as `BP_Water_Lake_01` from `ANarisWaterVolume`.
1. Set WaterBounds to the swimmable volume.
2. Set SurfaceOffset so it matches the visible water surface.
3. Assign a plane/static mesh and production material to SurfaceMesh.
4. For a river, set CurrentDirection and CurrentStrength.
5. For toxic/lava-like hazards, set HazardDamagePerSecond.
6. Do not mark decorative puddles swimmable.

## Runtime contracts
- The water volume is gameplay authority for surface/current/hazard.
- The swimming component is player-state authority for breath and swimming.
- The HUD only reads state; it does not own breath logic.
- Swimming component tick is disabled while outside water.

## Still required for AAA water visuals
This runtime does not fabricate final water rendering. Production visuals still require:
- authored surface mesh or Unreal Water plugin body;
- translucent/refraction material;
- shoreline foam/decal or Niagara response;
- underwater post-process volume and low-pass/reverb audio;
- splash entry/exit presentation cues;
- caustics, reflection strategy and scalability tiers;
- level-placement and packaged-build validation.

## Known next hardening
- overlapping nested water volumes should become priority/stack based;
- river current needs authored strength by spline/region rather than a single vector;
- authoritative animation state (swim surface / dive / turn / exit ledge);
- network authority if multiplayer is introduced.
