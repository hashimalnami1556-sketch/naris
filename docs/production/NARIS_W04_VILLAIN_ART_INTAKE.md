# NARIS villains — visual-asset and engine integration

**Status: development implementation, not shipped or fully verified.**

## What is in pull request #40

Seven new AI enemy archetypes have Unreal C++ game state, health, chase/patrol,
attacks, stagger and death. `ANarisVillainCharacter` has an explicit
`VisualMesh` skeletal mesh slot, plus six AnimSequence state slots. The importer
fails closed if a mesh or required clip is absent; visual placeholders remain
development-only. W04 Bone Beast narrative actor remains unchanged.

## Prototype geometry (separate downloadable deliverable)

The conversation contains a ZIP named `NARIS_VILLAIN_3D_PROTOTYPES.zip` with
seven newly constructed, primitive/procedural GLB 2.0 skinned character meshes.
Each has a 16-joint skeleton and seven embedded technical motion clips:
Idle, Walk, Attack_Light, Attack_Heavy, HitReact, Stagger, Death.
They are **not sculpted AAA art**, and not reconstructions of source images;
they are unapproved low-poly proof-of-pipeline examples. The ZIP is not
committed here as GitHub source: the current GitHub connection has not ingested
the binary asset package. To use it, place the downloaded archive locally on
the Windows development machine.

## Reproducible host installation (after tools are available)

```powershell
$root = 'D:\Path\To\naris' # actual checkout, not a guessed host path
$engine = 'C:\Program Files\Epic Games\UE_5.7'
$blender = 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe'
& "$root\tools\windows\Invoke-NarisW04VillainArtIntake.ps1" `
  -RepoRoot $root `
  -PrototypePackage 'C:\Users\<you>\Downloads\NARIS_VILLAIN_3D_PROTOTYPES.zip' `
  -BlenderExecutable $blender -UnrealEngineRoot $engine
```

The launcher unpacks and converts GLBs using Blender, builds the UE 5.7
editor, authors W04 development actor placements, imports FBX SkeletalMesh and
AnimSequence assets, checks required clips, and binds imported art to each
placed actor. It is fail-closed: no success claim without the importer report.
Outputs reside under `unreal/NARIS_W04/Saved/NarisVillainPrototypeIntake/`
and `Saved/TestReports/naris_villain_fbx_intake.json`.

**Important:** Blender FBX multi-clip output and Unreal 5.7 FBX asset/animation
import must be validated on the real Windows host; some Blender/Interchange
versions may require per-clip FBX exports and retargeting. C++ test runs here
are static; only Unreal build, PIE and runtime logs can prove in-game success.

## Current external blockers

- AsusRog was shown online by Desktop Commander but remote command service
  returned *monthly usage cap exceeded*; no additional remote execution is
  available from this turn.
- Connected fal AI account reports `balance_exhausted`; no paid Image-to-3D
  model generation was submitted.
- 3D studio sculpt/retopology, complete PBR textures, approved rigs,
  gameplay hit-event notifies, physics assets and shipping performance gates
  still require genuine authoring and testing.

CI green means source contract integrity only, not Windows/engine confirmation.
