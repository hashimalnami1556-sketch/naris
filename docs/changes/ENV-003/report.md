# ENV-003 collision export repair

Date: 2026-11-04. Executing agent: Codex.

## Change
The exporter rejected valid UV-less collision helpers, did not validate their render target names, and exported helpers into GLB as visible geometry. Collision helpers now skip render UV validation, must target a selected render mesh using Unreal naming, and remain in FBX while being excluded from GLB. Render UV requirements remain unchanged. Prefixes: UCX, UBX, UCP, USP.

## Evidence
- baseline.md records the unchanged main commit and scope.
- source-intake.json: fresh read of five original GLBs and SHA256. No source file modified.
- unit-tests.txt: 6 behavioral regressions, successful (included in CI total).
- ci-tests.txt: 413 tests successful.
- assetforge-tests.txt: 6 tests successful.
- repository-validation.txt: validator successful.
- blender-roundtrip.json and blender-run.log: Blender 4.5.3 LTS actually executed; old helper rejected the UV-less fixture; patched exporter wrote both formats and reimport verified only render mesh in GLB, render+UCX in FBX.
- Code diff is available in Git/PR; no visual source geometry changed. Runtime screenshots/GIF are not supplied because no runtime scene was executed or edited.

## Limits / next gate
These are synthetic fixture and exporter checks, NOT production collision approval. No actual arena collision has been authored. Convexity, closure, shape-specific primitive requirements, physical scale and passage clearance still require geometric review. GLB is visual exchange only; use FBX for authored Unreal collision. Helpers must not be parents of visible geometry in the source authoring hierarchy.
Unreal import, PIE, BuildCookRun, network tests and performance: NOT_RUN. No local UnrealEditor found. Remote query could not execute because connector requires a link_id; device online/offline state is unknown in this session.
Next: run Unreal 5.7 import of an approved original-asset walkable section and validate collision/camera/traversal. No runtime gate, G1-A, production status or AAA claim is closed.

## Risk and rollback
Existing incorrectly named helpers will now stop export and must be named against their actual selected render mesh. No automatic rename, destructive mesh repair or scale application. Revert this commit to restore exporter behavior; original assets are unchanged.

## Sources
https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-static-mesh-pipeline-in-unreal-engine
https://dev.epicgames.com/documentation/en-us/unreal-engine/simple-versus-complex-collision-in-unreal-engine?application_version=5.7
