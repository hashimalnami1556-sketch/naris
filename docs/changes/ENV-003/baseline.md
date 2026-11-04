# ENV-003 baseline

Executing agent: Codex. Date: 2026-11-04.
Base: 0d44d54cacab0443f28f4a11400d544ea4d0941f (main).
Scope: existing Blender exchange exporter collision validation and export selection only.
Before: collision meshes require render UVs; collision names are not checked against selected render meshes; GLB includes collision geometry.
Unreal descriptor: 5.7. No local UnrealEditor executable found. Remote device query could not execute (connector requires link_id).
Change.ps1 is absent; reuse tools/blender/naris_export.py and existing tests rather than introduce a duplicate orchestrator.
Runtime screenshots, Build, Cook, PIE, network, FPS/frame/memory: NOT_RUN / unmeasured.
Source assets: immutable; inspect GLB metadata without changing original geometry.
Rollback: revert this change; no production assets or engine settings are changed.
