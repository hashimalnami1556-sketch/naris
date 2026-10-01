# NARIS Blender Master Builder v1.0

NARIS Blender Master Builder v1.0
================================

Target: Blender 4.x

INSTALL / RUN
1) Open Blender > Scripting.
2) Open NARIS_Blender_Master_Builder_v1_0.py and Run Script.
   OR install it from Edit > Preferences > Add-ons > Install from Disk.
3) Open 3D View, press N, choose the NARIS tab.
4) Click "Build NARIS Master Scene".
5) Use Validate, Generate LODs, Generate Collisions.
6) Use Save + Export All for Godot / Unity / Unreal output packages.

GENERATED PROTOTYPE CONTENT
- Ashen Vessel
- Celestial Wolf
- Bone Beast
- Sword of Poem
- Ashen Forest
- Ash Gate
- Waystone
- NARIS color/material lookdev
- Camera and cinematic lighting
- Hero humanoid rig + basic animation actions
- Sockets metadata
- LOD proxies
- Collision proxies
- JSON asset manifest

IMPORTANT
This is an authoring / production-pipeline add-on. It does not replace runtime gameplay code in Unreal/Godot/Unity.

## Repository integration

- Canonical runtime: Unreal Engine / W04.
- Blender role: asset authoring, validation, LOD/collision generation, preview and exchange export.
- Existing gated exchange path remains authoritative for engine ingestion:
  - `tools/blender/naris_export.py`
  - `schemas/naris_blender_exchange.schema.json`
  - `unreal/NARIS_W04/Content/Python/naris_import_blender_exchange.py`
- This builder does not claim Unreal runtime, package, or playtest evidence.
- Generated meshes are production scaffolds/prototypes until they satisfy the canonical asset registry, provenance, art approval, technical budgets and Unreal validation gates.

## Canonical source

`tools/blender/NARIS_Blender_Master_Builder_v1_0.py`
