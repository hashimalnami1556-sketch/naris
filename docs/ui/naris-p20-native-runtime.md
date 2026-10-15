# P20 — Ash Gatekeeper UI design -> Unreal W04 native integration

**Date:** 2026-10-15  
**Target:** Unreal Engine 5.7, Windows PC / W04.  
**Evidence level:** Native source changes, awaiting CI and Unreal build. NOT an installed/running local game.

## Why this implementation differs from the browser reference

P20's HTML is a **separate interaction prototype** using a user-supplied demon image; it simulates health, attacks and a two-phase Ash Gatekeeper. Shipping its web page inside Unreal would leave it disconnected from native gameplay. Instead, this change ports P20's information architecture to the **existing C++ HUD and UMG main menu**:

- Native HUD draws live hero health, resonance and energy from `UNarisCombatComponent` and `UNarisEnergyComponent`.
- It draws a bottom-center encounter bar and actual phase values from the **W04 Bone Beast** boss. It does **not** relabel Bone Beast as Ash Gatekeeper or fabricate that enemy in W04.
- Key prompts use `ANarisPlayerController::GetActionKeyDisplayName` for action remapping, not the J/K test inputs from HTML.
- Main/front-end UMG menu uses a cinematic translucent scrim, a compact navigation region and hides the status card; settings and other submenus keep the highly opaque preexisting layout.
- The original game path `ANarisGameMode` -> `ANarisHUD` and the existing native input handlers stay unchanged. Save data, quest logic and enemy AI are not modified.

## Files changed

- `unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp`
- `unreal/NARIS_W04/Source/NARIS_W04/{Public/NarisSystemMenuWidget.h,Private/NarisSystemMenuWidget.cpp}`
- `tools/ci/test_p20_native_ui_contract.py`
- `tools/windows/Invoke-NarisP20NativeUI.ps1` (guarded build and optional launch)
- This document and the P20 active work record.

## Runtime/install verification required

1. Merge the candidate branch only after CI static checks and source review.
2. On an authorized Windows host with UE 5.7 and a complete W04 asset/level installation, run the launcher script with `-Launch`, setting `-ProjectRoot` to the **W04 project** and `-EngineRoot` to the actual UE installation. The script refuses to launch with no cooked/authoring `.umap`.
3. Confirm native front-end, keyboard/gamepad navigation, Health/Energy/Resonance values, Bone Beast phase changes and English/Arabic localization in the actual editor/game.
4. Capture fresh build/launch logs, real screenshots and measured performance. Only then claim installed/running.

## Known limitations / blockers

- The AsusRog remote device is paired/online but Desktop Commander returns a monthly usage-cap error as of this run. No local files were overwritten and no local Unreal process was launched.
- The repository checks in the W04 descriptor and source, but does not contain a confirmed playable `.umap` under the W04 map path. A local authored level or the real production project installation is required.
- The distinct production location `C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57` uses another project's module layout; DO NOT copy W04 source directly into that directory without assessing its classes and creating a targeted integration patch.
- Native C++ rendering mirrors **functional layout**; it does not yet contain P20's approved 3D background, original icons, audio or cinematics, and no UX/RTL/performance acceptance has been claimed.
