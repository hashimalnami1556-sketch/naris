# LEVEL-001 — Active blocker & non-destructive resource recovery audit (2026-11-21)

Status: **Jeddah lighting V3 is saved and its correct light vector is verified in UE 5.7.4; actual Lit post-fix screenshot and Build/Cook/network/FPS quality gates are NOT complete.** Do not close issue #112 or merge draft PR #113.

## Latest work and evidence
- Local user workstation `AsusRog`, `C:\Users\Admin\NARIS\NARIS.uproject`.
- Original certified GIS V2 map `Content\NARIS_GIS\Jeddah\Maps\L_Jeddah_GIS_V2.umap` untouched and still not Shipping-approved.
- Review-only map `Content\NARIS_GIS\Jeddah\Maps\L_Jeddah_AlBalad_Footprints_Review03.umap` saved in UE 5.7.4 with 189 real OSM building footprint extrusions and camera / lighting diagnostic improvements.
- Source of lighting failure fixed: bad positional `unreal.Rotator` order pointed sunlight upward. Real UE report `Saved\GIS\Jeddah\LEVEL001_AlBalad_Footprints_Review03\LEVEL001_SunDirection_FixV3_Report.json` has sun forward Z before **+0.34202**, after **-0.46947**; sunlight+sky now MOVABLE; sunlight 8500 lux, skylight 1.65; PostProcess exposure bias +1.5 EV. Unreal MapCheck 0 errors/0 warnings. Rollback copy `L_Jeddah_AlBalad_Footprints_Review03_before_sunfix.umap` in Saved.
- Local tests 14/14 PASS (4 GIS, 3 geometry GLB, 3 OSM street-spawn candidate, 4 actual UE sunfix report).
- Previous same-camera Lit screenshot V1 geometry visibility 4.64% (FAIL), exposure-only V2 12.61% (FAIL). These results are **before** sun-direction V3, and cannot be passed off as V3 visual acceptance. The post-sunfix 1920×1080 screenshot does not yet exist.

## Why testing was held
- Mandatory project resource preflight `Saved\GIS\Jeddah\LEVEL001_resource_preflight.ps1` requires at least **30 GiB free C:**, at least 8 GiB RAM and no competing Unreal process.
- Multiple real read-only checks show free disk fluctuating around **26–28 GiB** and some competing `UnrealEditor-Cmd.exe` builds appearing intermittently. With current preflight threshold, **running the V3 game screenshot / ShaderCompileWorker / BuildCookRun is blocked**.
- Prior shader failure was conclusively from C: insufficient space (error 112 / shader compiler transfer write failures), so this guard is based on a real failure, not just convenience.
- Read-only disk inventory shows three very large **generated PCH caches** in `C:\Users\Admin\NARIS\Intermediate\Build\Win64\x64\...\SharedPCH*.pch`: ~2.251, 1.938, 1.705 GiB (total ~5.9 GiB). Other paths: `C:\Temp` ~1.89 GiB (mainly unrelated Android emulator data), `NARIS\Saved` ~1.95 GiB (contains builds/cooked game), `NARIS\Intermediate` ~6.26 GiB. **Do not delete, move, compress or clean these paths automatically**; some may be needed by concurrent builds. No deletion/compression was done.
- User's live project has pre-existing unrelated modifications; previous recorded branch `feature/local-ui5-4-bell-marsh-20261003`, HEAD `57676f5`. No checkout/reset or broad staging attempted.
- Open Heritage 3D / CC BY-NC-ND scans must not be commercially embedded without the requested separate rights-holder permission.

## Remaining quality gates and recovery sequence
1. Free enough disk space through a separately approved, targeted recovery plan, or provision more storage. **Never** bypass the guard or mass-delete app/game files.
2. Ensure competing UE editors/cooks are idle. Run preflight, expect `eligible=true`.
3. Run V3 **-game** with same camera/resolution/quality: save `Saved/Screenshots/NARIS/LEVEL001_Jeddah_Review03_SunFixV3_after.png`; ensure actual image is visually legible.
4. Run `Saved/GIS/Jeddah/LEVEL001_lit_visibility_test.ps1 -CandidateLit ...SunFixV3_after.png` with current same-camera 1920×1080 Unlit mask. Pass threshold 50%, plus manual HDR / clipping and night aesthetic QA.
5. Produce Lit-before vs Lit-V3-after montage and diff. If V3 visibility still fails, diagnose physically based material import/sky environment and exposure; **do not** simply multiply every light or mislabel Unlit as final.
6. Only after validated V3 screenshot, add `LEVEL001_Safe_Street_Spawn_Candidate.json` to REVIEW map PlayerStart, collision / NavMesh / pawn / network 2 clients tests with independent evidence, then original licensed Hijazi modular facades, build, cook, fpschart, A11y/L10n, rollback and shipping gate.
7. PR #113 remains **draft**; issue #112 remains **open**. No packaged Jeddah build or approved photoreal map is claimed.

Official documentation: https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/Rotator?application_version=5.7 ; https://www.openstreetmap.org/copyright
