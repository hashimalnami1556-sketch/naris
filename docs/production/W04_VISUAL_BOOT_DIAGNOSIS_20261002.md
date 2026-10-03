# W04 visual launch: prevent running the smoke map as the game

## Confirmed diagnosis
The canonical `DefaultEngine.ini` points to `W04_Prototype`. The editor bootstrap describes it as a deterministic smoke-test map and creates `DEV_SmokeFloor` with `/Engine/BasicShapes/Cube`. This matches the reported black/primitive scene, but only a fresh packaged screenshot and log can identify the exact executable shown on AsusRog.

Map roles:
- `W04_Prototype`: runtime smoke; **never release**.
- `W04_AshenForest_Blockout`: authored six-zone review/blockout; **never release**.
- `W04_AshenForest`: proposed Shipping map; requires map and gameplay evidence before approval.

## Safer local next actions (only when AsusRog is online)
From the repository root in PowerShell:
```powershell
$engine = 'C:\Program Files\Epic Games\UE_5.7'
.\tools\windows\Invoke-NarisW04VisualReview.ps1 -RepoRoot (Get-Location).Path -UnrealEngineRoot $engine -Map Blockout -PrepareBlockout
```
This builds the editor and authors a new *blockout preview* before launching it via an explicit map argument. It **does not** modify `DefaultEngine.ini`, the original production branch, or approve Shipping. For a dry inspection without opening the game, omit `-PrepareBlockout` and add `-InspectOnly`.

Do not switch the default map to `W04_AshenForest` until its `.umap`, approved art/material assets, collision/NavMesh, lighting, gameplay loop, UI, audio/VFX, language support, performance and packaged Windows acceptance are demonstrated.

## Acceptance
1. Confirm a nonempty authored `W04_AshenForest_Blockout.umap`, and record which binary/map is actually launched.
2. Compare blockout preview with the smoke map; capture screenshot and Unreal log.
3. Produce/bind production hero, wolf, boss, environment, UI assets; replace placeholders.
4. Validate `W04_AshenForest` against `W04_ProductionMapRequirements.json` and the existing strict Shipping map gate.
5. Rebuild and play a fresh packaged Windows artifact, including main menu, inventory, map, journal, controls, Arabic UI, audio, gameplay, save/load, and performance regression.

## Offline status
This change supplies a guarded preview launcher. It has **not** been executed on AsusRog while Remote Desktop Commander reports the device offline; no claim of fixed visuals or final release is made.
