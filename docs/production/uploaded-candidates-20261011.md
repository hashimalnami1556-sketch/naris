# Uploaded 3D intake — 2026-10-11

Executing agent: Codex. Scope: owner-supplied 3D candidate validation, source-format correction, isolated Unreal review authoring and exact sampling workflow preparation.

## Completed evidence

Five embedded GLB files are now stored under `assets/intake/w04-20261011/`, registered as new W04 INTAKE blockouts and described by `data/intake/w04-20261011.json`. SHA-256, real triangle counts, bounds, joint counts, animation channels and source limitations are retained. No core production IDs or existing meshes were replaced.

| Candidate | Triangles | Skeleton | Animation |
|---|---:|---|---|
| environment-01 | 17,880 | None | None |
| character-03 | 18,210 | None | None |
| character-01-rigged | 49,886 | 18 joints | Idle, one rotation channel |
| city-01 | 18,161 | None | None |
| character-01 | 49,886 | None | None |

The uploaded `.usdz` is actually a USD crate with `PXR-USDC` magic. `source-corrected.usdc` preserves the original bytes with the correct extension; `source-mislabeled.usdz` preserves provenance. This is a filename correction, not USDZ conversion or USD scene validation. The ZIP supplied with the models contains the same five model filenames; it is not a sixth model.

The geometry validator checks container lengths, embedded dependencies, accessor/view ranges, finite values, triangle indices, skin joint references and normalized weights. It does not prove topology quality, deformation, visual fidelity, animation coverage, collisions, retargeting, performance or engine import success.

`geometry-preview.png` renders the supplied triangles and embedded base-color textures locally, without modifying the mesh. It is not an Unreal screenshot, nor proof of in-game material matching.

## Unreal review workflow

Use a fresh checkout of this branch or review the diff against the live Windows checkout before pulling. Close Unreal. Run:

```powershell
.\tools\windows\Invoke-NarisUploadedCandidates.ps1
```

Or run `assets\intake\w04-20261011\START_REVIEW.cmd`. Set `UNREAL_ENGINE_ROOT` or pass `-UnrealEngineRoot` if UE 5.7 is elsewhere. The launcher builds the editor, then imports the five audited GLBs through Unreal's installed glTF importer. It creates `/Game/NARIS/Intake/W04_20261011/Maps/DEV_IntakeReview`, with a walkable review floor, lighting and a PlayerStart, and opens that map. Press Play for local inspection.

Import requires the glTF Interchange importer to be installed/enabled. Missing importer support, missing meshes, altered hashes or wrong static/skeletal types fail explicitly. Existing imported meshes must match provenance; existing review placements are preserved. This path never writes the production map, startup-map settings, production skeleton, hero mesh or Animation Blueprint. Display geometry has collision disabled; the review floor supplies collision. Scale is normalized from imported bounds for comparison and is not authoritative world dimensions.

The report is written by the editor to `Saved/NARIS/Intake/w04-20261011-import.json` only after successful authoring. Development editor build, actual import, material appearance and PIE are unverified here. Shipping packaging remains gated by existing project requirements.

## Exact generation settings

Six API-format ComfyUI workflows cover Ash Gate, Bell Marsh, Twilight Citadel, Ashen Vessel, Celestial Wolf and Bronze Sentinel. Each uses 40 steps, CFG 7.5, `dpmpp_2m` + `karras`, 1344 × 768 base generation, then a model-based upscale. Seeds and full positive/negative prompts are stored in each workflow. Two output nodes save base and enlarged images.

The available fal SDXL schema exposes steps/CFG/dimensions but no selectable sampler/scheduler. No job was submitted through it and no alternate sampler is silently substituted. There is no connected ComfyUI/Blender/Unreal host here. No new generated image or new final character/map is claimed.

With ComfyUI running locally and an installed SDXL checkpoint plus a verified 2x upscaler:

```powershell
python tools/intake/queue_comfy_generation.py --checkpoint YOUR_SDXL.safetensors --upscaler YOUR_2X_MODEL.pth --validate-only
python tools/intake/queue_comfy_generation.py --checkpoint YOUR_SDXL.safetensors --upscaler YOUR_2X_MODEL.pth
```

The first command validates installed model and node names without submitting. The second queues six jobs and checkpoints accepted prompt IDs under `Saved/NARIS/Intake/`. A queued job is not a completed image. Inspect the resulting images and confirm upscale dimensions before any 3D conversion or runtime promotion. These concept workflows are not conditioned on the supplied pictures; reference fidelity is unverified.

## Remaining gates

- AsusRog was rechecked and is Offline; remote launch was not attempted against an unavailable device.
- Compile/import/PIE on UE 5.7; capture input, traversal, lighting and source-provenance evidence.
- Real character retopology, deforming rig, locomotion/combat animations and retargeting.
- Modular environment separation, collision, navigation, authored level design and performance checks.
- Execute exact generation workflows and inspect outputs; concepts alone do not create runtime art.
- No final EXE, new final maps, final wolf, or final UI redesign is included in this intake change.

References: [Epic AssetImportTask](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AssetImportTask), [ComfyOrg sampling](https://github.com/Comfy-Org/workflow_templates/blob/main/site/knowledge/concepts/samplers.md).


### Receipt recovery update — 2026-10-12

The runner now retains existing receipts and skips previously accepted identical workflows. Legacy receipts are preserved conservatively even if they lack a server field. Different seeds/settings constitute new workflows. Receipt writes are atomic; a `.lock` file blocks concurrent runners. Intent is saved before sending a prompt, so a lost response becomes unresolved rather than causing a blind retry. Inspect ComfyUI history and repair the receipt with the accepted prompt ID before continuing after an uncertain submission. Remove an abandoned lock only after verifying that the prior process has stopped. Queue receipts still do not prove completed generation.
