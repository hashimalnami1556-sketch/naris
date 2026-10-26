# Stage34: animation, materials and Windows editor gates

The user requested actual movement AnimBP/Montages, PBR textures with UV, and UE5.7 C++ compile plus gameplay/map tests.

## What is delivered in the repository
- An Unreal Python **read-only audit** for imported SkeletalMesh, AnimSequence, AnimMontage, AnimBlueprint, Material and Texture2D.
- A JSON transition specification for the hero and guardian, including movement thresholds and combat notifies.
- A Windows PowerShell **build-and-audit runner** that fails if the C++ build fails or required animation assets are missing.

## What is NOT delivered
- No generated or verified AnimBlueprint, Animation Montages, or UV-authored high-quality PBR assets.
- No confirmed C++ compile, PIE combat test, playable map, or Win64 EXE.
- The remote AsusRog host was offline. Running the script on an authorized Windows machine with UE5.7 is necessary.

## Running
```powershell
powershell -ExecutionPolicy Bypass -File tools/windows/Invoke-NarisStage34BuildAudit.ps1 -RepoRoot 'D:\UE_Projects\naris' -UnrealEngineRoot 'C:\Program Files\Epic Games\UE_5.7'
```
The example paths must be adapted to the actual installation. The audit will fail if the AnimBP/Montages are missing; this is intentional.
