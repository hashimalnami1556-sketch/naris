# Batch 09 — Delivery & QA Checklist

## Generated concept references

Two production concept boards were generated for the expanded asset family:
- Character / environment expansion board
- Full 3D assets / environments / props / tiles / VFX / UI showcase board

These are visual references only until source meshes and textures pass the engine QA gates.

## Character factory

- [x] Ash Wanderer role defined: DPS / Explorer
- [x] Marsh Seer role defined: Support / Caster
- [x] Castle Warden role defined: Tank / Guardian
- [x] Translucent Hero variant defined
- [x] Gate Guardian enemy defined
- [x] Babylon procedural preview specification added
- [x] Character switching defined

## Environment factory

- [x] W04 Ashen Forest kit expanded
- [x] Six gameplay locations preserved
- [x] Modular ground / cliff / ruin / bridge / gate pieces defined
- [x] Dressing library defined
- [x] PBR tileable stone family defined
- [x] LOD / instancing / Nanite candidates defined

## Engine handoff

- Unreal Engine 5: final runtime target; Nanite/Lumen/Niagara validation required.
- Babylon.js: GLB procedural preview and character switching.
- Unity 6: compatibility target for exported FBX/GLB where required.
- Godot 4: preview/secondary runtime compatibility.

## Final acceptance gates

1. Mesh topology and normals clean.
2. UVs valid and texel density consistent.
3. PBR maps complete.
4. Skeleton and sockets validated.
5. Collision proxies validated.
6. LOD transitions validated.
7. Transparency and depth-fade validated for spectral assets.
8. Runtime memory and draw-call budget validated.
9. Asset ID and registry entry verified.
10. Source and game-ready files archived.

**Important:** generated concept art does not equal an engine-ready 3D asset. Production status changes to `approved` only after the gates above are passed.
