# Environment RC1 approval and collision gate follow-up

Owner approval received 2026-11-04. Eight files total are accepted as SOURCE EXPORT CANDIDATES FOR TESTING. This is not a packaged-game RC1 or a runtime gate closure. Exact filenames/hashes and prior Blender roundtrip evidence are in rc1-manifest.json. City and Environment are composite assets, not verified modular kits. No original source or export geometry was changed.

The selected menu image is a visual reference, with identity/hash recorded. No UMG widget, asset import, executable or functioning menu is implied. Keep canonical W04 paths and existing menu implementation. Do not create another project tree.

Fixed the Unreal production validator accepting customized_collision=True without geometry. Required-collision assets must have a positive simple or convex shape count; negative API results fail closed. Box-only collisions are recognized. This is a minimum presence test, not proof of correct channels, passage clearance or character traversal. Unreal execution remains unavailable.

Collision authoring is blocked on physical-scale and walkable-section review of the composite assets. Do not wrap an entire city in a convex hull, which can seal passages. No fabricated floor/wall modules are included. Lumen/lightmap, Nanite/LOD and mesh-combination settings remain per-asset decisions; no blind bulk changes. Existing Factory v2 grid remains unchanged.

Validation: behavioral Python tests and repository validator recorded separately. Build/Cook/PIE/traversal/performance: NOT_RUN. Rollback: revert this follow-up; source exports unchanged.

Reference: https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/StaticMeshEditorSubsystem?application_version=5.7
