# NARIS — Fiery Demon W04 production handoff (2026-10-14)

**Source of truth:** branch `feat/w04-character-intake-20261012`, PR #39.
**Runtime namespace:** `NARIS_W04`, UE 5.7 target.
**Approval:** optional Ash Gate boss **development/QA approved**, **NOT shipping approved**.

## Actual available work
- Native class `ANarisFieryDemonBoss` reuses the existing `ABoneBeastBoss` combat, lock-on, HP, save and reward pathways.
- Visual proxy `NARIS_Fiery_Demon_COMBAT_PROXY_Rigged.glb` comes from the prior chat delivery. It is **not** the original demon USDZ converted to a bespoke rig.
- Native boss tuning: HP 6200, 55% phase transition, attack windup, restricted damage impact window, autonomous aggro, 2-phase attacks and no story demo completion on death.
- `tools/unreal/import_fiery_demon_runtime.py` authoring tool targets **`/Game/NARIS/W04/Maps/L_FieryDemon_QA`**.
- `tools/blender/export_naris_fiery_demon.py` validates Blender rig/actions and exports FBX.
- `tools/windows/Invoke-NarisFieryDemonBuild.ps1` orchestrates Blender, C++ compile, Unreal import, optional Windows BuildCookRun and packaged launch.
- GitHub Actions run static/unit/contract checks only on GitHub-hosted runners; `Unreal Windows package gate` is **skipped** unless a suitable Windows/Unreal self-hosted job is deliberately executed.

## Device workflow (AsusRog)
Clone/fetch and check out the branch from GitHub into `C:\Users\Admin\NARIS\naris-repo`, or point `-RepoRoot` at your existing checkout. Put the animated GLB extracted from the previous user delivery in a private asset folder. Do **not** publish unreviewed model binaries to a public repo.

In Windows PowerShell (editor closed):

```powershell
cd C:\Users\Admin\NARIS\naris-repo
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\windows\Invoke-NarisFieryDemonBuild.ps1 `
  -RepoRoot "C:\Users\Admin\NARIS\naris-repo" `
  -DemonGlb "C:\Users\Admin\NARIS\Assets\NARIS_Fiery_Demon_COMBAT_PROXY_Rigged.glb" `
  -EnvironmentGlb "C:\Users\Admin\NARIS\Assets\Environmental 1.glb" `
  -UnrealEngineRoot "C:\Program Files\Epic Games\UE_5.7" `
  -Package -Launch
```

Edit the paths to match the real project and where you extracted the assets. Environment GLB is optional; if omitted, a basic collision platform is still generated. The launcher **refuses** to run stale EXEs and never overwrites a production map without `-AllowProductionMapEdit`.

## Gates and evidence
| Gate | Evidence | Acceptance |
| --- | --- | --- |
| GLB integrity | Blender JSON and FBX | >=15 bones, >=4 actions, skinned meshes |
| Native build | Build.bat `NARIS_W04Editor Win64 Development` | exit 0 |
| Level authoring | `naris_fiery_demon_editor_import.json`, actual `.umap` | status `editor_map_saved`, >=3 UE animations |
| Windows package | `BuildCookRun`, new EXE path | exit 0, `NARIS_W04.exe` exists |
| Packaged map smoke | fresh runtime log | process survives initial startup and log mentions `L_FieryDemon_QA` |
| Gameplay | human/autonomous PIE QA | aggro/chase, phase 55%, melee range, death, persistent respawn, collision and animation playback |
| Performance | Unreal Insights/CsvProfiler | measured FPS and frame time, no assumption of 60 FPS |
| Shipping | signed release checklist | only after passing all gates |

Output manifests:
`artifacts/fiery_demon_qa/naris_fiery_demon_build_report.json`,
`artifacts/fiery_demon_qa/naris_fiery_demon_editor_import.json`.

**Caution:** map-load/process-alive smoke is not proof of playable gameplay. Until UE is executed on AsusRog/self-hosted runner, it is inaccurate to describe this as a built and working `NARIS.exe` containing Fiery Demon.

## Known next tasks
- Get a genuine animation review in UE5.7 (bone influence/retarget, limb deformation, montage notifies).
- Replace clip timers with native AnimNotify impact windows before Shipping.
- Build collision capsule and navigation bounds, run AI and real combat tests in PIE.
- Add visual/material/VFX/audio artist passes; rights/redistribution verification.
- Keep the original W04 map safe; promote from isolated QA to Ash Gate only following test evidence.
