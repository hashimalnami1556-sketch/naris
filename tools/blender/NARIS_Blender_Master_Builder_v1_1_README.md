# NARIS Blender Master Builder v1.1 — W04 Contract Integration

## Canonical role
This tool is Blender authoring automation for the Unreal Engine 5.4 / W04 production path. It does not replace Unreal validation or constitute runtime evidence.

## Bound core assets
- `NARIS-W04-CHR-HERO-0001` — Ashen Vessel
- `NARIS-W04-CHR-COMPANION-0001` — Celestial Wolf
- `NARIS-W04-ENM-BONEBEAST-0001` — Bone Beast
- `NARIS-W04-WPN-SWORD-0001` — Sword of Poem

Each generated root receives `naris_asset_id`, `naris_engine_target`, `expected_unreal_object_path`, registry/binding metadata and the canonical exporter reference.

## Sources of truth
- `data/MASTER_ASSET_REGISTRY.json` — immutable asset identity/status.
- `unreal/NARIS_W04/Content/NARIS/W04/Production/W04_ProductionAssetBindings.json` — Unreal object path and technical gate.
- `data/environments/W04_AshenForest_environment_factory_v2.json` — environment dimensions/policies.
- `tools/blender/naris_export.py` — registry-gated exchange export.

## W04 environment contract
The builder may consume, but must not contradict:
- grid: 1 m
- floor module: 4 m
- wall height: 3.5 m
- streaming cell: 128 m
- maximum material slots per core static mesh: 4

## Promotion rule
Generated geometry remains prototype/scaffold content until visual approval, provenance, technical-art validation, registry-gated export, Unreal import, collision/LOD/material validation, performance validation and gameplay QA are complete.

## Validation
Static contract test:
`python -m unittest tools.ci.test_blender_master_builder_v11_contract -v`

Repository gate:
`python tools/ci/validate_naris.py`
