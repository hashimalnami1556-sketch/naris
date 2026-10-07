# NARIS Master Build UE5.7 Integration

Canonical production target: `unreal/NARIS_W04/NARIS_W04.uproject`.

## Integration policy
- Extend the existing `NARIS_W04` runtime module; do not create a competing `NARIS` project/module.
- Unreal Engine 5.7 is the production engine.
- Unity/Godot remain prototype/reference sources only.
- Build + Test + Manifest is the acceptance gate.
- Never enable CesiumForUnreal until the plugin installation is verified.
- Cesium ion tokens are external secrets and must never be committed.
- Binary Unreal/source-art assets must use Git LFS where configured.

## Current verified local production state
- W04 runtime/gameplay foundation exists.
- 10 authored W04 material instances were previously validated.
- Three rigged source prototypes are present locally: Ashen Vessel, Bone Beast, Celestial Wolf.
- Their inspected rigs total 64 bones and 22 animation actions.
- Blender CLEAN sources and inspection reports exist locally.
- Windows packaged runtime smoke previously passed 25/25 checks.
- Python CI previously passed 252/252 tests.
- Local integration commit: `eac0db9` (not yet transferred to GitHub because the workstation Git credential returned 403).

## Active production sequence
1. RPG foundation and deterministic automation tests.
2. UE5.7 editor build gate.
3. Jeddah/Cesium verified integration.
4. Character import, retarget, animation and combat validation.
5. 14 Niagara production systems.
6. 16 presentation SFX contracts and audio implementation.
7. Environment and Jeddah-to-NARIS art pass.
8. UI/UX, Arabic RTL and localization compilation.
9. Cinematics and presentation.
10. Performance/scalability.
11. Cook/package/runtime smoke.
12. Final QA manifest and release candidate.

## Safety
Do not treat concepts, blockouts, placeholders, generated text, or filenames as runtime evidence. Runtime readiness requires build/test evidence.
