# UI-002 — Actual original-image intake / installation gate

Owner feedback: UI-001 was **NOT an installation**; only markdown was committed, with zero user images imported into Unreal. This correction supersedes any description suggesting the screens were already active.

## Exact approved images
| Screen | Original file in handoff ZIP | Original pixels | SHA256 (manifest) | Unreal target |
|---|---|---:|---|---|
| Character/Equipment | `UI_Character_Approved.png` | 1672×941 | `ff2e0f0…` | `/Game/NARIS/UI/ApprovedReferences/T_Naris_Approved_Character` |
| Main Menu | `UI_MainMenu_Approved.png` | 2048×1152 | `8d216d0…` | `/Game/NARIS/UI/ApprovedReferences/T_Naris_Approved_MainMenu` |
| Combat HUD | `UI_Combat_Approved.png` | 2048×1152 | `19734e1…` | `/Game/NARIS/UI/ApprovedReferences/T_Naris_Approved_Combat` |

Full digests are in `docs/ui/references/UI-002/manifest.json`. Unmodified PNG binaries and local audit/test files are in `NARIS_UI_002_ORIGINALS_AND_IMPORT.zip`, delivered to the owner in the conversation. **Binary PNGs are NOT committed in Git**; import requires the unpacked ZIP.

## Installation (not yet performed)
1. Extract the UI-002 ZIP to the Unreal machine.
2. Set `NARIS_UI_REFERENCE_ROOT` to the extracted `NARIS_UI_002_REAL_IMAGES` directory.
3. Run `tools/ui/import_approved_ui_references.py` inside UE5.7 Editor Python against `unreal/NARIS_W04/NARIS_W04.uproject`.
4. Verify exactly three `Texture2D` assets in Content Browser and retain `UE5_Import_Result.json` for evidence. The script refuses overwrite and validates PNG SHA256 and dimensions before making any changes.
5. Build *real* UMG widgets with separate, interactive, keyboard/gamepad-accessible controls and live gameplay bindings, referencing these images as visual design targets. **Do not display screenshots as fake clickable interfaces.**
6. Capture before/after/diff from the actual game, run Windows build/cook/PIE, EN/AR RTL and screen-resolution QA, server + two clients and FPS benchmark. Only then mark implementation approved.

## Actual status
- Owner visual design: APPROVED
- Exact original PNG bytes packaged and tested: YES (local tests 4/4 PASS)
- Git branch: manifest + importer checked in
- Git LFS PNG intake: NOT DONE
- Unreal Texture2D import: NOT RUN
- UMG menu/character/combat wiring: NOT DONE
- Editor/Windows gameplay installation: NOT DONE
- Ready to merge: NO

## Risk and rollback
Unsafe overwrite, rendered-menu fake interactivity, and loss of screen readability/RTL. Script refuses pre-existing target assets. Revert feature branch and selectively delete generated imported reference textures after inspecting dependencies. Existing UI source and original 3D art are unchanged.
