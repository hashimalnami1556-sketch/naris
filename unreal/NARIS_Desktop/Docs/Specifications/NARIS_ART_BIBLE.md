# NARIS — Character & Environment Art Bible

## Core art thesis
Dark high fantasy shaped by ash, ruined stone, oxidized metal, bone and restrained aether luminescence. Readable silhouettes and material storytelling take priority over micro-detail.

## Characters
- Hero silhouette: 60/30/10 distribution — cloak/armor/body accent. Distinct shoulder and weapon negative space.
- Faces: realistic proportions, asymmetric micro-detail, roughness variation, no plastic skin.
- Materials: layered master material for skin, cloth, leather, oxidized metal, bone, corruption/aether emissive.
- Texture density: consistent texel density by screen importance; face/hands higher than torso; hidden surfaces reduced.
- LOD: LOD0 cinematic/gameplay close; LOD1 55–65% triangles; LOD2 25–35%; LOD3 silhouette preservation.
- Rig: Epic-compatible humanoid naming where practical; IK hands/feet, twist bones, weapon sockets, cloth anchors.
- Animation: locomotion 8-way, start/stop/pivots, additive lean, turn-in-place, hit reactions by direction, contextual traversal, attack anticipation/contact/recovery.
- Enemies: each archetype must read by silhouette at 25–40 m. Attack tells use pose + audio + VFX, not color alone.

## Environments
Every biome uses 5 layers: macro silhouette, traversal geometry, mid-scale set dressing, micro-decals/foliage, atmospheric layer.
- Hero landmarks visible from navigation routes.
- Repetition broken through modular variants, vertex paint, decals, rotation/scale constraints.
- Paths communicated with value contrast, composition, lights, wind/particles, not glowing arrows.
- Interior/exterior transitions use exposure volumes and audio portals.

## Lighting
Key/fill separation, restrained practicals, volumetric depth, readable combat floor. Aether light is rare and meaningful. Avoid uniform blue fog. Boss arenas have phase-responsive lighting but preserve target visibility.

## Materials
One shared surface framework: base color, normal, packed ORM, macro variation, detail normal, edge wear mask, wetness/ash, optional emissive corruption. Instances, not duplicated materials.

## VFX
Niagara tiers: gameplay-critical / ambient / cinematic. Telegraphs have fixed timing and readable silhouettes. Hit VFX duration <0.45 s for normal strikes. Persistent ambient effects use strict spawn budgets.

## Audio presentation
Layered weapon transients, armor/cloth foley, material-aware footsteps, enemy tell signatures, location reverb. UI audio has three families: navigation, confirmation, danger; no generic beeps.
