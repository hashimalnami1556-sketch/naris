# G0-001 — Original GLB inventory / audit 008

Five original `.glb` files were parsed from their binary JSON chunks and checked for valid GLB v2 headers and full declared file length.

| Original | Declared skins | Joint references | Animations | Classification |
| --- | ---: | ---: | ---: | --- |
| `Character 1.glb` | 0 | 0 | 0 | Unrigged |
| `Character 3.glb` | 0 | 0 | 0 | Unrigged |
| `Character1_NARIS_Rigged_Prototype.glb` | 1 | 18 | 1 | Prototype only |
| `City 1.glb` | 0 | 0 | 0 | Static environment |
| `Environmental 1.glb` | 0 | 0 | 0 | Static environment |

Audit: **5/5 GLB binary structural checks passed**; Python scripts syntax checked. Source GLB bytes were not modified. Reproducible local package: `NARIS_CONTINUATION_008_G0_AUDIT.zip` (contains CSV, JSON, non-destructive audit and UE Editor import preparation script).

**Blocked:** actual 92-joint production skeleton, vertex weighting, IK Rig/Retargeter, gameplay level import, runtime PIE, before/after/diff captures, BuildCookRun, automation tests and multiplayer benchmark. `AsusRog` connection is offline. This file records inventory only; do not present it as engine/runtime or complete game verification.

**Rollback:** revert documentation-only commit; preserve source assets.
