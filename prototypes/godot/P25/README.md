# NARIS REALMS — Godot P25 stabilization

**Status:** source-only prototype fixes. The production source of truth remains Unreal/W04; this is a separate Godot prototype branch.

## Verified
- 37/37 Python structural/regression tests passed locally.
- GLB original assets preserved in the downloadable P25 source package.
- Input actions: move_left/right/forward/back, sprint, jump, dodge, attack.
- Jump/dodge/attack use just-pressed input to prevent repeated triggers.
- Named AnimationLibrary playback supported for enemy visuals.
- Character model swap stops old AnimationPlayer.
- Health rejects nonfinite damage and caps damage to remaining HP.
- Godot import gate distinguishes static environment meshes from rigged characters.

## Unverified
- No Godot editor/headless runtime or Blender runtime available in the execution environment.
- No rigging/retargeting/IK/ragdoll production acceptance, FPS measurement, or EXE build.
- Full binary GLB files and complete Godot project are delivered in the P25 ZIP, not committed to this lightweight branch.

## Run checks
```bash
python -m unittest discover -s tests -v
godot --headless --path . --editor --import
godot --headless --path . --script res://tools/validate_import_headless.gd
```
