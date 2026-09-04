# CALL OF NARIS — New Asset Pack QA

**Date:** 2026-09-04  
**Pack:** NARIS-ASSET-PACK-2026-09-04  
**Scope:** character expansion + translucent assets + waystone + portal + tileable stone + Babylon preview

## 1. Production checklist

| Item | Result | Notes |
|---|---|---|
| Ash Wanderer role defined | PASS | DPS / Explorer |
| Marsh Seer role defined | PASS | Support / Caster |
| Castle Warden role defined | PASS | Tank / Guardian |
| Independent visual direction | PASS | Dedicated asset identity and palette in pack manifest; composite artboard stored as visual master |
| Babylon procedural factory | PASS | Deterministic factory functions and canonical IDs |
| Character switching | PASS | Interactive Babylon preview |
| Translucent Hero | PASS | Fresnel-style alpha material |
| Gate Guardian | PASS | Ethereal ember material + silhouette horns |
| Waystone / Save Point | PASS | Crystal + stone base |
| Holy Portal | PASS | Radiant ring + portal core |
| Tileable stone material | PASS | Repeatable procedural bump preview |
| Asset registry update | PASS | New pack IDs added to master registry |
| Delivery manifest | PASS | JSON manifest committed |

## 2. Technical acceptance

- All new preview assets carry immutable NARIS Asset IDs.
- Babylon preview is intentionally a procedural blockout/validation layer, not a replacement for final Unreal hero meshes.
- Transparent materials are isolated from opaque materials so alpha behavior can be tested independently.
- Character switching is available without rebuilding the scene.
- The preview uses the same canonical asset IDs used by the production registry.
- Final binary exports (`GLB/FBX/PNG/JPG`) remain subject to external binary storage and final art approval.

## 3. Known limitation

The procedural Babylon models are production-preview geometry, not final sculpted AAA character topology. They are suitable for scale, silhouette, material, scene-integration and pipeline validation. Final hero/enemy production still requires approved sculpt/retopo/UV/texture/rig/animation passes before release.

## 4. Delivery gate

**Pack state: READY FOR NEXT PRODUCTION PASS**

Next production targets:
1. Replace procedural character bodies with approved high-resolution meshes.
2. Bind animation sets and combat sockets.
3. Author final PBR texture sets at the target resolution.
4. Export GLB/FBX and register storage locations.
5. Run Unreal import, LOD, Nanite/material, collision and performance QA.
