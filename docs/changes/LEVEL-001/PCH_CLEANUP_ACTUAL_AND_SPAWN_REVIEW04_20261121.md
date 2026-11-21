# LEVEL-001 — Authorized targeted PCH cleanup and QA readiness

Date: 2026-11-21. Applies to user's authorized AsusRog workstation and existing project `C:\Users\Admin\NARIS`.

## Explicit authorization and safety gate
Owner instructed **"قم باللازم"**, approving previously requested disposal of **three known regenerated SharedPCH build caches**, with condition to confirm no active Unreal/build process. No blanket deletion of Downloads/installed applications/assets/source/other build artifacts was authorized.

Actual read-only precheck showed no matching active UnrealEditor/ShaderCompileWorker/UBT/MSBuild/cl/link/dotnet tasks at deletion time. Free C: space before cleanup was **19.587 GiB**, memory available **20.71 GiB**.

## Only files removed (precise paths, prior sizes)
1. `Intermediate\Build\Win64\x64\NARIS\Development\Engine\SharedPCH.Engine.Project.ValApi.ValExpApi.Cpp20.h.pch` — **2,080,435,136 bytes**.
2. `Intermediate\Build\Win64\x64\NARIS\Shipping\Engine\SharedPCH.Engine.Project.ValApi.ValExpApi.Cpp20.h.pch` — **1,830,944,648 bytes**.
3. `Intermediate\Build\Win64\x64\NARISEditor\Development\UnrealEd\SharedPCH.UnrealEd.Project.ValApi.ValExpApi.Cpp20.h.pch` — **2,416,574,456 bytes**.

All three deletions returned success and the file paths no longer existed immediately after removal. **Actual disk capacity gain = 5.893 GiB**, C: increased from **19.587 to 25.481 GiB**. These are generated compiler precompiled headers and may need rebuilding; no persistent source asset touched.

## Current resource-gate outcome
Follow-up read-only resource preflight confirmed `free_disk_gb=25.48`, `min_free_disk_gb=30`, `eligible=false`, `reasons=[LOW_DISK]`. Later another Unreal run appeared, so competing-process safety also became false. The cleanup was **not enough** to clear the pre-existing >=30 GiB threshold, because C: space had declined since the earlier 26–28 GiB checks. We did **not** bypass the gate, run heavy UE build, shader compiler, or falsely claim successful post-SunFixV3 nighttime rendering.

At least **4.52 GiB more free space** is needed at this measured state. Inspect-only search found other candidate caches/artifacts in `NARIS/Saved`, `C:\Temp\TxGameDownload`, and `AppData/Local/UnrealEngine`, but **none were deleted or relocated**. Avoid deleting unrelated emulator assets or built deliverables; obtain scope-specific approval before further destructive cleanup, or use more storage.

## Continuation accomplished without heavy engine launch
- Re-opened and validated previously selected actual OSM pedestrian spawn candidate: OSM way **45204113**, Unreal world **[27632.27,-340805.6,140] cm**, yaw **132.93°**, geometry clearance 1857.06 cm (not runtime collision/NavMesh clearance).
- Wrote safe review-only importer for next QA step: `Saved/GIS/Jeddah/LEVEL001_review04_spawn_apply_after_gate.py`. It refuses to act if <30 GiB free, checks correct project and candidate, creates rollback `.umap`, requires exactly one PlayerStart, updates **only** isolated Review03 map, and checks original `L_Jeddah_GIS_V2.umap` file metadata unchanged. It records runtime collision/NavMesh/server-client tests as **false**. This importer has **Python syntax check PASS but is NOT executed** due the resource gate.
- Original GIS V2 map `Content/NARIS_GIS/Jeddah/Maps/L_Jeddah_GIS_V2.umap` checked still at 10,414,445 bytes, timestamp Oct 2, 2026.

## Needed next steps
1. Recover at least ~4.52 GiB additional C: free capacity in a separately approved, narrowly targeted action, and confirm no competing UE jobs. No broad recursive deletion.
2. Re-run `Saved/GIS/Jeddah/LEVEL001_resource_preflight.ps1`. Only on `eligible=true`, capture actual V3 same-camera Lit screenshot (1920×1080), retest >50% geometry-mask visibility and visually inspect light direction, brightness and overexposure.
3. After the V3 lighting QA passes, run gated Review04 PlayerStart application, collision, NavMesh walk, server + two clients, Build/Cook, localization and perf; preserve all before/after/diff and rollback evidence.
4. Keep Open Heritage 3D scans out until explicit separate commercial/derivative permission arrives. GitHub PR #113 remains draft, issue #112 open.

Documentation-only commit. The user workstation's current `.umap`/binary materials are **not committed to GitHub**.
