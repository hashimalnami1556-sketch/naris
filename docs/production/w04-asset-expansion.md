# W04 source blockout expansion

Status: source geometry verified; Blender/Unreal execution pending.

The canonical asset registry now includes the procedural source kit in
`assets/w04-expansion/manifest.json`. Counts and geometry statistics live in that
manifest. Each entry has a unique ID, mesh JSON, portable OBJ and SHA-256. These
are environmental blockouts, not finished character assets or release approvals.
Geometry uses meters, Z up and ground-level origin. Components may overlap;
closed components do not imply a welded watertight union. OBJ is an inspection
format without authored UVs/materials. The Blender adapter generates UVs.

## Windows execution

From the repository root with Python and Blender 4.x installed:

```powershell
python tools/assetforge/export_w04_expansion.py --blender "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" --out "C:\NARIS\ExpansionExchange"
```

Replace the Blender path with the actual installation. Add `--asset-id` to test
one entry first. Every asset gets a fresh background process; the adapter saves
`.blend`, then calls the existing registry-gated `naris_export.py` for FBX/GLB
and its exchange manifest. Existing export directories are rejected.

Launch Unreal with `NARIS_EXPANSION_EXCHANGE` set to that output directory, then
execute `Content/Python/naris_import_expansion.py` in the W04 Editor. It validates
all expected packages and destination availability before using the existing
Unreal bridge, and records partial success if an import fails. Existing
Unreal destinations are rejected. After a partial import, review the result
report and use the single-asset bridge for remaining entries; do not delete
imported work blindly. No production map or release asset is replaced.

## Validation and limits

Python tests verify finite coordinates, non-degenerate faces, closed component
edges, geometry uniqueness, source hashes, registry identity and idempotent
generation. Repository static validation passes; 9 AssetForge tests and 252 CI contract tests passed locally on 2026-09-24. Blender and Unreal are absent
in this execution environment, so FBX dimensions, orientation, UV quality,
collision, LOD, materials and import must still be checked on Windows.

Factory corrections: existing trees now respect the supplied Z coordinate;
the Wave 2 portal disc faces the arch opening. No performance claim is made.

Recovered attachment provenance is recorded in
`data/manifests/SOURCE_INTAKE_2026-09-24.json`. The two PDF copies have identical
bytes; both originals remain intact. Reference images were reviewed as a contact
sheet; videos/PDF pages were not inspected or converted to runtime assets.

References: [Blender API](https://docs.blender.org/api/current/),
[Unreal import tasks](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AssetImportTask?application_version=5.4).
