# NARIS Character Production Integration

## Canonical chain

Higgsfield concept → Approved visual reference → Immutable Asset ID → Adobe/Figma source references → Blender 3D → Unreal Character/Skeletal Mesh → Animation → VFX/Materials → QA → Release.

## System ownership

| System | Canonical responsibility |
|---|---|
| Higgsfield | Character concept, pose, turnaround and cinematic visual reference |
| Adobe | High-quality source art, texture/material studies and visual source files |
| Figma | Character reference boards, UX dependencies and design-system presentation |
| Blender | High-poly, retopology, UV, baking, material preparation and export |
| Unreal Engine | Skeletal mesh, animation blueprint, materials, Niagara, gameplay and runtime |
| GitHub | Versioned source specifications, registries, prompts, automation and review history |
| MCP | Controlled inspection, validation and production status orchestration |

## Asset identity

Primary character: `NARIS-CHR-ASHEN-VESSEL-0001`

Primary weapon: `NARIS-W10-WPN-SWD-0001`

Secondary weapon: `NARIS-W10-WPN-SWD-0002`

## Required handoff package

- Character turnaround reference.
- Face close-up.
- Weapon profile.
- Material reference.
- Costume construction reference.
- Proportion sheet.
- Negative-art-direction sheet.
- High-poly source.
- Retopologized game mesh.
- UV layout.
- Texture set.
- Material instance definition.
- Rig/skeleton.
- Animation set.
- Unreal integration metadata.
- QA evidence.

## Integrity rules

1. Asset IDs are immutable.
2. No tool may silently change the locked visual identity.
3. The primary sword length must remain approximately 150 cm total / 115 cm blade unless a deliberate design revision is approved.
4. Character face, hair, costume and weapon must remain consistent across cinematic and gameplay references.
5. Binary payloads belong in a binary-capable transport such as Git LFS; GitHub text metadata remains the canonical record when binary upload is not available.
6. Never mark an asset Approved without evidence of the required production gates.
